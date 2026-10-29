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

    def single_file(self, root=None):
        return build.render(root or self.root)[f'dist/{build.OUTPUT}'].decode()

    def test_reproducible_and_committed(self):
        self.assertEqual(build.render(self.root), build.render(self.root))
        for path, data in build.render(ROOT).items():
            self.assertEqual((ROOT / path).read_bytes(), data, f'{path} is stale')

    def test_every_guide_included_once_and_end_marker(self):
        text = self.single_file()
        for guide in (self.root / 'skill/references').glob('*.md'):
            self.assertEqual(text.count(f'<!-- guide: {guide.stem} -->'), 1)
        version = (self.root / 'skill/VERSION').read_text().strip()
        self.assertTrue(text.endswith(f'END OF SCHOOL-PARENT KIT {version}\n'))
        self.assertNotIn('`references/', text)

    def test_both_forms_reach_the_school_pack(self):
        # An agent given only the single file, or only the skill folder, must be able to open every school file.
        pack = __import__('json').loads((self.root / 'schools/sees/school.json').read_text())
        guide = build.render(self.root)[f'skill/references/{build.SCHOOL_GUIDE}.md'].decode()
        for link in pack['files'].values():
            self.assertIn(link, self.single_file())
            self.assertIn(link, guide)
        self.assertIn('`references/your-school.md`', (self.root / 'skill/SKILL.md').read_text())

    def test_skill_zip_matches_the_skill_folder(self):
        # Uploadable skill: one folder named like the skill, holding SKILL.md and every guide, byte for byte.
        import io
        import zipfile
        built = build.render(self.root)
        archive = zipfile.ZipFile(io.BytesIO(built[f'dist/{build.ZIP_OUTPUT}']))
        names = sorted(archive.namelist())
        self.assertIn('school-parent/SKILL.md', names)
        self.assertEqual(archive.read('school-parent/SKILL.md'), (self.root / 'skill/SKILL.md').read_bytes())
        for guide in (self.root / 'skill/references').glob('*.md'):
            self.assertEqual(archive.read(f'school-parent/references/{guide.name}'),
                             built.get(f'skill/references/{guide.name}', guide.read_bytes()))
        self.assertEqual(len(names), 1 + len(list((self.root / 'skill/references').glob('*.md'))))

    def test_readme_grants_authority_through_the_parent_not_the_page(self):
        # Assistants treat instructions inside fetched pages as untrusted; the parent's own request carries it.
        readme = (ROOT / 'README.md').read_text()
        self.assertNotIn("If you're an AI assistant", readme)
        self.assertIn("Don't send, delete or change anything", readme)

    def test_kit_joins_the_assistant_rather_than_replacing_it(self):
        # The parent's assistant keeps its own identity and routines; the kit never introduces a separate helper.
        skill = (self.root / 'skill/SKILL.md').read_text()
        self.assertIn('keep your own name, voice, memory', skill)
        self.assertNotIn("I'm a school helper", skill)

    def test_front_doors_point_at_the_built_file(self):
        # The README's agent section and the old v4 address both lead to the file the build writes.
        url = f'https://raw.githubusercontent.com/RohanHL/sees-agent-parent-kit/main/dist/{build.OUTPUT}'
        self.assertIn(url, (ROOT / 'README.md').read_text())
        self.assertIn(url, (ROOT / 'dist/PARENT-KIT.md').read_text())

    def test_school_pack_without_links_fails(self):
        self.edit('schools/sees/school.json', '"facts": "https://', '"facts": "')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_unlisted_guide_fails(self):
        (self.root / 'skill/references/extra.md').write_text('# Extra\n')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_missing_guide_fails(self):
        (self.root / 'skill/references/reading-and-updates.md').unlink()
        with self.assertRaises((ValueError, OSError)):
            build.render(self.root)

    def test_version_must_match_skill_text(self):
        (self.root / 'skill/VERSION').write_text('5.0.1\n')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_behavior_cannot_link_out(self):
        self.edit('skill/references/reading-and-updates.md', '# Reading', '# Reading https://example.com')
        with self.assertRaises(ValueError):
            build.render(self.root)

    def test_frontmatter_required(self):
        self.edit('skill/SKILL.md', 'name: school-parent\n', '')
        with self.assertRaises(ValueError):
            build.render(self.root)


if __name__ == '__main__':
    unittest.main()
