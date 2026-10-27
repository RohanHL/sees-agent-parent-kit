#!/usr/bin/env python3
"""Rewrite school-menu.md from the district's YumYummi menu feed. Code only, no judgment; run weekly by CI.

Guards, learned from the feed's real behavior (Sep-Oct 2026):
- On days without school the feed silently serves the next school day's menu, so only school days are fetched:
  weekdays inside the school year that schools/<school>/dates.csv doesn't mark as no school. Days off are shown
  as days off, with the reason.
- The meal is whatever the feed's own markup says ("Mealgroup Breakfast"), never guessed from the dishes.
- Since Oct 4 the feed has at times returned the breakfast payload for a lunch request. A page is kept only if its
  label names the meal requested, so one meal is never published as the other.
- If the school year's dates are out of date (mid-August onward), it can't tell school days from days off: the
  file says so and the run fails visibly until schools/<school>/ is updated for the new year.
- If school is in session this week and the feed labeled no meal page at all, the site changed and this script
  can't read it: the existing file is left untouched and the run fails, so the failure is visible. Days the district
  hasn't posted yet (labeled pages, no dishes), breaks and summer are not failures.

Usage: python3 tools/refresh_menu.py [--start YYYY-MM-DD] [--days N]
"""
import argparse
import datetime as dt
import html
import importlib.util
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'school-menu.md'
_spec = importlib.util.spec_from_file_location('build_dates', ROOT / 'tools/build_dates.py')
dates = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dates)
MEALS = ('Breakfast', 'Lunch')
CODES = {'Breakfast': 'BF', 'Lunch': 'L'}
LOOKAHEAD = 35  # calendar days; long enough to see past winter break

_ACTIVE_MEAL = re.compile(r'data-speech-text="Mealgroup ([A-Za-z]+)"[^>]*class="[^"]*active')
_ANY_MEAL = re.compile(r'data-speech-text="Mealgroup ([A-Za-z]+)"')
_DISH_TAG = re.compile(r'<[^>]*\bdata-dish-id="\d+"[^>]*>')


def fetch(feed, meal_code, day, attempts=3):
    body = urllib.parse.urlencode({'sid': feed['school_id'], 'mg': meal_code, 'd': day.isoformat()}).encode()
    req = urllib.request.Request(feed['url'], data=body, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(attempts):
        try:
            return urllib.request.urlopen(req, timeout=20).read().decode('utf-8', 'ignore')
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(5 * (attempt + 1))


def meal_label(page):
    """The meal the feed says it is serving, or None. Only Breakfast or Lunch are trusted."""
    for pattern in (_ACTIVE_MEAL, _ANY_MEAL):
        found = pattern.search(page or '')
        if found and found.group(1) in MEALS:
            return found.group(1)
    return None


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
    """{meal: [dishes]} for one day. A page counts only if the feed's own label names the meal we asked for: a
    page labeled as the other meal (the same-payload bug) or not labeled at all is dropped, never relabeled."""
    out = {}
    for meal, page in (('Breakfast', breakfast_page), ('Lunch', lunch_page)):
        if meal_label(page) == meal:
            out[meal] = dishes(page)
    return out


def plan(start, count, rows, info):
    """Weekdays from start until `count` school days are covered (at most LOOKAHEAD days ahead).
    Returns [(date, reason)]: reason is None for a school day, else why there's no school."""
    out, school_days, day = [], 0, start
    last = dt.date.fromisoformat(info['school_year']['last_day'])
    while school_days < count and day <= min(last, start + dt.timedelta(days=LOOKAHEAD)):
        if day.weekday() < 5:
            if dates.is_school_day(day, rows, info):
                out.append((day, None))
                school_days += 1
            elif dates.no_school_reason(day, rows):
                out.append((day, dates.no_school_reason(day, rows)))
        day += dt.timedelta(days=1)
    return out


def year_out_of_date(today, info):
    """Past the school year's date range by mid-August: the new year's dates haven't been added."""
    return today > dt.date.fromisoformat(info['school_year']['dates_to']) + dt.timedelta(days=45)


def render(rendered_on, days, info):
    """days: list of (date, reason or None, {meal: [dishes]}). Returns the markdown file."""
    live = info['menu_feed']['live']
    lines = ['# Breakfast and lunch menu', '',
             f'Snapshot rendered {rendered_on.isoformat()} by this repo\'s weekly menu job, from the district menu '
             'site. Menus change: this is a snapshot, not the source.', f'Live menu: {live}', '']
    if year_out_of_date(rendered_on, info):
        lines += [f'Not published: this repo\'s school dates are for {info["school_year"]["label"]} and the new '
                  'school year hasn\'t been added yet, so it can\'t tell school days from days off. Use the live menu.']
        return '\n'.join(lines) + '\n'
    if not days:
        lines += ['No school days in the coming weeks of this school year\'s calendar (break or summer). Menus '
                  'resume when school does; check the live menu.']
        return '\n'.join(lines) + '\n'
    lines[2] += f' Covers {dates.day(days[0][0], year=False)} to {dates.day(days[-1][0])}.'
    for day, reason, meals in days:
        lines += [f'## {dates.day(day)}', '']
        if reason:
            lines += [f'No school: {reason}.', '']
            continue
        if not any(meals.values()):
            lines += ['Not posted yet. Check the live menu.', '']
            continue
        for meal in MEALS:
            if meal in meals:
                items = meals[meal]
                lines.append(f'**{meal}:** ' + ('; '.join(items) + '.' if items else 'not posted.'))
            else:
                lines.append(f'**{meal}:** not available from the menu site for this day.')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def feed_broken(start, days):
    """School is in session in the next week, yet no school day came back as a meal page the feed labeled. A labeled
    page with no dishes just means the district hasn't posted that day yet (it posts in batches); no labeled page
    at all means the site changed and this script can't read it."""
    in_session = any(reason is None and day <= start + dt.timedelta(days=6) for day, reason, _ in days)
    return in_session and not any(meals for _, reason, meals in days if reason is None)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    info = dates.pack()
    today = dt.datetime.now(ZoneInfo(info['timezone'])).date()
    parser.add_argument('--start', type=dt.date.fromisoformat, default=today)
    parser.add_argument('--days', type=int, default=10)
    args = parser.parse_args()
    feed = info.get('menu_feed')
    if not feed:
        print(f'No menu_feed in {info["_folder"]}/school.json; nothing to refresh.')
        return
    if year_out_of_date(today, info):
        OUTPUT.write_text(render(today, [], info))
        print(f'FAIL: school dates are for {info["school_year"]["label"]}; update {info["_folder"]}/dates.csv and '
              'school.json for the new school year', file=sys.stderr)
        sys.exit(3)
    rows = dates.load()
    collected = []
    for day, reason in plan(args.start, args.days, rows, info):
        meals = {}
        if reason is None:
            try:
                meals = day_meals(fetch(feed, CODES['Breakfast'], day), fetch(feed, CODES['Lunch'], day))
            except OSError as error:
                print(f'FAIL: menu site unreachable for {day}: {error}', file=sys.stderr)
                sys.exit(1)
        collected.append((day, reason, meals))
        print(f'{day}: ' + (f'no school ({reason})' if reason else
                            ', '.join(f'{m} {len(d)}' for m, d in meals.items()) or 'nothing posted'))
    if feed_broken(args.start, collected):
        print('FAIL: school is in session but no dishes for any school day; school-menu.md left unchanged',
              file=sys.stderr)
        sys.exit(2)
    OUTPUT.write_text(render(today, collected, info))
    print(f'Wrote {OUTPUT.name}')


if __name__ == '__main__':
    main()
