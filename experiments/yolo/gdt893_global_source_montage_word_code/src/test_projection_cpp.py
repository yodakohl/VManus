"""Synthetic exhaustive validation of symbolic GDT893 optima and projection.

No manuscript, source corpus, held data, or frozen fit input is opened.
The oracle enumerates subsets and checks pairwise equality independently.
"""
from hashlib import sha256
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).parent


def candidate(paragraph, weight, mapping):
    return {"paragraph": paragraph, "weight": weight, "mapping": mapping}


def subset_oracle(candidates):
    best, optimum = 0, {()}
    for bits in range(1 << len(candidates)):
        chosen = tuple(i for i in range(len(candidates)) if bits & (1 << i))
        paragraphs = [candidates[i]["paragraph"] for i in chosen]
        if len(paragraphs) != len(set(paragraphs)):
            continue
        pairs = [(code, value) for i in chosen for code, value in candidates[i]["mapping"].items()]
        if any((a == b) != (u == v) for a, u in pairs for b, v in pairs):
            continue
        weight = sum(candidates[i]["weight"] for i in chosen)
        if weight > best:
            best, optimum = weight, set()
        if weight == best:
            optimum.add(chosen)
    forced_candidates = set.intersection(*(set(chosen) for chosen in optimum))
    forced_pairs = set.intersection(*({pair for i in chosen for pair in candidates[i]["mapping"].items()}
                                     for chosen in optimum))
    return best, optimum, forced_candidates, forced_pairs


class ProjectionCPPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("g++")
        if not compiler:
            raise RuntimeError("g++ required for projection validation")
        cls.temporary = tempfile.TemporaryDirectory(prefix="gdt893-projection-fixtures-")
        cls.scratch = Path(cls.temporary.name)
        source = (HERE / "solve_projection.cpp").read_bytes()
        cls.source_hash = sha256(source).hexdigest()
        frozen = cls.scratch / "solve_projection.cpp"
        frozen.write_bytes(source)
        cls.binary = cls.scratch / "solve_projection"
        subprocess.run([compiler, "-std=c++17", "-O3", "-DNDEBUG", "-Wall", "-Wextra",
                        str(frozen), "-o", str(cls.binary)], check=True, capture_output=True, text=True)
        cls.calls = cls.membership_calls = 0
        print(json.dumps({"validation": "INVENTED_EXHAUSTIVE_OPTIMA_AND_UNIVERSAL_PROJECTION",
                          "cpp_source_sha256": cls.source_hash}, sort_keys=True), flush=True)

    @classmethod
    def tearDownClass(cls):
        print(json.dumps({"cpp_fixture_calls": cls.calls, "membership_replays": cls.membership_calls,
                          "cpp_source_sha256": cls.source_hash}, sort_keys=True), flush=True)
        cls.temporary.cleanup()

    def run_cpp(self, candidates, seconds=10):
        self.input_path = self.scratch / "input.txt"
        output = self.scratch / "output.json"
        lines = [str(len(candidates))]
        for row in candidates:
            fields = [row["paragraph"], row["weight"], len(row["mapping"])]
            fields += [value for pair in row["mapping"].items() for value in pair]
            lines.append(" ".join(map(str, fields)))
        self.input_path.write_text("\n".join(lines) + "\n")
        process = subprocess.run([str(self.binary), str(self.input_path), str(output), str(seconds)],
                                 check=True, capture_output=True, text=True, timeout=30)
        type(self).calls += 1
        result = json.loads(output.read_text())
        summary = json.loads(process.stdout)
        self.assertEqual(summary["status"], result["status"])
        self.assertEqual(summary["best_weight"], result["best_weight"])
        return result

    def member(self, weight, indices):
        process = subprocess.run([str(self.binary), "--member", str(self.input_path), str(weight),
                                  *map(str, indices)], check=True, capture_output=True, text=True, timeout=10)
        type(self).membership_calls += 1
        return json.loads(process.stdout)["member"]

    def compare(self, rows, replay_all=False):
        best, optima, forced, pairs = subset_oracle(rows)
        result = self.run_cpp(rows)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["best_weight"], best)
        self.assertIn(tuple(result["oneoptimum"]), optima)
        self.assertEqual(set(result["forced_candidate_indices"]), forced)
        self.assertEqual({tuple(pair) for pair in result["forced_word_values"]}, pairs)
        self.assertTrue(result["stats"]["best_weight_is_proven"])
        self.assertTrue(result["stats"]["universal_projection_is_complete"])
        self.assertEqual(result["stats"]["upper_bound"], best)
        self.assertEqual(result["symbolic_optima"]["maximum_weight"], best)
        self.assertEqual(result["symbolic_optima"]["candidate_count"], len(rows))
        self.assertNotIn("optimal_solutions", result)
        self.assertNotIn("optimum_count", result)
        # Verify every claimed query result against the FULL optimum family.
        for query in result["query_certificates"]:
            self.assertEqual(query["target_weight"], best)
            if query["kind"] == "FORBID_CANDIDATE":
                possible = {chosen for chosen in optima if query["candidate_index"] not in chosen}
            else:
                pair = tuple(query["word_pair"])
                possible = {chosen for chosen in optima if all(pair not in rows[i]["mapping"].items()
                                                               for i in chosen)}
            if possible:
                self.assertEqual(query["outcome"], "FOUND_WITNESS")
                self.assertIn(tuple(query["witness"]), possible)
            else:
                self.assertEqual(query["outcome"], "EXHAUSTIVE_UNSAT")
                self.assertIsNone(query["witness"])
        if replay_all:
            for bits in range(1 << len(rows)):
                chosen = tuple(i for i in range(len(rows)) if bits & (1 << i))
                self.assertEqual(self.member(best, chosen), chosen in optima)
        return result

    def test_empty_and_zero_optimum(self):
        self.compare([], replay_all=True)
        result = self.compare([candidate(0, 0, {}), candidate(1, 0, {1: 3}),
                               candidate(1, 0, {1: 4})], replay_all=True)
        self.assertEqual(result["oneoptimum"], [])
        self.assertEqual(result["query_certificates"], [])

    def test_unique_optimum_proves_all_pairs_via_candidate(self):
        result = self.compare([candidate(0, 4, {0: 1, 1: 2}), candidate(1, 7, {2: 3}),
                               candidate(2, 3, {0: 4})], replay_all=True)
        self.assertEqual(result["forced_candidate_indices"], [0, 1])
        self.assertEqual(result["stats"]["word_projection_queries"], 0)

    def test_alias_candidates_can_force_words_without_forcing_candidate(self):
        result = self.compare([candidate(0, 5, {0: 8}), candidate(0, 5, {0: 8})], replay_all=True)
        self.assertEqual(result["forced_candidate_indices"], [])
        self.assertEqual(result["forced_word_values"], [[0, 8]])
        self.assertEqual(result["stats"]["word_projection_queries"], 1)

    def test_absent_code_is_a_word_counterexample(self):
        result = self.compare([candidate(0, 5, {0: 1}), candidate(0, 5, {})], replay_all=True)
        self.assertEqual(result["forced_word_values"], [])

    def test_changed_code_is_a_word_counterexample(self):
        self.compare([candidate(0, 5, {0: 1}), candidate(0, 5, {0: 2})], replay_all=True)

    def test_bulk_counterexample_intersection(self):
        rows = [candidate(p, 3, {42: variant}) for p in range(8) for variant in (0, 1)]
        result = self.compare(rows)
        self.assertEqual(result["forced_candidate_indices"], [])
        self.assertEqual(result["forced_word_values"], [])
        self.assertEqual(len(result["query_certificates"]), 1)

    def test_weighted_reverse_forward_and_paragraph_constraints(self):
        self.compare([candidate(0, 9, {0: 0, 1: 1}), candidate(1, 5, {0: 2}),
                      candidate(2, 5, {1: 3}), candidate(3, 3, {7: 3}),
                      candidate(3, 2, {8: 4}), candidate(1, 6, {9: 0})], replay_all=True)

    def test_large_signed_original_ids_are_returned(self):
        result = self.compare([candidate(-(2**60), 5, {2**60: -(2**61), -7: 2**59}),
                               candidate(3, 6, {2**60: -(2**61), 41: 99})], replay_all=True)
        self.assertIn([2**60, -(2**61)], result["forced_word_values"])

    def test_negative_and_optional_zero_candidates(self):
        self.compare([candidate(0, -3, {0: 0}), candidate(1, 4, {}),
                      candidate(2, 0, {0: 0}), candidate(2, 0, {0: 1})], replay_all=True)

    def test_independent_random_all_optima_and_query_certificates(self):
        rng = random.Random(893309)
        for iteration in range(240):
            rows = []
            for _ in range(rng.randrange(11)):
                size = rng.randrange(4)
                rows.append(candidate(rng.randrange(5), rng.randrange(-2, 10),
                                      dict(zip(rng.sample(range(6), size), rng.sample(range(7), size)))))
            self.compare(rows, replay_all=(iteration < 12))

    def test_exponential_zero_tie_family_is_symbolic_and_complete(self):
        rows = [candidate(i, 0, {i: i + 1000}) for i in range(200)]
        result = self.run_cpp(rows, seconds=2)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["best_weight"], 0)
        self.assertEqual(result["forced_candidate_indices"], [])
        self.assertEqual(result["forced_word_values"], [])
        self.assertTrue(self.member(0, list(range(200))))
        self.assertTrue(self.member(0, []))

    def test_exponential_positive_alias_family_never_materialized(self):
        rows = [candidate(i, 1, {i: i + 1000}) for i in range(55) for _ in range(2)]
        result = self.run_cpp(rows, seconds=5)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["best_weight"], 55)
        self.assertEqual(result["forced_candidate_indices"], [])
        self.assertEqual(len(result["forced_word_values"]), 55)
        self.assertLess(len(json.dumps(result)), 100000)

    def test_timeout_has_no_universal_projection_claim(self):
        result = self.run_cpp([candidate(0, 3, {0: 0})], seconds=0)
        self.assertEqual(result["status"], "UNKNOWN_BUDGET")
        self.assertFalse(result["stats"]["best_weight_is_proven"])
        self.assertIsNone(result["forced_candidate_indices"])
        self.assertIsNone(result["forced_word_values"])
        self.assertIsNone(result["symbolic_optima"]["maximum_weight"])

    def test_membership_rejects_duplicates_and_bad_indices(self):
        self.run_cpp([candidate(0, 4, {})])
        self.assertFalse(self.member(4, [0, 0]))
        self.assertFalse(self.member(4, [-1]))
        self.assertFalse(self.member(4, [1]))
        self.assertFalse(self.member(3, [0]))

    def test_noninjective_input_is_an_error(self):
        input_path, output = self.scratch / "bad.txt", self.scratch / "bad.json"
        input_path.write_text("1\n0 3 2 0 5 1 5\n")
        process = subprocess.run([str(self.binary), str(input_path), str(output), "10"],
                                 capture_output=True, text=True, timeout=10)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("Noninjective", process.stderr)


if __name__ == "__main__":
    unittest.main()
