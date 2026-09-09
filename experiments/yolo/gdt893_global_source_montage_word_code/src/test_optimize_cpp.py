"""Independent synthetic parity checks for the exact C++ acceleration.

Compiles only optimize_cpp.cpp and creates only invented candidate records.
Checks complete result sets against both exhaustive subsets and optimize.py.
"""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import time
import unittest


HERE = Path(__file__).parent
_SPEC = importlib.util.spec_from_file_location("gdt893_python_reference", HERE / "optimize.py")
python_reference = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(python_reference)


def candidate(paragraph, weight, mapping):
    return {"paragraph": paragraph, "weight": weight, "mapping": mapping}


def subset_oracle(candidates):
    best, optimal = 0, {()}
    for mask in range(1 << len(candidates)):
        chosen = tuple(index for index in range(len(candidates)) if mask & (1 << index))
        paragraphs = [candidates[index]["paragraph"] for index in chosen]
        if len(set(paragraphs)) != len(paragraphs):
            continue
        pairs = [(code, value) for index in chosen for code, value in candidates[index]["mapping"].items()]
        if any((a == b) != (x == y) for a, x in pairs for b, y in pairs):
            continue
        weight = sum(candidates[index]["weight"] for index in chosen)
        if weight > best:
            best, optimal = weight, set()
        if weight == best:
            optimal.add(chosen)
    return best, optimal


class OptimizeCPPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("g++")
        if compiler is None:
            raise RuntimeError("g++ is required for executable C++ optimizer validation")
        cls.temporary = tempfile.TemporaryDirectory(prefix="gdt893-cpp-fixtures-")
        cls.scratch = Path(cls.temporary.name)
        source = (HERE / "optimize_cpp.cpp").read_bytes()
        cls.source_hash = sha256(source).hexdigest()
        cls.reference_hash = sha256((HERE / "optimize.py").read_bytes()).hexdigest()
        frozen = cls.scratch / "optimize_cpp.cpp"
        frozen.write_bytes(source)
        cls.binary = cls.scratch / "optimize_cpp"
        subprocess.run([compiler, "-std=c++17", "-O3", "-DNDEBUG", str(frozen), "-o", str(cls.binary)],
                       check=True, capture_output=True, text=True)
        cls.calls = 0
        print(json.dumps({"validation": "INVENTED_COMPLETE_SUBSET_AND_PYTHON_PARITY",
                          "cpp_source_sha256": cls.source_hash,
                          "python_source_sha256": cls.reference_hash}, sort_keys=True), flush=True)

    @classmethod
    def tearDownClass(cls):
        print(json.dumps({"cpp_fixture_calls": cls.calls, "cpp_source_sha256": cls.source_hash},
                         sort_keys=True), flush=True)
        cls.temporary.cleanup()

    def run_cpp(self, candidates, seconds=10):
        input_path, output_path = self.scratch / "input.txt", self.scratch / "output.json"
        lines = [str(len(candidates))]
        for row in candidates:
            fields = [row["paragraph"], row["weight"], len(row["mapping"])]
            fields.extend(value for pair in row["mapping"].items() for value in pair)
            lines.append(" ".join(map(str, fields)))
        input_path.write_text("\n".join(lines) + "\n")
        completed = subprocess.run([str(self.binary), str(input_path), str(output_path), str(seconds)],
                                   check=True, capture_output=True, text=True, timeout=30)
        type(self).calls += 1
        result = json.loads(output_path.read_text())
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["status"], result["status"])
        self.assertEqual(summary["best_weight"], result["best_weight"])
        self.assertEqual(summary["solution_sets"], len(result["optimal_solutions"]))
        return result

    def compare(self, candidates):
        expected_weight, expected_sets = subset_oracle(candidates)
        cpp = self.run_cpp(candidates)
        python_candidates = [dict(row, paragraph=str(row["paragraph"])) for row in candidates]
        py = python_reference.solve(python_candidates, time.monotonic() + 10)
        for result in (cpp, py):
            self.assertEqual(result["status"], "COMPLETE")
            self.assertEqual(result["best_weight"], expected_weight)
            self.assertEqual({tuple(indices) for indices in result["optimal_solutions"]}, expected_sets)
            self.assertEqual(len(result["optimal_solutions"]), len(expected_sets))
            self.assertEqual(result["stats"]["upper_bound"], expected_weight)
            self.assertTrue(result["stats"]["best_weight_is_proven"])
        return cpp

    def test_empty_and_zero_weight_omission_ties(self):
        self.compare([])
        result = self.compare([candidate(0, 0, {}), candidate(1, 0, {})])
        self.assertEqual(result["optimal_solutions"], [[], [0], [0, 1], [1]])

    def test_forward_reverse_and_paragraph_exclusion(self):
        self.compare([candidate(0, 5, {0: 0}), candidate(1, 4, {0: 1}),
                      candidate(2, 3, {2: 0}), candidate(0, 6, {3: 3}),
                      candidate(3, 2, {4: 4})])

    def test_all_equally_optimal_aliases_and_coverages(self):
        self.compare([candidate(0, 4, {0: 0}), candidate(0, 4, {0: 0}),
                      candidate(1, 6, {1: 1})])
        result = self.compare([candidate(0, 5, {0: 0}), candidate(1, 5, {0: 1})])
        self.assertEqual(result["optimal_solutions"], [[0], [1]])

    def test_weight_not_candidate_count_and_no_greedy_selection(self):
        for heavy in (9, 10, 11):
            self.compare([candidate(0, heavy, {0: 0, 1: 1}),
                          candidate(1, 5, {0: 2}), candidate(2, 5, {1: 3})])

    def test_dense_id_compression_preserves_large_signed_ids(self):
        self.compare([candidate(-100, 4, {2**60: -(2**60), -50: 900}),
                      candidate(2**55, 6, {-50: 900, 77: -66}),
                      candidate(3, 8, {2**60: 901})])

    def test_negative_weights_and_empty_mappings(self):
        self.compare([candidate(0, -5, {0: 0}), candidate(1, 0, {}),
                      candidate(2, 7, {}), candidate(1, 0, {})])

    def test_undo_shared_keys_across_sibling_branches(self):
        self.compare([candidate(0, 3, {0: 0, 1: 1}), candidate(0, 3, {0: 2, 1: 3}),
                      candidate(1, 4, {0: 0, 2: 2}), candidate(1, 4, {0: 2, 2: 0}),
                      candidate(2, 5, {1: 1, 3: 3}), candidate(2, 5, {1: 3, 3: 1})])

    def test_random_complete_subset_and_python_parity(self):
        rng = random.Random(893206)
        for _ in range(180):
            rows = []
            for _ in range(rng.randrange(11)):
                size = rng.randrange(4)
                rows.append(candidate(rng.randrange(5), rng.randrange(-1, 10),
                                      dict(zip(rng.sample(range(6), size), rng.sample(range(7), size)))))
            self.compare(rows)

    def test_zero_time_is_unknown_not_an_empty_optimum_claim(self):
        result = self.run_cpp([candidate(0, 3, {0: 0})], seconds=0)
        self.assertEqual(result["status"], "UNKNOWN_BUDGET")
        self.assertEqual(result["best_weight"], 0)
        self.assertEqual(result["optimal_solutions"], [[]])
        self.assertFalse(result["stats"]["best_weight_is_proven"])

    def test_huge_tie_space_times_out_without_solution_cap(self):
        # 2**45 equally optimal optional subsets cannot be exhausted during
        # this tiny cooperative budget.  No truth or real ciphertext is used.
        rows = [candidate(index, 0, {}) for index in range(45)]
        result = self.run_cpp(rows, seconds=.003)
        self.assertEqual(result["status"], "UNKNOWN_BUDGET")
        self.assertEqual(result["best_weight"], 0)
        self.assertFalse(result["stats"]["best_weight_is_proven"])
        self.assertTrue(all(indices == sorted(set(indices)) for indices in result["optimal_solutions"]))
        self.assertTrue(all(all(0 <= index < 45 for index in indices) for indices in result["optimal_solutions"]))

    def test_noninjective_local_input_is_error(self):
        input_path, output_path = self.scratch / "bad.txt", self.scratch / "bad.json"
        input_path.write_text("1\n0 3 2 0 5 1 5\n")
        result = subprocess.run([str(self.binary), str(input_path), str(output_path), "10"],
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Noninjective", result.stderr)


if __name__ == "__main__":
    unittest.main()
