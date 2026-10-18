#!/usr/bin/env python3
"""Build/check a complete prompt bundle using only the Python standard library."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    'core/PRINCIPLES.md', 'core/SETUP.md', 'core/TRIAGE.md',
    'contracts/SCHOOL-PACK.md', 'contracts/HOST.md',
    'contracts/HOUSEHOLD.md', 'contracts/VERSIONING.md',
)
VERSION_RE = re.compile(r'\d+\.\d+\.\d+-draft\.\d+\Z')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def render(root=ROOT):
    config = json.loads((root / 'manifest.json').read_text())
    if set(config) != {'format_version', 'behavior_version', 'modules'}:
        raise ValueError('Unexpected manifest fields')
    if config['format_version'] != 1 or not VERSION_RE.fullmatch(config['behavior_version']):
        raise ValueError('Unsupported manifest format or draft version')
    if config['modules'] != list(REQUIRED):
        raise ValueError('Manifest must contain the complete ordered module set exactly once')
    # Catch accidentally added maintained instructions that were not bundled.
    discovered = {str(p.relative_to(root)) for folder in ('core', 'contracts')
                  for p in (root / folder).rglob('*.md')}
    if discovered != set(REQUIRED):
        raise ValueError('Missing or unlisted maintained module')
    version = config['behavior_version']
    parts = [f'# Complete Parent Kit · {version}\n\nLOCAL REVIEW DRAFT. No live host validation.\n\n'
             'All behavioral modules are included below. School facts and private family data are not included.\n\n'
             'Behavior version: ' + version + '\n\nModule inventory:\n' +
             ''.join(f'- {name}\n' for name in REQUIRED)]
    records = []
    for name in REQUIRED:
        raw = (root / name).read_bytes()
        content = raw.decode('utf-8')
        if not content.strip() or not content.startswith('# '):
            raise ValueError(f'Empty or untitled module: {name}')
        if '\r' in content:
            raise ValueError(f'Use LF newlines: {name}')
        # No behavior depends on external or relative files. Source URLs belong
        # to independent evidence packs, not this complete instruction bundle.
        checked_content = content
        if name == 'contracts/SCHOOL-PACK.md':
            # Exact default evidence references only; never permit remote behavior.
            for evidence_file in ('school-facts.md', 'school-dates.md', 'school-menu.md',
                                  'senders.json', 'topics/INDEX.md'):
                checked_content = checked_content.replace(
                    'https://raw.githubusercontent.com/RohanHL/sees-agent-parent-kit/main/' + evidence_file, '')
        if re.search(r'\]\([^)]*\)|https?://|\[\[[^]]+\]\]', checked_content):
            raise ValueError(f'Behavioral dependency/link is not self-contained: {name}')
        records.append({'path': name, 'sha256': sha(raw), 'bytes': len(raw)})
        parts.append(f'\n---\n\n<!-- BEGIN MODULE {name} -->\n\n{content.rstrip()}\n\n<!-- END MODULE {name} -->\n')
    parts.append(f'\nEND COMPLETE PARENT KIT {version}\n')
    bundle = '\n'.join(parts).encode('utf-8')
    manifest = {'format_version': 1, 'behavior_version': version,
                'bundle': 'PARENT-KIT.md', 'bundle_sha256': sha(bundle),
                'modules': records}
    return bundle, (json.dumps(manifest, indent=2, ensure_ascii=False) + '\n').encode()


def validate_examples(root=ROOT):
    """Validate our two fixtures, not arbitrary host data or a production schema."""
    version = json.loads((root / 'manifest.json').read_text())['behavior_version']
    cp = json.loads((root / 'examples/session-checkpoint.json').read_text())
    hp = json.loads((root / 'examples/host-profile.json').read_text())
    if cp['synthetic'] is not True or hp['synthetic'] is not True:
        raise ValueError('Examples must be explicitly synthetic')
    if cp['schema_version'] != 1 or cp['behavior_version'] != version:
        raise ValueError('Checkpoint schema/version mismatch')
    if cp['persistence'] != 'session_only' or cp['read_scope'] != {
        'accounts': [], 'senders': [], 'permission_evidence': None
    }:
        raise ValueError('Illustrative fixture cannot grant access or persistence')
    if hp['profile_status'] != 'illustrative_unverified' or hp['evidence']:
        raise ValueError('Host example must not claim verification')
    allowed = {'unknown', 'unavailable', 'verified'}
    for capabilities in (cp['capabilities'], hp['capabilities']):
        if not set(capabilities.values()) <= allowed:
            raise ValueError('Invalid capability state')
    if any(value != 'unknown' for value in hp['capabilities'].values()):
        raise ValueError('Host example must be entirely unverified')
    children = {c['id'] for c in cp['children']}
    events = {e['id']: e for e in cp['occurrences']}
    if len(children) != len(cp['children']) or len(events) != len(cp['occurrences']):
        raise ValueError('Duplicate fixture identities')
    for event in events.values():
        if not set(event['children']) <= children:
            raise ValueError('Dangling occurrence child')
    for task in cp['obligations']:
        if task['occurrence_id'] not in events or task['child_id'] not in children:
            raise ValueError('Dangling obligation reference')
        if task['child_id'] not in events[task['occurrence_id']]['children']:
            raise ValueError('Obligation child outside occurrence')
        if task['status'] not in {'unknown', 'outstanding', 'completed', 'superseded'}:
            raise ValueError('Invalid obligation state')
        if task['status'] == 'completed' and not task['evidence']:
            raise ValueError('Completion requires evidence')
    recurring = cp['recurring']
    if recurring != {'readiness': 'on_demand', 'health': 'unknown', 'approval': None,
                     'job_id': None, 'first_delivery_evidence': None}:
        raise ValueError('Illustrative fixture must remain on demand')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if generated files are absent or stale')
    args = parser.parse_args()
    try:
        validate_examples()
        outputs = dict(zip(('PARENT-KIT.md', 'bundle-manifest.json'), render()))
        if args.check:
            for name, data in outputs.items():
                target = ROOT / 'dist' / name
                if not target.exists() or target.read_bytes() != data:
                    raise ValueError(f'Missing/stale generated file: dist/{name}')
            print('PASS: complete, coherent, reproducible bundle and synthetic examples')
        else:
            (ROOT / 'dist').mkdir(exist_ok=True)
            for name, data in outputs.items():
                (ROOT / 'dist' / name).write_bytes(data)
            print('Built dist/PARENT-KIT.md and dist/bundle-manifest.json')
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
