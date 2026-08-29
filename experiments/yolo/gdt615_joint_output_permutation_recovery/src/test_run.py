#!/usr/bin/env python3
"""Focused tests for the public GDT615 Stage-0 integration runner."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

if __package__:
    from . import run
else:
    import run


def fixture_context() -> run.RegisteredContext:
    return run.RegisteredContext(
        primitive_order=(("a", "literal"), ("b", "literal")),
        cards={
            "L01": {
                "card_id": "L01",
                "output": "x",
                "role": "literal",
                "length": 1,
            },
            "L02": {
                "card_id": "L02",
                "output": "y",
                "role": "literal",
                "length": 1,
            },
        },
        merge_names=("ab", "aba", "abb"),
        input_hashes={
            "REGISTERED_SEARCH.json": "a" * 64,
            "REGISTERED_TRAIN_SUBSTRINGS.txt": "b" * 64,
            "merge_tree.tsv": "c" * 64,
        },
    )


def fixture_primary() -> dict[str, object]:
    context = fixture_context()
    return {
        "schema": run.PRIMARY_SCHEMA,
        "decision": "STAGE0_MAPPING_BOUND_PASS",
        "input_hashes": dict(context.input_hashes),
        "mapping": [
            {
                "primitive_id": "a",
                "role": "literal",
                "card_id": "L02",
                "output": "y",
                "length": 1,
            },
            {
                "primitive_id": "b",
                "role": "literal",
                "card_id": "L01",
                "output": "x",
                "length": 1,
            },
        ],
        "objective": {
            "raw_train_supported_named_merges": 2,
            "exact_minimum_core_hit": 1,
            "lexicographic_card_id_sequence": ["L02", "L01"],
        },
        "raw_merges": [
            {"rank": 1, "merge": "ab", "train_substring_member": True},
            {"rank": 2, "merge": "aba", "train_substring_member": False},
            {"rank": 3, "merge": "abb", "train_substring_member": True},
        ],
        "canonical_minimum_cover": [{"rank": 2, "merge": "aba"}],
        "negative_control": {
            "expected_raw_supported_merges": 1,
            "expected_exact_minimum": 2,
            "replayed_raw_supported_merges": 1,
            "replayed_exact_minimum": 2,
            "canonical_cover_ranks": [1, 3],
        },
    }


def fixture_independent() -> dict[str, object]:
    context = fixture_context()
    return {
        "schema": run.INDEPENDENT_SCHEMA,
        "status": "GLOBAL_OPTIMUM_COMPLETE",
        "complete": True,
        "input_sha256": dict(context.input_hashes),
        "winner_direct_replay_matches": True,
        "mapping": [
            {
                "primitive_id": "a",
                "role": "literal",
                "card_id": "L02",
                "output": "y",
            },
            {
                "primitive_id": "b",
                "role": "literal",
                "card_id": "L01",
                "output": "x",
            },
        ],
        "objective": {
            "raw_supported_merge_count": 2,
            "minimum_inclusive_dag_cover": 1,
        },
        "supported_merge_ranks": [1, 3],
        "minimum_cover_ranks": [2],
        "negative_control": {
            "raw_supported_merge_count": 1,
            "minimum_inclusive_dag_cover": 2,
            "minimum_cover_ranks": [1, 3],
            "matches_registered_expectation": True,
        },
    }


class CanonicalComparisonTests(unittest.TestCase):
    def test_equivalent_solver_results_compare_equal(self) -> None:
        context = fixture_context()
        primary = run.canonical_primary(fixture_primary(), context)
        independent = run.canonical_independent(fixture_independent(), context)
        run.compare_canonical_results(primary, independent)
        self.assertEqual(primary, independent)

    def test_support_set_disagreement_is_a_hard_mismatch(self) -> None:
        context = fixture_context()
        primary = run.canonical_primary(fixture_primary(), context)
        independent = run.canonical_independent(fixture_independent(), context)
        independent["supported_merge_ranks"] = [1, 2]
        with self.assertRaises(run.IntegrationMismatch) as caught:
            run.compare_canonical_results(primary, independent)
        self.assertIn("supported_merge_ranks", caught.exception.fields)

    def test_mapping_card_output_must_match_registration(self) -> None:
        result = fixture_independent()
        mapping = result["mapping"]
        assert isinstance(mapping, list) and isinstance(mapping[0], dict)
        mapping[0]["output"] = "x"
        with self.assertRaisesRegex(run.IntegrationError, "output disagrees"):
            run.canonical_independent(result, fixture_context())

    def test_noncanonical_cover_order_is_rejected(self) -> None:
        result = fixture_independent()
        negative = result["negative_control"]
        assert isinstance(negative, dict)
        negative["minimum_cover_ranks"] = [3, 1]
        with self.assertRaisesRegex(run.IntegrationError, "strictly ascending"):
            run.canonical_independent(result, fixture_context())


class OutputRootTests(unittest.TestCase):
    def test_new_output_root_is_reserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            requested = Path(temporary) / "new-run"
            reserved = run.reserve_output_root(requested)
            self.assertEqual(reserved, requested.resolve())
            self.assertTrue(reserved.is_dir())

    def test_existing_output_root_is_never_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            requested = Path(temporary) / "existing"
            requested.mkdir()
            with self.assertRaisesRegex(run.IntegrationError, "overwrite"):
                run.reserve_output_root(requested)

    def test_sealed_data_token_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            requested = Path(temporary) / "f84r-output"
            with self.assertRaisesRegex(run.IntegrationError, "forbidden"):
                run.reserve_output_root(requested)
            self.assertFalse(requested.exists())


class CommandIsolationTests(unittest.TestCase):
    def test_primary_receives_only_fixed_scientific_inputs(self) -> None:
        command = run.primary_command(Path("gdt615-test-output"), 100, 2)
        self.assertEqual(command.count("--registered-search"), 1)
        self.assertEqual(command.count("--train-substrings"), 1)
        self.assertEqual(command.count("--merge-tree"), 1)
        self.assertNotIn("--input", command)

    def test_independent_receives_only_fixed_scientific_inputs(self) -> None:
        command = run.independent_command(Path("gdt615-test-output"), 100, 2)
        self.assertEqual(command.count("--registered-search"), 1)
        self.assertEqual(command.count("--substrings"), 1)
        self.assertEqual(command.count("--merge-tree"), 1)
        self.assertNotIn("--input", command)


if __name__ == "__main__":
    unittest.main()
