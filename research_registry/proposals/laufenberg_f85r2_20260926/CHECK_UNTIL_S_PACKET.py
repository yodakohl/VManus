#!/usr/bin/env python3
"""Check frozen literal coverage; no interpretation or temporal simulation."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
PACKET = BASE / 'until_s_draft'
checks = []


def require(value, name):
    if not value:
        raise AssertionError(name)
    checks.append(name)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open() as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


receipt = json.loads((PACKET / 'FREEZE_RECEIPT.json').read_text())
for name, expected in receipt['files'].items():
    require(digest(PACKET / name) == expected, 'freeze:' + name)
draft = json.loads((PACKET / 'DRAFT.json').read_text())
native_path = ROOT / 'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv'
require(digest(native_path) == 'e50307f834b04ff2ce17a97f14fd2c7b3f24b4818bc7fda3f57c372afc6b9d3c', 'declared native input')
guard_path = ROOT / receipt['input']['path']
require(digest(guard_path) == receipt['input']['sha256'], 'actual author input')
native, guarded = rows(native_path), rows(guard_path)
require(len(native) == len(guarded) == 473, 'complete owned row counts')
keys = ['edition', 'locus', 'source_group_id', 'source_group_index',
        'source_group_count', 'paragraph_start', 'paragraph_end',
        'left_separator', 'right_separator', 'ivtff_group_raw']
require(all(tuple(a[k] for k in keys) == tuple(b[k] for k in keys)
            for a, b in zip(native, guarded)), 'all shared source fields unchanged')
old = draft['fixed_idea550_bindings']
new = draft['new_whole_form_values']
require(set(old) == {'chey', 'sorain', 'orar'}, 'three seed forms')
require([old[k]['type'] for k in ('chey', 'sorain', 'orar')] ==
        ['Event -> TemporalGuard', 'Event', 'Event'], 'seed types preserved')
require(len(new) == 21 and not(set(new) & set(old)), '21 new values without overwrite')
lex = {**old, **new}
expected = {r['source_group_id']: r for r in native if r['ivtff_group_raw'] in lex}
observed = rows(PACKET / 'ASSIGNED_OCCURRENCES.tsv')
require(len(observed) == len(expected) == 125, '125 assigned positions')
require(len({r['group_id'] for r in observed}) == 125, 'no duplicate inventory identities')
require(set(expected) == {r['group_id'] for r in observed}, 'all and only exact matches')
contexts = defaultdict(list)
for r in native:
    contexts[(r['edition'], r['locus'])].append(r['ivtff_group_raw'])
for r in observed:
    src = expected[r['group_id']]
    require(r['surface_exact'] == src['ivtff_group_raw'] and
            r['edition'] == src['edition'] and r['locus'] == src['locus'] and
            r['group_index'] == src['source_group_index'], 'identity:' + r['group_id'])
    require(r['raw_group_context'] == ' '.join(contexts[(r['edition'], r['locus'])]),
            'whole context:' + r['group_id'])
    require(r['meaning'] == lex[r['surface_exact']]['meaning'] and
            r['type'] == lex[r['surface_exact']]['type'], 'literal value:' + r['group_id'])
zl_s = [r for r in native if r['edition'] == 'ZL3b' and r['block'] == 'S']
require(len(zl_s) == 26 and len({r['ivtff_group_raw'] for r in zl_s}) == 24, 'whole ZL S')
require(set(lex) == {r['ivtff_group_raw'] for r in zl_s}, 'no omitted ZL S type')
parsed = ' '.join(x['surface'] for x in draft['zl3b_parse']).split()
require(parsed == [r['ivtff_group_raw'] for r in zl_s], 'parse display preserves every raw group in order')
coverage = {}
for edition in ('ZL3b', 'IT2a', 'RF1b'):
    sr = [r for r in native if r['edition'] == edition and r['block'] == 'S']
    coverage[edition] = {'assigned_S': sum(r['ivtff_group_raw'] in lex for r in sr),
                         'unassigned_S': [r['ivtff_group_raw'] for r in sr if r['ivtff_group_raw'] not in lex],
                         'outside_S': sum(r['edition'] == edition and r['block'] != 'S' for r in expected.values())}
result = {'status': 'PASS', 'checked_utc': datetime.now(timezone.utc).isoformat(),
          'check_count': len(checks), 'checks': checks,
          'all_occurrences': dict(Counter(r['edition'] for r in observed)),
          'coverage': coverage, 'author_freeze_timestamp_validated': False,
          'author_freeze_timestamp_correction': 'manually entered20:33 withdrawn by author; hashes retained',
          'meaning': 'literal conservation and input equivalence only; no typed semantic execution or confirmed word'}
(BASE / 'UNTIL_S_INTEGRITY_RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ('status', 'checked_utc', 'check_count', 'all_occurrences', 'coverage')}))
