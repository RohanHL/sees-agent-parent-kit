#!/usr/bin/env python3
"""Build/check the single-file form of skill/ for hosts that can't load a skill folder."""
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'school-parent-kit.md'
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
    present = sorted(p.stem for p in (root / 'skill/references').glob('*.md'))
    if len(set(listed)) != len(listed) or sorted(listed) != present:
        raise ValueError('SKILL.md must list each reference guide exactly once')
    parts = [f'# School-parent kit {version}\n\n'
             'Single-file form of the skill folder: the main instructions, then each reference guide.\n',
             REF_RE.sub(lambda m: f'the "{m.group(1)}" guide below', body).rstrip() + '\n']
    for name in listed:
        guide = (root / f'skill/references/{name}.md').read_text()
        if '\r' in guide or not guide.startswith('# '):
            raise ValueError(f'Untitled guide or CRLF: {name}')
        if re.search(r'https?://', guide + body):
            raise ValueError(f'Behavior must not link out (school links belong in schools/): {name}')
        parts.append(f'\n---\n\n<!-- guide: {name} -->\n\n{guide.rstrip()}\n')
    parts.append(f'\n---\n\nEND OF SCHOOL-PARENT KIT {version}\n')
    return '\n'.join(parts).encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if the generated file is absent or stale')
    args = parser.parse_args()
    try:
        data = render()
        target = ROOT / 'dist' / OUTPUT
        if args.check:
            if not target.exists() or target.read_bytes() != data:
                raise ValueError(f'dist/{OUTPUT} is stale; run tools/build_skill.py')
            print(f'PASS: dist/{OUTPUT} matches skill/')
        else:
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(data)
            print(f'Wrote dist/{OUTPUT} ({len(data.split())} words)')
    except (OSError, ValueError, KeyError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
