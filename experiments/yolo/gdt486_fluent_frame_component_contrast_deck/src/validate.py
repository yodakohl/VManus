#!/usr/bin/env python3
"""Validate GDT486's fluent-frame one-component contrast deck."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt486_fluent_frame_component_contrast_deck"
OUT = BASE / "artifacts"
G485 = ROOT / "experiments/yolo/gdt485_fluent_reversible_microrecord_edition/artifacts"
RUN = BASE / "src/run.py"
RECORDS_IN = G485 / "gdt485_135_fluent_reversible_records.tsv"
EVENTS_IN = G485 / "gdt485_183_literal_backprojection_events.tsv"
FRAME_ASSIGNMENTS = OUT / "gdt486_135_fluent_frame_assignments.tsv"
REGISTER_PAIRS = OUT / "gdt486_48_register_minimal_pairs.tsv"
SAME_PAGE_PAIRS = OUT / "gdt486_33_same_page_minimal_pairs.tsv"
REGISTER_EXTENSION = OUT / "gdt486_15_cross_page_register_extension_pairs.tsv"
CONTRAST_RULES = OUT / "gdt486_29_model_conditioned_contrast_rules.tsv"
CONTEXT_VARIANTS = OUT / "gdt486_1_contextual_realization_explanation.tsv"
PAGE_CAPACITY = OUT / "gdt486_6_page_capacity_summary.tsv"
READABLE = OUT / "GDT486_FLUENT_COMPONENT_CONTRAST_DECK.md"
RESULT = OUT / "gdt486_result.json"
VALIDATION = OUT / "gdt486_validation.json"
STATUS = "TWENTY_NINE_FLUENT_COMPONENT_CONTRASTS__ONE_CONTEXTUAL_VARIANT__ZERO_DICTIONARY_PRESSURE"
EXPECTED_CHANGED_VALUES = {
    "ANTEIL", "AUSGANG", "BAHN", "DANACH", "EINHEIT", "EINSTELLEN",
    "FORTSETZEN", "HALTEN", "HIER", "POSTEN", "SCHLUSS", "WERT", "ZIELORT",
}
EXPECTED_ACTION_VALUES = {"EINSTELLEN", "FORTSETZEN", "HALTEN"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [FRAME_ASSIGNMENTS, REGISTER_PAIRS, SAME_PAGE_PAIRS, REGISTER_EXTENSION, CONTRAST_RULES, CONTEXT_VARIANTS, PAGE_CAPACITY, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT486 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    source_records = read_tsv(RECORDS_IN)
    source_events = read_tsv(EVENTS_IN)
    assignments = read_tsv(FRAME_ASSIGNMENTS)
    pairs = read_tsv(REGISTER_PAIRS)
    same_pairs = read_tsv(SAME_PAGE_PAIRS)
    extension = read_tsv(REGISTER_EXTENSION)
    rules = read_tsv(CONTRAST_RULES)
    contexts = read_tsv(CONTEXT_VARIANTS)
    pages = read_tsv(PAGE_CAPACITY)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("source_record_count_135", len(source_records) == 135, len(source_records))
    check("source_event_count_183", len(source_events) == 183, len(source_events))
    check("assignment_count_135", len(assignments) == 135, len(assignments))
    check("register_pair_count_48", len(pairs) == 48, len(pairs))
    check("same_page_pair_count_33", len(same_pairs) == 33, len(same_pairs))
    check("extension_pair_count_15", len(extension) == 15, len(extension))
    check("rule_count_29", len(rules) == 29, len(rules))
    check("context_count_1", len(contexts) == 1, len(contexts))
    check("page_count_6", len(pages) == 6, len(pages))

    source_record_map = {row["record_id"]: row for row in source_records}
    assignment_map = {row["record_id"]: row for row in assignments}
    pair_map = {row["pair_id"]: row for row in pairs}
    rule_map = {row["rule_id"]: row for row in rules}
    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_events:
        events_by_record[row["record_id"]].append(row)
    check("assignment_record_keys_exact", set(assignment_map) == set(source_record_map))
    check("assignment_record_ids_unique", len(assignment_map) == len(assignments))
    check("pair_ids_unique", len(pair_map) == len(pairs))
    check("rule_ids_unique", len(rule_map) == len(rules))
    check("strict_pair_ids_unique", len({row["strict_pair_id"] for row in same_pairs}) == 33)
    check("extension_pair_ids_unique", len({row["extension_pair_id"] for row in extension}) == 15)

    assignment_fields = ("physical_page", "register", "surface_sequence", "active_model_sequence", "fluent_reading_de")
    check("assignment_source_fields_exact", all(all(row[field] == source_record_map[row["record_id"]][field] for field in assignment_fields) for row in assignments))
    check("assignment_component_traces_exact", all(row["component_trace_de"] == source_record_map[row["record_id"]]["normalized_component_trace_de"] for row in assignments))
    check("assignment_source_flags_yes", all(row["source_record_preserved"] == "YES" for row in assignments))
    check("assignment_frame_classes_nonempty", all(row["fluent_frame_class"] for row in assignments))
    check("assignment_frame_class_count_20", len({row["fluent_frame_class"] for row in assignments}) == 20)
    check("assignment_structural_frame_count_54", len({row["structural_frame_id"] for row in assignments}) == 54)
    check("assignment_component_counts_nonnegative", all(int(row["functional_component_count"]) >= 0 and int(row["opaque_slot_count"]) >= 0 for row in assignments))
    check("only_family_name_record_has_zero_functional", {row["record_id"] for row in assignments if int(row["functional_component_count"]) == 0} == {"G475-R101"})
    check("assignment_contrast_covered_exact", all((int(row["register_pair_degree"]) > 0) == (row["contrast_covered"] == "YES") for row in assignments))
    check("assignment_covered_record_count_47", sum(row["contrast_covered"] == "YES" for row in assignments) == 47)
    check("assignment_register_degree_total_96", sum(int(row["register_pair_degree"]) for row in assignments) == 96)
    check("assignment_same_page_degree_total_66", sum(int(row["same_page_pair_degree"]) for row in assignments) == 66)

    def flat_tokens(record_id: str) -> list[str]:
        return [token for event in events_by_record[record_id] for token in event["semantic_tokens"].split("|")]

    check("pair_record_keys_valid", all(row["source_record_id"] in source_record_map and row["target_record_id"] in source_record_map for row in pairs))
    check("pair_source_target_distinct", all(row["source_record_id"] != row["target_record_id"] for row in pairs))
    check("pair_registers_exact", all(source_record_map[row["source_record_id"]]["register"] == source_record_map[row["target_record_id"]]["register"] == row["register"] for row in pairs))
    check("pair_active_models_exact", all(source_record_map[row["source_record_id"]]["active_model_sequence"] == source_record_map[row["target_record_id"]]["active_model_sequence"] == row["active_model_sequence"] for row in pairs))
    check("pair_frame_classes_exact", all(assignment_map[row["source_record_id"]]["fluent_frame_class"] == assignment_map[row["target_record_id"]]["fluent_frame_class"] == row["fluent_frame_class"] for row in pairs))
    check("pair_event_shapes_exact", all(assignment_map[row["source_record_id"]]["event_boundary_shape"] == assignment_map[row["target_record_id"]]["event_boundary_shape"] for row in pairs))
    check("pair_single_component_delta_exact", all(sum(a != b for a, b in zip(flat_tokens(row["source_record_id"]), flat_tokens(row["target_record_id"]))) == 1 for row in pairs))
    check("pair_component_vectors_same_length", all(len(flat_tokens(row["source_record_id"])) == len(flat_tokens(row["target_record_id"])) for row in pairs))
    check("pair_changed_ordinals_exact", all(flat_tokens(row["source_record_id"])[int(row["changed_flat_component_ordinal"]) - 1] == row["component_a"] and flat_tokens(row["target_record_id"])[int(row["changed_flat_component_ordinal"]) - 1] == row["component_b"] for row in pairs))
    check("pair_components_canonical_order", all(row["component_a"] < row["component_b"] for row in pairs))
    check("pair_components_functional", all(not row["component_a"].startswith("{") and not row["component_b"].startswith("{") for row in pairs))
    check("pair_changed_values_exact", {row[field] for row in pairs for field in ("component_a", "component_b")} == EXPECTED_CHANGED_VALUES)
    check("pair_source_fields_exact", all(row["source_surface_sequence"] == source_record_map[row["source_record_id"]]["surface_sequence"] and row["target_surface_sequence"] == source_record_map[row["target_record_id"]]["surface_sequence"] and row["source_component_trace_de"] == source_record_map[row["source_record_id"]]["normalized_component_trace_de"] and row["target_component_trace_de"] == source_record_map[row["target_record_id"]]["normalized_component_trace_de"] for row in pairs))
    check("pair_fluent_readings_exact", all(row["source_fluent_reading_de"] == source_record_map[row["source_record_id"]]["fluent_reading_de"] and row["target_fluent_reading_de"] == source_record_map[row["target_record_id"]]["fluent_reading_de"] for row in pairs))
    check("pair_support_tiers_exact", all(row["source_support_tier"] == source_record_map[row["source_record_id"]]["support_tier"] and row["target_support_tier"] == source_record_map[row["target_record_id"]]["support_tier"] for row in pairs))
    check("pair_scope_class_exact", all((row["source_physical_page"] == row["target_physical_page"]) == (row["scope_class"] == "SAME_PAGE_OWNER") for row in pairs))
    check("pair_scope_profile_exact", Counter(row["scope_class"] for row in pairs) == Counter({"SAME_PAGE_OWNER": 33, "SAME_REGISTER_CROSS_PAGE": 15}))
    check("pair_preservation_flags_yes", all(row["same_register"] == row["same_active_model"] == row["same_readable_frame_class"] == row["same_event_boundary_shape"] == row["single_functional_component_delta"] == "YES" for row in pairs))
    check("pair_meaning_cues_all_visible", all(row["component_a_cue_visible"] == row["component_b_cue_visible"] == row["meaning_change_visible"] == "YES" for row in pairs))
    check("pair_edit_signatures_nonempty", all(row["phrase_change_signature_de"] and int(row["phrase_edit_block_count"]) > 0 for row in pairs))
    check("pair_edit_block_profile_exact", Counter(row["phrase_edit_block_count"] for row in pairs) == Counter({"1": 29, "2": 19}))
    check("pair_frame_ids_nonempty", all(row["contrast_frame_id"].startswith("G486-CF") and row["wildcard_component_frame"].count("*") == 1 for row in pairs))

    same_pair_ids = {row["pair_id"] for row in pairs if row["scope_class"] == "SAME_PAGE_OWNER"}
    extension_pair_ids = {row["pair_id"] for row in pairs if row["scope_class"] == "SAME_REGISTER_CROSS_PAGE"}
    check("same_page_subset_exact", {row["pair_id"] for row in same_pairs} == same_pair_ids)
    check("extension_subset_exact", {row["pair_id"] for row in extension} == extension_pair_ids)
    common_pair_fields = tuple(pairs[0])
    check("same_page_rows_copy_full_pairs", all(all(row[field] == pair_map[row["pair_id"]][field] for field in common_pair_fields) for row in same_pairs))
    check("extension_rows_copy_full_pairs", all(all(row[field] == pair_map[row["pair_id"]][field] for field in common_pair_fields) for row in extension))
    check("same_page_record_count_32", len({row[field] for row in same_pairs for field in ("source_record_id", "target_record_id")}) == 32)
    check("register_pair_record_count_47", len({row[field] for row in pairs for field in ("source_record_id", "target_record_id")}) == 47)

    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in pairs:
        grouped[(row["active_model_sequence"], row["fluent_frame_class"], row["component_a"], row["component_b"])].append(row)
    check("rule_group_keys_exact", set(grouped) == {(row["active_model_sequence"], row["fluent_frame_class"], row["component_a"], row["component_b"]) for row in rules})
    check("rule_pair_counts_exact", all(int(row["pair_count"]) == len(grouped[(row["active_model_sequence"], row["fluent_frame_class"], row["component_a"], row["component_b"])]) for row in rules))
    check("rule_signature_counts_exact", all(int(row["phrase_signature_count"]) == len({pair["phrase_change_signature_de"] for pair in grouped[(row["active_model_sequence"], row["fluent_frame_class"], row["component_a"], row["component_b"])]}) for row in rules))
    check("rule_pair_ids_exact", all(set(row["pair_ids"].split("|")) == {pair["pair_id"] for pair in grouped[(row["active_model_sequence"], row["fluent_frame_class"], row["component_a"], row["component_b"])]} for row in rules))
    check("rule_pair_partition_total_48", sum(int(row["pair_count"]) for row in rules) == 48)
    check("rule_recurrence_profile_exact", Counter("RECURRENT" if int(row["pair_count"]) > 1 else "SINGLE" for row in rules) == Counter({"RECURRENT": 13, "SINGLE": 16}))
    check("rule_status_profile_exact", Counter(row["rule_status"] for row in rules) == Counter({"EXACT_RECURRENT_WORDING_RULE": 12, "SINGLE_WITNESS_WORDING_RULE": 16, "CONTEXTUAL_GERMAN_REALIZATION": 1}))
    check("rule_exact_signature_count_28", sum(int(row["phrase_signature_count"]) == 1 for row in rules) == 28)
    check("rule_all_meaning_cues_yes", all(row["all_meaning_cues_visible"] == "YES" for row in rules))
    check("rule_zero_dictionary_pressure", all(row["dictionary_remap_required"] == "NO" and row["rule_status"] != "DICTIONARY_PRESSURE" for row in rules))
    contextual_rule = next(row for row in rules if row["rule_status"] == "CONTEXTUAL_GERMAN_REALIZATION")
    check("contextual_rule_exact_key", (contextual_rule["active_model_sequence"], contextual_rule["fluent_frame_class"], contextual_rule["component_a"], contextual_rule["component_b"]) == ("CATALOGUE", "CATALOGUE_ENTRY", "POSTEN", "ZIELORT"))
    check("contextual_rule_counts_exact", (int(contextual_rule["pair_count"]), int(contextual_rule["phrase_signature_count"])) == (5, 2))
    check("context_row_links_exact", contexts[0]["rule_id"] == contextual_rule["rule_id"] and contexts[0]["pair_ids"] == contextual_rule["pair_ids"])
    check("context_explanation_mentions_counting", "Zählung" in contexts[0]["context_explanation_de"] and "zweifacher Zielzuordnung" in contexts[0]["context_explanation_de"])
    check("context_no_remap", contexts[0]["dictionary_remap_required"] == "NO" and contexts[0]["all_meaning_cues_visible"] == "YES")

    check("page_set_exact", {row["physical_page"] for row in pages} == {row["physical_page"] for row in source_records})
    check("page_record_total_135", sum(int(row["record_count"]) for row in pages) == 135)
    check("page_same_pair_total_33", sum(int(row["same_page_pair_count"]) for row in pages) == 33)
    check("page_capacity_count_4", sum(int(row["register_pair_incidence_count"]) > 0 for row in pages) == 4)
    check("zero_capacity_pages_exact", {row["physical_page"] for row in pages if int(row["register_pair_incidence_count"]) == 0} == {"f17r", "f77r"})
    check("page_covered_record_union_47", sum(int(row["contrast_covered_record_count"]) for row in pages) == 47)
    check("page_covered_uncovered_total_135", sum(int(row["contrast_covered_record_count"]) + int(row["contrast_uncovered_record_count"]) for row in pages) == 135)

    check("readable_contains_all_rules", all(row["rule_id"] not in readable or f"{row['component_a']} ↔ {row['component_b']}" in readable for row in rules))
    check("readable_contains_all_pairs", all(f"{row['source_record_id']} ↔ {row['target_record_id']}" in readable for row in pairs))
    check("readable_reports_core_counts", "**33 Paare / 32 Records**" in readable and "**48 Paare / 47 Records**" in readable)
    check("readable_reports_zero_pressure", "Wörterbuchdruck: **0**" in readable)
    check("readable_reports_context_explanation", contexts[0]["context_explanation_de"] in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_source_counts_exact", (result.get("record_count"), result.get("event_count"), result.get("page_count")) == (135, 183, 6))
    check("result_frame_counts_exact", (result.get("fluent_frame_class_count"), result.get("structural_frame_count")) == (20, 54))
    check("result_pair_counts_exact", (result.get("same_page_pair_count"), result.get("same_page_record_count"), result.get("register_pair_count"), result.get("register_pair_record_count"), result.get("cross_page_register_extension_pair_count")) == (33, 32, 48, 47, 15))
    check("result_rule_counts_exact", (result.get("contrast_rule_count"), result.get("recurrent_contrast_rule_count"), result.get("singleton_contrast_rule_count"), result.get("exact_signature_rule_count"), result.get("exact_recurrent_wording_rule_count"), result.get("contextual_rule_count"), result.get("dictionary_pressure_rule_count")) == (29, 13, 16, 28, 12, 1, 0))
    check("result_edit_counts_exact", (result.get("single_edit_block_pair_count"), result.get("two_edit_block_pair_count")) == (29, 19))
    check("result_changed_values_exact", set(result.get("changed_component_values", [])) == EXPECTED_CHANGED_VALUES and result.get("changed_component_value_count") == 13)
    check("result_changed_actions_exact", set(result.get("changed_action_values", [])) == EXPECTED_ACTION_VALUES and result.get("changed_action_value_count") == 3)
    check("result_capacity_exact", result.get("pair_capacity_page_count") == 4 and set(result.get("zero_pair_capacity_pages", [])) == {"f17r", "f77r"})
    check("result_all_meaning_changes_visible", result.get("all_pair_meaning_changes_visible") is True)
    unchanged = ("meaning_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "no independent semantic confirmation" in result.get("claim_ceiling", "") and "no independent" in result.get("claim_ceiling", ""))

    failed = [row for row in checks if not row["pass"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [row["name"] for row in failed],
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total", "failed_checks")}, indent=2, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
