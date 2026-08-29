#!/usr/bin/env python3
"""Validate the terminal GDT616 Stage-A dual-solver result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt616_joint_child_feasible_binding"
STAGE = EXP / "artifacts/stage_a"
OUTPUT = STAGE / "VALIDATION.json"
EXPECTED = {
    "PRIMARY_RESULT.json": "d87d925fff5c7e185a256dacf53619b72a8fe430e2db21ce6f6232f2e906faef",
    "INDEPENDENT_RESULT.json": "38b7e7741850791731946d9bc963f3ad44d5147eb267e0387d6c57b71f601361",
    "COMPARISON.json": "e098d63da66b49134e2277e5646639a20cc3b6a8c840b22394da284a1f14aa2c",
}
DIAGNOSTIC_NAME = "UNSAT_CORE_DIAGNOSTIC.json"
DIAGNOSTIC_SHA256 = (
    "2c81f2ba6aae266c04ef460d50969dc673de2f5456937a944522dcf75436ab38"
)
DIAGNOSTIC_SOURCE_SHA256 = (
    "f5af33c7ee5c8e6918dbfa707453d12ac9be14c87632b6237c79a54fdbbbb102"
)
RELAXATION_NAME = "RELAXATION_DIAGNOSTIC.json"
RELAXATION_SHA256 = (
    "b2f3ee9254e2e1fc0973b0d407f0cdb5c45ac2e58ca91718525db87c078fd59c"
)
RELAXATION_SOURCE_SHA256 = (
    "2662f87d01fbecf6e00a27105ae9e2d8283e9e3da2e39ca2f07ffd1c61829ec2"
)
PRIMARY_SOURCE_SHA256 = (
    "f99785892749ddafc999b8bb2145ee67cdfe5b7c75635012c271ee140c3dc381"
)
EXPECTED_CORE_RANKS = {
    2,
    3,
    4,
    6,
    9,
    10,
    11,
    14,
    23,
    38,
    43,
    45,
    51,
    52,
    60,
    61,
    62,
    63,
    64,
}
EXPECTED_CORE_CAPS = {
    ("short:1", "de"),
    ("short:2", "di"),
    ("short:3", "ent"),
}
EXPECTED_RELAXATION_RANKS = {14, 18, 45, 47, 49, 59}
EXPECTED_REPRESENTATIVE_BREAKS = {
    (14, "Ey", "hoa", "ere", "short:4"),
    (45, "Sol", "hire", "runt", "macro:2"),
    (47, "qokEdy", "tinhora", "con", "macro:1"),
    (49, "qokedy", "tinura", "erunt", "macro:3"),
}
DECISION = "NO_JOINT_CHILD_FEASIBLE_BINDING"
REGISTRATION_SHA256 = "281fe360e6e3eda19323f5e62a99fe4822546b136f7ca91b85fdf4552e565aae"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load(name: str) -> dict[str, Any]:
    value = json.loads((STAGE / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} is not a JSON object")
    return value


def canonical_write(path: Path, value: dict[str, Any]) -> None:
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    for name, expected in EXPECTED.items():
        check(f"hash_{name}", sha256(STAGE / name) == expected, expected)

    primary = load("PRIMARY_RESULT.json")
    independent = load("INDEPENDENT_RESULT.json")
    comparison = load("COMPARISON.json")

    check("primary_decision", primary.get("decision") == DECISION)
    check("independent_decision", independent.get("decision") == DECISION)
    check("comparison_decision", comparison.get("decision") == DECISION)
    check("comparison_status", comparison.get("status") == "PASS")
    agreement = comparison.get("agreement", {})
    check("decision_agreement", agreement.get("decision") is True)
    check("unsat_mapping_na", agreement.get("canonical_mapping") is None)
    check("unsat_paid_na", agreement.get("canonical_paid_assignment") is None)

    counts = primary.get("counts", {})
    check("primitive_count", counts.get("primitives") == 34)
    check("merge_count", counts.get("merges") == 64)
    check("paid_count", counts.get("paid_cards") == 8)
    check("train_count", counts.get("train_substrings") == 28101)
    check("primary_one_exact_query", primary.get("query_count") == 1)
    queries = primary.get("queries", [])
    check("primary_query_unsat", len(queries) == 1 and queries[0].get("status") == "unsat")

    check("independent_strict_unsat", independent.get("strict_joint_child_span_status") == "UNSAT")
    check("independent_no_witness", independent.get("witness") is None)
    boundary = independent.get("exact_boundary_queries", [])
    check(
        "independent_zero_violation_unsat",
        len(boundary) == 1
        and boundary[0].get("paid_child_span_violations_equal") == 0
        and boundary[0].get("status") == "UNSAT",
    )
    check("diagnostic_not_in_decision", independent.get("diagnostic_relaxation_status") == "NOT_RUN_AFTER_TERMINAL_STRICT_UNSAT")

    result_rows = comparison.get("results", [])
    result_hashes = {row.get("path"): row.get("sha256") for row in result_rows}
    check("comparison_primary_hash", result_hashes.get("PRIMARY_RESULT.json") == EXPECTED["PRIMARY_RESULT.json"])
    check("comparison_independent_hash", result_hashes.get("INDEPENDENT_RESULT.json") == EXPECTED["INDEPENDENT_RESULT.json"])

    check(
        "registration_hash_primary",
        primary.get("input_sha256", {}).get("GDT616_REGISTERED_SEARCH.json") == REGISTRATION_SHA256,
    )
    check(
        "registration_hash_independent",
        independent.get("input_sha256", {}).get("gdt616_registration") == REGISTRATION_SHA256,
    )
    check(
        "primary_source_hash",
        primary.get("source_sha256") == sha256(EXP / "src/primary_bound.py"),
    )
    check(
        "registered_primary_source_hash",
        primary.get("source_sha256") == PRIMARY_SOURCE_SHA256,
    )
    check(
        "registered_independent_source_hash",
        sha256(EXP / "src/independent_bound.py") == "014d2363fd38be7979d1286afbb639cb294b0001a3fa34b05109730439804f15",
    )

    scope = primary.get("scope", {})
    included = set(scope.get("included", []))
    check("scope_same_role_bijection", "complete same-role primitive/output bijection" in included)
    check("scope_eight_paid", any("exactly eight distinct paid" in row for row in included))
    check("scope_all_children", "every one of 64 child compositions in TRAIN_SUBSTRINGS" in included)
    check("scope_all_effective", "every one of 64 effective merge outputs nonempty and in TRAIN_SUBSTRINGS" in included)
    check("scope_paid_diff", "paid output differs from its child composition" in included)
    check("scope_semantic_none", scope.get("semantic_claim") == "none")

    for label, payload in (
        ("comparison", comparison),
        ("independent", independent.get("access", {})),
    ):
        check(f"{label}_held_closed", payload.get("held_or_lm_confirm_opened") is False)
        check(f"{label}_f84_closed", payload.get("f84_or_f84r_opened") is False)
    check("comparison_target_closed", comparison.get("voynich_target_opened") is False)
    check(
        "independent_target_closed",
        independent.get("access", {}).get("voynich_target_or_meaning_opened") is False,
    )

    diagnostic_path = STAGE / DIAGNOSTIC_NAME
    diagnostic_source_path = EXP / "src/diagnose_unsat_core.py"
    check(
        "hash_UNSAT_CORE_DIAGNOSTIC.json",
        sha256(diagnostic_path) == DIAGNOSTIC_SHA256,
        DIAGNOSTIC_SHA256,
    )
    check(
        "hash_diagnose_unsat_core.py",
        sha256(diagnostic_source_path) == DIAGNOSTIC_SOURCE_SHA256,
        DIAGNOSTIC_SOURCE_SHA256,
    )
    diagnostic = load(DIAGNOSTIC_NAME)
    check(
        "diagnostic_schema",
        diagnostic.get("schema") == "gdt616-stage-a-unsat-core-diagnostic-v1",
    )
    check("diagnostic_experiment_id", diagnostic.get("experiment_id") == "GDT616")
    check("diagnostic_decision", diagnostic.get("decision") == DECISION)
    check(
        "diagnostic_kind",
        diagnostic.get("diagnostic_kind")
        == "SUBSET_MINIMAL_GROUP_CORE_OF_EXACTLY_TO_AT_MOST_RELAXATION",
    )

    diagnostic_sources = diagnostic.get("source_sha256", {})
    check(
        "diagnostic_source_self_hash",
        diagnostic_sources.get("diagnose_unsat_core.py")
        == DIAGNOSTIC_SOURCE_SHA256,
    )
    check(
        "diagnostic_primary_source_hash",
        diagnostic_sources.get("primary_bound.py") == PRIMARY_SOURCE_SHA256,
    )
    frozen = diagnostic.get("frozen_stage_a", {})
    check("diagnostic_frozen_decision", frozen.get("decision") == DECISION)
    check(
        "diagnostic_frozen_artifact_hashes",
        frozen.get("files_sha256") == EXPECTED,
    )

    replay = diagnostic.get("replay", {})
    check(
        "diagnostic_strict_unsat",
        replay.get("strict_registered_stage_a", {}).get("status") == "unsat",
    )
    check(
        "diagnostic_full_at_most_relaxation_unsat",
        replay.get("full_exactly_to_at_most_relaxation", {}).get("status")
        == "unsat",
    )
    check(
        "diagnostic_no_cap_relaxation_sat",
        replay.get("exact_use_removed_without_replacement_caps", {}).get("status")
        == "sat",
    )
    implication_checks = replay.get("exactly_once_implies_at_most_once_checks", [])
    check("diagnostic_implication_count", len(implication_checks) == 8)
    check(
        "diagnostic_implications_unsat",
        len(implication_checks) == 8
        and all(row.get("status") == "unsat" for row in implication_checks),
    )

    core = diagnostic.get("core", {})
    check("diagnostic_core_unsat", core.get("status") == "unsat")
    check("diagnostic_core_group_count", core.get("group_count") == 23)
    check("diagnostic_core_role_count", core.get("role_group_count") == 1)
    check("diagnostic_core_rank_count", core.get("rank_group_count") == 19)
    check("diagnostic_core_cap_count", core.get("card_cap_group_count") == 3)
    core_groups = core.get("groups", [])
    group_names = [row.get("group") for row in core_groups]
    check(
        "diagnostic_core_groups_unique",
        len(core_groups) == 23 and len(set(group_names)) == 23,
    )
    role_rows = [row for row in core_groups if row.get("kind") == "primitive_role_binding"]
    rank_rows = [row for row in core_groups if row.get("kind") == "merge_rank"]
    cap_rows = [row for row in core_groups if row.get("kind") == "relaxed_paid_card_cap"]
    check(
        "diagnostic_core_literal_role",
        len(role_rows) == 1 and role_rows[0].get("role") == "literal_carrier",
    )
    check(
        "diagnostic_core_exact_ranks",
        {row.get("rank") for row in rank_rows} == EXPECTED_CORE_RANKS,
    )
    check(
        "diagnostic_core_exact_caps",
        {(row.get("card_id"), row.get("output")) for row in cap_rows}
        == EXPECTED_CORE_CAPS,
    )

    minimality = diagnostic.get("minimality", {})
    drop_rows = minimality.get("drop_one_checks", [])
    check("diagnostic_drop_one_count", len(drop_rows) == 23)
    check(
        "diagnostic_drop_one_all_sat",
        len(drop_rows) == 23 and all(row.get("status") == "sat" for row in drop_rows),
    )
    check(
        "diagnostic_drop_one_exact_groups",
        {row.get("dropped_group") for row in drop_rows} == set(group_names),
    )

    diagnostic_access = diagnostic.get("access_boundary", {})
    check("diagnostic_train_only", diagnostic_access.get("registered_train_only") is True)
    check(
        "diagnostic_restricted_inputs_closed",
        all(
            diagnostic_access.get(field) is False
            for field in (
                "held_opened",
                "lm_confirm_opened",
                "voynich_target_opened",
                "f84_opened",
                "f84r_opened",
            )
        ),
    )

    relaxation_path = STAGE / RELAXATION_NAME
    relaxation_source_path = EXP / "src/diagnose_relaxation.py"
    check(
        "hash_RELAXATION_DIAGNOSTIC.json",
        sha256(relaxation_path) == RELAXATION_SHA256,
        RELAXATION_SHA256,
    )
    check(
        "hash_diagnose_relaxation.py",
        sha256(relaxation_source_path) == RELAXATION_SOURCE_SHA256,
        RELAXATION_SOURCE_SHA256,
    )
    relaxation = load(RELAXATION_NAME)
    check(
        "relaxation_schema",
        relaxation.get("schema") == "gdt616-stage-a-relaxation-diagnostic-v1",
    )
    check("relaxation_decision_preserved", relaxation.get("decision_preserved") == DECISION)
    check(
        "relaxation_result",
        relaxation.get("diagnostic_result")
        == "SAT_AFTER_MINIMUM_CHILD_TRAIN_GATE_RELAXATION",
    )
    check(
        "relaxation_source_self_hash",
        relaxation.get("source_sha256") == RELAXATION_SOURCE_SHA256,
    )
    minimum = relaxation.get("minimum_relaxation", {})
    check("relaxation_minimum_four", minimum.get("total_train_gate_violations") == 4)
    check("relaxation_child_minimum_four", minimum.get("child_train_gate_violations") == 4)
    check("relaxation_effective_gate_intact", minimum.get("effective_train_gate_violations") == 0)
    check(
        "relaxation_other_constraints_intact",
        minimum.get("all_other_registered_stage_a_constraints_unchanged") is True,
    )
    check("relaxation_paid_budget_intact", minimum.get("paid_budget_changed") is False)
    check("relaxation_all_eight_cards", minimum.get("exact_registered_paid_cards_used") == 8)

    relaxation_boundary = relaxation.get("boundary_queries", [])
    check(
        "relaxation_exact_boundary",
        [
            (row.get("paid_child_train_gate_violations_equal"), row.get("status"))
            for row in relaxation_boundary
        ]
        == [(0, "UNSAT"), (1, "UNSAT"), (2, "UNSAT"), (3, "UNSAT"), (4, "SAT")],
    )
    rank_sweeps = relaxation.get("rank_sweeps", [])
    check("relaxation_four_rank_sweeps", len(rank_sweeps) == 4)
    check(
        "relaxation_sweeps_complete",
        len(rank_sweeps) == 4
        and all(
            len(sweep.get("rows", [])) == 64
            and {row.get("rank") for row in sweep.get("rows", [])} == set(range(1, 65))
            for sweep in rank_sweeps
        ),
    )
    check(
        "relaxation_k1_to_k3_all_unsat",
        len(rank_sweeps) == 4
        and all(
            all(row.get("status") == "UNSAT" for row in sweep.get("rows", []))
            for sweep in rank_sweeps[:3]
        ),
    )
    minimum_rows = relaxation.get("rank_feasibility", [])
    minimum_sat_ranks = {
        row.get("rank") for row in minimum_rows if row.get("status") == "SAT"
    }
    check("relaxation_minimum_rows_complete", len(minimum_rows) == 64)
    check("relaxation_exact_feasible_ranks", minimum_sat_ranks == EXPECTED_RELAXATION_RANKS)
    check(
        "relaxation_boolean_status_agreement",
        len(minimum_rows) == 64
        and all(
            row.get("can_participate_in_a_minimum_relaxation")
            is (row.get("status") == "SAT")
            for row in minimum_rows
        ),
    )
    relaxation_summary = relaxation.get("minimum_relaxation_rank_summary", {})
    check("relaxation_feasible_rank_count", relaxation_summary.get("feasible_rank_count") == 6)
    check(
        "relaxation_summary_exact_ranks",
        set(relaxation_summary.get("feasible_ranks", [])) == EXPECTED_RELAXATION_RANKS,
    )
    check(
        "relaxation_representative_ranks",
        relaxation_summary.get("representative_violation_ranks") == [14, 45, 47, 49],
    )
    representative_breaks = relaxation.get("representative_breaks", [])
    observed_breaks = {
        (
            row.get("rank"),
            row.get("merge"),
            row.get("child_composition"),
            row.get("effective_output"),
            row.get("paid_card_id"),
        )
        for row in representative_breaks
    }
    check("relaxation_exact_representative_breaks", observed_breaks == EXPECTED_REPRESENTATIVE_BREAKS)
    check(
        "relaxation_break_modes",
        len(representative_breaks) == 4
        and all(
            row.get("mode") == "PAID"
            and row.get("child_composition_in_train") is False
            for row in representative_breaks
        ),
    )
    witness = relaxation.get("representative_witness", {})
    check(
        "relaxation_witness_violation_ranks",
        witness.get("paid_child_span_violation_ranks") == [14, 45, 47, 49],
    )
    check("relaxation_witness_64_merges", len(witness.get("merge_replay", [])) == 64)
    check("relaxation_witness_eight_paid", len(witness.get("actual_paid_locations", [])) == 8)
    replay_checks = witness.get("replay_checks", {})
    check("relaxation_witness_effective_train", replay_checks.get("all_effective_outputs_in_train") is True)
    check("relaxation_witness_default_train", replay_checks.get("all_default_child_compositions_in_train") is True)
    check("relaxation_witness_exact_paid", replay_checks.get("every_paid_card_used_once") is True)
    check("relaxation_witness_strict_gate_broken", replay_checks.get("strict_paid_child_gate") is False)
    relaxation_terminal = relaxation.get("terminal_artifact_sha256", {})
    check(
        "relaxation_terminal_hashes",
        relaxation_terminal
        == {
            "primary_result": EXPECTED["PRIMARY_RESULT.json"],
            "independent_result": EXPECTED["INDEPENDENT_RESULT.json"],
            "comparison": EXPECTED["COMPARISON.json"],
            "independent_bound_source": "014d2363fd38be7979d1286afbb639cb294b0001a3fa34b05109730439804f15",
        },
    )
    relaxation_access = relaxation.get("access", {})
    check(
        "relaxation_restricted_inputs_closed",
        all(
            relaxation_access.get(field) is False
            for field in (
                "held_or_lm_confirm_opened",
                "voynich_target_or_meaning_opened",
                "f84_or_f84r_opened",
            )
        ),
    )

    result = {
        "schema": "gdt616-terminal-stage-a-validation-v3",
        "status": "PASS",
        "decision": DECISION,
        "checks_total": len(checks),
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks": checks,
        "terminal_artifact_sha256": dict(sorted(EXPECTED.items())),
        "diagnostic_artifact_sha256": DIAGNOSTIC_SHA256,
        "diagnostic_source_sha256": DIAGNOSTIC_SOURCE_SHA256,
        "relaxation_artifact_sha256": RELAXATION_SHA256,
        "relaxation_source_sha256": RELAXATION_SOURCE_SHA256,
        "held_or_lm_confirm_opened": False,
        "voynich_target_opened": False,
        "f84_or_f84r_opened": False,
    }
    canonical_write(OUTPUT, result)
    print(f"GDT616_TERMINAL_VALIDATION_PASS {result['checks_passed']}/{result['checks_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
