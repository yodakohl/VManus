#!/usr/bin/env python3
"""Validate GDT493's labelled owner-dependent T/R realization deck."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt493_owner_dependent_tr_realization_deck"
OUT = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G415 = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
G416_BASE = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler"
G416 = G416_BASE / "artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G492 = ROOT / "experiments/yolo/gdt492_owner_variant_slot_bridge_atlas/artifacts"
RUN = BASE / "src/run.py"
COMPONENTS_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
REGISTER_ATLAS_IN = G415 / "gdt415_95_register_expansion_atlas.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
RENDERER_IN = G416_BASE / "src/run.py"
FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
G492_RESULT_IN = G492 / "gdt492_result.json"
VALUE_CELLS = OUT / "gdt493_55_observed_register_value_cells.tsv"
DECK = OUT / "gdt493_110_owner_frame_realization_cells.tsv"
OBSERVED = OUT / "gdt493_37_observed_clause_cells.tsv"
COMPOSED = OUT / "gdt493_73_composed_working_cells.tsv"
CONTRASTS = OUT / "gdt493_55_tr_register_contrast_cards.tsv"
FRAME_COVERAGE = OUT / "gdt493_11_frame_coverage.tsv"
REGISTER_COVERAGE = OUT / "gdt493_5_register_coverage.tsv"
STATE_FRAMES = OUT / "gdt493_4_state_dependent_frames.tsv"
STATE_OVERRIDES = OUT / "gdt493_3_observed_inherited_argument_overrides.tsv"
READABLE = OUT / "GDT493_OWNER_DEPENDENT_TR_REALIZATION_DECK.md"
RESULT = OUT / "gdt493_result.json"
VALIDATION = OUT / "gdt493_validation.json"
STATUS = "ONE_HUNDRED_TEN_OWNER_REALIZATIONS__THIRTY_SEVEN_OBSERVED__SEVENTY_THREE_COMPOSED_WORKING"
ROOTS = ("T", "R", "AIIN", "AIN", "AL", "Y", "CH", "E", "CHD", "OL", "OR")
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
ACTIONS = ("T", "R")
FRAMES = (
    "@ACTION", "@ACTION+AIIN", "@ACTION+AIN", "@ACTION+AL",
    "@ACTION+AL+Y", "@ACTION+CH+E+Y", "@ACTION+CHD+Y",
    "@ACTION+OL", "@ACTION+OR+Y", "@ACTION+Y", "CH+@ACTION",
)
STATE_DEPENDENT = {"@ACTION", "@ACTION+AL", "@ACTION+OL", "CH+@ACTION"}
EXPECTED_FRAME_OBSERVED = dict(zip(FRAMES, (6, 5, 3, 4, 2, 2, 3, 5, 2, 3, 2)))
EXPECTED_FRAME_CARRIERS = dict(zip(FRAMES, (22, 13, 5, 5, 2, 2, 7, 11, 2, 5, 2)))
EXPECTED_FRAME_FORMS = dict(zip(FRAMES, (10, 5, 3, 4, 2, 2, 3, 8, 2, 3, 2)))
EXPECTED_REGISTER = {
    "SOURCE_SECTION_T": (3, 19, 3, 3),
    "HERBAL": (9, 13, 15, 11),
    "BIOLOGICAL": (17, 5, 46, 19),
    "CELESTIAL": (3, 19, 4, 4),
    "PHARMA": (5, 17, 8, 7),
}
EXPECTED_ROOT_EVENTS = {
    "T": (27, 103, 105, 38, 22),
    "R": (6, 14, 61, 14, 19),
    "AIIN": (27, 100, 162, 70, 73),
    "AIN": (15, 39, 160, 8, 18),
    "AL": (7, 50, 177, 71, 43),
    "Y": (70, 307, 804, 168, 196),
    "CH": (57, 215, 255, 92, 151),
    "E": (32, 75, 548, 121, 189),
    "CHD": (1, 29, 259, 7, 5),
    "OL": (26, 109, 365, 59, 118),
    "OR": (11, 95, 79, 30, 47),
}
EXPECTED_OVERRIDES = {
    ("R+AL", "PHARMA", "OR"),
    ("CH+T", "HERBAL", "AIIN"),
    ("CH+R", "BIOLOGICAL", "AIIN"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_renderer() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gdt416_validator_renderer", RENDERER_IN)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load GDT416 renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [VALUE_CELLS, DECK, OBSERVED, COMPOSED, CONTRASTS, FRAME_COVERAGE, REGISTER_COVERAGE, STATE_FRAMES, STATE_OVERRIDES, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT493 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    components = read_tsv(COMPONENTS_IN)
    register_atlas = read_tsv(REGISTER_ATLAS_IN)
    clauses = read_tsv(CLAUSES_IN)
    frame_source = read_tsv(FRAMES_IN)
    g492 = json.loads(G492_RESULT_IN.read_text(encoding="utf-8"))
    renderer = load_renderer()
    values = read_tsv(VALUE_CELLS)
    deck = read_tsv(DECK)
    observed = read_tsv(OBSERVED)
    composed = read_tsv(COMPOSED)
    contrasts = read_tsv(CONTRASTS)
    frame_coverage = read_tsv(FRAME_COVERAGE)
    register_coverage = read_tsv(REGISTER_COVERAGE)
    state_frames = read_tsv(STATE_FRAMES)
    overrides = read_tsv(STATE_OVERRIDES)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    clause_map = {row["global_running_event_id"]: row for row in clauses}
    value_map = {(row["root"], row["register"]): row for row in values}
    cell_map = {(row["frozen_frame"], row["action_root"], row["register"]): row for row in deck}
    frame_map = {row["frozen_frame"]: row for row in frame_coverage}
    register_map = {row["register"]: row for row in register_coverage}

    check("source_component_count_46", len(components) == 46, len(components))
    check("source_register_atlas_count_95", len(register_atlas) == 95, len(register_atlas))
    check("source_clause_count_4576", len(clauses) == 4576, len(clauses))
    check("source_frame_count_104", len(frame_source) == 104, len(frame_source))
    check("source_tr_frame_count_11", sum(row["contrast_pair"] == "T~R" for row in frame_source) == 11)
    check("source_tr_frame_order_exact", tuple(row["frozen_frame"] for row in frame_source if row["contrast_pair"] == "T~R") == FRAMES)
    check("source_g492_status_exact", g492.get("status") == "FOUR_OWNER_VARIANTS_DECOMPOSED__THIRTY_FIVE_SLOT_CELLS_OBSERVED__NINE_ALTERNATE_ACTION_CELLS")
    check("value_cell_count_55", len(values) == 55, len(values))
    check("deck_count_110", len(deck) == 110, len(deck))
    check("observed_count_37", len(observed) == 37, len(observed))
    check("composed_count_73", len(composed) == 73, len(composed))
    check("contrast_count_55", len(contrasts) == 55, len(contrasts))
    check("frame_coverage_count_11", len(frame_coverage) == 11, len(frame_coverage))
    check("register_coverage_count_5", len(register_coverage) == 5, len(register_coverage))
    check("state_frame_count_4", len(state_frames) == 4, len(state_frames))
    check("override_count_3", len(overrides) == 3, len(overrides))

    check("value_ids_unique", len({row["value_cell_id"] for row in values}) == 55)
    check("value_keys_unique", len(value_map) == 55)
    check("value_root_set_exact", {row["root"] for row in values} == set(ROOTS))
    check("value_register_set_exact", {row["register"] for row in values} == set(REGISTERS))
    check("value_full_cartesian", set(value_map) == {(root, register) for root in ROOTS for register in REGISTERS})
    check("value_all_observed", all(row["observed_old_value_cell"] == "YES" and int(row["event_count"]) > 0 for row in values))
    check("value_event_counts_exact", all(int(value_map[(root, register)]["event_count"]) == EXPECTED_ROOT_EVENTS[root][REGISTERS.index(register)] for root in ROOTS for register in REGISTERS))
    check("value_mentions_cover_events", all(int(row["mention_count"]) >= int(row["event_count"]) for row in values))
    check("value_pages_positive", all(int(row["page_count"]) > 0 for row in values))
    check("value_owner_positive", all(int(row["owner_count"]) > 0 for row in values))
    check("value_e_stable", {row["owner_local_expansion_de"] for row in values if row["root"] == "E"} == {"GRAD I"})
    check("value_e_source_exact", all(row["source_atlas"] == "GDT413_COMPONENT_PLUS_GDT416_CARRIERS" for row in values if row["root"] == "E"))
    check("value_core_source_exact", all(row["source_atlas"] == "GDT415_REGISTER_EXPANSION_ATLAS" for row in values if row["root"] != "E"))

    check("deck_ids_unique", len({row["realization_cell_id"] for row in deck}) == 110)
    check("deck_keys_unique", len(cell_map) == 110)
    check("deck_full_cartesian", set(cell_map) == {(frame, action, register) for frame in FRAMES for action in ACTIONS for register in REGISTERS})
    check("deck_frame_ids_exact", len({row["frame_id"] for row in deck}) == 11)
    check("deck_recipe_exact", all(row["action_recipe"] == row["frozen_frame"].replace("@ACTION", row["action_root"]) for row in deck))
    check("deck_status_set_exact", {row["evidence_status"] for row in deck} == {"OBSERVED_CLAUSE", "COMPOSED_WORKING"})
    check("deck_status_profile_exact", Counter(row["evidence_status"] for row in deck) == Counter({"OBSERVED_CLAUSE": 37, "COMPOSED_WORKING": 73}))
    check("deck_all_display_phrases", all(row["display_phrase_de"] for row in deck))
    check("deck_all_portable_traces", all(row["portable_component_trace_de"] and row["owner_local_slot_trace_de"] for row in deck))
    check("deck_all_value_cells_observed", all(row["all_recipe_value_cells_observed"] == "YES" for row in deck))
    check("deck_no_new_slot_value", all(row["new_slot_value_required"] == "NO" for row in deck))
    check("deck_state_profile_exact", all(row["state_requirement"] == ("ACTIVE_ARGUMENT_REQUIRED" if row["frozen_frame"] in STATE_DEPENDENT else "SELF_CONTAINED_ARGUMENT") for row in deck))
    check("deck_state_default_exact", all(row["composed_state_default"] == ("Y=POSTEN [wie zuvor]" if row["frozen_frame"] in STATE_DEPENDENT else "NONE") for row in deck))
    check("deck_observed_flags_exact", all((row["display_phrase_is_observed_clause"], row["display_phrase_is_composed_working"]) == (("YES", "NO") if row["evidence_status"] == "OBSERVED_CLAUSE" else ("NO", "YES")) for row in deck))
    check("deck_composed_labels_visible", all(row["composed_working_label_visible"] == ("YES" if row["evidence_status"] == "COMPOSED_WORKING" else "NOT_APPLICABLE") for row in deck))
    check("deck_observed_have_events", all(int(row["observed_event_count"]) > 0 and row["observed_event_ids"] != "NONE" for row in observed))
    check("deck_composed_have_no_events", all(row["observed_event_count"] == "0" and row["observed_event_ids"] == "NONE" and row["all_observed_clause_forms_de"] == "NONE" for row in composed))
    check("observed_rows_exact_subset", observed == [row for row in deck if row["evidence_status"] == "OBSERVED_CLAUSE"])
    check("composed_rows_exact_subset", composed == [row for row in deck if row["evidence_status"] == "COMPOSED_WORKING"])

    observed_provenance = True
    default_selection = True
    for row in observed:
        event_ids = row["observed_event_ids"].split("|")
        local = [clause_map[event_id] for event_id in event_ids]
        observed_provenance &= all(source["component_recipe"] == row["action_recipe"] and source["register"] == row["register"] for source in local)
        observed_provenance &= set(row["all_observed_clause_forms_de"].split(" || ")) == {source["imperative_clause_de"] for source in local}
        counter = Counter(source["imperative_clause_de"] for source in local)
        default, count = sorted(counter.items(), key=lambda item: (-item[1], len(item[0]), item[0]))[0]
        default_selection &= row["display_phrase_de"] == default and int(row["selected_observed_phrase_carrier_count"]) == count
    check("observed_provenance_exact", observed_provenance)
    check("observed_default_selection_exact", default_selection)
    check("observed_carrier_total_76", sum(int(row["observed_event_count"]) for row in observed) == 76)
    check("observed_form_total_44", sum(int(row["observed_clause_form_count"]) for row in observed) == 44)
    check("observed_renderer_phrase_count_34", sum(row["composed_phrase_observed_in_exact_cell"] == "YES" for row in observed) == 34)
    check("observed_selected_equals_renderer_count_33", sum(row["selected_phrase_equals_composed_phrase"] == "YES" for row in observed) == 33)

    renderer_recomputed = True
    for row in deck:
        recipe_parts = row["action_recipe"].split("+")
        explicit_actions = [part for part in recipe_parts if part in renderer.ACTION_ROOTS]
        explicit_arguments = [part for part in recipe_parts if part in renderer.ARGUMENT_ROOTS]
        inherited_argument = "" if explicit_arguments else "Y"
        renderer_recomputed &= row["composed_working_phrase_de"] == renderer.render_clause(row["register"], recipe_parts, explicit_actions, "", inherited_argument)
        if row["evidence_status"] == "COMPOSED_WORKING":
            renderer_recomputed &= row["display_phrase_de"] == row["composed_working_phrase_de"]
    check("canonical_renderer_recomputed", renderer_recomputed)

    check("contrast_ids_unique", len({row["contrast_id"] for row in contrasts}) == 55)
    check("contrast_keys_unique", len({(row["frozen_frame"], row["register"]) for row in contrasts}) == 55)
    check("contrast_full_cartesian", {(row["frozen_frame"], row["register"]) for row in contrasts} == {(frame, register) for frame in FRAMES for register in REGISTERS})
    check("contrast_cells_resolve", all(row["t_display_phrase_de"] == cell_map[(row["frozen_frame"], "T", row["register"])]["display_phrase_de"] and row["r_display_phrase_de"] == cell_map[(row["frozen_frame"], "R", row["register"])]["display_phrase_de"] for row in contrasts))
    check("contrast_statuses_resolve", all(row["t_evidence_status"] == cell_map[(row["frozen_frame"], "T", row["register"])]["evidence_status"] and row["r_evidence_status"] == cell_map[(row["frozen_frame"], "R", row["register"])]["evidence_status"] for row in contrasts))
    check("contrast_pair_profile_exact", Counter(row["pair_evidence_status"] for row in contrasts) == Counter({"BOTH_OBSERVED": 8, "MIXED_OBSERVED_COMPOSED": 21, "BOTH_COMPOSED_WORKING": 26}))
    check("contrast_all_formal_remainders", all(row["formal_remainder_unchanged"] == "YES" for row in contrasts))
    check("contrast_all_distinct", all(row["display_phrases_distinct"] == "YES" for row in contrasts))
    check("contrast_all_values_observed", all(row["all_value_cells_observed"] == "YES" for row in contrasts))

    check("frame_ids_unique", len({row["frame_id"] for row in frame_coverage}) == 11)
    check("frame_order_exact", tuple(row["frozen_frame"] for row in frame_coverage) == FRAMES)
    check("frame_cells_10_each", all(row["realization_cell_count"] == "10" for row in frame_coverage))
    check("frame_observed_profile_exact", all(int(frame_map[frame]["observed_cell_count"]) == EXPECTED_FRAME_OBSERVED[frame] for frame in FRAMES))
    check("frame_composed_profile_exact", all(int(frame_map[frame]["composed_cell_count"]) == 10 - EXPECTED_FRAME_OBSERVED[frame] for frame in FRAMES))
    check("frame_carrier_profile_exact", all(int(frame_map[frame]["observed_carrier_count"]) == EXPECTED_FRAME_CARRIERS[frame] for frame in FRAMES))
    check("frame_form_profile_exact", all(int(frame_map[frame]["observed_clause_form_count"]) == EXPECTED_FRAME_FORMS[frame] for frame in FRAMES))
    check("frame_state_profile_exact", all(frame_map[frame]["state_requirement"] == ("ACTIVE_ARGUMENT_REQUIRED" if frame in STATE_DEPENDENT else "SELF_CONTAINED_ARGUMENT") for frame in FRAMES))
    check("frame_coverage_flags", all(row["all_registers_covered"] == "YES" and row["both_actions_covered"] == "YES" for row in frame_coverage))

    check("register_ids_unique", len({row["register_id"] for row in register_coverage}) == 5)
    check("register_order_exact", tuple(row["register"] for row in register_coverage) == REGISTERS)
    check("register_cells_22_each", all(row["realization_cell_count"] == "22" for row in register_coverage))
    register_fields = ("observed_cell_count", "composed_cell_count", "observed_carrier_count", "observed_clause_form_count")
    check("register_profiles_exact", all(tuple(int(register_map[register][field]) for field in register_fields) == EXPECTED_REGISTER[register] for register in REGISTERS))
    check("register_frame_action_coverage", all(row["frame_count"] == "11" and row["action_count"] == "2" for row in register_coverage))
    check("register_display_flags", all(row["all_cells_have_display_phrase"] == "YES" for row in register_coverage))

    check("state_frame_ids_unique", len({row["state_frame_id"] for row in state_frames}) == 4)
    check("state_frame_set_exact", {row["frozen_frame"] for row in state_frames} == STATE_DEPENDENT)
    check("state_frame_cells_10_each", all(row["realization_cell_count"] == "10" for row in state_frames))
    check("state_frame_default_exact", all(row["composed_state_default"] == "Y=POSTEN [wie zuvor]" for row in state_frames))
    check("state_frame_flags_exact", all(row["state_can_override_y_default"] == "YES" and row["composed_phrase_claimed_observed"] == "NO" for row in state_frames))

    check("override_ids_unique", len({row["override_id"] for row in overrides}) == 3)
    check("override_keys_exact", {(row["action_recipe"], row["register"], row["observed_inherited_argument_roots"]) for row in overrides} == EXPECTED_OVERRIDES)
    check("override_cells_resolve", all(row["realization_cell_id"] in {cell["realization_cell_id"] for cell in observed} for row in overrides))
    check("override_phrases_differ", all(row["composed_working_phrase_de"] != row["selected_observed_phrase_de"] for row in overrides))
    check("override_flags_exact", all(row["observation_overrides_composed_default"] == "YES" and row["new_meaning_required"] == "NO" for row in overrides))

    check("readable_core_counts", "**110/110**" in readable and "**37**" in readable and "**76**" in readable and "**44**" in readable and "**73**" in readable and "**0**" in readable and "**55/55**" in readable)
    check("readable_all_frames", all(f"`{frame}`" in readable for frame in FRAMES))
    check("readable_status_labels", "`OBSERVED_CLAUSE`" in readable and "`COMPOSED_WORKING`" in readable)
    check("readable_all_display_phrases", all(row["display_phrase_de"] in readable for row in deck))
    check("readable_contrast_profile", "Acht Paare" in readable and "21" in readable and "26" in readable)
    check("readable_override_keys", all(f"`{recipe}`" in readable and register in readable for recipe, register, _ in EXPECTED_OVERRIDES))
    check("readable_model_statement", "Mischarchitektur aus kurzen Fachkürzeln" in readable)
    check("readable_next_route", "73 zusammengesetzten Zellen" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_dimensions_exact", (result.get("frame_count"), result.get("action_count"), result.get("register_count"), result.get("realization_cell_count")) == (11, 2, 5, 110))
    check("result_evidence_counts_exact", (result.get("observed_clause_cell_count"), result.get("composed_working_cell_count"), result.get("observed_carrier_count"), result.get("observed_clause_form_count")) == (37, 73, 76, 44))
    check("result_value_counts_exact", (result.get("observed_register_value_cell_count"), result.get("relevant_value_count"), result.get("new_slot_value_count")) == (55, 11, 0))
    check("result_contrast_counts_exact", (result.get("tr_register_contrast_count"), result.get("both_observed_contrast_count"), result.get("mixed_contrast_count"), result.get("both_composed_contrast_count"), result.get("distinct_tr_display_count")) == (55, 8, 21, 26, 55))
    check("result_state_counts_exact", (result.get("state_dependent_frame_count"), result.get("canonical_renderer_phrase_observed_cell_count"), result.get("selected_default_equals_renderer_count"), result.get("observed_inherited_argument_override_count")) == (4, 34, 33, 3))
    check("result_provenance_guards_zero", result.get("unlabelled_composed_count") == 0 and result.get("claimed_observed_without_witness_count") == 0)
    unchanged = ("meaning_change_count", "source_wording_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "37 cells are exact observed clauses" in result.get("claim_ceiling", "") and "73 are visibly labelled compositions" in result.get("claim_ceiling", ""))

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
