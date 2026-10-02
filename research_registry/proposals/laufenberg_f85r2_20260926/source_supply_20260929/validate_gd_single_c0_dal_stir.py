#!/usr/bin/env python3
"""Recheck an exposed authored note's accounting, not meaning or all separators."""
import hashlib
import json
from pathlib import Path
import re

BASE = Path('research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929')
receipt = json.loads((BASE / 'GD_SINGLE_C0_DAL_STIR_RECEIPT_20261002.json').read_text())
note = Path(receipt['authored_note'])
assert hashlib.sha256(note.read_bytes()).hexdigest() == receipt['authored_note_sha256']
for item in receipt['input_bindings']:
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest() == item['sha256']
text = note.read_text()
source = json.loads(Path('experiments/yolo/gdt1115_final_formation_predication/src/SOURCE.json').read_text())
assert len(source['units']) == 4
assert {u['page'] for u in source['units']} == {'f77r', 'f115v'}
expected = {(u['edition'], line['locus']): line['words'] for u in source['units'] for line in u['lines']}
edition, seen = None, {}
for line in text.splitlines():
    heading = re.match(r'### (ZL3b|IT2a) ', line)
    if heading:
        edition = heading[1]
    row = re.match(r'^(f\d+\w*\.\d+) (.*)$', line)
    if row and edition:
        key = edition, row[1]
        assert key not in seen
        seen[key] = [word for word in row[2].split() if word not in ('/', '//')]
assert seen == expected
assert len(seen) == receipt['lines'] == 32
assert sum(map(len, seen.values())) == receipt['raw_groups'] == 238
pins = re.findall(r'^- `([^`]+)`: `([0-9a-f]{64})`$', text, re.M)
assert len(pins) == receipt['pinned_predecessors'] == 12
for path, digest in pins:
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
counter = json.loads(Path('experiments/yolo/gdt1116_joint_state_recipient_chain/src/SOURCE.json').read_text())
unit = next(u for u in counter['units'] if u['edition'] == 'IT2a' and u['page'] == 'f114r')
assert unit['id'] == receipt['counter_unit']
assert unit['lines'][-1]['end'] is True
assert unit['lines'][-1]['words'][-2:] == ['dal', 'chedy']
print(json.dumps({'status': 'SOURCE_ACCOUNTING_PASS', 'units': 4, 'lines': 32,
                  'groups': 238, 'pins': 12, 'semantic_validation': False,
                  'global_separator_validation': False}))
