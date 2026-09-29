#!/usr/bin/env python3
"""Post-result presentation check only; does not amend the frozen scientific test."""
import csv
import json
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'artifacts'
rows = json.loads((p / 'CASES.json').read_text())
with (p / 'CANDIDATES.tsv').open() as stream:
    table = list(csv.DictReader(stream, delimiter='\t'))
assert len(table) == len(rows)
for row, display in zip(rows, table):
    for key, value in display.items():
        assert value == ('NA' if row.get(key) is None else str(row[key])), key
result = dict(status='PASS', rows=len(rows),
              check='Every published TSV cell equals its corresponding primary CASES.json value; post-result presentation validation only.')
(p / 'TABLE_VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
