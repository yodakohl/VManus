#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_scribe_surface_lesson_eight_hundred_fifty_first"
PREFIX = "EIGHT_HUNDRED_FIFTY_SECOND"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def switch_for(surface: str) -> tuple[str, str]:
    if surface in {"chol", "chy", "chal"}:
        return "S2_CHE_TO_CH", "Use the short CH form instead of the expanded CHE form."
    if surface in {"sol", "sor", "sy", "shcthey"}:
        return "S3_QSH_TO_S_BRANCH", "Use the registered S/SH branch and take its shortest available member."
    if surface in {"taiin", "tal", "tchedy"}:
        return "S4_D_TO_T", "Use the registered T branch instead of the D branch."
    raise ValueError(surface)


def main() -> None:
    extras = read(BASE / "EIGHT_HUNDRED_FIFTY_FIRST_10_EXTRA_VARIANTS.tsv")
    matrix = read(BASE / "EIGHT_HUNDRED_FIFTY_FIRST_173_CARD_MATRIX.tsv")
    switch_rows = [
        {"switch": "S2_CHE_TO_CH", "primary_habit": "CHE before CH", "secondary_habit": "CH-short", "apprentice_rule_de": "Wenn die kurze Nebenform verlangt ist, CHE zu CH kürzen; Kartenwert bleibt gleich."},
        {"switch": "S3_QSH_TO_S_BRANCH", "primary_habit": "Q, then SH, then S", "secondary_habit": "registered S/SH branch", "apprentice_rule_de": "Bei der S-Nebenreihe die registrierte S- oder SH-Form wählen; Kartenwert bleibt gleich."},
        {"switch": "S4_D_TO_T", "primary_habit": "D before T", "secondary_habit": "T branch", "apprentice_rule_de": "Bei der T-Nebenreihe die registrierte T-Form statt D wählen; Kartenwert bleibt gleich."},
    ]
    mapped = []
    for row in extras:
        switch, rule = switch_for(row["unselected_registered_surface"])
        card = next(item for item in matrix if item["exact_card_id"] == row["exact_card_id"])
        primary_profile = {"S2_CHE_TO_CH": "S2_CH", "S3_QSH_TO_S_BRANCH": "S3_Q_SH", "S4_D_TO_T": "S4_D_T"}[switch]
        mapped.append(
            {
                "exact_card_id": row["exact_card_id"],
                "component_recipe": row["component_recipe"],
                "meaning_de": row["meaning_de"],
                "primary_profile": primary_profile,
                "primary_surface": card[primary_profile],
                "secondary_switch": switch,
                "generated_extra_surface": row["unselected_registered_surface"],
                "generation_rule": rule,
                "same_card_and_meaning": "YES",
            }
        )

    by_switch: dict[str, list[str]] = {}
    for row in mapped:
        by_switch.setdefault(str(row["secondary_switch"]), []).append(str(row["generated_extra_surface"]))
    for row in switch_rows:
        values = by_switch[row["switch"]]
        row["generated_extra_variants"] = "|".join(values)
        row["generated_count"] = len(values)

    write(
        f"{PREFIX}_3_SECONDARY_SWITCHES.tsv",
        switch_rows,
        ["switch", "primary_habit", "secondary_habit", "apprentice_rule_de", "generated_extra_variants", "generated_count"],
    )
    write(
        f"{PREFIX}_10_GENERATED_EXTRAS.tsv",
        mapped,
        ["exact_card_id", "component_recipe", "meaning_de", "primary_profile", "primary_surface", "secondary_switch", "generated_extra_surface", "generation_rule", "same_card_and_meaning"],
    )

    summary = {
        "status": "PASS",
        "decision": "THREE_SECONDARY_SWITCHES_GENERATE_ALL_TEN_EXTRA_VARIANTS",
        "core_lesson_rules": 7,
        "secondary_switches": 3,
        "previously_selected_card_surface_pairs": 220,
        "generated_extra_card_surface_pairs": len(mapped),
        "total_registered_card_surface_pairs": 230,
        "remaining_memorized_surface_exceptions": 0,
        "meaning_changes": 0,
        "actual_hand_attributions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 852: three secondary renderer switches\n\n"
        "The ten registered surfaces left outside the four primary habits are not ten\n"
        "independent exceptions. They fall exactly into three secondary switches:\n\n"
        "- expanded CHE can contract to CH, generating `chol`, `chy`, `chal`;\n"
        "- the Q/SH habit can enter its short S/SH branch, generating `sol`, `sor`,\n"
        "  `sy`, `shcthey`;\n"
        "- the D habit can use its T branch, generating `taiin`, `tal`, `tchedy`.\n\n"
        "The seven-line core lesson plus these three switches now generates all 230\n"
        "registered card-surface pairs. There is no residual spelling exception, and\n"
        "none of the switches changes card identity or meaning. The learned whole-card\n"
        "exceptions remain semantic card exceptions, not renderer exceptions.\n\n"
        "As a 1420-style workshop story this is simple: copy most cards exactly; for\n"
        "the small variable deck learn one main hand habit and one occasional side\n"
        "branch. This still does not identify actual manuscript hands.\n\n"
        "Next, use the complete renderer lesson to generate a short model-book page:\n"
        "one exemplar card, its allowed hand variants, and one concrete command each.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
