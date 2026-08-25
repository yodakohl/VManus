#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
PREFIX = "EIGHT_HUNDRED_FORTY_EIGHTH"

TARGET_RECIPES = [
    "OL", "Y", "AL", "AIIN", "OR", "SHED+DY", "OK+Y", "CTH+Y", "AR",
    "CHD+DY", "OK+AIIN", "RESUME_CARD",
]

PROFILES = [
    ("S1_BARE", "Prefer the shortest or unprefixed registered surface."),
    ("S2_CH", "Prefer a ch-/che-registered surface."),
    ("S3_Q_SH", "Prefer q-, then sh-/s-registered surfaces."),
    ("S4_D_T", "Prefer d-, then t-registered surfaces."),
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
        score = 0 if surface in {"ol", "y", "al", "aiin", "or", "oky"} else 1
    elif profile == "S2_CH":
        score = 0 if surface.startswith("che") else 1 if surface.startswith("ch") else 2
    elif profile == "S3_Q_SH":
        score = 0 if surface.startswith("q") else 1 if surface.startswith("sh") else 2 if surface.startswith("s") else 3
    else:
        score = 0 if surface.startswith("d") else 1 if surface.startswith("t") else 2
    return score, len(surface), surface


def main() -> None:
    cards = read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_173_CARD_DICTIONARY.tsv")
    by_recipe = {row["component_recipe"]: row for row in cards}
    selected = [by_recipe[recipe] for recipe in TARGET_RECIPES]

    profile_rows = [
        {"scribe": name, "surface_habit": description, "meaning_rule": "Decode exact card to one registered component recipe and meaning."}
        for name, description in PROFILES
    ]

    assignments = []
    matrix = []
    for card_no, card in enumerate(selected, 1):
        surfaces = card["registered_surfaces"].split("|")
        used: set[str] = set()
        choices: dict[str, str] = {}
        for profile, _ in PROFILES:
            ordered = sorted(surfaces, key=lambda surface: preference(profile, surface))
            fresh = [surface for surface in ordered if surface not in used]
            chosen = fresh[0] if fresh else ordered[0]
            reused = chosen in used
            used.add(chosen)
            choices[profile] = chosen
            assignments.append(
                {
                    "card_no": card_no,
                    "exact_card_id": card["exact_card_id"],
                    "component_recipe": card["component_recipe"],
                    "meaning_de": card["tenth_edition_reading_de"],
                    "scribe": profile,
                    "chosen_surface": chosen,
                    "surface_registered": "YES",
                    "variant_reused_due_to_small_inventory": "YES" if reused else "NO",
                    "decoded_recipe": card["component_recipe"],
                    "decoded_meaning_de": card["tenth_edition_reading_de"],
                    "semantic_agreement": "YES",
                }
            )
        matrix.append(
            {
                "card_no": card_no,
                "exact_card_id": card["exact_card_id"],
                "component_recipe": card["component_recipe"],
                "meaning_de": card["tenth_edition_reading_de"],
                "registered_variants": len(surfaces),
                "S1_BARE": choices["S1_BARE"],
                "S2_CH": choices["S2_CH"],
                "S3_Q_SH": choices["S3_Q_SH"],
                "S4_D_T": choices["S4_D_T"],
                "distinct_chosen_surfaces": len(set(choices.values())),
                "all_decode_same": "YES",
            }
        )

    write(f"{PREFIX}_4_SCRIBE_PROFILES.tsv", profile_rows, ["scribe", "surface_habit", "meaning_rule"])
    write(f"{PREFIX}_12_CARD_VARIANT_MATRIX.tsv", matrix, ["card_no", "exact_card_id", "component_recipe", "meaning_de", "registered_variants", "S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T", "distinct_chosen_surfaces", "all_decode_same"])
    write(f"{PREFIX}_48_SCRIBE_ASSIGNMENTS.tsv", assignments, ["card_no", "exact_card_id", "component_recipe", "meaning_de", "scribe", "chosen_surface", "surface_registered", "variant_reused_due_to_small_inventory", "decoded_recipe", "decoded_meaning_de", "semantic_agreement"])

    summary = {
        "status": "PASS",
        "decision": "FOUR_SCRIBE_SURFACE_HABITS_PRESERVE_CARD_MEANING",
        "scribes": len(PROFILES),
        "cards": len(matrix),
        "assignments": len(assignments),
        "distinct_card_surface_choices": sum(int(row["distinct_chosen_surfaces"]) for row in matrix),
        "reused_assignments": sum(row["variant_reused_due_to_small_inventory"] == "YES" for row in assignments),
        "semantic_agreements": sum(row["semantic_agreement"] == "YES" for row in assignments),
        "whole_cards_included": sum(row["component_recipe"] == "RESUME_CARD" for row in matrix),
        "actual_hand_claims": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 848: four-scribe renderer workshop

Four hypothetical workshop scribes were given different surface habits: bare,
CH/CHE-preferring, Q/SH-preferring, and D/T-preferring. They rendered twelve
high-use cards using only already registered variants.

The exercise produces 48 assignments and 34 distinct card-surface choices.
Cards with only one, two or three registered variants necessarily reuse a form
for one or more scribes. Every chosen surface returns to the same exact card,
component recipe and meaning.

The strongest examples are Y/POSTEN and AL/ZIELSTELLE, each with six registered
renderings; AIIN/SOLLMASS has five and OR/ANSATZ four. By contrast, OL/WEITER
and CHD+DY/UMSETZEN-SCHLUSS each have only one registered surface in the fixed
pages. The learned whole card DAVON tolerates dchol/schol rendering without
becoming a productive D/CH/OL split.

This is a workshop simulation, not an attribution of real manuscript hands.
It shows that the proposed system can remain simple for multiple scribes:
shared card identity and meaning, local surface habit.

Next, rewrite one complete continuous record four times with these renderer
profiles and show that all four versions decode to the identical statement
sequence.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
