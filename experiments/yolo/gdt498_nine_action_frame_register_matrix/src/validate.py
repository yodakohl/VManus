#!/usr/bin/env python3
"""Validate the complete 495-cell GDT498 action/frame/register matrix."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt498_nine_action_frame_register_matrix"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler"
G415 = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
G493 = ROOT / "experiments/yolo/gdt493_owner_dependent_tr_realization_deck/artifacts"
G497 = ROOT / "experiments/yolo/gdt497_complete_context_safe_tr_default_deck/artifacts"

CLAUSES_IN = G416 / "artifacts/gdt416_4576_imperative_clauses.tsv"
COMPILER_IN = G416 / "src/run.py"
VALUES_IN = G415 / "gdt415_95_register_expansion_atlas.tsv"
FRAMES_IN = G493 / "gdt493_11_frame_coverage.tsv"
FRAME_VALUES_IN = G493 / "gdt493_55_observed_register_value_cells.tsv"
TR_DEFAULTS_IN = G497 / "gdt497_110_current_default_cells.tsv"
MATRIX_OUT = ART / "gdt498_495_action_frame_register_cells.tsv"
OBSERVED_OUT = ART / "gdt498_observed_cells.tsv"
COMPOSED_OUT = ART / "gdt498_composed_cells.tsv"
ACTION_OUT = ART / "gdt498_9_action_coverage.tsv"
FRAME_OUT = ART / "gdt498_11_frame_coverage.tsv"
REGISTER_OUT = ART / "gdt498_5_register_coverage.tsv"
ACTION_FRAME_OUT = ART / "gdt498_99_action_frame_coverage.tsv"
FRAME_REGISTER_OUT = ART / "gdt498_55_frame_register_head_coverage.tsv"
READABLE_OUT = ART / "GDT498_NINE_ACTION_FRAME_REGISTER_MATRIX.md"
RESULT_OUT = ART / "gdt498_result.json"
VALIDATION_OUT = ART / "gdt498_validation.json"

ACTION_ORDER = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
REGISTER_ORDER = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
STATUS = "ALL_FOUR_HUNDRED_NINETY_FIVE_CELLS_READABLE__ZERO_UNAVAILABLE__OBSERVED_AND_COMPOSED_VISIBLE"
GUARD = "WORKING_MEANING_MATRIX__NO_SURFACE_OR_OCCURRENCE_PREDICTION"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def load_compiler() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gdt416_compiler_validation", COMPILER_IN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT416 compiler")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_phrase(rows: list[dict[str, str]]) -> tuple[str, int]:
    counts = Counter(row["imperative_clause_de"] for row in rows)
    return sorted(counts.items(), key=lambda item: (-item[1], len(item[0].split()), len(item[0]), item[0]))[0]


def context_generalize(phrase: str, frame: str) -> tuple[str, int, str]:
    pattern = r"\b(?:den|die|das) [^.;]+? \[wie zuvor\]"
    expected = 2 if frame == "CH+@ACTION" else 1
    matches = list(re.finditer(pattern, phrase))
    if len(matches) != expected:
        raise ValueError(f"state phrase noun count drift: {frame} {phrase}")
    index = 0

    def replace(_match: re.Match[str]) -> str:
        nonlocal index
        index += 1
        return "das zuvor Genannte" if index == 1 else "es"

    output = re.sub(pattern, replace, phrase)
    change = "CONTEXT_NOUN_GENERALIZED"
    if frame == "@ACTION+OL":
        body = output.removeprefix("Weiter ")
        if body == output:
            raise ValueError("OL phrase lost Weiter")
        output = "Fahre fort: " + body[0].upper() + body[1:]
        change = "CONTEXT_NOUN_GENERALIZED__FORTSETZEN_COLON"
    return output, expected, change


def main() -> int:
    compiler = load_compiler()
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _value_fields, values = read_tsv(VALUES_IN)
    _frame_fields, frames = read_tsv(FRAMES_IN)
    _frame_value_fields, frame_values = read_tsv(FRAME_VALUES_IN)
    _tr_fields, tr_defaults = read_tsv(TR_DEFAULTS_IN)
    matrix_fields, matrix = read_tsv(MATRIX_OUT)
    observed_fields, observed = read_tsv(OBSERVED_OUT)
    composed_fields, composed = read_tsv(COMPOSED_OUT)
    _action_fields, actions = read_tsv(ACTION_OUT)
    _frame_out_fields, frame_summary = read_tsv(FRAME_OUT)
    _register_fields, registers = read_tsv(REGISTER_OUT)
    _action_frame_fields, action_frames = read_tsv(ACTION_FRAME_OUT)
    _frame_register_fields, frame_registers = read_tsv(FRAME_REGISTER_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    expected_counts = (4576, 95, 11, 55, 110, 495, 143, 352, 9, 11, 5, 99, 55)
    actual_counts = (len(clauses), len(values), len(frames), len(frame_values), len(tr_defaults), len(matrix), len(observed), len(composed), len(actions), len(frame_summary), len(registers), len(action_frames), len(frame_registers))
    check("all_table_counts_exact", actual_counts == expected_counts, f"actual={actual_counts}")
    check("matrix_ids_exact", [row["matrix_cell_id"] for row in matrix] == [f"G498-M{i:03d}" for i in range(1, 496)], "M001..M495")
    check("action_frame_ids_exact", [row["action_frame_id"] for row in action_frames] == [f"G498-AF{i:03d}" for i in range(1, 100)], "AF001..AF099")
    check("frame_register_ids_exact", [row["frame_register_id"] for row in frame_registers] == [f"G498-FR{i:02d}" for i in range(1, 56)], "FR01..FR55")
    check("observed_subset_schema_exact", observed_fields == matrix_fields, "same schema")
    check("composed_subset_schema_exact", composed_fields == matrix_fields, "same schema")
    required = {
        "portable_component_trace_de",
        "owner_local_component_trace_de",
        "current_default_phrase_de",
        "composition_support_class",
        "same_frame_register_observed_other_actions",
        "same_action_frame_observed_other_registers",
    }
    check("matrix_schema_complete", required <= set(matrix_fields), f"fields={len(matrix_fields)}")

    value_by_key = {(row["root"], row["register"]): row for row in values}
    for row in frame_values:
        key = (row["root"], row["register"])
        if key in value_by_key:
            check(
                f"overlap_value_{row['root']}_{row['register']}",
                value_by_key[key]["portable_default_de"] == row["portable_default_de"]
                and value_by_key[key]["owner_local_expansion_de"] == row["owner_local_expansion_de"],
                str(key),
            )
        else:
            value_by_key[key] = row

    clauses_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_key[(row["component_recipe"], row["register"])].append(row)
    tr_by_key = {(row["frozen_frame"], row["action_root"], row["register"]): row for row in tr_defaults}
    matrix_by_key = {(row["frozen_frame"], row["action_root"], row["register"]): row for row in matrix}
    check("matrix_unique_495_keys", len(matrix_by_key) == 495, f"keys={len(matrix_by_key)}")
    expected_keys = {
        (frame["frozen_frame"], action, register)
        for frame in frames for action in ACTION_ORDER for register in REGISTER_ORDER
    }
    check("matrix_cartesian_key_coverage", set(matrix_by_key) == expected_keys, "11x9x5 exact")

    for index, row in enumerate(matrix, start=1):
        atoms = row["action_recipe"].split("+")
        value_cells = [value_by_key[(atom, row["register"])] for atom in atoms]
        source_clauses = clauses_by_key[(row["action_recipe"], row["register"])]
        selected_phrase, selected_count = select_phrase(source_clauses) if source_clauses else ("NONE", 0)
        expected_evidence = "OBSERVED_CLAUSE" if source_clauses else "COMPOSED_WORKING"
        check(
            f"cell_{index:03d}_formal_and_value_trace_exact",
            row["action_recipe"] == row["frozen_frame"].replace("@ACTION", row["action_root"])
            and row["portable_component_trace_de"] == " · ".join(cell["portable_default_de"] for cell in value_cells)
            and row["owner_local_component_trace_de"] == " · ".join(cell["owner_local_expansion_de"] for cell in value_cells)
            and row["availability_status"] == "READABLE"
            and row["missing_owner_value_atoms"] == "NONE"
            and row["all_component_value_cells_old"] == "YES",
            f"{row['frozen_frame']} {row['action_root']} {row['register']}",
        )
        check(
            f"cell_{index:03d}_observation_inventory_exact",
            row["evidence_status"] == expected_evidence
            and int(row["observed_event_count"]) == len(source_clauses)
            and int(row["observed_clause_form_count"]) == len({item["imperative_clause_de"] for item in source_clauses})
            and int(row["selected_observed_phrase_carrier_count"]) == selected_count
            and row["selected_observed_phrase_de"] == selected_phrase
            and row["observed_event_ids"] == ("|".join(item["global_running_event_id"] for item in source_clauses) or "NONE"),
            f"events={len(source_clauses)} forms={len({item['imperative_clause_de'] for item in source_clauses})}",
        )

        if row["action_root"] in {"T", "R"}:
            inherited = tr_by_key[(row["frozen_frame"], row["action_root"], row["register"])]
            expected_phrase = inherited["current_default_phrase_de"]
            expected_policy = "GDT497_CURRENT_DEFAULT_INHERITED"
            expected_change = inherited["editorial_change_type"]
            expected_nouns = inherited["generalized_inherited_noun_count"]
        elif source_clauses:
            expected_phrase = selected_phrase
            expected_policy = "SELECTED_OBSERVED_CLAUSE"
            expected_change = "UNCHANGED_OBSERVED"
            expected_nouns = "0"
        else:
            explicit_actions = [atom for atom in atoms if atom in compiler.ACTION_ROOTS]
            explicit_arguments = [atom for atom in atoms if atom in compiler.ARGUMENT_ROOTS]
            rendered = compiler.render_clause(
                row["register"], atoms, explicit_actions, "",
                "Y" if row["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED" else "",
            )
            if row["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED":
                expected_phrase, noun_count, expected_change = context_generalize(rendered, row["frozen_frame"])
                expected_nouns = str(noun_count)
            else:
                expected_phrase = rendered
                expected_nouns = "0"
                expected_change = "UNCHANGED_SELF_CONTAINED_RENDERER"
            expected_policy = "GDT416_RENDERER_PLUS_OLD_REGISTER_VALUES"
        check(
            f"cell_{index:03d}_default_exact",
            row["current_default_phrase_de"] == expected_phrase
            and row["current_default_policy"] == expected_policy
            and row["editorial_change_type"] == expected_change
            and row["generalized_inherited_noun_count"] == expected_nouns,
            expected_phrase,
        )
        check(
            f"cell_{index:03d}_integrity_guards",
            row["working_root_meaning_changed"] == "NO"
            and row["surface_prediction_made"] == "NO"
            and row["occurrence_prediction_made"] == "NO"
            and row["guard"] == GUARD,
            row["matrix_cell_id"],
        )
        check(
            f"cell_{index:03d}_readable_present",
            row["matrix_cell_id"] in readable and row["current_default_phrase_de"] in readable,
            row["matrix_cell_id"],
        )

    expected_observed = [row for row in matrix if row["evidence_status"] == "OBSERVED_CLAUSE"]
    expected_composed = [row for row in matrix if row["evidence_status"] == "COMPOSED_WORKING"]
    check("observed_subset_exact", observed == expected_observed, "143 rows in matrix order")
    check("composed_subset_exact", composed == expected_composed, "352 rows in matrix order")
    check("zero_unavailable", all(row["availability_status"] == "READABLE" for row in matrix), "495/495")

    by_frame_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    by_frame_action: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in matrix:
        by_frame_register[(row["frozen_frame"], row["register"])].append(row)
        by_frame_action[(row["frozen_frame"], row["action_root"])].append(row)
    for index, row in enumerate(matrix, start=1):
        local = [cell for cell in by_frame_register[(row["frozen_frame"], row["register"])] if cell["action_root"] != row["action_root"] and cell["evidence_status"] == "OBSERVED_CLAUSE"]
        cross = [cell for cell in by_frame_action[(row["frozen_frame"], row["action_root"])] if cell["register"] != row["register"] and cell["evidence_status"] == "OBSERVED_CLAUSE"]
        if row["evidence_status"] == "OBSERVED_CLAUSE":
            expected_class = "OBSERVED_EXACT_CELL"
        elif len(local) >= 2:
            expected_class = "COMPOSED_MULTIHEAD_SAME_REGISTER"
        elif len(local) == 1:
            expected_class = "COMPOSED_SINGLE_HEAD_SAME_REGISTER"
        elif cross:
            expected_class = "COMPOSED_CROSS_REGISTER_SAME_ACTION"
        else:
            expected_class = "COMPOSED_OLD_VALUES_ONLY"
        check(
            f"support_{index:03d}_exact",
            int(row["same_frame_register_observed_other_action_count"]) == len(local)
            and row["same_frame_register_observed_other_actions"] == ("|".join(cell["action_root"] for cell in local) or "NONE")
            and int(row["same_action_frame_observed_other_register_count"]) == len(cross)
            and row["same_action_frame_observed_other_registers"] == ("|".join(cell["register"] for cell in cross) or "NONE")
            and row["composition_support_class"] == expected_class,
            expected_class,
        )

    def check_axis(label: str, rows: list[dict[str, str]], axis: str, expected_values: list[str]) -> None:
        check(f"{label}_values_exact", [row[axis] for row in rows] == expected_values, str(expected_values))
        check(f"{label}_cells_sum_495", sum(int(row["matrix_cell_count"]) for row in rows) == 495, "sum=495")
        check(f"{label}_observed_sum_143", sum(int(row["observed_cell_count"]) for row in rows) == 143, "sum=143")
        check(f"{label}_composed_sum_352", sum(int(row["composed_cell_count"]) for row in rows) == 352, "sum=352")
        check(f"{label}_unavailable_zero", sum(int(row["unavailable_cell_count"]) for row in rows) == 0, "sum=0")
        check(f"{label}_all_readable_old", all(row["all_value_cells_old"] == row["all_defaults_readable"] == "YES" for row in rows), f"{len(rows)}/{len(rows)}")

    check_axis("action", actions, "action_root", list(ACTION_ORDER))
    check_axis("frame", frame_summary, "frozen_frame", sorted(row["frozen_frame"] for row in frames))
    check_axis("register", registers, "register", list(REGISTER_ORDER))
    check("action_frame_every_five", all(row["register_cell_count"] == "5" and row["all_five_registers_readable"] == row["all_owner_value_cells_old"] == "YES" for row in action_frames), "99/99")
    check("action_frame_totals", sum(int(row["observed_register_cell_count"]) for row in action_frames) == 143 and sum(int(row["composed_register_cell_count"]) for row in action_frames) == 352, "143/352")
    check("frame_register_every_nine", all(row["action_cell_count"] == "9" and row["all_nine_actions_readable"] == row["all_owner_value_cells_old"] == "YES" for row in frame_registers), "55/55")
    check("frame_register_totals", sum(int(row["observed_action_head_count"]) for row in frame_registers) == 143 and sum(int(row["composed_action_cell_count"]) for row in frame_registers) == 352, "143/352")
    check("readable_has_495_matrix_rows", len(re.findall(r"^\| G498-M\d{3} \|", readable, flags=re.MULTILINE)) == 495, "495 rows")
    check("readable_has_99_action_frame_rows", len(re.findall(r"^\| `@?[^|]+` \| (?:OK|CH|SH|K|S|CHD|T|R|P) \|", readable, flags=re.MULTILINE)) == 99, "99 rows")
    check("readable_guard_present", f"`{GUARD}`" in readable, GUARD)
    check("readable_no_f84", "f84" not in readable.lower(), "sealed folio absent")

    support_counts = Counter(row["composition_support_class"] for row in matrix)
    tr_matrix = [row for row in matrix if row["action_root"] in {"T", "R"}]
    expected_result = {
        "status": STATUS,
        "matrix_cells": 495,
        "action_count": 9,
        "frame_count": 11,
        "register_count": 5,
        "action_frame_cells": 99,
        "frame_register_cells": 55,
        "observed_cells": 143,
        "composed_cells": 352,
        "unavailable_cells": 0,
        "observed_events": sum(int(row["observed_event_count"]) for row in observed),
        "multihead_same_register_compositions": support_counts["COMPOSED_MULTIHEAD_SAME_REGISTER"],
        "single_head_same_register_compositions": support_counts["COMPOSED_SINGLE_HEAD_SAME_REGISTER"],
        "cross_register_same_action_compositions": support_counts["COMPOSED_CROSS_REGISTER_SAME_ACTION"],
        "old_values_only_compositions": support_counts["COMPOSED_OLD_VALUES_ONLY"],
        "context_generalized_cells": sum(int(row["generalized_inherited_noun_count"]) > 0 for row in matrix),
        "inherited_noun_occurrences_generalized": sum(int(row["generalized_inherited_noun_count"]) for row in matrix),
        "tr_cells": len(tr_matrix),
        "tr_current_default_exact_matches": sum(row["current_default_phrase_de"] == tr_by_key[(row["frozen_frame"], row["action_root"], row["register"])]["current_default_phrase_de"] for row in tr_matrix),
        "all_value_cells_old": sum(row["all_component_value_cells_old"] == "YES" for row in matrix),
        "working_root_meaning_changes": sum(row["working_root_meaning_changed"] == "YES" for row in matrix),
        "surface_predictions": sum(row["surface_prediction_made"] == "YES" for row in matrix),
        "occurrence_predictions": sum(row["occurrence_prediction_made"] == "YES" for row in matrix),
        "guard": GUARD,
    }
    check("result_exact", result == expected_result, "result JSON reconstructed")
    check("result_observed_events_660", result["observed_events"] == 660, f"events={result['observed_events']}")
    check("result_support_partition_352", sum(result[key] for key in ("multihead_same_register_compositions", "single_head_same_register_compositions", "cross_register_same_action_compositions", "old_values_only_compositions")) == 352, "composed support partition")
    check("result_110_tr_exact", result["tr_cells"] == result["tr_current_default_exact_matches"] == 110, "110/110")
    check("result_495_old_values", result["all_value_cells_old"] == 495, "495/495")
    check("result_zero_changes_predictions", result["working_root_meaning_changes"] == result["surface_predictions"] == result["occurrence_predictions"] == 0, "all zero")

    failed = [entry for entry in checks if not entry["passed"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [entry["name"] for entry in failed],
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total", "failed_checks")}, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
