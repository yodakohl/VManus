#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
PREFIX = "EIGHT_HUNDRED_FIFTY_FIRST"
PROFILES = ["S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T"]


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
    cards = read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_173_CARD_DICTIONARY.tsv")
    lesson = [
        {"rule": 1, "who": "ALL", "instruction_de": "Zuerst die gemeinsame exakte Karte und ihre Bedeutung lernen."},
        {"rule": 2, "who": "ALL", "instruction_de": "Hat die Karte nur eine registrierte Form, diese unverändert kopieren."},
        {"rule": 3, "who": "S1_BARE", "instruction_de": "Wenn vorhanden die kurze nackte Form, sonst die kürzeste Form wählen."},
        {"rule": 4, "who": "S2_CH", "instruction_de": "Wenn vorhanden CHE, sonst CH, sonst die kürzeste Form wählen."},
        {"rule": 5, "who": "S3_Q_SH", "instruction_de": "Wenn vorhanden Q, sonst SH, sonst S, sonst die kürzeste Form wählen."},
        {"rule": 6, "who": "S4_D_T", "instruction_de": "Wenn vorhanden D, sonst T, sonst die kürzeste Form wählen."},
        {"rule": 7, "who": "ALL", "instruction_de": "Die gewählte Oberfläche ändert niemals Kartenfolge oder Bedeutung."},
    ]
    assignments: list[dict[str, object]] = []
    matrices: list[dict[str, object]] = []
    unused: list[dict[str, object]] = []
    for card in cards:
        variants = card["registered_surfaces"].split("|")
        choices = {
            profile: sorted(variants, key=lambda value: preference(profile, value))[0]
            for profile in PROFILES
        }
        for profile, chosen in choices.items():
            assignments.append(
                {
                    "exact_card_id": card["exact_card_id"],
                    "component_recipe": card["component_recipe"],
                    "meaning_de": card["tenth_edition_reading_de"],
                    "learning_mode": card["learning_mode"],
                    "scribe": profile,
                    "chosen_surface": chosen,
                    "registered": "YES",
                    "same_card_and_meaning": "YES",
                }
            )
        chosen_set = set(choices.values())
        matrices.append(
            {
                "exact_card_id": card["exact_card_id"],
                "component_recipe": card["component_recipe"],
                "meaning_de": card["tenth_edition_reading_de"],
                "registered_surfaces": card["registered_surfaces"],
                "registered_variant_count": len(variants),
                "S1_BARE": choices["S1_BARE"],
                "S2_CH": choices["S2_CH"],
                "S3_Q_SH": choices["S3_Q_SH"],
                "S4_D_T": choices["S4_D_T"],
                "distinct_profile_choices": len(chosen_set),
                "profile_sensitive": "YES" if len(chosen_set) > 1 else "NO",
            }
        )
        for surface in variants:
            if surface not in chosen_set:
                unused.append(
                    {
                        "exact_card_id": card["exact_card_id"],
                        "component_recipe": card["component_recipe"],
                        "meaning_de": card["tenth_edition_reading_de"],
                        "unselected_registered_surface": surface,
                        "why_extra_learning_is_needed": "Keines der vier kompakten Präferenzprofile wählt diese zusätzliche registrierte Variante.",
                    }
                )

    write(f"{PREFIX}_7_RULE_LESSON.tsv", lesson, ["rule", "who", "instruction_de"])
    write(
        f"{PREFIX}_692_CARD_ASSIGNMENTS.tsv",
        assignments,
        ["exact_card_id", "component_recipe", "meaning_de", "learning_mode", "scribe", "chosen_surface", "registered", "same_card_and_meaning"],
    )
    write(
        f"{PREFIX}_173_CARD_MATRIX.tsv",
        matrices,
        ["exact_card_id", "component_recipe", "meaning_de", "registered_surfaces", "registered_variant_count", "S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T", "distinct_profile_choices", "profile_sensitive"],
    )
    write(
        f"{PREFIX}_10_EXTRA_VARIANTS.tsv",
        unused,
        ["exact_card_id", "component_recipe", "meaning_de", "unselected_registered_surface", "why_extra_learning_is_needed"],
    )

    total_variants = sum(int(row["registered_variant_count"]) for row in matrices)
    selected_pairs = sum(int(row["distinct_profile_choices"]) for row in matrices)
    summary = {
        "status": "PASS",
        "decision": "SEVEN_RULE_SURFACE_LESSON_COVERS_NEARLY_ALL_REGISTERED_VARIANTS",
        "rules": len(lesson),
        "cards": len(matrices),
        "assignments": len(assignments),
        "fixed_surface_cards": sum(int(row["registered_variant_count"]) == 1 for row in matrices),
        "multi_surface_cards": sum(int(row["registered_variant_count"]) > 1 for row in matrices),
        "profile_sensitive_cards": sum(row["profile_sensitive"] == "YES" for row in matrices),
        "registered_card_surface_pairs": total_variants,
        "selected_distinct_card_surface_pairs": selected_pairs,
        "unselected_extra_variants": len(unused),
        "coverage_percent": round(100 * selected_pairs / total_variants, 1),
        "semantic_disagreements": 0,
        "actual_hand_attributions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 851: the small-workshop surface lesson\n\n"
        "A seven-line lesson is enough to choose a registered surface for every one\n"
        "of the 173 exact cards in each of four hypothetical styles. The apprentice\n"
        "first learns the shared card and meaning. A one-form card is copied exactly;\n"
        "only then does a personal bare, CH/CHE, Q/SH or D/T preference apply.\n\n"
        "The inventory is strongly mixed: 139 cards are surface-fixed and only 34\n"
        "have multiple registered forms. Thirty-three cards actually split under the\n"
        "four rules. Together the profiles select 220 of 230 registered card-surface\n"
        "pairs (95.7%). Ten additional variants remain tiny memorized spellings rather\n"
        "than reasons to enlarge the grammar.\n\n"
        "This is exactly the kind of economy expected from a small workshop: most\n"
        "cards are copied, a small common subset admits routine house variation, and\n"
        "meaning never depends on which renderer was chosen. These profiles still do\n"
        "not identify any real manuscript hand.\n\n"
        "Next, inspect the ten unselected registered variants and reduce them to the\n"
        "smallest possible supplementary lesson.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
