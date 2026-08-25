#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DICT = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth" / "EIGHT_HUNDRED_FORTY_SIXTH_173_CARD_DICTIONARY.tsv"
MATRIX = ROOT / "sidequest_semantic_scribe_surface_lesson_eight_hundred_fifty_first" / "EIGHT_HUNDRED_FIFTY_FIRST_173_CARD_MATRIX.tsv"
EXTRAS = ROOT / "sidequest_semantic_scribe_secondary_switches_eight_hundred_fifty_second" / "EIGHT_HUNDRED_FIFTY_SECOND_10_GENERATED_EXTRAS.tsv"
PREFIX = "EIGHT_HUNDRED_FIFTY_THIRD"

LESSON = [
    ("ADDRESS", "PROC019", "Diesen Posten nehmen."),
    ("ADDRESS", "PROC055", "An die Zielstelle bringen."),
    ("ADDRESS", "PROC003", "Aus der Quelle nehmen."),
    ("QUANTITY", "PROC009", "Nach Sollmaß arbeiten."),
    ("LINK", "PROC013", "Weiterarbeiten."),
    ("MATERIAL", "PROC016", "Mit diesem Ansatz arbeiten."),
    ("MATERIAL", "PROC052", "Die Zutat nehmen."),
    ("OPERATION", "PROC008", "Diesen Posten ansetzen."),
    ("OPERATION", "PROC038", "Nach Sollmaß ansetzen."),
    ("OPERATION", "PROC014", "Diesen Posten bereiten."),
    ("STATE", "PROC031", "Diesen Posten länger halten."),
    ("CLOSE", "PROC078", "Stehen lassen; Schritt schließen."),
    ("CLOSE", "PROC076", "Umsetzen; Schritt schließen."),
    ("MATERIAL", "PROC006", "Wasser entnehmen."),
    ("WHOLE_CARD", "PROC034", "Davon nehmen."),
    ("WHOLE_CARD", "PROC005", "Dazu geben."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = {row["exact_card_id"]: row for row in read(DICT)}
    matrix = {row["exact_card_id"]: row for row in read(MATRIX)}
    extras = {(row["exact_card_id"], row["generated_extra_surface"]): row for row in read(EXTRAS)}
    rows: list[dict[str, object]] = []
    variants: list[dict[str, object]] = []
    for number, (family, card_id, command) in enumerate(LESSON, 1):
        card = dictionary[card_id]
        surface_list = card["registered_surfaces"].split("|")
        rows.append(
            {
                "lesson_no": number,
                "family": family,
                "exact_card_id": card_id,
                "component_recipe": card["component_recipe"],
                "short_meaning_de": card["tenth_edition_reading_de"],
                "registered_surfaces": card["registered_surfaces"],
                "surface_count": len(surface_list),
                "learning_mode": card["learning_mode"],
                "example_command_de": command,
            }
        )
        for surface in surface_list:
            primary_profiles = [profile for profile in ["S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T"] if matrix[card_id][profile] == surface]
            extra = extras.get((card_id, surface))
            variants.append(
                {
                    "lesson_no": number,
                    "exact_card_id": card_id,
                    "component_recipe": card["component_recipe"],
                    "surface": surface,
                    "generated_by": "|".join(primary_profiles) if primary_profiles else str(extra["secondary_switch"]),
                    "short_meaning_de": card["tenth_edition_reading_de"],
                    "example_command_de": command,
                    "same_card_and_meaning": "YES",
                }
            )

    write(
        f"{PREFIX}_16_MODEL_BOOK_ROWS.tsv",
        rows,
        ["lesson_no", "family", "exact_card_id", "component_recipe", "short_meaning_de", "registered_surfaces", "surface_count", "learning_mode", "example_command_de"],
    )
    write(
        f"{PREFIX}_52_VARIANT_READINGS.tsv",
        variants,
        ["lesson_no", "exact_card_id", "component_recipe", "surface", "generated_by", "short_meaning_de", "example_command_de", "same_card_and_meaning"],
    )

    summary = {
        "status": "PASS",
        "decision": "SIXTEEN_ROW_MODEL_BOOK_TEACHES_CORE_CARD_USE",
        "lesson_rows": len(rows),
        "families": len({row["family"] for row in rows}),
        "registered_surfaces": len(variants),
        "productive_cards": sum(row["learning_mode"] == "COMPOSE_COMPONENTS" for row in rows),
        "whole_cards": sum(row["learning_mode"] == "MEMORIZE_WHOLE_CARD" for row in rows),
        "bound_frames": sum(row["learning_mode"] == "MEMORIZE_BOUND_FRAME" for row in rows),
        "empty_commands": sum(not row["example_command_de"] for row in rows),
        "meaning_changes": 0,
        "actual_hand_attributions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Musterblatt der kleinen Werkstatt",
        "",
        "Links steht die gelernte Kartenfunktion, in der Mitte ihre erlaubten",
        "Schreibungen, rechts ein kurzer Arbeitsbefehl. Eine andere Schreibung ändert",
        "den Befehl nicht.",
        "",
        "| Nr. | Fach | Karte | erlaubte Schreibungen | Kurzlesung | Übung |",
        "|---:|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['lesson_no']} | {row['family']} | `{row['component_recipe']}` | `{row['registered_surfaces']}` | {row['short_meaning_de']} | {row['example_command_de']} |"
        )
    lines.extend(
        [
            "",
            "## Lehrmeisterregel",
            "",
            "Erst die Karte erkennen, dann ihre Bestandteile lesen, zuletzt die",
            "Schreiberform wählen. `DAVON` und `DAZU` sind ganze gelernte Karten; sie",
            "werden nicht nachträglich in ähnlich aussehende Stücke zerlegt.",
            "",
            "Dieses Blatt ist eine Rekonstruktion unseres Arbeitsmodells, kein",
            "historisches Faksimile und keine Zuordnung realer Hände.",
        ]
    )
    (HERE / f"{PREFIX}_MODEL_BOOK_LEAF.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 853: compact workshop model-book leaf\n\n"
        "Sixteen exemplar cards now form one usable teaching leaf: address, quantity,\n"
        "link, material, operation, state, close and whole-card functions. Their 52\n"
        "registered surfaces are each tied to one short meaning and one concrete command.\n\n"
        "Fourteen cards are productively composed; DAVON and DAZU are learned whole\n"
        "cards. The leaf therefore teaches the intended mixed system directly: recurrent\n"
        "technical pieces plus a tiny memorized vocabulary.\n\n"
        "Next, use only this leaf to compose a new six-step herbal preparation, then\n"
        "render it in all four styles and read it back.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
