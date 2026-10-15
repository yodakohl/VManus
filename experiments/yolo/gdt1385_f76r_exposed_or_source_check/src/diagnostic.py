#!/usr/bin/env python3
"""Separate guided diagnostic; never overwrites the primary result."""
import json
from run import B, FIELDS, combine, consequences, read, sha


def main():
    spec = read(B / 'src/SPEC.json')
    diagnostic_spec = B / 'src/LOCALIZATION_DIAGNOSTIC_SPEC.json'
    primary = B / 'artifacts/RESULT.json'
    primary_hash = sha(primary)
    assert read(primary)['status'] == 'UNRESOLVED'
    paths = [B / 'artifacts/NATIVE_A.json', B / 'artifacts/NATIVE_B2_GUIDED.json']
    records = [read(p) for p in paths]
    for row in records:
        assert all(k in row for k in spec['required_fields'])
        assert row['image_sha256'] == spec['image']['sha256']
        assert type(row['localized']) is bool
        for field in FIELDS:
            assert row[field] in spec['ratings'][field]
    combined = combine(*records)
    status, cap = consequences(combined)
    result = {
        'experiment_id': 'GDT1385',
        'phase': 'ONE_POST_RESULT_GUIDED_LOCALIZATION_DIAGNOSTIC',
        'status': status, 'combined': combined, 'p2_consequence': cap,
        'original_result_status': 'UNRESOLVED',
        'original_result_sha256': primary_hash,
        'diagnostic_spec_sha256': sha(diagnostic_spec),
        'record_sha256': {p.name: sha(p) for p in paths},
        'limits': [
            'A and B2 share the root-provided locator; not independent localization.',
            'B2 is the same observer B after one orientation clarification, not a third observer.',
            'A ratings were withheld from B2; both know the competing source readings.',
            'Primary A/B1 result and GDT1384 remain unchanged.',
            'Local comparative compatibility only; no word boundary, alphabet or meaning selected.',
        ],
    }
    (B / 'artifacts/DIAGNOSTIC_RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    assert sha(primary) == primary_hash
    print(json.dumps({'phase': result['phase'], 'status': status, 'combined': combined}))


if __name__ == '__main__':
    main()
