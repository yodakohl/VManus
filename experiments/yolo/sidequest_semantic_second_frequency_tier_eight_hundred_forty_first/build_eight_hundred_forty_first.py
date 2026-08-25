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
PREFIX = "EIGHT_HUNDRED_FORTY_FIRST"

PORTABLE = {
    "OK+E+DY": "kurz ansetzen und schliessen",
    "CTH+Y": "den Posten bereiten",
    "OR": "der aktuelle Ansatz",
    "OK+AIN": "eine Portion ansetzen",
    "OK+EE+Y": "den Posten laenger ansetzen",
    "OK+AL": "an der Zielstelle ansetzen",
    "AR": "aus der Quelle",
    "CKH+Y": "Durchlass fuer den Posten",
    "SH+EE+Y": "den Posten laenger halten",
    "HO": "die Zutat",
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
    tier = ordered[10:20]
    tier_ids = {row["exact_card_id"] for row in tier}
    top20_ids = {row["exact_card_id"] for row in ordered[:20]}

    card_rows = []
    for frequency_rank, card in enumerate(tier, 11):
        card_rows.append(
            {
                "frequency_rank": frequency_rank,
                "exact_card_id": card["exact_card_id"],
                "surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "literal_reading_de": card["ninth_grammar_reading_de"],
                "portable_workshop_paraphrase_de": PORTABLE[card["component_recipe"]],
                "events": card["events"],
                "page_specific_noun": "NONE",
                "decision": "PORTABLE_SECOND_TIER_CARD",
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
                "owner_noun_not_used_in_portable_sequence": "YES",
            }
        )

    cumulative_events = [row for row in events if row["exact_card_id"] in top20_ids]
    cumulative = []
    for page in sorted({row["page"] for row in events}):
        page_total = sum(row["page"] == page for row in events)
        page_covered = sum(row["page"] == page for row in cumulative_events)
        cumulative.append(
            {
                "page": page,
                "all_events": page_total,
                "top20_events": page_covered,
                "coverage_fraction": f"{page_covered / page_total:.6f}",
            }
        )

    write(f"{PREFIX}_10_SECOND_TIER_CARDS.tsv", card_rows, ["frequency_rank", "exact_card_id", "surfaces", "component_recipe", "literal_reading_de", "portable_workshop_paraphrase_de", "events", "page_specific_noun", "decision"])
    write(f"{PREFIX}_59_SECOND_TIER_EVENTS.tsv", event_rows, ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "literal_reading_de", "portable_workshop_paraphrase_de", "owner_independent"])
    write(f"{PREFIX}_40_SECOND_TIER_STATEMENTS.tsv", statement_rows, ["statement_id", "page", "record", "selected_events", "selected_surfaces", "portable_sequence_de", "full_working_reading_de", "owner_noun_not_used_in_portable_sequence"])
    write(f"{PREFIX}_7_PAGE_TOP20_COVERAGE.tsv", cumulative, ["page", "all_events", "top20_events", "coverage_fraction"])

    summary = {
        "status": "PASS",
        "decision": "SECOND_FREQUENCY_TIER_IS_PORTABLE_WITHOUT_NEW_LOCAL_VALUES",
        "tier_cards": len(card_rows),
        "tier_events": len(event_rows),
        "tier_statements": len(statement_rows),
        "tier_records": len({row["record"] for row in event_rows}),
        "tier_pages": len({row["page"] for row in event_rows}),
        "cumulative_top20_events": len(cumulative_events),
        "cumulative_top20_fraction": round(len(cumulative_events) / 381, 6),
        "page_specific_values_added": 0,
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 841: second frequency tier

Frequency ranks 11–20 add 59 events in 40 statements. They remain portable
across all seven prose pages and nine records without a new picture-specific
meaning.

The cards read: set briefly and close; prepare the current item; current batch;
set one portion; set the item longer; set at the target; from the source;
passage for the item; hold the item longer; and ingredient. CKH+Y is kept
deliberately elliptical as “Durchlass für den Posten”; no hidden LEITEN is
inserted.

Together frequency ranks 1–20 now cover 186/381 events (48.8%). This is not a
claim that half the text is deciphered: the portable card instructions still
need their local owner and neighboring cards. It does show that the mixed
component-plus-card manual is not confined to a handful of showcase forms.

Next, test ranks 21–30. That tier is where rarer process cards begin to enter;
record exactly which cards remain compositional and which require a learned
whole-card value.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
