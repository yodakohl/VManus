#!/usr/bin/env python3
"""Rank the fifty old-values-only cells by exact old partial-frame support."""

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


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def page_key(page: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if match:
        return int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), page
    return 10**9, 0, 0, page


def pages_of(rows: list[dict[str, str]]) -> list[str]:
    return sorted({row["physical_page"] for row in rows}, key=page_key)


def unique_partial_candidates(tokens: list[str]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for length in range(2, len(tokens)):
        for positions in itertools.combinations(range(len(tokens)), length):
            partial = [tokens[position] for position in positions]
            recipe = "+".join(partial)
            removed = [position for position in range(len(tokens)) if position not in positions]
            entry = grouped.setdefault(recipe, {
                "partial_recipe": recipe,
                "partial_tokens": partial,
                "partial_component_count": length,
                "removal_position_sets": [],
                "removed_token_sets": [],
                "near_deletion": length == len(tokens) - 1,
                "contiguous": False,
            })
            entry["removal_position_sets"].append(",".join(str(position + 1) for position in removed))
            entry["removed_token_sets"].append("+".join(tokens[position] for position in removed))
            if positions == tuple(range(positions[0], positions[0] + length)):
                entry["contiguous"] = True
    return list(grouped.values())


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _pair_fields, pairs = read_tsv(PAIR_IN)
    _frontier_fields, frontier = read_tsv(FRONTIER_IN)
    _current_fields, current = read_tsv(CURRENT_IN)
    if (len(clauses), len(pairs), len(frontier), len(current)) != (4576, 81, 50, 495):
        raise ValueError("source count drift")
    current_by_source = {row["source_matrix_cell_id"]: row for row in current}
    pair_by_key = {row["ordered_pair"]: row for row in pairs}
    clauses_by_recipe_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    clauses_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_recipe_register[(row["component_recipe"], row["register"])].append(row)
        clauses_by_recipe[row["component_recipe"]].append(row)

    draft: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    witness_rows: list[dict[str, object]] = []
    pair_rows: list[dict[str, object]] = []
    for target in frontier:
        target_id = target["source_matrix_cell_id"]
        current_cell = current_by_source[target_id]
        tokens = target["action_recipe"].split("+")
        candidates = unique_partial_candidates(tokens)
        local_action_candidates: list[tuple[dict[str, object], list[dict[str, str]]]] = []
        local_backbone_candidates: list[tuple[dict[str, object], list[dict[str, str]]]] = []
        cross_action_candidates: list[tuple[dict[str, object], list[dict[str, str]]]] = []
        target_witness_start = len(witness_rows)
        for candidate in candidates:
            recipe = str(candidate["partial_recipe"])
            partial_tokens = list(candidate["partial_tokens"])
            contains_target_action = target["action_root"] in partial_tokens
            same = clauses_by_recipe_register[(recipe, target["register"])]
            cross = [row for row in clauses_by_recipe[recipe] if row["register"] != target["register"]]
            same_pages = pages_of(same)
            cross_pages = pages_of(cross)
            cross_registers = sorted({row["register"] for row in cross})
            candidate_id = f"G501-C{len(candidate_rows) + 1:04d}"
            candidate_rows.append({
                "partial_candidate_id": candidate_id,
                "target_matrix_cell_id": target_id,
                "target_frame": target["frozen_frame"],
                "target_action_root": target["action_root"],
                "target_action_recipe": target["action_recipe"],
                "target_register": target["register"],
                "partial_recipe": recipe,
                "partial_component_count": candidate["partial_component_count"],
                "removed_component_count": len(tokens) - int(candidate["partial_component_count"]),
                "removal_position_sets": "|".join(candidate["removal_position_sets"]),
                "removed_token_sets": "|".join(candidate["removed_token_sets"]),
                "near_single_deletion": "YES" if candidate["near_deletion"] else "NO",
                "contiguous_in_target": "YES" if candidate["contiguous"] else "NO",
                "contains_target_action_root": "YES" if contains_target_action else "NO",
                "same_register_exact_cell_count": 1 if same else 0,
                "same_register_event_count": len(same),
                "same_register_clause_form_count": len({row["imperative_clause_de"] for row in same}),
                "same_register_page_count": len(same_pages),
                "same_register_pages": "|".join(same_pages) or "NONE",
                "cross_register_exact_cell_count": len(cross_registers),
                "cross_registers": "|".join(cross_registers) or "NONE",
                "cross_register_event_count": len(cross),
                "cross_register_page_count": len(cross_pages),
                "cross_register_pages": "|".join(cross_pages) or "NONE",
                "guard": GUARD,
            })
            if contains_target_action and same:
                local_action_candidates.append((candidate, same))
            if not contains_target_action and same:
                local_backbone_candidates.append((candidate, same))
            if contains_target_action and cross:
                cross_action_candidates.append((candidate, cross))
            for register in sorted({row["register"] for row in clauses_by_recipe[recipe]}):
                carrier_rows = clauses_by_recipe_register[(recipe, register)]
                carrier_pages = pages_of(carrier_rows)
                witness_rows.append({
                    "partial_witness_id": f"G501-W{len(witness_rows) + 1:04d}",
                    "partial_candidate_id": candidate_id,
                    "target_matrix_cell_id": target_id,
                    "target_action_recipe": target["action_recipe"],
                    "target_register": target["register"],
                    "partial_recipe": recipe,
                    "partial_component_count": candidate["partial_component_count"],
                    "near_single_deletion": "YES" if candidate["near_deletion"] else "NO",
                    "contains_target_action_root": "YES" if contains_target_action else "NO",
                    "witness_relation": "SAME_REGISTER" if register == target["register"] else "CROSS_REGISTER",
                    "witness_register": register,
                    "observed_event_count": len(carrier_rows),
                    "observed_clause_form_count": len({row["imperative_clause_de"] for row in carrier_rows}),
                    "observed_page_count": len(carrier_pages),
                    "observed_pages": "|".join(carrier_pages),
                    "observed_event_ids": "|".join(row["global_running_event_id"] for row in carrier_rows),
                    "observed_surfaces": "|".join(sorted({row["surface"] for row in carrier_rows})),
                    "observed_clauses_de": " || ".join(sorted({row["imperative_clause_de"] for row in carrier_rows})),
                    "guard": GUARD,
                })

        action_tokens = [token for token in tokens if token in ACTION_ROOTS]
        if len(action_tokens) == 2:
            ordered_pair = "+".join(action_tokens)
            pair = pair_by_key[ordered_pair]
            pair_attested = pair["status"] == "PAIR_ATTESTED"
            pair_registers = [] if pair["registers"] == "NONE" else pair["registers"].split("|")
            pair_same_register = target["register"] in pair_registers
            pair_rows.append({
                "pair_support_id": f"G501-P{len(pair_rows) + 1:03d}",
                "target_matrix_cell_id": target_id,
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
                "pair_attested_in_target_register": "YES" if pair_same_register else "NO",
                "licensed_grades": pair["licensed_grades"],
                "licensed_arguments": pair["licensed_arguments"],
                "endpoint_license": pair["endpoint_license"],
                "guard": GUARD,
            })
        else:
            ordered_pair = "NONE"
            pair_attested = False
            pair_same_register = False
            pair = None

        local_near = [item for item in local_action_candidates if bool(item[0]["near_deletion"])]
        cross_near = [item for item in cross_action_candidates if bool(item[0]["near_deletion"])]
        local_action_events = sum(len(rows) for _candidate, rows in local_action_candidates)
        local_near_events = sum(len(rows) for _candidate, rows in local_near)
        local_backbone_events = sum(len(rows) for _candidate, rows in local_backbone_candidates)
        cross_action_events = sum(len(rows) for _candidate, rows in cross_action_candidates)
        cross_near_events = sum(len(rows) for _candidate, rows in cross_near)
        longest_local = max((int(candidate["partial_component_count"]) for candidate, _rows in local_action_candidates), default=0)
        longest_cross = max((int(candidate["partial_component_count"]) for candidate, _rows in cross_action_candidates), default=0)
        if local_near:
            tier = "A_SAME_REGISTER_NEAR_DELETION"
            reason = "EXACT_ACTION_RETAINING_N_MINUS_ONE_RECIPE_SAME_REGISTER"
        elif local_action_candidates:
            tier = "B_SAME_REGISTER_ACTION_PARTIAL"
            reason = "EXACT_ACTION_RETAINING_SHORTER_RECIPE_SAME_REGISTER"
        elif cross_near or pair_attested or local_backbone_candidates or cross_action_candidates:
            tier = "C_STRUCTURAL_PARTIAL_OR_ACTION_PAIR"
            reason = "CROSS_REGISTER_PARTIAL_OR_ATTESTED_PAIR_OR_LOCAL_BACKBONE"
        else:
            tier = "D_ATOMIC_VALUES_ONLY"
            reason = "NO_EXACT_MULTIATOM_PARTIAL_OR_ATTESTED_ACTION_PAIR"
        draft.append({
            "frontier_priority_rank": 0,
            "frontier_tier_rank": 0,
            "frontier_support_tier": tier,
            "frontier_support_reason": reason,
            "source_matrix_cell_id": target_id,
            "frozen_frame": target["frozen_frame"],
            "action_root": target["action_root"],
            "action_recipe": target["action_recipe"],
            "register": target["register"],
            "portable_component_trace_de": target["portable_component_trace_de"],
            "owner_local_component_trace_de": target["owner_local_component_trace_de"],
            "current_default_phrase_de": current_cell["current_default_phrase_de"],
            "gdt500_editorial_status": current_cell["editorial_status"],
            "component_count": len(tokens),
            "partial_candidate_count": len(candidates),
            "exact_partial_witness_count": len(witness_rows) - target_witness_start,
            "same_register_action_partial_count": len(local_action_candidates),
            "same_register_action_partial_recipes": "|".join(str(item[0]["partial_recipe"]) for item in local_action_candidates) or "NONE",
            "same_register_action_partial_event_count": local_action_events,
            "same_register_near_deletion_count": len(local_near),
            "same_register_near_deletion_recipes": "|".join(str(item[0]["partial_recipe"]) for item in local_near) or "NONE",
            "same_register_near_deletion_event_count": local_near_events,
            "longest_same_register_action_partial_length": longest_local,
            "same_register_frame_backbone_count": len(local_backbone_candidates),
            "same_register_frame_backbone_recipes": "|".join(str(item[0]["partial_recipe"]) for item in local_backbone_candidates) or "NONE",
            "same_register_frame_backbone_event_count": local_backbone_events,
            "cross_register_action_partial_count": len(cross_action_candidates),
            "cross_register_action_partial_event_count": cross_action_events,
            "cross_register_near_deletion_count": len(cross_near),
            "cross_register_near_deletion_event_count": cross_near_events,
            "longest_cross_register_action_partial_length": longest_cross,
            "ordered_action_pair": ordered_pair,
            "ordered_pair_attested": "YES" if pair_attested else "NO",
            "ordered_pair_attested_in_target_register": "YES" if pair_same_register else "NO",
            "ordered_pair_event_count": int(pair["event_count"]) if pair else 0,
            "ordered_pair_register_count": int(pair["register_count"]) if pair else 0,
            "all_component_value_cells_old": target["all_component_value_cells_old"],
            "evidence_status_retained": target["evidence_status_retained"],
            "working_root_meaning_changed": "NO",
            "current_phrase_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    ranked = sorted(draft, key=lambda row: (
        TIER_ORDER[str(row["frontier_support_tier"])],
        -int(row["longest_same_register_action_partial_length"]),
        -int(row["same_register_near_deletion_event_count"]),
        -int(row["same_register_action_partial_event_count"]),
        -int(row["same_register_frame_backbone_event_count"]),
        -int(row["cross_register_near_deletion_event_count"]),
        -int(row["ordered_pair_event_count"]),
        int(row["component_count"]),
        str(row["action_recipe"]),
        str(row["register"]),
    ))
    tier_counter: Counter[str] = Counter()
    for rank, row in enumerate(ranked, start=1):
        tier_counter[str(row["frontier_support_tier"])] += 1
        row["frontier_priority_rank"] = rank
        row["frontier_tier_rank"] = tier_counter[str(row["frontier_support_tier"])]
    write_tsv(RANKED_OUT, ranked)
    write_tsv(CANDIDATE_OUT, candidate_rows)
    write_tsv(WITNESS_OUT, witness_rows)
    write_tsv(PAIR_OUT, pair_rows)

    def summarize(axis: str) -> list[dict[str, object]]:
        output: list[dict[str, object]] = []
        for value in sorted({str(row[axis]) for row in ranked}):
            group = [row for row in ranked if row[axis] == value]
            tiers = Counter(str(row["frontier_support_tier"]) for row in group)
            output.append({
                axis: value,
                "frontier_cell_count": len(group),
                "tier_a_near_same_register_count": tiers["A_SAME_REGISTER_NEAR_DELETION"],
                "tier_b_partial_same_register_count": tiers["B_SAME_REGISTER_ACTION_PARTIAL"],
                "tier_c_structural_count": tiers["C_STRUCTURAL_PARTIAL_OR_ACTION_PAIR"],
                "tier_d_atomic_only_count": tiers["D_ATOMIC_VALUES_ONLY"],
                "same_register_action_partial_count": sum(int(row["same_register_action_partial_count"]) for row in group),
                "same_register_action_partial_event_count": sum(int(row["same_register_action_partial_event_count"]) for row in group),
                "attested_ordered_pair_cell_count": sum(row["ordered_pair_attested"] == "YES" for row in group),
                "gdt500_phrase_change_count": sum(row["current_phrase_changed"] == "YES" for row in group),
            })
        return output

    tier_rows = summarize("frontier_support_tier")
    frame_rows = summarize("frozen_frame")
    action_rows = summarize("action_root")
    write_tsv(TIER_OUT, tier_rows)
    write_tsv(FRAME_OUT, frame_rows)
    write_tsv(ACTION_OUT, action_rows)

    lines = [
        "# GDT501 — Teilrahmenatlas der fünfzigzelligen Front",
        "",
        f"Status: `{STATUS}`",
        "",
        "Die GDT499-Tier-D-Zellen bleiben Kompositionen. Ihre neue Reihenfolge zeigt",
        "nur, welche alten kürzeren Rezepte oder geordneten Aktionspaare bereits",
        "beobachtet sind. Die aktuellen GDT500-Phrasen bleiben unverändert.",
        "",
        "## Vollständige Rangfolge",
        "",
        "| Rang | Stufe | Rezept | Register | aktueller Default | lokales N−1 | lokale Teilrezepte/Events | Paar/Events |",
        "|---:|---|---|---|---|---:|---:|---|",
    ]
    for row in ranked:
        lines.append(
            f'| {row["frontier_priority_rank"]} | `{row["frontier_support_tier"]}` | '
            f'`{row["action_recipe"]}` | {row["register"]} | {row["current_default_phrase_de"]} | '
            f'{row["same_register_near_deletion_count"]} | '
            f'{row["same_register_action_partial_count"]}/{row["same_register_action_partial_event_count"]} | '
            f'`{row["ordered_action_pair"]}`/{row["ordered_pair_event_count"]} |'
        )
    lines.extend(["", f"`{GUARD}`", ""])
    READABLE_OUT.write_text("\n".join(lines), encoding="utf-8")

    tiers = Counter(str(row["frontier_support_tier"]) for row in ranked)
    result = {
        "status": STATUS,
        "frontier_cells_ranked": len(ranked),
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
        "frame_count": len(frame_rows),
        "action_count": len(action_rows),
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
