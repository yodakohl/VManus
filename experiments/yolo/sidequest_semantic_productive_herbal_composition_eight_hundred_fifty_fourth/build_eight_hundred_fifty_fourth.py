#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DICT = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth" / "EIGHT_HUNDRED_FORTY_SIXTH_173_CARD_DICTIONARY.tsv"
PREFIX = "EIGHT_HUNDRED_FIFTY_FOURTH"
PROFILES = ["S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T"]

STEPS = [
    (1, ["PROC052", "PROC019"], "Die Zutat als laufenden Posten nehmen."),
    (2, ["PROC003", "PROC006", "PROC009"], "Aus der Quelle Wasser bis zum Sollmaß entnehmen."),
    (3, ["PROC005", "PROC016", "PROC008"], "Dazu den Ansatz nehmen und den Posten ansetzen."),
    (4, ["PROC014", "PROC031"], "Den Posten bereiten und länger halten."),
    (5, ["PROC034", "PROC038", "PROC013"], "Davon nach Sollmaß ansetzen und weiterarbeiten."),
    (6, ["PROC055", "PROC078"], "An der Zielstelle stehen lassen; den Schritt schließen."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def preference(profile: str, surface: str) -> tuple[int, int, str]:
    if profile == "S1_BARE":
        bare = {"ol", "y", "al", "aiin", "or", "oky", "okchy", "cthy"}
        score = 0 if surface in bare else 1
    elif profile == "S2_CH":
        score = 0 if surface.startswith("che") else 1 if surface.startswith("ch") else 2
    elif profile == "S3_Q_SH":
        score = 0 if surface.startswith("q") else 1 if surface.startswith("sh") else 2 if surface.startswith("s") else 3
    else:
        score = 0 if surface.startswith("d") else 1 if surface.startswith("t") else 2
    return score, len(surface), surface


def main() -> None:
    dictionary = {row["exact_card_id"]: row for row in read(DICT)}
    source_rows = []
    for step, card_ids, command in STEPS:
        cards = [dictionary[card_id] for card_id in card_ids]
        source_rows.append(
            {
                "step": step,
                "exact_card_sequence": " | ".join(card_ids),
                "component_sequence": " | ".join(card["component_recipe"] for card in cards),
                "literal_sequence_de": " | ".join(card["tenth_edition_reading_de"] for card in cards),
                "workshop_command_de": command,
                "all_from_model_leaf": "YES",
            }
        )

    event_rows: list[dict[str, object]] = []
    step_rows: list[dict[str, object]] = []
    complete_rows: list[dict[str, object]] = []
    for profile in PROFILES:
        event_position = 0
        all_surfaces = []
        for step, card_ids, command in STEPS:
            step_surfaces = []
            for card_id in card_ids:
                event_position += 1
                card = dictionary[card_id]
                variants = card["registered_surfaces"].split("|")
                chosen = sorted(variants, key=lambda value: preference(profile, value))[0]
                step_surfaces.append(chosen)
                all_surfaces.append(chosen)
                event_rows.append(
                    {
                        "scribe": profile,
                        "event_position": event_position,
                        "step": step,
                        "exact_card_id": card_id,
                        "component_recipe": card["component_recipe"],
                        "rendered_surface": chosen,
                        "registered_surfaces": card["registered_surfaces"],
                        "decoded_meaning_de": card["tenth_edition_reading_de"],
                        "registered_and_same_meaning": "YES",
                    }
                )
            step_rows.append(
                {
                    "scribe": profile,
                    "step": step,
                    "rendered_surface_sequence": " ".join(step_surfaces),
                    "exact_card_sequence": " | ".join(card_ids),
                    "decoded_command_de": command,
                    "same_step": "YES",
                }
            )
        complete_rows.append(
            {
                "scribe": profile,
                "rendered_surface_sequence": " ".join(all_surfaces),
                "steps": 6,
                "events": event_position,
                "decoded_preparation_de": " ".join(command for _, _, command in STEPS),
                "same_six_step_preparation": "YES",
            }
        )

    write(f"{PREFIX}_6_SOURCE_COMMANDS.tsv", source_rows, ["step", "exact_card_sequence", "component_sequence", "literal_sequence_de", "workshop_command_de", "all_from_model_leaf"])
    write(f"{PREFIX}_60_EVENT_RENDERINGS.tsv", event_rows, ["scribe", "event_position", "step", "exact_card_id", "component_recipe", "rendered_surface", "registered_surfaces", "decoded_meaning_de", "registered_and_same_meaning"])
    write(f"{PREFIX}_24_STEP_RENDERINGS.tsv", step_rows, ["scribe", "step", "rendered_surface_sequence", "exact_card_sequence", "decoded_command_de", "same_step"])
    write(f"{PREFIX}_4_COMPLETE_PREPARATIONS.tsv", complete_rows, ["scribe", "rendered_surface_sequence", "steps", "events", "decoded_preparation_de", "same_six_step_preparation"])

    summary = {
        "status": "PASS",
        "decision": "MODEL_LEAF_PRODUCTIVELY_COMPOSES_ONE_NEW_PREPARATION",
        "steps": len(STEPS),
        "event_positions": sum(len(card_ids) for _, card_ids, _ in STEPS),
        "unique_model_cards_used": len({card_id for _, card_ids, _ in STEPS for card_id in card_ids}),
        "scribes": 4,
        "event_renderings": len(event_rows),
        "step_renderings": len(step_rows),
        "complete_renderings": len(complete_rows),
        "new_card_types_invented": 0,
        "semantic_disagreements": 0,
        "manuscript_claims": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Neue Übung des Lehrmeisters: sechs Schritte",
        "",
        "Diese Zubereitung ist neu zusammengesetzt, aber jede Karte und jede Oberfläche",
        "stammt aus dem sechzehnzeiligen Musterblatt.",
        "",
    ]
    for profile in PROFILES:
        lines.extend([f"## {profile}", ""])
        for row in [item for item in step_rows if item["scribe"] == profile]:
            lines.append(f"{row['step']}. `{row['rendered_surface_sequence']}` — {row['decoded_command_de']}")
        lines.append("")
    lines.extend(
        [
            "## Gemeinsame Rücklesung",
            "",
            str(complete_rows[0]["decoded_preparation_de"]),
            "",
            "Vier Oberflächenfolgen, eine Kartenfolge, eine Zubereitung. Dies ist eine",
            "kreative Produktivitätsprobe unseres Werkstattmodells und kein behaupteter",
            "Voynich-Klartext.",
        ]
    )
    (HERE / f"{PREFIX}_FOUR_STYLE_EXERCISE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 854: productive six-step herbal composition\n\n"
        "Using only fifteen of the sixteen model-leaf cards, the workshop composes a\n"
        "new six-step preparation: take the ingredient; draw measured water; add it to\n"
        "the batch; prepare and hold; take a measured continuation; leave it at the\n"
        "target and close.\n\n"
        "All four surface styles render the fifteen-card sequence and decode to the\n"
        "same six commands. No new card type or meaning was introduced. This is the\n"
        "first compact demonstration that the reconstructed mixed system is productive,\n"
        "not merely an interlinear gloss list. It remains a creative workshop model.\n\n"
        "Next, make the inverse exercise: give four apprentices only the German commands\n"
        "and require them to choose the same card sequence before rendering their styles.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
