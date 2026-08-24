#!/usr/bin/env python3
"""Enumerate every nonempty ordered fragment of the five six-card cases."""

from __future__ import annotations

import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P631 = ROOT / "experiments/yolo/sidequest_semantic_five_branch_composition_six_hundred_thirty_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def is_subsequence(fragment: list[str], sequence: list[str]) -> bool:
    cursor = iter(sequence)
    return all(any(candidate == target for candidate in cursor) for target in fragment)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(P613 / "SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv")
    masters = read_tsv(P631 / "SIX_HUNDRED_THIRTY_FIRST_5_ORDER_SUMMARY.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    template_cards = {row["intended_case_id"]: row["card_sequence"].split("|") for row in masters}
    template_surfaces = {row["intended_case_id"]: row["surface_sequence"].split() for row in masters}

    fragment_rows: list[dict[str, object]] = []
    ambiguous_rows: list[dict[str, object]] = []
    by_case_size: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for case_id in sorted(template_cards):
        cards_for_case = template_cards[case_id]
        surfaces_for_case = template_surfaces[case_id]
        for size in range(1, 7):
            for number, positions in enumerate(itertools.combinations(range(6), size), 1):
                fragment_cards = [cards_for_case[index] for index in positions]
                fragment_surfaces = [surfaces_for_case[index] for index in positions]
                matching_cases = [candidate for candidate in sorted(template_cards) if is_subsequence(fragment_cards, template_cards[candidate])]
                unique = len(matching_cases) == 1
                row = {
                    "fragment_id": f"{case_id}_K{size}_{number:02d}",
                    "source_case": case_id,
                    "surviving_cards": size,
                    "source_positions": "|".join(str(index + 1) for index in positions),
                    "surface_fragment": " ".join(fragment_surfaces),
                    "card_fragment": "|".join(fragment_cards),
                    "matching_cases": "|".join(matching_cases),
                    "matching_case_count": len(matching_cases),
                    "unique_case_recovery": "YES" if unique and matching_cases[0] == case_id else "NO",
                    "owner_or_margin_needed": "NO" if unique else "YES",
                }
                fragment_rows.append(row)
                by_case_size[(case_id, size)].append(row)
                if not unique:
                    ambiguous_rows.append({
                        **row,
                        "shared_commands_de": " / ".join(card_by_id[card_id]["standard_command_de"] for card_id in fragment_cards),
                        "resolution_rule_de": "Bildbesitzer, Randmarke oder eine zusätzliche fallcharakteristische Karte verwenden",
                    })

    threshold_rows: list[dict[str, object]] = []
    for case_id in sorted(template_cards):
        threshold = next(
            size
            for size in range(1, 7)
            if all(row["unique_case_recovery"] == "YES" for larger in range(size, 7) for row in by_case_size[(case_id, larger)])
        )
        rows = [row for size in range(1, 7) for row in by_case_size[(case_id, size)]]
        largest_ambiguous = max(int(row["surviving_cards"]) for row in rows if row["unique_case_recovery"] == "NO")
        threshold_rows.append({
            "case_id": case_id,
            "all_nonempty_fragments": len(rows),
            "unique_fragments": sum(row["unique_case_recovery"] == "YES" for row in rows),
            "ambiguous_fragments": sum(row["unique_case_recovery"] == "NO" for row in rows),
            "largest_ambiguous_fragment_size": largest_ambiguous,
            "worst_case_guaranteed_survivors": threshold,
            "example_largest_ambiguous_surface": next(row["surface_fragment"] for row in rows if row["unique_case_recovery"] == "NO" and int(row["surviving_cards"]) == largest_ambiguous),
            "example_largest_ambiguous_matches": next(row["matching_cases"] for row in rows if row["unique_case_recovery"] == "NO" and int(row["surviving_cards"]) == largest_ambiguous),
        })

    signature_rows: list[dict[str, object]] = []
    for case_id in sorted(template_cards):
        for position, (surface, card_id) in enumerate(zip(template_surfaces[case_id], template_cards[case_id]), 1):
            matching_cases = [candidate for candidate in sorted(template_cards) if card_id in template_cards[candidate]]
            if matching_cases == [case_id]:
                signature_rows.append({
                    "case_id": case_id,
                    "master_position": position,
                    "surface": surface,
                    "card_no": card_id,
                    "semantic_component_parse": card_by_id[card_id]["semantic_component_parse"],
                    "command_de": card_by_id[card_id]["standard_command_de"],
                    "single_card_identifies_case": "YES",
                })

    size_rows: list[dict[str, object]] = []
    for case_id in sorted(template_cards):
        for size in range(1, 7):
            rows = by_case_size[(case_id, size)]
            size_rows.append({
                "case_id": case_id,
                "surviving_cards": size,
                "fragments": len(rows),
                "unique": sum(row["unique_case_recovery"] == "YES" for row in rows),
                "ambiguous": sum(row["unique_case_recovery"] == "NO" for row in rows),
                "all_unique": "YES" if all(row["unique_case_recovery"] == "YES" for row in rows) else "NO",
            })

    write_tsv(HERE / "SIX_HUNDRED_FORTY_SIXTH_315_ORDERED_FRAGMENTS.tsv", fragment_rows, list(fragment_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_SIXTH_AMBIGUOUS_FRAGMENTS.tsv", ambiguous_rows, list(ambiguous_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_SIXTH_5_CASE_THRESHOLDS.tsv", threshold_rows, list(threshold_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_SIXTH_SIGNATURE_CARDS.tsv", signature_rows, list(signature_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_SIXTH_30_SIZE_COUNTS.tsv", size_rows, list(size_rows[0]))

    md = [
        "# Wie viel eines Falles muss übrig bleiben?",
        "",
        "Alle 63 nichtleeren geordneten Teilfragmente jedes Sechskartenfalls wurden mit dem Fünf-Fälle-Deck verglichen.",
        "",
        "| Fall | garantiert eindeutig ab | größter mehrdeutiger Rest |",
        "|---|---:|---|",
    ]
    for row in threshold_rows:
        md.append(f"| {row['case_id']} | {row['worst_case_guaranteed_survivors']} Karten | `{row['example_largest_ambiguous_surface']}` ({row['example_largest_ambiguous_matches']}) |")
    md.extend([
        "",
        "C1 und C3 teilen den vierteiligen Rückgrat `qokaiin qokal shey shedy`. Ohne OS/LSHO beziehungsweise CFHY/CPHY bleibt dieser Rest absichtlich unentschieden. C2 braucht im ungünstigsten Fall zwei Karten, C4 und C5 drei.",
        "",
        f"Daneben existieren {len(signature_rows)} einzelne Signaturkarten, die innerhalb dieses kleinen Decks schon allein ihren Fall nennen. Das ist die schnelle Lehrlingsroute; die Schwellen oben sind die pessimistische Route, wenn ausgerechnet nur gemeinsame Karten überleben.",
    ])
    (HERE / "SIX_HUNDRED_FORTY_SIXTH_FRAGMENT_CAPACITY_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "cases": 5,
        "fragments": len(fragment_rows),
        "ambiguous_fragment_rows": len(ambiguous_rows),
        "unique_fragment_rows": sum(row["unique_case_recovery"] == "YES" for row in fragment_rows),
        "signature_cards": len(signature_rows),
        "worst_case_thresholds": {row["case_id"]: int(row["worst_case_guaranteed_survivors"]) for row in threshold_rows},
        "largest_ambiguous_backbone": max(int(row["surviving_cards"]) for row in ambiguous_rows),
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "CASE_RECOGNITION_LIMITS_LOCALIZED_TO_SHARED_BACKBONES",
    }
    (HERE / "SIX_HUNDRED_FORTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
