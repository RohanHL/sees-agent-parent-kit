#!/usr/bin/env python3
"""Rewrite school-menu.md from the district's YumYummi menu feed. Code only, no judgment; run weekly by CI.

Guards, learned from the feed's real behavior (Sep-Oct 2026):
- On weekends the feed silently serves the next school day's menu, so weekend dates are never fetched.
- The meal is whatever the feed's own markup says ("Mealgroup Breakfast"), never guessed from the dishes.
- Since Oct 4 the feed has at times returned the same payload for breakfast and lunch requests. Identical raw
  payloads mean the meals aren't separated: that day is published as the one labeled meal, never twice.
- If no day has any dishes, the existing file is left untouched and the run fails, so the failure is visible.

Usage: python3 tools/refresh_menu.py [--start YYYY-MM-DD] [--days N]
"""
import argparse
import datetime as dt
import html
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'school-menu.md'
FEED = 'https://smusd.yumyummi.com/webapp/load-ajax-school-menus/'
LIVE = 'https://smusd.yumyummi.com/webapp/san-elijo-elementary/daily/lunch'
SCHOOL_ID = '16345'  # San Elijo Elementary
MEALS = ('Breakfast', 'Lunch')
CODES = {'Breakfast': 'BF', 'Lunch': 'L'}

_ACTIVE_MEAL = re.compile(r'data-speech-text="Mealgroup ([A-Za-z]+)"[^>]*class="[^"]*active')
_ANY_MEAL = re.compile(r'data-speech-text="Mealgroup ([A-Za-z]+)"')
_CACHE_BUSTER = re.compile(r'\?\d+')
_DISH_TAG = re.compile(r'<[^>]*\bdata-dish-id="\d+"[^>]*>')


def fetch(meal_code, day):
    body = urllib.parse.urlencode({'sid': SCHOOL_ID, 'mg': meal_code, 'd': day.isoformat()}).encode()
    req = urllib.request.Request(FEED, data=body, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=20).read().decode('utf-8', 'ignore')


def meal_label(page):
    """The meal the feed says it is serving, or None. Only Breakfast or Lunch are trusted."""
    for pattern in (_ACTIVE_MEAL, _ANY_MEAL):
        found = pattern.search(page or '')
        if found and found.group(1) in MEALS:
            return found.group(1)
    return None


def same_payload(a, b):
    def norm(page):
        return re.sub(r'\s+', ' ', _CACHE_BUSTER.sub('?X', page or '')).strip()
    return norm(a) == norm(b)


def dishes(page):
    """Dish names with allergens where the feed lists them, in feed order, without repeats."""
    starts = [m.start() for m in _DISH_TAG.finditer(page or '')]
    out, seen = [], set()
    for i, start in enumerate(starts):
        chunk = page[start:starts[i + 1] if i + 1 < len(starts) else len(page)]
        tag = _DISH_TAG.match(chunk).group(0)
        speech = re.search(r'data-speech-text="([^"]*)"', tag)
        name = ' '.join(html.unescape(speech.group(1) if speech else '').split('Serving Size')[0].split())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        allergens = []
        for alt in (re.findall(r'<img[^>]*alt="([^"]*)"[^>]*/allergen/', chunk)
                    + re.findall(r'<img[^>]*/allergen/[^>]*alt="([^"]*)"', chunk)):
            alt = ' '.join(html.unescape(alt).split())
            if alt and alt not in allergens:
                allergens.append(alt)
        out.append(f'{name} (contains: {", ".join(allergens)})' if allergens else name)
    return out


def day_meals(breakfast_page, lunch_page):
    """{meal: [dishes]} for one day, using the feed's own labels; {} if the feed didn't label the meal."""
    if breakfast_page and lunch_page and not same_payload(breakfast_page, lunch_page):
        return {meal_label(breakfast_page) or 'Breakfast': dishes(breakfast_page),
                meal_label(lunch_page) or 'Lunch': dishes(lunch_page)}
    label = meal_label(breakfast_page) or meal_label(lunch_page)
    return {label: dishes(breakfast_page or lunch_page)} if label else {}


def school_days(start, count):
    day, out = start, []
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += dt.timedelta(days=1)
    return out


def render(rendered_on, days):
    """days: list of (date, {meal: [dishes]}). Returns the markdown file."""
    lines = ['# This week\'s breakfast and lunch menu', '',
             f'Snapshot rendered {rendered_on.isoformat()} by this repo\'s weekly menu job, from the SMUSD menu site.',
             f'Covers {len(days)} school days from {days[0][0]:%a %b %-d, %Y}. Menus change: this is a snapshot,',
             f'not the source. Live menu: {LIVE}', '']
    for day, meals in days:
        lines += [f'## {day:%a %b %-d, %Y}', '']
        if not any(meals.values()):
            lines += ['Not posted (or no school that day). Check the live menu.', '']
            continue
        for meal in MEALS:
            if meal in meals:
                items = meals[meal]
                lines.append(f'**{meal}:** ' + ('; '.join(items) + '.' if items else 'not posted.'))
            else:
                lines.append(f'**{meal}:** not available from the menu site for this day.')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    today = dt.datetime.now(ZoneInfo('America/Los_Angeles')).date()
    parser.add_argument('--start', type=dt.date.fromisoformat, default=today)
    parser.add_argument('--days', type=int, default=10)
    args = parser.parse_args()
    collected = []
    for day in school_days(args.start, args.days):
        try:
            meals = day_meals(fetch(CODES['Breakfast'], day), fetch(CODES['Lunch'], day))
        except OSError as error:
            print(f'FAIL: menu site unreachable for {day}: {error}', file=sys.stderr)
            sys.exit(1)
        collected.append((day, meals))
        print(f'{day}: ' + ', '.join(f'{m} {len(d)}' for m, d in meals.items()) if meals else f'{day}: none')
    if not any(any(meals.values()) for _, meals in collected):
        print('FAIL: no dishes for any day; school-menu.md left unchanged', file=sys.stderr)
        sys.exit(2)
    OUTPUT.write_text(render(today, collected))
    print(f'Wrote {OUTPUT.name}')


if __name__ == '__main__':
    main()
