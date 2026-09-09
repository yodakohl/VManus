#!/usr/bin/env python3
"""Independent whole-paragraph matcher checks on invented integer sequences only.

Compile the sibling C++ program and compare every returned window against a
simple two-way-map oracle. No implementation import and no research data reads.
"""
import csv
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import tempfile
import unittest


def equal_up_to_bijection(left, right):
    if len(left) != len(right):
        return False
    forward, reverse = {}, {}
    for a, b in zip(left, right):
        if a in forward and forward[a] != b:
            return False
        if b in reverse and reverse[b] != a:
            return False
        forward[a] = b
        reverse[b] = a
    return True


def exhaustive_windows(targets, sources):
    found = set()
    for ti, target in enumerate(targets):
        if not target:
            continue  # Empty sequence is not a complete paragraph.
        for si, source in enumerate(sources):
            for start in range(len(source) - len(target) + 1):
                if equal_up_to_bijection(target, source[start:start + len(target)]):
                    found.add((ti, si, start, len(target)))
    return found


def write_records(path, sequences, prefix):
    rows = [str(len(sequences))]
    # Reverse numeric labels deliberately disagree with input positions. IDs
    # are labels, not the target_index/source_index required in the output.
    for index, sequence in enumerate(sequences):
        label = prefix + str(10000 - index)
        rows.append(' '.join([label, str(len(sequence))] + list(map(str, sequence))))
    path.write_text('\n'.join(rows) + '\n')


class IndependentMatcherTests(unittest.TestCase):
    cases_checked = 0
    windows_checked = 0
    exact_matches_checked = 0

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='gdt893_match_fixture_')
        cls.work = Path(cls.temporary.name)
        cls.source = Path(__file__).with_name('match.cpp')
        if not cls.source.exists():
            raise RuntimeError('match.cpp not ready; no fixture test executed')
        cls.binary = cls.work / 'match'
        subprocess.run(['g++', '-std=c++17', '-O2', '-fopenmp', '-Wall', '-Wextra',
                        str(cls.source), '-o', str(cls.binary)],
                       check=True, capture_output=True, text=True, timeout=90)
        cls.source_sha256 = hashlib.sha256(cls.source.read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def assert_matches(self, targets, sources):
        target_file, source_file = self.work / 'target.txt', self.work / 'source.txt'
        output_file = self.work / 'matches.csv'
        write_records(target_file, targets, 't')
        write_records(source_file, sources, 's')
        if output_file.exists():
            output_file.unlink()
        subprocess.run([str(self.binary), str(target_file), str(source_file), str(output_file)],
                       check=True, capture_output=True, text=True, timeout=60)
        with output_file.open(newline='') as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            self.assertEqual(header, ['target_index', 'source_index', 'start', 'length'])
            actual_list = [tuple(int(value) for value in row) for row in reader]
        self.assertTrue(all(len(row) == 4 for row in actual_list))
        self.assertEqual(len(actual_list), len(set(actual_list)), 'duplicate output rows')
        expected = exhaustive_windows(targets, sources)
        actual = set(actual_list)
        self.assertEqual(actual, expected,
                         'missing=' + repr(sorted(expected - actual)[:5]) +
                         ' extra=' + repr(sorted(actual - expected)[:5]))
        cls = type(self)
        cls.cases_checked += 1
        cls.windows_checked += sum(max(0, len(s) - len(t) + 1) for t in targets if t for s in sources)
        cls.exact_matches_checked += len(expected)
        return actual

    def test_explicit_incidence_boundaries_and_overlaps(self):
        targets = [[3, 7, 3], [9, 9], [1, 2, 3, 4], [0],
                   [2, 3, 3, 2], [1, 2, 1, 3], [7, 7, 7, 7, 7, 7]]
        sources = [[80, 90, 80, 90, 80], [4, 4, 4], [1, 2, 3, 4, 5],
                   [90, 80, 80, 90], [2, 3, 2, 2], [3], [], [1, 2]]
        result = self.assert_matches(targets, sources)
        self.assertIn((0, 0, 0, 3), result)
        self.assertIn((0, 0, 1, 3), result)
        self.assertIn((0, 0, 2, 3), result)
        self.assertIn((1, 1, 0, 2), result)
        self.assertIn((1, 1, 1, 2), result)
        self.assertFalse(any(ti == 6 for ti, _, _, _ in result))
        # [1,2,1,3] and [2,3,2,2] violate injectivity in the reverse map.
        self.assertNotIn((5, 4, 0, 4), result)

    def test_exhaustive_binary_sequences(self):
        targets = [list(x) for n in range(1, 6) for x in itertools.product(range(2), repeat=n)]
        sources = [list(x) for n in range(8) for x in itertools.product(range(2), repeat=n)]
        self.assert_matches(targets, sources)

    def test_deterministic_random_and_large_symbol_ids(self):
        rng = random.Random(893)
        targets = [[rng.randrange(rng.randrange(1, 8)) for _ in range(rng.randrange(1, 18))]
                   for _ in range(60)]
        sources = [[rng.randrange(8) for _ in range(rng.randrange(0, 40))] for _ in range(30)]
        # Add guaranteed positives of lengths larger than a small fixed mask.
        long = [n % 11 for n in range(75)]
        targets.append(long)
        sources.append([999999] + [x * 101 + 700001 for x in long] + [999999])
        original = self.assert_matches(targets, sources)
        target_renaming = {x: 1000000 + 37 * x for row in targets for x in row}
        source_renaming = {x: 5000000 + 41 * x for row in sources for x in row}
        renamed = self.assert_matches([[target_renaming[x] for x in row] for row in targets],
                                      [[source_renaming[x] for x in row] for row in sources])
        self.assertEqual(original, renamed)
        self.assertIn((len(targets) - 1, len(sources) - 1, 1, 75), original)

    def test_no_sources_and_no_targets(self):
        self.assert_matches([[1, 2, 1]], [])
        self.assert_matches([], [[1, 2, 1]])
        self.assert_matches([[], [1], []], [[], [1, 2, 1]])

    def test_source_units_must_not_be_concatenated(self):
        self.assertEqual(self.assert_matches([[1, 2, 3, 4]], [[1, 2], [3, 4]]), set())


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IndependentMatcherTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'status': 'PASS' if result.wasSuccessful() else 'FAIL',
                      'fixture_batches': IndependentMatcherTests.cases_checked,
                      'oracle_windows': IndependentMatcherTests.windows_checked,
                      'exact_match_rows': IndependentMatcherTests.exact_matches_checked,
                      'matcher_sha256': getattr(IndependentMatcherTests, 'source_sha256', None),
                      'scope': 'Invented sequence fixtures only; no research data.'}, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
