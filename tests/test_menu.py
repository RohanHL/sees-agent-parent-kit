"""Offline tests for the menu job: parsing, meal identity, the same-payload guard, weekends, rendering."""
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures'
spec = importlib.util.spec_from_file_location('refresh_menu', ROOT / 'tools/refresh_menu.py')
menu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(menu)


def page(meal, dish_names, token='123'):
    group = f'<a data-speech-text="Mealgroup {meal}" class="tab active" href="/m?{token}">{meal}</a>'
    items = ''.join(
        f'<div data-dish-id="{i}" data-speech-text="{name} Serving Size 1 each">'
        f'<img alt="Milk" src="/img/allergen/milk.png"></div>' if name == 'Cheese Pizza' else
        f'<div data-dish-id="{i}" data-speech-text="{name}"></div>'
        for i, name in enumerate(dish_names))
    return group + items


class MenuTests(unittest.TestCase):
    def test_dishes_with_allergens_and_no_repeats(self):
        self.assertEqual(menu.dishes(page('Lunch', ['Cheese Pizza', 'Apples', 'apples'])),
                         ['Cheese Pizza (contains: Milk)', 'Apples'])

    def test_separate_meals_use_feed_labels(self):
        meals = menu.day_meals(page('Breakfast', ['Waffles']), page('Lunch', ['Tacos']))
        self.assertEqual(meals, {'Breakfast': ['Waffles'], 'Lunch': ['Tacos']})

    def test_same_payload_is_one_meal_not_two(self):
        # The feed served one payload for both requests (Oct 4); only the cache-buster differed.
        meals = menu.day_meals(page('Breakfast', ['Waffles'], '1'), page('Breakfast', ['Waffles'], '2'))
        self.assertEqual(meals, {'Breakfast': ['Waffles']})

    def test_unlabeled_single_payload_is_dropped(self):
        unlabeled = '<div data-dish-id="1" data-speech-text="Mystery"></div>'
        self.assertEqual(menu.day_meals(unlabeled, unlabeled), {})

    def plan(self, start, count=10):
        return menu.plan(dt.date.fromisoformat(start), count, self.rows, self.info)

    def setUp(self):
        # A frozen copy of the 2026-27 school data, so next year's update can't break these tests.
        self.rows, self.info = menu.dates.load(FIXTURE), menu.dates.pack(FIXTURE)

    def test_lunch_request_answered_with_breakfast_is_dropped(self):
        # Different payloads, but the lunch page is labeled Breakfast: never publish it as either meal twice.
        meals = menu.day_meals(page('Breakfast', ['Waffles']), page('Breakfast', ['Tacos'], '9'))
        self.assertEqual(meals, {'Breakfast': ['Waffles']})

    def test_out_of_date_school_year_is_said_plainly(self):
        self.assertFalse(menu.year_out_of_date(dt.date(2027, 7, 20), self.info))
        self.assertTrue(menu.year_out_of_date(dt.date(2027, 8, 16), self.info))
        self.assertIn('Not published', menu.render(dt.date(2027, 8, 16), [], self.info))

    def test_weekends_skipped(self):
        days = self.plan('2026-10-30', 3)  # Fri, then Mon, Tue
        self.assertEqual([(d.weekday(), r) for d, r in days], [(4, None), (0, None), (1, None)])

    def test_holidays_shown_not_fetched(self):
        # Thanksgiving week: the feed would serve the next school day's menu for these, so they're never fetched.
        days = dict(self.plan('2026-11-23', 2))
        self.assertEqual(days[dt.date(2026, 11, 25)], 'Thanksgiving recess')
        self.assertIsNone(days[dt.date(2026, 11, 30)])

    def test_winter_break_is_not_a_failure(self):
        days = self.plan('2026-12-21')
        fetched = [(d, r, {} if r else {'Lunch': []}) for d, r in days]
        self.assertTrue(all(r for d, r in days if d < dt.date(2027, 1, 11)))
        self.assertFalse(menu.feed_broken(dt.date(2026, 12, 21), fetched))

    def test_in_session_with_unreadable_feed_is_a_failure(self):
        fetched = [(d, r, {}) for d, r in self.plan('2026-11-02')]  # no page the feed labeled
        self.assertTrue(menu.feed_broken(dt.date(2026, 11, 2), fetched))

    def test_menu_not_posted_yet_is_not_a_failure(self):
        # Seen live Oct 27: Nov 3 onward came back labeled but empty (the district posts in batches).
        fetched = [(d, r, {'Breakfast': [], 'Lunch': []}) for d, r in self.plan('2026-11-02')]
        self.assertFalse(menu.feed_broken(dt.date(2026, 11, 2), fetched))
        text = menu.render(dt.date(2026, 11, 2), [(d, r, m) for d, r, m in fetched[:1]], self.info)
        self.assertIn('Not posted yet.', text)

    def test_summer_fetches_nothing(self):
        self.assertEqual(self.plan('2027-06-14'), [])
        self.assertIn('Menus resume when school does', menu.render(dt.date(2027, 6, 14), [], self.info))

    def test_render_marks_missing_meals_and_days_off(self):
        text = menu.render(dt.date(2026, 11, 9), [
            (dt.date(2026, 11, 9), None, {'Breakfast': ['Waffles'], 'Lunch': ['Tacos']}),
            (dt.date(2026, 11, 10), None, {'Breakfast': ['Muffin']}),
            (dt.date(2026, 11, 11), 'Veterans Day', {}),
            (dt.date(2026, 11, 12), None, {}),
        ], self.info)
        self.assertIn('## Mon Nov 9, 2026', text)
        self.assertIn('**Lunch:** Tacos.', text)
        self.assertIn('**Lunch:** not available from the menu site for this day.', text)
        self.assertIn('No school: Veterans Day.', text)
        self.assertIn('Not posted yet.', text)
        self.assertIn(self.info['menu_feed']['live'], text)


if __name__ == '__main__':
    unittest.main()
