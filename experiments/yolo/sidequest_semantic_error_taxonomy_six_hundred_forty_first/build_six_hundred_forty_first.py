#!/usr/bin/env python3
"""Separate harmless allography, wrong-card substitution, and wrong order."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P640 = ROOT / "experiments/yolo/sidequest_semantic_three_desk_allography_six_hundred_fortieth"


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
    strips = read_tsv(P640 / "SIX_HUNDRED_FORTIETH_3_DESK_STRIPS.tsv")
    cards_by_id = {row["card_no"]: row for row in cards}
    surface_to_cards: dict[str, set[str]] = defaultdict(set)
    for row in cards:
        for surface in row["surfaces"].split("|"):
            surface_to_cards[surface].add(row["card_no"])

    station = next(row for row in strips if row["desk"] == "S_STATION_DESK")
    expected_surfaces = station["surface_strip"].split()
    expected_cards = station["card_strip"].split("|")
    variants = [
        ("MASTER", expected_surfaces, "NONE", "ACCEPT"),
        (
            "HARMLESS_ALLOGRAPH",
            ["okaiin", *expected_surfaces[1:]],
            "same exact card PROC038 written with its licensed unframed surface",
            "ACCEPT_ALLOGRAPH",
        ),
        (
            "WRONG_CARD_LOOKALIKE",
            [*expected_surfaces[:4], "shey", expected_surfaces[5]],
            "SHEY backreads to PROC031 long hold, not PROC122 short hold",
            "RESTORE_EXPECTED_CARD",
        ),
        (
            "WRONG_PROCESS_ORDER",
            [*expected_surfaces[:2], expected_surfaces[3], expected_surfaces[2], *expected_surfaces[4:]],
            "fill card precedes wring card although both card identities survive",
            "RESTORE_CARD_ORDER",
        ),
    ]

    diagnostic_rows: list[dict[str, object]] = []
    position_rows: list[dict[str, object]] = []
    for variant_id, surfaces, diagnosis, correction in variants:
        actual_cards = []
        for position, surface in enumerate(surfaces, 1):
            mapped = surface_to_cards[surface]
            actual_card = next(iter(mapped)) if len(mapped) == 1 else "AMBIGUOUS"
            actual_cards.append(actual_card)
            expected_card = expected_cards[position - 1]
            position_rows.append({
                "variant": variant_id,
                "position": position,
                "expected_surface": expected_surfaces[position - 1],
                "actual_surface": surface,
                "expected_card_no": expected_card,
                "actual_card_no": actual_card,
                "expected_command_de": cards_by_id[expected_card]["standard_command_de"],
                "actual_command_de": cards_by_id[actual_card]["standard_command_de"] if actual_card != "AMBIGUOUS" else "AMBIGUOUS",
                "same_surface": "YES" if surface == expected_surfaces[position - 1] else "NO",
                "same_exact_card": "YES" if actual_card == expected_card else "NO",
                "position_diagnosis": (
                    "UNCHANGED"
                    if surface == expected_surfaces[position - 1]
                    else "LICENSED_ALLOGRAPH_SAME_CARD"
                    if actual_card == expected_card
                    else "DIFFERENT_EXACT_CARD"
                ),
            })
        same_sequence = actual_cards == expected_cards
        same_multiset = Counter(actual_cards) == Counter(expected_cards)
        same_meanings = [cards_by_id[item]["standard_command_de"] for item in actual_cards] == [cards_by_id[item]["standard_command_de"] for item in expected_cards]
        if same_sequence:
            error_class = "NONE" if surfaces == expected_surfaces else "SURFACE_ONLY_ALLOGRAPHY"
        elif same_multiset:
            error_class = "PROCESS_ORDER_ERROR"
        else:
            error_class = "EXACT_CARD_SUBSTITUTION"
        diagnostic_rows.append({
            "variant": variant_id,
            "surface_strip": " ".join(surfaces),
            "backread_card_strip": "|".join(actual_cards),
            "all_surfaces_known": "YES" if all(surface_to_cards[item] for item in surfaces) else "NO",
            "exact_card_sequence_preserved": "YES" if same_sequence else "NO",
            "exact_card_multiset_preserved": "YES" if same_multiset else "NO",
            "command_sequence_preserved": "YES" if same_meanings else "NO",
            "error_class": error_class,
            "master_diagnosis_de": diagnosis,
            "correction_action": correction,
            "cards_changed": sum(a != b for a, b in zip(actual_cards, expected_cards)),
            "positions_changed": sum(a != b for a, b in zip(surfaces, expected_surfaces)),
        })

    write_tsv(HERE / "SIX_HUNDRED_FORTY_FIRST_4_STRIP_DIAGNOSTICS.tsv", diagnostic_rows, list(diagnostic_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_FIRST_24_POSITION_AUDIT.tsv", position_rows, list(position_rows[0]))

    md = [
        "# Drei Fehlerarten auf einem Streifen",
        "",
        f"**Meister:** `{diagnostic_rows[0]['surface_strip']}`",
        "",
        f"**Erlaubte Schreiberform:** `{diagnostic_rows[1]['surface_strip']}`",
        "",
        "`okaiin` und `qokaiin` sind dieselbe exakte Sollmaßkarte. Nichts wird korrigiert.",
        "",
        f"**Falsche Karte:** `{diagnostic_rows[2]['surface_strip']}`",
        "",
        "`shey` ist zwar eine echte Karte, bedeutet hier aber lang halten. Für den kurzen Halt muss `tshey` zurück.",
        "",
        f"**Falsche Reihenfolge:** `{diagnostic_rows[3]['surface_strip']}`",
        "",
        "`cphy` und `cfhy` sind beide richtig kopiert, aber Einfüllen steht vor Auswringen. Nur ihre Reihenfolge wird korrigiert.",
        "",
        "## Lehrregel",
        "",
        "1. Andere Oberfläche, gleiche Karte: stehen lassen.",
        "2. Andere Karte: erwartete Karte wiederherstellen.",
        "3. Gleiche Karten, falsche Reihenfolge: Karten umstellen.",
    ]
    (HERE / "SIX_HUNDRED_FORTY_FIRST_MASTER_CORRECTIONS.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "variants": len(diagnostic_rows),
        "positions_audited": len(position_rows),
        "master_surface_strip": diagnostic_rows[0]["surface_strip"],
        "accepted_allograph_surface_strip": diagnostic_rows[1]["surface_strip"],
        "wrong_card_surface_strip": diagnostic_rows[2]["surface_strip"],
        "wrong_order_surface_strip": diagnostic_rows[3]["surface_strip"],
        "error_classes": [row["error_class"] for row in diagnostic_rows],
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "WORKSHOP_SEPARATES_SURFACE_CARD_AND_ORDER_CORRECTIONS",
    }
    (HERE / "SIX_HUNDRED_FORTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
