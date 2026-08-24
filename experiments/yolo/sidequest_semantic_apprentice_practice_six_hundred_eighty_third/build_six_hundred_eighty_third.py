#!/usr/bin/env python3
"""Build one compact practice page for twelve recurrent recipe families."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P682 = ROOT / "experiments/yolo/sidequest_semantic_multi_scribe_production_six_hundred_eighty_second"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


MISTAKES = {
    "AIIN": ("AIN statt AIIN waehlen", "MASS ist der Sollwert; PORTION ist die abgegrenzte Gabe."),
    "OL": ("OT lesen und einen neuen Gang beginnen", "OL behaelt denselben Gang; OT bedeutet DANACH."),
    "Y": ("sichtbares dy als Schluss lesen", "Diese exakte Y-Karte meint DIES; nur die lizenzierte Endkarte schliesst."),
    "OK+Y": ("q oder ch als eigene Handlung deuten", "Das Rezept bleibt ANSETZEN+DIES; die Eintrittsform wird kopiert."),
    "CHD+Y": ("mit CHD+DY verwechseln", "Y haelt den Posten aktiv; DY-Endkarte schliesst."),
    "SHED+DY": ("nach dem Absetzen offen weiterlesen", "Diese gelernte Karte enthaelt den Schluss."),
    "AL": ("AR als Quelle einsetzen", "AL zeigt zum ZIEL; AR kommt aus der QUELLE."),
    "OK+AIIN": ("eine Portion statt eines Sollwerts ansetzen", "AIIN bleibt MASS auch unter OK."),
    "OK+AIN": ("AIIN waehlen", "AIN ist PORTION; die Karte setzt eine abgegrenzte Gabe an."),
    "OK+EE+Y": ("den langen Grad als Abschluss lesen", "EE bedeutet LANG; Y laesst den Posten aktiv."),
    "AR": ("das Ziel statt des Ausgangs nennen", "AR ist QUELLE und beantwortet woher."),
    "OR": ("AR oder AIR einsetzen", "OR ist der ANSATZ; AR ist Quelle und AIR der Lauf."),
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    lessons = read(P682 / "SIX_HUNDRED_EIGHTY_SECOND_12_TEACHING_FAMILIES.tsv")
    traces = read(P682 / "SIX_HUNDRED_EIGHTY_SECOND_268_MULTI_SCRIBE_TRACES.tsv")
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for trace in traces:
        by_recipe[trace["dictated_recipe"]].append(trace)

    practice_rows = []
    drill_rows = []
    for lesson in lessons:
        recipe = lesson["dictated_recipe"]
        examples = by_recipe[recipe]
        example_a = examples[0]
        example_b = next((row for row in examples[1:] if row["copied_surface"] != example_a["copied_surface"] or row["page"] != example_a["page"]), examples[1])
        mistake, correction = MISTAKES[recipe]
        practice_rows.append({
            "lesson_no": lesson["lesson_no"],
            "master_dictation_de": lesson["spoken_value_de"],
            "component_recipe": recipe,
            "exact_card_choices": lesson["exact_cards"],
            "allowed_surfaces": lesson["surfaces"],
            "example_a": f"{example_a['event_id']}:{example_a['page']}:{example_a['statement_position']}:{example_a['copied_surface']}",
            "example_b": f"{example_b['event_id']}:{example_b['page']}:{example_b['statement_position']}:{example_b['copied_surface']}",
            "copying_instruction_de": "Rezeptadresse finden; Karte und Oberflaeche aus dem lokalen Exemplar waehlen.",
            "common_mistake_de": mistake,
            "master_correction_de": correction,
        })
        stages = [
            ("HEAR", lesson["spoken_value_de"], recipe),
            ("LOOK_UP", recipe, lesson["exact_cards"]),
            ("COPY", lesson["exact_cards"], lesson["surfaces"]),
            ("READ_BACK", lesson["surfaces"], lesson["spoken_value_de"]),
        ]
        for stage_no, (stage, prompt, expected) in enumerate(stages, start=1):
            drill_rows.append({
                "lesson_no": lesson["lesson_no"],
                "stage_no": stage_no,
                "stage": stage,
                "prompt": prompt,
                "expected": expected,
                "do_not_do": mistake if stage in {"LOOK_UP", "COPY"} else "keine Zusatzbedeutung erfinden",
            })

    manual_rows = [
        {"step": 1, "master": "Bildbesitzer zeigen und einen kurzen Wert diktieren.", "apprentice": "Besitzer merken und Komponenten aufsagen."},
        {"step": 2, "master": "Rezeptfolge bestaetigen.", "apprentice": "Ersten Komponentenreiter oeffnen."},
        {"step": 3, "master": "Nur bei Doppelzeile die lokale Variante anzeigen.", "apprentice": "Exakte Karte waehlen."},
        {"step": 4, "master": "Eintrittsposition oder Recordexemplar nennen.", "apprentice": "Sichtbare Form kopieren."},
        {"step": 5, "master": "Atomare Ruecklesung verlangen.", "apprentice": "Karte ohne Bildnomen ruecklesen."},
        {"step": 6, "master": "Auf den Besitzer zeigen.", "apprentice": "Kurzen Wert als konkrete Werkstattanweisung aussprechen."},
    ]

    write("SIX_HUNDRED_EIGHTY_THIRD_12_FAMILY_PRACTICE_PAGE.tsv", practice_rows)
    write("SIX_HUNDRED_EIGHTY_THIRD_48_FOUR_STAGE_DRILLS.tsv", drill_rows)
    write("SIX_HUNDRED_EIGHTY_THIRD_6_MASTER_APPRENTICE_STEPS.tsv", manual_rows)

    summary = {
        "status": "PASS",
        "practice_families": len(practice_rows),
        "actual_events_covered": sum(int(lesson["events"]) for lesson in lessons),
        "four_stage_drills": len(drill_rows),
        "master_apprentice_steps": len(manual_rows),
        "actual_example_events": len({part.split(":", 1)[0] for row in practice_rows for part in [row["example_a"], row["example_b"]]}),
    }
    (HERE / "SIX_HUNDRED_EIGHTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
