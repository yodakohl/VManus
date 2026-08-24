#!/usr/bin/env python3
"""Align the five complete cases by shared workshop phase and branch cue."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MODULE_DIR = ROOT / "experiments/yolo/sidequest_semantic_case_modules_six_hundred_nineteenth"
LAYER_DIR = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"
WORD_DIR = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth"
ARCH_DIR = ROOT / "experiments/yolo/sidequest_semantic_six_case_astro_architecture_six_hundred_twenty_fourth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


TEACHING_ORDER = {
    "M01": (1, "DOSIEREN", "Sollmass, Portion, Nachportion oder Arbeitsstufe setzen"),
    "M02": (2, "ANSETZEN_BEHANDELN", "aktiven Posten ansetzen oder behandeln"),
    "M03": (3, "ADRESSIEREN_WEITERLEITEN", "Vorrat, Lauf, Kanal, Zielstelle oder Fach waehlen und bewegen"),
    "M04": (4, "HALTEN_ABSETZEN", "Posten halten, gradieren oder absetzen"),
    "M05": (5, "AUFFANGEN", "abgenommenen oder weitergeleiteten Bestand auffangen"),
    "M06": (6, "FORTSETZEN", "denselben Arbeitsfaden fortsetzen oder spaeter wiederaufnehmen"),
    "M07": (7, "BEREITSCHAFT_PRUEFEN", "bis zum bereiten Zustand arbeiten"),
    "M08": (8, "SCHLIESSEN", "lokalen Arbeitsschritt mit lizenzierter Schlusskarte beenden"),
}


BRANCH_COMPONENTS = {
    "AIR": ("M03", "FLUESSIGKEITSLAUF", "sichtbaren oder gedachten Fluessigkeitslauf als Transferpfad benutzen"),
    "AN": ("M01", "NACHPORTION", "nach der ersten Portion eine zweite Portion ansetzen"),
    "CFH": ("M03", "AUSWRINGEN", "bereiteten Stoff ausdruecken oder auswringen"),
    "CTH": ("M07", "BEREIT", "einen ausdruecklichen Bereitzustand verlangen"),
    "DA": ("M01", "ZWEITMARKER", "einen zweiten Einsatz oder zweite Stufe markieren"),
    "EEE": ("M02", "VOLL", "eine Behandlung bis zum Vollgrad fuehren"),
    "HO": ("M02", "ZUTAT", "wiederholt weitere Zutat in den aktiven Ansatz bringen"),
    "LD": ("M03", "BEFESTIGEN", "den angesetzten Posten an der Zielstelle festmachen"),
    "LSH": ("M02", "WASCHEN", "einen ausdruecklichen Waschgang ausfuehren"),
    "OS": ("M03", "ARBEITSFACH", "ein bestimmtes Arbeitsfach adressieren"),
    "P": ("M03", "EINFUELLEN", "Bestand in einen lokalen Empfaenger fuellen"),
    "R": ("M04", "KUEHLEN", "Arbeitsbestand vor dem naechsten Schritt kuehlen"),
    "RESUME_CARD": ("M06", "WIEDERAUFNEHMEN", "einen frueheren Arbeitsfaden wieder aufnehmen"),
    "S": ("M01", "TEILEN", "Charge oder Portion in getrennte Teile gliedern"),
    "T": ("M03", "EINTRAGEN", "aktiven Posten in Fach oder Ablauf eintragen"),
    "TALAM": ("M08", "VERWAHREN", "fertigen oder befestigten Posten verwahren"),
}


CASE_BRANCHES = {
    "C1": ("MILD_WASH_AND_WORK_COMPARTMENT", "LSH=WASCHEN und OS=ARBEITSFACH", "milder Grundgang mit ausdruecklichem Waschen und eigenem Arbeitsfach"),
    "C2": ("DIVIDED_FULL_TREATMENT", "S=TEILEN; hohe Dosierdichte; EEE=VOLL und P=EINFUELLEN", "geteilt dosierter Nach-/Spuelgang mit Vollbehandlung und Empfaengerfuellung"),
    "C3": ("FLOWER_EXTRACTION_AND_IMMERSION", "CFH=AUSWRINGEN; EEE=VOLL; P=EINFUELLEN; sechs Bereitschaftsstellen", "Bluetenauszug mit Auswringen, Gefaessfuellung, Vollgrad und wiederholter Bereitschaft"),
    "C4": ("PORTION_AFTERPORTION_CONTACT", "AN=NACHPORTION; LD=BEFESTIGEN; TALAM=VERWAHREN", "Kontakt-/Auflagegang mit Portion, Nachportion, Befestigung und Verwahrung"),
    "C5": ("ADDITIVE_CONCENTRATE_TRANSFER", "HO=ZUTAT achtmal; DA=ZWEITMARKER; kein Auffang- oder Bereitschaftsmodul", "zutatendichter Konzentratgang, der weiterleitet und haelt, ohne eigenen Bereit-Check"),
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    module_matrix = read_tsv(MODULE_DIR / "SIX_HUNDRED_NINETEENTH_48_CASE_MODULE_MATRIX.tsv")
    modules = read_tsv(MODULE_DIR / "SIX_HUNDRED_NINETEENTH_8_WORKSHOP_MODULES.tsv")
    events = read_tsv(LAYER_DIR / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    words = read_tsv(WORD_DIR / "SIX_HUNDRED_SEVENTEENTH_39_SHARP_WORDS.tsv")
    architecture = read_tsv(ARCH_DIR / "SIX_HUNDRED_TWENTY_FOURTH_6_CASE_ARCHITECTURE.tsv")
    main_cases = [f"C{i}" for i in range(1, 6)]
    word_by_component = {row["canonical_component"]: row for row in words}
    arch_by_case = {row["case_id"]: row for row in architecture}

    phase_rows = []
    for row in module_matrix:
        if row["case_id"] not in main_cases:
            continue
        order, name, reading = TEACHING_ORDER[row["module_id"]]
        total = int(row["total_statements"])
        phase_rows.append({
            "teaching_order": order,
            "module_id": row["module_id"],
            "phase_name_de": name,
            "case_id": row["case_id"],
            "case_title_de": arch_by_case[row["case_id"]]["case_title_de"],
            "prepare_statements": row["prepare_statements"],
            "operate_apply_statements": row["operate_apply_statements"],
            "total_statements": total,
            "phase_present": "YES" if total else "NO",
            "statement_ids": row["statement_ids"],
            "phase_reading_de": reading,
        })
    phase_rows.sort(key=lambda row: (int(row["teaching_order"]), row["case_id"]))

    component_counts: dict[str, Counter[str]] = defaultdict(Counter)
    component_sets: dict[str, set[str]] = defaultdict(set)
    for row in events:
        if row["case_id"] not in main_cases:
            continue
        for component in row["semantic_component_parse"].split("+"):
            component_counts[row["case_id"]][component] += 1
            component_sets[row["case_id"]].add(component)

    common = set.intersection(*(component_sets[case] for case in main_cases))
    common_rows = []
    for component in sorted(common):
        word = word_by_component[component]
        common_rows.append({
            "component": component,
            "spoken_workshop_word_de": word["spoken_workshop_word_de"],
            "sentence_role": word["sentence_role"],
            "c1_events": component_counts["C1"][component],
            "c2_events": component_counts["C2"][component],
            "c3_events": component_counts["C3"][component],
            "c4_events": component_counts["C4"][component],
            "c5_events": component_counts["C5"][component],
            "total_events": sum(component_counts[case][component] for case in main_cases),
            "core_status": "PRESENT_IN_ALL_FIVE_COMPLETE_CASES",
        })

    union = set.union(*(component_sets[case] for case in main_cases))
    branch_rows = []
    for component in sorted(union):
        case_ids = [case for case in main_cases if component in component_sets[case]]
        if len(case_ids) > 3:
            continue
        module_id, spoken, branch = BRANCH_COMPONENTS[component]
        branch_rows.append({
            "component": component,
            "spoken_workshop_word_de": spoken,
            "module_id": module_id,
            "case_count": len(case_ids),
            "case_ids": "|".join(case_ids),
            "event_counts_by_case": "|".join(f"{case}:{component_counts[case][component]}" for case in case_ids),
            "unique_to_one_case": "YES" if len(case_ids) == 1 else "NO",
            "branch_contribution_de": branch,
        })

    module_presence = defaultdict(dict)
    for row in phase_rows:
        module_presence[row["case_id"]][row["module_id"]] = int(row["total_statements"])
    case_rows = []
    for case_id in main_cases:
        branch_id, cue, reading = CASE_BRANCHES[case_id]
        exclusive = sorted(component_sets[case_id] - set.union(*(component_sets[other] for other in main_cases if other != case_id)))
        absent_modules = [module for module in TEACHING_ORDER if module_presence[case_id][module] == 0]
        case_rows.append({
            "case_id": case_id,
            "case_title_de": arch_by_case[case_id]["case_title_de"],
            "branch_id": branch_id,
            "branch_cues_de": cue,
            "case_specific_reading_de": reading,
            "exclusive_components": "|".join(exclusive),
            "absent_modules": "|".join(absent_modules) if absent_modules else "NONE",
            "six_module_core_present": "YES" if all(module_presence[case_id][module] > 0 for module in ("M01", "M02", "M03", "M04", "M06", "M08")) else "NO",
            "statements": arch_by_case[case_id]["statements"],
            "events": arch_by_case[case_id]["events"],
        })

    write_tsv(HERE / "SIX_HUNDRED_TWENTY_FIFTH_40_CASE_PHASE_ALIGNMENT.tsv", phase_rows, list(phase_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_FIFTH_19_COMMON_CORE_COMPONENTS.tsv", common_rows, list(common_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_FIFTH_16_BRANCH_COMPONENTS.tsv", branch_rows, list(branch_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_FIFTH_5_CASE_BRANCH_SUMMARY.tsv", case_rows, list(case_rows[0]))

    md = [
        "# Lehrmeistertafel: ein Grundablauf, fuenf konkrete Fallzweige",
        "",
        "## Gemeinsamer Kern",
        "",
        "Alle fuenf vollstaendigen Faelle besitzen dieselben sechs Module: DOSIEREN, ANSETZEN/BEHANDELN, ADRESSIEREN/WEITERLEITEN, HALTEN/ABSETZEN, FORTSETZEN und SCHLIESSEN. AUFFANGEN fehlt C5; ein ausdruecklicher BEREIT-Check fehlt C4 und C5.",
        "",
        "Die folgende Reihenfolge ist die Lehrordnung, nicht die Behauptung, dass jedes Modul nur einmal oder immer in dieser Chronologie vorkommt.",
        "",
    ]
    rows_by_module: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in phase_rows:
        rows_by_module[str(row["module_id"])].append(row)
    for module_id in TEACHING_ORDER:
        order, name, reading = TEACHING_ORDER[module_id]
        md.extend([f"## {order}. {name}", "", reading + ".", ""])
        for row in rows_by_module[module_id]:
            md.append(f"- **{row['case_id']}**: {row['total_statements']} Aussagen — {row['statement_ids']}")
        md.append("")
    md.extend(["# Die fuenf Abzweigungen", ""])
    for row in case_rows:
        md.extend([
            f"## {row['case_id']}: {row['case_title_de']}",
            "",
            f"**Spezifischer Zug:** {row['case_specific_reading_de']}.",
            "",
            f"**Lehrzeichen:** {row['branch_cues_de']}.",
            "",
            f"**Nur hier:** {row['exclusive_components']}. Fehlende Module: {row['absent_modules']}.",
            "",
        ])
    md.extend([
        "# Kurze Schreibregel fuer den Lehrling",
        "",
        "1. Bildpflanze oder aktive Station als stillen Besitzer festlegen.",
        "2. Fallzweig C1 bis C5 bestimmen.",
        "3. Sollmass/Portion/Stufe setzen und den Posten ansetzen.",
        "4. Vorrat, Fluessigkeitslauf, Kanal, Zielstelle oder Arbeitsfach adressieren.",
        "5. Den Fallzweig ausfuehren: waschen, teilen, auswringen, nachdosieren/befestigen oder Zutaten zufuehren.",
        "6. Kurz/lang/voll halten, absetzen, gegebenenfalls auffangen und fortsetzen.",
        "7. Falls der Fall einen Bereit-Check besitzt, ihn vor dem lokalen Schluss lesen.",
        "8. Nur mit einer lizenzierten Schlusskarte schliessen.",
        "",
        "C6 wird nicht in diese Fuenferfolge gepresst. Es bleibt eine eigene offene Nachtragsschablone.",
    ])
    (HERE / "SIX_HUNDRED_TWENTY_FIFTH_FIVE_CASE_VARIANT_MANUAL.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    module_present_cases = {
        module: sum(module_presence[case][module] > 0 for case in main_cases)
        for module in TEACHING_ORDER
    }
    summary = {
        "status": "PASS",
        "complete_cases": len(main_cases),
        "phase_rows": len(phase_rows),
        "modules": len(TEACHING_ORDER),
        "modules_present_in_all_five": sum(value == 5 for value in module_present_cases.values()),
        "universal_module_ids": [module for module, value in module_present_cases.items() if value == 5],
        "optional_module_ids": [module for module, value in module_present_cases.items() if value < 5],
        "common_components": len(common_rows),
        "low_mobility_branch_components": len(branch_rows),
        "single_case_components": sum(row["unique_to_one_case"] == "YES" for row in branch_rows),
        "covered_statements": sum(int(arch_by_case[case]["statements"]) for case in main_cases),
        "covered_events": sum(int(arch_by_case[case]["events"]) for case in main_cases),
        "new_words": 0,
        "decision": "SIX_MODULE_COMMON_PROCEDURE_WITH_FIVE_CASE_SPECIFIC_BRANCHES",
    }
    (HERE / "SIX_HUNDRED_TWENTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
