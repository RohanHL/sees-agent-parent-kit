"""Static tests for the skill folder and its single-file build; they cannot validate model behavior."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_skill', ROOT / 'tools/build_skill.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'kit'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('__pycache__', '.git'))

    def edit(self, path, old, new):
        file = self.root / path
        text = file.read_text()
        self.assertIn(old, text)
        file.write_text(text.replace(old, new, 1))

    def test_reproducible_and_committed(self):
        self.assertEqual(build.render(self.root), build.render(self.root))
        self.assertEqual((ROOT / 'dist' / build.OUTPUT).read_bytes(), build.render(ROOT))

    def test_every_guide_included_once_and_end_marker(self):
        text = build.render(self.root).decode()
        for guide in (self.root / 'skill/references').glob('*.md'):
            self.assertEqual(text.count(f'<!-- guide: {guide.stem} -->'), 1)
        version = (self.root / 'skill/VERSION').read_text().strip()
        self.assertTrue(text.endswith(f'END OF SCHOOL-PARENT KIT {version}\n'))
        self.assertNotIn('`references/', text)

    def test_unlisted_guide_fails(self):
        (self.root / 'skill/references/extra.md').write_text('# Extra\n')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_missing_guide_fails(self):
        (self.root / 'skill/references/upgrades.md').unlink()
        with self.assertRaises((ValueError, OSError)):
            build.render(self.root)

    def test_version_must_match_skill_text(self):
        (self.root / 'skill/VERSION').write_text('5.0.1\n')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_behavior_cannot_link_out(self):
        self.edit('skill/references/upgrades.md', '# Loading', '# Loading https://example.com')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_frontmatter_required(self):
        self.edit('skill/SKILL.md', 'name: school-parent\n', '')
        with self.assertRaises(ValueError):
            build.render(self.root)


if __name__ == '__main__':
    unittest.main()
