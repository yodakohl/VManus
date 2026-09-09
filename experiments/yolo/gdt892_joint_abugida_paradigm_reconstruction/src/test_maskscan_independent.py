"""Independent invented-codebook oracle for the GDT892 C++ mask scanner.

No control ciphertext, target data, decoder module, or source lexicon is read.
The oracle enumerates actual prefix-free codebooks, then recursively decodes
strings from those codebooks.  It does not infer cuts from a singleton mask.
"""

from functools import lru_cache
from hashlib import sha256
from itertools import combinations, product
import csv
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).with_name("maskscan.cpp")


def canonical_pattern(codes):
    ordered_unique = []
    output = []
    for code in codes:
        if code not in ordered_unique:
            ordered_unique.append(code)
        output.append(ordered_unique.index(code))
    return bytes(output)


@lru_cache(maxsize=None)
def actual_codebooks(alphabet, component_count):
    candidates = tuple(alphabet) + tuple(a + b for a in alphabet for b in alphabet)
    output = []
    for codebook in combinations(candidates, component_count):
        if any(left != right and right.startswith(left)
               for left in codebook for right in codebook):
            continue
        output.append(codebook)
    return tuple(output)


def decode_from_codebook(word, codebook):
    """Direct independent dictionary parsing, without a mask/cut rule."""
    def visit(position, consumed):
        if position == len(word):
            yield tuple(consumed)
            return
        for code in codebook:
            if word.startswith(code, position):
                yield from visit(position + len(code), consumed + [code])
    solutions = list(visit(0, []))
    if len(solutions) > 1:
        raise AssertionError("The enumerated codebook was not uniquely decodable")
    return solutions[0] if solutions else None


def brute_oracle(alphabet, words, pattern_sets, component_count):
    """Project all actual legal complete codebooks onto (mask, live bits)."""
    result = {}
    for codebook in actual_codebooks(alphabet, component_count):
        decoded = [decode_from_codebook(word, codebook) for word in words]
        if any(value is None for value in decoded):
            continue
        patterns = [canonical_pattern(value) for value in decoded]
        alive = sum(1 << index for index, allowed in enumerate(pattern_sets)
                    if all(pattern in allowed for pattern in patterns))
        if not alive:
            continue
        singleton_mask = sum(1 << alphabet.index(code) for code in codebook if len(code) == 1)
        # For a fixed singleton set a prefix-free length1/2 codebook has the
        # same observed cut pattern regardless of its unused double codes.
        if singleton_mask in result and result[singleton_mask] != alive:
            raise AssertionError("Codebooks with the same singletons disagree")
        result[singleton_mask] = alive
    return result


def pattern_universe(maximum=4):
    return {canonical_pattern(sequence)
            for length in range(1, maximum + 1)
            for sequence in product(range(maximum), repeat=length)}


class MaskscanIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("g++")
        if compiler is None:
            raise RuntimeError("g++ is required for executable maskscan validation")
        cls.temporary = tempfile.TemporaryDirectory(prefix="gdt892-mask-fixtures-")
        cls.scratch = Path(cls.temporary.name)
        source_bytes = SOURCE.read_bytes()
        cls.source_sha256 = sha256(source_bytes).hexdigest()
        frozen_source = cls.scratch / "maskscan.cpp"
        frozen_source.write_bytes(source_bytes)
        cls.binary = cls.scratch / "maskscan"
        subprocess.run([compiler, "-std=c++17", "-O2", "-fopenmp", str(frozen_source),
                        "-o", str(cls.binary)], check=True, capture_output=True, text=True)
        cls.calls = 0
        print(json.dumps({"validation": "INVENTED_CODEBOOK_ENUMERATION",
                          "maskscan_source_sha256": cls.source_sha256}, sort_keys=True), flush=True)

    @classmethod
    def tearDownClass(cls):
        print(json.dumps({"maskscan_fixture_calls": cls.calls,
                          "maskscan_source_sha256": cls.source_sha256}, sort_keys=True), flush=True)
        cls.temporary.cleanup()

    def run_scanner(self, alphabet, words, pattern_sets, component_count):
        self.assertEqual(len(pattern_sets), 6)
        payload = bytearray()
        for allowed in pattern_sets:
            ordered = sorted(allowed)
            payload.extend(struct.pack("<I", len(ordered)))
            for pattern in ordered:
                payload.extend(struct.pack("<H", len(pattern)))
                payload.extend(pattern)
        patterns_path = self.scratch / "patterns.bin"
        input_path = self.scratch / "input.txt"
        output_path = self.scratch / "output.csv"
        patterns_path.write_bytes(payload)
        input_path.write_text(alphabet + "\n" + str(len(words)) + "\n" + "\n".join(words) + "\n")
        command = [str(self.binary), str(patterns_path), str(input_path), str(output_path)]
        if component_count is not None:
            command.append(str(component_count))
        environment = dict(os.environ, OMP_THREAD_LIMIT="1")
        completed = subprocess.run(command, check=True, capture_output=True, text=True,
                                   env=environment, timeout=20)
        type(self).calls += 1
        status = json.loads(completed.stdout)
        self.assertEqual(status["status"], "COMPLETE")
        self.assertEqual(status["masks_examined"], 1 << len(alphabet))
        with output_path.open() as stream:
            records = list(csv.DictReader(stream))
        result = {int(row["mask"]): int(row["inherent_bits"]) for row in records}
        self.assertEqual(len(records), len(result))
        self.assertEqual(status["surviving_masks"], len(result))
        self.assertEqual(list(result), sorted(result))
        self.assertTrue(all(0 < bits < 64 for bits in result.values()))
        return result

    def compare(self, alphabet, words, patterns, count):
        expected = brute_oracle(alphabet, words, patterns, count)
        actual = self.run_scanner(alphabet, words, patterns, count)
        self.assertEqual(actual, expected, (alphabet, words, count))
        return actual

    def test_all_binary_words_through_length_four_and_all_small_codebooks(self):
        universe = pattern_universe()
        six = [universe, {bytes([0]), bytes([0, 1])},
               {bytes([0, 0]), bytes([0, 1, 0]), bytes([0, 1, 0, 1])},
               {bytes([0, 1, 2]), bytes([0, 0, 1])},
               universe - {bytes([0])}, set()]
        for count in range(1, 5):
            for length in range(1, 5):
                for letters in product("ab", repeat=length):
                    with self.subTest(count=count, word="".join(letters)):
                        self.compare("ab", ["".join(letters)], six, count)

    def test_joint_word_vocabulary_and_inherent_intersection(self):
        universe = pattern_universe()
        six = [universe, {bytes([0])}, {bytes([0, 0])},
               {bytes([0, 1])}, {bytes([0]), bytes([0, 0])}, set()]
        fixtures = [["aa", "ab", "ba"], ["ab", "abab"], ["a", "bb"],
                    ["aa", "bb", "cc"], ["ab", "bc", "ca"], ["abc", "cba"]]
        for words in fixtures:
            alphabet = "abc" if any("c" in word for word in words) else "ab"
            for count in range(1, 5):
                with self.subTest(words=words, count=count):
                    self.compare(alphabet, words, six, count)

    def test_trailing_half_code_cannot_be_consumed(self):
        result = self.compare("ab", ["a"], [{bytes([0])}] * 6, 2)
        self.assertNotIn(0, result)
        self.assertIn(3, result)

    def test_global_used_code_cap_even_when_each_word_matches(self):
        # Three distinct observed length2 codes cannot fit a two-component
        # codebook.  Each word individually has the allowed pattern[0].
        result = self.compare("ab", ["aa", "ab", "ba"], [{bytes([0])}] * 6, 2)
        self.assertEqual(result, {})

    def test_unused_singletons_count_in_exact_codebook_completion(self):
        result = self.compare("abc", ["a"], [{bytes([0])}] * 6, 2)
        self.assertNotIn(7, result)

    def test_total_completion_capacity(self):
        result = self.compare("ab", ["a"], [{bytes([0])}] * 6, 3)
        self.assertNotIn(3, result)

    def test_all_six_inherent_values_remain_unknown(self):
        result = self.compare("abc", ["aa"], [{bytes([0, 0])}] * 6, 3)
        self.assertTrue(result)
        self.assertEqual(set(result.values()), {63})

    def test_single_inherent_bit_is_not_renumbered(self):
        six = [set() for _ in range(6)]
        six[4] = {bytes([0, 0])}
        result = self.compare("abc", ["aa"], six, 3)
        self.assertTrue(result)
        self.assertEqual(set(result.values()), {16})

    def test_multiple_equivalent_observed_masks_are_retained(self):
        result = self.compare("abc", ["aa"], [{bytes([0, 0])}] * 6, 3)
        self.assertEqual(set(result), {1, 3, 5, 7})
        for mask in result:
            witnesses = [book for book in actual_codebooks("abc", 3)
                         if sum(1 << "abc".index(code) for code in book if len(code) == 1) == mask]
            observed = {decode_from_codebook("aa", book) for book in witnesses}
            self.assertEqual(observed, {("a", "a")})

    def test_empty_source_pattern_decks_admit_no_inherent_value(self):
        self.assertEqual(self.compare("ab", ["aa"], [set()] * 6, 2), {})

    def test_primary_default_component_count_stays_twenty_seven(self):
        # A binary alphabet has only four available length1/2 codewords at
        # maximum capacity, hence cannot support the default27 components.
        self.assertEqual(self.run_scanner("ab", ["aa"], [pattern_universe()] * 6, None), {})


if __name__ == "__main__":
    unittest.main()
