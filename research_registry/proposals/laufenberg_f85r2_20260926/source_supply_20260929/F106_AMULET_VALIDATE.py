"""Independent complete lexical accounting checks; no semantic inference."""
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path

base = Path(__file__).resolve().parent
repo = next(p for p in base.parents if (p / 'vmanus-work').exists())
out = json.loads((base / 'F106_AMULET_ACCOUNT.json').read_text())
checks = []


def check(name, condition):
    checks.append({'name': name, 'pass': bool(condition)})


for p, sha in out['input_hashes'].items():
    check('input unchanged: ' + p, hashlib.sha256((repo / p).read_bytes()).hexdigest() == sha)
parent = json.loads((repo / 'experiments/yolo/gdt1023_amulet_complete_typed_assembly/src/SOURCE.json').read_text())
extension = json.loads((repo / 'research_registry/proposals/raw_f108r_amulet_frozen71_complete_commentary_20260921.json').read_text())
lex = parent['lexicon'] | extension['new_17_lexical_entries']
check('all88 old values exact', out['unchanged_88_entries'] == lex and len(lex) == 88)
units = json.loads((repo / 'experiments/yolo/gdt999_typed_pair_frame_transfer/artifacts/MATCHING_PARAGRAPHS.json').read_text())
check('entire source records and flags copied', out['complete_units'] == units)
expected = [(u['edition'], l['locus'], i + 1, sid, w, l['anchor_eligible'])
            for u in units for l in u['paragraph']['lines']
            for i, (sid, w) in enumerate(zip(l['source_ids'], l['words']))]
actual = [(r['edition'], r['locus'], r['index'], r['source_id'], r['raw'], r['anchor_eligible']) for r in out['rows']]
check('all112 groups exact and in order', len(actual) == 112 and actual == expected)
forms = defaultdict(set)
for a in lex:
    forms[a].add((a,))
    for b in lex:
        forms[a + b].add((a, b))
check('all atomic/binary alternatives independently enumerated', all(
    {tuple(x) for x in r['alternatives']} == forms.get(r['raw'], set()) for r in out['rows']))
check('all meanings/tags copied from original entries', all(
    r['tags'] == [[lex[w]['tag'] for w in a] for a in r['alternatives']]
    and r['meanings'] == [[lex[w]['meaning'] for w in a] for a in r['alternatives']]
    for r in out['rows']))
for ed, n, k in [('ZL3b', 57, 13), ('IT2a', 55, 11)]:
    rows = [r for r in out['rows'] if r['edition'] == ed]
    check(ed + ' coverage and unknowns', len(rows) == n and sum(bool(r['alternatives']) for r in rows) == k
          and sum(not r['alternatives'] for r in rows) == 44
          and len({r['raw'] for r in rows if not r['alternatives']}) == 41)
    by = [r for r in rows if r['raw'] == 'otedy']
    check(ed + ' all BY positions inventoried', [r['locus'] for r in by] == ['f106r.43', 'f106r.46'])
    for row in by:
        next_row = next(r for r in rows if r['locus'] == row['locus'] and r['index'] == row['index'] + 1)
        check(ed + ' BY right group ' + row['locus'], next_row['raw'] == ('qokain' if row['locus'].endswith('.43') else 'qokeedy'))
    wing = [r for r in rows if r['raw'] == 'qokeedy']
    check(ed + ' exact two wing/state alternatives', len(wing) == 1 and wing[0]['tags'] == [['WING_TIP_OF'], ['ENCLOSED_STATE', 'AND']])
with (base / 'F106_AMULET_ALL_POSITIONS.tsv').open() as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
check('TSV retains every raw group and alternatives', len(rows) == 112 and all(
    a['source_id'] == b['source_id'] and a['raw'] == b['raw']
    and json.loads(a['alternatives']) == b['alternatives']
    for a, b in zip(rows, out['rows'])))
result = {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL',
          'check_count': len(checks), 'checks': checks,
          'ceiling': 'Source integrity, full accounting and inherited lexical alternatives only. Root separately reviews the typed consequence; no meaning validity or new source eligibility.'}
(base / 'F106_AMULET_VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'checks'}))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
