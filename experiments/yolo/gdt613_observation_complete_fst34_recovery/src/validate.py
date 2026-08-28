#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import itertools
from collections import Counter
from pathlib import Path

import z3

from fst import Piece, parse_pieces
from structural_model import (
    RAW_MAX60_WITNESS_ROLES,
    RID,
    ROLE_ORDER,
    ROLE_COUNTS,
    build_solver,
    build_raw_leaf_solver,
    load_inputs,
    query_fingerprint,
    valid_complete_strings,
    valid_substrings,
)


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt613_observation_complete_fst34_recovery"
ART = EXP / "artifacts"
checks = []


def check(name: str, condition: bool) -> None:
    checks.append({"check": name, "status": "PASS" if condition else "FAIL"})
    if not condition:
        raise AssertionError(name)


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    check("z3_version", z3.get_version_string() == "4.15.3")
    rows, primitives, hashes = load_inputs(ROOT)
    check("source_hash_count", len(hashes) == 3)
    complete = valid_complete_strings(6)
    parser_mismatches = 0
    parser_cases = 0
    role_name = {
        "L": "literal_carrier",
        "Y": "syllabic_carrier",
        "P": "prefix_operator",
        "U": "suffix_operator",
        "C": "connector",
        "X": "context_abbreviation_mark",
        "W": "wholeform_logogram",
        "N": "null_layout",
    }
    for length in range(1, 7):
        for roles in itertools.product(ROLE_ORDER, repeat=length):
            pieces = tuple(
                Piece(role_name[role], "" if role == "N" else "a", 0, "audit")
                for role in roles
            )
            parser_mismatches += parse_pieces(pieces).legal != (roles in complete)
            parser_cases += 1
    check("parser_exhaustive_case_count", parser_cases == 299592)
    check("parser_exact_ebnf_parity", parser_mismatches == 0)
    result = json.loads((ART / "RESULTS.json").read_text(encoding="utf-8"))
    queries = read_tsv(ART / "structural_queries.tsv")
    bridge = read_tsv(ART / "grammar_scope_bridge.tsv")
    witness = json.loads((ART / "relaxed_control_witness.json").read_text(encoding="utf-8"))
    length_audit = json.loads((ART / "length_deck_feasibility.json").read_text(encoding="utf-8"))
    raw_bound = json.loads((ART / "raw_leaf_merge_bound.json").read_text(encoding="utf-8"))
    check("decision", result["decision"] == "MODEL_SCOPE_UNDERSPECIFIED_OR_INFEASIBLE")
    check("stopped_before_world", result["status"] == "STOPPED_BEFORE_TRUTH_WORLD_OR_TARGET")
    check("length_cards_required", length_audit["one_character_cards_required"] == 23)
    check("length_values_observed", length_audit["one_character_values_observed"] == 22)
    check(
        "length_values_eligible",
        length_audit["one_character_values_meeting_8_train_types_and_16_held_events"] == 21,
    )
    check(
        "length_minimum_repair",
        length_audit["minimum_length1_to_length2_moves_with_registered_exposure"] == 2,
    )
    check(
        "whole_envelope_maxima",
        [
            row["maximum_train_word_types"]
            for row in length_audit["whole_envelope_upper_bounds"]
        ]
        == [5, 4, 3, 3],
    )
    check(
        "whole_parameters_below_threshold",
        length_audit["whole_parameters_reaching_train_threshold"] == 0,
    )
    raw_solver, _raw_variables, raw_accepted = build_raw_leaf_solver(rows, primitives)
    raw_solver.add(z3.Sum([z3.If(value, 1, 0) for value in raw_accepted.values()]) >= 61)
    check("raw_leaf_at_least_61_unsat", raw_solver.check() == z3.unsat)
    fixed_solver, fixed_variables, fixed_accepted = build_raw_leaf_solver(rows, primitives)
    for primitive, role in RAW_MAX60_WITNESS_ROLES.items():
        fixed_solver.add(fixed_variables[primitive] == RID[role])
    check("raw_leaf_fixed_witness_sat", fixed_solver.check() == z3.sat)
    fixed_model = fixed_solver.model()
    fixed_bad = [
        name
        for name, expression in fixed_accepted.items()
        if not z3.is_true(fixed_model.eval(expression))
    ]
    check("raw_leaf_fixed_witness_60", fixed_bad == ["daN", "dal", "dar", "daI"])
    check("raw_leaf_artifact_parity", fixed_bad == raw_bound["fixed_witness_illegal_merges"])
    check("query_count", len(queries) == 3)
    check(
        "stored_query_statuses",
        [row["status"] for row in queries] == ["unsat", "unsat", "sat"],
    )

    replay_statuses = []
    for name, skip_child, forbid_family in (
        ("STRICT_REGISTERED_QOK_ONLY", False, False),
        ("STRICT_SENSITIVITY_ALL_QOK_FAMILY", False, True),
        ("CONTROL_DROP_CARD_CHILD_GATE", True, False),
    ):
        solver, _variables, _patterns = build_solver(
            rows,
            primitives,
            skip_card_child_gate=skip_child,
            forbid_all_qok_whole=forbid_family,
        )
        query_hash = query_fingerprint(
            rows,
            skip_card_child_gate=skip_child,
            forbid_all_qok_whole=forbid_family,
        )
        stored = next(row for row in queries if row["query"] == name)
        check(f"query_hash_{name}", query_hash == stored["query_sha256"])
        replay_statuses.append(str(solver.check()))
    check("replay_statuses", replay_statuses == ["unsat", "unsat", "sat"])

    check("relaxed_role_count", Counter(witness["roles"].values()) == Counter(ROLE_COUNTS))
    check("relaxed_card_count", len(witness["cards"]) == 8)
    check("relaxed_short_count", list(witness["cards"].values()).count("short") == 4)
    check("relaxed_whole_count", list(witness["cards"].values()).count("whole") == 4)
    check("qok_not_whole", witness["cards"].get("qok") != "whole")
    patterns = valid_substrings()
    illegal_selected = []
    for row in witness["merges"]:
        child = tuple(row["child_role_sequence"])
        accepted = child in patterns[len(child)]
        check(f"stored_child_flag_{row['unit']}", accepted == row["child_embeddable"])
        if row["card"] == "none":
            check(f"relaxed_noncard_embeddable_{row['unit']}", accepted)
        elif not accepted:
            illegal_selected.append(row["unit"])
    check("relaxed_isolates_child_gate", len(illegal_selected) > 0)
    check(
        "relaxed_illegal_list",
        illegal_selected == result["relaxed_control"]["cards_with_illegal_unoverridden_children"],
    )

    bridge_key = {(row["split"], row["model"]): row for row in bridge}
    exact_train = bridge_key[("train", "GDT609_EXACT_SINGLE_CORE")]
    run_train = bridge_key[("train", "DIAGNOSTIC_V2_ADJACENT_CORE_RUN")]
    exact_held = bridge_key[("held", "GDT609_EXACT_SINGLE_CORE")]
    run_held = bridge_key[("held", "DIAGNOSTIC_V2_ADJACENT_CORE_RUN")]
    check(
        "bridge_exact_train",
        (exact_train["legal_events"], exact_train["total_events"]) == ("1922", "14553"),
    )
    check(
        "bridge_run_train",
        (run_train["legal_events"], run_train["total_events"]) == ("14461", "14553"),
    )
    check(
        "bridge_exact_held",
        (exact_held["legal_events"], exact_held["total_events"]) == ("505", "3639"),
    )
    check(
        "bridge_run_held",
        (run_held["legal_events"], run_held["total_events"]) == ("3562", "3639"),
    )
    check("no_f84_input", "f84" not in json.dumps(result).lower())

    validation = {
        "schema": "gdt613-validation-v1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_failed": 0,
        "checks": checks,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"VALIDATION_PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
