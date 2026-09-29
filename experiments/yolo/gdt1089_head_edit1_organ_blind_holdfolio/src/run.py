#!/usr/bin/env python3
"""Join frozen, word-blind visual inventories to registered pairs and controls."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SRC, ART = BASE / 'src', BASE / 'artifacts'
CODES = ('HORIZONTAL_BEADS', 'BASAL_SWOLLEN_BRANCHES', 'RADIATE_HEAD',
         'SPINY_ROUND_HEAD', 'BROAD_PETAL_FLOWER', 'MULTI_UNIT_SPIKE')

def read(path):
    with path.open(newline='') as fh:
        return list(csv.DictReader(fh, delimiter='\t'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, rows):
    with path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

def main():
    folios = [x['folio'] for x in read(SRC / 'BLIND_IMAGE_LIST.tsv')]
    source = read(ART / 'SOURCE.tsv')
    assert len(folios) == 38 and [x['folio'] for x in source] == folios
    assert sum(x['scope'] == 'NEW_GDT1089' for x in source) == 11
    for x in source:
        assert x['folio'] not in ('f84', 'f84r')
        assert len(x['sha256']) == 64 and int(x['bytes']) > 100000
    anno = {}
    for label in 'AB':
        rows = read(ART / f'BLIND_{label}.tsv')
        assert len(rows) == 38 and [x['folio'] for x in rows] == folios
        assert all(x[c] in ('YES', 'NO', 'UNKNOWN') for x in rows for c in CODES)
        anno[label] = {x['folio']: x for x in rows}
    targets, controls = read(SRC / 'FIXED_EDIT1_PAIRS.tsv'), read(SRC / 'FIXED_CONTROLS.tsv')
    assert len(targets) == len(controls) == 25
    assert sum(x['newly_covered'] == '1' for x in targets) == 14
    assert all((t['folio_a'], t['folio_b'], t['newly_covered']) ==
               (c['anchor_folio'], c['edit1_folio'], c['newly_covered'])
               for t, c in zip(targets, controls))
    assert all(x['folio_a'] in folios and x['folio_b'] in folios for x in targets)
    assert all(x['control_folio'] in folios for x in controls)

    def judge(left, right):
        definite, possible = [], []
        for code in CODES:
            lv, rv = [anno[a][left][code] for a in 'AB'], [anno[a][right][code] for a in 'AB']
            if lv == ['YES', 'YES'] and rv == ['YES', 'YES']:
                definite.append(code)
            # A code is definitely absent only when both readers say NO on a page.
            if lv != ['NO', 'NO'] and rv != ['NO', 'NO']:
                possible.append(code)
        return ('YES' if definite else 'UNDECIDABLE' if possible else 'NO',
                ','.join(definite), ','.join(possible))

    decisions = []
    for i, (t, c) in enumerate(zip(targets, controls), 1):
        for kind, right, head in (('TARGET', t['folio_b'], t['head_b']),
                                  ('CONTROL', c['control_folio'], c['control_head'])):
            status, shared, possible = judge(t['folio_a'], right)
            decisions.append(dict(pair_id=f'P{i:02d}', kind=kind,
                                  folio_a=t['folio_a'], folio_b=right,
                                  head_a=t['head_a'], head_b=head,
                                  newly_covered=t['newly_covered'], status=status,
                                  shared_codes=shared or "NONE", possible_codes=possible or "NONE"))
    write(ART / 'PAIR_DECISIONS.tsv', decisions)
    counts = {}
    for subset, rows in (('all', decisions),
                         ('newly_covered', [x for x in decisions if x['newly_covered'] == '1']),
                         ('previously_covered', [x for x in decisions if x['newly_covered'] == '0'])):
        counts[subset] = {kind: dict(Counter(x['status'] for x in rows if x['kind'] == kind))
                          for kind in ('TARGET', 'CONTROL')}
    nt, nc = counts['newly_covered']['TARGET'], counts['newly_covered']['CONTROL']
    ty, tu = nt.get('YES', 0), nt.get('UNDECIDABLE', 0)
    cy, cu = nc.get('YES', 0), nc.get('UNDECIDABLE', 0)
    tr, cr = (ty / (14-tu) if tu < 14 else None), (cy / (14-cu) if cu < 14 else None)
    wins = sum(decisions[2*i]['status'] == 'YES' and decisions[2*i+1]['status'] == 'NO'
               for i in range(25) if targets[i]['newly_covered'] == '1')
    distinct = len({tuple(sorted((x['head_a'], x['head_b']))) for x in decisions
                    if x['kind'] == 'TARGET' and x['newly_covered'] == '1' and x['status'] == 'YES'})
    if tu > 14/3:
        decision = 'INVALID_VISUAL_CAPACITY'
    elif ty >= 4 and distinct >= 3 and ((cr == 0 and wins >= 3) or
         (cr not in (None, 0) and tr is not None and tr >= 2*cr)):
        decision = 'EXPLORATORY_POSITIVE_ASSOCIATION'
    elif ty <= 1 or tr is not None and cr is not None and tr <= cr:
        decision = 'NEGATIVE_EXTENSION'
    else:
        decision = 'INCONCLUSIVE'
    result = dict(experiment='GDT1089', decision=decision, counts=counts,
                  new_target_yes_fraction=tr, new_control_yes_fraction=cr,
                  new_target_control_discordant_wins=wins,
                  new_distinct_yes_whole_form_pairs=distinct,
                  hashes={p.name: sha(p) for p in (ART/'SOURCE.tsv', ART/'BLIND_A.tsv', ART/'BLIND_B.tsv',
                                                    SRC/'FIXED_EDIT1_PAIRS.tsv', SRC/'FIXED_CONTROLS.tsv')},
                  claim_ceiling='Exploratory form-to-image association only; no significance or word meaning.')
    (ART / 'RESULT.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
