#!/usr/bin/env python3
"""Independent source coverage checks; cannot validate any word meaning."""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
BASE = Path(__file__).resolve().parent
saved = list(csv.DictReader((BASE / 'BM_F56_PROJECTED.tsv').open(), delimiter='\t'))
fields = list(saved[0])
raw = subprocess.check_output([
    str(ROOT / 'vmanus-exp'), 'query-tsv',
    'experiments/semantic_assumptions/results/source_separator_transcription.tsv',
    '--selector', 'page', '--allow', 'f56r', '--columns', ','.join(fields)],
    cwd=ROOT, text=True)
actual = list(csv.DictReader(io.StringIO(raw), delimiter='\t'))
assert actual == saved and len(actual) == 301
units = json.loads((BASE / 'BM_COMPLETE_CONTEXTS.json').read_text())
flat = [r for u in units for line in u['lines'] for r in line['groups']]
assert {r['source_group_id']: r for r in actual} == {r['source_group_id']: r for r in flat}
assert len(flat) == len(actual)
observed = {}
for u in units:
    e, label = u['edition'], u['unit']
    target = list(range(1, 9)) if label == 'A' else list(range(9, 20))
    assert [int(line['locus'].split('.')[1]) for line in u['lines']] == target
    assert u['group_count'] == sum(len(line['groups']) for line in u['lines'])
    for line in u['lines']:
        assert all(r['edition'] == e and r['locus'] == line['locus'] for r in line['groups'])
        observed[(e, line['locus'])] = [r['ivtff_group_raw'] for r in line['groups']]
    flags = [(set(r['paragraph_start'] for r in line['groups']),
              set(r['paragraph_end'] for r in line['groups'])) for line in u['lines']]
    if e == 'RF1b':
        assert u['boundary_basis'] == 'aligned_window'
        assert all(a == b == {'0'} for a, b in flags)
    else:
        assert u['boundary_basis'] == 'native_flags'
        assert [i for i, (a, b) in enumerate(flags) if a == {'1'}] == [0]
        assert [i for i, (a, b) in enumerate(flags) if b == {'1'}] == [len(flags) - 1]
for e in ('ZL3b', 'IT2a', 'RF1b'):
    assert observed[(e, 'f56r.8')] == ['schol', 'choy', 'choky', 'cheeckhody']
    assert observed[(e, 'f56r.7')] == ['sho', 'kchol', 'otchor', 'choky', 'dal']
    assert observed[(e, 'f56r.14')] == (['schol', 'chotol', 'qotchy'] if e == 'IT2a'
                                      else ['s', 'chol', 'chotol', 'qotchy'])
    assert observed[(e, 'f56r.15')][-2:] == ['chol', 'cthy']
    assert observed[(e, 'f56r.16')][0] == 'qotchy'
    assert not any('chol' in observed[(e, f'f56r.{n}')] for n in range(9, 14))
result = json.loads((BASE / 'BM_RESULT.json').read_text())
assert result['projected_groups'] == len(actual)
assert result['native_paragraphs'] == 2 and result['physical_leaf_count'] == 1
assert result['confirmed_words'] == result['independent_confirmation_capacity'] == 0
assert result['semantic_validation'] is result['significance_claim'] is False
bound = [p for p in BASE.glob('BM_*') if p.is_file() and p.name != 'BM_VALIDATION.json']
receipt = {'status': 'PASS_SOURCE_COVERAGE_ONLY', 'projected_groups': 301,
           'native_paragraphs': 2, 'rf_native_paragraphs': 0,
           'meaning_validated': False,
           'files': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(bound)}}
(BASE / 'BM_VALIDATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'files'}, indent=2))
