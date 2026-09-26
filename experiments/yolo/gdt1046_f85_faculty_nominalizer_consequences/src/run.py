#!/usr/bin/env python3
"""Reproduce literal scope and one fixed conditional type consequence; no decoder."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]


def read_json(path):
    return json.loads(path.read_text())


def write_table(name, rows):
    with (EXP / 'artifacts' / name).open('w') as f:
        writer = csv.DictWriter(f, list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    spec = read_json(EXP / 'src/SPEC.json')
    lock = read_json(EXP / 'src/REGISTRATION_LOCK.json')
    for rel, expected in lock['sha256'].items():
        assert hashlib.sha256((EXP / rel).read_bytes()).hexdigest() == expected, rel
    bound = {}
    for key, item in spec['inputs'].items():
        p = ROOT / item['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], key
        bound[key] = p
    # This is a prior owned projection containing f85r2 only, not a mixed raw TSV.
    with bound['projection'].open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert len(rows) == 473 and {r['page'] for r in rows} == {'f85r2'}
    parent_s = read_json(bound['parent_S'])
    parent_e = read_json(bound['parent_E'])['design']['assignments']
    lexicon = {**parent_s['fixed_idea550_bindings'], **parent_s['new_whole_form_values']}
    assert len(lexicon) == 24 and len(parent_e) == 6 and not set(lexicon) & set(parent_e)
    lexicon.update(parent_e)
    byline = defaultdict(list)
    e_rows, ar_rows, pairs = [], [], []
    for r in rows:
        byline[(r['edition'], r['locus'])].append(r)
        if 7 <= int(r['line_number']) <= 11:
            val = lexicon.get(r['ivtff_group_raw'])
            e_rows.append({**r, 'parent_type': val['type'] if val else '',
                           'parent_meaning': val['meaning'] if val else '',
                           'assignment_status': 'INHERITED_HYPOTHESIS' if val else 'UNASSIGNED'})
    for line in byline.values():
        line.sort(key=lambda r: int(r['source_group_index']))
        for i, r in enumerate(line):
            if r['ivtff_group_raw'] != 'ar':
                continue
            prev = line[i - 1] if i else None
            nxt = line[i + 1] if i + 1 < len(line) else None
            status = 'UNBOUND_PRECEDING_FRAME'
            if prev is None:
                status = 'UNRESOLVED_CROSS_LINE_SCOPE'
            elif prev['ivtff_group_raw'] == 'ar':
                status = 'SECOND_NOM_DOMAIN_MISMATCH_UNDER_FIXED_REDUCTIONS'
            elif nxt and nxt['ivtff_group_raw'] == 'ar':
                status = 'FIRST_NOM_FRAME_GRANTED_CONDITIONALLY'
            ar_rows.append({k: r[k] for k in ('edition', 'locus', 'source_group_id',
                                             'source_group_index', 'ivtff_group_raw',
                                             'left_separator', 'right_separator')} |
                           {'previous_id': prev['source_group_id'] if prev else '',
                            'previous_raw': prev['ivtff_group_raw'] if prev else '',
                            'next_id': nxt['source_group_id'] if nxt else '',
                            'next_raw': nxt['ivtff_group_raw'] if nxt else '',
                            'status': status})
            if nxt and nxt['ivtff_group_raw'] == 'ar':
                red = spec['reductions']
                first_output = red['nom_range']
                needed_input = red['nom_domain']
                assert not red['extra_reframing_or_casts']
                pairs.append({'edition': r['edition'], 'locus': r['locus'],
                              'first_id': r['source_group_id'], 'second_id': nxt['source_group_id'],
                              'between': r['right_separator'], 'after_second': nxt['right_separator'],
                              'granted_left_type': needed_input, 'first_result_type': first_output,
                              'second_required_type': needed_input,
                              'result': 'DOMAIN_MISMATCH' if first_output != needed_input else 'TYPED'})
    counts = {}
    for ed in ('ZL3b', 'IT2a', 'RF1b'):
        sub = [r for r in e_rows if r['edition'] == ed]
        counts[ed] = {'E_groups': len(sub), 'E_types': len({r['ivtff_group_raw'] for r in sub}),
                      'inherited_assigned': sum(bool(r['parent_type']) for r in sub),
                      'unassigned': sum(not r['parent_type'] for r in sub),
                      'bare_ar': sum(r['edition'] == ed for r in ar_rows),
                      'adjacent_nom_pairs': sum(r['edition'] == ed for r in pairs)}
    with bound['native_groups'].open() as f:
        native_rows = list(csv.DictReader(f, delimiter='\t'))
    with bound['native_alignment'].open() as f:
        aligned = list(csv.DictReader(f, delimiter='\t'))
    source_native = [r for r in rows if r['locus'] == 'f85r2.24']
    assert native_rows == source_native
    aligned_ids = [sid for a in aligned for ed in counts for sid in a[ed + '_ids'].split()]
    assert Counter(aligned_ids) == Counter(r['source_group_id'] for r in native_rows)
    result = {'experiment': 'GDT1046', 'status': 'STRICT_NOM_EXTENSION_FAILS_IT_RF_ZL_INCOMPLETE',
              'source_rows': len(rows), 'counts': counts, 'E_total': len(e_rows),
              'bare_ar_total': len(ar_rows), 'adjacent_nom_reader_records': len(pairs),
              'adjacent_nom_manuscript_loci': len({r['locus'] for r in pairs}),
              'fixed_consequence': spec['conditional_trace'],
              'whole_E_complete': False, 'ZL_impossibility_proved': False,
              'new_word_values_or_grammar_repairs': 0,
              'native_line_records': len(native_rows), 'native_alignment_units': len(aligned),
              'native_decision': spec['native_decision'],
              'source_correction': spec['source_correction'],
              'confirmed_words': 0, 'independent_confirmation_folios': 0,
              'claim_ceiling': 'Literal census and fixed conditional construction only; no significance or selected meaning.'}
    write_table('E_GROUPS.tsv', e_rows)
    write_table('BARE_AR.tsv', ar_rows)
    write_table('DOUBLE_AR.tsv', pairs)
    (EXP / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'E': len(e_rows), 'ar': len(ar_rows), 'pairs': len(pairs)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
