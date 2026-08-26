#!/usr/bin/env python3
"""Validate GDT483's exact running-carrier closure for sodar."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
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
BASE = ROOT / "experiments/yolo/gdt483_sodar_exact_running_carrier_closure"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G473 = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition/artifacts"
G482 = ROOT / "experiments/yolo/gdt482_residual_event_component_tiles/artifacts"
RUNNING_IN = G413 / "gdt413_4576_event_semantic_edition.tsv"
DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
IMPERATIVES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
LOCAL_IN = G473 / "gdt473_183_unified_address_working_edition.tsv"
TILES_IN = G482 / "gdt482_45_residual_event_internal_tiles.tsv"
DA_CONTEXTS = OUT / "gdt483_35_da_event_contexts.tsv"
DA_R_CONTEXTS = OUT / "gdt483_10_da_r_adjacent_contexts.tsv"
CARRIERS = OUT / "gdt483_3_sodar_exact_carriers.tsv"
WINDOWS = OUT / "gdt483_2_sodar_running_context_windows.tsv"
SUPPORT = OUT / "gdt483_sodar_component_support_summary.tsv"
CLOSURE = OUT / "gdt483_45_residual_closure.tsv"
READABLE = OUT / "GDT483_SODAR_EXACT_CARRIER_CLOSURE.md"
RESULT = OUT / "gdt483_result.json"
VALIDATION = OUT / "gdt483_validation.json"
STATUS = "SODAR_HAS_TWO_EXACT_RUNNING_CARRIERS__FINAL_FUNCTIONAL_RESIDUAL_CLOSED"
PAGES = (
    "f1r", "f10r", "f11r", "f13r", "f17r", "f18r", "f24v", "f55v",
    "f56r", "f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r", "f75r",
    "f76r", "f77r", "f81r", "f81v", "f82r", "f83r", "f88r", "f88v",
    "f89r", "f95v",
)
LOCAL_PAGES = ("f17r", "f71v", "f72r", "f77r", "f88v", "f89r")
RUNNING_PAGES = set(PAGES) - {"f69v", "f70v"}
EVENT_COLUMNS = (
    "global_running_ordinal", "global_running_event_id", "physical_page", "register",
    "locus", "source_statement_id", "owner_de", "surface", "component_recipe",
    "working_core_reading_de", "surface_status", "admission_color",
)
IMPERATIVE_COLUMNS = (
    "global_running_event_id", "global_statement_id", "card_ordinal_in_statement",
    "physical_page", "register", "owner_de", "surface", "component_recipe",
    "inherited_argument_root", "imperative_clause_de", "portable_back_projection_de",
    "roundtrip_exact",
)
LOCAL_COLUMNS = (
    "source_event_id", "physical_page", "register", "locus", "owner_de", "surface",
    "content_class", "edition_route", "edition_semantic_mode", "coverage_class",
    "working_recipe", "working_reading_de", "assignment_mode", "transfer_scope",
    "template_familiarity_state", "gdt459_decision_evidence",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_query(path: Path, pages: tuple[str, ...], columns: tuple[str, ...]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)), "--selector", "physical_page"]
    for page in pages:
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns)))
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr)
    match = re.search(r"GUARD_STATS (\{.*\})", completed.stderr)
    if not match:
        raise RuntimeError("Missing guard stats")
    return list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t")), json.loads(match.group(1))


def atoms(recipe: str) -> list[str]:
    return recipe.split("+")


def adjacent(recipe: str, unit: str) -> bool:
    sequence = atoms(recipe)
    fragment = unit.split("+")
    return any(sequence[index:index + len(fragment)] == fragment for index in range(len(sequence) - len(fragment) + 1))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [DA_CONTEXTS, DA_R_CONTEXTS, CARRIERS, WINDOWS, SUPPORT, CLOSURE, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT483 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    running, running_stats = guarded_query(RUNNING_IN, PAGES, EVENT_COLUMNS)
    imperatives, imperative_stats = guarded_query(IMPERATIVES_IN, PAGES, IMPERATIVE_COLUMNS)
    local, local_stats = guarded_query(LOCAL_IN, LOCAL_PAGES, LOCAL_COLUMNS)
    dictionary = read_tsv(DICTIONARY_IN)
    tiles = read_tsv(TILES_IN)
    da_rows = read_tsv(DA_CONTEXTS)
    da_r_rows = read_tsv(DA_R_CONTEXTS)
    carriers = read_tsv(CARRIERS)
    windows = read_tsv(WINDOWS)
    support = read_tsv(SUPPORT)
    closure = read_tsv(CLOSURE)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("running_source_count_4576", len(running) == 4576, len(running))
    check("imperative_source_count_4576", len(imperatives) == 4576, len(imperatives))
    check("local_source_count_183", len(local) == 183, len(local))
    check("dictionary_count_46", len(dictionary) == 46, len(dictionary))
    check("residual_source_count_45", len(tiles) == 45, len(tiles))
    check("all_guarded_sources_fully_selected", (running_stats["selected"], imperative_stats["selected"], local_stats["selected"]) == (4576, 4576, 183))
    check("no_forbidden_rows_materialized", sum(stats["skipped_forbidden"] for stats in (running_stats, imperative_stats, local_stats)) == 0)
    check("running_pages_exact", {row["physical_page"] for row in running} == RUNNING_PAGES)
    check("local_pages_exact", {row["physical_page"] for row in local} == set(LOCAL_PAGES))
    check("sealed_pages_absent", all(not row["physical_page"].startswith("f84") for row in running + imperatives + local + da_rows + carriers + windows + closure))

    check("da_context_count_35", len(da_rows) == 35, len(da_rows))
    check("da_r_context_count_10", len(da_r_rows) == 10, len(da_r_rows))
    check("carrier_count_3", len(carriers) == 3, len(carriers))
    check("context_window_count_2", len(windows) == 2, len(windows))
    check("support_summary_count_10", len(support) == 10, len(support))
    check("closure_count_45", len(closure) == 45, len(closure))
    check("da_context_ids_unique", len({row["context_id"] for row in da_rows}) == 35)
    check("carrier_ids_unique", len({row["carrier_id"] for row in carriers}) == 3)
    check("window_ids_unique", len({row["window_id"] for row in windows}) == 2)
    check("closure_ids_unique", len({row["closure_id"] for row in closure}) == 45)
    check("closure_event_ids_unique", len({row["source_event_id"] for row in closure}) == 45)

    dictionary_map = {row["atom"]: row for row in dictionary}
    expected_values = {"S": "WÄHLEN", "O": "AUSFÜHRUNG", "DA": "ZWEITE STUFE", "R": "MARKIEREN"}
    check("dictionary_values_exact", all(dictionary_map[atom]["working_value_de"] == value for atom, value in expected_values.items()), {atom: dictionary_map[atom]["working_value_de"] for atom in expected_values})
    check("dictionary_decisions_retained", all(dictionary_map[atom]["decision"].startswith("KEEP") for atom in expected_values))

    running_map = {row["global_running_event_id"]: row for row in running}
    imperative_map = {row["global_running_event_id"]: row for row in imperatives}
    local_map = {row["source_event_id"]: row for row in local}
    tile_map = {row["source_event_id"]: row for row in tiles}
    da_source = [row for row in running if "DA" in atoms(row["component_recipe"])]
    da_r_source = [row for row in da_source if adjacent(row["component_recipe"], "DA+R")]
    check("da_source_selection_exact", {row["global_running_event_id"] for row in da_rows} == {row["global_running_event_id"] for row in da_source})
    check("da_r_source_selection_exact", {row["global_running_event_id"] for row in da_r_rows} == {row["global_running_event_id"] for row in da_r_source})
    check("da_rows_all_contain_da", all("DA" in atoms(row["component_recipe"]) for row in da_rows))
    check("da_r_rows_all_adjacent", all(adjacent(row["component_recipe"], "DA+R") for row in da_r_rows))
    check("da_context_source_fields_exact", all(row["surface"] == running_map[row["global_running_event_id"]]["surface"] and row["component_recipe"] == running_map[row["global_running_event_id"]]["component_recipe"] and row["working_core_reading_de"] == running_map[row["global_running_event_id"]]["working_core_reading_de"] for row in da_rows))
    check("da_r_recipe_profile_exact", Counter(row["component_recipe"] for row in da_r_rows) == Counter({"DA+R+Y": 5, "DA+R+A_ADDR+AM_ADDR": 2, "S+O+DA+R": 2, "L+DA+R": 1}), Counter(row["component_recipe"] for row in da_r_rows))
    check("da_r_page_count_7", len({row["physical_page"] for row in da_r_rows}) == 7)
    check("da_r_register_count_3", len({row["register"] for row in da_r_rows}) == 3)

    exact_running = [row for row in running if row["surface"] == "sodar"]
    check("running_sodar_count_2", len(exact_running) == 2, exact_running)
    check("running_sodar_ids_exact", {row["global_running_event_id"] for row in exact_running} == {"G407-E0930", "G407-E2712"})
    check("running_sodar_pages_exact", {row["physical_page"] for row in exact_running} == {"f67r2", "f77r"})
    check("running_sodar_registers_exact", {row["register"] for row in exact_running} == {"CELESTIAL", "BIOLOGICAL"})
    check("running_sodar_recipe_exact", all(row["component_recipe"] == "S+O+DA+R" for row in exact_running))
    check("running_sodar_reading_exact", all(row["working_core_reading_de"] == "WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN" for row in exact_running))
    check("running_sodar_no_surface_conflict", len({(row["component_recipe"], row["working_core_reading_de"]) for row in exact_running}) == 1)
    check("running_sodar_imperatives_resolve", all(row["global_running_event_id"] in imperative_map for row in exact_running))
    check("running_sodar_roundtrips_exact", all(imperative_map[row["global_running_event_id"]]["roundtrip_exact"] == "YES" for row in exact_running))
    check("running_sodar_backprojections_exact", all(imperative_map[row["global_running_event_id"]]["portable_back_projection_de"] == "WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN" for row in exact_running))
    check("running_sodar_inherited_arguments_exact", {imperative_map[row["global_running_event_id"]]["inherited_argument_root"] for row in exact_running} == {"AIN", "Y"})

    check("local_target_resolves", "P1008-E1297" in local_map and "P1008-E1297" in tile_map)
    local_target = local_map["P1008-E1297"]
    check("local_target_identity_exact", (local_target["physical_page"], local_target["register"], local_target["surface"], local_target["working_recipe"]) == ("f89r", "PHARMA", "sodar", "S+O+DA+R"), local_target)
    check("local_target_literal_exact", local_target["working_reading_de"] == "WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN")
    check("local_target_formula_side", (local_target["edition_route"], local_target["edition_semantic_mode"], local_target["coverage_class"]) == ("GDT459_FORMULA_SIDE", "PORTABLE_EXACT_RUNNING_FORMULA", "FULL_FUNCTION_FORMULA"))
    check("local_target_prior_running_evidence", local_target["gdt459_decision_evidence"] == "EXACT_SURFACE_HAS_ONE_RUNNING_RECIPE")

    carrier_map = {row["source_id"]: row for row in carriers}
    check("carrier_source_ids_exact", set(carrier_map) == {"P1008-E1297", "G407-E0930", "G407-E2712"})
    check("carrier_pages_exact", {row["physical_page"] for row in carriers} == {"f89r", "f67r2", "f77r"})
    check("carrier_registers_exact", {row["register"] for row in carriers} == {"PHARMA", "CELESTIAL", "BIOLOGICAL"})
    check("carrier_surface_recipe_exact", all((row["surface"], row["component_recipe"]) == ("sodar", "S+O+DA+R") for row in carriers))
    check("carrier_literal_exact", all(row["literal_component_reading_de"] == "WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN" for row in carriers))
    check("carrier_backprojection_exact", all(row["portable_back_projection_de"] == "WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN" for row in carriers))
    check("carrier_roundtrip_exact", all(row["roundtrip_exact"] == "YES" for row in carriers))
    check("carrier_type_profile_exact", Counter(row["carrier_type"] for row in carriers) == Counter({"RUNNING_EXACT_SURFACE_RECIPE_DONOR": 2, "LOCAL_ADDRESS_TARGET": 1}))

    check("windows_target_ids_exact", {row["target_event_id"] for row in windows} == {"G407-E0930", "G407-E2712"})
    check("windows_same_statement", all(row["same_statement_window"] == "YES" for row in windows))
    check("window_neighbors_exact", {(row["previous_event_id"], row["target_event_id"], row["following_event_id"]) for row in windows} == {("G407-E0929", "G407-E0930", "G407-E0931"), ("G407-E2711", "G407-E2712", "G407-E2713")})
    check("window_target_fields_exact", all(row["target_surface"] == "sodar" and row["target_recipe"] == "S+O+DA+R" for row in windows))
    check("window_inherited_arguments_exact", {row["inherited_argument_root"] for row in windows} == {"AIN", "Y"})

    support_map = {row["support_unit"]: row for row in support}
    check("support_units_exact", set(support_map) == {"S", "O", "DA", "R", "S+O", "O+DA", "DA+R", "S+O+DA", "O+DA+R", "S+O+DA+R"})
    expected_counts = {"S": 300, "O": 683, "DA": 35, "R": 114, "S+O": 13, "O+DA": 6, "DA+R": 10, "S+O+DA": 2, "O+DA+R": 2, "S+O+DA+R": 2}
    check("support_event_counts_exact", all(int(support_map[unit]["running_event_count"]) == count for unit, count in expected_counts.items()), {unit: support_map[unit]["running_event_count"] for unit in expected_counts})
    check("support_kind_exact", all(support_map[unit]["unit_kind"] == ("ATOM" if "+" not in unit else "CONTIGUOUS_FRAGMENT") for unit in support_map))
    check("atom_support_profiles_exact", (int(support_map["DA"]["distinct_recipe_count"]), int(support_map["DA"]["distinct_surface_count"]), int(support_map["DA"]["page_count"]), int(support_map["DA"]["register_count"]), int(support_map["R"]["distinct_recipe_count"]), int(support_map["R"]["page_count"])) == (20, 20, 14, 5, 52, 22))
    check("da_r_support_profile_exact", (int(support_map["DA+R"]["distinct_recipe_count"]), int(support_map["DA+R"]["distinct_surface_count"]), int(support_map["DA+R"]["page_count"]), int(support_map["DA+R"]["register_count"])) == (4, 4, 7, 3))
    check("exact_recipe_support_profile", (int(support_map["S+O+DA+R"]["distinct_recipe_count"]), int(support_map["S+O+DA+R"]["distinct_surface_count"]), int(support_map["S+O+DA+R"]["page_count"]), int(support_map["S+O+DA+R"]["register_count"])) == (1, 1, 2, 2))

    closure_map = {row["source_event_id"]: row for row in closure}
    check("closure_source_key_set_exact", set(closure_map) == set(tile_map))
    classes = Counter(row["gdt483_closure_class"] for row in closure)
    check("closure_class_profile_exact", classes == Counter({"LOCAL_COMPONENT_RECURRENT": 42, "LEARNED_LEXICAL_SLOT_ONLY": 2, "EXACT_RUNNING_SURFACE_RECIPE_CARRIER": 1}), classes)
    check("sodar_closure_exact", closure_map["P1008-E1297"]["gdt483_closure_class"] == "EXACT_RUNNING_SURFACE_RECIPE_CARRIER" and closure_map["P1008-E1297"]["exact_running_donor_count"] == "2")
    check("sodar_closure_donors_exact", set(closure_map["P1008-E1297"]["exact_running_donor_ids"].split("|")) == {"G407-E0930", "G407-E2712"})
    check("learned_closure_ids_exact", {row["source_event_id"] for row in closure if row["gdt483_closure_class"] == "LEARNED_LEXICAL_SLOT_ONLY"} == {"P1003-E0460", "P1008-E1182"})
    check("all_functional_explanations_complete", all(row["functional_explanation_complete"] == "YES" for row in closure))
    check("all_source_meanings_preserved", all(row["source_meaning_preserved"] == "YES" for row in closure))
    check("all_defaults_nonempty", all(row["concrete_default_reading_de"] for row in closure))

    check("readable_contains_all_carriers", all(source_id in readable for source_id in carrier_map))
    check("readable_reports_exact_phrase", "Wähle den Eintrag und markiere ihn" in readable)
    check("readable_reports_da_r_family", all(recipe in readable for recipe in ("DA+R+Y", "DA+R+A_ADDR+AM_ADDR", "S+O+DA+R", "L+DA+R")))
    check("readable_reports_closed_tail", "ungeklärter funktionaler Rest | 0" in readable and "kein unbekannter Funktionsbaustein" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_guard_counts_exact", (result.get("guarded_running_event_count"), result.get("guarded_imperative_count"), result.get("guarded_local_event_count"), result.get("forbidden_row_materialization_count")) == (4576, 4576, 183, 0))
    check("result_target_exact", (result.get("target_event_id"), result.get("target_surface"), result.get("target_recipe"), result.get("target_literal_reading_de")) == ("P1008-E1297", "sodar", "S+O+DA+R", "WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN"))
    check("result_carrier_counts_exact", (result.get("running_exact_surface_recipe_carrier_count"), result.get("combined_exact_surface_recipe_carrier_count"), result.get("combined_carrier_page_count"), result.get("combined_carrier_register_count")) == (2, 3, 3, 3))
    check("result_carrier_sets_exact", set(result.get("combined_carrier_pages", [])) == {"f67r2", "f77r", "f89r"} and set(result.get("combined_carrier_registers", [])) == {"BIOLOGICAL", "CELESTIAL", "PHARMA"})
    check("result_zero_conflicts", (result.get("running_surface_recipe_conflict_count"), result.get("running_literal_reading_conflict_count")) == (0, 0))
    check("result_support_counts_exact", (result.get("s_event_count"), result.get("o_event_count"), result.get("da_event_count"), result.get("r_event_count"), result.get("s_o_event_count"), result.get("o_da_event_count"), result.get("da_r_event_count"), result.get("exact_recipe_running_event_count")) == (300, 683, 35, 114, 13, 6, 10, 2))
    check("result_closure_counts_exact", (result.get("residual_event_count"), result.get("local_component_recurrent_count"), result.get("exact_running_carrier_closure_count"), result.get("learned_lexical_slot_count"), result.get("functionally_recurrent_or_exact_carrier_count"), result.get("functional_explanation_complete_count"), result.get("unexplained_functional_residual_count")) == (45, 42, 1, 2, 43, 45, 0))
    unchanged = ("component_meaning_change_count", "active_model_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("result_one_fluent_refinement", result.get("preferred_fluent_paraphrase_refinement_count") == 1 and result.get("preferred_generic_reading_de") in readable)
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
