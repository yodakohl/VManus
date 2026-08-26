#!/usr/bin/env python3
"""Validate GDT489's typed EINSTELLEN composition neighbourhood."""

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
BASE = ROOT / "experiments/yolo/gdt489_einstellen_typed_composition_neighbourhood"
OUT = BASE / "artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G485 = ROOT / "experiments/yolo/gdt485_fluent_reversible_microrecord_edition/artifacts"
G486 = ROOT / "experiments/yolo/gdt486_fluent_frame_component_contrast_deck/artifacts"
G487 = ROOT / "experiments/yolo/gdt487_model_conditioned_realization_lexicon/artifacts"
G488 = ROOT / "experiments/yolo/gdt488_action_endpoint_single_relaxation_closure/artifacts"
RUN = BASE / "src/run.py"
ACTION_FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
EVENTS_IN = G485 / "gdt485_183_literal_backprojection_events.tsv"
CONTRAST_RULES_IN = G486 / "gdt486_29_model_conditioned_contrast_rules.tsv"
LOCAL_EDGES_IN = G487 / "gdt487_13_local_recurrent_edges.tsv"
EINSTELLEN_CARRIERS_IN = G488 / "gdt488_2_einstellen_local_carriers.tsv"
FRAME_ATLAS = OUT / "gdt489_11_tr_composition_frames.tsv"
CONTEXT_WITNESSES = OUT / "gdt489_168_local_context_witnesses.tsv"
LOCAL_CONTACTS = OUT / "gdt489_3_local_einstellen_frame_contacts.tsv"
TYPED_EDGES = OUT / "gdt489_2_typed_einstellen_edges.tsv"
TYPED_CYCLE = OUT / "gdt489_1_typed_einstellen_cycle.tsv"
PAGE_SUPPORT = OUT / "gdt489_6_page_context_support.tsv"
READABLE = OUT / "GDT489_EINSTELLEN_TYPED_COMPOSITION_NEIGHBOURHOOD.md"
RESULT = OUT / "gdt489_result.json"
VALIDATION = OUT / "gdt489_validation.json"
STATUS = "EINSTELLEN_HAS_TWO_TYPED_COMPOSITION_EDGES__ALL_SIXTEEN_SINGLETONS_CONNECTED"
EXPECTED_FRAMES = [
    "@ACTION", "@ACTION+AIIN", "@ACTION+AIN", "@ACTION+AL",
    "@ACTION+AL+Y", "@ACTION+CH+E+Y", "@ACTION+CHD+Y",
    "@ACTION+OL", "@ACTION+OR+Y", "@ACTION+Y", "CH+@ACTION",
]
EXPECTED_CONTEXT_WITNESSES = {
    "@ACTION": 0,
    "@ACTION+AIIN": 18,
    "@ACTION+AIN": 11,
    "@ACTION+AL": 48,
    "@ACTION+AL+Y": 12,
    "@ACTION+CH+E+Y": 1,
    "@ACTION+CHD+Y": 0,
    "@ACTION+OL": 26,
    "@ACTION+OR+Y": 2,
    "@ACTION+Y": 40,
    "CH+@ACTION": 10,
}
EXPECTED_CONTEXT_POSITIONS = {
    "@ACTION": 0,
    "@ACTION+AIIN": 18,
    "@ACTION+AIN": 11,
    "@ACTION+AL": 51,
    "@ACTION+AL+Y": 12,
    "@ACTION+CH+E+Y": 1,
    "@ACTION+CHD+Y": 0,
    "@ACTION+OL": 28,
    "@ACTION+OR+Y": 2,
    "@ACTION+Y": 42,
    "CH+@ACTION": 10,
}
EXPECTED_EXTERNAL = {
    "@ACTION": (1, 21),
    "@ACTION+AIIN": (5, 8),
    "@ACTION+AIN": (2, 3),
    "@ACTION+AL": (3, 2),
    "@ACTION+AL+Y": (1, 1),
    "@ACTION+CH+E+Y": (1, 1),
    "@ACTION+CHD+Y": (5, 2),
    "@ACTION+OL": (7, 4),
    "@ACTION+OR+Y": (1, 1),
    "@ACTION+Y": (3, 2),
    "CH+@ACTION": (1, 1),
}
EXPECTED_PAGE = {
    "f17r": (2, 0, 0, 0, 0, 0),
    "f71v": (22, 19, 19, 12, 7, 0),
    "f72r": (96, 97, 101, 68, 9, 1),
    "f77r": (11, 5, 5, 4, 3, 0),
    "f88v": (14, 6, 6, 5, 5, 2),
    "f89r": (38, 41, 44, 32, 8, 0),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def match_positions(parts: list[str], pattern: list[str]) -> list[int]:
    if not pattern or len(pattern) > len(parts):
        return []
    return [index for index in range(len(parts) - len(pattern) + 1) if parts[index:index + len(pattern)] == pattern]


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [FRAME_ATLAS, CONTEXT_WITNESSES, LOCAL_CONTACTS, TYPED_EDGES, TYPED_CYCLE, PAGE_SUPPORT, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT489 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    action_frames = read_tsv(ACTION_FRAMES_IN)
    events = read_tsv(EVENTS_IN)
    rules = read_tsv(CONTRAST_RULES_IN)
    local_edges = read_tsv(LOCAL_EDGES_IN)
    carriers = read_tsv(EINSTELLEN_CARRIERS_IN)
    frames = read_tsv(FRAME_ATLAS)
    contexts = read_tsv(CONTEXT_WITNESSES)
    contacts = read_tsv(LOCAL_CONTACTS)
    edges = read_tsv(TYPED_EDGES)
    cycles = read_tsv(TYPED_CYCLE)
    pages = read_tsv(PAGE_SUPPORT)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    event_map = {row["backprojection_id"]: row for row in events}
    frame_map = {row["frozen_frame"]: row for row in frames}
    rule_map = {row["rule_id"]: row for row in rules}

    check("source_action_frame_count_104", len(action_frames) == 104, len(action_frames))
    check("source_event_count_183", len(events) == 183, len(events))
    check("source_rule_count_29", len(rules) == 29, len(rules))
    check("source_local_edge_count_13", len(local_edges) == 13, len(local_edges))
    check("source_carrier_count_2", len(carriers) == 2, len(carriers))
    check("source_tr_frame_count_11", sum(row["contrast_pair"] == "T~R" for row in action_frames) == 11)
    check("frame_count_11", len(frames) == 11, len(frames))
    check("context_count_168", len(contexts) == 168, len(contexts))
    check("contact_count_3", len(contacts) == 3, len(contacts))
    check("edge_count_2", len(edges) == 2, len(edges))
    check("cycle_count_1", len(cycles) == 1, len(cycles))
    check("page_count_6", len(pages) == 6, len(pages))

    check("frame_order_exact", [row["frozen_frame"] for row in frames] == EXPECTED_FRAMES)
    check("frame_ids_unique", len({row["frame_id"] for row in frames}) == 11)
    check("frame_values_unique", len(frame_map) == 11)
    check("frame_external_counts_exact", all((int(frame_map[name]["external_t_event_count"]), int(frame_map[name]["external_r_event_count"])) == counts for name, counts in EXPECTED_EXTERNAL.items()))
    check("frame_external_t_total_30", sum(int(row["external_t_event_count"]) for row in frames) == 30)
    check("frame_external_r_total_46", sum(int(row["external_r_event_count"]) for row in frames) == 46)
    check("frame_context_counts_exact", all(int(frame_map[name]["local_context_witness_count"]) == value for name, value in EXPECTED_CONTEXT_WITNESSES.items()))
    check("frame_context_positions_exact", all(int(frame_map[name]["local_context_positional_occurrence_count"]) == value for name, value in EXPECTED_CONTEXT_POSITIONS.items()))
    check("nonempty_frame_count_10", sum(row["context_recipe"] != "NONE" for row in frames) == 10)
    check("supported_context_frame_count_9", sum(row["context_recipe"] != "NONE" and int(row["local_context_witness_count"]) > 0 for row in frames) == 9)
    check("absent_context_exact", {row["frozen_frame"] for row in frames if row["local_support_class"] == "ABSENT_LOCAL_CONTEXT"} == {"@ACTION+CHD+Y"})
    check("empty_context_exact", {row["frozen_frame"] for row in frames if row["local_support_class"] == "EMPTY_CONTEXT_ACTION_BASELINE"} == {"@ACTION"})
    check("t_contact_frames_exact", {row["frozen_frame"] for row in frames if int(row["local_t_nonempty_contact_count"]) > 0} == {"@ACTION+Y", "CH+@ACTION"})
    check("context_only_frame_count_7", sum(row["local_support_class"] == "LOCAL_CONTEXT_ONLY" for row in frames) == 7)
    check("no_replacement_edges_from_frames", all(row["replacement_edge_created"] == "NO" for row in frames))
    check("frame_context_meanings_exact", frame_map["@ACTION+AIIN"]["context_meaning_de"] == "WERT" and frame_map["@ACTION+AIN"]["context_meaning_de"] == "ANTEIL" and frame_map["@ACTION+AL"]["context_meaning_de"] == "ZIELORT" and frame_map["@ACTION+OL"]["context_meaning_de"] == "FORTSETZEN")
    check("compound_context_meanings_exact", frame_map["@ACTION+AL+Y"]["context_meaning_de"] == "ZIELORT · POSTEN" and frame_map["@ACTION+CH+E+Y"]["context_meaning_de"] == "NEHMEN · GRAD I · POSTEN" and frame_map["@ACTION+OR+Y"]["context_meaning_de"] == "EINHEIT · POSTEN")

    check("context_ids_unique", len({row["context_witness_id"] for row in contexts}) == 168)
    check("context_frame_event_unique", len({(row["frame_id"], row["event_id"]) for row in contexts}) == 168)
    check("context_frames_no_empty_or_absent", "G489-F01" not in {row["frame_id"] for row in contexts} and "G489-F07" not in {row["frame_id"] for row in contexts})
    check("context_event_sources_exist", all(row["event_id"] in event_map for row in contexts))
    check("context_source_fields_exact", all(row["record_id"] == event_map[row["event_id"]]["record_id"] and row["physical_page"] == event_map[row["event_id"]]["physical_page"] and row["working_recipe"] == event_map[row["event_id"]]["working_recipe"] for row in contexts))
    check("context_readings_exact", all(row["current_event_reading_de"] == event_map[row["event_id"]]["current_event_reading_de"] for row in contexts))
    check("context_all_source_preserved", all(row["source_event_preserved"] == "YES" for row in contexts))
    check("context_position_total_175", sum(int(row["match_count"]) for row in contexts) == 175)
    check("context_unique_event_count_121", len({row["event_id"] for row in contexts}) == 121)
    check("context_complete_recipe_count_positive", sum(row["context_is_complete_event_recipe"] == "YES" for row in contexts) > 0)

    context_recomputed = True
    positions_recomputed = True
    for row in contexts:
        event = event_map[row["event_id"]]
        parts = event["working_recipe"].split("+")
        pattern = row["context_recipe"].split("+")
        positions = match_positions(parts, pattern)
        context_recomputed &= bool(positions)
        context_recomputed &= row["frozen_frame"] == frame_map[row["frozen_frame"]]["frozen_frame"]
        positions_recomputed &= int(row["match_count"]) == len(positions)
        positions_recomputed &= row["match_start_ordinals"] == "|".join(str(position + 1) for position in positions)
        positions_recomputed &= (row["context_is_complete_event_recipe"] == "YES") == (parts == pattern)
    check("context_matches_recomputed", context_recomputed)
    check("context_positions_recomputed", positions_recomputed)

    by_frame = Counter(row["frozen_frame"] for row in contexts)
    pos_by_frame = Counter()
    for row in contexts:
        pos_by_frame[row["frozen_frame"]] += int(row["match_count"])
    check("context_aggregation_to_frames_exact", all(by_frame[name] == EXPECTED_CONTEXT_WITNESSES[name] and pos_by_frame[name] == EXPECTED_CONTEXT_POSITIONS[name] for name in EXPECTED_FRAMES))

    contact_map = {(row["frozen_frame"], row["event_id"]): row for row in contacts}
    expected_contacts = {
        ("@ACTION+Y", "G485-E133"): ("CH+T+Y", "CONTIGUOUS_PARTIAL_FRAME", "2"),
        ("CH+@ACTION", "G485-E118"): ("CH+T", "EXACT_WHOLE_EVENT", "1"),
        ("CH+@ACTION", "G485-E133"): ("CH+T+Y", "CONTIGUOUS_PARTIAL_FRAME", "1"),
    }
    check("contacts_exact", set(contact_map) == set(expected_contacts))
    check("contact_ids_unique", len({row["contact_id"] for row in contacts}) == 3)
    check("contact_details_exact", all((contact_map[key]["working_recipe"], contact_map[key]["contact_class"], contact_map[key]["match_start_ordinals"]) == value for key, value in expected_contacts.items()))
    check("contact_class_profile_exact", Counter(row["contact_class"] for row in contacts) == Counter({"CONTIGUOUS_PARTIAL_FRAME": 2, "EXACT_WHOLE_EVENT": 1}))
    check("contact_event_set_exact", {row["event_id"] for row in contacts} == {"G485-E118", "G485-E133"})
    check("contact_frame_set_exact", {row["frozen_frame"] for row in contacts} == {"@ACTION+Y", "CH+@ACTION"})
    check("contacts_all_cues_visible", all(row["einstellen_cue_visible"] == "YES" for row in contacts))
    check("contacts_edge_type_exact", all(row["edge_type"] == "COMPOSITION_CONTACT_NOT_REPLACEMENT" for row in contacts))
    check("contacts_source_exact", all(row["current_event_reading_de"] == event_map[row["event_id"]]["current_event_reading_de"] and row["surface"] == event_map[row["event_id"]]["surface"] for row in contacts))
    check("contacts_match_carrier_inventory", {row["event_id"] for row in contacts} == {row["event_id"] for row in carriers})
    contact_recomputed = True
    for row in contacts:
        parts = event_map[row["event_id"]]["working_recipe"].split("+")
        pattern = row["instantiated_t_frame"].split("+")
        positions = match_positions(parts, pattern)
        contact_recomputed &= bool(positions)
        contact_recomputed &= row["match_start_ordinals"] == "|".join(str(position + 1) for position in positions)
        contact_recomputed &= (row["contact_class"] == "EXACT_WHOLE_EVENT") == (parts == pattern)
    check("contact_matches_recomputed", contact_recomputed)

    edge_map = {row["neighbour_meaning"]: row for row in edges}
    check("edge_neighbours_exact", set(edge_map) == {"NEHMEN", "POSTEN"})
    check("edge_ids_unique", len({row["edge_id"] for row in edges}) == 2)
    check("nehmen_edge_exact", edge_map["NEHMEN"]["source_frame"] == "CH+@ACTION" and edge_map["NEHMEN"]["neighbour_direction"] == "BEFORE_EINSTELLEN" and edge_map["NEHMEN"]["local_contact_count"] == "2")
    check("posten_edge_exact", edge_map["POSTEN"]["source_frame"] == "@ACTION+Y" and edge_map["POSTEN"]["neighbour_direction"] == "AFTER_EINSTELLEN" and edge_map["POSTEN"]["local_contact_count"] == "1")
    check("edge_local_events_exact", set(edge_map["NEHMEN"]["local_events"].split("|")) == {"G485-E118", "G485-E133"} and edge_map["POSTEN"]["local_events"] == "G485-E133")
    check("edge_external_counts_exact", (edge_map["NEHMEN"]["external_t_event_count"], edge_map["NEHMEN"]["external_r_event_count"]) == ("1", "1") and (edge_map["POSTEN"]["external_t_event_count"], edge_map["POSTEN"]["external_r_event_count"]) == ("3", "2"))
    check("edge_type_distinct", all(row["edge_type"] == "LOCAL_COMPOSITION_PLUS_EXTERNAL_T_R_SUBSTITUTION_FRAME" and row["replacement_edge"] == "NO" for row in edges))
    check("edge_no_meaning_change", all(row["meaning_change"] == "NO" for row in edges))
    check("edge_contacts_resolve", all(set(row["local_contact_ids"].split("|")) <= {contact["contact_id"] for contact in contacts} for row in edges))
    check("edge_readings_observed", all(all(event_map[event_id]["current_event_reading_de"] in row["observed_readings_de"] for event_id in row["local_events"].split("|")) for row in edges))

    cycle = cycles[0]
    check("cycle_id_exact", cycle["cycle_id"] == "G489-CY01")
    check("cycle_singleton_exact", cycle["singleton_rule_id"] == "G486-CR17" and {rule_map["G486-CR17"]["component_a"], rule_map["G486-CR17"]["component_b"]} == {"EINSTELLEN", "HIER"})
    check("cycle_composition_edge_exact", cycle["composition_edge_id"] == edge_map["POSTEN"]["edge_id"] and cycle["composition_source_frame"] == "@ACTION+Y" and cycle["composition_local_events"] == "G485-E133")
    check("cycle_bridge_exact", cycle["replacement_bridge_rule_id"] == "G486-CR25" and cycle["replacement_bridge_edge"] == "POSTEN~HIER" and cycle["replacement_bridge_pair_count"] == "2")
    check("cycle_bridge_source_exact", any(row["source_rule_id"] == "G486-CR25" and {row["component_a"], row["component_b"]} == {"HIER", "POSTEN"} and row["pair_count"] == "2" for row in local_edges))
    check("cycle_path_exact", cycle["alternate_path_excluding_singleton"] == "EINSTELLEN → POSTEN → HIER" and cycle["alternate_path_edge_count"] == "2")
    check("cycle_type_sequence_exact", cycle["edge_type_sequence"] == "COMPOSITION|RECURRENT_REPLACEMENT")
    check("cycle_typed_not_pure", cycle["typed_alternate_path_complete"] == "YES" and cycle["pure_replacement_cycle"] == "NO")
    check("cycle_endpoint_retained_no_remap", cycle["replacement_endpoint_status"] == "CAPACITY_LIMITED_RETAINED" and cycle["dictionary_remap_required"] == "NO")

    page_map = {row["physical_page"]: row for row in pages}
    check("page_set_exact", set(page_map) == set(EXPECTED_PAGE))
    check("page_counts_exact", all(tuple(int(page_map[page][field]) for field in ("event_count", "context_witness_count", "context_positional_occurrence_count", "context_unique_event_count", "context_frame_count", "local_t_contact_count")) == counts for page, counts in EXPECTED_PAGE.items()))
    check("page_event_total_183", sum(int(row["event_count"]) for row in pages) == 183)
    check("page_context_total_168", sum(int(row["context_witness_count"]) for row in pages) == 168)
    check("page_position_total_175", sum(int(row["context_positional_occurrence_count"]) for row in pages) == 175)
    check("page_contact_total_3", sum(int(row["local_t_contact_count"]) for row in pages) == 3)
    check("page_support_count_5", sum(row["has_context_support"] == "YES" for row in pages) == 5)
    check("page_zero_support_exact", {row["physical_page"] for row in pages if row["has_context_support"] == "NO"} == {"f17r"})

    check("readable_reports_core_counts", "**11**" in readable and "**30 T-**" in readable and "**46 R-Ereignissen**" in readable and "**168**" in readable and "**175**" in readable and "**121**" in readable)
    check("readable_reports_absent_context", "CHD+Y = BEARBEITEN · POSTEN" in readable)
    check("readable_all_contacts", all(row["event_id"] in readable and row["frozen_frame"] in readable for row in contacts))
    check("readable_both_edges", "EINSTELLEN — NEHMEN" in readable and "EINSTELLEN — POSTEN" in readable)
    check("readable_typed_cycle", "EINSTELLEN —KOMPOSITION→ POSTEN" in readable and "kein reiner Ersatzzyklus" in readable)
    check("readable_edge_distinction", "Nur der zweite Befund erzeugt eine Kompositionskante" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_frame_counts_exact", (result.get("tr_frame_count"), result.get("external_t_event_count"), result.get("external_r_event_count"), result.get("nonempty_context_frame_count"), result.get("locally_supported_context_frame_count"), result.get("absent_local_context_frame_count")) == (11, 30, 46, 10, 9, 1))
    check("result_absent_context_exact", result.get("absent_local_context_frames") == ["@ACTION+CHD+Y"])
    check("result_context_counts_exact", (result.get("local_context_witness_count"), result.get("local_context_positional_occurrence_count"), result.get("local_context_unique_event_count"), result.get("context_support_page_count")) == (168, 175, 121, 5))
    check("result_contact_counts_exact", (result.get("local_einstellen_event_count"), result.get("local_t_nonempty_frame_contact_count"), result.get("local_t_contact_frame_count"), result.get("local_t_contact_event_count")) == (2, 3, 2, 2))
    check("result_edge_counts_exact", result.get("typed_composition_edge_count") == 2 and set(result.get("typed_composition_neighbours", [])) == {"NEHMEN", "POSTEN"})
    check("result_cycle_counts_exact", (result.get("typed_alternate_cycle_count"), result.get("pure_replacement_cycle_added_count"), result.get("singleton_rule_connected_count_after_gdt489")) == (1, 0, 16))
    unchanged = ("meaning_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "composition and replacement edges remain distinct" in result.get("claim_ceiling", "") and "no new meaning" in result.get("claim_ceiling", ""))

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
