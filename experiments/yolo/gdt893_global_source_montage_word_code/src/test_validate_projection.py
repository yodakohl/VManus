"""Independent projection proof fixtures against explicit subset enumeration."""
import json
from pathlib import Path
import random
import subprocess
import tempfile
import unittest


def oracle(pool):
    best, solutions = -1, []
    for mask in range(1 << len(pool)):
        ids = [i for i in range(len(pool)) if mask >> i & 1]
        rows = [pool[i] for i in ids]
        if len({r[0] for r in rows}) != len(rows):
            continue
        pairs = [p for r in rows for p in r[2]]
        if any((a == c) != (b == d) for a, b in pairs for c, d in pairs):
            continue
        weight = sum(r[1] for r in rows)
        if weight > best:
            best, solutions = weight, []
        if weight == best:
            solutions.append(set(ids))
    forced = set.intersection(*solutions)
    values = [set(p for i in s for p in pool[i][2]) for s in solutions]
    return best, solutions, forced, set.intersection(*values)


def write(path, pool):
    with path.open('w') as f:
        f.write(str(len(pool)) + '\n')
        for paragraph, weight, pairs in pool:
            numbers = [paragraph, weight, len(pairs)] + [v for pair in pairs for v in pair]
            f.write(' '.join(map(str, numbers)) + '\n')


class ProjectionTests(unittest.TestCase):
    def test_queries_and_projection_match_all_subsets(self):
        rng = random.Random(893991)
        pools = [[], [(0, 1, [(1, 2)])],
                 [(0, 2, [(1, 2), (3, 4)]), (0, 2, [(1, 2), (3, 5)])],
                 [(0, 2, [(1, 2)]), (1, 2, [(1, 3)])],
                 [(0, 2, [(1, 2)]), (1, 2, [(3, 2)])],
                 [(0, 2, [(1, 2)]), (1, 3, [(3, 4)])]]
        for _ in range(100):
            weights = [rng.randrange(1, 8) for _ in range(5)]
            pool = []
            for _ in range(rng.randrange(1, 11)):
                group = rng.randrange(5)
                n = rng.randrange(1, 4)
                pool.append((group, weights[group], list(zip(rng.sample(range(6), n), rng.sample(range(7), n)))))
            pools.append(pool)
        with tempfile.TemporaryDirectory(prefix='gdt893_projection_fixture_') as folder:
            work = Path(folder)
            subprocess.run(['g++', '-O2', '-std=c++17', str(Path(__file__).with_name('validate_projection.cpp')),
                            '-o', str(work / 'oracle')], check=True, capture_output=True, timeout=60)
            for pool in pools:
                write(work / 'input', pool)
                subprocess.run([str(work / 'oracle'), str(work / 'input'), str(work / 'output'), '5'],
                               check=True, capture_output=True, timeout=6)
                result = json.loads((work / 'output').read_text())
                self.assertEqual(result['status'], 'COMPLETE')
                best, solutions, forced, values = oracle(pool)
                self.assertEqual(result['best_weight'], best)
                self.assertIn(set(result['witness']), solutions)
                self.assertEqual(set(result['forced_candidates']), forced)
                self.assertEqual({(p['cipher_word_id'], p['source_word_id']) for p in result['forced_word_values']}, values)
                for query in result['queries']:
                    if query['kind'] == 'candidate':
                        satisfying = [s for s in solutions if query['candidate'] not in s]
                    else:
                        pair = tuple(query['pair'])
                        satisfying = [s for s in solutions if all(pair not in pool[i][2] for i in s)]
                    self.assertEqual(query['status'], 'SAT' if satisfying else 'UNSAT')
                    if satisfying:
                        self.assertIn(set(query['witness']), satisfying)
            subprocess.run([str(work / 'oracle'), str(work / 'input'), str(work / 'output'), '-1'],
                           check=True, capture_output=True, timeout=6)
            result = json.loads((work / 'output').read_text())
            self.assertEqual(result['status'], 'UNKNOWN_BUDGET')
            self.assertFalse(result['projection_complete'])


if __name__ == '__main__':
    unittest.main()
