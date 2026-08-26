#!/usr/bin/env python3
"""Independently validate the GDT501 fifty-cell partial-support atlas."""

from __future__ import annotations

import csv
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt501_old_value_frontier_partial_support_atlas"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G421 = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license/artifacts"
G499 = ROOT / "experiments/yolo/gdt499_nine_action_composition_priority_atlas/artifacts"
G500 = ROOT / "experiments/yolo/gdt500_repeated_action_fluency_matrix/artifacts"

CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
PAIR_IN = G421 / "gdt421_81_ordered_pair_profiles.tsv"
FRONTIER_IN = G499 / "gdt499_50_old_values_only_compositions.tsv"
CURRENT_IN = G500 / "gdt500_495_current_fluent_cells.tsv"
RANKED_OUT = ART / "gdt501_50_ranked_frontier_cells.tsv"
CANDIDATE_OUT = ART / "gdt501_partial_subrecipe_candidates.tsv"
WITNESS_OUT = ART / "gdt501_exact_partial_recipe_witnesses.tsv"
PAIR_OUT = ART / "gdt501_ordered_action_pair_support.tsv"
TIER_OUT = ART / "gdt501_support_tier_coverage.tsv"
FRAME_OUT = ART / "gdt501_5_frame_frontier_coverage.tsv"
ACTION_OUT = ART / "gdt501_7_action_frontier_coverage.tsv"
READABLE_OUT = ART / "GDT501_FIFTY_CELL_PARTIAL_SUPPORT_ATLAS.md"
RESULT_OUT = ART / "gdt501_result.json"
VALIDATION_OUT = ART / "gdt501_validation.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
TIER_ORDER = {
    "A_SAME_REGISTER_NEAR_DELETION": 0,
    "B_SAME_REGISTER_ACTION_PARTIAL": 1,
    "C_STRUCTURAL_PARTIAL_OR_ACTION_PAIR": 2,
    "D_ATOMIC_VALUES_ONLY": 3,
}
STATUS = "FIFTY_CELL_FRONTIER_STRATIFIED_BY_OLD_PARTIAL_FRAMES_AND_ACTION_PAIRS"
GUARD = "PARTIAL_SUPPORT_RANKING_ONLY__CURRENT_PHRASES_AND_COMPOSED_LABELS_RETAINED"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def page_key(page: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if match:
        return int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), page
    return 10**9, 0, 0, page


def pages_of(rows: list[dict[str, str]]) -> list[str]:
    return sorted({row["physical_page"] for row in rows}, key=page_key)


def partials(tokens: list[str]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for length in range(2, len(tokens)):
        for positions in itertools.combinations(range(len(tokens)), length):
            recipe = "+".join(tokens[position] for position in positions)
            removed = [position for position in range(len(tokens)) if position not in positions]
            item = grouped.setdefault(recipe, {
                "partial_recipe": recipe,
                "partial_tokens": [tokens[position] for position in positions],
                "partial_component_count": length,
                "removal_position_sets": [],
                "removed_token_sets": [],
                "near_deletion": length == len(tokens) - 1,
                "contiguous": False,
            })
            item["removal_position_sets"].append(",".join(str(position + 1) for position in removed))
            item["removed_token_sets"].append("+".join(tokens[position] for position in removed))
            if positions == tuple(range(positions[0], positions[0] + length)):
                item["contiguous"] = True
    return list(grouped.values())


def main() -> int:
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _pair_fields, pair_profiles = read_tsv(PAIR_IN)
    _frontier_fields, frontier = read_tsv(FRONTIER_IN)
    _current_fields, current = read_tsv(CURRENT_IN)
    ranked_fields, ranked = read_tsv(RANKED_OUT)
    candidate_fields, candidate_rows = read_tsv(CANDIDATE_OUT)
    witness_fields, witness_rows = read_tsv(WITNESS_OUT)
    pair_out_fields, pair_rows = read_tsv(PAIR_OUT)
    _tier_fields, tier_rows = read_tsv(TIER_OUT)
    _frame_fields, frame_rows = read_tsv(FRAME_OUT)
    _action_fields, action_rows = read_tsv(ACTION_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    counts = (
        len(clauses), len(pair_profiles), len(frontier), len(current), len(ranked),
        len(candidate_rows), len(witness_rows), len(pair_rows), len(tier_rows),
        len(frame_rows), len(action_rows),
    )
    check("all_table_counts_exact", counts == (4576, 81, 50, 495, 50, 167, 285, 30, 4, 5, 7), f"actual={counts}")
    check("ranked_schema_complete", {"frontier_priority_rank", "same_register_near_deletion_count", "ordered_pair_event_count"} <= set(ranked_fields), f"fields={len(ranked_fields)}")
    check("candidate_schema_complete", {"partial_candidate_id", "partial_recipe", "same_register_event_count"} <= set(candidate_fields), f"fields={len(candidate_fields)}")
    check("witness_schema_complete", {"partial_witness_id", "partial_candidate_id", "observed_event_ids"} <= set(witness_fields), f"fields={len(witness_fields)}")
    check("pair_schema_complete", {"pair_support_id", "ordered_action_pair", "pair_status"} <= set(pair_out_fields), f"fields={len(pair_out_fields)}")
    check("candidate_ids_exact", [row["partial_candidate_id"] for row in candidate_rows] == [f"G501-C{i:04d}" for i in range(1, 168)], "C0001..C0167")
    check("witness_ids_exact", [row["partial_witness_id"] for row in witness_rows] == [f"G501-W{i:04d}" for i in range(1, 286)], "W0001..W0285")
    check("pair_ids_exact", [row["pair_support_id"] for row in pair_rows] == [f"G501-P{i:03d}" for i in range(1, 31)], "P001..P030")

    current_by_source = {row["source_matrix_cell_id"]: row for row in current}
    pair_by_key = {row["ordered_pair"]: row for row in pair_profiles}
    clauses_by_recipe_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    clauses_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_recipe_register[(row["component_recipe"], row["register"])].append(row)
        clauses_by_recipe[row["component_recipe"]].append(row)

    expected_candidates: list[dict[str, str]] = []
    expected_witnesses: list[dict[str, str]] = []
    expected_pairs: list[dict[str, str]] = []
    for target in frontier:
        tokens = target["action_recipe"].split("+")
        for candidate in partials(tokens):
            recipe = str(candidate["partial_recipe"])
            contains_action = target["action_root"] in list(candidate["partial_tokens"])
            same = clauses_by_recipe_register[(recipe, target["register"])]
            cross = [row for row in clauses_by_recipe[recipe] if row["register"] != target["register"]]
            same_pages = pages_of(same)
            cross_pages = pages_of(cross)
            cross_registers = sorted({row["register"] for row in cross})
            candidate_id = f"G501-C{len(expected_candidates) + 1:04d}"
            expected_candidates.append({
                "partial_candidate_id": candidate_id,
                "target_matrix_cell_id": target["source_matrix_cell_id"],
                "target_frame": target["frozen_frame"],
                "target_action_root": target["action_root"],
                "target_action_recipe": target["action_recipe"],
                "target_register": target["register"],
                "partial_recipe": recipe,
                "partial_component_count": str(candidate["partial_component_count"]),
                "removed_component_count": str(len(tokens) - int(candidate["partial_component_count"])),
                "removal_position_sets": "|".join(candidate["removal_position_sets"]),
                "removed_token_sets": "|".join(candidate["removed_token_sets"]),
                "near_single_deletion": "YES" if candidate["near_deletion"] else "NO",
                "contiguous_in_target": "YES" if candidate["contiguous"] else "NO",
                "contains_target_action_root": "YES" if contains_action else "NO",
                "same_register_exact_cell_count": "1" if same else "0",
                "same_register_event_count": str(len(same)),
                "same_register_clause_form_count": str(len({row["imperative_clause_de"] for row in same})),
                "same_register_page_count": str(len(same_pages)),
                "same_register_pages": "|".join(same_pages) or "NONE",
                "cross_register_exact_cell_count": str(len(cross_registers)),
                "cross_registers": "|".join(cross_registers) or "NONE",
                "cross_register_event_count": str(len(cross)),
                "cross_register_page_count": str(len(cross_pages)),
                "cross_register_pages": "|".join(cross_pages) or "NONE",
                "guard": GUARD,
            })
            for register in sorted({row["register"] for row in clauses_by_recipe[recipe]}):
                carriers = clauses_by_recipe_register[(recipe, register)]
                carrier_pages = pages_of(carriers)
                expected_witnesses.append({
                    "partial_witness_id": f"G501-W{len(expected_witnesses) + 1:04d}",
                    "partial_candidate_id": candidate_id,
                    "target_matrix_cell_id": target["source_matrix_cell_id"],
                    "target_action_recipe": target["action_recipe"],
                    "target_register": target["register"],
                    "partial_recipe": recipe,
                    "partial_component_count": str(candidate["partial_component_count"]),
                    "near_single_deletion": "YES" if candidate["near_deletion"] else "NO",
                    "contains_target_action_root": "YES" if contains_action else "NO",
                    "witness_relation": "SAME_REGISTER" if register == target["register"] else "CROSS_REGISTER",
                    "witness_register": register,
                    "observed_event_count": str(len(carriers)),
                    "observed_clause_form_count": str(len({row["imperative_clause_de"] for row in carriers})),
                    "observed_page_count": str(len(carrier_pages)),
                    "observed_pages": "|".join(carrier_pages),
                    "observed_event_ids": "|".join(row["global_running_event_id"] for row in carriers),
                    "observed_surfaces": "|".join(sorted({row["surface"] for row in carriers})),
                    "observed_clauses_de": " || ".join(sorted({row["imperative_clause_de"] for row in carriers})),
                    "guard": GUARD,
                })
        action_tokens = [token for token in tokens if token in ACTION_ROOTS]
        if len(action_tokens) == 2:
            ordered_pair = "+".join(action_tokens)
            pair = pair_by_key[ordered_pair]
            registers = [] if pair["registers"] == "NONE" else pair["registers"].split("|")
            expected_pairs.append({
                "pair_support_id": f"G501-P{len(expected_pairs) + 1:03d}",
                "target_matrix_cell_id": target["source_matrix_cell_id"],
                "target_frame": target["frozen_frame"],
                "target_action_recipe": target["action_recipe"],
                "target_register": target["register"],
                "ordered_action_pair": ordered_pair,
                "ordered_reading_de": pair["ordered_reading_de"],
                "pair_status": pair["status"],
                "pair_exact_recipe_type_count": pair["exact_recipe_type_count"],
                "pair_event_count": pair["event_count"],
                "pair_clean_recipe_type_count": pair["clean_recipe_type_count"],
                "pair_register_count": pair["register_count"],
                "pair_registers": pair["registers"],
                "pair_attested_in_target_register": "YES" if target["register"] in registers else "NO",
                "licensed_grades": pair["licensed_grades"],
                "licensed_arguments": pair["licensed_arguments"],
                "endpoint_license": pair["endpoint_license"],
                "guard": GUARD,
            })

    for index, (actual, expected) in enumerate(zip(candidate_rows, expected_candidates), start=1):
        check(f"candidate_{index:03d}_exact", actual == expected, expected["partial_candidate_id"])
    for index, (actual, expected) in enumerate(zip(witness_rows, expected_witnesses), start=1):
        check(f"witness_{index:03d}_exact", actual == expected, expected["partial_witness_id"])
    for index, (actual, expected) in enumerate(zip(pair_rows, expected_pairs), start=1):
        check(f"pair_{index:03d}_exact", actual == expected, expected["pair_support_id"])
    check("candidate_table_exact", candidate_rows == expected_candidates, "167 rows")
    check("witness_table_exact", witness_rows == expected_witnesses, "285 rows")
    check("pair_table_exact", pair_rows == expected_pairs, "30 rows")

    candidates_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    witnesses_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    pairs_by_target = {row["target_matrix_cell_id"]: row for row in pair_rows}
    for row in candidate_rows:
        candidates_by_target[row["target_matrix_cell_id"]].append(row)
    for row in witness_rows:
        witnesses_by_target[row["target_matrix_cell_id"]].append(row)
    frontier_by_id = {row["source_matrix_cell_id"]: row for row in frontier}
    ranking_keys: list[tuple[object, ...]] = []
    running_tiers: Counter[str] = Counter()
    for index, row in enumerate(ranked, start=1):
        target = frontier_by_id[row["source_matrix_cell_id"]]
        current_cell = current_by_source[row["source_matrix_cell_id"]]
        candidates = candidates_by_target[row["source_matrix_cell_id"]]
        local_action = [item for item in candidates if item["contains_target_action_root"] == "YES" and int(item["same_register_event_count"]) > 0]
        local_backbone = [item for item in candidates if item["contains_target_action_root"] == "NO" and int(item["same_register_event_count"]) > 0]
        cross_action = [item for item in candidates if item["contains_target_action_root"] == "YES" and int(item["cross_register_event_count"]) > 0]
        local_near = [item for item in local_action if item["near_single_deletion"] == "YES"]
        cross_near = [item for item in cross_action if item["near_single_deletion"] == "YES"]
        pair = pairs_by_target.get(row["source_matrix_cell_id"])
        pair_attested = pair is not None and pair["pair_status"] == "PAIR_ATTESTED"
        if local_near:
            tier = "A_SAME_REGISTER_NEAR_DELETION"
            reason = "EXACT_ACTION_RETAINING_N_MINUS_ONE_RECIPE_SAME_REGISTER"
        elif local_action:
            tier = "B_SAME_REGISTER_ACTION_PARTIAL"
            reason = "EXACT_ACTION_RETAINING_SHORTER_RECIPE_SAME_REGISTER"
        elif cross_near or pair_attested or local_backbone or cross_action:
            tier = "C_STRUCTURAL_PARTIAL_OR_ACTION_PAIR"
            reason = "CROSS_REGISTER_PARTIAL_OR_ATTESTED_PAIR_OR_LOCAL_BACKBONE"
        else:
            tier = "D_ATOMIC_VALUES_ONLY"
            reason = "NO_EXACT_MULTIATOM_PARTIAL_OR_ATTESTED_ACTION_PAIR"
        running_tiers[tier] += 1
        check(
            f"target_{index:02d}_identity_and_phrase_exact",
            row["frozen_frame"] == target["frozen_frame"]
            and row["action_root"] == target["action_root"]
            and row["action_recipe"] == target["action_recipe"]
            and row["register"] == target["register"]
            and row["portable_component_trace_de"] == target["portable_component_trace_de"]
            and row["owner_local_component_trace_de"] == target["owner_local_component_trace_de"]
            and row["current_default_phrase_de"] == current_cell["current_default_phrase_de"]
            and row["gdt500_editorial_status"] == current_cell["editorial_status"],
            target["source_matrix_cell_id"],
        )
        check(
            f"target_{index:02d}_tier_exact",
            row["frontier_support_tier"] == tier
            and row["frontier_support_reason"] == reason
            and int(row["frontier_priority_rank"]) == index
            and int(row["frontier_tier_rank"]) == running_tiers[tier],
            tier,
        )
        check(
            f"target_{index:02d}_local_metrics_exact",
            int(row["partial_candidate_count"]) == len(candidates)
            and int(row["exact_partial_witness_count"]) == len(witnesses_by_target[row["source_matrix_cell_id"]])
            and int(row["same_register_action_partial_count"]) == len(local_action)
            and row["same_register_action_partial_recipes"] == ("|".join(item["partial_recipe"] for item in local_action) or "NONE")
            and int(row["same_register_action_partial_event_count"]) == sum(int(item["same_register_event_count"]) for item in local_action)
            and int(row["same_register_near_deletion_count"]) == len(local_near)
            and row["same_register_near_deletion_recipes"] == ("|".join(item["partial_recipe"] for item in local_near) or "NONE")
            and int(row["same_register_near_deletion_event_count"]) == sum(int(item["same_register_event_count"]) for item in local_near)
            and int(row["longest_same_register_action_partial_length"]) == max((int(item["partial_component_count"]) for item in local_action), default=0)
            and int(row["same_register_frame_backbone_count"]) == len(local_backbone)
            and row["same_register_frame_backbone_recipes"] == ("|".join(item["partial_recipe"] for item in local_backbone) or "NONE")
            and int(row["same_register_frame_backbone_event_count"]) == sum(int(item["same_register_event_count"]) for item in local_backbone),
            f"local={len(local_action)} near={len(local_near)} backbone={len(local_backbone)}",
        )
        check(
            f"target_{index:02d}_cross_and_pair_metrics_exact",
            int(row["cross_register_action_partial_count"]) == len(cross_action)
            and int(row["cross_register_action_partial_event_count"]) == sum(int(item["cross_register_event_count"]) for item in cross_action)
            and int(row["cross_register_near_deletion_count"]) == len(cross_near)
            and int(row["cross_register_near_deletion_event_count"]) == sum(int(item["cross_register_event_count"]) for item in cross_near)
            and int(row["longest_cross_register_action_partial_length"]) == max((int(item["partial_component_count"]) for item in cross_action), default=0)
            and row["ordered_action_pair"] == (pair["ordered_action_pair"] if pair else "NONE")
            and row["ordered_pair_attested"] == ("YES" if pair_attested else "NO")
            and row["ordered_pair_attested_in_target_register"] == (pair["pair_attested_in_target_register"] if pair else "NO")
            and int(row["ordered_pair_event_count"]) == (int(pair["pair_event_count"]) if pair else 0)
            and int(row["ordered_pair_register_count"]) == (int(pair["pair_register_count"]) if pair else 0),
            f"cross={len(cross_action)} pair={pair_attested}",
        )
        check(
            f"target_{index:02d}_retention_guards_exact",
            row["all_component_value_cells_old"] == "YES"
            and row["evidence_status_retained"] == "COMPOSED_WORKING"
            and row["working_root_meaning_changed"] == "NO"
            and row["current_phrase_changed"] == "NO"
            and row["surface_prediction_made"] == "NO"
            and row["occurrence_prediction_made"] == "NO"
            and row["guard"] == GUARD,
            GUARD,
        )
        ranking_keys.append((
            TIER_ORDER[row["frontier_support_tier"]],
            -int(row["longest_same_register_action_partial_length"]),
            -int(row["same_register_near_deletion_event_count"]),
            -int(row["same_register_action_partial_event_count"]),
            -int(row["same_register_frame_backbone_event_count"]),
            -int(row["cross_register_near_deletion_event_count"]),
            -int(row["ordered_pair_event_count"]),
            int(row["component_count"]),
            row["action_recipe"],
            row["register"],
        ))
        check(f"target_{index:02d}_readable_present", row["current_default_phrase_de"] in readable, row["source_matrix_cell_id"])

    check("ranking_order_exact", ranking_keys == sorted(ranking_keys), "predeclared lexicographic rank")
    check("tier_counts_exact", running_tiers == Counter({"A_SAME_REGISTER_NEAR_DELETION": 16, "B_SAME_REGISTER_ACTION_PARTIAL": 3, "C_STRUCTURAL_PARTIAL_OR_ACTION_PAIR": 27, "D_ATOMIC_VALUES_ONLY": 4}), str(running_tiers))

    def expected_summary(axis: str) -> list[dict[str, str]]:
        output: list[dict[str, str]] = []
        for value in sorted({row[axis] for row in ranked}):
            group = [row for row in ranked if row[axis] == value]
            tiers = Counter(row["frontier_support_tier"] for row in group)
            output.append({
                axis: value,
                "frontier_cell_count": str(len(group)),
                "tier_a_near_same_register_count": str(tiers["A_SAME_REGISTER_NEAR_DELETION"]),
                "tier_b_partial_same_register_count": str(tiers["B_SAME_REGISTER_ACTION_PARTIAL"]),
                "tier_c_structural_count": str(tiers["C_STRUCTURAL_PARTIAL_OR_ACTION_PAIR"]),
                "tier_d_atomic_only_count": str(tiers["D_ATOMIC_VALUES_ONLY"]),
                "same_register_action_partial_count": str(sum(int(row["same_register_action_partial_count"]) for row in group)),
                "same_register_action_partial_event_count": str(sum(int(row["same_register_action_partial_event_count"]) for row in group)),
                "attested_ordered_pair_cell_count": str(sum(row["ordered_pair_attested"] == "YES" for row in group)),
                "gdt500_phrase_change_count": str(sum(row["current_phrase_changed"] == "YES" for row in group)),
            })
        return output

    check("tier_summary_exact", tier_rows == expected_summary("frontier_support_tier"), "4 rows")
    check("frame_summary_exact", frame_rows == expected_summary("frozen_frame"), "5 rows")
    check("action_summary_exact", action_rows == expected_summary("action_root"), "7 rows")
    check("readable_status_guard_exact", STATUS in readable and GUARD in readable, "status and guard")

    tiers = Counter(row["frontier_support_tier"] for row in ranked)
    expected_result = {
        "status": STATUS,
        "frontier_cells_ranked": 50,
        "tier_a_same_register_near_deletion": tiers["A_SAME_REGISTER_NEAR_DELETION"],
        "tier_b_same_register_action_partial": tiers["B_SAME_REGISTER_ACTION_PARTIAL"],
        "tier_c_structural_partial_or_action_pair": tiers["C_STRUCTURAL_PARTIAL_OR_ACTION_PAIR"],
        "tier_d_atomic_values_only": tiers["D_ATOMIC_VALUES_ONLY"],
        "partial_subrecipe_candidates": len(candidate_rows),
        "exact_partial_recipe_witnesses": len(witness_rows),
        "same_register_partial_witnesses": sum(row["witness_relation"] == "SAME_REGISTER" for row in witness_rows),
        "cross_register_partial_witnesses": sum(row["witness_relation"] == "CROSS_REGISTER" for row in witness_rows),
        "ordered_action_pair_cells": len(pair_rows),
        "ordered_action_pair_attested": sum(row["pair_status"] == "PAIR_ATTESTED" for row in pair_rows),
        "ordered_action_pair_attested_target_register": sum(row["pair_attested_in_target_register"] == "YES" for row in pair_rows),
        "cells_with_any_same_register_action_partial": sum(int(row["same_register_action_partial_count"]) > 0 for row in ranked),
        "cells_with_same_register_near_deletion": sum(int(row["same_register_near_deletion_count"]) > 0 for row in ranked),
        "cells_with_any_cross_register_action_partial": sum(int(row["cross_register_action_partial_count"]) > 0 for row in ranked),
        "cells_with_local_frame_backbone": sum(int(row["same_register_frame_backbone_count"]) > 0 for row in ranked),
        "gdt500_current_phrases_retained": sum(row["current_phrase_changed"] == "NO" for row in ranked),
        "composed_labels_retained": sum(row["evidence_status_retained"] == "COMPOSED_WORKING" for row in ranked),
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "frame_count": 5,
        "action_count": 7,
        "guard": GUARD,
    }
    check("result_exact", result == expected_result, json.dumps(expected_result, ensure_ascii=False, sort_keys=True))

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": failed,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
