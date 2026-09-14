"""Evaluate frozen meanings, not a decoder or learned grammar."""
import argparse
from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]


def jd(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + '\n'


def tsv(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue()


def build():
    lock = json.loads((EXP / 'PREREG_LOCK.json').read_text())
    for base, group in [(EXP, lock['files']), (ROOT, lock['source_files'])]:
        for name, digest in group.items():
            assert hashlib.sha256((base / name).read_bytes()).hexdigest() == digest, name
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    candidates = json.loads((EXP / 'src/CANDIDATES.json').read_text())
    rows = json.loads((ROOT / spec['source']).read_text())['groups']
    allowed = spec['discovery_pages'] + spec['additional_pages']
    assert all(r['page'] in allowed and not r['page'].startswith('f84') and r['page'] not in spec['forbidden_pages'] for r in rows)
    assert len({r['source_group_id'] for r in rows}) == len(rows)
    marked = {p['marked']: p['id'] for p in spec['pairs']}
    lines = defaultdict(list)
    for row in rows:
        lines[(row['edition'], row['page'], row['locus'])].append(row)
    lines = {k: sorted(v, key=lambda r: int(r['source_group_index'])) for k, v in lines.items()}
    cases, unresolved, full_lines = [], [], []
    for key in sorted(lines, key=lambda k: (spec['editions'].index(k[0]), allowed.index(k[1]), int(k[2].split('.')[1]))):
        group = lines[key]; local = []
        for i, row in enumerate(group):
            if row['kind'] != 'P' or row['ivtff_group_raw'] not in spec['operators']:
                continue
            right = group[i + 1] if i + 1 < len(group) else None
            case = {'edition': row['edition'], 'page': row['page'], 'locus': row['locus'],
                    'partition': 'DISCOVERY' if row['page'] in spec['discovery_pages'] else 'ADDITIONAL',
                    'operator_id': row['source_group_id'], 'operator': row['ivtff_group_raw'],
                    'result_id': right['source_group_id'] if right else '',
                    'result_raw': right['ivtff_group_raw'] if right else '',
                    'right_separator': row['right_separator'],
                    'next_left_separator': right['left_separator'] if right else ''}
            adjacent = right and int(right['source_group_index']) == int(row['source_group_index']) + 1
            definite = right and row['right_separator'] == right['left_separator'] == 'DEFINITE_SPACE'
            if adjacent and definite and right['kind'] == 'P' and right['ivtff_group_raw'] in marked:
                case.update(case_id=f'C{len(cases)+1:03}', pair=marked[right['ivtff_group_raw']])
                cases.append(case); local.append(case['case_id'])
            else:
                case['reason'] = ('LINE_END' if right is None else 'NONCONSECUTIVE' if not adjacent else
                                  'UNCERTAIN_SEPARATOR' if not definite else 'NO_LISTED_RESULT')
                unresolved.append(case)
        if local:
            full_lines.append({'edition': key[0], 'page': key[1], 'locus': key[2], 'case_ids': local, 'groups': group})
    result_rows, consequences = [], []
    classes = defaultdict(list)
    observed_classes = defaultdict(list)
    for candidate in candidates:
        predictions = {(p['operator'], p['result_raw']): p for p in candidate['all_possible_pair_predictions']}
        classes[tuple(p['compatible'] for p in candidate['all_possible_pair_predictions'])].append(candidate['id'])
        observed_classes[tuple(predictions[(c['operator'], c['result_raw'])]['compatible'] for c in cases)].append(candidate['id'])
        counts = {}
        for edition in spec['editions']:
            counts[edition] = {}
            for partition in ['DISCOVERY', 'ADDITIONAL']:
                selected = [c for c in cases if c['edition'] == edition and c['partition'] == partition]
                bad = [c['case_id'] for c in selected if not predictions[(c['operator'], c['result_raw'])]['compatible']]
                counts[edition][partition] = {'cases': len(selected), 'contradictions': bad,
                                               'compatible': len(selected)-len(bad), 'survives': not bad}
        for case in cases:
            p = predictions[(case['operator'], case['result_raw'])]
            consequences.append({'candidate': candidate['id'], 'case_id': case['case_id'],
                'edition': case['edition'], 'partition': case['partition'], 'locus': case['locus'],
                'operator_id': case['operator_id'], 'result_id': case['result_id'],
                'operator_raw': case['operator'], 'result_raw': case['result_raw'],
                'operation': p['operation'], 'named_result': p['named_result'],
                'required_phase': p['required_phase'], 'named_phase': p['named_phase'],
                'outcome': 'COMPATIBLE_ASSUMPTIONS' if p['compatible'] else 'CONTRADICTION'})
        result_rows.append({'candidate': candidate['id'], 'orientation': candidate['orientation'],
                            **candidate['assignments'], 'by_edition': counts})
    equivalence = [{'class_id': f'E{i+1:02}', 'compatibility_for_all_eight_possible_pairs': list(v),
                    'candidates': members, 'size': len(members)} for i, (v,members) in enumerate(sorted(classes.items()))]
    observed_equivalence = [{'class_id': f'O{i+1:02}', 'case_ids': [c['case_id'] for c in cases],
        'compatibility': list(v), 'candidates': members, 'size': len(members)}
        for i, (v, members) in enumerate(sorted(observed_classes.items()))]
    lookup = {mid: c['class_id'] for c in equivalence for mid in c['candidates']}
    observed_lookup = {mid: c['class_id'] for c in observed_equivalence for mid in c['candidates']}
    flat = []
    for row in result_rows:
        line = {k: v for k, v in row.items() if k != 'by_edition'}
        line['phase_prediction_class'] = lookup[row['candidate']]
        line['observed_prediction_class'] = observed_lookup[row['candidate']]
        for edition, parts in row['by_edition'].items():
            for partition, result in parts.items():
                line[edition+'_'+partition+'_cases'] = result['cases']
                line[edition+'_'+partition+'_contradictions'] = ','.join(result['contradictions']) or 'NONE'
        line['independent_meaning_confirmation'] = 'NONE'; flat.append(line)
    certificates = []
    for edition in spec['editions']:
        for partition in ['DISCOVERY', 'ADDITIONAL']:
            for pair in spec['pairs']:
                by_op = {op: [c for c in cases if c['edition']==edition and c['partition']==partition
                             and c['pair']==pair['id'] and c['operator']==op] for op in spec['operators']}
                if all(by_op.values()):
                    certificates.append({'edition': edition, 'partition': partition, 'pair': pair['id'],
                        'result_raw': pair['marked'], 'operator_1_cases': [c['case_id'] for c in by_op[spec['operators'][0]]],
                        'operator_2_cases': [c['case_id'] for c in by_op[spec['operators'][1]]],
                        'reason': 'One fixed named result would need both LIQUID and SOLID under either orientation.'})
    summaries = {}
    for edition in spec['editions']:
        summaries[edition] = {'source_groups': sum(r['edition']==edition for r in rows),
            'qualified_pairs': sum(c['edition']==edition for c in cases),
            'unresolved_operator_positions': sum(c['edition']==edition for c in unresolved)}
        for partition in ['DISCOVERY', 'ADDITIONAL']:
            summaries[edition][partition] = {'cases': sum(c['edition']==edition and c['partition']==partition for c in cases),
                'surviving_candidates': [r['candidate'] for r in result_rows if r['by_edition'][edition][partition]['survives']]}
        summaries[edition]['joint_surviving_candidates'] = [r['candidate'] for r in result_rows
            if all(x['survives'] for x in r['by_edition'][edition].values())]
    result = {'experiment': 'GDT950', 'status': 'FIXED_PHASE_OUTPUT_CONJUNCTION_AUDITED',
        'candidates': len(candidates), 'possible_pair_predictions': sum(len(c['all_possible_pair_predictions']) for c in candidates),
        'phase_prediction_classes': len(equivalence), 'qualified_pairs': len(cases),
        'observed_prediction_classes': len(observed_equivalence),
        'unresolved_operator_positions': len(unresolved), 'editions': summaries,
        'contradiction_certificates': certificates, 'new_manuscript_data': False,
        'confirmed_words': 0, 'independent_meaning_confirmation_capacity': 0,
        'semantic_winner': None, 'significance_tested': False,
        'scope': 'Contradiction or survival applies to specific phase meanings plus immediate named-result bridge; not to meteorology or individual glosses alone.'}
    return {'SOURCE_CASES.json': jd(cases), 'UNRESOLVED_OPERATORS.json': jd(unresolved),
            'COMPLETE_MATCHING_LINES.json': jd(full_lines), 'CANDIDATE_RESULTS.json': jd(result_rows),
            'CANDIDATE_TABLE.tsv': tsv(flat), 'CONSEQUENCES.tsv': tsv(consequences) if consequences else '',
            'PREDICTION_CLASSES.json': jd(equivalence),
            'OBSERVED_PREDICTION_CLASSES.json': jd(observed_equivalence), 'RESULT.json': jd(result)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    outputs = build()
    for name, content in outputs.items():
        path = EXP / 'artifacts' / name
        if args.check:
            assert path.read_text() == content, name
        else:
            path.write_text(content)
    r = json.loads(outputs['RESULT.json'])
    print(jd({'experiment': r['experiment'], 'candidates': r['candidates'],
        'qualified_pairs': r['qualified_pairs'], 'possible_prediction_classes': r['phase_prediction_classes'],
        'observed_prediction_classes': r['observed_prediction_classes'],
        'survivor_counts': {ed: len(v['joint_surviving_candidates']) for ed,v in r['editions'].items()}}))


if __name__ == '__main__':
    main()
