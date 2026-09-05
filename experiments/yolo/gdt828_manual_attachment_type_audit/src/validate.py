#!/usr/bin/env python3
"""Independent reconstruction of GDT828; no runner imports or inferred glosses."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
SOURCE = 'experiments/yolo/gdt827_joint_core_paragraph_contrast/artifacts/SOURCE_LINES.tsv'
HASH = '8df7f22589c8b79a778ac038ae901bd746947fe5781177bd7c59e7193a188fb5'
EDITIONS = ('ZL3b', 'IT2a', 'RF1b')
RULES = {'RIGHT_NOMINAL': 1, 'LEFT_NOMINAL': -1}
TYPES = {
    'qokeedy': 'IMPERATIVE', 'qokedy': 'IMPERATIVE', 'shedy': 'IMPERATIVE',
    'qokain': 'NOMINAL', 'qokaiin': 'NOMINAL', 'qokeey': 'NOMINAL',
    'qol': 'NOMINAL_PRONOUN', 'chedy': 'RELATION',
}
FIELDS = ('block_id', 'page', 'locus', 'edition', 'target_index',
          'source_group_id', 'rule', 'neighbor_index', 'neighbor_raw',
          'neighbor_type', 'status', 'target_left_separator',
          'target_right_separator', 'paragraph_start', 'paragraph_end')
KEY = ('block_id', 'page', 'locus', 'edition', 'target_index', 'rule')
STATUS = 'C0_IMMEDIATE_ATTACHMENT_CONSTRUCTIONS_FAIL_NO_LEXICAL_VERDICT'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_source(payload):
    # Authenticate this admitted-only artifact before decoding any source payload.
    require(hashlib.sha256(payload).hexdigest() == HASH, 'source hash mismatch')
    rows = list(csv.DictReader(io.StringIO(payload.decode('utf-8')), delimiter='\t'))
    require(len(rows) == 150, 'source line count')
    seen = set()
    loci = defaultdict(set)
    group_ids = set()
    decoded = []
    for row in rows:
        require(row['page'] in {'f75r', 'f76r', 'f77r', 'f81r'}, 'unadmitted page')
        require(not row['page'].startswith('f84'), 'sealed selector')
        require(row['edition'] in EDITIONS, 'unrecognized edition')
        require(row['locus'].startswith(row['page'] + '.'), 'page/locus mismatch')
        key = (row['locus'], row['edition'])
        require(key not in seen, 'duplicate source line')
        seen.add(key)
        loci[row['locus']].add(row['edition'])
        arrays = {name: json.loads(row[name + '_json']) for name in
                  ('source_ids', 'groups', 'left', 'right', 'start', 'end')}
        size = len(arrays['groups'])
        require(size > 0 and all(isinstance(a, list) and len(a) == size
                                for a in arrays.values()), 'source array alignment')
        require(all(isinstance(x, str) for a in arrays.values() for x in a),
                'source values must remain opaque strings')
        for pos, identity in enumerate(arrays['source_ids'], 1):
            require(identity == f"{row['edition']}|{row['locus']}|G{pos:03d}",
                    'source group identity mismatch')
            require(identity not in group_ids, 'duplicate source group')
            group_ids.add(identity)
        decoded.append((row, arrays))
    require(len(loci) == 50 and all(e == set(EDITIONS) for e in loci.values()),
            'all three readings required at every locus')
    require(len(group_ids) == 1157, 'source group count')
    return decoded


def reconstruct(decoded):
    expected = []
    for line, a in decoded:
        for index, raw in enumerate(a['groups']):
            if raw != 'chedy':
                continue
            for rule, step in RULES.items():
                neighbor = index + step
                present = 0 <= neighbor < len(a['groups'])
                neighbor_raw = a['groups'][neighbor] if present else ''
                kind = TYPES.get(neighbor_raw, 'UNKNOWN') if present else 'LINE_EDGE'
                if kind in {'NOMINAL', 'NOMINAL_PRONOUN'}:
                    verdict = 'TYPE_COMPATIBLE_ONLY'
                elif kind in {'IMPERATIVE', 'RELATION'}:
                    verdict = 'TYPE_CONFLICT'
                else:
                    verdict = 'UNRESOLVED'
                expected.append({
                    **{field: line[field] for field in ('block_id', 'page', 'locus', 'edition')},
                    'target_index': str(index), 'source_group_id': a['source_ids'][index],
                    'rule': rule, 'neighbor_index': str(neighbor if present else -1),
                    'neighbor_raw': neighbor_raw, 'neighbor_type': kind, 'status': verdict,
                    'target_left_separator': a['left'][index],
                    'target_right_separator': a['right'][index],
                    'paragraph_start': a['start'][index], 'paragraph_end': a['end'][index],
                })
    return expected


def compare_neighbors(actual, expected):
    require(len(actual) == len(expected), 'neighbor coverage count')
    indexed = {}
    for row in actual:
        require(set(row) == set(FIELDS), 'neighbor columns')
        key = tuple(row[field] for field in KEY)
        require(key not in indexed, 'duplicate target/rule')
        indexed[key] = row
    for row in expected:
        key = tuple(row[field] for field in KEY)
        require(key in indexed, 'missing exact target/rule')
        require(indexed[key] == row, 'source join, opaque neighbor, metadata or classification mismatch')


def expected_summary(expected):
    counts = defaultdict(Counter)
    for row in expected:
        counts[(row['edition'], row['rule'])][row['status']] += 1
    summary = {}
    for edition in EDITIONS:
        for rule in RULES:
            count = counts[(edition, rule)]
            summary[(edition, rule)] = {
                'edition': edition, 'rule': rule, 'targets': sum(count.values()),
                'type_compatible_only': count['TYPE_COMPATIBLE_ONLY'],
                'type_conflict': count['TYPE_CONFLICT'], 'unresolved': count['UNRESOLVED'],
                'construction_status': ('FAIL_FIXED_CONSTRUCTION' if count['TYPE_CONFLICT']
                                        else 'NO_CONFLICT_NOT_VALIDATION'),
            }
    return summary


def compare_result(result, expected):
    require(result.get('status') == STATUS, 'top-level result status')
    summary = expected_summary(expected)
    actual = result.get('by_reading_rule')
    require(isinstance(actual, list) and len(actual) == len(summary), 'summary coverage')
    seen = set()
    for row in actual:
        key = (row.get('edition'), row.get('rule'))
        require(key in summary and key not in seen, 'summary reading/rule identity')
        seen.add(key)
        require(row == summary[key], 'summary counts or construction verdict')
    # A conflict in an exposed alternate reading is enough to flag each fixed
    # construction here; it is not an all-reading failure or an independent vote.
    require(all(any(row['type_conflict'] > 0 for key, row in summary.items()
                    if key[1] == rule) for rule in RULES),
            'global failure status requires a conflict for each construction')
    metadata = {
        'experiment_id': 'GDT828', 'source_sha256': HASH,
        'source_lines': 150, 'source_loci': 50,
        'chedy_positions': len(expected) // 2,
        'unique_target_loci': len({row['locus'] for row in expected}),
        'confirmed_clauses': 0, 'confirmed_lexemes': 0,
        'dictionary_changed': False, 'new_admissions': 0,
        'new_images': 0, 'new_scored_relations': 0,
        'exposure': 'POST_EXPOSURE_FIXED_CONSTRUCTION_AUDIT_NOT_HELD_TEST',
        'sealed_data': ['f84', 'f84r'],
        'interpretation': 'Conditional construction failures; proposed types are not decoded POS; unknown is unresolved.',
        'status': STATUS,
    }
    require(set(result) == set(metadata) | {'by_reading_rule'}, 'result schema')
    for key, value in metadata.items():
        require(type(result[key]) is type(value) and result[key] == value,
                'result metadata/count mismatch: ' + key)


def rejected(name, call):
    try:
        call()
    except (ValueError, KeyError, TypeError):
        return {'name': name, 'status': 'REJECTED'}
    raise ValueError('mutation escaped rejection: ' + name)


def mutations(source_bytes, expected, result):
    outcomes = []
    outcomes.append(rejected('missing_target_rule',
                             lambda: compare_neighbors(expected[1:], expected)))
    altered = copy.deepcopy(expected)
    altered[0]['neighbor_raw'] += '_changed'
    outcomes.append(rejected('altered_neighbor', lambda: compare_neighbors(altered, expected)))
    unknown = copy.deepcopy(expected)
    row = next(r for r in unknown if r['neighbor_type'] == 'UNKNOWN')
    row['status'] = 'TYPE_COMPATIBLE_ONLY'
    outcomes.append(rejected('unknown_treated_as_fit', lambda: compare_neighbors(unknown, expected)))
    # Actual extended group in this bound source; no source or artifact is overwritten.
    source_text = source_bytes.decode('utf-8')
    require('shee@152;y' in source_text, 'opaque-entity mutation fixture absent')
    changed_source = source_text.replace('shee@152;y', 'shee @152; y', 1).encode('utf-8')
    outcomes.append(rejected('source_entity_split', lambda: load_source(changed_source)))
    wrong_result = copy.deepcopy(result)
    wrong_result['by_reading_rule'][0]['type_conflict'] += 1
    outcomes.append(rejected('altered_summary_count', lambda: compare_result(wrong_result, expected)))
    flags = copy.deepcopy(expected)
    flags[0]['paragraph_start'] = 'changed'
    outcomes.append(rejected('altered_native_paragraph_flag', lambda: compare_neighbors(flags, expected)))
    return outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='require exact existing validation artifact')
    args = parser.parse_args()
    spec = json.loads((HERE / 'src/SPEC.json').read_text())
    require(spec == {
        'experiment_id': 'GDT828', 'source': SOURCE, 'source_sha256': HASH,
        'allowed_pages': ['f75r', 'f76r', 'f77r', 'f81r'], 'editions': list(EDITIONS),
        'sealed_data': ['f84', 'f84r'], 'target': 'chedy', 'types': TYPES, 'rules': RULES,
        'exposure': 'POST_EXPOSURE_FIXED_CONSTRUCTION_AUDIT_NOT_HELD_TEST',
    }, 'fixed specification changed')
    source_bytes = (ROOT / SOURCE).read_bytes()
    expected = reconstruct(load_source(source_bytes))
    with (HERE / 'artifacts/NEIGHBORS.tsv').open(newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        require(reader.fieldnames == list(FIELDS), 'neighbor header/order mismatch')
        actual = list(reader)
    compare_neighbors(actual, expected)
    result = json.loads((HERE / 'artifacts/RESULT.json').read_text())
    compare_result(result, expected)
    mutation_results = mutations(source_bytes, expected, result)
    checks = ['fixed_specification', 'bound_source_hash', 'allowed_pages_and_sealed_exclusion',
              'source_group_identities_and_array_alignment', 'complete_three_reading_loci',
              'exact_target_rule_coverage', 'opaque_immediate_neighbors_and_source_metadata',
              'candidate_types_and_unknown_censoring', 'per_reading_counts_and_verdicts',
              'mutation_rejection']
    validation = {
        'experiment_id': 'GDT828', 'status': 'PASS_INDEPENDENT_RECONSTRUCTION',
        'source_sha256': HASH, 'source_lines': 150, 'source_loci': 50,
        'source_groups': 1157, 'neighbor_rows': len(expected),
        'checks_passed': len(checks), 'checks': checks,
        'mutation_count': len(mutation_results), 'mutations': mutation_results,
        'semantic_limits': {
            'confirmed_lexemes': 0, 'recovered_parts_of_speech': 0,
            'meaning_validation': False, 'held_prediction': False,
            'alternate_readings_are_independent_witnesses': False,
            'failure_scope': 'TWO_UNIFORM_IMMEDIATE_NOMINAL_CONSTRUCTIONS_UNDER_FIXED_C0_TYPES',
        },
    }
    rendered = json.dumps(validation, indent=2, ensure_ascii=False) + '\n'
    path = HERE / 'artifacts/VALIDATION.json'
    if args.check:
        require(path.read_text() == rendered, 'validation artifact differs from deterministic reconstruction')
    else:
        path.write_text(rendered)
    print(json.dumps({'status': validation['status'], 'checks_passed': len(checks),
                      'mutation_count': len(mutation_results), 'neighbor_rows': len(expected)}))


if __name__ == '__main__':
    main()
