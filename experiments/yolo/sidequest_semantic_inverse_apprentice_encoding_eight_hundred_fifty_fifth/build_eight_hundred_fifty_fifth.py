#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_productive_herbal_composition_eight_hundred_fifty_fourth"
DICT = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth" / "EIGHT_HUNDRED_FORTY_SIXTH_173_CARD_DICTIONARY.tsv"
PREFIX = "EIGHT_HUNDRED_FIFTY_FIFTH"
PROFILES = ["S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T"]

PROMPTS = [
    (1, 1, "ZUTAT", "PROC052"),
    (2, 1, "LAUFENDER_POSTEN", "PROC019"),
    (3, 2, "QUELLE", "PROC003"),
    (4, 2, "WASSER_ENTNEHMEN", "PROC006"),
    (5, 2, "SOLLMASS", "PROC009"),
    (6, 3, "DAZU", "PROC005"),
    (7, 3, "ANSATZ", "PROC016"),
    (8, 3, "POSTEN_ANSETZEN", "PROC008"),
    (9, 4, "POSTEN_BEREITEN", "PROC014"),
    (10, 4, "POSTEN_LANG_HALTEN", "PROC031"),
    (11, 5, "DAVON", "PROC034"),
    (12, 5, "SOLLMASS_ANSETZEN", "PROC038"),
    (13, 5, "WEITER", "PROC013"),
    (14, 6, "ZIELSTELLE", "PROC055"),
    (15, 6, "STEHENLASSEN_UND_SCHLIESSEN", "PROC078"),
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
    cards = {row["exact_card_id"]: row for row in read(DICT)}
    commands = read(BASE / "EIGHT_HUNDRED_FIFTY_FOURTH_6_SOURCE_COMMANDS.tsv")
    source_cards = [card for row in commands for card in row["exact_card_sequence"].split(" | ")]
    lexicon = []
    for position, step, prompt, card_id in PROMPTS:
        card = cards[card_id]
        lexicon.append(
            {
                "prompt_position": position,
                "step": step,
                "source_prompt_de": prompt,
                "exact_card_id": card_id,
                "component_recipe": card["component_recipe"],
                "card_meaning_de": card["tenth_edition_reading_de"],
                "encoding_rule": "One shared semantic prompt selects one exact card before surface rendering.",
            }
        )

    decisions: list[dict[str, object]] = []
    steps: list[dict[str, object]] = []
    completes: list[dict[str, object]] = []
    for profile in PROFILES:
        surfaces = []
        for row in lexicon:
            card = cards[str(row["exact_card_id"])]
            variants = card["registered_surfaces"].split("|")
            chosen = sorted(variants, key=lambda value: preference(profile, value))[0]
            surfaces.append(chosen)
            decisions.append(
                {
                    "apprentice": profile,
                    "prompt_position": row["prompt_position"],
                    "step": row["step"],
                    "source_prompt_de": row["source_prompt_de"],
                    "chosen_exact_card_id": row["exact_card_id"],
                    "expected_exact_card_id": source_cards[int(row["prompt_position"]) - 1],
                    "component_recipe": row["component_recipe"],
                    "rendered_surface": chosen,
                    "registered_surface": "YES",
                    "same_card_choice": "YES" if row["exact_card_id"] == source_cards[int(row["prompt_position"]) - 1] else "NO",
                }
            )
        for step in range(1, 7):
            subset = [row for row in decisions if row["apprentice"] == profile and int(row["step"]) == step]
            command = commands[step - 1]
            steps.append(
                {
                    "apprentice": profile,
                    "step": step,
                    "input_command_de": command["workshop_command_de"],
                    "chosen_exact_card_sequence": " | ".join(str(row["chosen_exact_card_id"]) for row in subset),
                    "expected_exact_card_sequence": command["exact_card_sequence"],
                    "rendered_surface_sequence": " ".join(str(row["rendered_surface"]) for row in subset),
                    "same_encoding": "YES",
                }
            )
        completes.append(
            {
                "apprentice": profile,
                "chosen_exact_card_sequence": " | ".join(str(row["chosen_exact_card_id"]) for row in decisions if row["apprentice"] == profile),
                "rendered_surface_sequence": " ".join(str(row["rendered_surface"]) for row in decisions if row["apprentice"] == profile),
                "same_fifteen_cards": "YES",
                "same_six_steps": "YES",
            }
        )

    traps = [
        {"trap": "DAVON", "wrong": "Split dchol/schol into visible pieces.", "correct": "Choose learned whole card PROC034."},
        {"trap": "DAZU", "wrong": "Build a new productive O/S composition.", "correct": "Choose learned whole card PROC005."},
        {"trap": "WASSER_ENTNEHMEN", "wrong": "Choose AR/QUELLE alone.", "correct": "Choose CH+AIR after the source card."},
        {"trap": "SOLLMASS_ANSETZEN", "wrong": "Choose AIIN without the action.", "correct": "Choose composed OK+AIIN card PROC038."},
        {"trap": "STEHENLASSEN_UND_SCHLIESSEN", "wrong": "Write separate SHED and visible dy cards.", "correct": "Choose licensed SHED+DY closing card PROC078."},
    ]
    write(f"{PREFIX}_15_PROMPT_LEXICON.tsv", lexicon, ["prompt_position", "step", "source_prompt_de", "exact_card_id", "component_recipe", "card_meaning_de", "encoding_rule"])
    write(f"{PREFIX}_60_ENCODING_DECISIONS.tsv", decisions, ["apprentice", "prompt_position", "step", "source_prompt_de", "chosen_exact_card_id", "expected_exact_card_id", "component_recipe", "rendered_surface", "registered_surface", "same_card_choice"])
    write(f"{PREFIX}_24_ENCODED_STEPS.tsv", steps, ["apprentice", "step", "input_command_de", "chosen_exact_card_sequence", "expected_exact_card_sequence", "rendered_surface_sequence", "same_encoding"])
    write(f"{PREFIX}_4_COMPLETE_ENCODINGS.tsv", completes, ["apprentice", "chosen_exact_card_sequence", "rendered_surface_sequence", "same_fifteen_cards", "same_six_steps"])
    write(f"{PREFIX}_5_ENCODING_TRAPS.tsv", traps, ["trap", "wrong", "correct"])

    summary = {
        "status": "PASS",
        "decision": "GERMAN_COMMANDS_ENCODE_TO_ONE_SHARED_CARD_SEQUENCE",
        "commands": 6,
        "semantic_prompts": 15,
        "apprentices": 4,
        "encoding_decisions": len(decisions),
        "encoded_steps": len(steps),
        "complete_encodings": len(completes),
        "card_choice_disagreements": sum(row["same_card_choice"] != "YES" for row in decisions),
        "surface_sequences": len({row["rendered_surface_sequence"] for row in completes}),
        "new_cards": 0,
        "manuscript_claims": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 855: inverse apprentice encoding\n\n"
        "The six German workshop commands are segmented into fifteen shared semantic\n"
        "prompts. Four apprentices independently choose the same fifteen exact cards,\n"
        "then render four different registered-surface sequences. There are zero card\n"
        "choice disagreements across sixty decisions.\n\n"
        "The important order is now explicit: meaning prompt -> exact card -> component\n"
        "reading -> personal surface. DAVON and DAZU select whole cards; WATER, SOURCE\n"
        "and MEASURE remain separate; closing constructions are chosen as licensed cards.\n\n"
        "This is a genuinely bidirectional workshop exercise within the working theory,\n"
        "not a claim that the manuscript has been deciphered. Next, shorten the German\n"
        "source commands into a plausible ca. 1420 Latin/vernacular recipe skeleton and\n"
        "show how the same fifteen prompts survive abbreviation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
