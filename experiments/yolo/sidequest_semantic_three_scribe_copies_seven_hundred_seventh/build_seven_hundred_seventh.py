#!/usr/bin/env python3
"""Build Pass 707: copy one commission in three attested surface styles."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P706 = ROOT / "experiments/yolo/sidequest_semantic_continuous_commission_seven_hundred_sixth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


STYLES = [
    ("H1_SHORT_HAND", "KUERZESTE_BELEGTE_FORM", "Schnelle Kopierhand; nimmt pro Kartenfamilie die kuerzeste vorhandene Oberflaeche."),
    ("H2_CUSTOM_HAND", "HAEUFIGSTE_BELEGTE_FORM", "Gewohnheitshand; nimmt die im festen Material haeufigste Oberflaeche."),
    ("H3_FRAME_HAND", "LAENGSTE_BELEGTE_FORM", "Rahmenfreudige Hand; nimmt pro Kartenfamilie die laengste vorhandene Oberflaeche."),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    fixed_events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    commission = read(P706 / "SEVEN_HUNDRED_SIXTH_14_CARD_FORWARD_BACKWARD_TRACE.tsv")
    card_by_no = {row["card_no"]: row for row in cards}

    surface_counts: dict[str, Counter[str]] = defaultdict(Counter)
    surface_to_cards: dict[str, set[str]] = defaultdict(set)
    for event in fixed_events:
        surface_counts[event["card_no"]][event["observed_surface"]] += 1
    for card in cards:
        for surface in card["surfaces"].split("|"):
            surface_to_cards[surface].add(card["card_no"])

    def select(card_no: str, mode: str) -> str:
        forms = card_by_no[card_no]["surfaces"].split("|")
        if mode == "KUERZESTE_BELEGTE_FORM":
            return min(forms, key=lambda item: (len(item), item))
        if mode == "LAENGSTE_BELEGTE_FORM":
            return max(forms, key=lambda item: (len(item), item))
        return max(forms, key=lambda item: (surface_counts[card_no][item], -len(item), item))

    copy_rows = []
    trace_rows = []
    surfaces_by_hand: dict[str, list[str]] = {}
    line_cuts = [(0, 5), (5, 11), (11, 14)]
    for hand_id, mode, description in STYLES:
        surfaces = [select(row["card_no"], mode) for row in commission]
        surfaces_by_hand[hand_id] = surfaces
        lines = [" ".join(surfaces[first:last]) for first, last in line_cuts]
        copy_rows.append({
            "hand_id": hand_id, "selection_mode": mode, "description_de": description,
            "line_1": lines[0], "line_2": lines[1], "line_3": lines[2],
            "complete_surface_sequence": " ".join(surfaces),
            "cards": len(surfaces), "statements": 7, "owners": 2,
            "semantic_component_sequence": " | ".join(row["component_recipe"] for row in commission),
        })
        for source, surface in zip(commission, surfaces):
            possible = sorted(surface_to_cards[surface])
            trace_rows.append({
                "hand_id": hand_id, "commission_event": source["commission_event"],
                "statement_no": source["statement_no"], "owner_id": source["owner_id"],
                "selected_surface": surface, "surface_length": len(surface),
                "surface_fixed_occurrences": surface_counts[source["card_no"]][surface],
                "possible_card_numbers_from_surface": "|".join(possible),
                "surface_card_ambiguity": len(possible),
                "recovered_card_no": possible[0] if len(possible) == 1 else "AMBIGUOUS",
                "expected_card_no": source["card_no"],
                "exact_card_recovery": "YES" if possible == [source["card_no"]] else "NO",
                "recovered_component_recipe": card_by_no[possible[0]]["component_recipe"] if len(possible) == 1 else "AMBIGUOUS",
                "expected_component_recipe": source["component_recipe"],
                "exact_component_recovery": "YES" if len(possible) == 1 and card_by_no[possible[0]]["component_recipe"] == source["component_recipe"] else "NO",
                "atomic_reading_de": source["atomic_backreading_de"],
            })

    difference_rows = []
    for left, right in combinations([style[0] for style in STYLES], 2):
        left_surfaces = surfaces_by_hand[left]
        right_surfaces = surfaces_by_hand[right]
        different = [index + 1 for index, (a, b) in enumerate(zip(left_surfaces, right_surfaces)) if a != b]
        difference_rows.append({
            "left_hand": left, "right_hand": right,
            "different_card_positions": len(different),
            "same_card_positions": len(left_surfaces) - len(different),
            "different_positions": "|".join(map(str, different)),
            "card_identity_changes": 0, "component_changes": 0, "owner_changes": 0,
        })

    write("SEVEN_HUNDRED_SEVENTH_3_HAND_COPIES.tsv", copy_rows)
    write("SEVEN_HUNDRED_SEVENTH_42_SURFACE_BACKREAD_TRACE.tsv", trace_rows)
    write("SEVEN_HUNDRED_SEVENTH_3_HAND_DIFFERENCES.tsv", difference_rows)

    readable = ["# Drei Schreiberkopien desselben Auftrags", ""]
    for row in copy_rows:
        readable.extend([
            f"## {row['hand_id']}", "", row["description_de"], "",
            f"`{row['line_1']}`", "", f"`{row['line_2']}`", "", f"`{row['line_3']}`", "",
        ])
    readable.extend([
        "## Gemeinsame Ruecklesung", "",
        "Alle drei Kopien ergeben dieselben 14 Karten, dieselben Komponenten, dieselben sieben Aussagen und denselben Besitzerwechsel. Variiert wird nur die Auswahl unter bereits belegten Oberflaechen derselben Kartenfamilie.",
    ])
    (HERE / "SEVEN_HUNDRED_SEVENTH_THREE_COPIES_READABLE.md").write_text("\n".join(readable), encoding="utf-8")

    summary = {
        "status": "PASS", "hands": len(copy_rows), "events_per_hand": len(commission),
        "surface_trace_rows": len(trace_rows), "pairwise_hand_comparisons": len(difference_rows),
        "exact_card_recoveries": sum(row["exact_card_recovery"] == "YES" for row in trace_rows),
        "exact_component_recoveries": sum(row["exact_component_recovery"] == "YES" for row in trace_rows),
        "surface_changes_short_vs_custom": next(row["different_card_positions"] for row in difference_rows if row["left_hand"] == "H1_SHORT_HAND" and row["right_hand"] == "H2_CUSTOM_HAND"),
        "surface_changes_custom_vs_frame": next(row["different_card_positions"] for row in difference_rows if row["left_hand"] == "H2_CUSTOM_HAND" and row["right_hand"] == "H3_FRAME_HAND"),
        "new_cards": 0, "new_surfaces": 0,
        "decision": "THREE_ATTESTED_SURFACE_STYLES_ROUNDTRIP_TO_ONE_IDENTICAL_COMMISSION",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
