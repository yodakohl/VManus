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
PREFIX = "EIGHT_HUNDRED_FORTY_SECOND"

PORTABLE = {
    "CHD+DY": "umsetzen und schliessen",
    "CHK+E+Y": "den Posten kurz waermen",
    "K+AIN": "eine Portion zugeben",
    "OK+Y": "den Posten ansetzen",
    "OL+CHD+DY": "weiter umsetzen und schliessen",
    "SOLK+EE+DY": "laenger sammeln und schliessen",
    "OT+AIIN": "danach nach Sollmass",
    "OT+AL": "danach zur Zielstelle",
    "OK+CHD+DY": "ansetzen, umsetzen und schliessen",
    "SH+CKH+E+DY": "kurz am Durchlass halten und schliessen",
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
    tier = ordered[20:30]
    tier_ids = {row["exact_card_id"] for row in tier}
    top30_ids = {row["exact_card_id"] for row in ordered[:30]}

    card_rows = []
    for frequency_rank, card in enumerate(tier, 21):
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
                "page_specific_noun": "NONE",
                "decision": "PORTABLE_THIRD_TIER_CARD",
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
            "literal_reading_de": event["ninth_grammar_reading_de"],
            "portable_workshop_paraphrase_de": portable_by_id[event["exact_card_id"]],
            "owner_independent": "YES",
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

    boundary = []
    for frequency_rank, card in enumerate(ordered[30:35], 31):
        is_whole = card["card_tier"].startswith("MEMORIZED_WHOLE")
        boundary.append(
            {
                "frequency_rank": frequency_rank,
                "exact_card_id": card["exact_card_id"],
                "surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "reading_de": card["ninth_grammar_reading_de"],
                "events": card["events"],
                "card_tier": card["card_tier"],
                "learned_whole_card_required": "YES" if is_whole else "NO",
                "boundary_note": "FIRST_MEMORIZED_WHOLE_IN_DETERMINISTIC_RANKING" if is_whole else "STILL_COMPOSITIONAL",
            }
        )

    cumulative_events = [row for row in events if row["exact_card_id"] in top30_ids]
    write(f"{PREFIX}_10_THIRD_TIER_CARDS.tsv", card_rows, ["frequency_rank", "exact_card_id", "surfaces", "component_recipe", "literal_reading_de", "portable_workshop_paraphrase_de", "events", "card_tier", "page_specific_noun", "decision"])
    write(f"{PREFIX}_31_THIRD_TIER_EVENTS.tsv", event_rows, ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "literal_reading_de", "portable_workshop_paraphrase_de", "owner_independent"])
    write(f"{PREFIX}_29_THIRD_TIER_STATEMENTS.tsv", statement_rows, ["statement_id", "page", "record", "selected_events", "selected_surfaces", "portable_sequence_de", "full_working_reading_de"])
    write(f"{PREFIX}_5_WHOLE_CARD_BOUNDARY_ROWS.tsv", boundary, ["frequency_rank", "exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "card_tier", "learned_whole_card_required", "boundary_note"])

    summary = {
        "status": "PASS",
        "decision": "THIRD_FREQUENCY_TIER_COMPOSITIONAL__FIRST_WHOLE_CARD_AT_RANK35",
        "tier_cards": len(card_rows),
        "tier_events": len(event_rows),
        "tier_statements": len(statement_rows),
        "tier_records": len({row["record"] for row in event_rows}),
        "tier_pages": len({row["page"] for row in event_rows}),
        "cumulative_top30_events": len(cumulative_events),
        "cumulative_top30_fraction": round(len(cumulative_events) / 381, 6),
        "first_whole_card_rank": next(int(row["frequency_rank"]) for row in boundary if row["learned_whole_card_required"] == "YES"),
        "first_whole_card_surface": next(row["surfaces"] for row in boundary if row["learned_whole_card_required"] == "YES"),
        "page_specific_values_added": 0,
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 842: third frequency tier

Frequency ranks 21–30 remain completely compositional. They add 31 events in
29 statements and require no picture-specific noun. Their cards cover moving
and closing, short warming, adding a portion, setting the item, continuing a
transfer, collecting longer, next prescribed measure, next target, combined
set/transfer/close, and short holding at a passage.

The top 30 exact cards now cover 217/381 events (57.0%). The first learned whole
card in the deterministic frequency-then-surface ordering appears only at rank
35: `dchol/schol = DAVON`, the two-occurrence anaphoric resumption card. Ranks
31–34 are still ordinary component recipes.

This is the architecture we were looking for: a broad productive workshop
grammar interrupted by a small learned vocabulary, not a choice between pure
compositional language and an arbitrary codebook.

Next, read ranks 31–40 as one mixed tier, with DAVON treated honestly as a
memorized whole card, and determine whether its two occurrences function as
the same anaphoric instruction across Herbal and Biological contexts.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
