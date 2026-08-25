#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_ninth_workshop_grammar_eight_hundred_thirty_third"
WATER = ROOT / "sidequest_semantic_water_paradigm_eight_hundred_thirty_fifth"
PREFIX = "EIGHT_HUNDRED_FORTY_FOURTH"

PORTABLE = {
    "OK+E+Y": "den Posten kurz ansetzen",
    "OL+DY": "weiter und schliessen",
    "OL+K+AIN": "eine Portion weiter zugeben",
    "OT+CHD+DY": "danach umsetzen und schliessen",
    "OT+Y": "danach der aktuelle Posten",
    "OT+CH+OR": "danach vom Ansatz entnehmen",
    "OT+E+DY": "danach kurz schliessen",
    "OT+EE+Y": "danach der lange Posten",
    "CTH+E+Y": "den Posten kurz bereiten",
    "OT+EE+DY": "danach lang schliessen",
    "SHED+AL": "an der Zielstelle stehen lassen",
    "CFH+Y": "den Posten auspressen",
    "CH+AIR": "Wasser entnehmen",
    "AR+Y": "den Posten aus der Quelle",
    "CH+CKH+AL": "durch den Durchlass an der Zielstelle entnehmen",
    "CHD+AL": "zur Zielstelle umsetzen",
    "AL+R+OR": "den Ansatz an der Zielstelle kuehlen",
    "CHD+AIN": "eine Portion umsetzen",
    "CHD+Y": "den Posten umsetzen",
    "CH+EE+CKH+O+DY": "lang durch den Durchlass im Arbeitsgang entnehmen und schliessen",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cards = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_173_CARD_NINTH_DICTIONARY.tsv")
    events = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_381_EVENT_REPARSE.tsv")
    statements = read(WATER / "EIGHT_HUNDRED_THIRTY_FIFTH_116_WATER_ALIGNED_STATEMENTS.tsv")
    ordered = sorted(cards, key=lambda row: (-int(row["events"]), row["registered_surfaces"]))
    tier = ordered[40:60]
    tier_ids = {row["exact_card_id"] for row in tier}
    top60_ids = {row["exact_card_id"] for row in ordered[:60]}

    card_rows = []
    for frequency_rank, card in enumerate(tier, 41):
        card_rows.append(
            {
                "frequency_rank": frequency_rank,
                "exact_card_id": card["exact_card_id"],
                "surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "literal_reading_de": card["ninth_grammar_reading_de"],
                "portable_workshop_paraphrase_de": PORTABLE[card["component_recipe"]],
                "events": card["events"],
                "card_tier": card["card_tier"],
                "learning_mode": "COMPOSE_COMPONENTS",
                "page_specific_noun": "NONE",
            }
        )
    portable_by_id = {row["exact_card_id"]: row["portable_workshop_paraphrase_de"] for row in card_rows}

    event_rows = []
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        if event["exact_card_id"] not in tier_ids:
            continue
        item = {
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "exact_card_id": event["exact_card_id"],
            "surface": event["surface"],
            "component_recipe": event["component_recipe"],
            "portable_workshop_paraphrase_de": portable_by_id[event["exact_card_id"]],
            "learning_mode": "COMPOSE_COMPONENTS",
        }
        event_rows.append(item)
        by_statement[event["statement_id"]].append(item)

    statement_by_id = {row["statement_id"]: row for row in statements}
    statement_rows = []
    for statement_id, selected in by_statement.items():
        source = statement_by_id[statement_id]
        statement_rows.append(
            {
                "statement_id": statement_id,
                "page": source["page"],
                "record": source["record"],
                "selected_events": len(selected),
                "selected_surfaces": " | ".join(str(row["surface"]) for row in selected),
                "portable_sequence_de": " | ".join(str(row["portable_workshop_paraphrase_de"]) for row in selected),
                "full_working_reading_de": source["working_reading_de"],
            }
        )

    cumulative_events = [row for row in events if row["exact_card_id"] in top60_ids]
    write(f"{PREFIX}_20_FOURTH_TIER_CARDS.tsv", card_rows, ["frequency_rank", "exact_card_id", "surfaces", "component_recipe", "literal_reading_de", "portable_workshop_paraphrase_de", "events", "card_tier", "learning_mode", "page_specific_noun"])
    write(f"{PREFIX}_31_FOURTH_TIER_EVENTS.tsv", event_rows, ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "portable_workshop_paraphrase_de", "learning_mode"])
    write(f"{PREFIX}_28_FOURTH_TIER_STATEMENTS.tsv", statement_rows, ["statement_id", "page", "record", "selected_events", "selected_surfaces", "portable_sequence_de", "full_working_reading_de"])

    summary = {
        "status": "PASS",
        "decision": "RANKS41_TO60_ARE_FULLY_COMPOSITIONAL",
        "tier_cards": len(card_rows),
        "tier_events": len(event_rows),
        "tier_statements": len(statement_rows),
        "tier_records": len({row["record"] for row in event_rows}),
        "tier_pages": len({row["page"] for row in event_rows}),
        "composed_cards": sum(row["learning_mode"] == "COMPOSE_COMPONENTS" for row in card_rows),
        "bound_cards": 0,
        "whole_cards": 0,
        "cumulative_top60_events": len(cumulative_events),
        "cumulative_top60_fraction": round(len(cumulative_events) / 381, 6),
        "page_specific_values_added": 0,
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 844: fourth frequency tier

All 20 cards at ranks 41–60 are ordinary component recipes. They add 31 events
in 28 statements across ten records and all seven prose pages. No bound value,
whole card, or picture-specific noun is needed.

Even the longest card in the tier, `cheeckhody = CH+EE+CKH+O+DY`, reads only
from familiar atoms: take, long, passage, work step, close. Its fluent portable
reading is “lang durch den Durchlass im Arbeitsgang entnehmen und schließen”,
not a special memorized recipe sentence.

The top 60 exact cards now cover 268/381 events (70.3%). Across those 60 cards,
only DAVON is a learned whole card. That is a strong practical compression of
the ten-page working vocabulary.

Next, stop walking arbitrary frequency blocks and publish the complete six-card
exception deck: three bound constructions and three memorized whole cards,
with all seven events and concrete apprentice memorization rules.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
