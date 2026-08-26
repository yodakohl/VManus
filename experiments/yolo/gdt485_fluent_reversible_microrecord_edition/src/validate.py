#!/usr/bin/env python3
"""Validate GDT485's fluent layer and exact backprojection channel."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
BASE = ROOT / "experiments/yolo/gdt485_fluent_reversible_microrecord_edition"
OUT = BASE / "artifacts"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
G482 = ROOT / "experiments/yolo/gdt482_residual_event_component_tiles/artifacts"
G484 = ROOT / "experiments/yolo/gdt484_complete_microrecord_provenance_edition/artifacts"
RUN = BASE / "src/run.py"
CURATION = BASE / "src/fluent_readings.tsv"
RECORDS_479 = G479 / "gdt479_135_definitive_microrecords.tsv"
EVENTS_479 = G479 / "gdt479_183_definitive_local_events.tsv"
SEQUENCES_482 = G482 / "gdt482_183_event_component_sequences.tsv"
RECORDS_484 = G484 / "gdt484_135_record_provenance_edition.tsv"
EVENTS_484 = G484 / "gdt484_183_event_support_assignments.tsv"
RECORD_EDITION = OUT / "gdt485_135_fluent_reversible_records.tsv"
EVENT_BACKPROJECTION = OUT / "gdt485_183_literal_backprojection_events.tsv"
TRANSFORMATION_SUMMARY = OUT / "gdt485_13_transformation_summary.tsv"
MARKER_SUMMARY = OUT / "gdt485_readability_marker_summary.tsv"
PAGE_SUMMARY = OUT / "gdt485_6_page_summary.tsv"
READABLE = OUT / "GDT485_FLUENT_135_MICRORECORD_EDITION.md"
RESULT = OUT / "gdt485_result.json"
VALIDATION = OUT / "gdt485_validation.json"
STATUS = "ALL_135_HAVE_FLUENT_REVERSIBLE_GERMAN__183_EVENT_BACKPROJECTIONS_EXACT"
EXPECTED_CODES = {
    "ALREADY_FLUENT": 14,
    "CATALOGUE_PROSE": 53,
    "CONTINUATION_SMOOTHED": 17,
    "COORDINATE_PROSE": 26,
    "DUPLICATE_COLLAPSED": 15,
    "GDT483_RETAINED": 1,
    "LIST_COMPACTED": 28,
    "MULTI_LOCUS_SMOOTHED": 8,
    "OBJECT_REFERENCE_SMOOTHED": 21,
    "ORDER_TRACE_SEPARATED": 54,
    "PUNCTUATION_SMOOTHED": 3,
    "QUALIFIER_REORDERED": 12,
    "SAME_GANG_SMOOTHED": 11,
}
EXPECTED_MARKERS = {
    "ORDER_META_SENTENCE": 57,
    "NUMBERED_EVENT_MARKER": 67,
    "ADDRESS_ARROW": 52,
    "INVERTED_CONTINUATION_IMPERATIVE": 12,
    "DOUBLE_CONTINUATION": 1,
    "SAME_GANG_META_PREFIX": 6,
    "RELATED_ADDRESS_META_PREFIX": 2,
    "SLASHED_LABEL_REPEAT": 10,
    "COMMA_BEFORE_CLOSURE": 4,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guillemet_values(text: str) -> list[str]:
    return re.findall(r"»([^»]+)«", text)


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [RECORD_EDITION, EVENT_BACKPROJECTION, TRANSFORMATION_SUMMARY, MARKER_SUMMARY, PAGE_SUMMARY, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT485 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    records_479 = read_tsv(RECORDS_479)
    events_479 = read_tsv(EVENTS_479)
    sequences_482 = read_tsv(SEQUENCES_482)
    records_484 = read_tsv(RECORDS_484)
    events_484 = read_tsv(EVENTS_484)
    curation = read_tsv(CURATION)
    records = read_tsv(RECORD_EDITION)
    events = read_tsv(EVENT_BACKPROJECTION)
    transformations = read_tsv(TRANSFORMATION_SUMMARY)
    markers = read_tsv(MARKER_SUMMARY)
    pages = read_tsv(PAGE_SUMMARY)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("source_record_count_135", len(records_479) == len(records_484) == 135)
    check("source_event_count_183", len(events_479) == len(sequences_482) == len(events_484) == 183)
    check("curation_count_135", len(curation) == 135, len(curation))
    check("record_output_count_135", len(records) == 135, len(records))
    check("event_output_count_183", len(events) == 183, len(events))
    check("transformation_summary_count_13", len(transformations) == 13, len(transformations))
    check("marker_summary_count_9", len(markers) == 9, len(markers))
    check("page_summary_count_6", len(pages) == 6, len(pages))

    r479 = {row["record_id"]: row for row in records_479}
    r484 = {row["record_id"]: row for row in records_484}
    curated = {row["record_id"]: row for row in curation}
    record_map = {row["record_id"]: row for row in records}
    e479 = {row["source_event_id"]: row for row in events_479}
    s482 = {row["source_event_id"]: row for row in sequences_482}
    e484 = {row["source_event_id"]: row for row in events_484}
    event_map = {row["source_event_id"]: row for row in events}
    record_keys = set(r484)
    event_keys = set(e479)
    check("source_record_keys_exact", set(r479) == set(curated) == set(record_map) == record_keys)
    check("source_event_keys_exact", set(s482) == set(e484) == set(event_map) == event_keys)
    check("record_ids_unique", len(record_map) == len(records))
    check("event_ids_unique", len(event_map) == len(events))
    check("curation_ids_unique", len(curated) == len(curation))
    check("edition_ids_unique", len({row["edition_id"] for row in records}) == 135)
    check("backprojection_ids_unique", len({row["backprojection_id"] for row in events}) == 183)

    record_fields = ("physical_page", "register", "page_record_ordinal", "record_start_role", "bundle_count", "event_count", "bundle_ids", "surface_sequence", "active_model_sequence")
    check("record_source_fields_exact", all(all(row[field] == r484[row["record_id"]][field] for field in record_fields) for row in records))
    check("technical_readings_byte_exact", all(row["technical_reading_de"] == r484[row["record_id"]]["current_record_reading_de"] for row in records))
    check("fluent_readings_match_curation", all(row["fluent_reading_de"] == curated[row["record_id"]]["fluent_reading_de"] for row in records))
    check("transformation_codes_match_curation", all(row["transformation_codes"] == curated[row["record_id"]]["transformation_codes"] for row in records))
    check("fluent_readings_nonempty", all(row["fluent_reading_de"].strip() for row in records))
    check("fluent_readings_terminal_punctuation", all(row["fluent_reading_de"].endswith((".", "!", "?")) for row in records))
    check("no_tabs_or_newlines_in_fluent", all("\t" not in row["fluent_reading_de"] and "\n" not in row["fluent_reading_de"] for row in records))
    check("no_double_spaces_in_fluent", all("  " not in row["fluent_reading_de"] for row in records))
    check("all_record_preservation_flags_yes", all(row["technical_reading_byte_preserved"] == row["literal_backprojection_complete"] == row["order_trace_preserved"] == row["distinct_named_values_preserved_in_fluent"] == row["meaning_inventory_preserved"] == "YES" for row in records))
    check("distinct_named_value_sets_exact", all(set(guillemet_values(row["technical_reading_de"])) == set(guillemet_values(row["fluent_reading_de"])) for row in records))
    check("stored_name_value_lists_exact", all(row["technical_guillemet_values"] == ("|".join(guillemet_values(row["technical_reading_de"])) or "NONE") and row["fluent_guillemet_values"] == ("|".join(guillemet_values(row["fluent_reading_de"])) or "NONE") for row in records))
    check("support_fields_exact", all(row["support_tier_rank"] == r484[row["record_id"]]["support_tier_rank"] and row["support_tier"] == r484[row["record_id"]]["support_tier"] and row["support_tier_label_de"] == r484[row["record_id"]]["support_tier_label_de"] and row["support_explanation_de"] == r484[row["record_id"]]["support_explanation_de"] for row in records))
    check("literal_name_slot_counts_exact", all(row["literal_name_slot_count"] == r484[row["record_id"]]["literal_name_slot_count"] for row in records))
    check("all_code_sets_known", all(set(row["transformation_codes"].split("|")) <= set(EXPECTED_CODES) for row in records))
    check("no_duplicate_code_within_record", all(len(row["transformation_codes"].split("|")) == len(set(row["transformation_codes"].split("|"))) for row in records))
    check("transformation_count_fields_exact", all(int(row["transformation_count"]) == len(row["transformation_codes"].split("|")) for row in records))
    check("already_fluent_count_14", sum(row["transformation_codes"] == "ALREADY_FLUENT" for row in records) == 14)
    check("already_fluent_strings_byte_exact", all(row["technical_reading_de"] == row["fluent_reading_de"] for row in records if row["transformation_codes"] == "ALREADY_FLUENT"))
    check("only_already_fluent_strings_byte_exact_except_sodar", all(row["transformation_codes"] in {"ALREADY_FLUENT", "GDT483_RETAINED"} for row in records if row["technical_reading_de"] == row["fluent_reading_de"]))
    check("sodar_gdt483_retained_exact", record_map["G475-R125"]["transformation_codes"] == "GDT483_RETAINED" and record_map["G475-R125"]["fluent_reading_de"] == r484["G475-R125"]["current_record_reading_de"])

    event_source_fields = ("record_id", "bundle_id", "physical_page", "register", "locus", "surface", "working_recipe", "active_model", "literal_working_reading_de", "order_occurrence_count", "order_root_sequence", "state_operation_sequence", "scope_orientation_sequence", "order_scope_trace_de")
    check("event_source_fields_exact", all(all(row[field] == e479[row["source_event_id"]][field] for field in event_source_fields) for row in events))
    check("event_normalized_literals_exact", all(row["normalized_literal_de"] == s482[row["source_event_id"]]["normalized_literal_de"] for row in events))
    check("event_semantic_tokens_exact", all(row["semantic_tokens"] == s482[row["source_event_id"]]["semantic_tokens"] and row["semantic_separators"] == s482[row["source_event_id"]]["semantic_separators"] for row in events))
    check("event_readings_exact", all(row["source_event_reading_de"] == e484[row["source_event_id"]]["source_event_reading_de"] and row["current_event_reading_de"] == e484[row["source_event_id"]]["current_event_reading_de"] for row in events))
    check("event_support_exact", all(row["event_support_tier"] == e484[row["source_event_id"]]["event_support_tier"] and row["event_support_detail"] == e484[row["source_event_id"]]["event_support_detail"] for row in events))
    check("all_event_preservation_flags_yes", all(row["exact_source_event_preserved"] == row["exact_component_sequence_preserved"] == row["exact_order_trace_preserved"] == "YES" for row in events))

    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    source_events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_record[row["record_id"]].append(row)
    for row in events_479:
        source_events_by_record[row["record_id"]].append(row)
    check("record_event_counts_exact", all(len(events_by_record[row["record_id"]]) == int(row["event_count"]) for row in records))
    check("record_event_ordinals_exact", all([int(event["record_event_ordinal"]) for event in events_by_record[row["record_id"]]] == list(range(1, int(row["event_count"]) + 1)) for row in records))
    check("record_backprojection_event_ids_exact", all(row["backprojection_event_ids"].split("|") == [event["source_event_id"] for event in source_events_by_record[row["record_id"]]] for row in records))
    check("record_recipe_sequences_exact", all(row["working_recipe_sequence"].split("|") == [event["working_recipe"] for event in source_events_by_record[row["record_id"]]] for row in records))
    check("record_literal_traces_exact", all(row["literal_component_trace_de"] == " || ".join(event["literal_working_reading_de"] for event in source_events_by_record[row["record_id"]]) for row in records))
    check("record_normalized_traces_exact", all(row["normalized_component_trace_de"] == " || ".join(s482[event["source_event_id"]]["normalized_literal_de"] for event in source_events_by_record[row["record_id"]]) for row in records))
    check("record_order_counts_exact", all(row["order_occurrence_count"] == r479[row["record_id"]]["order_occurrence_count"] for row in records))
    check("record_order_traces_exact", all(row["exact_order_scope_trace_de"] == r479[row["record_id"]]["order_scope_trace_de"] for row in records))
    check("order_record_count_54", sum(int(row["order_occurrence_count"]) > 0 for row in records) == 54)
    check("order_occurrence_total_69", sum(int(row["order_occurrence_count"]) for row in records) == 69)
    check("nonorder_trace_none", all((int(row["order_occurrence_count"]) == 0) == (row["exact_order_scope_trace_de"] == "NONE") for row in records))

    actual_codes = Counter(code for row in records for code in row["transformation_codes"].split("|"))
    check("transformation_profile_exact", actual_codes == Counter(EXPECTED_CODES), actual_codes)
    check("transformation_summary_codes_exact", {row["transformation_code"] for row in transformations} == set(EXPECTED_CODES))
    check("transformation_summary_counts_exact", {row["transformation_code"]: int(row["record_count"]) for row in transformations} == EXPECTED_CODES)
    check("transformation_summary_ids_exact", all(set(row["record_ids"].split("|")) == {record["record_id"] for record in records if row["transformation_code"] in record["transformation_codes"].split("|")} for row in transformations))
    check("order_separation_records_exact", {row["record_id"] for row in records if "ORDER_TRACE_SEPARATED" in row["transformation_codes"].split("|")} == {row["record_id"] for row in records if int(row["order_occurrence_count"]) > 0})

    marker_map = {row["marker_code"]: row for row in markers}
    check("marker_codes_exact", set(marker_map) == set(EXPECTED_MARKERS))
    check("technical_marker_profile_exact", {code: int(row["technical_occurrence_count"]) for code, row in marker_map.items()} == EXPECTED_MARKERS)
    check("all_target_marker_fluent_counts_zero", all(int(row["fluent_occurrence_count"]) == 0 and row["all_removed"] == "YES" for row in markers))
    check("removed_marker_counts_exact", all(int(row["removed_occurrence_count"]) == int(row["technical_occurrence_count"]) for row in markers))
    check("technical_marker_total_211", sum(int(row["technical_occurrence_count"]) for row in markers) == 211)

    check("page_set_exact", {row["physical_page"] for row in pages} == {row["physical_page"] for row in records})
    check("page_record_total_135", sum(int(row["record_count"]) for row in pages) == 135)
    check("page_event_total_183", sum(int(row["event_count"]) for row in pages) == 183)
    check("page_edited_total_121", sum(int(row["edited_fluent_record_count"]) for row in pages) == 121)
    check("page_already_total_14", sum(int(row["already_fluent_record_count"]) for row in pages) == 14)
    check("page_order_record_total_54", sum(int(row["order_trace_record_count"]) for row in pages) == 54)
    check("page_order_occurrence_total_69", sum(int(row["order_occurrence_count"]) for row in pages) == 69)
    check("page_technical_marker_total_211", sum(int(row["technical_marker_count"]) for row in pages) == 211)
    check("page_fluent_marker_total_zero", sum(int(row["fluent_marker_count"]) for row in pages) == 0)
    check("page_preservation_flags_yes", all(row["all_literal_backprojections_complete"] == row["all_names_preserved"] == "YES" for row in pages))

    check("readable_contains_all_records", all(record_id in readable for record_id in record_map))
    check("readable_contains_all_fluent_readings", all(row["fluent_reading_de"] in readable for row in records))
    check("readable_contains_all_technical_readings", all(row["technical_reading_de"] in readable for row in records))
    check("readable_contains_all_transformation_codes", all(code in readable for code in EXPECTED_CODES))
    check("readable_reports_135_135", "Werkstattfassungen: **135/135**" in readable)
    check("readable_reports_183_183", "Exakte Event-Rückprojektionen: **183/183**" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_core_counts_exact", (result.get("record_count"), result.get("event_count"), result.get("event_backprojection_count"), result.get("page_count")) == (135, 183, 183, 6))
    check("result_transformation_counts_exact", (result.get("transformation_code_count"), result.get("transformation_assignment_count"), result.get("already_fluent_record_count"), result.get("edited_fluent_record_count")) == (13, 263, 14, 121))
    check("result_order_counts_exact", (result.get("order_trace_record_count"), result.get("order_occurrence_count")) == (54, 69))
    check("result_marker_counts_exact", (result.get("technical_marker_occurrence_count"), result.get("fluent_marker_occurrence_count"), result.get("removed_marker_occurrence_count"), result.get("all_target_markers_removed")) == (211, 0, 211, True))
    check("result_preservation_flags_true", all(result.get(key) is True for key in ("all_technical_readings_byte_preserved", "all_literal_backprojections_complete", "all_order_traces_preserved", "all_distinct_named_values_preserved_in_fluent")))
    unchanged = ("meaning_inventory_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "no new root" in result.get("claim_ceiling", "") and "no new" in result.get("claim_ceiling", ""))

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
