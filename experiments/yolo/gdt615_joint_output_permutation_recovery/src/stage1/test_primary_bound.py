#!/usr/bin/env python3
"""Toy tests for the GDT615 Stage-1 primary necessary bound."""

from __future__ import annotations

import unittest

if __package__:
    from . import primary_bound as bound
else:
    import primary_bound as bound


class NecessaryBoundToyTests(unittest.TestCase):
    def test_isolated_unsupported_ineligible_node_is_unsat(self) -> None:
        instance = bound.BoundInstance(
            merge_names=("m1", "m2", "m3"),
            eligible_paid_ranks=frozenset({2, 3}),
            unsupported_subtrees={1: (1,)},
            paid_location_count=2,
        )
        result = bound.solve_bound(instance)
        self.assertEqual(result["status"], "UNSAT")
        self.assertEqual(
            result["minimal_unsat_core_labels"],
            [
                "E01_paid_requires_train_child_span",
                "U01_raw_unsupported_requires_paid_subtree",
            ],
        )
        self.assertTrue(result["core_subset_minimal"])

    def test_sibling_paid_node_cannot_cover_unsupported_merge(self) -> None:
        instance = bound.BoundInstance(
            merge_names=("left", "right"),
            eligible_paid_ranks=frozenset({2}),
            unsupported_subtrees={1: (1,)},
            paid_location_count=1,
        )
        self.assertEqual(bound.solve_bound(instance)["status"], "UNSAT")

    def test_eligible_descendant_can_cover_unsupported_parent(self) -> None:
        instance = bound.BoundInstance(
            merge_names=("child", "parent", "extra"),
            eligible_paid_ranks=frozenset({1, 3}),
            unsupported_subtrees={2: (1, 2)},
            paid_location_count=2,
        )
        result = bound.solve_bound(instance)
        self.assertEqual(result["status"], "SAT")
        self.assertEqual(result["witness_paid_ranks"], [1, 3])

    def test_exact_paid_cardinality_is_part_of_formula(self) -> None:
        instance = bound.BoundInstance(
            merge_names=("m1", "m2"),
            eligible_paid_ranks=frozenset({1}),
            unsupported_subtrees={},
            paid_location_count=2,
        )
        result = bound.solve_bound(instance)
        self.assertEqual(result["status"], "UNSAT")
        self.assertIn(
            "C000_exactly_2_paid_locations", result["minimal_unsat_core_labels"]
        )
        self.assertIn(
            "E02_paid_requires_train_child_span",
            result["minimal_unsat_core_labels"],
        )

    def test_inclusive_subtree_must_contain_root(self) -> None:
        instance = bound.BoundInstance(
            merge_names=("m1", "m2"),
            eligible_paid_ranks=frozenset({1, 2}),
            unsupported_subtrees={2: (1,)},
            paid_location_count=1,
        )
        with self.assertRaisesRegex(bound.BoundError, "contain its root"):
            bound.solve_bound(instance)


if __name__ == "__main__":
    unittest.main()
