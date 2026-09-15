"""Fixed complete-purpose equality and component-presence consequences; no decoder."""
import csv
import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

E = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((E / name).read_text())


def write_json(name, value):
    (E / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def write_tsv(name, rows, fields):
    with (E / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter='\t')
        w.writeheader()
        w.writerows(rows)


def mapping(candidate):
    return {row: f"f69v.{4 + (candidate['start'] + candidate['direction'] * (row - 1)) % 28}"
            for row in range(1, 29)}


def predictions():
    source, spec = read('src/SOURCE.json'), read('src/SPEC.json')
    rows = []
    for candidate in spec['candidates']:
        m = mapping(candidate)
        for row in source['rows']:
            rows.append({'candidate': candidate['id'], 'source_row': row['row'],
                         'locus': m[row['row']], 'purpose_id': row['purpose_id'] or 'UNKNOWN',
                         'purpose_de': row['meaning_de'],
                         'present_atoms': 'UNKNOWN' if row['atoms'] is None else ','.join(row['atoms']),
                         'absent_atoms': 'UNKNOWN' if row['atoms'] is None else ','.join(
                             a['id'] for a in source['atoms'] if a['id'] not in row['atoms'])})
    write_tsv('artifacts/ALL_PREDICTIONS.tsv', rows, list(rows[0]))
    return rows


def targets(data, spec):
    raw = defaultdict(list)
    legacy = {}
    for x in data['raw']:
        raw[x['edition'], x['locus']].append(x)
    for x in data['legacy']:
        key = x['edition'], x['locus']
        assert key not in legacy, key
        legacy[key] = x
    result = {}
    for edition in spec['editions']:
        for locus in spec['loci']:
            key = edition, locus
            group_rows = sorted(raw[key], key=lambda x: int(x['source_group_index']))
            assert group_rows and len(group_rows) == int(group_rows[0]['source_group_count'])
            indices = [int(x['source_group_index']) for x in group_rows]
            assert indices == list(range(1, len(group_rows) + 1)), key
            groups = [x['ivtff_group_raw'] for x in group_rows]
            literal_reasons = []
            if any(not re.fullmatch('[a-z]+', g) for g in groups):
                literal_reasons.append('NONLITERAL_RAW_GROUP')
            if any(a['right_separator'] != 'DEFINITE_SPACE' or b['left_separator'] != 'DEFINITE_SPACE'
                   for a, b in zip(group_rows, group_rows[1:])):
                literal_reasons.append('UNCERTAIN_INTERNAL_SEAM')
            lr = legacy[key]
            root_groups = lr['root_sequence'].split()
            units = [u for g in root_groups for u in g.split('+')]
            root_reasons = list(literal_reasons)
            if lr['surface'].split() != groups:
                root_reasons.append('LEGACY_SURFACE_MISMATCH')
            if len(root_groups) != len(groups):
                root_reasons.append('LEGACY_ROOT_GROUP_COUNT_MISMATCH')
            if not units or any(not re.fullmatch('[A-Za-z]+', u) for u in units):
                root_reasons.append('NONALPHABETIC_ROOT_UNIT')
            result[key] = {'edition': edition, 'locus': locus, 'groups': groups,
                           'whole': None if literal_reasons else tuple(groups),
                           'legacy_root_sequence': lr['root_sequence'],
                           'units': None if root_reasons else set(units),
                           'literal_unknown': literal_reasons, 'root_unknown': root_reasons}
    return result


def maximum_matching(domains):
    assigned = {}

    def visit(atom, seen):
        for unit in sorted(domains[atom]):
            if unit in seen:
                continue
            seen.add(unit)
            if unit not in assigned or visit(assigned[unit], seen):
                assigned[unit] = atom
                return True
        return False

    for atom in sorted(domains):
        visit(atom, set())
    matching = {a: u for u, a in assigned.items()}
    certificate = None
    if len(matching) < len(domains):
        atoms = sorted(domains)
        for k in range(1, len(atoms) + 1):
            for subset in itertools.combinations(atoms, k):
                neighbors = set().union(*(set(domains[a]) for a in subset))
                if len(neighbors) < k:
                    certificate = {'atoms': list(subset), 'units': sorted(neighbors)}
                    return matching, certificate
    return matching, certificate


def calculate():
    lock = read('PREREG_LOCK.json')
    for path, h in lock['files'].items():
        assert hashlib.sha256((E / path).read_bytes()).hexdigest() == h, path
    source, spec, data = read('src/SOURCE.json'), read('src/SPEC.json'), read('artifacts/INPUT.json')
    target = targets(data, spec)
    known = [r for r in source['rows'] if r['purpose_id'] is not None]
    summaries, pair_checks, component_checks, candidate_details = [], [], [], []
    for edition in spec['editions']:
        universe = sorted(set().union(*(t['units'] or set() for (ed, _), t in target.items() if ed == edition)))
        for candidate in spec['candidates']:
            m = mapping(candidate)
            statuses = Counter()
            for a, b in itertools.combinations(known, 2):
                ta, tb = target[edition, m[a['row']]], target[edition, m[b['row']]]
                expected = a['purpose_id'] == b['purpose_id']
                observed = None if ta['whole'] is None or tb['whole'] is None else ta['whole'] == tb['whole']
                status = 'UNKNOWN' if observed is None else ('AGREE' if observed == expected else 'CONTRADICTION')
                statuses[status] += 1
                pair_checks.append({'edition': edition, 'candidate': candidate['id'],
                    'source_row_a': a['row'], 'source_row_b': b['row'],
                    'locus_a': m[a['row']], 'locus_b': m[b['row']],
                    'expected_equal': int(expected), 'observed_equal': '?' if observed is None else int(observed),
                    'status': status})
            domains, upper_domains = {}, {}
            for atom in source['atoms']:
                domains[atom['id']] = []
                upper_domains[atom['id']] = []
                for unit in universe:
                    positive, negative, unknown, mismatches = [], [], [], []
                    for r in known:
                        locus = m[r['row']]
                        units = target[edition, locus]['units']
                        expected = r['row'] in atom['rows']
                        if units is None:
                            unknown.append(locus)
                        elif (unit in units) != expected:
                            mismatches.append(f"{locus}:{int(expected)}>{int(unit in units)}")
                        elif expected:
                            positive.append(locus)
                        else:
                            negative.append(locus)
                    compatible = not mismatches and len(positive) >= spec['minimum_observed_positive'] and len(negative) >= spec['minimum_observed_negative']
                    if not mismatches:
                        upper_domains[atom['id']].append(unit)
                    if compatible:
                        domains[atom['id']].append(unit)
                    component_checks.append({'edition': edition, 'candidate': candidate['id'],
                        'atom': atom['id'], 'unit': unit, 'no_observed_contradiction': int(not mismatches), 'compatible': int(compatible),
                        'observed_positive_loci': ','.join(positive), 'observed_negative_loci': ','.join(negative),
                        'unknown_loci': ','.join(unknown), 'contradictions_expected_to_observed': ','.join(mismatches)})
                if not any(target[edition, m[r]]['units'] is not None for r in atom['rows']):
                    upper_domains[atom['id']].append('UNOBSERVED_' + atom['id'])
            matching, hall = maximum_matching(domains)
            upper_matching, upper_hall = maximum_matching(upper_domains)
            p_status = 'CONTRADICTED' if statuses['CONTRADICTION'] else ('UNRESOLVED' if statuses['UNKNOWN'] else 'COMPATIBLE')
            c_status = 'P_CONTRADICTED' if p_status == 'CONTRADICTED' else ('COMPONENT_CONTRADICTED' if len(upper_matching) < len(domains) else ('NO_CAPACITY' if len(matching) < len(domains) else 'COMPONENT_FEASIBLE'))
            summary = {'edition': edition, 'candidate': candidate['id'], 'P_status': p_status,
                       'P_agree': statuses['AGREE'], 'P_contradictions': statuses['CONTRADICTION'],
                       'P_unknown': statuses['UNKNOWN'], 'C_status': c_status,
                       'component_matching_size': len(matching), 'component_upper_matching_size': len(upper_matching), 'component_atoms': len(domains),
                       'empty_component_domains': ','.join(a for a in domains if not domains[a]),
                       'unknown_source_rows': '22', 'physical_leaves': 1, 'independent_confirmation_leaves': 0}
            summaries.append(summary)
            candidate_details.append({**summary, 'mapping': m, 'component_domains': domains,
                                     'component_upper_domains': upper_domains,
                                     'one_matching_not_uniqueness': matching, 'hall_certificate': hall,
                                     'upper_one_matching_not_uniqueness': upper_matching, 'upper_hall_certificate': upper_hall})
    records = [{**{k: t[k] for k in ['edition', 'locus', 'legacy_root_sequence']},
                'raw_groups': ' '.join(t['groups']), 'literal_known': int(t['whole'] is not None),
                'root_known': int(t['units'] is not None), 'units': ','.join(sorted(t['units'] or set())),
                'literal_unknown_reasons': ','.join(t['literal_unknown']), 'root_unknown_reasons': ','.join(t['root_unknown'])}
               for t in target.values()]
    for filename, rows in [('COMPLETE_TARGET_RECORDS.tsv', records), ('CANDIDATE_TABLE.tsv', summaries),
                           ('ALL_PAIR_CONSEQUENCES.tsv', pair_checks), ('ALL_COMPONENT_CONSEQUENCES.tsv', component_checks)]:
        write_tsv('artifacts/' + filename, rows, list(rows[0]))
    write_json('artifacts/CANDIDATE_DETAILS.json', candidate_details)
    result = {'status': 'COMPLETE_FIXED_MODEL_EVALUATION', 'candidates_per_reading': 56,
              'source_rows': 28, 'source_unknown_rows': [22], 'recurrent_atoms': 11,
              'pair_consequences': len(pair_checks), 'component_unit_checks': len(component_checks),
              'editions': {}, 'independent_confirmation_leaves': 0, 'confirmed_words': 0,
              'input_sha256': hashlib.sha256((E / 'artifacts/INPUT.json').read_bytes()).hexdigest(),
              'claim_ceiling': 'Discovery-seeded conditional content consistency; catalogue-order condition; no search null or independent semantic confirmation.'}
    for edition in spec['editions']:
        xs = [x for x in summaries if x['edition'] == edition]
        result['editions'][edition] = {'P_outcomes': dict(Counter(x['P_status'] for x in xs)),
                                      'C_outcomes': dict(Counter(x['C_status'] for x in xs)),
                                      'P_remaining': [x['candidate'] for x in xs if x['P_status'] != 'CONTRADICTED'],
                                      'C_remaining': [x['candidate'] for x in xs if x['C_status'] == 'COMPONENT_FEASIBLE'],
                                      'known_whole_labels': sum(t['whole'] is not None for (ed, _), t in target.items() if ed == edition),
                                      'known_component_labels': sum(t['units'] is not None for (ed, _), t in target.items() if ed == edition)}
    write_json('artifacts/RESULT.json', result)
    return result


if __name__ == '__main__':
    import sys
    if '--predict-only' in sys.argv:
        print(json.dumps({'source_only_predictions': len(predictions()), 'target_opened': False}))
    else:
        print(json.dumps(calculate(), ensure_ascii=False, indent=2))
