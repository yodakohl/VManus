#!/usr/bin/env python3
"""Account for two already guarded lines; no image parser or language decoder."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
G0 = BASE / 'HAND_WRITER_NATIVE_G0_20261004.json'
RAW = BASE / 'runtime/hand_writer_f25v_two_lines_raw.tsv'
RECEIPT = BASE / 'runtime/hand_writer_f25v_two_lines_receipt.json'
G0_SHA = '04f272e17ca6863a730fb66b869079c667115fff938cd594415a41c466215c0b'


def account(surface, recipes, allow_insertion=False):
    parts = []
    pos = 0
    while pos < len(surface):
        candidate = surface[pos:pos + 3]
        if (allow_insertion and len(candidate) == 3
                and candidate[0] == 'c' and candidate[1] in 'ktpf'
                and candidate[2] == 'h'):
            parts.append({'surface': candidate,
                          'recipe': 'INSERT(BE,' + recipes[candidate[1]]['code'] + ')',
                          'resolved_symbolically': True})
            pos += 3
            continue
        candidate = surface[pos:pos + 2]
        if candidate not in ('ch', 'sh'):
            candidate = surface[pos]
        record = recipes.get(candidate)
        parts.append({'surface': candidate,
                      'recipe': record['code'] if record else 'UNKNOWN[' + candidate + ']',
                      'resolved_symbolically': record is not None})
        pos += len(candidate)
    assert ''.join(x['surface'] for x in parts) == surface
    return parts


def main():
    assert hashlib.sha256(G0.read_bytes()).hexdigest() == G0_SHA
    receipt = json.loads(RECEIPT.read_text())
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == receipt['selected_output_sha256']
    recipes = json.loads(G0.read_text())['motif_recipes']
    # RAW is the exact output of selector-first query-tsv, not a mixed source.
    with RAW.open(newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert len(rows) == 53
    assert {r['locus'] for r in rows} == {'f25v.1', 'f25v.2'}
    assert {r['edition'] for r in rows} == {'ZL3b', 'IT2a', 'RF1b'}
    counts = Counter((r['edition'], r['locus']) for r in rows)
    assert counts == {('ZL3b', 'f25v.1'): 9, ('IT2a', 'f25v.1'): 8,
                      ('RF1b', 'f25v.1'): 9, ('ZL3b', 'f25v.2'): 9,
                      ('IT2a', 'f25v.2'): 9, ('RF1b', 'f25v.2'): 9}
    keys = {(r['edition'], r['locus'], r['source_group_index']) for r in rows}
    assert len(keys) == len(rows)
    records = []
    totals = {}
    for row in rows:
        g0 = account(row['ivtff_group_raw'], recipes)
        g1 = account(row['ivtff_group_raw'], recipes, allow_insertion=True)
        record = dict(row, G0=g0, G1_post_application_extension=g1)
        # Symbolic recognition never certifies every stroke in the photograph.
        record['native_caution'] = (
            'Faded opening tall form: native identity unresolved'
            if row['locus'] == 'f25v.1' and row['source_group_index'] == '1'
            else 'Single-observer graphic plausibility only; no proved grapheme boundary')
        records.append(record)
        key = row['edition'] + '/' + row['locus']
        total = totals.setdefault(key, {'groups': 0, 'G0_symbolically_complete': 0,
                                      'G1_symbolically_complete': 0})
        total['groups'] += 1
        total['G0_symbolically_complete'] += int(all(x['resolved_symbolically'] for x in g0))
        total['G1_symbolically_complete'] += int(all(x['resolved_symbolically'] for x in g1))
    obj = {
        'status': 'LOCAL_EXPLORATORY_GRAPHIC_ACCOUNT_NOT_NATIVE_DECIPHERMENT',
        'G0_sha256': G0_SHA,
        'raw_sha256': receipt['selected_output_sha256'],
        'G1_status': 'Added after G0 application; descriptive fit, not successful transfer',
        'G1_added_rule': 'Insert one of the four distinct tall motifs through BE; c[kptf]h reference spelling',
        'G1_not_authorized_inferences': [
            'No equivalence between tch and cth, or between kch and ckh',
            'No order or values for proposed underlying letters',
            'No uppercase/lowercase collapse',
            'No prediction or visual validation of absent cph/cfh occurrences'],
        'scope': 'Both lines exposed, three readings of one manuscript; one informed observer',
        'summary': totals, 'records': records}
    out = BASE / 'HAND_WRITER_NATIVE_ACCOUNT_20261004.json'
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    md = ['# Vollständige Zweizeilen-Buchhaltung', '',
          'EVA-Formen sind Referenznamen, keine Lautwerte. G0 bleibt unverändert. '
          'G1 ergänzt erst nach der Anwendung eine Einsetzregel. '
          'Vollständig bedeutet hier ausschließlich symbolisch abgedeckt, '
          'nicht aus dem Bild eindeutig gelesen.', '']
    for edition in ('ZL3b', 'IT2a', 'RF1b'):
        for locus in ('f25v.1', 'f25v.2'):
            md += ['## ' + edition + ' — ' + locus, '',
                   '| Nr. | Rohform | links / rechts | G0 | G1, nachträglicher Entwurf |',
                   '|---|---|---|---|---|']
            for r in records:
                if r['edition'] == edition and r['locus'] == locus:
                    a = ' · '.join(p['recipe'] for p in r['G0'])
                    b = ' · '.join(p['recipe'] for p in r['G1_post_application_extension'])
                    md.append(f"| {r['source_group_index']} | `{r['ivtff_group_raw']}` | "
                              f"{r['left_separator']} / {r['right_separator']} | {a} | {b} |")
            md += ['']
    md += ['Der hohe Anfang von Zeile 1 bleibt verblasst und graphisch ungesichert. '
           'Keine unklare Leerstelle wurde vereinigt; keine Leser wurden gepoolt. '
           'Die G1-Abdeckung erklärt nicht, warum oder in welcher Reihenfolge '
           'ein Schreiber die Bauteile sprachlich kombiniert hätte.', '']
    (BASE / 'HAND_WRITER_NATIVE_ACCOUNT_20261004.md').write_text('\n'.join(md))
    print(json.dumps(totals, indent=2))
    print('53 complete records; exact input-string round trips; all separator labels retained.')


if __name__ == '__main__':
    main()
