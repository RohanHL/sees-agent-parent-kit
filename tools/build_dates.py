#!/usr/bin/env python3
"""Build school-dates.md and school-year.ics from schools/<school>/dates.csv, the one place year-long dates live.

Only dates fixed for the year belong in dates.csv: the district's board-approved calendar and the PTO's published
year plan. Week-to-week dates (newsletters, ParentSquare, class mail) reach each parent by email and are their own
assistant's job. Weekdays are computed, never typed, so they can't disagree with the date. Everything
school-specific (sources, school year, notes) comes from schools/<school>/school.json.

Usage: python3 tools/build_dates.py [--check]
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
KINDS = {'school': 'First day of school', 'no-school': 'No school', 'minimum-day': 'Minimum days (early dismissal)',
         'pto': 'PTO events (planned; the PTO newsletter has the latest)'}
CALENDAR_KINDS = ('school', 'no-school', 'minimum-day')  # what changes a family's week; PTO events stay opt-in


def school_folder(root=ROOT):
    """schools/<name>: $KIT_SCHOOL if set, else the only folder in schools/ (a copy of the repo serves one school)."""
    name = os.environ.get('KIT_SCHOOL')
    if not name:
        folders = sorted(p.name for p in (root / 'schools').iterdir() if p.is_dir())
        if len(folders) != 1:
            raise ValueError(f'schools/ has {len(folders)} folders; set KIT_SCHOOL to pick one')
        name = folders[0]
    return root / 'schools' / name


def pack(root=ROOT):
    folder = school_folder(root)
    info = json.loads((folder / 'school.json').read_text())
    info['_folder'] = f'schools/{folder.name}'
    return info


def load(root=ROOT):
    info = pack(root)
    year = info['school_year']
    low, high = dt.date.fromisoformat(year['dates_from']), dt.date.fromisoformat(year['dates_to'])
    rows = []
    with open(school_folder(root) / 'dates.csv', newline='') as f:
        for n, row in enumerate(csv.DictReader(f), start=2):
            start = dt.date.fromisoformat(row['start'])
            end = dt.date.fromisoformat(row['end']) if row['end'] else start
            if not (low <= start <= end <= high):
                raise ValueError(f'dates.csv line {n}: dates outside the school year or end before start')
            if row['kind'] not in KINDS or row['source'] not in info['date_sources'] or not row['what'].strip():
                raise ValueError(f'dates.csv line {n}: unknown kind or source, or empty description')
            rows.append({'start': start, 'end': end, 'kind': row['kind'], 'what': row['what'].strip(),
                         'source': row['source']})
    return sorted(rows, key=lambda r: (r['start'], r['what']))


def is_school_day(day, rows, info):
    """A weekday inside the school year that no no-school row covers."""
    year = info['school_year']
    if day.weekday() >= 5 or not (dt.date.fromisoformat(year['first_day']) <= day
                                  <= dt.date.fromisoformat(year['last_day'])):
        return False
    return not any(r['kind'] == 'no-school' and r['start'] <= day <= r['end'] for r in rows)


def no_school_reason(day, rows):
    return next((r['what'] for r in rows if r['kind'] == 'no-school' and r['start'] <= day <= r['end']), None)


def day(d, year=True):
    """'Mon Nov 23, 2026' (or without the year); portable, unlike strftime's %-d."""
    return f'{d:%a %b} {d.day}' + (f', {d.year}' if year else '')


def when(row):
    if row['start'] == row['end']:
        return day(row['start'])
    return f'{day(row["start"], year=False)} – {day(row["end"])}'


def markdown(rows, info):
    out = [f'# {info["short_name"]} school dates {info["school_year"]["label"]}', '',
           f'Dates fixed for the whole school year, each with its source. Built from `{info["_folder"]}/dates.csv`; '
           'updated once a year (August) or when the district changes its calendar.', '',
           '**Not here on purpose:** week-to-week dates (Flag Salute, picture day, spirit days, class events). They '
           'come in the principal newsletter, ParentSquare and class mail, which each family already gets; read '
           'the parent\'s own school mail for those. A newer official notice beats this file.', '',
           '## Every week', '']
    out += [f'- {note}' for note in info['weekly_notes']] + ['']
    for kind, title in KINDS.items():
        items = [r for r in rows if r['kind'] == kind]
        if items:
            out += [f'## {title}', '']
            out += [f'- **{when(r)}**: {r["what"]} [{r["source"]}]' for r in items]
            out.append('')
    out += ['## Sources', '']
    out += [f'- [{key}] {s["name"]}: {s["url"]}' for key, s in info['date_sources'].items()]
    out += ['', '## Known errors in other sources (don\'t repeat them)', '']
    out += [f'- {error}' for error in info['known_date_errors']]
    out += ['', 'The first day, no-school days and minimum days as a calendar the parent can subscribe to once (the dates '
            'are fixed for the year, so there is nothing to keep in sync):',
            f'- iPhone or Mac: {info["files"]["year_calendar_apple"]}',
            f'- Google Calendar (Other calendars > From URL): {info["files"]["year_calendar_file"]}']
    return '\n'.join(out) + '\n'


def fold(line):
    """RFC 5545: content lines longer than 75 octets continue on lines starting with a space."""
    data, parts = line.encode(), []
    while len(data) > 75:
        cut = 75 if not parts else 74
        while (data[cut] & 0xC0) == 0x80:  # don't split a UTF-8 character
            cut -= 1
        parts.append(data[:cut])
        data = data[cut:]
    parts.append(data)
    return '\r\n '.join(p.decode() for p in parts)


def text(value):
    return value.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,')


def ics(rows, info):
    label, name = info['school_year']['label'], info['short_name']
    out = ['BEGIN:VCALENDAR', 'VERSION:2.0', f'PRODID:-//{name} parent kit//school year//EN', 'CALSCALE:GREGORIAN',
           f'X-WR-CALNAME:{text(f"{name} {label} days off and minimum days")}', f'X-WR-TIMEZONE:{info["timezone"]}']
    for r in rows:
        if r['kind'] not in CALENDAR_KINDS:
            continue
        title = {'no-school': f'No school: {r["what"]}', 'school': r['what'],
                 'minimum-day': r['what'] if 'inimum' in r['what'] else f'Minimum day: {r["what"]}'}[r['kind']]
        uid = hashlib.sha256(f'{name}|{r["start"]}|{r["what"]}'.encode()).hexdigest()[:20]
        source = info['date_sources'][r['source']]
        out += ['BEGIN:VEVENT', f'UID:{uid}@school-parent-kit', f'DTSTAMP:{r["start"]:%Y%m%d}T000000Z',
                f'DTSTART;VALUE=DATE:{r["start"]:%Y%m%d}',
                f'DTEND;VALUE=DATE:{r["end"] + dt.timedelta(days=1):%Y%m%d}',
                f'SUMMARY:{text(f"{title} ({name})")}', f'DESCRIPTION:{text("Source: " + source["name"])}',
                f'URL:{source["url"]}', 'TRANSP:TRANSPARENT', 'END:VEVENT']
    out.append('END:VCALENDAR')
    return ''.join(fold(line) + '\r\n' for line in out)


def outputs(root=ROOT):
    rows, info = load(root), pack(root)
    return {'school-dates.md': markdown(rows, info).encode(), 'school-year.ics': ics(rows, info).encode()}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true', help='fail if the built files are stale')
    args = parser.parse_args()
    try:
        for name, data in outputs().items():
            target = ROOT / name
            if args.check:
                if not target.exists() or target.read_bytes() != data:
                    raise ValueError(f'{name} is stale; run tools/build_dates.py')
                print(f'PASS: {name} matches dates.csv')
            else:
                target.write_bytes(data)
                print(f'Wrote {name}')
    except (OSError, ValueError, KeyError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
