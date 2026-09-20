#!/usr/bin/env python3
"""Post-result saved-table audit only; no matching or new target search."""
import collections
import csv
import gzip
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
A = E / 'artifacts'
P = E.parent / 'gdt990_smaragdina_complete_role_frames/artifacts'

def read_gz(path):
    return json.loads(gzip.decompress(path.read_bytes()))

cases = read_gz(A / 'CASES.json.gz')
old = {r['case']: r for r in read_gz(P / 'INTERRUPTED_CASES.json.gz')}
journals = {}
for name in ('PATTERN', 'REVERSE'):
    records = [json.loads(x) for x in (A / f'{name}_JOURNAL.jsonl').read_text().splitlines()]
    journals[name] = {r['case']: r['outcome'] for r in records}
    assert len(records) == len(journals[name])
assert len(cases) == len(old) == 32376
assert len({r['case'] for r in cases}) == len(cases)
eligible = {n for n, r in old.items() if r['status'] == 'UNKNOWN_UNRETAINED_SOLVER_RESULT'}
assert set(journals['PATTERN']) == eligible and len(eligible) == 1980
negatives = {n for n, r in journals['PATTERN'].items() if r['status'] == 'NO_COMPLETE_ROLE_FORM_PATTERN'}
assert set(journals['REVERSE']) == negatives and len(negatives) == 1407
for r in cases:
    o = old[r['case']]
    for key in ('edition', 'paragraph', 'page', 'leaf', 'variant', 'writer', 'source_forms', 'target_groups'):
        assert r[key] == o[key], (r['case'], key)
    assert r['original_status'] == o['status']
    if r['case'] not in eligible:
        assert r['status'] == o['status']
        continue
    m = journals['PATTERN'][r['case']]
    assert r['pattern'] == m
    if m['status'] == 'UNKNOWN_PATTERN_LIMIT':
        assert r['status'] == 'UNKNOWN_PATTERN_LIMIT'
    else:
        assert m['status'] == 'NO_COMPLETE_ROLE_FORM_PATTERN'
        rev = journals['REVERSE'][r['case']]
        assert r['reverse'] == rev
        expected = ('CONTRADICTED_COMPLETE_ROLE_FORM_PATTERN' if rev['status'] == 'REVERSE_EXHAUSTED'
                    else 'PRIMARY_PATTERN_EXHAUSTION_UNCORROBORATED')
        assert rev['status'] in ('REVERSE_EXHAUSTED', 'UNKNOWN_REVERSE_LIMIT')
        assert r['status'] == expected
with (A / 'CANDIDATES.tsv').open() as handle:
    table = list(csv.DictReader(handle, delimiter='\t'))
assert len(table) == len(cases)
for row, case in zip(table, cases):
    assert all(row[k] == str(case[k]) for k in row), case['case']
counts = collections.Counter(r['status'] for r in cases)
result = json.loads((A / 'RESULT.json').read_text())
assert dict(counts) == result['status_counts']
assert counts['CONTRADICTED_COMPLETE_ROLE_FORM_PATTERN'] == 108
assert result['original_equations_remaining_unresolved'] == 1872
assert result['saved_pattern_witnesses'] == result['original_code_witness_cases'] == 0
assert result['fixed_ninety_percent_stop'] is True
assert read_gz(A / 'COMPLETE_ALIGNMENTS.json.gz') == []
statuses = sorted(counts)
groups = collections.defaultdict(collections.Counter)
for r in cases:
    groups[(r['variant'], r['writer'])][r['status']] += 1
assert len(groups) == 24
with (A / 'MODEL_SUMMARY.tsv').open('w') as handle:
    writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
    writer.writerow(['variant', 'writer', 'all_cases', *statuses])
    for (variant, order), c in sorted(groups.items()):
        writer.writerow([variant, order, sum(c.values()), *(c[s] for s in statuses)])
out = dict(status='PASS', scope='saved journal/table identity and accounting only; no new search',
           cases=len(cases), model_groups=len(groups), primary_jobs=len(eligible),
           reverse_jobs=len(negatives), confirmed_new_negatives=108, unresolved=1872,
           source_unknown=counts['UNKNOWN_SOURCE'], independent_meaning_capacity=0,
           files={n: hashlib.sha256((A / n).read_bytes()).hexdigest() for n in
                  ('CASES.json.gz', 'CANDIDATES.tsv', 'PATTERN_JOURNAL.jsonl', 'REVERSE_JOURNAL.jsonl',
                   'MODEL_SUMMARY.tsv', 'RESULT.json')})
(A / 'REPORTING_AUDIT.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
