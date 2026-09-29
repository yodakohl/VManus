"""Document integrity only. No semantic parsing, solver or target acquisition."""
import csv
import hashlib
import json
from pathlib import Path

base = Path(__file__).resolve().parent
repo = next(p for p in base.parents if (p / 'vmanus-work').exists())
checks = []


def check(name, condition):
    checks.append({'name': name, 'pass': bool(condition)})


inputs = json.loads((base / 'X_INPUTS.json').read_text())
for row in inputs['inputs']:
    actual = hashlib.sha256((repo / row['path']).read_bytes()).hexdigest()
    check('unchanged input: ' + row['path'], actual == row['sha256'])

data = json.loads((base / 'X_COMPLETE_UNITS.json').read_text())
summary = json.loads((base / 'X_ACCOUNT_SUMMARY.json').read_text())
with (base / 'X_WHOLE_ACCOUNT.tsv').open() as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
original = json.loads((base / 'R_COMPLETE_UNITS.json').read_text())
check('f75v complete units copied exactly', data['f75v_complete_units'] == original)
flat = [(u['edition'], g) for u in original['units'] for line in u['lines'] for g in line['groups']]
check('all 225 f75v groups retained', len(rows) == len(flat) == 225)
check('all raw groups, IDs and separators exact', all(
    (r['edition'], r['source_group_id'], r['raw'], r['left_separator'], r['right_separator'])
    == (ed, g[0], g[2], g[3], g[4]) for r, (ed, g) in zip(rows, flat)))
check('nine inherited choices', len(data['inherited_nine_hypotheses']) == 9)
check('24 older meanings retained', len(data['older_full_hypothesis_for_comparison']['all_24_meanings_exact']) == 24)
check('40 later values retained', len(data['GDT1025_40_new_whole_values_for_comparison']) == 40)
for ed, expected in {'ZL3b': (75, 17, 10, 48, 2, 1), 'IT2a': (77, 17, 11, 49, 3, 0), 'RF1b': (73, 16, 8, 49, 2, 1)}.items():
    selected = [r for r in rows if r['edition'] == ed]
    actual = (len(selected),
              sum(r['status'] == 'INHERITED_C0_LEXICAL_CHOICE' for r in selected),
              sum(r['status'] == 'NEW_UNSELECTED_C0_OPERATOR_OR_COMPOSITION' for r in selected),
              sum(r['status'] == 'UNKNOWN_IN_THIS_PARTIAL_DRAFT' for r in selected),
              sum(r['raw'] == 'qokar' for r in selected),
              sum(r['raw'] == 'qotar' for r in selected))
    check(ed + ' full coverage / unknowns / qokar / qotar', actual == expected)
check('all nine qokar/qotar positions inventoried', summary['all_qokar_qotar_occurrences'] == [r for r in rows if r['raw'] in ('qokar', 'qotar')])
check('complete old f83r paragraph .25-.30', data['f83r_25_30']['diplomatic_record']['groups'] == 33 and len(data['f83r_25_30']['diplomatic_record']['lines']) == 6)
check('complete older f83r paragraph .18-.24', data['f83r_18_24']['record']['groups'] == 63 and len(data['f83r_18_24']['record']['lines']) == 7)
check('two unnormalized old raw/projection differences retained', len(data['f83r_25_30']['known_differences']) == 2)
result = {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL', 'claim_ceiling': 'Document integrity only; no translation, semantic test, novelty proof or registry review.', 'check_count': len(checks), 'checks': checks}
(base / 'X_VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'checks'}, ensure_ascii=False))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
