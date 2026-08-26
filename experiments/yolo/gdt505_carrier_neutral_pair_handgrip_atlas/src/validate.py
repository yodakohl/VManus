#!/usr/bin/env python3
"""Independently validate all GDT505 carriers, handgrips and target mappings."""

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
BASE = ROOT / "experiments/yolo/gdt505_carrier_neutral_pair_handgrip_atlas"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G421 = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license/artifacts"
G504 = ROOT / "experiments/yolo/gdt504_semantic_delta_phrase_consistency_atlas/artifacts"

DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
PAIR_PROFILES_IN = G421 / "gdt421_81_ordered_pair_profiles.tsv"
TARGETS_IN = G504 / "gdt504_46_semantic_delta_cards.tsv"
HANDGRIPS_OUT = ART / "gdt505_5_carrier_neutral_handgrips.tsv"
CARRIERS_OUT = ART / "gdt505_55_exact_pair_carriers.tsv"
REGISTER_OUT = ART / "gdt505_15_observed_pair_register_cells.tsv"
TARGET_OUT = ART / "gdt505_11_target_pair_handgrip_cards.tsv"
BETWEEN_OUT = ART / "gdt505_15_pair_between_pattern_summary.tsv"
FRAME_OUT = ART / "gdt505_16_frame_atom_coverage.tsv"
READABLE_OUT = ART / "GDT505_CARRIER_NEUTRAL_PAIR_HANDGRIP_ATLAS.md"
RESULT_OUT = ART / "gdt505_result.json"
VALIDATION_OUT = ART / "gdt505_validation.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
PAIR_ORDER = ("P+CH", "S+CHD", "CH+P", "CH+CH", "CH+SH")
PHRASES = {
    "P+CH": "Setze das zuvor Genannte ein und nimm es.",
    "S+CHD": "Wähle das zuvor Genannte und bearbeite es.",
    "CH+P": "Nimm das zuvor Genannte und setze es ein.",
    "CH+CH": "Nimm das zuvor Genannte zweimal.",
    "CH+SH": "Nimm das zuvor Genannte und halte es.",
}
MARKERS = {"P": "setz", "S": "wähl", "CHD": "bearbeit", "CH": "nimm", "SH": "halt"}
STATUS = "FIVE_HANDGRIPS_SURVIVE_ALL_FIFTY_FIVE_OLD_CARRIERS__ELEVEN_TARGETS_MAPPED"
GUARD = "CARRIER_NEUTRAL_ACTION_ORDER_ONLY__FOREIGN_FRAME_VALUES_NOT_TRANSFERRED"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def action_indices(recipe: list[str], pair: str) -> list[int]:
    result: list[int] = []
    start = 0
    for action in pair.split("+"):
        position = recipe.index(action, start)
        result.append(position)
        start = position + 1
    return result


def marker_positions(phrase: str, pair: str, compressed: bool = False) -> list[int]:
    text = phrase.casefold()
    if compressed and pair == "CH+CH":
        first = text.find("nimm")
        return [first, text.find("zweimal", first + 1)]
    result: list[int] = []
    start = 0
    for action in pair.split("+"):
        position = text.find(MARKERS[action], start)
        result.append(position)
        start = position + 1 if position >= 0 else start
    return result


def arg_mode(row: dict[str, str]) -> str:
    if row["explicit_argument_roots"] != "NONE":
        return "EXPLICIT_ARGUMENTS"
    return "INHERITED_ARGUMENT" if row["inherited_argument_root"] != "NONE" else "ARGUMENT_FREE"


def main() -> int:
    dict_fields, dictionary = read_tsv(DICTIONARY_IN)
    clause_fields, clauses = read_tsv(CLAUSES_IN)
    profile_fields, profiles = read_tsv(PAIR_PROFILES_IN)
    target_source_fields, target_source = read_tsv(TARGETS_IN)
    handgrip_fields, handgrips = read_tsv(HANDGRIPS_OUT)
    carrier_fields, carriers = read_tsv(CARRIERS_OUT)
    register_fields, register_rows = read_tsv(REGISTER_OUT)
    target_fields, target_rows = read_tsv(TARGET_OUT)
    between_fields, between_rows = read_tsv(BETWEEN_OUT)
    frame_fields, frame_rows = read_tsv(FRAME_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("all_table_counts_exact", (len(dictionary), len(clauses), len(profiles), len(target_source), len(handgrips), len(carriers), len(register_rows), len(target_rows), len(between_rows), len(frame_rows)) == (46, 4576, 81, 46, 5, 55, 15, 11, 15, 16), "46/4576/81/46 -> 5/55/15/11/15/16")
    check("input_schemas_complete", {"atom", "working_value_de"} <= set(dict_fields) and {"explicit_action_roots", "component_recipe", "imperative_clause_de"} <= set(clause_fields) and {"ordered_pair", "event_count"} <= set(profile_fields) and {"support_depth", "target_action_recipe"} <= set(target_source_fields), "four input schemas")
    check("output_schemas_complete", {"handgrip_id", "ordered_action_pair", "old_carrier_event_count"} <= set(handgrip_fields) and {"pair_carrier_id", "before_action_atoms", "between_action_atoms", "after_action_atoms"} <= set(carrier_fields) and {"pair_register_cell_id", "register"} <= set(register_fields) and {"target_handgrip_card_id", "handgrip_projection_class"} <= set(target_fields) and {"between_pattern_id", "between_action_atoms"} <= set(between_fields) and {"frame_atom", "carrier_mention_count"} <= set(frame_fields), "six output schemas")
    check("handgrip_ids_exact", [row["handgrip_id"] for row in handgrips] == [f"G505-H{i:02d}" for i in range(1, 6)], "H01..H05")
    check("carrier_ids_exact", [row["pair_carrier_id"] for row in carriers] == [f"G505-C{i:02d}" for i in range(1, 56)], "C01..C55")
    check("register_ids_exact", [row["pair_register_cell_id"] for row in register_rows] == [f"G505-R{i:02d}" for i in range(1, 16)], "R01..R15")
    check("target_ids_exact", [row["target_handgrip_card_id"] for row in target_rows] == [f"G505-T{i:02d}" for i in range(1, 12)], "T01..T11")
    check("between_ids_exact", [row["between_pattern_id"] for row in between_rows] == [f"G505-B{i:02d}" for i in range(1, 16)], "B01..B15")
    check("handgrip_pair_order_exact", [row["ordered_action_pair"] for row in handgrips] == list(PAIR_ORDER), "five fixed pairs")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    profiles_by_pair = {row["ordered_pair"]: row for row in profiles}
    selected_clauses = [row for row in clauses if row["explicit_action_roots"].replace("|", "+") in PAIR_ORDER]
    selected_targets = [row for row in target_source if row["support_depth"] == "PAIR_BACKBONE_FRAME_EDIT"]
    check("source_selections_exact", len(selected_clauses) == 55 and len(selected_targets) == 11, "55 old carriers/11 targets")

    carriers_by_event = {row["global_running_event_id"]: row for row in carriers}
    carriers_by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    frame_mentions: Counter[str] = Counter()
    frame_events: dict[str, set[str]] = defaultdict(set)
    frame_pairs: dict[str, set[str]] = defaultdict(set)
    frame_registers: dict[str, set[str]] = defaultdict(set)
    argument_modes: Counter[str] = Counter()
    for index, source in enumerate(selected_clauses, start=1):
        prefix = f"carrier_{index:02d}"
        row = carriers_by_event[source["global_running_event_id"]]
        pair = source["explicit_action_roots"].replace("|", "+")
        recipe = source["component_recipe"].split("+")
        positions = action_indices(recipe, pair)
        before = recipe[: positions[0]]
        between = recipe[positions[0] + 1 : positions[1]]
        after = recipe[positions[1] + 1 :]
        frame = before + between + after
        phrase_positions = marker_positions(source["imperative_clause_de"], pair)
        order_exact = len(phrase_positions) == 2 and phrase_positions[0] >= 0 and phrase_positions[1] > phrase_positions[0]
        mode = arg_mode(source)
        argument_modes[mode] += 1
        carriers_by_pair[pair].append(row)
        for atom in frame:
            frame_mentions[atom] += 1
            frame_events[atom].add(source["global_running_event_id"])
            frame_pairs[atom].add(pair)
            frame_registers[atom].add(source["register"])
        check(f"{prefix}_source_exact", row["pair_carrier_id"] == f"G505-C{index:02d}" and row["ordered_action_pair"] == pair and row["global_running_event_id"] == source["global_running_event_id"] and row["physical_page"] == source["physical_page"] and row["register"] == source["register"] and row["component_recipe"] == source["component_recipe"] and row["imperative_clause_de"] == source["imperative_clause_de"], source["global_running_event_id"])
        check(f"{prefix}_recipe_split_exact", row["action_component_positions"] == ",".join(str(position + 1) for position in positions) and row["before_action_atoms"] == ("+".join(before) or "NONE") and row["between_action_atoms"] == ("+".join(between) or "NONE") and row["after_action_atoms"] == ("+".join(after) or "NONE") and row["frame_atom_trace"] == ("+".join(frame) or "NONE"), f"before={before},between={between},after={after}")
        check(f"{prefix}_phrase_order_exact", row["clause_action_marker_positions"] == ",".join(str(position + 1) for position in phrase_positions) and row["clause_action_order_exact"] == ("YES" if order_exact else "NO") == "YES", str(phrase_positions))
        check(f"{prefix}_frame_values_exact", row["frame_value_trace_de"] == (" · ".join(values[atom] for atom in frame) or "NONE") and row["direct_component_adjacency"] == ("YES" if not between else "NO"), row["frame_value_trace_de"])
        check(f"{prefix}_argument_exact", row["argument_mode"] == mode and row["explicit_argument_roots"] == source["explicit_argument_roots"] and row["inherited_argument_root"] == source["inherited_argument_root"], mode)
        check(f"{prefix}_handgrip_exact", row["portable_action_trace_de"] == " → ".join(values[action] for action in pair.split("+")) and row["carrier_neutral_handgrip_de"] == PHRASES[pair], PHRASES[pair])
        check(f"{prefix}_guards_exact", row["roundtrip_exact"] == "YES" and row["working_root_meaning_changed"] == row["surface_prediction_made"] == row["occurrence_prediction_made"] == "NO" and row["guard"] == GUARD, GUARD)

    handgrip_by_pair = {row["ordered_action_pair"]: row for row in handgrips}
    for pair in PAIR_ORDER:
        row = handgrip_by_pair[pair]
        group = carriers_by_pair[pair]
        profile = profiles_by_pair[pair]
        registers = {item["register"] for item in group}
        patterns = {item["between_action_atoms"] for item in group}
        frame_atoms = {atom for item in group for atom in item["frame_atom_trace"].split("+") if atom != "NONE"}
        modes = Counter(item["argument_mode"] for item in group)
        check(f"handgrip_{pair}_identity", row["carrier_neutral_handgrip_de"] == PHRASES[pair] and row["portable_action_trace_de"] == " → ".join(values[action] for action in pair.split("+")) and row["gdt421_status"] == "PAIR_ATTESTED", PHRASES[pair])
        check(f"handgrip_{pair}_counts", int(row["old_carrier_event_count"]) == len(group) == int(profile["event_count"]) and int(row["old_recipe_type_count"]) == len({item["component_recipe"] for item in group}) == int(profile["exact_recipe_type_count"]) and int(row["old_register_count"]) == len(registers) == int(profile["register_count"]), f"events={len(group)}")
        check(f"handgrip_{pair}_frame_counts", int(row["direct_adjacency_event_count"]) == sum(item["direct_component_adjacency"] == "YES" for item in group) and int(row["separated_action_event_count"]) == sum(item["direct_component_adjacency"] == "NO" for item in group) and int(row["between_pattern_count"]) == len(patterns) and int(row["frame_atom_family_count"]) == len(frame_atoms), f"patterns={patterns}")
        check(f"handgrip_{pair}_argument_counts", int(row["explicit_argument_event_count"]) == modes["EXPLICIT_ARGUMENTS"] and int(row["inherited_argument_event_count"]) == modes["INHERITED_ARGUMENT"] and int(row["argument_free_event_count"]) == modes["ARGUMENT_FREE"], str(modes))
        check(f"handgrip_{pair}_guards", row["all_old_clause_action_orders_exact"] == row["all_old_roundtrips_exact"] == "YES" and row["working_root_meaning_changed"] == "NO" and row["guard"] == GUARD, GUARD)
        check(f"handgrip_{pair}_readable", PHRASES[pair] in readable and pair in readable, pair)

    expected_register_cells = [(pair, register) for pair in PAIR_ORDER for register in REGISTERS if any(row["register"] == register for row in carriers_by_pair[pair])]
    check("register_cell_keys_exact", [(row["ordered_action_pair"], row["register"]) for row in register_rows] == expected_register_cells, str(expected_register_cells))
    for index, row in enumerate(register_rows, start=1):
        group = [item for item in carriers_by_pair[row["ordered_action_pair"]] if item["register"] == row["register"]]
        check(f"register_{index:02d}_counts", int(row["old_carrier_event_count"]) == len(group) and int(row["old_recipe_type_count"]) == len({item["component_recipe"] for item in group}) and int(row["direct_adjacency_event_count"]) + int(row["separated_action_event_count"]) == len(group) and row["all_clause_action_orders_exact"] == "YES" and row["guard"] == GUARD, f"events={len(group)}")

    target_by_source = {row["source_gdt504_delta_card_id"]: row for row in target_rows}
    carrier_pair_register_counts = Counter((row["ordered_action_pair"], row["register"]) for row in carriers)
    for index, source in enumerate(selected_targets, start=1):
        row = target_by_source[source["semantic_delta_card_id"]]
        pair = "+".join(atom for atom in source["target_action_recipe"].split("+") if atom in ACTION_ROOTS)
        positions = marker_positions(source["target_current_default_phrase_de"], pair, pair == "CH+CH")
        target_register_count = carrier_pair_register_counts[(pair, source["target_register"])]
        expected_projection = "TARGET_REGISTER_OLD_HANDGRIP" if target_register_count else "CROSS_REGISTER_OLD_HANDGRIP"
        check(f"target_{index:02d}_source_exact", row["target_handgrip_card_id"] == f"G505-T{index:02d}" and row["source_gdt504_delta_card_id"] == source["semantic_delta_card_id"] and row["target_action_recipe"] == source["target_action_recipe"] and row["target_register"] == source["target_register"] and row["target_current_default_phrase_de"] == source["target_current_default_phrase_de"], source["semantic_delta_card_id"])
        check(f"target_{index:02d}_handgrip_exact", row["ordered_action_pair"] == pair and row["carrier_neutral_handgrip_de"] == PHRASES[pair] and row["target_phrase_handgrip_marker_positions"] == ",".join(str(position + 1) for position in positions) and row["target_phrase_handgrip_visible"] == "YES", str(positions))
        check(f"target_{index:02d}_support_exact", int(row["old_pair_carrier_event_count"]) == len(carriers_by_pair[pair]) and int(row["target_register_old_pair_event_count"]) == target_register_count and row["handgrip_projection_class"] == expected_projection, expected_projection)
        check(f"target_{index:02d}_guards", row["foreign_carrier_frame_transferred"] == row["target_phrase_changed"] == row["working_root_meaning_changed"] == row["surface_prediction_made"] == row["occurrence_prediction_made"] == "NO" and row["target_evidence_status_retained"] == "COMPOSED_WORKING" and row["guard"] == GUARD, GUARD)
        check(f"target_{index:02d}_readable", source["target_current_default_phrase_de"] in readable and expected_projection in readable, source["semantic_delta_card_id"])

    expected_between = [(pair, pattern) for pair in PAIR_ORDER for pattern in sorted({row["between_action_atoms"] for row in carriers_by_pair[pair]})]
    check("between_keys_exact", [(row["ordered_action_pair"], row["between_action_atoms"]) for row in between_rows] == expected_between, str(expected_between))
    for index, row in enumerate(between_rows, start=1):
        group = [item for item in carriers_by_pair[row["ordered_action_pair"]] if item["between_action_atoms"] == row["between_action_atoms"]]
        expected_values = "NONE" if row["between_action_atoms"] == "NONE" else " · ".join(values[atom] for atom in row["between_action_atoms"].split("+"))
        check(f"between_{index:02d}_exact", int(row["carrier_event_count"]) == len(group) and row["between_value_trace_de"] == expected_values and row["direct_component_adjacency"] == ("YES" if row["between_action_atoms"] == "NONE" else "NO") and row["all_clause_action_orders_exact"] == "YES" and row["guard"] == GUARD, f"events={len(group)}")

    check("frame_atom_order_exact", [row["frame_atom"] for row in frame_rows] == sorted(frame_mentions), str(sorted(frame_mentions)))
    for row in frame_rows:
        atom = row["frame_atom"]
        check(f"frame_{atom}_exact", row["working_value_de"] == values[atom] and int(row["carrier_mention_count"]) == frame_mentions[atom] and int(row["carrier_event_count"]) == len(frame_events[atom]) and int(row["pair_count"]) == len(frame_pairs[atom]) and int(row["register_count"]) == len(frame_registers[atom]) and row["transferred_into_neutral_handgrip"] == "NO" and row["guard"] == GUARD, f"mentions={frame_mentions[atom]}")

    expected_result = {
        "status": STATUS,
        "carrier_neutral_handgrips": 5,
        "exact_old_pair_carriers": 55,
        "old_recipe_types": 45,
        "old_clause_forms": 50,
        "old_surfaces": 48,
        "old_pages": 20,
        "old_registers": 5,
        "old_owner_classes": 13,
        "direct_component_adjacency_events": 34,
        "separated_action_events": 21,
        "pair_specific_between_patterns": 15,
        "frame_atom_families": 16,
        "explicit_argument_events": 37,
        "inherited_argument_events": 16,
        "argument_free_events": 2,
        "old_clause_action_orders_exact": 55,
        "old_clause_roundtrips_exact": 55,
        "observed_pair_register_cells": 15,
        "mapped_gdt504_target_cards": 11,
        "target_register_old_handgrips": 4,
        "cross_register_old_handgrips": 7,
        "target_phrase_handgrips_visible": 11,
        "foreign_frame_values_transferred": 0,
        "target_phrase_changes": 0,
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    check("argument_mode_totals", argument_modes == Counter({"EXPLICIT_ARGUMENTS": 37, "INHERITED_ARGUMENT": 16, "ARGUMENT_FREE": 2}), str(argument_modes))
    check("result_exact", result == expected_result, json.dumps(expected_result, ensure_ascii=False, sort_keys=True))
    check("readable_status_guard_exact", STATUS in readable and GUARD in readable, "status and guard")

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
