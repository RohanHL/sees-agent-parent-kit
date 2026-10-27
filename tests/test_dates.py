"""Offline tests for the year-long dates: one source (dates.csv), built files current, bad rows refused."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_dates', ROOT / 'tools/build_dates.py')
dates = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dates)


class DatesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        # A frozen copy of the 2026-27 school data, so next year's update can't break these tests.
        self.root = Path(self.tmp.name) / 'kit'
        shutil.copytree(ROOT / 'tests/fixtures', self.root)
        self.csv = self.root / 'schools/sees/dates.csv'

    def test_school_folder_found_or_named(self):
        self.assertEqual(dates.school_folder(self.root).name, 'sees')
        shutil.copytree(self.root / 'schools/sees', self.root / 'schools/other')
        with self.assertRaises(ValueError):
            dates.school_folder(self.root)

    def test_built_files_are_committed(self):
        for name, data in dates.outputs(ROOT).items():
            self.assertEqual((ROOT / name).read_bytes(), data, f'{name} is stale')

    def test_ranges_shown_in_full_with_weekdays(self):
        text = dates.outputs(self.root)['school-dates.md'].decode()
        self.assertIn('**Mon Nov 23 – Fri Nov 27, 2026**: Thanksgiving recess [D]', text)
        self.assertIn('**Wed Nov 11, 2026**: Veterans Day [D]', text)

    def test_calendar_file_holds_only_week_changing_days(self):
        cal = dates.outputs(self.root)['school-year.ics'].decode()
        self.assertIn('DTSTART;VALUE=DATE:20261123\r\nDTEND;VALUE=DATE:20261128', cal)  # end is exclusive
        self.assertNotIn('PTO meeting', cal)
        self.assertEqual(cal.count('BEGIN:VEVENT'), cal.count('END:VEVENT'))

    def test_calendar_lines_folded_to_75_octets(self):
        cal = dates.outputs(self.root)['school-year.ics']
        self.assertTrue(all(len(line) <= 75 for line in cal.split(b'\r\n')))
        self.assertTrue(cal.endswith(b'END:VCALENDAR\r\n'))

    def test_first_and_last_day_are_in_the_list(self):
        rows, year = dates.load(self.root), dates.pack(self.root)['school_year']
        starts = {r['start'].isoformat() for r in rows}
        self.assertIn(year['first_day'], starts)
        self.assertIn(year['last_day'], starts)

    def test_date_outside_school_year_refused(self):
        self.csv.write_text(self.csv.read_text() + '2028-01-01,,no-school,Typo year,D\n')
        with self.assertRaises(ValueError):
            dates.load(self.root)

    def test_unknown_source_refused(self):
        self.csv.write_text(self.csv.read_text() + '2026-12-01,,no-school,Rumor,blog\n')
        with self.assertRaises(ValueError):
            dates.load(self.root)


if __name__ == '__main__':
    unittest.main()
