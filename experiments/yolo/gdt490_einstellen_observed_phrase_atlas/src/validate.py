#!/usr/bin/env python3
"""Validate GDT490's observed EINSTELLEN phrase atlas."""

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
BASE = ROOT / "experiments/yolo/gdt490_einstellen_observed_phrase_atlas"
OUT = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G489 = ROOT / "experiments/yolo/gdt489_einstellen_typed_composition_neighbourhood/artifacts"
RUN = BASE / "src/run.py"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
ACTION_FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
LOCAL_FRAME_ATLAS_IN = G489 / "gdt489_11_tr_composition_frames.tsv"
CARRIERS = OUT / "gdt490_30_readable_t_carriers.tsv"
FORMS = OUT / "gdt490_22_observed_t_clause_forms.tsv"
CELLS = OUT / "gdt490_11_t_frame_phrase_cells.tsv"
PHRASEBOOK = OUT / "gdt490_11_observed_default_phrases.tsv"
REGISTERS = OUT / "gdt490_5_register_phrase_support.tsv"
ABSENT_RECOVERY = OUT / "gdt490_1_absent_local_context_recovery.tsv"
READABLE = OUT / "GDT490_EINSTELLEN_OBSERVED_PHRASE_ATLAS.md"
RESULT = OUT / "gdt490_result.json"
VALIDATION = OUT / "gdt490_validation.json"
STATUS = "ALL_ELEVEN_T_FRAMES_HAVE_OBSERVED_PHRASES__TWENTY_TWO_FORMS__ZERO_INVENTED"
EXPECTED_FRAMES = [
    "@ACTION", "@ACTION+AIIN", "@ACTION+AIN", "@ACTION+AL",
    "@ACTION+AL+Y", "@ACTION+CH+E+Y", "@ACTION+CHD+Y",
    "@ACTION+OL", "@ACTION+OR+Y", "@ACTION+Y", "CH+@ACTION",
]
EXPECTED_CARRIERS = dict(zip(EXPECTED_FRAMES, (1, 5, 2, 3, 1, 1, 5, 7, 1, 3, 1)))
EXPECTED_FORMS = dict(zip(EXPECTED_FRAMES, (1, 3, 2, 2, 1, 1, 2, 6, 1, 2, 1)))
EXPECTED_DEFAULTS = {
    "@ACTION": "Stelle den Pflanzenposten [wie zuvor] ein.",
    "@ACTION+AIIN": "Stelle den Arbeitswert ein.",
    "@ACTION+AIN": "Stelle den Drogenanteil ein.",
    "@ACTION+AL": "Stelle den Stationsposten [wie zuvor] ein; zur Zielstation.",
    "@ACTION+AL+Y": "Stelle den Positionsposten ein; zur Zielposition.",
    "@ACTION+CH+E+Y": "Lege den laufenden Eintrag fest und entnimm den laufenden Eintrag; auf Grad I.",
    "@ACTION+CHD+Y": "Stelle den Stationsposten ein und bearbeite den Stationsposten.",
    "@ACTION+OL": "Weiter stelle den Pflanzenposten [wie zuvor] ein.",
    "@ACTION+OR+Y": "Stelle die Arbeitseinheit und den Pflanzenposten ein.",
    "@ACTION+Y": "Stelle den Pflanzenposten ein.",
    "CH+@ACTION": "Nimm den Arbeitswert [wie zuvor] und stelle den Arbeitswert [wie zuvor] ein.",
}
EXPECTED_REGISTERS = {
    "SOURCE_SECTION_T": (2, 2, 2, 1),
    "HERBAL": (11, 7, 8, 5),
    "CELESTIAL": (2, 2, 2, 2),
    "BIOLOGICAL": (11, 6, 6, 5),
    "PHARMA": (4, 3, 4, 2),
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

    generated = [CARRIERS, FORMS, CELLS, PHRASEBOOK, REGISTERS, ABSENT_RECOVERY, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT490 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    clauses = read_tsv(CLAUSES_IN)
    action_frames = read_tsv(ACTION_FRAMES_IN)
    local_frames = read_tsv(LOCAL_FRAME_ATLAS_IN)
    carriers = read_tsv(CARRIERS)
    forms = read_tsv(FORMS)
    cells = read_tsv(CELLS)
    phrasebook = read_tsv(PHRASEBOOK)
    registers = read_tsv(REGISTERS)
    recovery = read_tsv(ABSENT_RECOVERY)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    clause_map = {row["global_running_event_id"]: row for row in clauses}
    cell_map = {row["frozen_frame"]: row for row in cells}
    phrasebook_map = {row["frozen_frame"]: row for row in phrasebook}
    local_map = {row["frozen_frame"]: row for row in local_frames}

    check("source_clause_count_4576", len(clauses) == 4576, len(clauses))
    check("source_action_frame_count_104", len(action_frames) == 104, len(action_frames))
    check("source_local_frame_count_11", len(local_frames) == 11, len(local_frames))
    check("source_tr_frame_count_11", sum(row["contrast_pair"] == "T~R" for row in action_frames) == 11)
    check("carrier_count_30", len(carriers) == 30, len(carriers))
    check("form_count_22", len(forms) == 22, len(forms))
    check("cell_count_11", len(cells) == 11, len(cells))
    check("phrasebook_count_11", len(phrasebook) == 11, len(phrasebook))
    check("register_count_5", len(registers) == 5, len(registers))
    check("recovery_count_1", len(recovery) == 1, len(recovery))

    check("cell_frame_order_exact", [row["frozen_frame"] for row in cells] == EXPECTED_FRAMES)
    check("phrasebook_frame_order_exact", [row["frozen_frame"] for row in phrasebook] == EXPECTED_FRAMES)
    check("cell_ids_unique", len({row["cell_id"] for row in cells}) == 11)
    check("frame_ids_unique", len({row["frame_id"] for row in cells}) == 11)
    check("phrasebook_ids_unique", len({row["phrasebook_id"] for row in phrasebook}) == 11)
    check("cell_carrier_counts_exact", all(int(cell_map[frame]["carrier_count"]) == count for frame, count in EXPECTED_CARRIERS.items()))
    check("cell_form_counts_exact", all(int(cell_map[frame]["observed_clause_form_count"]) == count for frame, count in EXPECTED_FORMS.items()))
    check("cell_defaults_exact", all(cell_map[frame]["default_observed_phrase_de"] == phrase for frame, phrase in EXPECTED_DEFAULTS.items()))
    check("phrasebook_defaults_exact", all(phrasebook_map[frame]["default_observed_phrase_de"] == phrase for frame, phrase in EXPECTED_DEFAULTS.items()))
    check("cell_default_selection_rule_exact", all(row["default_selection_rule"] == "MOST_CARRIERS_THEN_SHORTEST_THEN_LEXICAL" for row in cells))
    check("cell_defaults_observed", all(row["default_phrase_observed_not_invented"] == "YES" and row["default_observed_phrase_de"] in row["observed_clause_forms_de"].split(" || ") for row in cells))
    check("cell_all_roundtrip", all(row["all_carriers_roundtrip_exact"] == "YES" for row in cells))
    check("cell_local_support_exact", all(row["gdt489_local_context_witness_count"] == local_map[row["frozen_frame"]]["local_context_witness_count"] and row["gdt489_local_t_contact_count"] == local_map[row["frozen_frame"]]["local_t_nonempty_contact_count"] and row["gdt489_local_support_class"] == local_map[row["frozen_frame"]]["local_support_class"] for row in cells))
    check("cell_meaning_examples_exact", cell_map["@ACTION+AIIN"]["frame_working_meaning_de"] == "EINSTELLEN · WERT" and cell_map["@ACTION+AIN"]["frame_working_meaning_de"] == "EINSTELLEN · ANTEIL" and cell_map["@ACTION+AL"]["frame_working_meaning_de"] == "EINSTELLEN · ZIELORT" and cell_map["CH+@ACTION"]["frame_working_meaning_de"] == "NEHMEN · EINSTELLEN")

    check("carrier_ids_unique", len({row["carrier_id"] for row in carriers}) == 30)
    check("carrier_event_ids_unique", len({row["global_running_event_id"] for row in carriers}) == 30)
    check("carrier_sources_exist", all(row["global_running_event_id"] in clause_map for row in carriers))
    check("carrier_source_identity_exact", all(row["global_statement_id"] == clause_map[row["global_running_event_id"]]["global_statement_id"] and row["physical_page"] == clause_map[row["global_running_event_id"]]["physical_page"] and row["surface"] == clause_map[row["global_running_event_id"]]["surface"] for row in carriers))
    check("carrier_recipe_exact", all(row["t_recipe"] == clause_map[row["global_running_event_id"]]["component_recipe"] and row["t_recipe"] == row["frozen_frame"].replace("@ACTION", "T") for row in carriers))
    check("carrier_clause_exact", all(row["imperative_clause_de"] == clause_map[row["global_running_event_id"]]["imperative_clause_de"] for row in carriers))
    check("carrier_readings_exact", all(row["owner_local_atom_reading_de"] == clause_map[row["global_running_event_id"]]["owner_local_atom_reading_de"] and row["portable_back_projection_de"] == clause_map[row["global_running_event_id"]]["portable_back_projection_de"] for row in carriers))
    check("carrier_roundtrip_exact", all(row["roundtrip_exact"] == "YES" for row in carriers))
    check("carrier_flags_exact", all(row["exact_gdt428_t_carrier"] == "YES" and row["phrase_observed_not_invented"] == "YES" for row in carriers))
    check("carrier_frame_profile_exact", Counter(row["frozen_frame"] for row in carriers) == Counter(EXPECTED_CARRIERS))
    check("carrier_page_count_15", len({row["physical_page"] for row in carriers}) == 15)
    check("carrier_register_set_exact", {row["register"] for row in carriers} == set(EXPECTED_REGISTERS))
    check("carrier_owner_class_count_9", len({row["owner_class"] for row in carriers}) == 9)

    tr_source = {row["frozen_frame"]: row for row in action_frames if row["contrast_pair"] == "T~R"}
    check("carrier_counts_match_gdt428", all(sum(row["frozen_frame"] == frame for row in carriers) == int(tr_source[frame]["left_event_count"]) for frame in EXPECTED_FRAMES))
    check("carrier_surfaces_in_gdt428", all(row["surface"] in tr_source[row["frozen_frame"]]["left_surfaces"].split("|") for row in carriers))

    check("form_ids_unique", len({row["form_id"] for row in forms}) == 22)
    check("form_frame_clause_unique", len({(row["frozen_frame"], row["observed_clause_de"]) for row in forms}) == 22)
    check("form_all_observed", all(row["observed_not_invented"] == "YES" for row in forms))
    check("form_all_roundtrip", all(row["all_roundtrip_exact"] == "YES" for row in forms))
    check("form_carrier_total_30", sum(int(row["carrier_count"]) for row in forms) == 30)
    check("form_event_ids_resolve", all(set(row["event_ids"].split("|")) <= {carrier["global_running_event_id"] for carrier in carriers} for row in forms))
    check("form_sources_recompute", all(int(row["carrier_count"]) == sum(carrier["frozen_frame"] == row["frozen_frame"] and carrier["imperative_clause_de"] == row["observed_clause_de"] for carrier in carriers) for row in forms))
    check("form_pages_recompute", all(set(row["pages"].split("|")) == {carrier["physical_page"] for carrier in carriers if carrier["frozen_frame"] == row["frozen_frame"] and carrier["imperative_clause_de"] == row["observed_clause_de"]} for row in forms))
    check("form_registers_recompute", all(set(row["registers"].split("|")) == {carrier["register"] for carrier in carriers if carrier["frozen_frame"] == row["frozen_frame"] and carrier["imperative_clause_de"] == row["observed_clause_de"]} for row in forms))
    check("form_profile_exact", Counter(row["frozen_frame"] for row in forms) == Counter(EXPECTED_FORMS))

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

    register_map = {row["register"]: row for row in registers}
    check("register_set_exact", set(register_map) == set(EXPECTED_REGISTERS))
    check("register_ids_unique", len({row["register_id"] for row in registers}) == 5)
    check("register_counts_exact", all(tuple(int(register_map[name][field]) for field in ("carrier_count", "frame_count", "observed_clause_form_count", "page_count")) == counts for name, counts in EXPECTED_REGISTERS.items()))
    check("register_carrier_total_30", sum(int(row["carrier_count"]) for row in registers) == 30)
    check("register_all_roundtrip", all(row["all_roundtrip_exact"] == "YES" for row in registers))
    check("register_all_observed", all(row["all_phrases_observed_not_invented"] == "YES" for row in registers))
    check("register_frames_recompute", all(set(row["frames"].split("|")) == {carrier["frozen_frame"] for carrier in carriers if carrier["register"] == row["register"]} for row in registers))
    check("register_pages_recompute", all(set(row["pages"].split("|")) == {carrier["physical_page"] for carrier in carriers if carrier["register"] == row["register"]} for row in registers))

    recovered = recovery[0]
    check("recovery_id_exact", recovered["recovery_id"] == "G490-AR01")
    check("recovery_frame_exact", recovered["frozen_frame"] == "@ACTION+CHD+Y" and recovered["t_recipe"] == "T+CHD+Y")
    check("recovery_local_absence_exact", recovered["gdt489_local_context_status"] == "ABSENT_LOCAL_CONTEXT" and recovered["gdt489_local_context_witness_count"] == "0")
    check("recovery_carrier_counts_exact", (recovered["gdt416_readable_t_carrier_count"], recovered["gdt416_page_count"], recovered["observed_clause_form_count"]) == ("5", "3", "2"))
    check("recovery_pages_exact", set(recovered["gdt416_pages"].split("|")) == {"f75r", "f83r", "f95v"})
    check("recovery_registers_exact", set(recovered["gdt416_registers"].split("|")) == {"BIOLOGICAL", "HERBAL"})
    check("recovery_default_exact", recovered["default_observed_phrase_de"] == EXPECTED_DEFAULTS["@ACTION+CHD+Y"])
    check("recovery_flags_exact", recovered["local_absence_retained"] == "YES" and recovered["phrase_capacity_recovered_from_admitted_pages"] == "YES" and recovered["phrase_observed_not_invented"] == "YES")

    priority = {"@ACTION+AIIN", "@ACTION+AIN", "@ACTION+AL", "@ACTION+OL", "@ACTION+Y"}
    check("priority_frames_exact", priority <= set(cell_map))
    check("priority_frames_all_have_phrases", all(int(cell_map[frame]["observed_clause_form_count"]) > 0 for frame in priority))
    check("priority_default_phrases_visible", all(EXPECTED_DEFAULTS[frame] in readable for frame in priority))

    check("readable_core_counts", "**11/11**" in readable and "**30**" in readable and "**15 Seiten**" in readable and "**5 Registern**" in readable and "**22**" in readable and "**0**" in readable)
    check("readable_all_frames", all(f"`{frame}`" in readable for frame in EXPECTED_FRAMES))
    check("readable_all_defaults", all(phrase in readable for phrase in EXPECTED_DEFAULTS.values()))
    check("readable_all_forms", all(row["observed_clause_de"] in readable for row in forms))
    check("readable_absent_recovery", "lokal fehlende Kontext ist sprachlich nicht leer" in readable and "fünf T-Träger" in readable)
    check("readable_next_route", "R=MARKIEREN" in readable and "T- und R-Defaults" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_core_counts_exact", (result.get("frame_count"), result.get("readable_t_carrier_count"), result.get("observed_clause_form_count"), result.get("observed_default_phrase_count"), result.get("invented_phrase_count")) == (11, 30, 22, 11, 0))
    check("result_scope_counts_exact", (result.get("page_count"), result.get("register_count"), result.get("owner_class_count")) == (15, 5, 9))
    check("result_priority_counts_exact", (result.get("priority_frame_count"), result.get("priority_frame_with_observed_phrase_count")) == (5, 5))
    check("result_flags_true", result.get("all_frames_have_observed_phrase") is True and result.get("all_carriers_roundtrip_exact") is True)
    check("result_recovery_count_1", result.get("formerly_absent_local_context_recovery_count") == 1)
    unchanged = ("meaning_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "all defaults are existing" in result.get("claim_ceiling", "") and "no invented phrase" in result.get("claim_ceiling", ""))

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
