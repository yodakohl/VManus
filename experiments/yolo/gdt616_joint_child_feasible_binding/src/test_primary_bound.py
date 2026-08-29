#!/usr/bin/env python3
"""Toy-only tests for the GDT616 primary Stage-A necessary bound."""

from __future__ import annotations

import unittest

import z3

if __package__:
    from . import primary_bound as bound
else:
    import primary_bound as bound


def card(card_id: str, role: str, output: str, side: str | None = None) -> bound.Card:
    return bound.Card(card_id, role, output, side)


def two_merge_instance(
    *,
    train: set[str],
    paid: tuple[bound.Card, ...] | None = None,
    names: tuple[str, str] = ("ab", "aba"),
) -> bound.Instance:
    primitives = (bound.Primitive("A", "literal"), bound.Primitive("B", "literal"))
    cards = {
        "literal": (
            card("L01", "literal", "a"),
            card("L02", "literal", "b"),
        )
    }
    paid_cards = paid or (
        card("P01", "short_card", "x"),
        card("P02", "short_card", "y"),
    )
    merges = (
        bound.Merge(1, "A", "B", names[0]),
        bound.Merge(2, names[0], "A", names[1]),
    )
    return bound.Instance(
        primitives,
        cards,
        tuple(sorted(paid_cards, key=lambda row: row.card_id)),
        merges,
        frozenset(train),
    )


class PrimaryBoundToyTests(unittest.TestCase):
    def test_sat_uses_complete_paid_bijection_and_recursive_effective_value(self) -> None:
        instance = two_merge_instance(
            train={"x", "y", "ab", "ba", "xa", "xb", "ya", "yb"},
        )
        result = bound.solve_instance(instance)
        self.assertEqual(result["decision"], "JOINT_CHILD_NECESSARY_BOUND_SAT")
        witness = result["witness"]
        self.assertEqual(len(witness["paid_assignments"]), 2)
        self.assertEqual(
            {row["card_id"] for row in witness["paid_assignments"]}, {"P01", "P02"}
        )
        self.assertTrue(all(row["child_is_train_substring"] for row in witness["merges"]))

    def test_paid_card_cannot_rescue_missing_child_counterpart(self) -> None:
        instance = two_merge_instance(train={"xa", "xb", "ya", "yb"})
        result = bound.solve_instance(instance)
        self.assertEqual(result["decision"], "NO_JOINT_CHILD_FEASIBLE_BINDING")

    def test_paid_effective_output_itself_must_be_in_train(self) -> None:
        instance = two_merge_instance(
            train={"ab", "ba", "xa", "xb", "ya", "yb"},
        )
        result = bound.solve_instance(instance)
        self.assertEqual(result["decision"], "NO_JOINT_CHILD_FEASIBLE_BINDING")

    def test_paid_output_must_differ_from_child_composition(self) -> None:
        instance = bound.Instance(
            primitives=(bound.Primitive("A", "fixed"), bound.Primitive("B", "fixed2")),
            cards_by_role={
                "fixed": (card("A01", "fixed", "a"),),
                "fixed2": (card("B01", "fixed2", "b"),),
            },
            paid_cards=(card("P01", "short_card", "ab"),),
            merges=(bound.Merge(1, "A", "B", "ab"),),
            train_substrings=frozenset({"ab"}),
        )
        result = bound.solve_instance(instance)
        self.assertEqual(result["decision"], "NO_JOINT_CHILD_FEASIBLE_BINDING")

    def test_qok_paid_macro_is_statically_forbidden(self) -> None:
        instance = bound.Instance(
            primitives=(bound.Primitive("q", "qrole"), bound.Primitive("o", "orole")),
            cards_by_role={
                "qrole": (card("Q01", "qrole", "a"),),
                "orole": (card("O01", "orole", "b"),),
            },
            paid_cards=(card("M01", "macro_core", "con", "RIGHT_HOST"),),
            merges=(bound.Merge(1, "q", "o", "qok"),),
            train_substrings=frozenset({"ab", "con"}),
        )
        result = bound.solve_instance(instance)
        self.assertEqual(result["decision"], "NO_JOINT_CHILD_FEASIBLE_BINDING")

    def test_rolewise_mapping_is_a_bijection(self) -> None:
        instance = two_merge_instance(
            train={"x", "y", "ab", "xa", "xb", "ya", "yb"},
        )
        result = bound.solve_instance(instance)
        self.assertEqual(result["decision"], "JOINT_CHILD_NECESSARY_BOUND_SAT")
        mapping = result["witness"]["mapping"]
        self.assertEqual({row["card_id"] for row in mapping}, {"L01", "L02"})
        self.assertEqual(mapping[0]["card_id"], "L01")

    def test_canonical_paid_card_rank_sequence_is_lexicographic(self) -> None:
        instance = two_merge_instance(
            train={"x", "y", "ab", "ba", "xa", "xb", "ya", "yb"},
        )
        result = bound.solve_instance(instance)
        sequence = result["witness"]["paid_assignment_tuple"]
        self.assertEqual(sequence, [[1, "P01"], [2, "P02"]])

    def test_paid_pairs_are_interleaved_not_rank_set_first(self) -> None:
        cards = (
            card("P01", "short_card", "x"),
            card("P02", "short_card", "y"),
        )
        merges = (
            bound.Merge(1, "A", "B", "m1"),
            bound.Merge(2, "A", "B", "m2"),
            bound.Merge(3, "A", "B", "m3"),
        )
        assignment = {
            (merge.rank, paid.card_id): z3.Bool(
                f"counterexample__{merge.rank}__{paid.card_id}"
            )
            for merge in merges
            for paid in cards
        }

        def exact_world(selected: set[tuple[int, str]]) -> z3.BoolRef:
            return z3.And(
                *[
                    variable if pair in selected else z3.Not(variable)
                    for pair, variable in assignment.items()
                ]
            )

        rank_first_world = {(1, "P02"), (2, "P01")}
        pairwise_first_world = {(1, "P01"), (3, "P02")}
        runner = bound.ExactRunner(
            [
                z3.Or(
                    exact_world(rank_first_world),
                    exact_world(pairwise_first_world),
                )
            ],
            30,
        )
        chosen = bound.canonicalize_paid_assignment_pairs(
            runner, merges, cards, assignment, []
        )
        self.assertEqual(chosen, ((1, "P01"), (3, "P02")))

    def test_non_topological_merge_is_rejected(self) -> None:
        instance = two_merge_instance(
            train={"ab", "xa"},
            names=("A", "aba"),
        )
        with self.assertRaisesRegex(bound.BoundError, "non-topological"):
            bound.solve_instance(instance)


if __name__ == "__main__":
    unittest.main()
