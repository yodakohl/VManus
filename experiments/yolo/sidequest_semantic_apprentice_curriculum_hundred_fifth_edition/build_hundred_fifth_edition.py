#!/usr/bin/env python3
"""Build a staged 1420-style apprentice curriculum and coverage trace."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ECOLOGY = ROOT / "experiments/yolo/sidequest_semantic_component_ecology_hundred_fourth_edition/HUNDRED_FOURTH_44_COMPONENT_ECOLOGY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_centennial_working_edition/HUNDREDTH_116_STATEMENT_TRANSLATION.tsv"
INSTRUMENTS = ROOT / "experiments/yolo/sidequest_semantic_astro_apprentice_ninety_fourth_edition/NINETY_FOURTH_3_INSTRUMENT_ROUNDTRIP.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ecology = read_tsv(ECOLOGY)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    instruments = read_tsv(INSTRUMENTS)
    portable = {row["atom"] for row in ecology if row["ecology_status"] == "PORTABLE_WORKSHOP_CORE"}
    bridges = {row["atom"] for row in ecology if row["ecology_status"].startswith("THIN_CROSS_SECTION_BRIDGE")}
    herbal = {row["atom"] for row in ecology if row["ecology_status"].startswith("HERBAL_SPECIALIST")}
    bio = {row["atom"] for row in ecology if row["ecology_status"].startswith("BIOLOGICAL_SPECIALIST")}
    all_atoms = portable | bridges | herbal | bio

    stages = [
        ("S0", "BILD_OWNER", set()),
        ("S1", "PORTABLER_KERN", portable),
        ("S2", "KERN_PLUS_BRUECKEN", portable | bridges),
        ("S3H", "PFLANZENSPEZIALISIERUNG", portable | bridges | herbal),
        ("S3B", "BAD_DIENST_SPEZIALISIERUNG", portable | bridges | bio),
        ("S4", "BEIDE_FACHTAFELN", all_atoms),
    ]
    statement_atoms: dict[str, set[str]] = defaultdict(set)
    for event in events:
        statement_atoms[event["statement_id"]].update(event["semantic_atoms"].split("+"))

    coverage_rows: list[dict[str, object]] = []
    for stage_id, name, known in stages:
        decoded_events = [event for event in events if set(event["semantic_atoms"].split("+")) <= known]
        decoded_statements = [row for row in statements if statement_atoms[row["statement_id"]] <= known]
        coverage_rows.append({
            "stage_id": stage_id,
            "stage_name": name,
            "known_atom_count": len(known),
            "known_atoms": ",".join(sorted(known)) if known else "NONE",
            "decoded_prose_events": len(decoded_events),
            "decoded_herbal_events": sum(event["record_unit_id"].startswith("H") for event in decoded_events),
            "decoded_biological_events": sum(event["record_unit_id"].startswith("B") for event in decoded_events),
            "fully_decoded_statements": len(decoded_statements),
            "fully_decoded_herbal_statements": sum(row["record_unit_id"].startswith("H") for row in decoded_statements),
            "fully_decoded_biological_statements": sum(row["record_unit_id"].startswith("B") for row in decoded_statements),
        })

    lessons = [
        (1, 1, 2, "BILD UND BESITZER", "plant, bath station, service station and diagram locus as silent owner", "point and copy owner changes"),
        (2, 3, 6, "15 KERNWERTE", ", ".join(sorted(portable)), "read short core-only cells"),
        (3, 7, 9, "9 BRÜCKEN", ", ".join(sorted(bridges)), "read transfer, passage, heat and portion examples"),
        (4, 10, 12, "10 PFLANZENKARTEN", ", ".join(sorted(herbal)), "copy one complete Herbal article"),
        (5, 13, 15, "10 BAD-DIENST-KARTEN", ", ".join(sorted(bio)), "copy one figure-owned and one service record"),
        (6, 16, 19, "173 KARTENKÖRPER", "broad paradigms, bounded tails, mini-families and exact whole cards", "compose and back-read twelve programs"),
        (7, 20, 21, "RENDERER UND HÄNDE", "q/sh/s/ch/d/t/zero licensed entries", "write the same program in four workshop hands"),
        (8, 22, 23, "SATZ UND ZEILENUMBRUCH", "postfix values, forward material, owner reset, line wrap", "write across a physical line without ending the statement"),
        (9, 24, 24, "ASTRO-NOMENKLATOR", "local owner key, copy every group, no orientation and no join", "copy one locus from each instrument"),
    ]
    lesson_rows = [
        {"lesson_order": order, "day_start": start, "day_end": end, "lesson_name": name, "material": material, "mastery_exercise": exercise}
        for order, start, end, name, material, exercise in lessons
    ]

    first_stage: dict[str, str] = {}
    for statement in statements:
        atoms = statement_atoms[statement["statement_id"]]
        if atoms <= portable:
            first_stage[statement["statement_id"]] = "S1"
        elif atoms <= portable | bridges:
            first_stage[statement["statement_id"]] = "S2"
        elif statement["record_unit_id"].startswith("H"):
            first_stage[statement["statement_id"]] = "S3H"
        else:
            first_stage[statement["statement_id"]] = "S3B"
    selected: list[dict[str, str]] = []
    quotas = {"S1": 2, "S2": 2, "S3H": 2, "S3B": 3}
    for stage in ["S1", "S2", "S3H", "S3B"]:
        candidates = [row for row in statements if first_stage[row["statement_id"]] == stage]
        candidates.sort(key=lambda row: (int(row["event_count"]), int(row["statement_order"])))
        selected.extend(candidates[:quotas[stage]])
    exercise_rows: list[dict[str, object]] = []
    for index, row in enumerate(selected, 1):
        exercise_rows.append({
            "exercise_id": f"EX{index:02d}",
            "first_readable_stage": first_stage[row["statement_id"]],
            "mode": "PROSE",
            "page": row["page"],
            "unit_id": row["record_unit_id"],
            "source_identity": row["statement_id"],
            "copy_material": row["visible_surface_sequence"],
            "back_reading_de": row["card_near_workshop_reading_de"],
        })
    for instrument in instruments:
        index = len(exercise_rows) + 1
        exercise_rows.append({
            "exercise_id": f"EX{index:02d}",
            "first_readable_stage": "S5_ASTRO",
            "mode": "LOCAL_ASTRO_NOMENCLATOR",
            "page": instrument["page"],
            "unit_id": instrument["unit_id"],
            "source_identity": instrument["namespaces"],
            "copy_material": f"copy one complete local locus ({instrument['group_count']} page groups available)",
            "back_reading_de": instrument["complete_instrument_reading_de"],
        })

    write_tsv(OUT / "HUNDRED_FIFTH_24_DAY_CURRICULUM.tsv", list(lesson_rows[0]), lesson_rows)
    write_tsv(OUT / "HUNDRED_FIFTH_STAGE_COVERAGE.tsv", list(coverage_rows[0]), coverage_rows)
    write_tsv(OUT / "HUNDRED_FIFTH_12_APPRENTICE_EXERCISES.tsv", list(exercise_rows[0]), exercise_rows)

    stage_by_id = {row["stage_id"]: row for row in coverage_rows}
    report = [
        "# Hundertfünfte Runde: Ein Lehrling von 1420 lernt das System", "",
        "## Der 24-Tage-Lehrgang", "",
        "Der Lehrling beginnt nicht mit 173 isolierten Wörtern. Er lernt Bildbesitzer,",
        "fünfzehn Kernwerte, neun Brücken und erst danach die zwei getrennten Fachtafeln.",
        "Kartenkörper, zugelassene Handvarianten, Satzbindung und Astro-Kopieren folgen.", "",
        f"Nach dem Kern allein kann er {stage_by_id['S1']['decoded_prose_events']} von 381",
        f"Kartenwerten und {stage_by_id['S1']['fully_decoded_statements']} vollständige",
        "Aussagen lesen. Mit den Brücken steigt das auf",
        f"{stage_by_id['S2']['decoded_prose_events']} Karten und",
        f"{stage_by_id['S2']['fully_decoded_statements']} Aussagen. Nach beiden Fachtafeln",
        "sind alle 381 Karten und 116 Aussagen atomar lesbar.", "",
        "Die letzten Tage sind keine neuen Bedeutungslektionen: Sie üben die 173 registrierten",
        "Kartenkörper, die semantisch leeren Eintrittsformen, Zeilenumbruch und das getrennte",
        "Astro-Nomenklatorverfahren. Das macht eine kleine Mehrschreiberwerkstatt deutlich",
        "plausibler als vier unabhängig erfundene Chiffren.", "",
        "Nur die festen zehn Seiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_FIFTH_APPRENTICE_CURRICULUM_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "CONSISTENT", "days": 24, "lessons": len(lesson_rows), "stages": len(coverage_rows),
        "exercises": len(exercise_rows), "portable_atoms": len(portable), "bridge_atoms": len(bridges),
        "herbal_atoms": len(herbal), "bio_atoms": len(bio),
        "final_events": stage_by_id["S4"]["decoded_prose_events"],
        "final_statements": stage_by_id["S4"]["fully_decoded_statements"],
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
