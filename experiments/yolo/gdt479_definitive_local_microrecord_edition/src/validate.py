#!/usr/bin/env python3
"""Validate the GDT479 definitive six-page local working edition."""

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
BASE = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G475 = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/artifacts"
G476 = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution/artifacts"
G478 = ROOT / "experiments/yolo/gdt478_paired_ot_ol_order_grammar/artifacts"
BUNDLES_IN = G474 / "gdt474_146_locus_bundle_meaning_triptych.tsv"
EVENTS_IN = G474 / "gdt474_183_event_meaning_triptych.tsv"
BOUNDARIES_IN = G475 / "gdt475_146_bundle_boundary_roles.tsv"
RECORDS_IN = G475 / "gdt475_135_page_microrecords.tsv"
DECISIONS_IN = G476 / "gdt476_64_tie_context_decisions.tsv"
ORDER_IN = G478 / "gdt478_69_paired_order_scope_occurrences.tsv"
EVENTS = OUT / "gdt479_183_definitive_local_events.tsv"
BUNDLES = OUT / "gdt479_146_definitive_local_bundles.tsv"
RECORDS = OUT / "gdt479_135_definitive_microrecords.tsv"
PAGES = OUT / "gdt479_6_page_edition_summary.tsv"
READABLE = OUT / "GDT479_DEFINITIVE_SIX_PAGE_LOCAL_EDITION.md"
RESULT = OUT / "gdt479_result.json"
VALIDATION = OUT / "gdt479_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [EVENTS, BUNDLES, RECORDS, PAGES, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT479 builder before validation")

    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run(
        [sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False
    )
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    source_bundles = read_tsv(BUNDLES_IN)
    source_events = read_tsv(EVENTS_IN)
    source_boundaries = read_tsv(BOUNDARIES_IN)
    source_records = read_tsv(RECORDS_IN)
    decisions = read_tsv(DECISIONS_IN)
    source_order = read_tsv(ORDER_IN)
    events = read_tsv(EVENTS)
    bundles = read_tsv(BUNDLES)
    records = read_tsv(RECORDS)
    pages = read_tsv(PAGES)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    source_bundle_map = {row["bundle_id"]: row for row in source_bundles}
    source_event_map = {row["source_event_id"]: row for row in source_events}
    boundary_map = {row["bundle_id"]: row for row in source_boundaries}
    source_record_map = {row["record_id"]: row for row in source_records}
    decision_map = {row["bundle_id"]: row for row in decisions}
    event_map = {row["source_event_id"]: row for row in events}
    bundle_map = {row["bundle_id"]: row for row in bundles}
    record_map = {row["record_id"]: row for row in records}
    order_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_order:
        order_by_event[row["source_event_id"]].append(row)

    check("input_bundle_count_146", len(source_bundles) == 146, len(source_bundles))
    check("input_event_count_183", len(source_events) == 183, len(source_events))
    check("input_boundary_count_146", len(source_boundaries) == 146, len(source_boundaries))
    check("input_record_count_135", len(source_records) == 135, len(source_records))
    check("input_decision_count_64", len(decisions) == 64, len(decisions))
    check("input_order_count_69", len(source_order) == 69, len(source_order))
    check("output_event_count_183", len(events) == 183, len(events))
    check("output_bundle_count_146", len(bundles) == 146, len(bundles))
    check("output_record_count_135", len(records) == 135, len(records))
    check("output_page_count_6", len(pages) == 6, len(pages))

    check("unique_source_event_ids", len(event_map) == len(events), len(event_map))
    check("unique_bundle_ids", len(bundle_map) == len(bundles), len(bundle_map))
    check("unique_record_ids", len(record_map) == len(records), len(record_map))
    check(
        "event_order_preserved",
        [row["source_event_id"] for row in events] == [row["source_event_id"] for row in source_events],
        [row["source_event_id"] for row in events[:3]],
    )
    check(
        "bundle_order_preserved",
        [row["bundle_id"] for row in bundles] == [row["bundle_id"] for row in source_bundles],
        [row["bundle_id"] for row in bundles[:3]],
    )
    check(
        "record_order_preserved",
        [row["record_id"] for row in records] == [row["record_id"] for row in source_records],
        [row["record_id"] for row in records[:3]],
    )
    check("event_key_set_exact", set(event_map) == set(source_event_map), len(event_map))
    check("bundle_key_set_exact", set(bundle_map) == set(source_bundle_map), len(bundle_map))
    check("record_key_set_exact", set(record_map) == set(source_record_map), len(record_map))

    valid_models = {"COORDINATE", "INSTRUCTION", "CATALOGUE"}
    check("all_event_models_valid", all(row["active_model"] in valid_models for row in events), Counter(row["active_model"] for row in events))
    check("all_bundle_models_valid", all(row["active_model"] in valid_models for row in bundles), Counter(row["active_model"] for row in bundles))
    check("all_event_defaults_present", all(row["active_event_reading_de"].strip() for row in events), len(events))
    check("all_definitive_event_readings_present", all(row["definitive_event_reading_de"].strip() for row in events), len(events))
    check("all_bundle_defaults_present", all(row["active_bundle_reading_de"].strip() for row in bundles), len(bundles))
    check("all_record_defaults_present", all(row["definitive_record_reading_de"].strip() for row in records), len(records))
    check("all_event_alternatives_present", all(all(row[f"{model}_event_reading_de"].strip() for model in ("coordinate", "instruction", "catalogue")) for row in events), len(events))
    check("all_bundle_alternatives_present", all(all(row[f"{model}_bundle_reading_de"].strip() for model in ("coordinate", "instruction", "catalogue")) for row in bundles), len(bundles))
    check("all_three_bundle_alternatives_marked", all(row["all_three_alternative_readings_retained"] == "YES" for row in bundles), len(bundles))

    expected_changed_bundles = {
        "G474-B061", "G474-B071", "G474-B072", "G474-B090", "G474-B115", "G474-B116"
    }
    changed_bundles = {row["bundle_id"] for row in bundles if row["model_changed_from_gdt474"] == "YES"}
    changed_events = {row["source_event_id"] for row in events if row["model_changed_from_gdt474"] == "YES"}
    check("six_expected_bundle_model_changes", changed_bundles == expected_changed_bundles, sorted(changed_bundles))
    check("seven_event_reading_changes", len(changed_events) == 7, sorted(changed_events))
    check(
        "active_bundle_model_counts",
        Counter(row["active_model"] for row in bundles) == Counter({"COORDINATE": 28, "INSTRUCTION": 59, "CATALOGUE": 59}),
        Counter(row["active_model"] for row in bundles),
    )
    check(
        "active_event_model_counts",
        Counter(row["active_model"] for row in events) == Counter({"COORDINATE": 39, "INSTRUCTION": 73, "CATALOGUE": 71}),
        Counter(row["active_model"] for row in events),
    )
    expected_bundle_models = {
        row["bundle_id"]: decision_map.get(row["bundle_id"], {}).get("context_selected_model", row["selected_model"])
        for row in source_bundles
    }
    check("all_bundle_models_follow_context_rule", all(row["active_model"] == expected_bundle_models[row["bundle_id"]] for row in bundles), len(bundles))
    check("all_event_models_follow_bundle", all(row["active_model"] == bundle_map[row["bundle_id"]]["active_model"] for row in events), len(events))
    check("active_event_reading_matches_model", all(row["active_event_reading_de"] == row[f"{row['active_model'].lower()}_event_reading_de"] for row in events), len(events))
    check("active_bundle_reading_matches_model", all(row["active_bundle_reading_de"] == row[f"{row['active_model'].lower()}_bundle_reading_de"] for row in bundles), len(bundles))

    check("surfaces_preserved", all(row["surface"] == source_event_map[row["source_event_id"]]["surface"] for row in events), len(events))
    check("recipes_preserved", all(row["working_recipe"] == source_event_map[row["source_event_id"]]["working_recipe"] for row in events), len(events))
    check("literal_readings_preserved", all(row["literal_working_reading_de"] == source_event_map[row["source_event_id"]]["literal_working_reading_de"] for row in events), len(events))
    check("event_alternatives_preserved", all(all(row[f"{model}_event_reading_de"] == source_event_map[row["source_event_id"]][f"{model}_event_reading_de"] for model in ("coordinate", "instruction", "catalogue")) for row in events), len(events))
    check("bundle_surfaces_preserved", all(row["surface_sequence"] == source_bundle_map[row["bundle_id"]]["surface_sequence"] for row in bundles), len(bundles))
    check("bundle_recipes_preserved", all(row["recipe_sequence"] == source_bundle_map[row["bundle_id"]]["recipe_sequence"] for row in bundles), len(bundles))
    check("bundle_alternatives_preserved", all(all(row[f"{model}_bundle_reading_de"] == source_bundle_map[row["bundle_id"]][f"{model}_bundle_reading_de"] for model in ("coordinate", "instruction", "catalogue")) for row in bundles), len(bundles))
    check("boundary_roles_preserved", all(row["boundary_role"] == boundary_map[row["bundle_id"]]["boundary_role"] for row in bundles), len(bundles))
    check("bundle_record_links_preserved", all(row["record_id"] == boundary_map[row["bundle_id"]]["record_id"] for row in bundles), len(bundles))
    check("record_bundle_lists_preserved", all(row["bundle_ids"] == source_record_map[row["record_id"]]["bundle_ids"] for row in records), len(records))
    check("record_surface_sequences_preserved", all(row["surface_sequence"] == source_record_map[row["record_id"]]["surface_sequence"] for row in records), len(records))

    check("order_occurrence_count_69", sum(int(row["order_occurrence_count"]) for row in events) == 69, sum(int(row["order_occurrence_count"]) for row in events))
    check("order_event_count_60", sum(int(row["order_occurrence_count"]) > 0 for row in events) == 60, sum(int(row["order_occurrence_count"]) > 0 for row in events))
    check("non_order_event_count_123", sum(int(row["order_occurrence_count"]) == 0 for row in events) == 123, sum(int(row["order_occurrence_count"]) == 0 for row in events))
    check("ot_occurrence_count_41", sum(row["root"] == "OT" for row in source_order) == 41, Counter(row["root"] for row in source_order))
    check("ol_occurrence_count_28", sum(row["root"] == "OL" for row in source_order) == 28, Counter(row["root"] for row in source_order))
    check("order_roots_attached_exactly", all(row["order_root_sequence"].split("|") == [item["root"] for item in order_by_event[row["source_event_id"]]] if order_by_event[row["source_event_id"]] else row["order_root_sequence"] == "NONE" for row in events), len(events))
    check("order_operations_attached_exactly", all(row["state_operation_sequence"].split("|") == [item["state_operation"] for item in order_by_event[row["source_event_id"]]] if order_by_event[row["source_event_id"]] else row["state_operation_sequence"] == "NONE" for row in events), len(events))
    check("order_orientations_attached_exactly", all(row["scope_orientation_sequence"].split("|") == [item["scope_orientation"] for item in order_by_event[row["source_event_id"]]] if order_by_event[row["source_event_id"]] else row["scope_orientation_sequence"] == "NONE" for row in events), len(events))
    check("ordered_readings_explicit", all(("Reihenfolge konkret:" in row["definitive_event_reading_de"]) == (int(row["order_occurrence_count"]) > 0) for row in events), len(events))

    check("record_bundle_total_146", sum(int(row["bundle_count"]) for row in records) == 146, sum(int(row["bundle_count"]) for row in records))
    check("record_event_total_183", sum(int(row["event_count"]) for row in records) == 183, sum(int(row["event_count"]) for row in records))
    check("multi_locus_record_count_8", sum(int(row["bundle_count"]) > 1 for row in records) == 8, sum(int(row["bundle_count"]) > 1 for row in records))
    check("all_record_default_flags_yes", all(row["all_events_have_default"] == "YES" for row in records), len(records))
    check("page_event_total_183", sum(int(row["event_count"]) for row in pages) == 183, sum(int(row["event_count"]) for row in pages))
    check("page_bundle_total_146", sum(int(row["bundle_count"]) for row in pages) == 146, sum(int(row["bundle_count"]) for row in pages))
    check("page_record_total_135", sum(int(row["record_count"]) for row in pages) == 135, sum(int(row["record_count"]) for row in pages))
    check("page_order_total_69", sum(int(row["order_occurrence_count"]) for row in pages) == 69, sum(int(row["order_occurrence_count"]) for row in pages))
    check("page_change_total_6", sum(int(row["model_change_count"]) for row in pages) == 6, sum(int(row["model_change_count"]) for row in pages))
    check("six_expected_pages", [row["physical_page"] for row in pages] == ["f17r", "f71v", "f72r", "f77r", "f88v", "f89r"], [row["physical_page"] for row in pages])
    check("sealed_pages_absent", all(not row["physical_page"].startswith("f84") for row in events + bundles + records + pages), sorted({row["physical_page"] for row in pages}))

    check("exact_package_surfaces_present", sorted(row["surface"] for row in events if row["surface"] in {"ykyd", "yddy"}) == ["yddy", "ykyd"], sorted(row["surface"] for row in events if row["surface"] in {"ykyd", "yddy"}))
    check("zero_root_meaning_changes", all(row["root_meaning_change"] == "NO" for row in events + bundles), len(events) + len(bundles))
    check("zero_learned_name_changes", all(row["learned_name_change"] == "NO" for row in events + bundles), len(events) + len(bundles))
    check("all_event_ids_in_readable", all(row["source_event_id"] in readable for row in events), len(events))
    check("all_bundle_ids_in_readable", all(row["bundle_id"] in readable for row in bundles), len(bundles))
    check("all_record_ids_in_readable", all(row["record_id"] in readable for row in records), len(records))
    check("readable_page_sections_6", sum(readable.count(f"## {row['physical_page']}") for row in pages) == 6, len(pages))

    check("result_status_exact", result.get("status") == "DEFINITIVE_183_EVENT_135_MICRORECORD_LOCAL_WORKING_EDITION_COMPLETE", result.get("status"))
    check("result_counts_exact", (result.get("event_count"), result.get("bundle_count"), result.get("record_count"), result.get("page_count")) == (183, 146, 135, 6), {key: result.get(key) for key in ("event_count", "bundle_count", "record_count", "page_count")})
    check("result_changed_bundle_ids_exact", set(result.get("bundle_model_change_ids", [])) == expected_changed_bundles, result.get("bundle_model_change_ids"))
    check("result_all_defaults_183", result.get("all_events_have_default_count") == 183, result.get("all_events_have_default_count"))
    check("result_all_alternatives_146", result.get("all_bundles_retain_three_alternatives_count") == 146, result.get("all_bundles_retain_three_alternatives_count"))
    unchanged_keys = ("component_meaning_change_count", "learned_name_change_count", "surface_change_count", "recipe_change_count", "new_page_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged_keys), {key: result.get(key) for key in unchanged_keys})

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
