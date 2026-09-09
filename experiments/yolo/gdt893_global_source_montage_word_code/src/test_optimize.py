"""Invented exact-subset oracle for the GDT893 coverage optimizer."""

import importlib.util
from pathlib import Path
import random
import time
import unittest
from unittest.mock import patch


_SPEC = importlib.util.spec_from_file_location("gdt893_optimize", Path(__file__).with_name("optimize.py"))
optimize = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(optimize)


def candidate(paragraph, weight, mapping):
    return {"paragraph": paragraph, "weight": weight, "mapping": mapping}


def brute(candidates):
    best = 0
    optimal = {()}
    for mask in range(1 << len(candidates)):
        selected = tuple(index for index in range(len(candidates)) if mask & (1 << index))
        paragraphs = [candidates[index]["paragraph"] for index in selected]
        if len(set(paragraphs)) != len(paragraphs):
            continue
        pairs = [(left, right) for index in selected for left, right in candidates[index]["mapping"].items()]
        # Pairwise equality equivalence independently establishes consistency
        # and injectivity, without reproducing the optimizer's two dictionaries.
        if any((left1 == left2) != (right1 == right2)
               for left1, right1 in pairs for left2, right2 in pairs):
            continue
        weight = sum(candidates[index]["weight"] for index in selected)
        if weight > best:
            best, optimal = weight, set()
        if weight == best:
            optimal.add(selected)
    return best, optimal


class OptimizeTests(unittest.TestCase):
    def compare(self, candidates):
        expected_weight, expected_sets = brute(candidates)
        result = optimize.solve(candidates, time.monotonic() + 20)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["best_weight"], expected_weight)
        self.assertEqual({tuple(indices) for indices in result["optimal_solutions"]}, expected_sets)
        self.assertEqual(len(result["optimal_solutions"]), len(expected_sets))
        self.assertEqual(result["stats"]["upper_bound"], expected_weight)
        self.assertTrue(result["stats"]["best_weight_is_proven"])
        return result

    def test_empty_input_retains_empty_optimum(self):
        result = self.compare([])
        self.assertEqual(result["optimal_solutions"], [[]])

    def test_at_most_one_candidate_per_paragraph(self):
        result = self.compare([candidate("p", 4, {0: 0}), candidate("p", 5, {1: 1})])
        self.assertEqual(result["optimal_solutions"], [[1]])

    def test_forward_and_reverse_conflicts_are_both_enforced(self):
        self.compare([candidate("p", 5, {0: 0}), candidate("q", 4, {0: 1}),
                      candidate("r", 3, {2: 0}), candidate("s", 2, {3: 3})])

    def test_shared_consistent_dictionary_accumulates(self):
        result = self.compare([candidate("p", 3, {0: 0, 1: 1}),
                               candidate("q", 4, {1: 1, 2: 2}),
                               candidate("r", 5, {0: 0, 2: 2})])
        self.assertEqual(result["best_weight"], 12)
        self.assertEqual(result["optimal_solutions"], [[0, 1, 2]])

    def test_weighted_coverage_is_not_paragraph_count(self):
        result = self.compare([candidate("long", 11, {0: 0, 1: 1}),
                               candidate("short-a", 5, {0: 2}),
                               candidate("short-b", 5, {1: 3})])
        self.assertEqual(result["optimal_solutions"], [[0]])

    def test_not_greedy_first_heavy_candidate(self):
        result = self.compare([candidate("long", 9, {0: 0, 1: 1}),
                               candidate("short-a", 5, {0: 2}),
                               candidate("short-b", 5, {1: 3})])
        self.assertEqual(result["optimal_solutions"], [[1, 2]])

    def test_alias_ties_are_not_collapsed_or_cut_at_equal_bound(self):
        result = self.compare([candidate("p", 4, {0: 0}), candidate("p", 4, {0: 0}),
                               candidate("q", 6, {1: 1})])
        self.assertEqual(result["optimal_solutions"], [[0, 2], [1, 2]])

    def test_alternative_coverage_sets_have_no_forced_paragraph(self):
        candidates = [candidate("p", 5, {0: 0}), candidate("q", 5, {0: 1})]
        result = self.compare(candidates)
        self.assertEqual(result["optimal_solutions"], [[0], [1]])
        covered = [{candidates[index]["paragraph"] for index in indices}
                   for indices in result["optimal_solutions"]]
        self.assertEqual(set.intersection(*covered), set())

    def test_shared_forced_paragraph_survives_ambiguous_other_readings(self):
        candidates = [candidate("forced", 4, {0: 0}), candidate("other", 5, {1: 1}),
                      candidate("other", 5, {1: 2})]
        result = self.compare(candidates)
        self.assertEqual(result["optimal_solutions"], [[0, 1], [0, 2]])
        self.assertEqual(set.intersection(*(set(indices) for indices in result["optimal_solutions"])), {0})

    def test_zero_weights_preserve_all_optimal_optional_subsets(self):
        result = self.compare([candidate("p", 0, {}), candidate("q", 0, {})])
        self.assertEqual({tuple(x) for x in result["optimal_solutions"]}, {(), (0,), (1,), (0, 1)})

    def test_negative_weights_cannot_help_and_empty_maps_are_valid(self):
        self.compare([candidate("p", -4, {0: 0}), candidate("q", 0, {}),
                      candidate("r", 5, {}), candidate("q", 0, {})])

    def test_small_random_inputs_against_all_subsets(self):
        rng = random.Random(893607)
        for _ in range(220):
            candidates = []
            for _ in range(rng.randrange(10)):
                size = rng.randrange(4)
                left = rng.sample(range(5), size)
                right = rng.sample(range(6), size)
                candidates.append(candidate("p" + str(rng.randrange(4)),
                                            rng.randrange(0, 9), dict(zip(left, right))))
            self.compare(candidates)

    def test_expired_deadline_retains_only_valid_lower_bound(self):
        result = optimize.solve([candidate("p", 3, {0: 0})], time.monotonic() - 1)
        self.assertEqual(result["status"], "UNKNOWN_BUDGET")
        self.assertEqual(result["best_weight"], 0)
        self.assertEqual(result["optimal_solutions"], [[]])
        self.assertFalse(result["stats"]["best_weight_is_proven"])

    def test_timeout_during_search_does_not_claim_first_hit_unique(self):
        # A deterministic fake clock checks deadline propagation without sleeps.
        clock = [0.0]
        calls = [0]
        def monotonic():
            calls[0] += 1
            if calls[0] >= 13:
                clock[0] = 2.0
            return clock[0]
        candidates = [candidate("p", 3, {0: 0}), candidate("p", 3, {0: 1}),
                      candidate("q", 4, {2: 2}), candidate("q", 4, {2: 3})]
        with patch.object(optimize.time, "monotonic", side_effect=monotonic):
            result = optimize.solve(candidates, 1.0)
        self.assertEqual(result["status"], "UNKNOWN_BUDGET")
        self.assertFalse(result["stats"]["best_weight_is_proven"])
        self.assertEqual(result["stats"]["upper_bound"], 7)
        for selected in result["optimal_solutions"]:
            self.assertEqual(sum(candidates[index]["weight"] for index in selected), result["best_weight"])
        self.assertLessEqual(result["best_weight"], 7)

    def test_input_errors_are_not_false_no_solution_findings(self):
        fixtures = [candidate("p", 1, {0: 0, 1: 0}), candidate("p", 1.5, {0: 0}),
                    candidate(1, 2, {0: 0}), candidate("p", 2, {"0": 0})]
        for item in fixtures:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    optimize.solve([item], time.monotonic() + 20)


if __name__ == "__main__":
    unittest.main()
