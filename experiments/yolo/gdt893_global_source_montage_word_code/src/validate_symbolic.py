#!/usr/bin/env python3
"""Check primary symbolic results against independent maximum/projection evidence.

The independent reference may be a COMPLETE validate_projection.cpp result or a
previous COMPLETE validate_optima.cpp full family. No fitter code is imported.
"""
import argparse
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def read_pool(path):
    pool = []
    with Path(path).open() as handle:
        n = int(handle.readline())
        require(n >= 0, 'negative candidate count')
        for _ in range(n):
            row = list(map(int, handle.readline().split()))
            require(len(row) >= 3, 'missing candidate record')
            group, weight, size = row[:3]
            require(weight > 0 and size >= 0 and len(row) == 3 + 2 * size,
                    'record outside positive whole-paragraph weight scope')
            pairs = list(zip(row[3::2], row[4::2]))
            require(len({c for c, _ in pairs}) == size and len({p for _, p in pairs}) == size,
                    'invalid candidate bijection')
            pool.append((group, weight, dict(pairs)))
        require(not handle.read().strip(), 'extra candidate records')
    return pool


def witness_map(pool, indices, weight):
    require(isinstance(indices, list) and len(indices) == len(set(indices)), 'duplicate witness index')
    require(all(type(i) is int and 0 <= i < len(pool) for i in indices), 'witness index bounds')
    groups, forward, reverse, total = set(), {}, {}, 0
    for i in indices:
        group, value, mapping = pool[i]
        require(group not in groups, 'two candidates for one paragraph')
        groups.add(group)
        total += value
        for c, p in mapping.items():
            require(c not in forward or forward[c] == p, 'witness forward conflict')
            require(p not in reverse or reverse[p] == c, 'witness reverse conflict')
            forward[c], reverse[p] = p, c
    require(total == weight, 'witness weight mismatch')
    return forward


def reference_projection(pool, reference):
    require(reference['status'] == 'COMPLETE', 'independent reference incomplete')
    if 'optimal_solutions' in reference:
        solutions = reference['optimal_solutions']
        require(solutions, 'complete family has no optimum, including empty selection')
        forced = set(solutions[0])
        pairs = witness_map(pool, solutions[0], reference['best_weight'])
        for solution in solutions[1:]:
            # The full-family source is separately hash-bound and already
            # exhaustively produced. Intersections cannot subsequently grow.
            forced.intersection_update(solution)
            mapping = {}
            for index in solution:
                mapping.update(pool[index][2])
            pairs = {c: p for c, p in pairs.items() if mapping.get(c) == p}
            if not forced and not pairs:
                break
        return forced, set(pairs.items())
    require(reference['max_complete'] and reference['projection_complete'],
            'independent completeness flags missing')
    witness_map(pool, reference['witness'], reference['best_weight'])
    return set(reference['forced_candidates']), {
        (p['cipher_word_id'], p['source_word_id']) for p in reference['forced_word_values']}


def evaluate(pool, primary, independent):
    require(primary['status'] in ('COMPLETE', 'UNKNOWN_BUDGET'), 'primary status')
    weight = primary['best_weight']
    witness_map(pool, primary['oneoptimum'], weight)
    queries = primary['query_certificates']
    require(not queries or primary['stats']['best_weight_is_proven'], 'queries before maximum proof')
    complete_reference = independent['status'] == 'COMPLETE'
    forced, pairs = reference_projection(pool, independent) if complete_reference else (set(), set())
    if complete_reference and primary['stats']['best_weight_is_proven']:
        require(weight == independent['best_weight'], 'independent maximum differs')
    elif complete_reference:
        require(weight <= independent['best_weight'], 'invalid primary lower bound')
    counts = {'SAT_witnesses_checked': 0, 'UNSAT_queries_checked': 0, 'unknown_queries': 0}
    for query in queries:
        require(query['target_weight'] == weight, 'query target differs from optimum')
        require(query['kind'] in ('FORBID_CANDIDATE', 'FORBID_WORD_PAIR'), 'unknown query kind')
        if query['kind'] == 'FORBID_CANDIDATE':
            index = query['candidate_index']
            require(type(index) is int and 0 <= index < len(pool), 'query candidate bounds')
            independently_unsat = index in forced
        else:
            pair = tuple(query['word_pair'])
            require(len(pair) == 2 and all(type(x) is int for x in pair), 'invalid pair query')
            independently_unsat = pair in pairs
        if query['outcome'] == 'FOUND_WITNESS':
            mapping = witness_map(pool, query['witness'], weight)
            if query['kind'] == 'FORBID_CANDIDATE':
                require(index not in query['witness'], 'forbidden candidate retained')
            else:
                require(mapping.get(pair[0]) != pair[1], 'forbidden pair retained')
            counts['SAT_witnesses_checked'] += 1
        elif query['outcome'] == 'EXHAUSTIVE_UNSAT':
            require(query['witness'] is None, 'UNSAT has a witness')
            if complete_reference:
                require(independently_unsat, 'UNSAT contradicted by independent optimum family')
                counts['UNSAT_queries_checked'] += 1
        elif query['outcome'] == 'UNKNOWN_BUDGET':
            counts['unknown_queries'] += 1
        else:
            raise ValueError('unknown query outcome')
    if primary['status'] == 'COMPLETE':
        require(primary['stats']['best_weight_is_proven'] and
                primary['stats']['universal_projection_is_complete'] and
                counts['unknown_queries'] == 0, 'COMPLETE with unproved work')
        if complete_reference:
            reported = primary['forced_candidate_indices']
            require(len(reported) == len(set(reported)) and set(reported) == forced,
                    'forced candidate identity mismatch')
            reported_pairs = list(map(tuple, primary['forced_word_values']))
            require(len(reported_pairs) == len(set(reported_pairs)) and set(reported_pairs) == pairs,
                    'universal word-pair mismatch')
    else:
        require(primary['forced_candidate_indices'] is None and primary['forced_word_values'] is None,
                'UNKNOWN presents an incomplete projection as complete')
        require(not primary['stats']['universal_projection_is_complete'], 'UNKNOWN projection flag')
    return {'status': 'PASS' if primary['status'] == 'COMPLETE' and complete_reference else 'UNKNOWN_BUDGET',
            'primary_status': primary['status'], 'independent_status': independent['status'],
            'best_weight': weight, **counts,
            'forced_candidates': len(forced) if complete_reference else None,
            'forced_pairs': len(pairs) if complete_reference else None,
            'interpretation': 'Computational maximum and universal-projection parity; no optimum count, meaning, or null claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('input', 'primary', 'independent', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        result = evaluate(read_pool(args.input), json.loads(args.primary.read_text()),
                          json.loads(args.independent.read_text()))
    except (ValueError, KeyError, TypeError, IndexError, OSError) as exc:
        result = {'status': 'VALIDATION_ERROR', 'reason': str(exc)}
    result['input_sha256'] = sha(args.input)
    result['primary_result_sha256'] = sha(args.primary)
    result['independent_result_sha256'] = sha(args.independent)
    result['checker_sha256'] = sha(__file__)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status']}))
    if result['status'] == 'VALIDATION_ERROR':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
