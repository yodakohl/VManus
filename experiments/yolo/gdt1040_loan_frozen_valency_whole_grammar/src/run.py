#!/usr/bin/env python3
"""Complete fixed-arity capacity; no lexical meanings or semantic state fitted."""
import argparse
import collections
import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
ART = EXP / 'artifacts'
OPTIONS = (-1, 1, 2)


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def write_tsv(path, fields, rows):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def paths_for_assignment(words, fixed, recurrent):
    """Each singleton's category is determined by its unique clause position."""
    cats = fixed | recurrent
    n = len(words)
    counts = [0] * (n + 1)
    best = [None] * (n + 1)
    counts[0], best[0] = 1, ()
    for start in range(n):
        if not counts[start]:
            continue
        head = words[start]
        choices = (cats[head],) if head in cats else OPTIONS
        for arity in choices:
            end = start + arity + 1
            if arity < 0 or end > n:
                continue
            if any(word in cats and cats[word] != -1 for word in words[start + 1:end]):
                continue
            counts[end] += counts[start]
            candidate = best[start] + (arity + 1,)
            if best[end] is None or candidate < best[end]:
                best[end] = candidate
    furthest = max(i for i, count in enumerate(counts) if count)
    return counts[n], furthest, list(best[furthest])


def evaluate(words, fixed, cap=1000000):
    counts = collections.Counter(words)
    recurrent = sorted(word for word, count in counts.items() if count > 1 and word not in fixed)
    base = {'n_groups': len(words), 'n_types': len(counts), 'recurrent_unknowns': recurrent}
    if 3 ** len(recurrent) > cap:
        return base | {'status': 'UNKNOWN_CAP', 'assignments_checked': 0}, []
    rows = []
    for values in itertools.product(OPTIONS, repeat=len(recurrent)):
        assignment = dict(zip(recurrent, values))
        full, end, lengths = paths_for_assignment(words, fixed, assignment)
        rows.append({'assignment': assignment, 'full_paths': full,
                     'max_prefix': end, 'best_prefix_lengths': lengths})
    winner = min(rows, key=lambda row: (-row['max_prefix'],
                 tuple(row['assignment'][word] for word in recurrent), tuple(row['best_prefix_lengths'])))
    total = sum(row['full_paths'] for row in rows)
    return base | {'status': 'FULL_SAT' if total else 'FULL_UNSAT',
                   'assignments_checked': len(rows), 'total_full_paths': total,
                   'max_prefix': winner['max_prefix'],
                   'best_recurrent_assignment': winner['assignment'],
                   'best_prefix_lengths': winner['best_prefix_lengths']}, rows


def controls():
    fixed = {'statement': 0, 'unary': 1, 'binary': 2, 'thing': -1}
    cases = [(['statement'], 1), (['thing'], 0), (['unary', 'thing'], 1),
             (['binary', 'thing', 'thing'], 1), (['statement', 'statement'], 1),
             (['unary', 'statement'], 0), (['a', 'b'], 1),
             (['a', 'a'], 0), (['a', 'b', 'c'], 1), (['a', 'b', 'a', 'b'], 1)]
    for words, count in cases:
        result, _ = evaluate(words, fixed)
        assert result['total_full_paths'] == count, (words, result)
    result, _ = evaluate(['statement', 'thing', 'statement'], fixed)
    assert result['max_prefix'] == 1 and result['best_prefix_lengths'] == [1]
    print('SYNTHETIC_CONTROLS_PASS', len(cases) + 1, 'NO_TARGET_READ')


def gate():
    lock = json.loads((EXP / 'PREREG_LOCK.json').read_text())
    receipt = json.loads((ART / 'PUBLIC_REGISTRATION.json').read_text())
    assert lock['status'] == 'REGISTERED_BEFORE_EXECUTION'
    assert receipt['registered_before_execution'] is True and receipt['commit']
    for row in lock['files']:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    if args.controls:
        controls()
        return
    gate()
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    source = json.loads((EXP / 'src/SOURCE.json').read_text())
    fixed = spec['fixed']
    results, assignments, groups_table, case_table = {}, {}, [], []
    for name in spec['models']:
        groups = source['models'][name]['groups']
        result, rows = evaluate([g['word'] for g in groups], fixed, spec['primary_assignment_cap'])
        results[name], assignments[name] = result, rows
        case_table.append({'model': name, 'groups': result['n_groups'], 'types': result['n_types'],
                           'status': result['status'], 'assignments_checked': result['assignments_checked'],
                           'full_paths': result.get('total_full_paths', ''), 'max_prefix': result.get('max_prefix', ''),
                           'unparsed_groups': len(groups) - result.get('max_prefix', 0),
                           'independent_confirmation_capacity': 0})
        chosen = fixed | result.get('best_recurrent_assignment', {})
        spans, pos = {}, 0
        for number, length in enumerate(result.get('best_prefix_lengths', []), 1):
            for offset in range(length):
                idx = pos + offset
                category = length - 1 if offset == 0 else -1
                assert groups[idx]['word'] not in chosen or chosen[groups[idx]['word']] == category
                chosen[groups[idx]['word']] = category
                spans[idx] = (number, 'HEAD' if offset == 0 else 'ARGUMENT', category)
            pos += length
        assert pos == result.get('max_prefix', 0)
        for i, group in enumerate(groups):
            clause, role, cat = spans.get(i, ('', 'UNPARSED', chosen.get(group['word'], 'UNASSIGNED')))
            groups_table.append({'model': name, 'position': i + 1, **group,
                'clause': clause, 'diagnostic_role': role, 'category_in_selected_prefix': cat,
                'fixed_old_meaning': source['frozen_seven_full_values'].get(group['word'], 'UNASSIGNED'),
                'is_full_interpretation': False})
    statuses = [r['status'] for r in results.values()]
    joint = {'status': 'FULL_UNSAT_BY_CONTAINMENT' if 'FULL_UNSAT' in statuses else
             ('UNKNOWN_CAP' if 'UNKNOWN_CAP' in statuses else 'JOINT_REQUIRES_SHARED_SOLVER'),
             'basis': [name for name, row in results.items() if row['status'] == 'FULL_UNSAT']}
    output = {'status': 'COMPLETE_FIXED_SYNTAX_CAPACITY', 'models': results, 'joint': joint,
              'semantic_execution': False, 'new_meanings_assigned': 0, 'confirmed_words': 0,
              'independent_meaning_confirmation_capacity': 0,
              'partial_prefixes_are_not_readings': True}
    dump(ART / 'RESULT.json', output)
    dump(ART / 'ALL_ASSIGNMENTS.json', assignments)
    write_tsv(ART / 'CANDIDATE_TABLE.tsv', list(case_table[0]), case_table)
    fields = ['model', 'position', 'locus', 'line_index', 'word', 'source_id', 'original_alignment_status',
              'clause', 'diagnostic_role', 'category_in_selected_prefix', 'fixed_old_meaning', 'is_full_interpretation']
    for row in groups_table:
        row.setdefault('original_alignment_status', '')
    write_tsv(ART / 'ALL_GROUPS.tsv', fields, groups_table)
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
