#!/usr/bin/env python3
"""Validate GDT484's complete microrecord support-provenance edition."""

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
BASE = ROOT / "experiments/yolo/gdt484_complete_microrecord_provenance_edition"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
G480 = ROOT / "experiments/yolo/gdt480_microrecord_template_atlas/artifacts"
G481 = ROOT / "experiments/yolo/gdt481_microrecord_fragment_grammar/artifacts"
G482 = ROOT / "experiments/yolo/gdt482_residual_event_component_tiles/artifacts"
G483 = ROOT / "experiments/yolo/gdt483_sodar_exact_running_carrier_closure/artifacts"
RECORDS_IN = G479 / "gdt479_135_definitive_microrecords.tsv"
EVENTS_IN = G479 / "gdt479_183_definitive_local_events.tsv"
TEMPLATES_IN = G480 / "gdt480_135_record_template_assignments.tsv"
COVERAGE_IN = G481 / "gdt481_135_record_fragment_coverage.tsv"
FRAGMENTS_IN = G481 / "gdt481_183_event_fragment_assignments.tsv"
SEQUENCES_IN = G482 / "gdt482_183_event_component_sequences.tsv"
TILES_IN = G482 / "gdt482_45_residual_event_internal_tiles.tsv"
CLOSURE_IN = G483 / "gdt483_45_residual_closure.tsv"
G483_RESULT_IN = G483 / "gdt483_result.json"
EVENT_SUPPORT = OUT / "gdt484_183_event_support_assignments.tsv"
MULTI_EVENT_TILES = OUT / "gdt484_7_multi_event_tail_component_tiles.tsv"
MULTI_RECORD_CLOSURE = OUT / "gdt484_3_multi_event_tail_closure.tsv"
RECORD_EDITION = OUT / "gdt484_135_record_provenance_edition.tsv"
TIER_SUMMARY = OUT / "gdt484_10_provenance_tier_summary.tsv"
PAGE_SUMMARY = OUT / "gdt484_6_page_summary.tsv"
READABLE = OUT / "GDT484_COMPLETE_135_RECORD_PROVENANCE_EDITION.md"
RESULT = OUT / "gdt484_result.json"
VALIDATION = OUT / "gdt484_validation.json"
STATUS = "ALL_135_MICRORECORDS_HAVE_READINGS_AND_SUPPORT_PROVENANCE__ZERO_FUNCTIONAL_RESIDUE"
TIER_ORDER = (
    "RECURRENT_STRICT_WHOLE_RECORD",
    "RECURRENT_ROLE_WHOLE_RECORD",
    "ALL_EVENTS_STRICT_RECURRENT",
    "PARTIAL_STRICT_EVENT_RECURRENT",
    "ALL_EVENTS_ROLE_RECURRENT",
    "PARTIAL_ROLE_EVENT_RECURRENT",
    "SAME_MODEL_COMPONENT_TILE",
    "MODEL_FREE_COMPONENT_BACKOFF",
    "EXACT_RUNNING_CARRIER",
    "LEARNED_LEXICAL_SLOT",
)
EXPECTED_TIERS = {
    "RECURRENT_STRICT_WHOLE_RECORD": 28,
    "RECURRENT_ROLE_WHOLE_RECORD": 23,
    "ALL_EVENTS_STRICT_RECURRENT": 4,
    "PARTIAL_STRICT_EVENT_RECURRENT": 19,
    "ALL_EVENTS_ROLE_RECURRENT": 6,
    "PARTIAL_ROLE_EVENT_RECURRENT": 7,
    "SAME_MODEL_COMPONENT_TILE": 42,
    "MODEL_FREE_COMPONENT_BACKOFF": 3,
    "EXACT_RUNNING_CARRIER": 1,
    "LEARNED_LEXICAL_SLOT": 2,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [EVENT_SUPPORT, MULTI_EVENT_TILES, MULTI_RECORD_CLOSURE, RECORD_EDITION, TIER_SUMMARY, PAGE_SUMMARY, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT484 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    source_records = read_tsv(RECORDS_IN)
    source_events = read_tsv(EVENTS_IN)
    templates = read_tsv(TEMPLATES_IN)
    coverage = read_tsv(COVERAGE_IN)
    fragments = read_tsv(FRAGMENTS_IN)
    sequences = read_tsv(SEQUENCES_IN)
    g482_tiles = read_tsv(TILES_IN)
    g483_closure = read_tsv(CLOSURE_IN)
    g483_result = json.loads(G483_RESULT_IN.read_text(encoding="utf-8"))
    event_support = read_tsv(EVENT_SUPPORT)
    multi_tiles = read_tsv(MULTI_EVENT_TILES)
    multi_records = read_tsv(MULTI_RECORD_CLOSURE)
    records = read_tsv(RECORD_EDITION)
    tiers = read_tsv(TIER_SUMMARY)
    pages = read_tsv(PAGE_SUMMARY)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("source_record_count_135", len(source_records) == 135, len(source_records))
    check("source_event_count_183", len(source_events) == 183, len(source_events))
    check("template_assignment_count_135", len(templates) == 135, len(templates))
    check("coverage_count_135", len(coverage) == 135, len(coverage))
    check("fragment_assignment_count_183", len(fragments) == 183, len(fragments))
    check("sequence_count_183", len(sequences) == 183, len(sequences))
    check("gdt482_tile_count_45", len(g482_tiles) == 45, len(g482_tiles))
    check("gdt483_closure_count_45", len(g483_closure) == 45, len(g483_closure))
    check("event_support_count_183", len(event_support) == 183, len(event_support))
    check("multi_event_tile_count_7", len(multi_tiles) == 7, len(multi_tiles))
    check("multi_record_closure_count_3", len(multi_records) == 3, len(multi_records))
    check("record_edition_count_135", len(records) == 135, len(records))
    check("tier_summary_count_10", len(tiers) == 10, len(tiers))
    check("page_summary_count_6", len(pages) == 6, len(pages))

    source_record_map = {row["record_id"]: row for row in source_records}
    source_event_map = {row["source_event_id"]: row for row in source_events}
    template_map = {row["record_id"]: row for row in templates}
    coverage_map = {row["record_id"]: row for row in coverage}
    fragment_map = {row["source_event_id"]: row for row in fragments}
    sequence_map = {row["source_event_id"]: row for row in sequences}
    g482_tile_map = {row["source_event_id"]: row for row in g482_tiles}
    closure_map = {row["source_event_id"]: row for row in g483_closure}
    event_support_map = {row["source_event_id"]: row for row in event_support}
    record_map = {row["record_id"]: row for row in records}
    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_events:
        events_by_record[row["record_id"]].append(row)

    check("event_assignment_ids_unique", len({row["assignment_id"] for row in event_support}) == 183)
    check("event_support_keys_unique", len(event_support_map) == 183)
    check("multi_tile_ids_unique", len({row["tile_id"] for row in multi_tiles}) == 7)
    check("multi_tile_event_ids_unique", len({row["source_event_id"] for row in multi_tiles}) == 7)
    check("multi_record_ids_unique", len({row["closure_id"] for row in multi_records}) == 3)
    check("edition_ids_unique", len({row["edition_id"] for row in records}) == 135)
    check("record_keys_unique", len(record_map) == 135)
    check("source_event_key_set_exact", set(event_support_map) == set(source_event_map))
    check("source_record_key_set_exact", set(record_map) == set(source_record_map))
    check("event_source_order_exact", [row["source_event_id"] for row in event_support] == [row["source_event_id"] for row in source_events])
    check("record_source_order_exact", [row["record_id"] for row in records] == [row["record_id"] for row in source_records])

    event_fields = ("record_id", "bundle_id", "physical_page", "register", "active_model", "surface", "working_recipe")
    check("event_source_fields_preserved", all(all(row[field] == source_event_map[row["source_event_id"]][field] for field in event_fields) for row in event_support))
    check("event_fragment_links_exact", all(row["strict_template_id"] == fragment_map[row["source_event_id"]]["strict_template_id"] and row["strict_occurrence_count"] == fragment_map[row["source_event_id"]]["strict_occurrence_count"] and row["role_shape_id"] == fragment_map[row["source_event_id"]]["role_shape_id"] and row["role_occurrence_count"] == fragment_map[row["source_event_id"]]["role_occurrence_count"] for row in event_support))
    check("all_event_provenance_assigned", all(row["provenance_assigned"] == "YES" and row["event_support_tier"] and row["event_support_detail"] for row in event_support))
    check("all_event_source_meanings_preserved", all(row["source_meaning_preserved"] == "YES" for row in event_support))
    check("one_event_reading_refined", sum(row["reading_refined_by_gdt483"] == "YES" for row in event_support) == 1)
    check("refined_event_exact", event_support_map["P1008-E1297"]["reading_refined_by_gdt483"] == "YES" and event_support_map["P1008-E1297"]["current_event_reading_de"] == g483_result["preferred_generic_reading_de"])
    check("other_event_readings_unchanged", all(row["current_event_reading_de"] == row["source_event_reading_de"] for row in event_support if row["source_event_id"] != "P1008-E1297"))
    check("sealed_pages_absent", all(not row["physical_page"].startswith("f84") for row in event_support + multi_tiles + multi_records + records + pages))

    expected_multi_records = {"G475-R074", "G475-R084", "G475-R107"}
    expected_multi_events = {event["source_event_id"] for record_id in expected_multi_records for event in events_by_record[record_id]}
    check("multi_record_keys_exact", {row["record_id"] for row in multi_records} == expected_multi_records)
    check("multi_event_keys_exact", {row["source_event_id"] for row in multi_tiles} == expected_multi_events)
    check("multi_event_record_links_exact", all(row["record_id"] == source_event_map[row["source_event_id"]]["record_id"] for row in multi_tiles))
    check("multi_event_source_fields_exact", all(row["surface"] == source_event_map[row["source_event_id"]]["surface"] and row["working_recipe"] == source_event_map[row["source_event_id"]]["working_recipe"] and row["definitive_event_reading_de"] == source_event_map[row["source_event_id"]]["definitive_event_reading_de"] for row in multi_tiles))
    check("multi_event_token_counts_exact", all(int(row["token_count"]) == int(sequence_map[row["source_event_id"]]["token_count"]) for row in multi_tiles))
    check("multi_event_all_conditioned_complete", all(int(row["conditioned_recurrent_token_count"]) == int(row["token_count"]) and row["conditioned_local_tokens"] == "NONE" for row in multi_tiles))
    check("multi_event_all_free_complete", all(int(row["free_recurrent_token_count"]) == int(row["token_count"]) for row in multi_tiles))
    check("multi_event_no_local_trace", all("LOCAL:" not in row["conditioned_tile_trace"] for row in multi_tiles))
    check("multi_event_component_total_20", sum(int(row["token_count"]) for row in multi_tiles) == 20)
    check("multi_event_conditioned_total_20", sum(int(row["conditioned_recurrent_token_count"]) for row in multi_tiles) == 20)
    check("multi_event_multi_fragment_total_10", sum(int(row["conditioned_multi_fragment_token_count"]) for row in multi_tiles) == 10)
    check("multi_record_event_profile_exact", Counter(row["event_count"] for row in multi_records) == Counter({"2": 2, "3": 1}))
    check("multi_record_component_profile_exact", {row["record_id"]: int(row["total_component_count"]) for row in multi_records} == {"G475-R074": 7, "G475-R084": 5, "G475-R107": 8})
    check("multi_records_all_complete", all(row["all_events_conditioned_complete"] == "YES" and row["total_component_count"] == row["conditioned_recurrent_component_count"] for row in multi_records))
    check("multi_record_readings_preserved", all(row["definitive_record_reading_de"] == source_record_map[row["record_id"]]["definitive_record_reading_de"] and row["source_meaning_preserved"] == "YES" for row in multi_records))

    record_fields = ("physical_page", "register", "page_record_ordinal", "record_start_role", "bundle_count", "event_count", "bundle_ids", "surface_sequence", "active_model_sequence")
    check("record_source_fields_preserved", all(all(row[field] == source_record_map[row["record_id"]][field] for field in record_fields) for row in records))
    check("record_template_links_exact", all(row["strict_template_id"] == template_map[row["record_id"]]["strict_template_id"] and row["strict_template_record_count"] == template_map[row["record_id"]]["strict_template_record_count"] and row["role_shape_id"] == template_map[row["record_id"]]["role_shape_id"] and row["role_shape_record_count"] == template_map[row["record_id"]]["role_shape_record_count"] for row in records))
    check("record_coverage_links_exact", all(row["recurrent_strict_event_count"] == coverage_map[row["record_id"]]["recurrent_strict_event_count"] and row["recurrent_role_event_count"] == coverage_map[row["record_id"]]["recurrent_role_event_count"] and row["decomposition_class"] == coverage_map[row["record_id"]]["decomposition_class"] for row in records))
    check("record_name_slot_counts_exact", all(row["literal_name_slot_count"] == template_map[row["record_id"]]["literal_name_slot_count"] for row in records))
    check("all_record_defaults_retained", all(row["all_events_have_default"] == "YES" and row["current_record_reading_de"] for row in records))
    check("all_record_provenance_complete", all(row["provenance_complete"] == "YES" and row["support_explanation_de"] for row in records))
    check("all_record_source_meanings_preserved", all(row["source_meaning_preserved"] == "YES" for row in records))
    check("one_record_reading_refined", sum(row["reading_refined_by_gdt483"] == "YES" for row in records) == 1)
    check("refined_record_exact", record_map["G475-R125"]["reading_refined_by_gdt483"] == "YES" and record_map["G475-R125"]["current_record_reading_de"] == g483_result["preferred_generic_reading_de"])
    check("other_record_readings_unchanged", all(row["current_record_reading_de"] == row["source_record_reading_de"] for row in records if row["record_id"] != "G475-R125"))

    actual_tiers = Counter(row["support_tier"] for row in records)
    check("tier_profile_exact", actual_tiers == Counter(EXPECTED_TIERS), actual_tiers)
    check("tier_ranks_exact", all(int(row["support_tier_rank"]) == TIER_ORDER.index(row["support_tier"]) + 1 for row in records))
    check("strict_whole_tier_exact", all((row["support_tier"] == TIER_ORDER[0]) == (int(row["strict_template_record_count"]) > 1) for row in records))
    check("role_whole_tier_requires_strict_singleton", all(row["support_tier"] != TIER_ORDER[1] or (int(row["strict_template_record_count"]) == 1 and int(row["role_shape_record_count"]) > 1) for row in records))
    check("all_strict_event_tier_exact", all(row["support_tier"] != TIER_ORDER[2] or coverage_map[row["record_id"]]["all_events_strict_recurrent"] == "YES" for row in records))
    check("partial_strict_event_tier_exact", all(row["support_tier"] != TIER_ORDER[3] or 0 < int(row["recurrent_strict_event_count"]) < int(row["event_count"]) for row in records))
    check("all_role_event_tier_exact", all(row["support_tier"] != TIER_ORDER[4] or coverage_map[row["record_id"]]["all_events_role_recurrent"] == "YES" for row in records))
    check("partial_role_event_tier_exact", all(row["support_tier"] != TIER_ORDER[5] or 0 < int(row["recurrent_role_event_count"]) < int(row["event_count"]) for row in records))
    check("same_model_tier_includes_multi_exact", expected_multi_records <= {row["record_id"] for row in records if row["support_tier"] == TIER_ORDER[6]})
    check("model_free_tier_ids_exact", {row["record_id"] for row in records if row["support_tier"] == TIER_ORDER[7]} == {"G475-R073", "G475-R086", "G475-R123"})
    check("running_carrier_tier_exact", {row["record_id"] for row in records if row["support_tier"] == TIER_ORDER[8]} == {"G475-R125"})
    check("learned_slot_tier_ids_exact", {row["record_id"] for row in records if row["support_tier"] == TIER_ORDER[9]} == {"G475-R101", "G475-R119"})

    tail_records = [row for row in records if row["decomposition_class"] == "SINGLETON_FRAGMENT_TAIL"]
    check("fragment_tail_count_48", len(tail_records) == 48)
    check("fragment_tail_tier_profile_exact", Counter(row["support_tier"] for row in tail_records) == Counter({"SAME_MODEL_COMPONENT_TILE": 42, "MODEL_FREE_COMPONENT_BACKOFF": 3, "EXACT_RUNNING_CARRIER": 1, "LEARNED_LEXICAL_SLOT": 2}))
    check("fragment_tail_event_count_profile", Counter(row["event_count"] for row in tail_records) == Counter({"1": 45, "2": 2, "3": 1}))
    check("single_tail_closure_links_exact", all(row["record_id"] in expected_multi_records or events_by_record[row["record_id"]][0]["source_event_id"] in closure_map for row in tail_records))

    check("tier_summary_order_exact", [row["support_tier"] for row in tiers] == list(TIER_ORDER))
    check("tier_summary_ranks_exact", [int(row["tier_rank"]) for row in tiers] == list(range(1, 11)))
    check("tier_summary_counts_exact", {row["support_tier"]: int(row["record_count"]) for row in tiers} == EXPECTED_TIERS)
    check("tier_summary_record_totals_135", sum(int(row["record_count"]) for row in tiers) == 135)
    check("tier_summary_event_totals_183", sum(int(row["event_count"]) for row in tiers) == 183)
    check("tier_summary_ids_exact", all(set(row["record_ids"].split("|")) == {record["record_id"] for record in records if record["support_tier"] == row["support_tier"]} for row in tiers))

    check("page_set_exact", {row["physical_page"] for row in pages} == {row["physical_page"] for row in records})
    check("page_record_totals_135", sum(int(row["record_count"]) for row in pages) == 135)
    check("page_event_totals_183", sum(int(row["event_count"]) for row in pages) == 183)
    check("page_refinement_total_1", sum(int(row["reading_refinement_count"]) for row in pages) == 1)
    check("page_tier_totals_exact", all(sum(int(row[f"tier_{rank:02d}_count"]) for row in pages) == EXPECTED_TIERS[tier] for rank, tier in enumerate(TIER_ORDER, 1)))
    check("page_defaults_complete", all(row["all_records_have_default"] == "YES" and row["all_records_have_provenance"] == "YES" for row in pages))

    check("readable_contains_all_records", all(record_id in readable for record_id in record_map))
    check("readable_contains_all_tiers", all(row["tier_label_de"] in readable for row in tiers))
    check("readable_reports_multi_records", all(record_id in readable for record_id in expected_multi_records))
    check("readable_reports_target_phrase", g483_result["preferred_generic_reading_de"] in readable)
    check("readable_reports_zero_residue", "Ungeklärte Funktionsreste: **0**" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_core_counts_exact", (result.get("record_count"), result.get("event_count"), result.get("page_count"), result.get("provenance_tier_count")) == (135, 183, 6, 10))
    check("result_tier_counts_exact", result.get("tier_counts") == EXPECTED_TIERS)
    check("result_layer_totals_exact", (result.get("whole_record_supported_record_count"), result.get("event_fragment_supported_record_count"), result.get("same_model_component_supported_record_count"), result.get("model_free_component_backoff_record_count"), result.get("exact_running_carrier_record_count"), result.get("learned_lexical_slot_record_count")) == (51, 36, 42, 3, 1, 2))
    check("result_multi_tail_exact", (result.get("multi_event_tail_record_count"), result.get("multi_event_tail_event_count"), result.get("multi_event_tail_component_count"), result.get("multi_event_tail_conditioned_recurrent_component_count")) == (3, 7, 20, 20))
    check("result_complete_counts_exact", (result.get("all_records_have_concrete_default_count"), result.get("all_records_have_support_provenance_count"), result.get("unexplained_functional_record_count")) == (135, 135, 0))
    check("result_refinement_exact", result.get("preferred_fluent_paraphrase_refinement_count") == 1 and result.get("refined_record_ids") == ["G475-R125"])
    unchanged = ("component_meaning_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
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
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total", "failed_checks")}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
