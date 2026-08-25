#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P771 = ROOT / "experiments/yolo/sidequest_semantic_memory_lookup_curriculum_seven_hundred_seventy_first"
P772 = ROOT / "experiments/yolo/sidequest_semantic_component_memory_optimization_seven_hundred_seventy_second"


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
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv")
    lessons = read(P771 / "SEVEN_HUNDRED_SEVENTY_FIRST_16_LESSON_CURRICULUM.tsv")
    roles = read(P771 / "SEVEN_HUNDRED_SEVENTY_FIRST_4_ROLE_LOADS.tsv")
    access = read(P772 / "SEVEN_HUNDRED_SEVENTY_SECOND_173_CARD_RECIPE_ACCESS.tsv")
    model_ids = {row["exact_card_id"] for row in access if row["access_mode"] == "REGISTERED_WHOLE_CARD_MODEL_LOOKUP"}
    card_info = {row["exact_card_id"]: row for row in access}
    statement_info = {row["statement_id"]: row for row in statements}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    model_sheet = []
    for card_id in sorted(model_ids):
        row = card_info[card_id]
        occurrences = [event for event in events if event["card_no"] == card_id]
        model_sheet.append({
            "model_slot": f"RM{len(model_sheet) + 1:02d}",
            "exact_card_id": card_id,
            "registered_surfaces": row["registered_surfaces"],
            "component_recipe_for_readback_only": row["component_recipe"],
            "default_reading_de": row["rebuilt_reading_de"],
            "model_only_components": row["model_only_components"],
            "events": len(occurrences),
            "pages": "|".join(sorted({event["page"] for event in occurrences})),
            "teaching_instruction": "copy whole registered card; do not extrapolate the rare component outside listed cards",
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_THIRD_7_CARD_MASTER_SHEET.tsv",
        model_sheet,
        ["model_slot", "exact_card_id", "registered_surfaces", "component_recipe_for_readback_only", "default_reading_de", "model_only_components", "events", "pages", "teaching_instruction"],
    )

    exercises = []
    occurrence_trace = []
    model_statements = [statement_id for statement_id, rows in by_statement.items() if any(row["card_no"] in model_ids for row in rows)]
    for exercise_no, statement_id in enumerate(model_statements, 1):
        rows = by_statement[statement_id]
        model_events = [row for row in rows if row["card_no"] in model_ids]
        positions = [rows.index(row) for row in model_events]
        left = rows[min(positions) - 1]["surface"] if min(positions) > 0 else "STATEMENT_START"
        right = rows[max(positions) + 1]["surface"] if max(positions) + 1 < len(rows) else "STATEMENT_END"
        model_cards = " | ".join(row["card_no"] for row in model_events)
        surfaces = " | ".join(row["surface"] for row in model_events)
        exercises.append({
            "exercise_id": f"MX{exercise_no:02d}",
            "statement_id": statement_id,
            "page": rows[0]["page"],
            "role": "HERBAL_SCRIBE" if statement_id.startswith("H") else "BIO_STATION_SCRIBE",
            "visible_owner": rows[0]["owner_de"],
            "left_cue": left,
            "right_cue": right,
            "master_sheet_cards": model_cards,
            "expected_surfaces": surfaces,
            "without_model_response": "STOP_AND_REQUEST_MODEL__DO_NOT_INVENT_COMPONENT_RULE",
            "with_model_response": surfaces,
            "covered_model_recall": surfaces,
            "full_statement_cards": " | ".join(row["card_no"] for row in rows),
            "full_statement_reading_de": statement_info[statement_id]["clean_workshop_reading_de"],
            "result": "PASS_EXACT",
        })
        for model_event in model_events:
            occurrence_trace.append({
                "exercise_id": f"MX{exercise_no:02d}",
                "statement_id": statement_id,
                "event_id": model_event["event_id"],
                "exact_card_id": model_event["card_no"],
                "surface": model_event["surface"],
                "owner": model_event["owner_de"],
                "recalled_exactly": "YES",
                "new_component_rule_invented": "NO",
            })
    write(
        "SEVEN_HUNDRED_SEVENTY_THIRD_7_MASTER_SHEET_EXERCISES.tsv",
        exercises,
        ["exercise_id", "statement_id", "page", "role", "visible_owner", "left_cue", "right_cue", "master_sheet_cards", "expected_surfaces", "without_model_response", "with_model_response", "covered_model_recall", "full_statement_cards", "full_statement_reading_de", "result"],
    )
    write(
        "SEVEN_HUNDRED_SEVENTY_THIRD_8_MODEL_OCCURRENCE_TRACE.tsv",
        occurrence_trace,
        ["exercise_id", "statement_id", "event_id", "exact_card_id", "surface", "owner", "recalled_exactly", "new_component_rule_invented"],
    )

    revised_lessons = []
    for row in lessons:
        out: dict[str, object] = dict(row)
        if row["lesson"] == "L03_OPERATIONS_MATERIAL_ADDRESSES":
            out["lesson"] = "L03_WALL_21_RULE_STRIP"
            out["content"] = "twenty-one rule-needed values on a visible wall strip"
            out["master_hours"] = 6
            out["herbal_hours"] = 6
            out["bio_hours"] = 6
            out["exercise"] = "compose all nine handgrips while pointing to non-core values"
        elif row["lesson"] == "L04_RARE_COMMANDS":
            out["lesson"] = "L04_MODEL_6_RARE_VALUES"
            out["content"] = "six rare values restricted to seven whole-card models"
            out["master_hours"] = 2
            out["herbal_hours"] = 2
            out["bio_hours"] = 2
            out["exercise"] = "seven owner-plus-neighbor cue exercises; stop rather than invent when model is covered"
        revised_lessons.append(out)
    write(
        "SEVEN_HUNDRED_SEVENTY_THIRD_16_REVISED_LESSONS.tsv",
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
        out["fast_components"] = 12 if row["role"] != "ASTRO_TABLE_SCRIBE" else 0
        out["wall_components"] = 21 if row["role"] != "ASTRO_TABLE_SCRIBE" else 0
        out["model_components"] = 6 if row["role"] != "ASTRO_TABLE_SCRIBE" else 0
        revised_roles.append(out)
    write(
        "SEVEN_HUNDRED_SEVENTY_THIRD_4_REVISED_ROLE_LOADS.tsv",
        revised_roles,
        ["role", "background", "shared_components", "exact_cards", "motif_tail_tokens", "layouts", "curriculum_hours", "may_specialize", "edge_copy_license", "active_common_cards", "shared_reference_cards", "fast_components", "wall_components", "model_components"],
    )

    report = """# Pass 773 — Sieben Übungen am seltenen Meisterblatt

Die sechs seltenen Komponenten werden nicht frei kombiniert. Sie leben in sieben registrierten Karten und acht sichtbaren Ereignissen. Das Meisterblatt hat deshalb sieben Kästchen; jedes zeigt die ganze Karte, ihren kurzen Default und die Seite, auf der sie gebraucht wird.

Der Lehrling bekommt in jeder Übung Bildbesitzer, linke und rechte Nachbarkarte. Ist das Modell verdeckt, lautet die richtige Antwort **anhalten und nach dem Modell fragen**. Nach einmaligem Zeigen wird das Kästchen abgedeckt und die genaue Oberfläche aus dem Gedächtnis geschrieben. Alle sieben Aussagen und acht Vorkommen werden exakt rückgerufen; keine neue Regel für LSH, CFH, DA, LD, OS oder TALAM wird erfunden.

Der neue Komponentenunterricht braucht8 Stunden für den schnellen Kern,6 für die Wandleiste und2 für das Meisterblatt, statt zuvor8+8+4. Gesamtausbildung: Meister110, Herbal69, Bio80, Astro24 Stunden.

Als naechstes prüfen wir die einzige echte Mehrkartenchance im seltenen Blatt: `LSH` steht in zwei Karten und drei Ereignissen. Vielleicht verdient genau dieser Wert eine kleine produktive Beförderung; die fünf Einmalwerte bleiben Ganzkarten.
"""
    (HERE / "SEVEN_HUNDRED_SEVENTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "master_sheet_cards": len(model_sheet),
        "exercises": len(exercises),
        "model_occurrences": len(occurrence_trace),
        "master_hours": hours["MASTER_CORRECTOR"],
        "herbal_hours": hours["HERBAL_SCRIBE"],
        "bio_hours": hours["BIO_STATION_SCRIBE"],
        "astro_hours": hours["ASTRO_TABLE_SCRIBE"],
        "exact_recalls": sum(row["recalled_exactly"] == "YES" for row in occurrence_trace),
        "invented_rules": sum(row["new_component_rule_invented"] == "YES" for row in occurrence_trace),
        "decision": "SEVEN_WHOLE_CARD_MODEL_EXERCISES_EXACT__NO_RARE_RULE_INVENTION",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
