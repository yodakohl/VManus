"""Validate preserved documents only; no target search or semantic execution."""
from pathlib import Path
import csv
import hashlib
import json

base = Path(__file__).resolve().parent
repo = next(p for p in base.parents if (p / 'vmanus-work').exists())
checks = []


def check(name, condition):
    checks.append({'name': name, 'pass': bool(condition)})


receipt = json.loads((base / 'Y_ADD_RECEIPT.json').read_text())
check('registered author bytes unchanged', hashlib.sha256((repo / receipt['author_file']).read_bytes()).hexdigest() == receipt['author_sha256'])
inputs = json.loads((base / 'Y_INPUTS.json').read_text())
for row in inputs['inputs']:
    check('unchanged input: ' + row['path'], hashlib.sha256((repo / row['path']).read_bytes()).hexdigest() == row['sha256'])
for left, right in [('Y_COMPLETE_UNITS.json', 'W_COMPLETE_UNITS.json'), ('Y_COMPLETE_UNITS.md', 'W_COMPLETE_UNITS.md'), ('Y_SOURCE_COMPLETE_PASSAGES.txt', 'Q_OWNED_CELESTIAL_DRAW_PASSAGES.txt')]:
    check('byte-exact copy: ' + left, (base / left).read_bytes() == (base / right).read_bytes())
with (base / 'Y_WHOLE_ACCOUNT.tsv').open() as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
source = json.loads((repo / 'experiments/yolo/gdt1051_frozen_grammar_local_application/artifacts/RESULT.json').read_text())['groups']
check('all288 groups retained', len(rows) == len(source) == 288)
check('raw forms separators source order and frozen formal analyses retained', all(
    all(str(s[k]) == r[k] for k in ['part', 'edition', 'locus', 'index', 'raw', 'left_separator', 'right_separator'])
    and json.loads(r['frozen_formal_analysis']) == s['wrapper_host']
    and r['frozen_formal_status'] == s['parse_status'] for r, s in zip(rows, source)))
summary = json.loads((base / 'Y_ACCOUNT_SUMMARY.json').read_text())
for ed, count in {'ZL3b': (95, 10, 85), 'IT2a': (97, 11, 86), 'RF1b': (96, 12, 84)}.items():
    rs = [r for r in rows if r['edition'] == ed]
    check(ed + ' whole accounting', (len(rs), sum(r['Y_status'] != 'UNKNOWN_UNASSIGNED' for r in rs), sum(r['Y_status'] == 'UNKNOWN_UNASSIGNED' for r in rs)) == count)
check('16 authored application occurrences recorded', len(summary['all_literal_proposed_applications']) == 16)
check('all9 opening/internal first-word-family occurrences unassigned', len(summary['openings_all_literal_occurrences']) == 9 and all(r['meaning'].startswith('UNASSIGNED') for r in summary['openings_all_literal_occurrences']))
indexed = {r['source_group_id']: r for r in rows}
check('authored right partners point to actual retained literal groups', all(indexed[p['expression_id']]['raw'] == p['expression'] and indexed[p['proposed_right_argument_id']]['raw'] == p['proposed_right_argument'] for p in summary['all_literal_proposed_applications']))
card = json.loads((base / 'Y_01_LUMINARY_INCORPORATION.json').read_text())
check('RAW unreviewed status retained', 'RAW_UNREVIEWED' in card['summary'])
check('explicit named-unit-only scope, no all-prose extension offer', 'ONLY' in card['design']['application_scope']['offered_scope'] and 'does NOT offer' in card['design']['application_scope']['offered_scope'])
check('countercase qualification retained before add', 'not yet six/six/five source-boundary-certified' in card['design']['known_countercases_before_registration'][0])
check('no observed okoar invented', not any(r['raw'] == 'okoar' for r in rows) and 'no occurrence' in card['design']['application_scope']['unobserved_output'])
out = {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL', 'check_count': len(checks), 'claim_ceiling': 'Document integrity only. The authored roles are not tested or confirmed; no repeat separator/paragraph inspection or external semantic test is performed.', 'checks': checks}
(base / 'Y_VALIDATION.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in out.items() if k != 'checks'}, ensure_ascii=False))
raise SystemExit(0 if out['status'] == 'PASS' else 1)
