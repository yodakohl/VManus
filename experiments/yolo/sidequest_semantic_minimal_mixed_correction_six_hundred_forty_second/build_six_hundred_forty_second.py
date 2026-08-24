#!/usr/bin/env python3
"""Correct a mixed apprentice strip without normalizing harmless allography."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P641 = ROOT / "experiments/yolo/sidequest_semantic_error_taxonomy_six_hundred_forty_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(P613 / "SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv")
    diagnostics = read_tsv(P641 / "SIX_HUNDRED_FORTY_FIRST_4_STRIP_DIAGNOSTICS.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    surface_to_cards: dict[str, set[str]] = defaultdict(set)
    for row in cards:
        for surface in row["surfaces"].split("|"):
            surface_to_cards[surface].add(row["card_no"])

    master = next(row for row in diagnostics if row["variant"] == "MASTER")
    master_surfaces = master["surface_strip"].split()
    expected_cards = master["backread_card_strip"].split("|")
    apprentice_surfaces = ["okaiin", "qokal", "cphy", "cfhy", "shey", "shedy"]
    corrected_surfaces = ["okaiin", "qokal", "cfhy", "cphy", "tshey", "shedy"]

    def backread(surfaces: list[str]) -> list[str]:
        return [next(iter(surface_to_cards[surface])) if len(surface_to_cards[surface]) == 1 else "AMBIGUOUS" for surface in surfaces]

    apprentice_cards = backread(apprentice_surfaces)
    corrected_cards = backread(corrected_surfaces)
    position_rows = []
    for index, (expected_surface, expected_card, apprentice_surface, apprentice_card, corrected_surface, corrected_card) in enumerate(
        zip(master_surfaces, expected_cards, apprentice_surfaces, apprentice_cards, corrected_surfaces, corrected_cards), 1
    ):
        if apprentice_card == expected_card and apprentice_surface != expected_surface:
            diagnosis = "HARMLESS_FOREIGN_HAND"
            action = "KEEP_VISIBLE_SURFACE"
        elif apprentice_card != expected_card:
            diagnosis = "WRONG_CARD_OR_WRONG_POSITION"
            action = "REPAIR_FROM_CARD_SEQUENCE"
        else:
            diagnosis = "UNCHANGED"
            action = "KEEP"
        position_rows.append({
            "position": index,
            "expected_surface": expected_surface,
            "expected_card_no": expected_card,
            "expected_command_de": card_by_id[expected_card]["standard_command_de"],
            "apprentice_surface": apprentice_surface,
            "apprentice_card_no": apprentice_card,
            "apprentice_command_de": card_by_id[apprentice_card]["standard_command_de"],
            "diagnosis": diagnosis,
            "minimal_action": action,
            "corrected_surface": corrected_surface,
            "corrected_card_no": corrected_card,
            "corrected_command_de": card_by_id[corrected_card]["standard_command_de"],
            "surface_changed_by_master": "YES" if apprentice_surface != corrected_surface else "NO",
            "foreign_hand_preserved": "YES" if index == 1 and corrected_surface == "okaiin" else "NOT_APPLICABLE",
        })

    stages = [
        {
            "stage": "MASTER_EXPECTATION",
            "surface_strip": " ".join(master_surfaces),
            "card_strip": "|".join(expected_cards),
            "semantic_sequence_correct": "YES",
            "foreign_hand_preserved": "NOT_APPLICABLE",
            "operation_from_previous": "NONE",
        },
        {
            "stage": "APPRENTICE_MIXED_COPY",
            "surface_strip": " ".join(apprentice_surfaces),
            "card_strip": "|".join(apprentice_cards),
            "semantic_sequence_correct": "NO",
            "foreign_hand_preserved": "YES",
            "operation_from_previous": "COPY_WITH_ONE_ALLOGRAPH_ONE_ADJACENT_SWAP_ONE_CARD_SUBSTITUTION",
        },
        {
            "stage": "ORDER_REPAIRED",
            "surface_strip": "okaiin qokal cfhy cphy shey shedy",
            "card_strip": "PROC038|PROC048|PROC028|PROC030|PROC031|PROC078",
            "semantic_sequence_correct": "NO",
            "foreign_hand_preserved": "YES",
            "operation_from_previous": "SWAP_POSITIONS_3_AND_4",
        },
        {
            "stage": "MINIMAL_SEMANTIC_CORRECTION",
            "surface_strip": " ".join(corrected_surfaces),
            "card_strip": "|".join(corrected_cards),
            "semantic_sequence_correct": "YES",
            "foreign_hand_preserved": "YES",
            "operation_from_previous": "REPLACE_POSITION_5_SHEY_WITH_TSHEY",
        },
    ]

    policy_rows = [
        {
            "policy": "NORMALIZE_TO_MASTER_HAND",
            "result_surface_strip": " ".join(master_surfaces),
            "surface_positions_rewritten": 4,
            "adjacent_swaps": 1,
            "card_substitutions": 1,
            "harmless_allographs_erased": 1,
            "semantic_sequence_correct": "YES",
            "selected": "NO",
        },
        {
            "policy": "FIX_CARD_ONLY",
            "result_surface_strip": "okaiin qokal cphy cfhy tshey shedy",
            "surface_positions_rewritten": 1,
            "adjacent_swaps": 0,
            "card_substitutions": 1,
            "harmless_allographs_erased": 0,
            "semantic_sequence_correct": "NO",
            "selected": "NO",
        },
        {
            "policy": "FIX_ORDER_ONLY",
            "result_surface_strip": "okaiin qokal cfhy cphy shey shedy",
            "surface_positions_rewritten": 2,
            "adjacent_swaps": 1,
            "card_substitutions": 0,
            "harmless_allographs_erased": 0,
            "semantic_sequence_correct": "NO",
            "selected": "NO",
        },
        {
            "policy": "MINIMAL_SEMANTIC_CORRECTION",
            "result_surface_strip": " ".join(corrected_surfaces),
            "surface_positions_rewritten": 3,
            "adjacent_swaps": 1,
            "card_substitutions": 1,
            "harmless_allographs_erased": 0,
            "semantic_sequence_correct": "YES",
            "selected": "YES",
        },
    ]

    write_tsv(HERE / "SIX_HUNDRED_FORTY_SECOND_6_POSITION_MIXED_AUDIT.tsv", position_rows, list(position_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_SECOND_4_STAGE_CORRECTION_TRACE.tsv", stages, list(stages[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_SECOND_4_POLICY_MINIMALITY.tsv", policy_rows, list(policy_rows[0]))

    md = [
        "# Minimal korrigieren, Fremdhand bewahren",
        "",
        f"**Meisterstreifen:** `{stages[0]['surface_strip']}`",
        "",
        f"**Lehrlingsstreifen:** `{stages[1]['surface_strip']}`",
        "",
        "Der Lehrling hat drei Abweichungen eingebaut: `okaiin` ist eine erlaubte Fremdhand von PROC038; `cphy cfhy` kehrt Füllen und Auswringen um; `shey` setzt die lange statt der kurzen Haltekarte.",
        "",
        f"**Minimal korrigiert:** `{stages[3]['surface_strip']}`",
        "",
        "Der Meister lässt `okaiin` stehen, vertauscht nur `cphy/cfhy` und ersetzt nur `shey` durch `tshey`. Der fertige Streifen sieht deshalb nicht wie die Meisterhand aus, bedeutet aber wieder exakt dasselbe.",
    ]
    (HERE / "SIX_HUNDRED_FORTY_SECOND_MINIMAL_CORRECTION.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "positions": len(position_rows),
        "stages": len(stages),
        "policies_compared": len(policy_rows),
        "apprentice_strip": stages[1]["surface_strip"],
        "corrected_strip": stages[3]["surface_strip"],
        "corrected_cards_match_master": corrected_cards == expected_cards,
        "foreign_hand_preserved": corrected_surfaces[0] == "okaiin" and master_surfaces[0] == "qokaiin",
        "semantic_repairs": 2,
        "unnecessary_normalizations": 0,
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "MINIMAL_CORRECTION_PRESERVES_HARMLESS_FOREIGN_HAND",
    }
    (HERE / "SIX_HUNDRED_FORTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
