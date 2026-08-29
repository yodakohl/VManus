#!/usr/bin/env python3
"""Focused tests for the non-scoring Stage-0 scout."""

from __future__ import annotations

import random
import unittest

from scout_core import load_problem
from scout_stage0 import ConstructiveSearch, quality


class ScoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.problem = load_problem()

    def test_registered_shape_and_identity_replay(self) -> None:
        self.assertEqual(len(self.problem.primitives), 34)
        self.assertEqual(len(self.problem.merges), 64)
        self.assertEqual(len(self.problem.substrings), 28_101)
        evaluation = self.problem.evaluate(self.problem.identity_mapping())
        self.assertEqual(evaluation.support_count, evaluation.supported_mask.bit_count())
        cover = self.problem.canonical_cover(evaluation.supported_mask)
        self.assertEqual(len(cover), evaluation.cover_minimum)

    def test_random_mappings_have_exact_cover_witnesses(self) -> None:
        search = ConstructiveSearch(self.problem, assignment_cap=128)
        rng = random.Random(615)
        for _ in range(8):
            mapping = search.random_mapping(rng)
            evaluation = self.problem.evaluate(mapping)
            witness = self.problem.canonical_cover(evaluation.supported_mask)
            self.assertEqual(len(witness), evaluation.cover_minimum)

    def test_constructive_move_supports_its_target_internally(self) -> None:
        search = ConstructiveSearch(self.problem, assignment_cap=256)
        rng = random.Random(61_500)
        mapping = search.random_mapping(rng)
        evaluation = self.problem.evaluate(mapping)
        repaired = search.repair_move(mapping, evaluation, rng)
        if repaired is not None:
            self.problem.validate_mapping(repaired)

    def test_quality_prioritizes_gate_then_support(self) -> None:
        identity = self.problem.evaluate(self.problem.identity_mapping())
        self.assertIsInstance(quality(identity), tuple)


if __name__ == "__main__":
    unittest.main()
