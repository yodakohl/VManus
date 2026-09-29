#!/usr/bin/env python3
"""Validate accounting and replay, not meaning; same-author implementation."""
import csv
import json
from run import BASE, compute


def main():
    result, replay, tables = compute()
    assert result == json.loads((BASE / 'artifacts/RESULT.json').read_text())
    assert replay == json.loads((BASE / 'artifacts/FORMAL_REPLAY.json').read_text())
    for name, expected in tables.items():
        with (BASE / 'artifacts' / (name + '.tsv')).open() as f:
            actual = list(csv.DictReader(f, delimiter='\t'))
        assert actual == [{k: str(v) for k, v in r.items()} for r in expected], name
    for edition, n, d, adjacent in [('ZL3b', 60, 11, 1), ('IT2a', 57, 11, 1), ('RF1b', 59, 9, 0)]:
        s = result['summaries'][edition]
        assert (s['raw_groups'], s['physical_lines'], s['exact_daiin'], s['adjacent_daiin_pairs']) == (n, 7, d, adjacent)
    assert len(tables['FULL_PASSAGE']) == 21
    assert sum(r['count'] for r in tables['FORM_INVENTORY']) == 176
    assert result['fixed_semantic_tests'] == result['complete_semantic_candidates'] == result['confirmed_words'] == 0
    assert {c['package'] for c in tables['CANDIDATES']} == {'SNAKE', 'SCORPION', 'DOG'}
    out = dict(status='PASS', scope='complete raw accounting and deterministic formal replay only',
        semantic_validation=False, independent_validator=False, alternate_readings_not_independent=True,
        raw_groups=176, physical_lines_per_reader=7,
        sealed_data={'f84': 'FORBIDDEN_AND_ABSENT', 'f84r': 'FORBIDDEN_AND_ABSENT'})
    (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
