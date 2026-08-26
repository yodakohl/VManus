#!/usr/bin/env python3
"""Validate GDT491's observed MARKIEREN atlas and T/R contrast cards."""

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
BASE = ROOT / "experiments/yolo/gdt491_markierungen_observed_phrase_contrast_atlas"
OUT = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G490 = ROOT / "experiments/yolo/gdt490_einstellen_observed_phrase_atlas/artifacts"
RUN = BASE / "src/run.py"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
ACTION_FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
T_FORMS_IN = G490 / "gdt490_22_observed_t_clause_forms.tsv"
T_DEFAULTS_IN = G490 / "gdt490_11_observed_default_phrases.tsv"
CARRIERS = OUT / "gdt491_46_readable_r_carriers.tsv"
FORMS = OUT / "gdt491_22_observed_r_clause_forms.tsv"
CELLS = OUT / "gdt491_11_r_frame_phrase_cells.tsv"
PHRASEBOOK = OUT / "gdt491_11_observed_r_default_phrases.tsv"
CONTRASTS = OUT / "gdt491_11_observed_tr_contrast_cards.tsv"
EXACT_RESTS = OUT / "gdt491_7_exact_german_remainder_pairs.tsv"
OWNER_VARIANTS = OUT / "gdt491_4_owner_variant_contrast_cards.tsv"
REGISTERS = OUT / "gdt491_5_register_phrase_support.tsv"
READABLE = OUT / "GDT491_MARKIEREN_OBSERVED_PHRASE_CONTRAST_ATLAS.md"
RESULT = OUT / "gdt491_result.json"
VALIDATION = OUT / "gdt491_validation.json"
STATUS = "ALL_ELEVEN_R_FRAMES_HAVE_OBSERVED_PHRASES__SEVEN_EXACT_GERMAN_REMAINDERS__FOUR_OWNER_VARIANTS"
EXPECTED_FRAMES = [
    "@ACTION", "@ACTION+AIIN", "@ACTION+AIN", "@ACTION+AL",
    "@ACTION+AL+Y", "@ACTION+CH+E+Y", "@ACTION+CHD+Y",
    "@ACTION+OL", "@ACTION+OR+Y", "@ACTION+Y", "CH+@ACTION",
]
EXPECTED_CARRIERS = dict(zip(EXPECTED_FRAMES, (21, 8, 3, 2, 1, 1, 2, 4, 1, 2, 1)))
EXPECTED_FORMS = dict(zip(EXPECTED_FRAMES, (9, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1)))
EXPECTED_DEFAULTS = {
    "@ACTION": "Markiere den Stationsposten [wie zuvor].",
    "@ACTION+AIIN": "Markiere den Stationswert.",
    "@ACTION+AIN": "Markiere den Stationsanteil.",
    "@ACTION+AL": "Markiere die Ansatzeinheit [wie zuvor]; zum Zielgefäß.",
    "@ACTION+AL+Y": "Markiere den Stationsposten; zur Zielstation.",
    "@ACTION+CH+E+Y": "Markiere den Stationsposten und entnimm den Stationsposten; auf Grad I.",
    "@ACTION+CHD+Y": "Markiere den Stationsposten und bearbeite den Stationsposten.",
    "@ACTION+OL": "Weiter markiere den Stationsposten [wie zuvor].",
    "@ACTION+OR+Y": "Markiere die Stationseinheit und den Stationsposten.",
    "@ACTION+Y": "Markiere den Stationsposten.",
    "CH+@ACTION": "Entnimm den Stationswert [wie zuvor] und markiere den Stationswert [wie zuvor].",
}
EXACT_FRAMES = {
    "@ACTION", "@ACTION+AIIN", "@ACTION+AIN", "@ACTION+AL",
    "@ACTION+CHD+Y", "@ACTION+OL", "@ACTION+Y",
}
OWNER_VARIANT_FRAMES = {"@ACTION+AL+Y", "@ACTION+CH+E+Y", "@ACTION+OR+Y", "CH+@ACTION"}
EXPECTED_SELECTED = {
    "@ACTION": ("Stelle den Pflanzenposten [wie zuvor] ein.", "Markiere den Pflanzenposten [wie zuvor]."),
    "@ACTION+AIIN": ("Stelle den Stationswert ein.", "Markiere den Stationswert."),
    "@ACTION+AIN": ("Stelle den Stationsanteil ein.", "Markiere den Stationsanteil."),
    "@ACTION+AL": ("Stelle den Stationsposten [wie zuvor] ein; zur Zielstation.", "Markiere den Stationsposten [wie zuvor]; zur Zielstation."),
    "@ACTION+AL+Y": ("Stelle den Positionsposten ein; zur Zielposition.", "Markiere den Stationsposten; zur Zielstation."),
    "@ACTION+CH+E+Y": ("Lege den laufenden Eintrag fest und entnimm den laufenden Eintrag; auf Grad I.", "Markiere den Stationsposten und entnimm den Stationsposten; auf Grad I."),
    "@ACTION+CHD+Y": ("Stelle den Stationsposten ein und bearbeite den Stationsposten.", "Markiere den Stationsposten und bearbeite den Stationsposten."),
    "@ACTION+OL": ("Weiter stelle den Stationsposten [wie zuvor] ein.", "Weiter markiere den Stationsposten [wie zuvor]."),
    "@ACTION+OR+Y": ("Stelle die Arbeitseinheit und den Pflanzenposten ein.", "Markiere die Stationseinheit und den Stationsposten."),
    "@ACTION+Y": ("Stelle den Stationsposten ein.", "Markiere den Stationsposten."),
    "CH+@ACTION": ("Nimm den Arbeitswert [wie zuvor] und stelle den Arbeitswert [wie zuvor] ein.", "Entnimm den Stationswert [wie zuvor] und markiere den Stationswert [wie zuvor]."),
}
EXPECTED_REGISTERS = {
    "SOURCE_SECTION_T": (1, 1, 1, 1),
    "HERBAL": (4, 2, 3, 3),
    "CELESTIAL": (2, 1, 2, 2),
    "BIOLOGICAL": (35, 11, 13, 7),
    "PHARMA": (4, 2, 3, 3),
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

    generated = [CARRIERS, FORMS, CELLS, PHRASEBOOK, CONTRASTS, EXACT_RESTS, OWNER_VARIANTS, REGISTERS, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT491 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    clauses = read_tsv(CLAUSES_IN)
    action_frames = read_tsv(ACTION_FRAMES_IN)
    t_forms = read_tsv(T_FORMS_IN)
    t_defaults = read_tsv(T_DEFAULTS_IN)
    carriers = read_tsv(CARRIERS)
    forms = read_tsv(FORMS)
    cells = read_tsv(CELLS)
    phrasebook = read_tsv(PHRASEBOOK)
    contrasts = read_tsv(CONTRASTS)
    exact_rests = read_tsv(EXACT_RESTS)
    owner_variants = read_tsv(OWNER_VARIANTS)
    registers = read_tsv(REGISTERS)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    clause_map = {row["global_running_event_id"]: row for row in clauses}
    cell_map = {row["frozen_frame"]: row for row in cells}
    phrasebook_map = {row["frozen_frame"]: row for row in phrasebook}
    contrast_map = {row["frozen_frame"]: row for row in contrasts}
    t_form_keys = {(row["frozen_frame"], row["observed_clause_de"]) for row in t_forms}
    r_form_keys = {(row["frozen_frame"], row["observed_clause_de"]) for row in forms}

    check("source_clause_count_4576", len(clauses) == 4576, len(clauses))
    check("source_action_frame_count_104", len(action_frames) == 104, len(action_frames))
    check("source_t_form_count_22", len(t_forms) == 22, len(t_forms))
    check("source_t_default_count_11", len(t_defaults) == 11, len(t_defaults))
    check("source_tr_frame_count_11", sum(row["contrast_pair"] == "T~R" for row in action_frames) == 11)
    check("carrier_count_46", len(carriers) == 46, len(carriers))
    check("form_count_22", len(forms) == 22, len(forms))
    check("cell_count_11", len(cells) == 11, len(cells))
    check("phrasebook_count_11", len(phrasebook) == 11, len(phrasebook))
    check("contrast_count_11", len(contrasts) == 11, len(contrasts))
    check("exact_remainder_count_7", len(exact_rests) == 7, len(exact_rests))
    check("owner_variant_count_4", len(owner_variants) == 4, len(owner_variants))
    check("register_count_5", len(registers) == 5, len(registers))

    check("cell_frame_order_exact", [row["frozen_frame"] for row in cells] == EXPECTED_FRAMES)
    check("phrasebook_frame_order_exact", [row["frozen_frame"] for row in phrasebook] == EXPECTED_FRAMES)
    check("contrast_frame_order_exact", [row["frozen_frame"] for row in contrasts] == EXPECTED_FRAMES)
    check("cell_ids_unique", len({row["cell_id"] for row in cells}) == 11)
    check("frame_ids_unique", len({row["frame_id"] for row in cells}) == 11)
    check("phrasebook_ids_unique", len({row["phrasebook_id"] for row in phrasebook}) == 11)
    check("contrast_ids_unique", len({row["contrast_id"] for row in contrasts}) == 11)
    check("cell_carrier_counts_exact", all(int(cell_map[frame]["carrier_count"]) == count for frame, count in EXPECTED_CARRIERS.items()))
    check("cell_form_counts_exact", all(int(cell_map[frame]["observed_clause_form_count"]) == count for frame, count in EXPECTED_FORMS.items()))
    check("cell_defaults_exact", all(cell_map[frame]["default_observed_phrase_de"] == phrase for frame, phrase in EXPECTED_DEFAULTS.items()))
    check("phrasebook_defaults_exact", all(phrasebook_map[frame]["default_observed_phrase_de"] == phrase for frame, phrase in EXPECTED_DEFAULTS.items()))
    check("cell_default_rule_exact", all(row["default_selection_rule"] == "MOST_CARRIERS_THEN_SHORTEST_THEN_LEXICAL" for row in cells))
    check("cell_defaults_observed", all(row["default_phrase_observed_not_invented"] == "YES" and row["default_observed_phrase_de"] in row["observed_clause_forms_de"].split(" || ") for row in cells))
    check("cell_all_roundtrip", all(row["all_carriers_roundtrip_exact"] == "YES" for row in cells))
    check("cell_meaning_examples_exact", cell_map["@ACTION+AIIN"]["frame_working_meaning_de"] == "MARKIEREN · WERT" and cell_map["@ACTION+AIN"]["frame_working_meaning_de"] == "MARKIEREN · ANTEIL" and cell_map["CH+@ACTION"]["frame_working_meaning_de"] == "NEHMEN · MARKIEREN")

    check("carrier_ids_unique", len({row["carrier_id"] for row in carriers}) == 46)
    check("carrier_event_ids_unique", len({row["global_running_event_id"] for row in carriers}) == 46)
    check("carrier_sources_exist", all(row["global_running_event_id"] in clause_map for row in carriers))
    check("carrier_source_identity_exact", all(row["global_statement_id"] == clause_map[row["global_running_event_id"]]["global_statement_id"] and row["physical_page"] == clause_map[row["global_running_event_id"]]["physical_page"] and row["surface"] == clause_map[row["global_running_event_id"]]["surface"] for row in carriers))
    check("carrier_recipe_exact", all(row["r_recipe"] == clause_map[row["global_running_event_id"]]["component_recipe"] and row["r_recipe"] == row["frozen_frame"].replace("@ACTION", "R") for row in carriers))
    check("carrier_clause_exact", all(row["imperative_clause_de"] == clause_map[row["global_running_event_id"]]["imperative_clause_de"] for row in carriers))
    check("carrier_readings_exact", all(row["owner_local_atom_reading_de"] == clause_map[row["global_running_event_id"]]["owner_local_atom_reading_de"] and row["portable_back_projection_de"] == clause_map[row["global_running_event_id"]]["portable_back_projection_de"] for row in carriers))
    check("carrier_roundtrip_exact", all(row["roundtrip_exact"] == "YES" for row in carriers))
    check("carrier_flags_exact", all(row["exact_gdt428_r_carrier"] == "YES" and row["phrase_observed_not_invented"] == "YES" for row in carriers))
    check("carrier_frame_profile_exact", Counter(row["frozen_frame"] for row in carriers) == Counter(EXPECTED_CARRIERS))
    check("carrier_page_count_16", len({row["physical_page"] for row in carriers}) == 16)
    check("carrier_register_set_exact", {row["register"] for row in carriers} == set(EXPECTED_REGISTERS))
    check("carrier_owner_class_count_10", len({row["owner_class"] for row in carriers}) == 10)

    tr_source = {row["frozen_frame"]: row for row in action_frames if row["contrast_pair"] == "T~R"}
    check("carrier_counts_match_gdt428", all(sum(row["frozen_frame"] == frame for row in carriers) == int(tr_source[frame]["right_event_count"]) for frame in EXPECTED_FRAMES))
    check("carrier_surfaces_in_gdt428", all(row["surface"] in tr_source[row["frozen_frame"]]["right_surfaces"].split("|") for row in carriers))

    check("form_ids_unique", len({row["form_id"] for row in forms}) == 22)
    check("form_frame_clause_unique", len({(row["frozen_frame"], row["observed_clause_de"]) for row in forms}) == 22)
    check("form_all_observed", all(row["observed_not_invented"] == "YES" for row in forms))
    check("form_all_roundtrip", all(row["all_roundtrip_exact"] == "YES" for row in forms))
    check("form_carrier_total_46", sum(int(row["carrier_count"]) for row in forms) == 46)
    check("form_event_ids_resolve", all(set(row["event_ids"].split("|")) <= {carrier["global_running_event_id"] for carrier in carriers} for row in forms))
    check("form_sources_recompute", all(int(row["carrier_count"]) == sum(carrier["frozen_frame"] == row["frozen_frame"] and carrier["imperative_clause_de"] == row["observed_clause_de"] for carrier in carriers) for row in forms))
    check("form_pages_recompute", all(set(row["pages"].split("|")) == {carrier["physical_page"] for carrier in carriers if carrier["frozen_frame"] == row["frozen_frame"] and carrier["imperative_clause_de"] == row["observed_clause_de"]} for row in forms))
    check("form_registers_recompute", all(set(row["registers"].split("|")) == {carrier["register"] for carrier in carriers if carrier["frozen_frame"] == row["frozen_frame"] and carrier["imperative_clause_de"] == row["observed_clause_de"]} for row in forms))
    check("form_profile_exact", Counter(row["frozen_frame"] for row in forms) == Counter(EXPECTED_FORMS))
    check("form_neutral_action_visible", all("@ACTION" in row["action_neutral_clause_de"] for row in forms))

    default_recomputed = True
    for frame in EXPECTED_FRAMES:
        local = [row for row in carriers if row["frozen_frame"] == frame]
        counter = Counter(row["imperative_clause_de"] for row in local)
        default, count = sorted(counter.items(), key=lambda item: (-item[1], len(item[0]), item[0]))[0]
        default_recomputed &= cell_map[frame]["default_observed_phrase_de"] == default
        default_recomputed &= int(cell_map[frame]["default_phrase_carrier_count"]) == count
        default_recomputed &= phrasebook_map[frame]["default_observed_phrase_de"] == default
    check("default_selection_recomputed", default_recomputed)
    check("phrasebook_all_observed", all(row["phrase_observed_not_invented"] == "YES" for row in phrasebook))
    check("phrasebook_alternative_counts_exact", all(int(row["alternative_observed_phrase_count"]) == EXPECTED_FORMS[row["frozen_frame"]] - 1 for row in phrasebook))
    check("phrasebook_source_sets_exact", all(set(row["source_pages"].split("|")) == set(cell_map[row["frozen_frame"]]["pages"].split("|")) and set(row["source_registers"].split("|")) == set(cell_map[row["frozen_frame"]]["registers"].split("|")) for row in phrasebook))

    check("contrast_selected_phrases_exact", all((contrast_map[frame]["t_selected_observed_phrase_de"], contrast_map[frame]["r_selected_observed_phrase_de"]) == pair for frame, pair in EXPECTED_SELECTED.items()))
    check("contrast_t_phrases_observed", all((row["frozen_frame"], row["t_selected_observed_phrase_de"]) in t_form_keys for row in contrasts))
    check("contrast_r_phrases_observed", all((row["frozen_frame"], row["r_selected_observed_phrase_de"]) in r_form_keys for row in contrasts))
    check("contrast_recipes_exact", all(row["t_recipe"] == row["frozen_frame"].replace("@ACTION", "T") and row["r_recipe"] == row["frozen_frame"].replace("@ACTION", "R") for row in contrasts))
    check("contrast_exact_frame_set", {row["frozen_frame"] for row in contrasts if row["german_sentence_remainder_match"] == "YES"} == EXACT_FRAMES)
    check("contrast_owner_variant_frame_set", {row["frozen_frame"] for row in contrasts if row["german_sentence_remainder_match"] == "NO"} == OWNER_VARIANT_FRAMES)
    check("contrast_match_recomputed", all((row["action_neutral_t_clause_de"] == row["action_neutral_r_clause_de"]) == (row["german_sentence_remainder_match"] == "YES") for row in contrasts))
    check("contrast_status_exact", all(row["contrast_status"] == ("RESTGLEICH" if row["frozen_frame"] in EXACT_FRAMES else "OWNER-VARIANTE") for row in contrasts))
    check("contrast_flags_exact", all(row["unchanged_formal_frame"] == "YES" and row["both_phrases_observed_not_invented"] == "YES" for row in contrasts))
    check("contrast_selection_rule_typed", all(row["pair_selection_rule"] == ("MAX_SUPPORT_PRODUCT_THEN_TOTAL_THEN_SHORTEST_AMONG_EXACT_ACTION_NEUTRAL_MATCHES" if row["frozen_frame"] in EXACT_FRAMES else "INDEPENDENT_OBSERVED_DEFAULTS_WHEN_NO_EXACT_ACTION_NEUTRAL_MATCH_EXISTS") for row in contrasts))
    check("contrast_selected_default_counts", (sum(row["t_selected_is_atlas_default"] == "YES" for row in contrasts), sum(row["r_selected_is_atlas_default"] == "YES" for row in contrasts)) == (7, 9))
    check("exact_remainder_rows_are_subset", exact_rests == [row for row in contrasts if row["frozen_frame"] in EXACT_FRAMES])
    check("owner_variant_rows_are_subset", owner_variants == [row for row in contrasts if row["frozen_frame"] in OWNER_VARIANT_FRAMES])

    register_map = {row["register"]: row for row in registers}
    check("register_set_exact", set(register_map) == set(EXPECTED_REGISTERS))
    check("register_ids_unique", len({row["register_id"] for row in registers}) == 5)
    check("register_counts_exact", all(tuple(int(register_map[name][field]) for field in ("carrier_count", "frame_count", "observed_clause_form_count", "page_count")) == counts for name, counts in EXPECTED_REGISTERS.items()))
    check("register_carrier_total_46", sum(int(row["carrier_count"]) for row in registers) == 46)
    check("register_all_roundtrip", all(row["all_roundtrip_exact"] == "YES" for row in registers))
    check("register_all_observed", all(row["all_phrases_observed_not_invented"] == "YES" for row in registers))
    check("register_frames_recompute", all(set(row["frames"].split("|")) == {carrier["frozen_frame"] for carrier in carriers if carrier["register"] == row["register"]} for row in registers))
    check("register_pages_recompute", all(set(row["pages"].split("|")) == {carrier["physical_page"] for carrier in carriers if carrier["register"] == row["register"]} for row in registers))

    check("readable_core_counts", "**11/11**" in readable and "**46**" in readable and "**16 Seiten**" in readable and "**5 Registern**" in readable and "**22**" in readable and "**7/11**" in readable and "**4/11**" in readable)
    check("readable_all_frames", all(f"`{frame}`" in readable for frame in EXPECTED_FRAMES))
    check("readable_all_defaults", all(phrase in readable for phrase in EXPECTED_DEFAULTS.values()))
    check("readable_all_selected_pairs", all(pair[0] in readable and pair[1] in readable for pair in EXPECTED_SELECTED.values()))
    check("readable_all_r_forms", all(row["observed_clause_de"] in readable for row in forms))
    check("readable_owner_variant_warning", "kein künstlich vereinheitlichter Satz" in readable)
    check("readable_next_route", "sieben restgleichen Paare" in readable and "vier Owner-Varianten" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_core_counts_exact", (result.get("frame_count"), result.get("readable_r_carrier_count"), result.get("observed_r_clause_form_count"), result.get("observed_r_default_phrase_count"), result.get("invented_phrase_count")) == (11, 46, 22, 11, 0))
    check("result_scope_counts_exact", (result.get("page_count"), result.get("register_count"), result.get("owner_class_count")) == (16, 5, 10))
    check("result_contrast_counts_exact", (result.get("tr_contrast_card_count"), result.get("exact_german_remainder_pair_count"), result.get("owner_variant_contrast_count")) == (11, 7, 4))
    check("result_flags_true", result.get("all_frames_have_observed_r_phrase") is True and result.get("all_carriers_roundtrip_exact") is True and result.get("all_contrast_phrases_observed") is True and result.get("all_contrast_frames_formally_unchanged") is True)
    check("result_selected_default_counts", (result.get("t_selected_default_count"), result.get("r_selected_default_count")) == (7, 9))
    unchanged = ("meaning_change_count", "wording_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "seven cards share an exact German remainder" in result.get("claim_ceiling", "") and "no invented phrase" in result.get("claim_ceiling", ""))

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
