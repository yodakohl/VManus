#!/usr/bin/env python3
"""Independently validate the GDT499 composition-priority atlas."""

from __future__ import annotations

import csv
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
BASE = ROOT / "experiments/yolo/gdt499_nine_action_composition_priority_atlas"
ART = BASE / "artifacts"
G498 = ROOT / "experiments/yolo/gdt498_nine_action_frame_register_matrix/artifacts"

MATRIX_IN = G498 / "gdt498_495_action_frame_register_cells.tsv"
RANKED_OUT = ART / "gdt499_352_ranked_compositions.tsv"
TIER_A_OUT = ART / "gdt499_165_local_multihead_compositions.tsv"
TIER_B_OUT = ART / "gdt499_88_local_single_head_compositions.tsv"
TIER_C_OUT = ART / "gdt499_49_cross_register_compositions.tsv"
TIER_D_OUT = ART / "gdt499_50_old_values_only_compositions.tsv"
LOCAL_OUT = ART / "gdt499_local_observed_support_witnesses.tsv"
CROSS_OUT = ART / "gdt499_cross_register_observed_support_witnesses.tsv"
REPEATED_OUT = ART / "gdt499_repeated_action_compositions.tsv"
FRAME_OUT = ART / "gdt499_11_frame_priority_coverage.tsv"
ACTION_OUT = ART / "gdt499_9_action_priority_coverage.tsv"
READABLE_OUT = ART / "GDT499_NINE_ACTION_COMPOSITION_PRIORITY_ATLAS.md"
RESULT_OUT = ART / "gdt499_result.json"
VALIDATION_OUT = ART / "gdt499_validation.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
TIER_ORDER = {
    "A_LOCAL_MULTIHEAD": 0,
    "B_LOCAL_SINGLE_HEAD": 1,
    "C_CROSS_REGISTER_SAME_ACTION": 2,
    "D_OLD_VALUES_ONLY": 3,
}
STATUS = "ONE_HUNDRED_SIXTY_FIVE_PRODUCTIVE_MULTIHEAD_COMPOSITIONS__FIFTY_OLD_VALUES_ONLY_FRONTIER"
GUARD = "COMPOSED_WORKING_RETAINED__NO_SURFACE_OR_OCCURRENCE_PREDICTION"


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


def union_pages(rows: list[dict[str, str]]) -> list[str]:
    pages: set[str] = set()
    for row in rows:
        pages.update(page for page in row["observed_pages"].split("|") if page and page != "NONE")
    return sorted(pages, key=page_key)


def main() -> int:
    matrix_fields, matrix = read_tsv(MATRIX_IN)
    ranked_fields, ranked = read_tsv(RANKED_OUT)
    a_fields, tier_a = read_tsv(TIER_A_OUT)
    b_fields, tier_b = read_tsv(TIER_B_OUT)
    c_fields, tier_c = read_tsv(TIER_C_OUT)
    d_fields, tier_d = read_tsv(TIER_D_OUT)
    local_fields, local_rows = read_tsv(LOCAL_OUT)
    cross_fields, cross_rows = read_tsv(CROSS_OUT)
    repeated_fields, repeated = read_tsv(REPEATED_OUT)
    _frame_fields, frame_rows = read_tsv(FRAME_OUT)
    _action_fields, action_rows = read_tsv(ACTION_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    expected_counts = (495, 352, 165, 88, 49, 50, 646, 288, 15, 11, 9)
    actual_counts = (
        len(matrix), len(ranked), len(tier_a), len(tier_b), len(tier_c), len(tier_d),
        len(local_rows), len(cross_rows), len(repeated), len(frame_rows), len(action_rows),
    )
    check("all_table_counts_exact", actual_counts == expected_counts, f"actual={actual_counts}")
    check("tier_subset_schemas_exact", a_fields == b_fields == c_fields == d_fields == repeated_fields == ranked_fields, "six ranked schemas")
    check("source_matrix_schema_expected", {"matrix_cell_id", "composition_support_class", "observed_event_ids"} <= set(matrix_fields), f"fields={len(matrix_fields)}")
    check("local_schema_complete", {"local_witness_id", "target_matrix_cell_id", "observed_matrix_cell_id"} <= set(local_fields), f"fields={len(local_fields)}")
    check("cross_schema_complete", {"cross_witness_id", "target_matrix_cell_id", "observed_matrix_cell_id"} <= set(cross_fields), f"fields={len(cross_fields)}")
    check("local_ids_exact", [row["local_witness_id"] for row in local_rows] == [f"G499-L{i:04d}" for i in range(1, 647)], "L0001..L0646")
    check("cross_ids_exact", [row["cross_witness_id"] for row in cross_rows] == [f"G499-X{i:04d}" for i in range(1, 289)], "X0001..X0288")

    source_by_id = {row["matrix_cell_id"]: row for row in matrix}
    observed = [row for row in matrix if row["evidence_status"] == "OBSERVED_CLAUSE"]
    composed = [row for row in matrix if row["evidence_status"] == "COMPOSED_WORKING"]
    check("source_evidence_split_exact", (len(observed), len(composed)) == (143, 352), f"observed={len(observed)} composed={len(composed)}")
    check("ranked_source_ids_exact", {row["source_matrix_cell_id"] for row in ranked} == {row["matrix_cell_id"] for row in composed}, "all composed and only composed")

    observed_by_frame_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    observed_by_frame_action: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in observed:
        observed_by_frame_register[(row["frozen_frame"], row["register"])].append(row)
        observed_by_frame_action[(row["frozen_frame"], row["action_root"])].append(row)

    expected_local: list[dict[str, str]] = []
    expected_cross: list[dict[str, str]] = []
    ranking_keys: list[tuple[object, ...]] = []
    tier_counts: Counter[str] = Counter()
    for index, row in enumerate(ranked, start=1):
        source = source_by_id[row["source_matrix_cell_id"]]
        local = [
            item for item in observed_by_frame_register[(source["frozen_frame"], source["register"])]
            if item["action_root"] != source["action_root"]
        ]
        cross = [
            item for item in observed_by_frame_action[(source["frozen_frame"], source["action_root"])]
            if item["register"] != source["register"]
        ]
        if len(local) >= 2:
            expected_tier = "A_LOCAL_MULTIHEAD"
            expected_reason = "TWO_OR_MORE_EXACT_OTHER_ACTION_CELLS_SAME_FRAME_REGISTER"
        elif len(local) == 1:
            expected_tier = "B_LOCAL_SINGLE_HEAD"
            expected_reason = "ONE_EXACT_OTHER_ACTION_CELL_SAME_FRAME_REGISTER"
        elif cross:
            expected_tier = "C_CROSS_REGISTER_SAME_ACTION"
            expected_reason = "EXACT_SAME_ACTION_FRAME_IN_OTHER_REGISTER"
        else:
            expected_tier = "D_OLD_VALUES_ONLY"
            expected_reason = "ONLY_COMPONENT_VALUE_CELLS_OBSERVED"
        tier_counts[expected_tier] += 1
        tokens = source["action_recipe"].split("+")
        action_tokens = [token for token in tokens if token in ACTION_ROOTS]
        repeats = sorted(root for root, count in Counter(action_tokens).items() if count > 1)
        local_pages = union_pages(local)
        cross_pages = union_pages(cross)
        check(
            f"cell_{index:03d}_source_fields_exact",
            row["frozen_frame"] == source["frozen_frame"]
            and row["action_root"] == source["action_root"]
            and row["action_recipe"] == source["action_recipe"]
            and row["register"] == source["register"]
            and row["portable_component_trace_de"] == source["portable_component_trace_de"]
            and row["owner_local_component_trace_de"] == source["owner_local_component_trace_de"]
            and row["current_default_phrase_de"] == source["current_default_phrase_de"]
            and row["state_requirement"] == source["state_requirement"]
            and row["editorial_change_type"] == source["editorial_change_type"],
            source["matrix_cell_id"],
        )
        check(
            f"cell_{index:03d}_tier_and_components_exact",
            row["priority_tier"] == expected_tier
            and row["priority_reason"] == expected_reason
            and int(row["component_count"]) == len(tokens)
            and int(row["action_component_count"]) == len(action_tokens)
            and int(row["repeated_action_root_count"]) == len(repeats)
            and row["repeated_action_roots"] == ("|".join(repeats) or "NONE")
            and row["repeated_action_fluency_warning"] == ("YES" if repeats else "NO"),
            f"tier={expected_tier} repeats={repeats}",
        )
        check(
            f"cell_{index:03d}_local_support_exact",
            int(row["local_observed_head_count"]) == len(local)
            and row["local_observed_heads"] == ("|".join(item["action_root"] for item in local) or "NONE")
            and int(row["local_observed_event_count"]) == sum(int(item["observed_event_count"]) for item in local)
            and int(row["local_observed_clause_form_count"]) == sum(int(item["observed_clause_form_count"]) for item in local)
            and int(row["local_observed_page_count"]) == len(local_pages)
            and row["local_observed_pages"] == ("|".join(local_pages) or "NONE"),
            f"heads={len(local)} events={sum(int(item['observed_event_count']) for item in local)}",
        )
        check(
            f"cell_{index:03d}_cross_support_exact",
            int(row["cross_register_observed_cell_count"]) == len(cross)
            and row["cross_register_observed_registers"] == ("|".join(item["register"] for item in cross) or "NONE")
            and int(row["cross_register_observed_event_count"]) == sum(int(item["observed_event_count"]) for item in cross)
            and int(row["cross_register_observed_page_count"]) == len(cross_pages)
            and row["cross_register_observed_pages"] == ("|".join(cross_pages) or "NONE"),
            f"cells={len(cross)} events={sum(int(item['observed_event_count']) for item in cross)}",
        )
        check(
            f"cell_{index:03d}_retention_guards_exact",
            row["all_component_value_cells_old"] == source["all_component_value_cells_old"] == "YES"
            and row["evidence_status_retained"] == source["evidence_status"] == "COMPOSED_WORKING"
            and row["working_root_meaning_changed"] == "NO"
            and row["surface_prediction_made"] == "NO"
            and row["occurrence_prediction_made"] == "NO"
            and row["guard"] == GUARD,
            GUARD,
        )
        check(f"cell_{index:03d}_global_rank_exact", int(row["global_priority_rank"]) == index, f"rank={index}")
        check(f"cell_{index:03d}_tier_rank_exact", int(row["tier_rank"]) == tier_counts[expected_tier], f"tier_rank={tier_counts[expected_tier]}")
        ranking_keys.append((
            TIER_ORDER[row["priority_tier"]],
            -int(row["local_observed_head_count"]),
            -int(row["local_observed_event_count"]),
            -int(row["cross_register_observed_cell_count"]),
            -int(row["cross_register_observed_event_count"]),
            int(row["repeated_action_root_count"]),
            int(row["component_count"]),
            row["action_recipe"],
            row["register"],
        ))
        for witness in local:
            expected_local.append({
                "local_witness_id": f"G499-L{len(expected_local) + 1:04d}",
                "target_matrix_cell_id": source["matrix_cell_id"],
                "target_frame": source["frozen_frame"],
                "target_action_root": source["action_root"],
                "target_action_recipe": source["action_recipe"],
                "target_register": source["register"],
                "observed_matrix_cell_id": witness["matrix_cell_id"],
                "observed_action_root": witness["action_root"],
                "observed_action_recipe": witness["action_recipe"],
                "observed_event_count": witness["observed_event_count"],
                "observed_clause_form_count": witness["observed_clause_form_count"],
                "observed_pages": witness["observed_pages"],
                "observed_event_ids": witness["observed_event_ids"],
                "observed_selected_phrase_de": witness["current_default_phrase_de"],
                "all_observed_clause_forms_de": witness["all_observed_clause_forms_de"],
                "exact_same_frame_and_register": "YES",
            })
        for witness in cross:
            expected_cross.append({
                "cross_witness_id": f"G499-X{len(expected_cross) + 1:04d}",
                "target_matrix_cell_id": source["matrix_cell_id"],
                "target_frame": source["frozen_frame"],
                "target_action_root": source["action_root"],
                "target_action_recipe": source["action_recipe"],
                "target_register": source["register"],
                "observed_matrix_cell_id": witness["matrix_cell_id"],
                "observed_register": witness["register"],
                "observed_event_count": witness["observed_event_count"],
                "observed_clause_form_count": witness["observed_clause_form_count"],
                "observed_pages": witness["observed_pages"],
                "observed_event_ids": witness["observed_event_ids"],
                "observed_selected_phrase_de": witness["current_default_phrase_de"],
                "all_observed_clause_forms_de": witness["all_observed_clause_forms_de"],
                "exact_same_action_and_frame": "YES",
            })

    # Witness files retain GDT498 matrix order, while the atlas itself is ranked.
    # Rebuild those two files independently in their actual source order.
    expected_local = []
    expected_cross = []
    for source in composed:
        local = [
            item for item in observed_by_frame_register[(source["frozen_frame"], source["register"])]
            if item["action_root"] != source["action_root"]
        ]
        cross = [
            item for item in observed_by_frame_action[(source["frozen_frame"], source["action_root"])]
            if item["register"] != source["register"]
        ]
        for witness in local:
            expected_local.append({
                "local_witness_id": f"G499-L{len(expected_local) + 1:04d}",
                "target_matrix_cell_id": source["matrix_cell_id"],
                "target_frame": source["frozen_frame"],
                "target_action_root": source["action_root"],
                "target_action_recipe": source["action_recipe"],
                "target_register": source["register"],
                "observed_matrix_cell_id": witness["matrix_cell_id"],
                "observed_action_root": witness["action_root"],
                "observed_action_recipe": witness["action_recipe"],
                "observed_event_count": witness["observed_event_count"],
                "observed_clause_form_count": witness["observed_clause_form_count"],
                "observed_pages": witness["observed_pages"],
                "observed_event_ids": witness["observed_event_ids"],
                "observed_selected_phrase_de": witness["current_default_phrase_de"],
                "all_observed_clause_forms_de": witness["all_observed_clause_forms_de"],
                "exact_same_frame_and_register": "YES",
            })
        for witness in cross:
            expected_cross.append({
                "cross_witness_id": f"G499-X{len(expected_cross) + 1:04d}",
                "target_matrix_cell_id": source["matrix_cell_id"],
                "target_frame": source["frozen_frame"],
                "target_action_root": source["action_root"],
                "target_action_recipe": source["action_recipe"],
                "target_register": source["register"],
                "observed_matrix_cell_id": witness["matrix_cell_id"],
                "observed_register": witness["register"],
                "observed_event_count": witness["observed_event_count"],
                "observed_clause_form_count": witness["observed_clause_form_count"],
                "observed_pages": witness["observed_pages"],
                "observed_event_ids": witness["observed_event_ids"],
                "observed_selected_phrase_de": witness["current_default_phrase_de"],
                "all_observed_clause_forms_de": witness["all_observed_clause_forms_de"],
                "exact_same_action_and_frame": "YES",
            })

    check("global_ranking_order_exact", ranking_keys == sorted(ranking_keys), "predeclared lexicographic order")
    check("tier_counts_exact", tier_counts == Counter({"A_LOCAL_MULTIHEAD": 165, "B_LOCAL_SINGLE_HEAD": 88, "C_CROSS_REGISTER_SAME_ACTION": 49, "D_OLD_VALUES_ONLY": 50}), str(tier_counts))
    check("tier_a_subset_exact", tier_a == [row for row in ranked if row["priority_tier"] == "A_LOCAL_MULTIHEAD"], "165 rows")
    check("tier_b_subset_exact", tier_b == [row for row in ranked if row["priority_tier"] == "B_LOCAL_SINGLE_HEAD"], "88 rows")
    check("tier_c_subset_exact", tier_c == [row for row in ranked if row["priority_tier"] == "C_CROSS_REGISTER_SAME_ACTION"], "49 rows")
    check("tier_d_subset_exact", tier_d == [row for row in ranked if row["priority_tier"] == "D_OLD_VALUES_ONLY"], "50 rows")
    check("repeated_subset_exact", repeated == [row for row in ranked if row["repeated_action_fluency_warning"] == "YES"], "15 rows")
    check("local_witness_rows_exact", local_rows == expected_local, f"rows={len(expected_local)}")
    check("cross_witness_rows_exact", cross_rows == expected_cross, f"rows={len(expected_cross)}")

    def expected_summary(axis: str) -> list[dict[str, str]]:
        output: list[dict[str, str]] = []
        for value in sorted({row[axis] for row in ranked}):
            group = [row for row in ranked if row[axis] == value]
            tiers = Counter(row["priority_tier"] for row in group)
            output.append({
                axis: value,
                "composed_cell_count": str(len(group)),
                "tier_a_multihead_count": str(tiers["A_LOCAL_MULTIHEAD"]),
                "tier_b_single_head_count": str(tiers["B_LOCAL_SINGLE_HEAD"]),
                "tier_c_cross_register_count": str(tiers["C_CROSS_REGISTER_SAME_ACTION"]),
                "tier_d_old_values_only_count": str(tiers["D_OLD_VALUES_ONLY"]),
                "local_witness_cell_count": str(sum(int(row["local_observed_head_count"]) for row in group)),
                "local_witness_event_count": str(sum(int(row["local_observed_event_count"]) for row in group)),
                "cross_witness_cell_count": str(sum(int(row["cross_register_observed_cell_count"]) for row in group)),
                "cross_witness_event_count": str(sum(int(row["cross_register_observed_event_count"]) for row in group)),
                "repeated_action_warning_count": str(sum(row["repeated_action_fluency_warning"] == "YES" for row in group)),
                "all_composed_labels_retained": "YES",
            })
        return output

    check("frame_summary_exact", frame_rows == expected_summary("frozen_frame"), "11 rows")
    check("action_summary_exact", action_rows == expected_summary("action_root"), "9 rows")
    check("readable_status_exact", STATUS in readable and GUARD in readable, "status and guard present")
    check("readable_all_ranked_rows_present", all(row["current_default_phrase_de"] in readable for row in ranked), "352 defaults")

    expected_result = {
        "status": STATUS,
        "ranked_compositions": 352,
        "tier_a_local_multihead": 165,
        "tier_b_local_single_head": 88,
        "tier_c_cross_register_same_action": 49,
        "tier_d_old_values_only": 50,
        "local_observed_support_witnesses": len(local_rows),
        "local_observed_support_events": sum(int(row["observed_event_count"]) for row in local_rows),
        "cross_register_observed_support_witnesses": len(cross_rows),
        "cross_register_observed_support_events": sum(int(row["observed_event_count"]) for row in cross_rows),
        "tier_a_local_support_witnesses": sum(int(row["local_observed_head_count"]) for row in tier_a),
        "tier_a_local_support_events": sum(int(row["local_observed_event_count"]) for row in tier_a),
        "repeated_action_compositions": len(repeated),
        "repeated_action_tier_a": sum(row["priority_tier"] == "A_LOCAL_MULTIHEAD" for row in repeated),
        "repeated_action_tier_d": sum(row["priority_tier"] == "D_OLD_VALUES_ONLY" for row in repeated),
        "all_old_value_cells_retained": sum(row["all_component_value_cells_old"] == "YES" for row in ranked),
        "composed_labels_retained": sum(row["evidence_status_retained"] == "COMPOSED_WORKING" for row in ranked),
        "working_root_meaning_changes": sum(row["working_root_meaning_changed"] == "YES" for row in ranked),
        "surface_predictions": sum(row["surface_prediction_made"] == "YES" for row in ranked),
        "occurrence_predictions": sum(row["occurrence_prediction_made"] == "YES" for row in ranked),
        "frame_count": 11,
        "action_count": 9,
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
