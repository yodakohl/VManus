#!/usr/bin/env python3
"""Validate GDT492's owner-variant slot and exact family bridge atlas."""

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
BASE = ROOT / "experiments/yolo/gdt492_owner_variant_slot_bridge_atlas"
OUT = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G415 = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G491 = ROOT / "experiments/yolo/gdt491_markierungen_observed_phrase_contrast_atlas/artifacts"
RUN = BASE / "src/run.py"
COMPONENTS_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
REGISTER_ATLAS_IN = G415 / "gdt415_95_register_expansion_atlas.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
OWNER_VARIANTS_IN = G491 / "gdt491_4_owner_variant_contrast_cards.tsv"
SLOT_MATRIX = OUT / "gdt492_35_observed_register_slot_cells.tsv"
SLOT_OCCURRENCES = OUT / "gdt492_12_owner_variant_slot_occurrences.tsv"
FAMILY_CARRIERS = OUT / "gdt492_23_exact_frame_family_carriers.tsv"
ACTION_CELLS = OUT / "gdt492_17_exact_frame_action_cells.tsv"
ACTION_REGISTER_CELLS = OUT / "gdt492_19_action_register_phrase_cells.tsv"
ALTERNATE_CELLS = OUT / "gdt492_9_non_tr_action_cells.tsv"
REGISTER_BRIDGES = OUT / "gdt492_2_same_action_cross_register_bridges.tsv"
CARD_SUMMARIES = OUT / "gdt492_4_owner_variant_card_summaries.tsv"
READABLE = OUT / "GDT492_OWNER_VARIANT_SLOT_BRIDGE_ATLAS.md"
RESULT = OUT / "gdt492_result.json"
VALIDATION = OUT / "gdt492_validation.json"
STATUS = "FOUR_OWNER_VARIANTS_DECOMPOSED__THIRTY_FIVE_SLOT_CELLS_OBSERVED__NINE_ALTERNATE_ACTION_CELLS"
FRAMES = ("@ACTION+AL+Y", "@ACTION+CH+E+Y", "@ACTION+OR+Y", "CH+@ACTION")
ROOTS = ("T", "R", "AL", "Y", "CH", "E", "OR")
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
EXPECTED_EXPANSIONS = {
    "T": ("FESTLEGEN", "ARBEITSSTUFE EINSTELLEN", "STATIONSWERT EINSTELLEN", "WERT EINSTELLEN", "ANSATZWERT EINSTELLEN"),
    "R": ("KENNZEICHNEN", "TEIL MARKIEREN", "STATION MARKIEREN", "POSITION MARKIEREN", "POSTEN MARKIEREN"),
    "AL": ("ZIELSPALTE", "ZIELSTELLE", "ZIELSTATION", "ZIELPOSITION", "ZIELGEFÄSS"),
    "Y": ("LAUFENDER EINTRAG", "PFLANZENPOSTEN", "STATIONSPOSTEN", "POSITIONSPOSTEN", "DROGENPOSTEN"),
    "CH": ("ENTNEHMEN", "PFLANZENTEIL NEHMEN", "POSTEN ENTNEHMEN", "POSITION AUFNEHMEN", "DROGENPOSTEN NEHMEN"),
    "E": ("GRAD I", "GRAD I", "GRAD I", "GRAD I", "GRAD I"),
    "OR": ("EINTRAGSEINHEIT", "ARBEITSEINHEIT", "STATIONSEINHEIT", "POSITIONSEINHEIT", "ANSATZEINHEIT"),
}
EXPECTED_EVENTS = {
    "T": (27, 103, 105, 38, 22),
    "R": (6, 14, 61, 14, 19),
    "AL": (7, 50, 177, 71, 43),
    "Y": (70, 307, 804, 168, 196),
    "CH": (57, 215, 255, 92, 151),
    "E": (32, 75, 548, 121, 189),
    "OR": (11, 95, 79, 30, 47),
}
EXPECTED_CARD_COUNTS = {
    "@ACTION+AL+Y": (3, 2, 2, 0, 10, 4, 2, 6, 6, 3, 7),
    "@ACTION+CH+E+Y": (4, 3, 2, 1, 5, 5, 3, 5, 5, 3, 3),
    "@ACTION+OR+Y": (3, 2, 2, 0, 4, 4, 2, 4, 4, 3, 3),
    "CH+@ACTION": (2, 1, 1, 0, 4, 4, 2, 4, 4, 3, 4),
}
EXPECTED_ACTION_ROOTS = {
    "@ACTION+AL+Y": ("OK", "CH", "T", "R"),
    "@ACTION+CH+E+Y": ("OK", "K", "S", "T", "R"),
    "@ACTION+OR+Y": ("SH", "S", "T", "R"),
    "CH+@ACTION": ("K", "S", "T", "R"),
}
EXPECTED_SELECTED_REGISTERS = {
    "@ACTION+AL+Y": ("CELESTIAL", "BIOLOGICAL"),
    "@ACTION+CH+E+Y": ("SOURCE_SECTION_T", "BIOLOGICAL"),
    "@ACTION+OR+Y": ("HERBAL", "BIOLOGICAL"),
    "CH+@ACTION": ("HERBAL", "BIOLOGICAL"),
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

    generated = [SLOT_MATRIX, SLOT_OCCURRENCES, FAMILY_CARRIERS, ACTION_CELLS, ACTION_REGISTER_CELLS, ALTERNATE_CELLS, REGISTER_BRIDGES, CARD_SUMMARIES, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT492 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    components = read_tsv(COMPONENTS_IN)
    register_atlas = read_tsv(REGISTER_ATLAS_IN)
    clauses = read_tsv(CLAUSES_IN)
    source_variants = read_tsv(OWNER_VARIANTS_IN)
    matrix = read_tsv(SLOT_MATRIX)
    slots = read_tsv(SLOT_OCCURRENCES)
    carriers = read_tsv(FAMILY_CARRIERS)
    action_cells = read_tsv(ACTION_CELLS)
    action_register_cells = read_tsv(ACTION_REGISTER_CELLS)
    alternates = read_tsv(ALTERNATE_CELLS)
    bridges = read_tsv(REGISTER_BRIDGES)
    cards = read_tsv(CARD_SUMMARIES)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    clause_map = {row["global_running_event_id"]: row for row in clauses}
    matrix_map = {(row["root"], row["register"]): row for row in matrix}
    card_map = {row["frozen_frame"]: row for row in cards}

    check("source_component_count_46", len(components) == 46, len(components))
    check("source_register_atlas_count_95", len(register_atlas) == 95, len(register_atlas))
    check("source_clause_count_4576", len(clauses) == 4576, len(clauses))
    check("source_owner_variant_count_4", len(source_variants) == 4, len(source_variants))
    check("source_owner_variant_order_exact", tuple(row["frozen_frame"] for row in source_variants) == FRAMES)
    check("matrix_count_35", len(matrix) == 35, len(matrix))
    check("slot_occurrence_count_12", len(slots) == 12, len(slots))
    check("family_carrier_count_23", len(carriers) == 23, len(carriers))
    check("action_cell_count_17", len(action_cells) == 17, len(action_cells))
    check("action_register_cell_count_19", len(action_register_cells) == 19, len(action_register_cells))
    check("alternate_cell_count_9", len(alternates) == 9, len(alternates))
    check("bridge_count_2", len(bridges) == 2, len(bridges))
    check("card_count_4", len(cards) == 4, len(cards))

    check("matrix_ids_unique", len({row["slot_cell_id"] for row in matrix}) == 35)
    check("matrix_root_register_unique", len(matrix_map) == 35)
    check("matrix_root_set_exact", {row["root"] for row in matrix} == set(ROOTS))
    check("matrix_register_set_exact", {row["register"] for row in matrix} == set(REGISTERS))
    check("matrix_full_cartesian", set(matrix_map) == {(root, register) for root in ROOTS for register in REGISTERS})
    check("matrix_all_observed", all(row["observed_old_slot_cell"] == "YES" and int(row["event_count"]) > 0 for row in matrix))
    check("matrix_expansions_exact", all(matrix_map[(root, register)]["owner_local_expansion_de"] == EXPECTED_EXPANSIONS[root][REGISTERS.index(register)] for root in ROOTS for register in REGISTERS))
    check("matrix_event_counts_exact", all(int(matrix_map[(root, register)]["event_count"]) == EXPECTED_EVENTS[root][REGISTERS.index(register)] for root in ROOTS for register in REGISTERS))
    check("matrix_mentions_cover_events", all(int(row["mention_count"]) >= int(row["event_count"]) for row in matrix))
    check("matrix_pages_positive", all(int(row["page_count"]) > 0 for row in matrix))
    check("matrix_owners_positive", all(int(row["owner_count"]) > 0 and int(row["owner_class_count"]) > 0 for row in matrix))
    check("matrix_e_source_exact", all(row["source_atlas"] == "GDT413_COMPONENT_PLUS_GDT416_OBSERVED_CARRIERS" for row in matrix if row["root"] == "E"))
    check("matrix_core_source_exact", all(row["source_atlas"] == "GDT415_REGISTER_EXPANSION_ATLAS" for row in matrix if row["root"] != "E"))
    check("matrix_e_stable", {row["owner_local_expansion_de"] for row in matrix if row["root"] == "E"} == {"GRAD I"})

    check("slot_ids_unique", len({row["slot_occurrence_id"] for row in slots}) == 12)
    check("slot_card_set_exact", {row["frozen_frame"] for row in slots} == set(FRAMES))
    check("slot_profile_exact", Counter(row["frozen_frame"] for row in slots) == Counter(dict(zip(FRAMES, (3, 4, 3, 2)))))
    check("slot_ordinals_exact", all([int(row["slot_ordinal"]) for row in slots if row["frozen_frame"] == frame] == list(range(1, len(frame.split("+")) + 1)) for frame in FRAMES))
    check("slot_selected_registers_exact", all((row["t_register"], row["r_register"]) == EXPECTED_SELECTED_REGISTERS[row["frozen_frame"]] for row in slots))
    check("slot_matrix_values_exact", all(row["t_owner_local_expansion_de"] == matrix_map[(row["t_root"], row["t_register"])]["owner_local_expansion_de"] and row["r_owner_local_expansion_de"] == matrix_map[(row["r_root"], row["r_register"])]["owner_local_expansion_de"] for row in slots))
    check("slot_support_exact", all(row["t_register_event_support"] == matrix_map[(row["t_root"], row["t_register"])]["event_count"] and row["r_register_event_support"] == matrix_map[(row["r_root"], row["r_register"])]["event_count"] for row in slots))
    check("slot_action_count_4", sum(row["slot_relation"] == "ACTION_CONTRAST_WITH_OWNER_LOCAL_REALIZATIONS" for row in slots) == 4)
    check("slot_owner_variant_count_7", sum(row["slot_relation"] == "OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE" for row in slots) == 7)
    check("slot_register_stable_count_1", sum(row["slot_relation"] == "REGISTER_STABLE_REALIZATION" for row in slots) == 1)
    check("slot_stable_is_e", [row["frame_token"] for row in slots if row["slot_relation"] == "REGISTER_STABLE_REALIZATION"] == ["E"])
    check("slot_action_roots_tr", all((row["t_root"], row["r_root"]) == ("T", "R") for row in slots if row["frame_token"] == "@ACTION"))
    check("slot_nonaction_roots_same", all(row["t_root"] == row["r_root"] == row["frame_token"] for row in slots if row["frame_token"] != "@ACTION"))
    check("slot_all_cells_observed", all(row["both_slot_cells_observed"] == "YES" for row in slots))
    check("slot_no_new_value", all(row["new_slot_value_required"] == "NO" for row in slots))

    check("carrier_ids_unique", len({row["carrier_id"] for row in carriers}) == 23)
    check("carrier_event_ids_unique", len({row["global_running_event_id"] for row in carriers}) == 23)
    check("carrier_sources_exist", all(row["global_running_event_id"] in clause_map for row in carriers))
    check("carrier_identity_exact", all(row["global_statement_id"] == clause_map[row["global_running_event_id"]]["global_statement_id"] and row["physical_page"] == clause_map[row["global_running_event_id"]]["physical_page"] and row["surface"] == clause_map[row["global_running_event_id"]]["surface"] for row in carriers))
    check("carrier_recipe_exact", all(row["action_recipe"] == clause_map[row["global_running_event_id"]]["component_recipe"] and row["action_recipe"] == row["frozen_frame"].replace("@ACTION", row["action_root"]) for row in carriers))
    check("carrier_clause_exact", all(row["imperative_clause_de"] == clause_map[row["global_running_event_id"]]["imperative_clause_de"] for row in carriers))
    check("carrier_back_projection_exact", all(row["portable_back_projection_de"] == clause_map[row["global_running_event_id"]]["portable_back_projection_de"] for row in carriers))
    check("carrier_roundtrip_exact", all(row["roundtrip_exact"] == "YES" for row in carriers))
    check("carrier_observed_flags", all(row["observed_not_invented"] == "YES" for row in carriers))
    check("carrier_frame_profile_exact", Counter(row["frozen_frame"] for row in carriers) == Counter(dict(zip(FRAMES, (10, 5, 4, 4)))))
    check("carrier_register_count_5", len({row["register"] for row in carriers}) == 5)
    check("carrier_page_count_11", len({row["physical_page"] for row in carriers}) == 11)
    check("carrier_action_root_count_7", len({row["action_root"] for row in carriers}) == 7)
    check("carrier_clause_form_count_19", len({(row["frozen_frame"], row["imperative_clause_de"]) for row in carriers}) == 19)

    check("action_cell_ids_unique", len({row["action_cell_id"] for row in action_cells}) == 17)
    check("action_cell_key_unique", len({(row["frozen_frame"], row["action_root"]) for row in action_cells}) == 17)
    check("action_roots_by_frame_exact", all(tuple(row["action_root"] for row in action_cells if row["frozen_frame"] == frame) == EXPECTED_ACTION_ROOTS[frame] for frame in FRAMES))
    check("action_cell_events_total_23", sum(int(row["event_count"]) for row in action_cells) == 23)
    check("action_cell_counts_recompute", all(int(row["event_count"]) == sum(carrier["frozen_frame"] == row["frozen_frame"] and carrier["action_root"] == row["action_root"] for carrier in carriers) for row in action_cells))
    check("action_cell_registers_recompute", all(set(row["registers"].split("|")) == {carrier["register"] for carrier in carriers if carrier["frozen_frame"] == row["frozen_frame"] and carrier["action_root"] == row["action_root"]} for row in action_cells))
    check("action_cell_forms_recompute", all(set(row["observed_clauses_de"].split(" || ")) == {carrier["imperative_clause_de"] for carrier in carriers if carrier["frozen_frame"] == row["frozen_frame"] and carrier["action_root"] == row["action_root"]} for row in action_cells))
    check("action_cell_all_roundtrip", all(row["all_roundtrip_exact"] == "YES" for row in action_cells))
    check("action_cell_tr_count_8", sum(row["is_t_or_r"] == "YES" for row in action_cells) == 8)
    check("action_cell_alternate_count_9", sum(row["is_t_or_r"] == "NO" for row in action_cells) == 9)
    check("alternate_rows_exact_subset", alternates == [row for row in action_cells if row["is_t_or_r"] == "NO"])

    check("action_register_ids_unique", len({row["action_register_cell_id"] for row in action_register_cells}) == 19)
    check("action_register_keys_unique", len({(row["frozen_frame"], row["action_root"], row["register"]) for row in action_register_cells}) == 19)
    check("action_register_events_total_23", sum(int(row["event_count"]) for row in action_register_cells) == 23)
    check("action_register_cells_recompute", all(int(row["event_count"]) == sum(carrier["frozen_frame"] == row["frozen_frame"] and carrier["action_root"] == row["action_root"] and carrier["register"] == row["register"] for carrier in carriers) for row in action_register_cells))
    check("action_register_all_observed", all(row["observed_not_invented"] == "YES" for row in action_register_cells))

    check("bridge_ids_unique", len({row["bridge_id"] for row in bridges}) == 2)
    check("bridge_frame_exact", {row["frozen_frame"] for row in bridges} == {"@ACTION+AL+Y"})
    check("bridge_actions_exact", {row["action_root"] for row in bridges} == {"OK", "CH"})
    check("bridge_recipes_exact", {row["action_recipe"] for row in bridges} == {"OK+AL+Y", "CH+AL+Y"})
    check("bridge_register_profiles_exact", {row["action_root"]: set(row["registers"].split("|")) for row in bridges} == {"OK": {"BIOLOGICAL", "CELESTIAL"}, "CH": {"BIOLOGICAL", "PHARMA"}})
    check("bridge_flags_exact", all(row["same_action_and_formal_frame_across_registers"] == "YES" and row["owner_words_vary_by_register"] == "YES" for row in bridges))

    check("card_ids_unique", len({row["card_id"] for row in cards}) == 4)
    check("card_order_exact", tuple(row["frozen_frame"] for row in cards) == FRAMES)
    check("card_selected_registers_exact", all((card_map[frame]["t_register"], card_map[frame]["r_register"]) == EXPECTED_SELECTED_REGISTERS[frame] for frame in FRAMES))
    card_fields = ("formal_slot_count", "nonaction_slot_count", "owner_variant_nonaction_slot_count", "register_stable_nonaction_slot_count", "family_event_count", "action_cell_count", "alternate_non_tr_action_cell_count", "action_register_cell_count", "observed_clause_form_count", "register_count", "page_count")
    check("card_counts_exact", all(tuple(int(card_map[frame][field]) for field in card_fields) == EXPECTED_CARD_COUNTS[frame] for frame in FRAMES))
    check("card_action_roots_exact", all(tuple(card_map[frame]["action_roots"].split("|")) == EXPECTED_ACTION_ROOTS[frame] for frame in FRAMES))
    check("card_source_phrases_exact", all(card_map[row["frozen_frame"]]["t_selected_observed_phrase_de"] == row["t_selected_observed_phrase_de"] and card_map[row["frozen_frame"]]["r_selected_observed_phrase_de"] == row["r_selected_observed_phrase_de"] for row in source_variants))
    check("card_all_slots_observed", all(row["all_slots_observed"] == "YES" for row in cards))
    check("card_no_invented_phrase", all(row["new_phrase_invented"] == "NO" for row in cards))

    check("readable_core_counts", "**4/4**" in readable and "**12**" in readable and "**0**" in readable and "**35/35**" in readable and "**23**" in readable and "**17**" in readable and "**19**" in readable and "**9**" in readable)
    check("readable_all_frames", all(f"`{frame}`" in readable for frame in FRAMES))
    check("readable_all_selected_phrases", all(row["t_selected_observed_phrase_de"] in readable and row["r_selected_observed_phrase_de"] in readable for row in cards))
    check("readable_all_roots", all(f"`{root}`" in readable for root in ROOTS))
    check("readable_bridge_recipes", "`OK+AL+Y`" in readable and "`CH+AL+Y`" in readable)
    check("readable_model_statement", "Mischung aus kurzen produktiven Fachkürzeln und gelernten owner-lokalen Ganzwörtern" in readable)
    check("readable_next_route", "Owner-abhängige Satzschablone" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_core_counts_exact", (result.get("owner_variant_card_count"), result.get("owner_variant_slot_occurrence_count"), result.get("nonaction_slot_occurrence_count"), result.get("owner_local_nonaction_slot_count"), result.get("register_stable_nonaction_slot_count"), result.get("undefined_slot_count")) == (4, 12, 8, 7, 1, 0))
    check("result_matrix_counts_exact", (result.get("relevant_root_count"), result.get("observed_register_slot_cell_count")) == (7, 35))
    check("result_family_counts_exact", (result.get("exact_family_carrier_count"), result.get("exact_action_cell_count"), result.get("action_register_cell_count"), result.get("observed_family_clause_form_count"), result.get("alternate_non_tr_action_cell_count"), result.get("same_action_cross_register_bridge_count")) == (23, 17, 19, 19, 9, 2))
    check("result_family_scope_exact", (result.get("family_register_count"), result.get("family_page_count"), result.get("family_action_root_count")) == (5, 11, 7))
    check("result_flags_true", result.get("all_slots_observed") is True and result.get("all_family_carriers_roundtrip_exact") is True)
    check("result_no_invention", result.get("invented_phrase_count") == 0 and result.get("new_portable_value_count") == 0)
    unchanged = ("meaning_change_count", "wording_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "all seven relevant values have old support in all five registers" in result.get("claim_ceiling", "") and "no invented phrase" in result.get("claim_ceiling", ""))

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
