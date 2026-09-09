"""Invented fixtures for independent full-fit verifier; no real source/VM data."""
import csv
import itertools
import json
from pathlib import Path
import random
import subprocess
import tempfile
import time
import unittest
import validate as v


def candidate(paragraph, mapping, weight=2, plain=None):
    return {'paragraph': paragraph, 'mapping': mapping, 'weight': weight,
            'plain_word_ids': list(mapping.values()) if plain is None else plain}


def subset_oracle(candidates):
    best, optima = -1, set()
    for mask in range(1 << len(candidates)):
        indices = [i for i in range(len(candidates)) if mask >> i & 1]
        selected = [candidates[i] for i in indices]
        if len({c['paragraph'] for c in selected}) != len(selected):
            continue
        pairs = [(int(k), p) for c in selected for k, p in c['mapping'].items()]
        # Pairwise consistency oracle, not the validator's accumulated-map join.
        if any((a == c) != (b == d) for a, b in pairs for c, d in pairs):
            continue
        weight = sum(c['weight'] for c in selected)
        if weight > best:
            best, optima = weight, set()
        if weight == best:
            optima.add(tuple(indices))
    return best, optima


class ValidatorTests(unittest.TestCase):
    def test_direct_map_both_directions(self):
        self.assertEqual(v.direct_map([1, 2, 1], [5, 7, 5]), {1: 5, 2: 7})
        for target, plain in [([1, 1], [5, 7]), ([1, 2], [5, 5]), ([1], [5, 7])]:
            with self.assertRaises(ValueError):
                v.direct_map(target, plain)

    def test_exhaustive_optima_against_subset_oracle(self):
        rng = random.Random(89371)
        fixtures = [[], [candidate('a', {1: 2})],
                    [candidate('a', {1: 2}), candidate('b', {1: 3})],
                    [candidate('a', {1: 2}), candidate('b', {3: 2})],
                    [candidate('a', {1: 2}), candidate('a', {1: 3})]]
        for _ in range(60):
            pool = []
            for n in range(rng.randrange(1, 9)):
                keys = rng.sample(range(5), rng.randrange(1, 4))
                vals = rng.sample(range(6), len(keys))
                pool.append(candidate(str(rng.randrange(4)), dict(zip(keys, vals)), rng.randrange(1, 8)))
            fixtures.append(pool)
        for pool in fixtures:
            best, optima, _ = v.exhaustive_optima(pool, time.monotonic() + 10)
            self.assertEqual((best, optima), subset_oracle(pool))
        with self.assertRaises(v.BudgetExpired):
            v.exhaustive_optima([], time.monotonic() - 1)

    def test_cpp_optima_against_subset_oracle(self):
        rng = random.Random(1893)
        fixtures = [[], [candidate('a', {1: 2})],
                    [candidate('a', {1: 2}), candidate('b', {1: 3})],
                    [candidate('a', {1: 2}), candidate('b', {3: 2})],
                    [candidate('a', {1: 2}), candidate('a', {1: 3})]]
        for _ in range(70):
            pool = []
            weights = {str(g): rng.randrange(1, 9) for g in range(5)}
            for n in range(rng.randrange(1, 11)):
                keys = rng.sample(range(6), rng.randrange(1, 4))
                vals = rng.sample(range(7), len(keys))
                paragraph = str(rng.randrange(5))
                pool.append(candidate(paragraph, dict(zip(keys, vals)), weights[paragraph]))
            fixtures.append(pool)
        with tempfile.TemporaryDirectory(prefix='gdt893_optimum_fixture_') as folder:
            work = Path(folder)
            subprocess.run(['g++', '-std=c++17', '-O2', str(Path(__file__).with_name('validate_optima.cpp')),
                            '-o', str(work / 'oracle')], check=True, capture_output=True, timeout=60)
            for pool in fixtures:
                v.write_optimum_records(work / 'input', pool)
                subprocess.run([str(work / 'oracle'), str(work / 'input'), str(work / 'output'), '5'],
                               check=True, capture_output=True, timeout=6)
                result = json.loads((work / 'output').read_text())
                self.assertEqual(result['status'], 'COMPLETE')
                solutions = {tuple(row) for row in result['optimal_solutions']}
                self.assertEqual(len(solutions), len(result['optimal_solutions']))
                self.assertEqual((result['best_weight'], solutions), subset_oracle(pool))
            subprocess.run([str(work / 'oracle'), str(work / 'input'), str(work / 'output'), '-1'],
                           check=True, capture_output=True, timeout=6)
            self.assertEqual(json.loads((work / 'output').read_text())['status'], 'UNKNOWN_BUDGET')

    def test_projection_omission_is_distinct(self):
        pool = [candidate('a', {1: 2}, plain=[2]), candidate('b', {3: 4}, plain=[4])]
        self.assertEqual(v.project(pool, {(0,), (1,)}), {'forced_paragraphs': [], 'forced_word_values': []})
        self.assertEqual(v.project(pool, {(0,), (0, 1)}),
                         {'forced_paragraphs': [('a', (2,))], 'forced_word_values': [(1, 2)]})

    def test_candidate_alias_completeness(self):
        packet = {'cipher_words': ['alpha', 'beta'], 'source_words': ['x', 'y'],
                  'panels': {'E': [{'id': 'p', 'words': ['alpha', 'beta', 'alpha']}]},
                  'source_units': [{'id': 'u1', 'source': 's1', 'word_ids': [0, 1, 0]},
                                   {'id': 'u2', 'source': 's2', 'word_ids': [0, 1, 0]}]}
        c = {'paragraph': 'p', 'mapping': {'0': 0, '1': 1}, 'weight': 3,
             'target_index': 0, 'plain_word_ids': [0, 1, 0],
             'provenance': [{'unit': 'u1', 'source': 's1', 'start': 0, 'length': 3},
                            {'unit': 'u2', 'source': 's2', 'start': 0, 'length': 3}]}
        fit = {'candidates': [c], 'raw_matches': 2, 'candidate_materialization_complete': True}
        matches = {(0, 0, 0, 3), (0, 1, 0, 3)}
        self.assertEqual(v.validate_candidates(packet, 'E', fit, matches)['status'], 'PASS')
        c['provenance'].pop()
        with self.assertRaises(ValueError):
            v.validate_candidates(packet, 'E', fit, matches)

    def test_independent_cpp_matches_pairwise_oracle(self):
        targets = [list(p) for n in range(1, 5) for p in itertools.product(range(2), repeat=n)] + [[]]
        sources = [list(p) for n in range(7) for p in itertools.product(range(2), repeat=n)]
        expected = set()
        for ti, target in enumerate(targets):
            if not target:
                continue
            for si, source in enumerate(sources):
                for start in range(len(source) - len(target) + 1):
                    window = source[start:start + len(target)]
                    if all((target[a] == target[b]) == (window[a] == window[b])
                           for a in range(len(target)) for b in range(len(target))):
                        expected.add((ti, si, start, len(target)))
        with tempfile.TemporaryDirectory(prefix='gdt893_validator_fixture_') as folder:
            work = Path(folder)
            subprocess.run(['g++', '-std=c++17', '-O2', str(Path(__file__).with_name('validate_windows.cpp')),
                            '-o', str(work / 'oracle')], check=True, capture_output=True, timeout=60)
            v.write_records(work / 'targets', targets)
            v.write_records(work / 'sources', sources)
            subprocess.run([str(work / 'oracle'), str(work / 'targets'), str(work / 'sources'), str(work / 'matches')],
                           check=True, capture_output=True, timeout=60)
            with (work / 'matches').open() as handle:
                reader = csv.reader(handle)
                next(reader)
                rows = [tuple(map(int, row)) for row in reader]
            self.assertEqual(len(rows), len(set(rows)))
            self.assertEqual(set(rows), expected)


if __name__ == '__main__':
    unittest.main()
