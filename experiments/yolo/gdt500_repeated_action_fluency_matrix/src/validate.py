#!/usr/bin/env python3
"""Independently validate the GDT500 complete fluent default deck."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt500_repeated_action_fluency_matrix"
ART = BASE / "artifacts"
G498 = ROOT / "experiments/yolo/gdt498_nine_action_frame_register_matrix/artifacts"
G499 = ROOT / "experiments/yolo/gdt499_nine_action_composition_priority_atlas/artifacts"

MATRIX_IN = G498 / "gdt498_495_action_frame_register_cells.tsv"
RANKED_IN = G499 / "gdt499_352_ranked_compositions.tsv"
REPEATED_IN = G499 / "gdt499_repeated_action_compositions.tsv"
MATRIX_OUT = ART / "gdt500_495_current_fluent_cells.tsv"
EDITED_OUT = ART / "gdt500_15_repeated_action_fluency_cards.tsv"
UNCHANGED_OUT = ART / "gdt500_480_unchanged_cells.tsv"
OBSERVED_OUT = ART / "gdt500_143_observed_phrase_retention.tsv"
COMPOSED_OUT = ART / "gdt500_352_composed_current_defaults.tsv"
REGISTER_OUT = ART / "gdt500_5_register_fluency_coverage.tsv"
RULE_OUT = ART / "gdt500_3_compression_rule_coverage.tsv"
READABLE_OUT = ART / "GDT500_COMPLETE_495_FLUENT_DEFAULT_DECK.md"
RESULT_OUT = ART / "gdt500_result.json"
VALIDATION_OUT = ART / "gdt500_validation.json"

STATUS = "FIFTEEN_REPEATED_ACTIONS_FLUENT_AND_REVERSIBLE__FOUR_HUNDRED_EIGHTY_UNCHANGED"
GUARD = "EDITORIAL_FLUENCY_ONLY__TWO_ACTION_SLOTS_RETAINED__NO_MEANING_OR_EVIDENCE_CHANGE"
RULE_BY_RECIPE = {
    "CH+CH": "CH_CH_ACTIVE_ARGUMENT_TO_ZWEIMAL",
    "CHD+CHD+Y": "CHD_CHD_POST_TO_ZWEIMAL",
    "CH+CH+E+Y": "CH_CH_GRADE_POST_TO_ZWEIMAL",
}
ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def expected_compression(source: dict[str, str]) -> tuple[str, str, str, str]:
    tail = "; auf Grad I." if source["action_recipe"] == "CH+CH+E+Y" else "."
    phrase = source["current_default_phrase_de"]
    if not phrase.endswith(tail):
        raise ValueError(f"tail drift: {source['matrix_cell_id']}")
    parts = phrase[:-len(tail)].split(" und ")
    if len(parts) != 2:
        raise ValueError(f"binary action drift: {source['matrix_cell_id']}")
    first, second = parts
    if first.endswith(" auf"):
        current = first[:-4] + " zweimal auf" + tail
    else:
        current = first + " zweimal" + tail
    return first, second, tail, current


def main() -> int:
    _source_fields, source = read_tsv(MATRIX_IN)
    _ranked_fields, ranked = read_tsv(RANKED_IN)
    _repeated_fields, repeated_source = read_tsv(REPEATED_IN)
    matrix_fields, matrix = read_tsv(MATRIX_OUT)
    edited_fields, edited = read_tsv(EDITED_OUT)
    unchanged_fields, unchanged = read_tsv(UNCHANGED_OUT)
    observed_fields, observed = read_tsv(OBSERVED_OUT)
    composed_fields, composed = read_tsv(COMPOSED_OUT)
    _register_fields, register_rows = read_tsv(REGISTER_OUT)
    _rule_fields, rule_rows = read_tsv(RULE_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    counts = (
        len(source), len(ranked), len(repeated_source), len(matrix), len(edited),
        len(unchanged), len(observed), len(composed), len(register_rows), len(rule_rows),
    )
    check("all_table_counts_exact", counts == (495, 352, 15, 495, 15, 480, 143, 352, 5, 3), f"actual={counts}")
    check("all_subset_schemas_exact", edited_fields == unchanged_fields == observed_fields == composed_fields == matrix_fields, "five schemas")
    check("matrix_ids_exact", [row["current_cell_id"] for row in matrix] == [f"G500-M{i:03d}" for i in range(1, 496)], "M001..M495")
    check("matrix_source_ids_exact", [row["source_matrix_cell_id"] for row in matrix] == [row["matrix_cell_id"] for row in source], "source order exact")

    source_by_id = {row["matrix_cell_id"]: row for row in source}
    rank_by_id = {row["source_matrix_cell_id"]: row for row in ranked}
    repeated_ids = {row["source_matrix_cell_id"] for row in repeated_source}
    independently_repeated_ids: set[str] = set()
    for row in source:
        action_tokens = [token for token in row["action_recipe"].split("+") if token in ACTION_ROOTS]
        if any(count > 1 for count in Counter(action_tokens).values()):
            independently_repeated_ids.add(row["matrix_cell_id"])
    check("repeated_source_set_independently_exact", repeated_ids == independently_repeated_ids, f"ids={len(repeated_ids)}")
    check("repeated_recipe_inventory_exact", Counter(source_by_id[key]["action_recipe"] for key in repeated_ids) == Counter({"CH+CH": 5, "CHD+CHD+Y": 5, "CH+CH+E+Y": 5}), "three recipes x five")

    expected_edited: list[dict[str, str]] = []
    expected_unchanged: list[dict[str, str]] = []
    expected_observed: list[dict[str, str]] = []
    expected_composed: list[dict[str, str]] = []
    for index, row in enumerate(matrix, start=1):
        old = source_by_id[row["source_matrix_cell_id"]]
        is_edited = old["matrix_cell_id"] in repeated_ids
        rank = rank_by_id.get(old["matrix_cell_id"])
        expected_action_count = sum(token in ACTION_ROOTS for token in old["action_recipe"].split("+"))
        check(
            f"cell_{index:03d}_source_identity_exact",
            row["frozen_frame"] == old["frozen_frame"]
            and row["action_root"] == old["action_root"]
            and row["action_recipe"] == old["action_recipe"]
            and row["register"] == old["register"]
            and row["portable_component_trace_de"] == old["portable_component_trace_de"]
            and row["owner_local_component_trace_de"] == old["owner_local_component_trace_de"]
            and row["previous_default_phrase_de"] == old["current_default_phrase_de"],
            old["matrix_cell_id"],
        )
        check(
            f"cell_{index:03d}_evidence_and_priority_exact",
            row["evidence_status_retained"] == old["evidence_status"]
            and row["composition_support_class"] == old["composition_support_class"]
            and row["state_requirement"] == old["state_requirement"]
            and row["observed_event_count"] == old["observed_event_count"]
            and row["observed_pages"] == old["observed_pages"]
            and row["all_component_value_cells_old"] == old["all_component_value_cells_old"] == "YES"
            and row["composition_priority_tier"] == (rank["priority_tier"] if rank else "OBSERVED_EXACT_CELL")
            and row["composition_global_priority_rank"] == (rank["global_priority_rank"] if rank else "NONE"),
            row["evidence_status_retained"],
        )
        if is_edited:
            first, second, tail, current = expected_compression(old)
            expected_root = "CHD" if old["action_recipe"].startswith("CHD") else "CH"
            if old["action_recipe"] == "CH+CH":
                verb = first.split(" ", 1)[0].lower()
                separable = " auf" if first.endswith(" auf") else ""
                expected_second = f"{verb} es{separable}"
            else:
                expected_second = first[:1].lower() + first[1:]
            check(
                f"cell_{index:03d}_repeated_source_shape_exact",
                second == expected_second
                and old["action_recipe"] in RULE_BY_RECIPE
                and expected_action_count == 2,
                f"first={first!r} second={second!r}",
            )
            check(
                f"cell_{index:03d}_compression_exact",
                row["current_default_phrase_de"] == current
                and row["editorial_status"] == "REPEATED_ACTION_COMPRESSED"
                and row["compression_rule"] == RULE_BY_RECIPE[old["action_recipe"]]
                and row["action_slot_count_retained"] == "2"
                and row["repeated_action_root_count"] == "1"
                and row["repeated_action_roots"] == expected_root
                and row["compressed_count_marker_de"] == "zweimal"
                and row["current_default_phrase_de"].count("zweimal") == 1,
                current,
            )
            check(
                f"cell_{index:03d}_roundtrip_segments_exact",
                row["source_first_action_clause_de"] == first
                and row["source_second_action_clause_de"] == second
                and row["source_phrase_tail_de"] == tail
                and row["roundtrip_expanded_phrase_de"] == f"{first} und {second}{tail}"
                and row["roundtrip_expanded_phrase_de"] == old["current_default_phrase_de"]
                and row["exact_source_phrase_roundtrip"] == "YES",
                old["current_default_phrase_de"],
            )
        else:
            check(
                f"cell_{index:03d}_unchanged_exact",
                row["current_default_phrase_de"] == old["current_default_phrase_de"]
                and row["editorial_status"] == "UNCHANGED"
                and row["compression_rule"] == "NONE"
                and int(row["action_slot_count_retained"]) == expected_action_count
                and row["repeated_action_root_count"] == "0"
                and row["repeated_action_roots"] == "NONE"
                and row["source_first_action_clause_de"] == "NONE"
                and row["source_second_action_clause_de"] == "NONE"
                and row["source_phrase_tail_de"] == "NONE"
                and row["compressed_count_marker_de"] == "NONE"
                and row["roundtrip_expanded_phrase_de"] == old["current_default_phrase_de"]
                and row["exact_source_phrase_roundtrip"] == "YES",
                old["current_default_phrase_de"],
            )
        check(
            f"cell_{index:03d}_guards_exact",
            row["working_root_meaning_changed"] == "NO"
            and row["evidence_status_changed"] == "NO"
            and row["recipe_changed"] == "NO"
            and row["surface_prediction_made"] == "NO"
            and row["occurrence_prediction_made"] == "NO"
            and row["guard"] == GUARD,
            GUARD,
        )
        check(
            f"cell_{index:03d}_readable_present",
            row["current_cell_id"] in readable and row["current_default_phrase_de"] in readable,
            row["current_cell_id"],
        )
        if is_edited:
            expected_edited.append(row)
        else:
            expected_unchanged.append(row)
        if row["evidence_status_retained"] == "OBSERVED_CLAUSE":
            expected_observed.append(row)
        else:
            expected_composed.append(row)

    check("edited_subset_exact", edited == expected_edited, "15 rows in matrix order")
    check("unchanged_subset_exact", unchanged == expected_unchanged, "480 rows in matrix order")
    check("observed_subset_exact", observed == expected_observed, "143 rows in matrix order")
    check("composed_subset_exact", composed == expected_composed, "352 rows in matrix order")
    check("all_observed_phrases_byte_retained", all(row["previous_default_phrase_de"] == row["current_default_phrase_de"] for row in observed), "143/143")
    check("all_nonrepeat_compositions_byte_retained", all(row["previous_default_phrase_de"] == row["current_default_phrase_de"] for row in composed if row["editorial_status"] == "UNCHANGED"), "337/337")

    by_register: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in matrix:
        by_register[row["register"]].append(row)
    expected_registers: list[dict[str, str]] = []
    for register in sorted(by_register):
        group = by_register[register]
        expected_registers.append({
            "register": register,
            "cell_count": str(len(group)),
            "observed_cell_count": str(sum(row["evidence_status_retained"] == "OBSERVED_CLAUSE" for row in group)),
            "composed_cell_count": str(sum(row["evidence_status_retained"] == "COMPOSED_WORKING" for row in group)),
            "edited_repeated_action_count": str(sum(row["editorial_status"] == "REPEATED_ACTION_COMPRESSED" for row in group)),
            "unchanged_count": str(sum(row["editorial_status"] == "UNCHANGED" for row in group)),
            "exact_roundtrip_count": str(sum(row["exact_source_phrase_roundtrip"] == "YES" for row in group)),
            "all_component_traces_retained": "YES",
        })
    check("register_summary_exact", register_rows == expected_registers, "five registers")

    by_rule: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in edited:
        by_rule[row["compression_rule"]].append(row)
    expected_rules: list[dict[str, str]] = []
    for rule in sorted(by_rule):
        group = by_rule[rule]
        expected_rules.append({
            "compression_rule": rule,
            "action_recipe": group[0]["action_recipe"],
            "edited_cell_count": str(len(group)),
            "register_count": str(len({row["register"] for row in group})),
            "registers": "|".join(sorted(row["register"] for row in group)),
            "exact_source_roundtrip_count": str(sum(row["exact_source_phrase_roundtrip"] == "YES" for row in group)),
            "two_action_slots_retained_count": str(sum(row["action_slot_count_retained"] == "2" for row in group)),
            "zweimal_marker_count": str(sum(row["current_default_phrase_de"].count("zweimal") == 1 for row in group)),
        })
    check("rule_summary_exact", rule_rows == expected_rules, "three rules")
    check("readable_status_and_guard_exact", STATUS in readable and GUARD in readable, "status and guard")

    rule_counts = Counter(row["compression_rule"] for row in edited)
    expected_result = {
        "status": STATUS,
        "complete_current_cells": 495,
        "observed_cells_retained": 143,
        "composed_cells_retained": 352,
        "edited_repeated_action_cells": 15,
        "unchanged_cells": 480,
        "ch_ch_active_argument_edits": rule_counts["CH_CH_ACTIVE_ARGUMENT_TO_ZWEIMAL"],
        "chd_chd_post_edits": rule_counts["CHD_CHD_POST_TO_ZWEIMAL"],
        "ch_ch_grade_post_edits": rule_counts["CH_CH_GRADE_POST_TO_ZWEIMAL"],
        "registers_each_with_three_edits": sum(row["edited_repeated_action_count"] == "3" for row in register_rows),
        "zweimal_markers": sum(row["current_default_phrase_de"].count("zweimal") for row in edited),
        "exact_source_phrase_roundtrips": sum(row["exact_source_phrase_roundtrip"] == "YES" for row in edited),
        "two_action_slot_traces_retained": sum(row["action_slot_count_retained"] == "2" for row in edited),
        "observed_phrase_changes": sum(row["previous_default_phrase_de"] != row["current_default_phrase_de"] for row in observed),
        "nonrepeated_composed_phrase_changes": sum(row["previous_default_phrase_de"] != row["current_default_phrase_de"] for row in composed if row["editorial_status"] == "UNCHANGED"),
        "component_trace_changes": 0,
        "working_root_meaning_changes": 0,
        "evidence_status_changes": 0,
        "recipe_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
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
