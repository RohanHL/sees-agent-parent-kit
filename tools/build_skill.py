#!/usr/bin/env python3
"""Build/check the single-file form of skill/ for hosts that can't load a skill folder."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('build_dates', ROOT / 'tools/build_dates.py')
dates = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dates)
OUTPUT = 'school-parent-kit.md'
ZIP_OUTPUT = 'school-parent-skill.zip'
VERSION_RE = re.compile(r'\d+\.\d+\.\d+(-draft\.\d+)?\Z')
REF_RE = re.compile(r'`references/([a-z-]+)\.md`')


def split_frontmatter(text):
    if not text.startswith('---\n'):
        raise ValueError('SKILL.md must start with frontmatter')
    head, sep, body = text[4:].partition('\n---\n')
    if not sep:
        raise ValueError('SKILL.md frontmatter is not closed')
    fields = dict(line.split(': ', 1) for line in head.splitlines() if ': ' in line)
    if set(fields) != {'name', 'description'} or not fields['name'] or not fields['description']:
        raise ValueError('Frontmatter needs exactly name and description')
    return fields, body.lstrip('\n')


SCHOOL_GUIDE = 'your-school'  # generated from school.json; the only guide allowed to hold links


def school_section(root):
    """The 'your-school' guide: the school's public links from its school.json, so both the skill folder and the
    single file can reach the school pack."""
    pack = dates.pack(root)
    files = pack['files']
    for key in ('facts', 'dates', 'menu', 'topics_index', 'pages', 'year_calendar_file'):
        if not files.get(key, '').startswith('https://'):
            raise ValueError(f'school.json needs an https link for files.{key}')
    lines = [f'# Your school: {pack["school"]}', '',
             f'<!-- Generated from {pack.get("_folder", "schools/<school>")}/school.json by tools/build_skill.py; '
             'edit that file, not this one. -->', '',
             f'{pack["district"]}, {pack["city"]}. Timezone {pack["timezone"]}. Maintained by '
             f'{pack["maintained_by"]}.', '',
             'This is the school pack. Open a file when a question needs it (public web addresses, no sign-in):',
             f'- School facts (contacts, hours, policies, programs): {files["facts"]}',
             f'- Year-long school dates (days off, minimum days, PTO plan), with sources: {files["dates"]}',
             f'- Breakfast and lunch menu, refreshed weekly: {files["menu"]}',
             f'- Topic briefs (index; each brief cites its sources): {files["topics_index"]}',
             f'- School map, for anything the files above don\'t cover: which school system does what, school-wide '
             f'documents and forms, and every page on the school, district and PTO websites (find the place, then '
             f'open it live; pages note their school year): {files["pages"]}',
             '- This year\'s days off and minimum days as a calendar the parent subscribes to once (fixed dates, nothing to update), if you can\'t add '
             'them to their calendar yourself. Give the one link for their calendar, as is; it opens their calendar '
             'app\'s own add prompt, with no web page in between:',
             f'  - iPhone or Mac (tap, then Subscribe): {files["year_calendar_apple"]}',
             f'  - Google Calendar (tap, then Add): {files["year_calendar_google"]}',
             f'  - Any other calendar app (add by URL): {files["year_calendar_file"]}',
             '  A calendar file you make for download is the clumsy path on a phone: it lands in a download prompt or '
             'Files, not in their calendar, and parents find it confusing. This calendar also holds the minimum days; '
             'if the parent wants fewer dates, tell them that and let them choose.']
    if not files.get('year_calendar_apple', '').startswith('webcal://'):
        raise ValueError('school.json needs a webcal:// link for files.year_calendar_apple')
    if not files.get('year_calendar_google', '').startswith('https://calendar.google.com/calendar/r?cid='):
        raise ValueError('school.json needs a Google add link for files.year_calendar_google')
    if 'raw.githubusercontent.com' in files['year_calendar_apple'] + files['year_calendar_file']:
        raise ValueError('Calendar links must be served as text/calendar (GitHub Pages), not raw GitHub (text/plain)')
    form = pack.get('contact_form')
    if form:
        if not (form.get('url', '').startswith('https://') and form.get('prefill', '').startswith('https://')):
            raise ValueError('school.json contact_form needs https url and prefill links')
        lines += ['', 'Only if the parent wants to send feedback, a question or an idea to the parent who keeps this '
                  f'pack: give them the contact form, {form["url"]}. You may hand them a pre-filled link '
                  f'({form["prefill"]}, each value URL-encoded); they review it and submit it themselves. Leave '
                  'out their children\'s names and other family details.']
    senders = pack.get('suggested_school_senders')
    if senders:
        lines += ['', 'School mail usually comes from: ' + ', '.join(senders['names'] + senders['domains'])
                  + '. Suggestions only; the parent decides what you search.']
    return '\n'.join(lines) + '\n'


def render(root=ROOT):
    version = (root / 'skill/VERSION').read_text().strip()
    if not VERSION_RE.fullmatch(version):
        raise ValueError('Unsupported version')
    skill = (root / 'skill/SKILL.md').read_text()
    if '\r' in skill:
        raise ValueError('Use LF newlines: SKILL.md')
    fields, body = split_frontmatter(skill)
    if not body.rstrip().endswith(f'version {version}.'):
        raise ValueError('SKILL.md must end by naming skill/VERSION')
    # Every guide is listed in SKILL.md once, in reading order, and every listed guide exists.
    listed = REF_RE.findall(body)
    present = sorted({p.stem for p in (root / 'skill/references').glob('*.md')} | {SCHOOL_GUIDE})
    if len(set(listed)) != len(listed) or sorted(listed) != present:
        raise ValueError('SKILL.md must list each reference guide exactly once')
    if re.search(r'https?://', body):
        raise ValueError('Behavior must not link out (school links belong in schools/): SKILL.md')
    school = school_section(root)
    parts = [f'# School-parent kit {version}\n\n'
             'Single-file form of the skill folder: the main instructions, then each reference guide.\n',
             REF_RE.sub(lambda m: f'the "{m.group(1)}" guide below', body).rstrip() + '\n']
    for name in listed:
        guide = school if name == SCHOOL_GUIDE else (root / f'skill/references/{name}.md').read_text()
        if '\r' in guide or not guide.startswith('# '):
            raise ValueError(f'Untitled guide or CRLF: {name}')
        if name != SCHOOL_GUIDE and re.search(r'https?://', guide):
            raise ValueError(f'Behavior must not link out (school links belong in schools/): {name}')
        parts.append(f'\n---\n\n<!-- guide: {name} -->\n\n{guide.rstrip()}\n')
    parts.append(f'\n---\n\nEND OF SCHOOL-PARENT KIT {version}\n')
    guides = {name: school if name == SCHOOL_GUIDE else (root / f'skill/references/{name}.md').read_text()
              for name in listed}
    return {f'dist/{OUTPUT}': '\n'.join(parts).encode('utf-8'),
            f'skill/references/{SCHOOL_GUIDE}.md': school.encode('utf-8'),
            f'dist/{ZIP_OUTPUT}': skill_zip(fields['name'], skill, guides)}


def skill_zip(name, skill, guides):
    """The skill folder as an uploadable zip (<name>/SKILL.md, <name>/references/*.md). Stored, not compressed, with
    fixed timestamps, so the bytes are identical on every machine and CI can check the committed copy."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_STORED) as archive:
        files = [('SKILL.md', skill)] + [(f'references/{g}.md', text) for g, text in sorted(guides.items())]
        for path, text in files:
            info = zipfile.ZipInfo(f'{name}/{path}', date_time=(2026, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            archive.writestr(info, text.encode('utf-8'))
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if the generated file is absent or stale')
    args = parser.parse_args()
    try:
        for path, data in render().items():
            target = ROOT / path
            if args.check:
                if not target.exists() or target.read_bytes() != data:
                    raise ValueError(f'{path} is stale; run tools/build_skill.py')
                print(f'PASS: {path} is current')
            else:
                target.parent.mkdir(exist_ok=True)
                target.write_bytes(data)
                print(f'Wrote {path} ({len(data)} bytes)')
    except (OSError, ValueError, KeyError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
