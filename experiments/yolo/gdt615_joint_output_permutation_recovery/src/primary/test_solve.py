#!/usr/bin/env python3
from __future__ import annotations

import itertools
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import z3

if __package__:
    from .solve import (
        ByteTrie,
        Card,
        Merge,
        Primitive,
        RegisteredInputs,
        build_boolean_model,
        exact_minimum_cover,
        load_registered_inputs,
        negative_control_mapping,
        render_merges,
    )
else:
    from solve import (
        ByteTrie,
        Card,
        Merge,
        Primitive,
        RegisteredInputs,
        build_boolean_model,
        exact_minimum_cover,
        load_registered_inputs,
        negative_control_mapping,
        render_merges,
    )


HERE = Path(__file__).resolve()
ROOT = next(parent for parent in HERE.parents if (parent / ".git").exists())
EXPERIMENT = ROOT / "experiments/yolo/gdt615_joint_output_permutation_recovery"
SEARCH = EXPERIMENT / "artifacts/REGISTERED_SEARCH.json"
SUBSTRINGS = EXPERIMENT / "artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt"
MERGES = (
    ROOT
    / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv"
)


def toy_inputs() -> RegisteredInputs:
    primitives = (
        Primitive("A", "letter"),
        Primitive("B", "letter"),
        Primitive("C", "null"),
    )
    cards_by_role = {
        "letter": (
            Card("L01", "letter", "a", 1, ()),
            Card("L02", "letter", "b", 1, ()),
        ),
        "null": (Card("N01", "null", "", 0, ()),),
    }
    merges = (
        Merge(1, "A", "C", "u1", ("A", "C"), 2, 1, (1,)),
        Merge(2, "C", "B", "u2", ("C", "B"), 2, 1, (2,)),
        Merge(
            3,
            "u1",
            "u2",
            "u3",
            ("A", "C", "C", "B"),
            4,
            2,
            (1, 2, 3),
        ),
    )
    return RegisteredInputs(
        search_path=Path("toy-search.json"),
        substring_path=Path("toy-substrings.txt"),
        merge_tree_path=Path("toy-merges.tsv"),
        search_sha256="",
        substring_sha256="",
        merge_tree_sha256="",
        search={},
        primitives=primitives,
        cards_by_role=cards_by_role,
        merges=merges,
        substrings=frozenset(("a", "ab")),
        substring_order=("a", "ab"),
    )


def toy_cover_inputs() -> RegisteredInputs:
    base = toy_inputs()
    merges = (
        Merge(1, "A", "C", "u1", ("A", "C"), 2, 1, (1,)),
        Merge(2, "C", "B", "u2", ("C", "B"), 2, 1, (2,)),
        Merge(3, "A", "B", "u3", ("A", "B"), 2, 1, (3,)),
        Merge(
            4,
            "u1",
            "u2",
            "u4",
            ("A", "C", "C", "B"),
            4,
            2,
            (1, 2, 4),
        ),
        Merge(
            5,
            "u2",
            "u3",
            "u5",
            ("C", "B", "A", "B"),
            4,
            2,
            (2, 3, 5),
        ),
        Merge(
            6,
            "u1",
            "u3",
            "u6",
            ("A", "C", "A", "B"),
            4,
            2,
            (1, 3, 6),
        ),
    )
    return replace(base, merges=merges)


class Stage0PrimaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_registered_inputs(SEARCH, SUBSTRINGS, MERGES)

    def test_registered_counts_and_tree(self):
        self.assertEqual(len(self.inputs.primitives), 34)
        self.assertEqual(len(self.inputs.merges), 64)
        self.assertEqual(len(self.inputs.substrings), 28101)
        self.assertEqual([merge.rank for merge in self.inputs.merges], list(range(1, 65)))
        for merge in self.inputs.merges:
            self.assertIn(merge.rank, merge.merge_descendant_ranks)
            self.assertLessEqual(len(merge.merge_descendant_ranks), 5)

    def test_trie_exactness(self):
        trie = ByteTrie(("a", "ab", "b"))
        self.assertTrue(trie.terminal[trie.transition(0, "a")])
        self.assertTrue(trie.terminal[trie.transition(0, "ab")])
        self.assertEqual(trie.transition(0, "ac"), -1)

    def test_empty_output_preserves_trie_state(self):
        trie = ByteTrie(("a", "ab", "b"))
        state_a = trie.transition(0, "a")
        state_ab = trie.transition(state_a, "b")

        self.assertEqual(trie.transition(0, ""), 0)
        self.assertEqual(trie.transition(state_a, ""), state_a)
        self.assertEqual(trie.transition(trie.transition(state_a, ""), "b"), state_ab)
        self.assertTrue(trie.terminal[state_a])
        self.assertTrue(trie.terminal[state_ab])

    def test_mdd_membership_matches_exhaustive_direct_rendering(self):
        inputs = toy_inputs()
        boolean_model = build_boolean_model(inputs)
        letter_cards = inputs.cards_by_role["letter"]
        null_card = inputs.cards_by_role["null"][0]

        for permutation in itertools.permutations(letter_cards):
            mapping = {
                "A": permutation[0],
                "B": permutation[1],
                "C": null_card,
            }
            direct = render_merges(inputs, mapping)
            solver = z3.SolverFor("QF_FD")
            solver.add(*boolean_model.assertions)
            for primitive_id, card in mapping.items():
                solver.add(boolean_model.assignment[(primitive_id, card.card_id)])

            with self.subTest(
                key=tuple(mapping[primitive].card_id for primitive in ("A", "B", "C"))
            ):
                self.assertEqual(solver.check(), z3.sat)
                model = solver.model()
                encoded = tuple(
                    z3.is_true(model.eval(variable, model_completion=True))
                    for variable in boolean_model.support
                )
                self.assertEqual(encoded, tuple(member for _, member in direct))

    def test_role_bijection_accepts_only_complete_permutations(self):
        inputs = toy_inputs()
        boolean_model = build_boolean_model(inputs)
        letter_cards = inputs.cards_by_role["letter"]
        null_card = inputs.cards_by_role["null"][0]

        self.assertNotIn(("A", null_card.card_id), boolean_model.assignment)
        self.assertNotIn(("C", letter_cards[0].card_id), boolean_model.assignment)
        for card_a, card_b in itertools.product(letter_cards, repeat=2):
            solver = z3.SolverFor("QF_FD")
            solver.add(*boolean_model.assertions)
            solver.add(boolean_model.assignment[("A", card_a.card_id)])
            solver.add(boolean_model.assignment[("B", card_b.card_id)])
            solver.add(boolean_model.assignment[("C", null_card.card_id)])
            expected = z3.sat if card_a.card_id != card_b.card_id else z3.unsat
            with self.subTest(card_a=card_a.card_id, card_b=card_b.card_id):
                self.assertEqual(solver.check(), expected)

    def test_exact_cover_is_minimum_and_lexicographically_first_on_toy_dag(self):
        inputs = toy_cover_inputs()
        supported = (True, True, True, False, False, False)
        unsupported = [
            index for index, member in enumerate(supported) if not member
        ]

        def is_cover(candidate: tuple[int, ...]) -> bool:
            selected_ranks = {rank + 1 for rank in candidate}
            return all(
                selected_ranks
                & set(inputs.merges[index].merge_descendant_ranks)
                for index in unsupported
            )

        exhaustive_minima: list[tuple[int, ...]] = []
        for size in range(len(inputs.merges) + 1):
            exhaustive_minima = [
                candidate
                for candidate in itertools.combinations(range(len(inputs.merges)), size)
                if is_cover(candidate)
            ]
            if exhaustive_minima:
                break

        self.assertGreater(len(exhaustive_minima), 1)
        self.assertEqual(min(exhaustive_minima), (0, 1))
        self.assertEqual(
            exact_minimum_cover(inputs, supported), min(exhaustive_minima)
        )

    def test_negative_control_minimum(self):
        mapping = negative_control_mapping(self.inputs)
        rendered = render_merges(self.inputs, mapping)
        cover = exact_minimum_cover(self.inputs, [member for _, member in rendered])
        self.assertEqual(sum(member for _, member in rendered), 25)
        self.assertEqual(len(cover), 15)
        self.assertEqual(
            [self.inputs.merges[rank].merged for rank in cover],
            [
                "dy",
                "ol",
                "aN",
                "Ce",
                "ot",
                "ar",
                "al",
                "Se",
                "aI",
                "Ey",
                "ai",
                "ey",
                "yk",
                "yt",
                "Sy",
            ],
        )


if __name__ == "__main__":
    unittest.main()
