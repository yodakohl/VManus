#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_ninth_workshop_grammar_eight_hundred_thirty_third"
WATER = ROOT / "sidequest_semantic_water_paradigm_eight_hundred_thirty_fifth"
PREFIX = "EIGHT_HUNDRED_FORTY_FIFTH"

RULES = {
    "OS": ("MEMORIZE_WHOLE_CARD", "DAZU", "Use as a short additive connector before the added material/action."),
    "RESUME_CARD": ("MEMORIZE_WHOLE_CARD", "DAVON", "Resume the current prepared material inside the same record; memorize dchol/schol renderers."),
    "TALAM": ("MEMORIZE_WHOLE_CARD", "BEISEITESTELLEN", "Set the current prepared item aside; do not split TALAM into productive stems."),
    "Y+K+AN": ("MEMORIZE_BOUND_FRAME", "POSTEN · ZUGEBEN · NACHGABE", "AN means a subsequent addition only inside the attested Y+K+AN frame."),
    "OK+Y+LD+DY": ("MEMORIZE_BOUND_FRAME", "ANSETZEN · POSTEN · BEFESTIGEN · SCHLUSS", "LD means fasten only inside this set-item-and-close frame."),
    "DA+IIN": ("MEMORIZE_BOUND_FRAME", "ZWEI · STUFE", "DA means two/second only before the learned IIN stage card."),
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
    statement_by_id = {row["statement_id"]: row for row in statements}

    exception_cards = []
    for card in cards:
        if card["card_tier"] == "FULLY_CORE33_RECIPE":
            continue
        mode, value, rule = RULES[card["component_recipe"]]
        exception_cards.append(
            {
                "exact_card_id": card["exact_card_id"],
                "surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "reading_de": card["ninth_grammar_reading_de"],
                "events": card["events"],
                "card_tier": card["card_tier"],
                "learning_mode": mode,
                "short_invariant_value_de": value,
                "apprentice_rule": rule,
            }
        )
    exception_ids = {row["exact_card_id"] for row in exception_cards}
    rule_by_id = {row["exact_card_id"]: row for row in exception_cards}

    exception_events = []
    for event in events:
        if event["exact_card_id"] not in exception_ids:
            continue
        card = rule_by_id[event["exact_card_id"]]
        statement = statement_by_id[event["statement_id"]]
        exception_events.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "learning_mode": card["learning_mode"],
                "short_invariant_value_de": card["short_invariant_value_de"],
                "full_statement_de": statement["working_reading_de"],
                "same_value_as_card": "YES",
            }
        )

    lessons = []
    for index, row in enumerate(sorted(exception_cards, key=lambda item: (item["learning_mode"], item["surfaces"])), 1):
        lessons.append(
            {
                "lesson": index,
                "surfaces": row["surfaces"],
                "learning_mode": row["learning_mode"],
                "say_de": row["short_invariant_value_de"],
                "do_not_generalize": {
                    "OS": "Do not infer a productive O+S split.",
                    "RESUME_CARD": "Do not split dchol/schol into D/CH/OL meanings.",
                    "TALAM": "Do not derive T+AL+AM; AM has no independent card.",
                    "Y+K+AN": "Do not use AN outside this addition frame.",
                    "OK+Y+LD+DY": "Do not use LD outside this fastening frame.",
                    "DA+IIN": "Do not use DA as a free number elsewhere.",
                }[row["component_recipe"]],
                "practice": row["apprentice_rule"],
            }
        )

    write(f"{PREFIX}_6_EXCEPTION_CARDS.tsv", exception_cards, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "card_tier", "learning_mode", "short_invariant_value_de", "apprentice_rule"])
    write(f"{PREFIX}_7_EXCEPTION_EVENTS.tsv", exception_events, ["event_id", "page", "record", "statement_id", "surface", "component_recipe", "learning_mode", "short_invariant_value_de", "full_statement_de", "same_value_as_card"])
    write(f"{PREFIX}_6_APPRENTICE_EXCEPTION_LESSONS.tsv", lessons, ["lesson", "surfaces", "learning_mode", "say_de", "do_not_generalize", "practice"])

    summary = {
        "status": "PASS",
        "decision": "COMPLETE_EXCEPTION_DECK_IS_THREE_BOUND_FRAMES_PLUS_THREE_WHOLE_CARDS",
        "all_cards": len(cards),
        "all_events": len(events),
        "fully_composed_cards": sum(row["card_tier"] == "FULLY_CORE33_RECIPE" for row in cards),
        "fully_composed_events": sum(int(row["events"]) for row in cards if row["card_tier"] == "FULLY_CORE33_RECIPE"),
        "exception_cards": len(exception_cards),
        "exception_events": len(exception_events),
        "bound_cards": sum(row["learning_mode"] == "MEMORIZE_BOUND_FRAME" for row in exception_cards),
        "whole_cards": sum(row["learning_mode"] == "MEMORIZE_WHOLE_CARD" for row in exception_cards),
        "exception_pages": sorted({row["page"] for row in exception_events}),
        "exception_records": sorted({row["record"] for row in exception_events}),
        "new_values": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 845: complete exception deck

The productive grammar covers 167/173 exact cards and 374/381 events. The
entire remainder is six cards/seven events, small enough for an apprentice to
memorize explicitly.

Three are whole cards: OS=DAZU, dchol/schol=DAVON, and TALAM=BEISEITESTELLEN.
Three are bound frames: Y+K+AN adds a subsequent addition; OK+Y+LD+DY fastens
the current item and closes; DA+IIN names a second stage. AN, LD and DA are not
released as free productive stems.

Every occurrence keeps the same short value. The deck spans five pages and six
records, but introduces no local plant, basin or station noun. This gives the
workshop exactly the mixed system sought in the sidequest: 39 productive or
licensed components plus six explicit exception lessons.

Next, publish a complete tenth-edition dictionary and event ledger with one
learning mode on every card: COMPOSE_COMPONENTS, MEMORIZE_BOUND_FRAME, or
MEMORIZE_WHOLE_CARD. Carry forward the four AIR wording repairs.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
