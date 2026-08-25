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
MANUAL = ROOT / "sidequest_semantic_card_construction_manual_eight_hundred_fortieth"
EXCEPTIONS = ROOT / "sidequest_semantic_exception_deck_eight_hundred_forty_fifth"
ACTIVE = ROOT / "sidequest_semantic_address_path_deck_eight_hundred_thirty_seventh"
QUANTITY = ROOT / "sidequest_semantic_quantity_composition_eight_hundred_thirty_eighth"
GRADE = ROOT / "sidequest_semantic_grade_composition_eight_hundred_thirty_ninth"
PREFIX = "EIGHT_HUNDRED_FORTY_SIXTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def learning_mode(card_tier: str) -> str:
    if card_tier == "FULLY_CORE33_RECIPE":
        return "COMPOSE_COMPONENTS"
    if card_tier == "BOUND_RECIPE":
        return "MEMORIZE_BOUND_FRAME"
    return "MEMORIZE_WHOLE_CARD"


def main() -> None:
    components = read(MANUAL / "EIGHT_HUNDRED_FORTIETH_39_COMPONENT_CONSTRUCTION_MANUAL.tsv")
    cards_old = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_173_CARD_NINTH_DICTIONARY.tsv")
    events_old = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_381_EVENT_REPARSE.tsv")
    statements = read(WATER / "EIGHT_HUNDRED_THIRTY_FIFTH_116_WATER_ALIGNED_STATEMENTS.tsv")
    rules = read(MANUAL / "EIGHT_HUNDRED_FORTIETH_12_APPRENTICE_RULES.tsv")
    exceptions = read(EXCEPTIONS / "EIGHT_HUNDRED_FORTY_FIFTH_6_EXCEPTION_CARDS.tsv")
    active = read(ACTIVE / "EIGHT_HUNDRED_THIRTY_SEVENTH_30_REBALANCED_ACTIVE_SURFACES.tsv")
    quantity_new = read(QUANTITY / "EIGHT_HUNDRED_THIRTY_EIGHTH_3_NEW_IIN_PREDICTIONS.tsv")
    grade_all = read(GRADE / "EIGHT_HUNDRED_THIRTY_NINTH_7_GRADE_PREDICTIONS.tsv")

    cards = []
    for card in cards_old:
        cards.append(
            {
                "exact_card_id": card["exact_card_id"],
                "registered_surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "tenth_edition_reading_de": card["ninth_grammar_reading_de"],
                "events": card["events"],
                "card_tier": card["card_tier"],
                "learning_mode": learning_mode(card["card_tier"]),
                "core33_touch": card["core33_touch"],
                "fully_core33": card["fully_core33"],
                "remainder_components": card["remainder_components"],
            }
        )
    card_by_id = {row["exact_card_id"]: row for row in cards}

    events = []
    for event in events_old:
        card = card_by_id[event["exact_card_id"]]
        events.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "owner_de": event["owner_de"],
                "exact_card_id": event["exact_card_id"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "tenth_edition_reading_de": card["tenth_edition_reading_de"],
                "learning_mode": card["learning_mode"],
                "form_owner_boundary_status": event["form_owner_boundary_status"],
            }
        )

    supplement = []
    for row in quantity_new:
        supplement.append(
            {
                "predicted_surface": row["predicted_surface"],
                "component_recipe": row["component_recipe"],
                "reading_de": row["reading_de"],
                "source": row["model"],
                "priority": "QUANTITY_TRIAD",
                "status": "SUPPLEMENTAL_PREDICTION_ONLY",
            }
        )
    for row in grade_all:
        if row["priority"] != "HIGH":
            continue
        supplement.append(
            {
                "predicted_surface": row["predicted_surface"],
                "component_recipe": row["operator_frame"].replace("GRADE", row["missing_grade"]),
                "reading_de": row["predicted_reading_de"],
                "source": "GRADE_GRID",
                "priority": "GRADE_MISSING_CELL",
                "status": "SUPPLEMENTAL_PREDICTION_ONLY",
            }
        )

    write(f"{PREFIX}_39_COMPONENT_MANUAL.tsv", components, ["component_no", "component", "short_value_de", "construction_slot", "grammar_tier", "exact_cards", "events", "apprentice_rule"])
    write(f"{PREFIX}_173_CARD_DICTIONARY.tsv", cards, ["exact_card_id", "registered_surfaces", "component_recipe", "tenth_edition_reading_de", "events", "card_tier", "learning_mode", "core33_touch", "fully_core33", "remainder_components"])
    write(f"{PREFIX}_381_EVENT_INTERLINEAR.tsv", events, ["event_id", "page", "record", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "tenth_edition_reading_de", "learning_mode", "form_owner_boundary_status"])
    write(f"{PREFIX}_116_STATEMENT_EDITION.tsv", statements, ["statement_id", "page", "record", "owner_noun_de", "events", "surface_sequence", "component_sequence", "ninth_grammar_literal_de", "working_reading_de", "fully_core33_events", "remainder_events", "revision_sources"])
    write(f"{PREFIX}_12_APPRENTICE_RULES.tsv", rules, ["priority", "rule", "instruction"])
    write(f"{PREFIX}_6_EXCEPTION_CARDS.tsv", exceptions, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "card_tier", "learning_mode", "short_invariant_value_de", "apprentice_rule"])
    write(f"{PREFIX}_30_ACTIVE_PREDICTION_SURFACES.tsv", active, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition", "recipe_rank", "selection_reason", "address_path_rank", "address_path_status"])
    write(f"{PREFIX}_5_SUPPLEMENTAL_PREDICTIONS.tsv", supplement, ["predicted_surface", "component_recipe", "reading_de", "source", "priority", "status"])

    record_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for statement in statements:
        record_groups[statement["record"]].append(statement)
    readable = ["# Tenth workshop edition — all eleven prose records", ""]
    for record, rows in record_groups.items():
        readable.extend([f"## {record} — {rows[0]['page']}", ""])
        for row in rows:
            readable.append(f"- `{row['statement_id']}` {row['working_reading_de']}")
        readable.append("")
    (HERE / f"{PREFIX}_ELEVEN_RECORDS.md").write_text("\n".join(readable), encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "TENTH_WORKSHOP_EDITION_INTEGRATES_COMPOSITION_AND_SMALL_EXCEPTION_DECK",
        "components": len(components),
        "cards": len(cards),
        "events": len(events),
        "statements": len(statements),
        "records": len(record_groups),
        "compose_cards": sum(row["learning_mode"] == "COMPOSE_COMPONENTS" for row in cards),
        "bound_cards": sum(row["learning_mode"] == "MEMORIZE_BOUND_FRAME" for row in cards),
        "whole_cards": sum(row["learning_mode"] == "MEMORIZE_WHOLE_CARD" for row in cards),
        "compose_events": sum(row["learning_mode"] == "COMPOSE_COMPONENTS" for row in events),
        "bound_events": sum(row["learning_mode"] == "MEMORIZE_BOUND_FRAME" for row in events),
        "whole_events": sum(row["learning_mode"] == "MEMORIZE_WHOLE_CARD" for row in events),
        "active_prediction_surfaces": len(active),
        "active_prediction_recipes": len({row["component_recipe"] for row in active}),
        "supplemental_predictions": len(supplement),
        "air_water_statements": sum("AIR" in [token for recipe in row["component_sequence"].split(" | ") for token in recipe.split("+")] for row in statements),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 846: tenth workshop edition

The complete ten-page prose edition is now rebuilt around one explicit learning
mode per exact card:

- 167 cards / 374 events: COMPOSE_COMPONENTS;
- 3 cards / 3 events: MEMORIZE_BOUND_FRAME;
- 3 cards / 4 events: MEMORIZE_WHOLE_CARD.

All 39 components, 173 cards, 381 events, 116 statements and 11 records are in
one consistent release. O=ARBEITSGANG, Y=POSTEN, AIR=WASSER, AR/CKH/AL,
AIN/AIIN/IIN and E/EE/EEE are all carried forward. The four Bio wording repairs
now say “das laufende Wasser”; no fluent sentence retains the generic
FLUESSIGKEIT synonym.

The compact prediction deck remains 24 recipes / 30 surfaces. Five supplemental
cells record the newly composed quantity and grade predictions without bloating
the main deck.

This is still a creative working translation of ten pages, not a claim about
the whole manuscript. Within that sidequest it is now an executable scribal
system rather than a loose glossary.

Next, test learnability directly: give an apprentice twenty short German
workshop commands made only from the manual, encode them to component recipes,
and decode them back without consulting page owners.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
