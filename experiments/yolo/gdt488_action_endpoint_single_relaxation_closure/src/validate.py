#!/usr/bin/env python3
"""Validate GDT488's single-relaxation endpoint closure."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt488_action_endpoint_single_relaxation_closure"
OUT = BASE / "artifacts"
G485 = ROOT / "experiments/yolo/gdt485_fluent_reversible_microrecord_edition/artifacts"
G486 = ROOT / "experiments/yolo/gdt486_fluent_frame_component_contrast_deck/artifacts"
G487 = ROOT / "experiments/yolo/gdt487_model_conditioned_realization_lexicon/artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
RUN = BASE / "src/run.py"
RECORDS_IN = G485 / "gdt485_135_fluent_reversible_records.tsv"
EVENTS_IN = G485 / "gdt485_183_literal_backprojection_events.tsv"
STRICT_PAIRS_IN = G486 / "gdt486_48_register_minimal_pairs.tsv"
STRICT_RULES_IN = G486 / "gdt486_29_model_conditioned_contrast_rules.tsv"
LOCAL_EDGES_IN = G487 / "gdt487_13_local_recurrent_edges.tsv"
ACTION_FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
REGISTER_ONLY = OUT / "gdt488_1_register_only_endpoint_pair.tsv"
EVENT_PAIRS = OUT / "gdt488_5_endpoint_event_minimal_pairs.tsv"
NEW_EVENT_PAIRS = OUT / "gdt488_3_new_event_projection_pairs.tsv"
EINSTELLEN_CARRIERS = OUT / "gdt488_2_einstellen_local_carriers.tsv"
CLOSURE_STATUS = OUT / "gdt488_2_endpoint_closure_status.tsv"
CAPACITY = OUT / "gdt488_2_endpoint_relaxation_capacity.tsv"
HALTEN_CYCLE = OUT / "gdt488_1_halten_cycle.tsv"
READABLE = OUT / "GDT488_ACTION_ENDPOINT_SINGLE_RELAXATION_CLOSURE.md"
RESULT = OUT / "gdt488_result.json"
VALIDATION = OUT / "gdt488_validation.json"
STATUS = "HALTEN_CYCLE_CLOSED__EINSTELLEN_REMAINS_CAPACITY_LIMITED"
EXPECTED_EVENT_SETS = {
    frozenset(("G485-E022", "G485-E023")),
    frozenset(("G485-E041", "G485-E050")),
    frozenset(("G485-E132", "G485-E177")),
    frozenset(("G485-E133", "G485-E157")),
    frozenset(("G485-E168", "G485-E169")),
}
EXPECTED_NEW_EVENT_SETS = {
    frozenset(("G485-E022", "G485-E023")),
    frozenset(("G485-E041", "G485-E050")),
    frozenset(("G485-E168", "G485-E169")),
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

    generated = [REGISTER_ONLY, EVENT_PAIRS, NEW_EVENT_PAIRS, EINSTELLEN_CARRIERS, CLOSURE_STATUS, CAPACITY, HALTEN_CYCLE, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT488 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    records = read_tsv(RECORDS_IN)
    events = read_tsv(EVENTS_IN)
    strict_pairs = read_tsv(STRICT_PAIRS_IN)
    strict_rules = read_tsv(STRICT_RULES_IN)
    local_edges = read_tsv(LOCAL_EDGES_IN)
    action_frames = read_tsv(ACTION_FRAMES_IN)
    register_rows = read_tsv(REGISTER_ONLY)
    event_rows = read_tsv(EVENT_PAIRS)
    new_rows = read_tsv(NEW_EVENT_PAIRS)
    carriers = read_tsv(EINSTELLEN_CARRIERS)
    statuses = read_tsv(CLOSURE_STATUS)
    capacities = read_tsv(CAPACITY)
    cycles = read_tsv(HALTEN_CYCLE)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    record_map = {row["record_id"]: row for row in records}
    event_map = {row["backprojection_id"]: row for row in events}
    strict_pair_map = {row["pair_id"]: row for row in strict_pairs}
    strict_rule_map = {row["rule_id"]: row for row in strict_rules}

    check("source_record_count_135", len(records) == 135, len(records))
    check("source_event_count_183", len(events) == 183, len(events))
    check("source_strict_pair_count_48", len(strict_pairs) == 48, len(strict_pairs))
    check("source_strict_rule_count_29", len(strict_rules) == 29, len(strict_rules))
    check("source_local_edge_count_13", len(local_edges) == 13, len(local_edges))
    check("source_action_frame_count_104", len(action_frames) == 104, len(action_frames))
    check("register_only_count_1", len(register_rows) == 1, len(register_rows))
    check("event_pair_count_5", len(event_rows) == 5, len(event_rows))
    check("new_event_pair_count_3", len(new_rows) == 3, len(new_rows))
    check("carrier_count_2", len(carriers) == 2, len(carriers))
    check("status_count_2", len(statuses) == 2, len(statuses))
    check("capacity_count_2", len(capacities) == 2, len(capacities))
    check("cycle_count_1", len(cycles) == 1, len(cycles))

    register = register_rows[0]
    check("register_pair_id_exact", register["relaxed_pair_id"] == "G488-RP01")
    check("register_pair_records_exact", (register["source_record_id"], register["target_record_id"]) == ("G475-R035", "G475-R129"))
    check("register_pair_components_exact", (register["component_a"], register["component_b"]) == ("BAHN", "HALTEN"))
    check("register_pair_pages_exact", (register["source_physical_page"], register["target_physical_page"]) == ("f72r", "f89r"))
    check("register_pair_registers_exact", (register["source_register"], register["target_register"]) == ("CELESTIAL", "PHARMA"))
    check("register_pair_frame_exact", register["active_model_sequence"] == "INSTRUCTION" and register["fluent_frame_class"] == "INSTRUCTION_SETZEN" and register["event_boundary_shape"] == "3:DOT|DOT")
    check("register_pair_wildcard_exact", register["wildcard_component_frame"] == "SETZEN · * · {N1}")
    check("register_pair_ordinal_2", register["changed_flat_component_ordinal"] == "2")
    check("register_pair_all_fixed_flags", all(register[key] == "YES" for key in ("same_active_model", "same_readable_frame_class", "same_event_boundary_shape", "single_functional_component_delta", "only_register_relaxed")))
    check("register_pair_cues_visible", register["component_a_cue_visible"] == "YES" and register["component_b_cue_visible"] == "YES")
    check("register_pair_source_rows_exist", register["source_record_id"] in record_map and register["target_record_id"] in record_map)
    check("register_pair_surfaces_exact", register["source_surface_sequence"] == record_map[register["source_record_id"]]["surface_sequence"] and register["target_surface_sequence"] == record_map[register["target_record_id"]]["surface_sequence"])
    check("register_pair_readings_exact", register["source_fluent_reading_de"] == record_map[register["source_record_id"]]["fluent_reading_de"] and register["target_fluent_reading_de"] == record_map[register["target_record_id"]]["fluent_reading_de"])

    event_sets = {frozenset((row["source_event_id"], row["target_event_id"])) for row in event_rows}
    new_sets = {frozenset((row["source_event_id"], row["target_event_id"])) for row in new_rows}
    check("event_sets_exact", event_sets == EXPECTED_EVENT_SETS, sorted(map(sorted, event_sets)))
    check("new_event_sets_exact", new_sets == EXPECTED_NEW_EVENT_SETS, sorted(map(sorted, new_sets)))
    check("event_ids_unique", len({row["event_pair_id"] for row in event_rows}) == 5)
    check("new_projection_ids_unique", len({row["new_projection_id"] for row in new_rows}) == 3)
    check("projection_profile_exact", Counter(row["projection_class"] for row in event_rows) == Counter({"NEW_EVENT_CONTEXT_PROJECTION": 3, "GDT486_STRICT_PAIR_SHADOW": 2}))
    check("new_rows_class_exact", all(row["projection_class"] == "NEW_EVENT_CONTEXT_PROJECTION" and row["record_context_only_relaxed"] == "YES" for row in new_rows))
    check("shadow_rows_class_exact", all(row["record_context_only_relaxed"] == "NO" and row["gdt486_pair_id"] in {"G486-P040", "G486-P041"} for row in event_rows if row["projection_class"] == "GDT486_STRICT_PAIR_SHADOW"))
    check("new_rows_no_strict_pair", all(row["gdt486_pair_id"] == "NONE" for row in new_rows))
    check("event_component_pairs_exact", Counter(tuple(sorted((row["component_a"], row["component_b"]))) for row in event_rows) == Counter({("DANACH", "HALTEN"): 1, ("HALTEN", "SETZEN"): 2, ("HALTEN", "ZIELORT"): 1, ("EINSTELLEN", "HIER"): 1}))
    check("new_component_pairs_exact", Counter(tuple(sorted((row["component_a"], row["component_b"]))) for row in new_rows) == Counter({("DANACH", "HALTEN"): 1, ("HALTEN", "SETZEN"): 2}))
    check("new_pairs_same_page", all(row["same_page"] == "YES" for row in new_rows))
    check("new_pairs_same_record_profile", Counter(row["same_record"] for row in new_rows) == Counter({"YES": 2, "NO": 1}))
    check("all_event_cues_visible", all(row["component_a_cue_visible"] == "YES" and row["component_b_cue_visible"] == "YES" for row in event_rows))
    check("all_event_single_delta", all(row["single_functional_component_delta"] == "YES" for row in event_rows))

    event_gate_ok = True
    event_source_ok = True
    event_wildcard_ok = True
    for row in event_rows:
        source = event_map[row["source_event_id"]]
        target = event_map[row["target_event_id"]]
        source_tokens = source["semantic_tokens"].split("|")
        target_tokens = target["semantic_tokens"].split("|")
        differences = [index for index, pair in enumerate(zip(source_tokens, target_tokens)) if pair[0] != pair[1]]
        event_gate_ok &= source["register"] == target["register"] == row["register"]
        event_gate_ok &= source["active_model"] == target["active_model"] == row["active_model"]
        event_gate_ok &= source["semantic_separators"] == target["semantic_separators"] == row["semantic_separators"]
        event_gate_ok &= len(source_tokens) == len(target_tokens) and len(differences) == 1
        event_gate_ok &= differences and differences[0] + 1 == int(row["changed_component_ordinal"])
        event_gate_ok &= not source_tokens[differences[0]].startswith("{") and not target_tokens[differences[0]].startswith("{")
        event_source_ok &= row["source_record_id"] == source["record_id"] and row["target_record_id"] == target["record_id"]
        event_source_ok &= row["source_surface"] == source["surface"] and row["target_surface"] == target["surface"]
        event_source_ok &= row["source_event_reading_de"] == source["current_event_reading_de"] and row["target_event_reading_de"] == target["current_event_reading_de"]
        wildcard = list(source_tokens)
        wildcard[differences[0]] = "*"
        separators = [] if source["semantic_separators"] == "NONE" else source["semantic_separators"].split("|")
        rendered = wildcard[0]
        for separator, token in zip(separators, wildcard[1:]):
            rendered += (" · " if separator == "DOT" else " / ") + token
        event_wildcard_ok &= row["wildcard_event_frame"] == rendered
    check("event_pair_gates_recomputed", event_gate_ok)
    check("event_sources_recomputed", event_source_ok)
    check("event_wildcards_recomputed", event_wildcard_ok)

    carrier_map = {row["event_id"]: row for row in carriers}
    check("carrier_events_exact", set(carrier_map) == {"G485-E118", "G485-E133"})
    check("carrier_ids_unique", len({row["carrier_id"] for row in carriers}) == 2)
    check("carrier_recipes_exact", (carrier_map["G485-E118"]["working_recipe"], carrier_map["G485-E133"]["working_recipe"]) == ("CH+T", "CH+T+Y"))
    check("carrier_contexts_exact", (carrier_map["G485-E118"]["action_context_frame"], carrier_map["G485-E133"]["action_context_frame"]) == ("CH+@ACTION", "CH+@ACTION+Y"))
    check("carrier_external_match_exact", carrier_map["G485-E118"]["exact_gdt428_tr_frame"] == "CH+@ACTION" and carrier_map["G485-E133"]["exact_gdt428_tr_frame"] == "NONE")
    check("carrier_external_counts_exact", (carrier_map["G485-E118"]["gdt428_t_event_count"], carrier_map["G485-E118"]["gdt428_r_event_count"]) == ("1", "1"))
    check("carrier_strict_role_exact", carrier_map["G485-E118"]["strict_gdt486_contrast_role"] == "NONE" and carrier_map["G485-E133"]["strict_gdt486_contrast_role"] == "G486-P041")
    check("carrier_pages_registers_exact", {(row["physical_page"], row["register"]) for row in carriers} == {("f72r", "CELESTIAL"), ("f88v", "PHARMA")})
    check("carrier_cues_visible", all(row["einstellen_cue_visible"] == "YES" and row["independent_local_carrier"] == "YES" for row in carriers))
    check("carrier_sources_exact", all(row["semantic_tokens"] == event_map[row["event_id"]]["semantic_tokens"] and row["current_event_reading_de"] == event_map[row["event_id"]]["current_event_reading_de"] for row in carriers))
    check("gdt428_context_frame_exists", any(row["contrast_pair"] == "T~R" and row["frozen_frame"] == "CH+@ACTION" and row["left_event_count"] == "1" and row["right_event_count"] == "1" for row in action_frames))

    status_map = {row["endpoint"]: row for row in statuses}
    capacity_map = {row["endpoint"]: row for row in capacities}
    check("status_endpoints_exact", set(status_map) == {"EINSTELLEN", "HALTEN"})
    check("capacity_endpoints_exact", set(capacity_map) == {"EINSTELLEN", "HALTEN"})
    check("status_ids_unique", len({row["endpoint_id"] for row in statuses}) == 2)
    check("capacity_ids_unique", len({row["capacity_id"] for row in capacities}) == 2)
    check("einstellen_status_exact", status_map["EINSTELLEN"]["closure_status"] == "CAPACITY_LIMITED_ENDPOINT_RETAINED" and status_map["EINSTELLEN"]["full_cycle_closed"] == "NO" and status_map["EINSTELLEN"]["new_contrast_neighbours"] == "NONE")
    check("halten_status_exact", status_map["HALTEN"]["closure_status"] == "FULL_ALTERNATE_CYCLE_CLOSED" and status_map["HALTEN"]["full_cycle_closed"] == "YES" and set(status_map["HALTEN"]["new_contrast_neighbours"].split("|")) == {"BAHN", "DANACH", "SETZEN"})
    check("status_strict_rules_exact", status_map["EINSTELLEN"]["strict_singleton_rule_id"] == "G486-CR17" and status_map["HALTEN"]["strict_singleton_rule_id"] == "G486-CR24")
    check("status_no_meaning_change", all(row["meaning_change"] == "NO" for row in statuses))
    check("capacity_local_counts_exact", (capacity_map["EINSTELLEN"]["local_event_count"], capacity_map["HALTEN"]["local_event_count"]) == ("2", "12"))
    check("capacity_new_counts_exact", (capacity_map["EINSTELLEN"]["one_relaxation_new_pair_count"], capacity_map["HALTEN"]["one_relaxation_new_pair_count"]) == ("0", "4"))
    check("capacity_decisions_exact", capacity_map["EINSTELLEN"]["capacity_decision"] == "NO_SECOND_LOCAL_CONTRAST_CAPACITY" and capacity_map["HALTEN"]["capacity_decision"] == "NEW_CYCLE_CAPACITY")
    check("capacity_pages_exact", set(capacity_map["EINSTELLEN"]["local_pages"].split("|")) == {"f72r", "f88v"} and set(capacity_map["HALTEN"]["local_pages"].split("|")) == {"f71v", "f72r", "f89r"})

    cycle = cycles[0]
    check("cycle_id_exact", cycle["cycle_id"] == "G488-HC01")
    check("cycle_endpoint_exact", cycle["endpoint"] == "HALTEN")
    check("cycle_singleton_exact", cycle["singleton_rule_id"] == "G486-CR24" and strict_rule_map["G486-CR24"]["pair_count"] == "1")
    check("cycle_new_edge_exact", cycle["new_edge_id"] == "G488-RP01" and cycle["new_edge_record_pair"] == "G475-R035~G475-R129")
    check("cycle_bridge_exact", cycle["recurrent_bridge_rule_id"] == "G486-CR05" and cycle["recurrent_bridge_edge"] == "BAHN~ZIELORT" and cycle["recurrent_bridge_pair_count"] == "2")
    check("cycle_bridge_source_exact", any(row["source_rule_id"] == "G486-CR05" and {row["component_a"], row["component_b"]} == {"BAHN", "ZIELORT"} and row["pair_count"] == "2" for row in local_edges))
    check("cycle_path_exact", cycle["alternate_path_excluding_singleton"] == "HALTEN → BAHN → ZIELORT" and cycle["alternate_path_edge_count"] == "2")
    check("cycle_complete_no_remap", cycle["alternate_path_complete"] == "YES" and cycle["dictionary_remap_required"] == "NO")

    check("readable_core_counts", "**1**" in readable and "**5**" in readable and "**3** neu" in readable)
    check("readable_cycle_exact", "HALTEN —G488 REGISTER_ONLY→ BAHN —G486 RECURRENT→ ZIELORT" in readable)
    check("readable_all_new_events", all(event_id in readable for pair in EXPECTED_NEW_EVENT_SETS for event_id in pair))
    check("readable_both_carriers", all(event_id in readable for event_id in ("G485-E118", "G485-E133")))
    check("readable_capacity_statement", "null** neue EINSTELLEN-Kontraste" in readable and "kapazitätsbegrenzt" in readable)
    check("readable_next_route", "Kompositionsumfeld" in readable and "WERT, ANTEIL, ZIELORT, FORTSETZEN und POSTEN" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_source_counts_exact", (result.get("record_count"), result.get("event_count"), result.get("endpoint_count")) == (135, 183, 2))
    check("result_local_counts_exact", (result.get("einstellen_local_event_count"), result.get("halten_local_event_count")) == (2, 12))
    check("result_pair_counts_exact", (result.get("register_only_endpoint_pair_count"), result.get("endpoint_event_pair_count"), result.get("new_event_projection_pair_count"), result.get("strict_event_shadow_pair_count")) == (1, 5, 3, 2))
    check("result_neighbours_exact", result.get("halten_new_contrast_neighbour_count") == 3 and set(result.get("halten_new_contrast_neighbours", [])) == {"BAHN", "DANACH", "SETZEN"})
    check("result_closure_counts_exact", (result.get("halten_full_cycle_count"), result.get("einstellen_full_cycle_count"), result.get("closed_endpoint_count"), result.get("capacity_limited_endpoint_count")) == (1, 0, 1, 1))
    check("result_external_carrier_count_1", result.get("einstellen_exact_gdt428_carrier_frame_match_count") == 1)
    check("result_all_cues_visible", result.get("all_pair_meaning_cues_visible") is True)
    unchanged = ("meaning_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "One-condition relaxation" in result.get("claim_ceiling", "") and "no new meaning" in result.get("claim_ceiling", ""))

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
