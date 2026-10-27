"""Offline tests for the menu job: parsing, meal identity, the same-payload guard, weekends, rendering."""
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
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

    def test_weekends_skipped(self):
        days = menu.school_days(dt.date(2026, 10, 30), 3)  # Fri, then Mon, Tue
        self.assertEqual([d.weekday() for d in days], [4, 0, 1])

    def test_render_marks_missing_meals(self):
        text = menu.render(dt.date(2026, 11, 2), [
            (dt.date(2026, 11, 2), {'Breakfast': ['Waffles'], 'Lunch': ['Tacos']}),
            (dt.date(2026, 11, 3), {'Breakfast': ['Muffin']}),
            (dt.date(2026, 11, 4), {}),
        ])
        self.assertIn('## Mon Nov 2, 2026', text)
        self.assertIn('**Lunch:** Tacos.', text)
        self.assertIn('**Lunch:** not available from the menu site for this day.', text)
        self.assertIn('Not posted (or no school that day).', text)
        self.assertIn(menu.LIVE, text)


if __name__ == '__main__':
    unittest.main()
