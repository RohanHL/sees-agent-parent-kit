"""Static packaging/fixture tests only; these cannot validate an assistant host."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / 'tools/build_bundle.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'kit'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('__pycache__'))

    def mutate_json(self, path, change):
        file = self.root / path
        data = json.loads(file.read_text())
        change(data)
        file.write_text(json.dumps(data))

    def test_build_reproducible(self):
        self.assertEqual(build.render(self.root), build.render(self.root))
        self.assertEqual(build.render(ROOT), build.render(self.root))

    def test_committed_artifacts_match(self):
        for name, data in zip(('PARENT-KIT.md', 'bundle-manifest.json'), build.render(ROOT)):
            self.assertEqual((ROOT / 'dist' / name).read_bytes(), data)

    def test_all_modules_once_and_hashes(self):
        bundle, encoded = build.render(self.root)
        manifest = json.loads(encoded)
        self.assertEqual(manifest['bundle_sha256'], build.sha(bundle))
        for record in manifest['modules']:
            path = record['path']
            raw = (self.root / path).read_bytes()
            self.assertEqual(record['sha256'], build.sha(raw))
            self.assertEqual(record['bytes'], len(raw))
            self.assertEqual(bundle.count(f'<!-- BEGIN MODULE {path} -->'.encode()), 1)
            self.assertIn(raw.rstrip(), bundle)
        self.assertTrue(bundle.endswith(f"END COMPLETE PARENT KIT {manifest['behavior_version']}\n".encode()))

    def test_missing_module_fails(self):
        (self.root / build.REQUIRED[-1]).unlink()
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_extra_module_fails(self):
        (self.root / 'core/UNLISTED.md').write_text('# Forgotten behavior\n')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_duplicate_manifest_module_fails(self):
        self.mutate_json('manifest.json', lambda d: d['modules'].append(d['modules'][0]))
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_module_order_change_fails(self):
        self.mutate_json('manifest.json', lambda d: d['modules'].reverse())
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_empty_module_fails(self):
        (self.root / build.REQUIRED[0]).write_text('')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_dangling_behavior_link_fails(self):
        for suffix in ('\nRead [missing](absent.md)\n', '\nRead https://example.test/main/SETUP.md\n'):
            file = self.root / build.REQUIRED[0]
            file.write_text(file.read_text() + suffix)
            with self.assertRaises(ValueError):
                build.render(self.root)

    def test_source_change_changes_bundle_identity(self):
        before = build.render(self.root)
        path = self.root / build.REQUIRED[0]
        path.write_text(path.read_text() + '\nA synthetic test addition.\n')
        after = build.render(self.root)
        self.assertNotEqual(before[0], after[0])
        self.assertNotEqual(json.loads(before[1])['bundle_sha256'], json.loads(after[1])['bundle_sha256'])

    def test_examples_valid(self):
        build.validate_examples(self.root)

    def test_example_version_mismatch_fails(self):
        self.mutate_json('examples/session-checkpoint.json', lambda d: d.update(behavior_version='old'))
        with self.assertRaises(ValueError):
            build.validate_examples(self.root)

    def test_dangling_obligation_fails(self):
        self.mutate_json('examples/session-checkpoint.json', lambda d: d['obligations'][0].update(child_id='missing'))
        with self.assertRaises(ValueError):
            build.validate_examples(self.root)

    def test_fictional_permissions_cannot_be_granted(self):
        self.mutate_json('examples/session-checkpoint.json', lambda d: d['read_scope']['senders'].append('example.test'))
        with self.assertRaises(ValueError):
            build.validate_examples(self.root)

    def test_host_example_cannot_claim_verification(self):
        self.mutate_json('examples/host-profile.json', lambda d: d['capabilities'].update(scheduling='verified'))
        with self.assertRaises(ValueError):
            build.validate_examples(self.root)

    def test_completion_requires_evidence(self):
        self.mutate_json('examples/session-checkpoint.json', lambda d: d['obligations'][0].update(evidence=''))
        with self.assertRaises(ValueError):
            build.validate_examples(self.root)

    def test_local_document_links_resolve(self):
        for path in self.root.rglob('*.md'):
            for dest in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' not in dest and not dest.startswith('#'):
                    self.assertTrue((path.parent / dest.split('#')[0]).is_file(), (path, dest))

    def test_manifest_is_optional_for_single_file_handoff(self):
        text = (self.root / 'contracts/VERSIONING.md').read_text()
        for phrase in ('optional maintainer integrity companion, not a runtime dependency',
                       'parents need only the complete generated instruction file',
                       'visible version, inventory and end marker without claiming cryptographic verification'):
            self.assertIn(phrase, text)
        self.assertNotIn('distribute the complete file and manifest together', text)

    def test_capability_health_and_consent_are_distinct(self):
        text = (self.root / 'contracts/HOST.md').read_text()
        for phrase in ('Capability availability, current operational health and parent consent are separate',
                       'A transient read or delivery failure does not establish unavailability',
                       'A declined connection is a consent decision',
                       'Neither verified capability nor recovered health grants consent'):
            self.assertIn(phrase, text)

    def test_default_school_evidence_is_bundled(self):
        bundle = build.render(self.root)[0].decode()
        for evidence in ('school-facts.md', 'school-dates.md', 'school-menu.md', 'senders.json', 'topics/INDEX.md'):
            self.assertIn('https://raw.githubusercontent.com/RohanHL/sees-agent-parent-kit/main/' + evidence, bundle)

    def test_school_pack_cannot_link_remote_behavior(self):
        file = self.root / 'contracts/SCHOOL-PACK.md'
        file.write_text(file.read_text() + '\nhttps://raw.githubusercontent.com/RohanHL/sees-agent-parent-kit/main/SETUP.md\n')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_no_mutable_behavior_urls_or_internal_paths(self):
        bundle = build.render(self.root)[0].decode()
        for forbidden in ('main/SETUP.md', 'main/PRINCIPLES.md', 'main/TRIAGE.md', '/workspace/', 'docs.google.com/forms'):
            self.assertNotIn(forbidden, bundle)


if __name__ == '__main__':
    unittest.main()
