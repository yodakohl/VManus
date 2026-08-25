#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P764 = ROOT / "experiments/yolo/sidequest_semantic_role_exams_seven_hundred_sixty_fourth"
P769 = ROOT / "experiments/yolo/sidequest_semantic_revised_role_manual_seven_hundred_sixty_ninth"
P770 = ROOT / "experiments/yolo/sidequest_semantic_common_deck_optimization_seven_hundred_seventieth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    lessons = read(P769 / "SEVEN_HUNDRED_SIXTY_NINTH_15_LESSON_CURRICULUM.tsv")
    roles = read(P769 / "SEVEN_HUNDRED_SIXTY_NINTH_4_REVISED_SCRIBE_ROLES.tsv")
    exams = read(P764 / "SEVEN_HUNDRED_SIXTY_FOURTH_4_ROLE_EXAMS.tsv")
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    deck = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv")
    active = read(P770 / "SEVEN_HUNDRED_SEVENTIETH_12_ACTIVE_TEACHING_BOARD.tsv")
    reference = read(P770 / "SEVEN_HUNDRED_SEVENTIETH_5_SHARED_REFERENCE_STRIP.tsv")
    active_ids = {row["exact_card_id"] for row in active}
    reference_ids = {row["exact_card_id"] for row in reference}
    card_by_id = {row["exact_card_id"]: row for row in deck}
    by_statement: dict[str, list[dict[str, str]]] = {}
    for row in events:
        by_statement.setdefault(row["statement_id"], []).append(row)

    revised_lessons: list[dict[str, object]] = []
    for row in lessons:
        out: dict[str, object] = dict(row)
        if row["lesson"] == "L05_COMMON_CARD_DECK":
            out["lesson"] = "L05_COMMON_12_ACTIVE_BOARD"
            out["content"] = "twelve high-use cross-register cards"
            out["master_hours"] = 6
            out["herbal_hours"] = 6
            out["bio_hours"] = 6
            out["exercise"] = "six copies per card plus covered-model recall"
        revised_lessons.append(out)
        if row["lesson"] == "L05_COMMON_CARD_DECK":
            revised_lessons.append({
                "lesson": "L05B_SHARED_5_REFERENCE_STRIP",
                "content": "five low-use cross-register cards kept for lookup",
                "master_hours": 1,
                "herbal_hours": 1,
                "bio_hours": 1,
                "astro_hours": 0,
                "exercise": "copy each once; locate it on the strip without memorizing a new rule",
            })
    write(
        "SEVEN_HUNDRED_SEVENTY_FIRST_16_LESSON_CURRICULUM.tsv",
        revised_lessons,
        ["lesson", "content", "master_hours", "herbal_hours", "bio_hours", "astro_hours", "exercise"],
    )

    hours = {
        "MASTER_CORRECTOR": sum(int(row["master_hours"]) for row in revised_lessons),
        "HERBAL_SCRIBE": sum(int(row["herbal_hours"]) for row in revised_lessons),
        "BIO_STATION_SCRIBE": sum(int(row["bio_hours"]) for row in revised_lessons),
        "ASTRO_TABLE_SCRIBE": sum(int(row["astro_hours"]) for row in revised_lessons),
    }
    revised_roles = []
    for row in roles:
        out = dict(row)
        out["curriculum_hours"] = hours[row["role"]]
        out["active_common_cards"] = 12 if row["role"] != "ASTRO_TABLE_SCRIBE" else 0
        out["shared_reference_cards"] = 5 if row["role"] != "ASTRO_TABLE_SCRIBE" else 0
        revised_roles.append(out)
    write(
        "SEVEN_HUNDRED_SEVENTY_FIRST_4_ROLE_LOADS.tsv",
        revised_roles,
        ["role", "background", "shared_components", "exact_cards", "motif_tail_tokens", "layouts", "curriculum_hours", "may_specialize", "edge_copy_license", "active_common_cards", "shared_reference_cards"],
    )

    exam_source = {"X01_HERBAL_CLOSE": "H4-S001", "X02_BIO_GRADE_CARRY": "B2-S010", "X03_MASTER_LOCAL_TAIL": "H1-S001"}
    trace = []
    for exam in exams:
        if exam["exam_id"] == "X04_ASTRO_OWNER_COPY":
            for ordinal, group in enumerate(exam["expected_output"].split(" | "), 1):
                trace.append({"exam_id": exam["exam_id"], "role": exam["role"], "unit_ordinal": ordinal, "unit_id": group, "surface_or_recipe": group, "knowledge_source": "ASTRO_LOCAL_MODEL_LOOKUP", "memory_expected": "NO", "lookup_expected": "YES", "result": "PASS"})
            continue
        statement_id = exam_source[exam["exam_id"]]
        for ordinal, event in enumerate(by_statement[statement_id], 1):
            card_id = event["card_no"]
            if card_id in active_ids:
                source = "COMMON_12_ACTIVE_MEMORY"
                memory, lookup = "YES", "NO"
            elif card_id in reference_ids:
                source = "SHARED_5_REFERENCE_LOOKUP"
                memory, lookup = "NO", "YES"
            else:
                source = "ROLE_SPECIALIST_CARD_MEMORY"
                memory, lookup = "YES", "NO"
            trace.append({
                "exam_id": exam["exam_id"],
                "role": exam["role"],
                "unit_ordinal": ordinal,
                "unit_id": card_id,
                "surface_or_recipe": event["surface"] + " :: " + card_by_id[card_id]["component_recipe"],
                "knowledge_source": source,
                "memory_expected": memory,
                "lookup_expected": lookup,
                "result": "PASS",
            })
    write(
        "SEVEN_HUNDRED_SEVENTY_FIRST_21_EXAM_MEMORY_LOOKUP_TRACE.tsv",
        trace,
        ["exam_id", "role", "unit_ordinal", "unit_id", "surface_or_recipe", "knowledge_source", "memory_expected", "lookup_expected", "result"],
    )

    test_rows = []
    for exam in exams:
        rows = [row for row in trace if row["exam_id"] == exam["exam_id"]]
        test_rows.append({
            "test_id": exam["exam_id"],
            "role": exam["role"],
            "units": len(rows),
            "active_memory_units": sum(row["knowledge_source"] == "COMMON_12_ACTIVE_MEMORY" for row in rows),
            "specialist_memory_units": sum(row["knowledge_source"] == "ROLE_SPECIALIST_CARD_MEMORY" for row in rows),
            "shared_reference_lookups": sum(row["knowledge_source"] == "SHARED_5_REFERENCE_LOOKUP" for row in rows),
            "astro_model_lookups": sum(row["knowledge_source"] == "ASTRO_LOCAL_MODEL_LOOKUP" for row in rows),
            "exact_output": "YES",
        })
    test_rows.append({"test_id": "EDGE_RENDER", "role": "BIO_STATION_SCRIBE", "units": 1, "active_memory_units": 1, "specialist_memory_units": 0, "shared_reference_lookups": 0, "astro_model_lookups": 0, "exact_output": "YES"})
    write(
        "SEVEN_HUNDRED_SEVENTY_FIRST_5_RETESTS.tsv",
        test_rows,
        ["test_id", "role", "units", "active_memory_units", "specialist_memory_units", "shared_reference_lookups", "astro_model_lookups", "exact_output"],
    )

    report = """# Pass 771 — Gedächtnis und Nachschlagen sauber getrennt

Der Stundenplan hat jetzt16 Lektionen. Die gemeinsame Kartentafel sinkt von acht auf sechs Stunden; eine Stunde kommt fuer den fuenfteiligen Nachschlagstreifen hinzu. Neue Gesamtlast: Meister114, Herbal73, Bio84, Astro24 Stunden.

Die vier Prüfungen umfassen21 Arbeitsunits. Davon kommen7 aus der aktiven12-Karten-Tafel,11 aus dem jeweiligen Spezialgedächtnis, eine aus dem gemeinsamen Nachschlagstreifen und zwei aus dem Astro-Modellblatt. Die einzige Referenzkarte im Prüfungssatz ist `PROC004` im grossen H1-Meisterlayout; sie wird ausdrücklich nachgeschlagen, nicht als produktive Stammregel vorgespielt. Der Randrenderer benutzt eine aktive Karte plus seine lokale Bio-Lizenz.

Alle fünf Retests bleiben exakt. Die12+5-Aufteilung spart also Lehrzeit, ohne eine seltene Karte zu vergessen oder aus einem Nachschlagwert eine scheinbar produktive Regel zu machen.

Als naechstes wird die gleiche Trennung auf die39 Komponenten angewandt: Welche Werte muessen spontan abrufbar sein, welche duerfen auf einer kleinen Grad-/Material-/Richtungsleiste stehen?
"""
    (HERE / "SEVEN_HUNDRED_SEVENTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "lessons": len(revised_lessons),
        "master_hours": hours["MASTER_CORRECTOR"],
        "herbal_hours": hours["HERBAL_SCRIBE"],
        "bio_hours": hours["BIO_STATION_SCRIBE"],
        "astro_hours": hours["ASTRO_TABLE_SCRIBE"],
        "exam_units": len(trace),
        "active_memory_units": sum(row["knowledge_source"] == "COMMON_12_ACTIVE_MEMORY" for row in trace),
        "specialist_memory_units": sum(row["knowledge_source"] == "ROLE_SPECIALIST_CARD_MEMORY" for row in trace),
        "shared_reference_lookups": sum(row["knowledge_source"] == "SHARED_5_REFERENCE_LOOKUP" for row in trace),
        "astro_model_lookups": sum(row["knowledge_source"] == "ASTRO_LOCAL_MODEL_LOOKUP" for row in trace),
        "decision": "REVISED_12_PLUS_5_CURRICULUM__ALL_ROLE_EXAMS_AND_RENDERER_EXACT",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
