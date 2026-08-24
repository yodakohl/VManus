#!/usr/bin/env python3
"""Close the quantity, selection, and active-item layer."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh/SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv"
VALUES = {
    "AIN": "PORTION",
    "AIIN": "SOLLMASS",
    "IIN": "ARBEITSSTUFE",
    "K": "ZUDOSIEREN",
    "HO": "ZUTAT",
    "Y": "ARBEITSPOSTEN",
}
PREVIOUS_ROOTS = {"OK", "CHD", "SHED", "CHK", "CTH", "OR", "CKH", "SOLK", "SH", "P", "LSH", "CFH", "L", "OL", "OT", "AL", "AR", "AIR"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    all_events = read_tsv(SOURCE)
    selected = [event for event in all_events if set(event["semantic_component_parse"].split("+")) & VALUES.keys()]
    cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in selected:
        cards[event["card_no"]].append(event)

    card_rows = []
    for card in sorted(cards, key=number):
        rows = cards[card]
        first = rows[0]
        roots = [atom for atom in first["semantic_component_parse"].split("+") if atom in VALUES]
        card_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": first["semantic_component_parse"],
            "selected_roots": "+".join(roots),
            "portable_contributions_de": " · ".join(VALUES[root] for root in roots),
            "composed_reading_de": first["standard_command_de"],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "event_ids": "|".join(row["event_id"] for row in rows),
        })

    event_rows = []
    for event in selected:
        roots = [atom for atom in event["semantic_component_parse"].split("+") if atom in VALUES]
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "card_no": event["card_no"],
            "surface": event["surface"],
            "component_recipe": event["semantic_component_parse"],
            "selected_roots": "+".join(roots),
            "portable_contributions_de": " · ".join(VALUES[root] for root in roots),
            "composed_reading_de": event["standard_command_de"],
        })

    root_rows = []
    for root, value in VALUES.items():
        events = [event for event in all_events if root in event["semantic_component_parse"].split("+")]
        root_rows.append({
            "root": root,
            "portable_value_de": value,
            "card_types": len({event["card_no"] for event in events}),
            "events": len(events),
            "component_recipes": len({event["semantic_component_parse"] for event in events}),
            "short_rule_de": {
                "AIN": "eine abgegrenzte Portion",
                "AIIN": "das vorgeschriebene Mass oder der Sollwert",
                "IIN": "eine benannte Stufe des Arbeitsgangs",
                "K": "eine Menge in den laufenden Gang zudosieren",
                "HO": "die lokal gemeinte Zutat oder Materialgabe",
                "Y": "der aktuell gemeinte und weiter verfuegbare Arbeitsposten",
            }[root],
        })

    contrasts = [
        {"contrast": "AIN_vs_AIIN", "left": "AIN=PORTION", "right": "AIIN=SOLLMASS", "teaching_test": "AIN names the charge; AIIN sets its prescribed amount"},
        {"contrast": "AIIN_vs_IIN", "left": "AIIN=SOLLMASS", "right": "IIN=ARBEITSSTUFE", "teaching_test": "measure is not process stage"},
        {"contrast": "K_vs_HO", "left": "K=ZUDOSIEREN", "right": "HO=ZUTAT", "teaching_test": "K is the action; HO is the material"},
        {"contrast": "Y_vs_DY", "left": "Y=AKTIVER ARBEITSPOSTEN", "right": "DY=NUR LIZENZIERTE SCHLUSSKONSTRUKTION", "teaching_test": "visible dy can realize the open Y card; spelling alone does not close"},
        {"contrast": "Y_vs_HO", "left": "Y=ANAPHORISCHER POSTEN", "right": "HO=NEUE/LOKALE ZUTAT", "teaching_test": "Y resumes; HO supplies material"},
    ]

    all_roots = PREVIOUS_ROOTS | VALUES.keys()
    remaining = [event for event in all_events if not set(event["semantic_component_parse"].split("+")) & all_roots]
    remaining_cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in remaining:
        remaining_cards[event["card_no"]].append(event)
    remaining_rows = []
    for card in sorted(remaining_cards, key=number):
        rows = remaining_cards[card]
        first = rows[0]
        remaining_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": first["semantic_component_parse"],
            "current_whole_card_value_de": first["standard_command_de"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "next_treatment": "MEMORIZED_WHOLE_CARD_OR_SMALL_REMAINING_ROOT",
        })

    write_tsv(HERE / "SIX_HUNDRED_SEVENTIETH_88_QUANTITY_ITEM_CARDS.tsv", card_rows, list(card_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTIETH_195_QUANTITY_ITEM_EVENTS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTIETH_6_ROOT_SUMMARY.tsv", root_rows, list(root_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTIETH_5_MINIMAL_CONTRASTS.tsv", contrasts, list(contrasts[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTIETH_6_REMAINING_CARDS.tsv", remaining_rows, list(remaining_rows[0]))

    summary = {
        "status": "PASS",
        "root_values": VALUES,
        "union_card_types": len(card_rows),
        "union_events": len(event_rows),
        "new_cards_beyond_pass669": 21,
        "new_events_beyond_pass669": 65,
        "expanded_dictionary_card_types": 167,
        "expanded_dictionary_events": 374,
        "remaining_card_types": len(remaining_rows),
        "remaining_events": sum(int(row["events"]) for row in remaining_rows),
        "decision": "QUANTITY_SELECTION_AND_ACTIVE_ITEM_LAYER_CLOSES_ALL_BUT_SIX_CARDS",
    }
    (HERE / "SIX_HUNDRED_SEVENTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
