#!/usr/bin/env python3
"""Mechanical agreement of informed visual records; no image display."""
import hashlib
import json
from pathlib import Path


def find_repo_root(start):
    for candidate in (start, *start.parents):
        if (candidate / 'vmanus-work').is_file():
            return candidate
    raise RuntimeError('VManus tool entry point not found')


ROOT = find_repo_root(Path(__file__).resolve().parent)
B = Path(__file__).resolve().parents[1]
FIELDS = ('middle_body', 'left_seam', 'right_seam')
LIMITS = [
    'Agreement of two informed records from one exposed image only.',
    'No word meaning, independent manuscript confirmation, or preferred transcription proof.',
    'Software cannot verify observer alignment, visual judgment, authority, or actual blinding.',
    'Source permission interpretation belongs to the recorded root scope decision, not this program.',
    'GDT1384 and all older decisions remain unchanged.',
]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def combine(a, b):
    return {field: a[field] if a['localized'] is True and b['localized'] is True
            and a[field] == b[field] and a[field] != 'UNRESOLVED'
            else 'UNRESOLVED' for field in FIELDS}


def consequences(combined):
    middle = combined['middle_body']
    if middle == 'A_LIKE':
        return 'LOCAL_AR_COMPATIBILITY', 'AR_BRANCH_SUPPORTED_NOT_P2_CONFIRMED'
    if middle == 'O_LIKE':
        cap = ('CONDITIONAL_THREE_OR_COUNTERCASE'
               if combined['left_seam'] == combined['right_seam'] == 'SPACE_LIKE'
               else 'UNRESOLVED')
        return 'LOCAL_OR_COMPATIBILITY', cap
    return 'UNRESOLVED', 'UNRESOLVED'


def main():
    spec_path = B / 'src/SPEC.json'
    spec = read(spec_path)
    paths = [B / 'artifacts/NATIVE_A.json', B / 'artifacts/NATIVE_B.json']
    records = [read(path) for path in paths]
    for record in records:
        if not all(key in record for key in spec['required_fields']):
            raise ValueError('Missing required observation field')
        if type(record['localized']) is not bool:
            raise ValueError('localized must be Boolean')
        if record['image_sha256'] != spec['image']['sha256']:
            raise ValueError('Observation image hash does not match fixed image')
        for field in FIELDS:
            if record[field] not in spec['ratings'][field]:
                raise ValueError('Observation category outside fixed inventory')
    combined = combine(*records)
    status, cap = consequences(combined)
    result = {
        'schema_version': 1, 'experiment_id': 'GDT1385',
        'status': status, 'combined': combined, 'p2_consequence': cap,
        'spec_sha256': sha(spec_path),
        'scope_decision_sha256': spec['scope_decision_sha256'],
        'image_sha256': spec['image']['sha256'],
        'record_sha256': {path.name: sha(path) for path in paths},
        'both_localized': all(record['localized'] for record in records),
        'limits': LIMITS,
    }
    (B / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': status, 'combined': combined, 'p2_consequence': cap}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
