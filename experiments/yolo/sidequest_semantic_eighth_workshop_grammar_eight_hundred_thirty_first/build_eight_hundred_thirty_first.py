#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_seventh_workshop_grammar_eight_hundred_twenty_seventh"
COMPONENTS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_39_COMPONENT_SEVENTH_GRAMMAR.tsv"
CARDS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_173_CARD_SEVENTH_DICTIONARY.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_116_STATEMENT_REPARSE.tsv"
EXCEPTIONS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_6_EXCEPTIONS.tsv"
PREDICTIONS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_76_UNATTESTED_PREDICTIONS.tsv"
RULES = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_19_TEACHING_RULES.tsv"
HIGH_RECIPES = ROOT / "sidequest_semantic_prediction_deck_eight_hundred_twenty_eighth" / "EIGHT_HUNDRED_TWENTY_EIGHTH_24_HIGH_VALUE_RECIPES.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    old_components = read(COMPONENTS)
    old_cards = read(CARDS)
    old_events = read(EVENTS)
    old_statements = read(STATEMENTS)

    component_rows = []
    for row in old_components:
        item = dict(row)
        if row["component"] == "Y":
            item["short_value_de"] = "POSTEN"
            item["teaching_rule"] = "name the current work item as POSTEN"
            item["exact_cards"] = "60"
            item["events"] = "124"
        component_rows.append(item)
    by_component = {row["component"]: row for row in component_rows}

    card_rows = []
    y_card_rows = []
    for row in old_cards:
        tokens = row["component_recipe"].split("+")
        reading = " · ".join(by_component[token]["short_value_de"] for token in tokens)
        item = {
            "exact_card_id": row["exact_card_id"],
            "registered_surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "eighth_grammar_reading_de": reading,
            "events": row["events"],
            "card_tier": row["card_tier"],
            "core33_components": row["core33_components"],
            "core33_touch": row["core33_touch"],
            "fully_core33": row["fully_core33"],
            "remainder_components": row["remainder_components"],
        }
        card_rows.append(item)
        if "Y" in tokens:
            y_card_rows.append(
                {
                    "exact_card_id": row["exact_card_id"],
                    "surfaces": row["registered_surfaces"],
                    "component_recipe": row["component_recipe"],
                    "events": row["events"],
                    "old_reading_de": row["seventh_grammar_reading_de"],
                    "new_reading_de": reading,
                }
            )
    by_card = {row["exact_card_id"]: row for row in card_rows}

    event_rows = []
    y_event_rows = []
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in old_events:
        card = by_card[row["exact_card_id"]]
        item = {
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "owner_de": row["owner_de"],
            "exact_card_id": row["exact_card_id"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "eighth_grammar_reading_de": card["eighth_grammar_reading_de"],
            "card_tier": card["card_tier"],
            "core33_touch": card["core33_touch"],
            "fully_core33": card["fully_core33"],
            "form_owner_boundary_status": row["form_owner_boundary_status"],
        }
        event_rows.append(item)
        by_statement[row["statement_id"]].append(item)
        if "Y" in row["component_recipe"].split("+"):
            y_event_rows.append(
                {
                    "event_id": row["event_id"],
                    "page": row["page"],
                    "statement_id": row["statement_id"],
                    "surface": row["surface"],
                    "component_recipe": row["component_recipe"],
                    "old_reading_de": row["seventh_grammar_reading_de"],
                    "new_reading_de": card["eighth_grammar_reading_de"],
                }
            )

    statement_rows = []
    y_statement_rows = []
    for row in old_statements:
        selected = by_statement[row["statement_id"]]
        working = row["working_reading_de"]
        revision = "NONE"
        if row["statement_id"] == "H3-S001":
            working = working.replace("Den Ansatz an der Zielstelle", "Den Posten an der Zielstelle")
            revision = "ANSATZ_TO_POSTEN"
        item = {
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "owner_noun_de": row["owner_noun_de"],
            "events": row["events"],
            "surface_sequence": row["surface_sequence"],
            "component_sequence": row["component_sequence"],
            "eighth_grammar_literal_de": " | ".join(str(event["eighth_grammar_reading_de"]) for event in selected),
            "working_reading_de": working,
            "fully_core33_events": row["fully_core33_events"],
            "remainder_events": row["remainder_events"],
            "revision_sources": row["revision_sources"] + (",PASS831_Y_POSTEN" if revision != "NONE" else ""),
        }
        statement_rows.append(item)
        if any("Y" in str(event["component_recipe"]).split("+") for event in selected):
            y_statement_rows.append(
                {
                    "statement_id": row["statement_id"],
                    "page": row["page"],
                    "record": row["record"],
                    "y_events": sum("Y" in str(event["component_recipe"]).split("+") for event in selected),
                    "posten_tokens": working.lower().count("posten"),
                    "revision": revision,
                    "working_reading_de": working,
                }
            )

    exception_rows = []
    for row in read(EXCEPTIONS):
        item = dict(row)
        item["reading_de"] = by_card[row["exact_card_id"]]["eighth_grammar_reading_de"]
        exception_rows.append(item)

    prediction_rows = []
    changed_predictions = 0
    for row in read(PREDICTIONS):
        tokens = row["component_recipe"].split("+")
        reading = " · ".join(by_component[token]["short_value_de"] for token in tokens)
        changed_predictions += reading != row["reading_de"]
        prediction_rows.append(
            {
                "predicted_surface": row["predicted_surface"],
                "component_recipe": row["component_recipe"],
                "reading_de": reading,
                "sources": row["sources"],
                "attested_on_fixed_pages": row["attested_on_fixed_pages"],
                "use_status": row["use_status"],
                "edition": "EIGHTH_GRAMMAR_RECOMPUTED",
            }
        )
    high_recipe_rows = read(HIGH_RECIPES)
    high_by_recipe = {row["component_recipe"]: row for row in high_recipe_rows}
    active_rows = []
    for row in prediction_rows:
        if row["component_recipe"] not in high_by_recipe:
            continue
        active_rows.append({**row, "recipe_rank": high_by_recipe[row["component_recipe"]]["recipe_rank"], "selection_reason": high_by_recipe[row["component_recipe"]]["selection_reason"]})

    rule_rows = read(RULES)
    for row in rule_rows:
        if row["rule"] == "ENDPOINT":
            row["instruction"] = "Y names current POSTEN; licensed DY closes"

    write("EIGHT_HUNDRED_THIRTY_FIRST_39_COMPONENT_EIGHTH_GRAMMAR.tsv", component_rows, ["component_no", "component", "short_value_de", "grammar_tier", "exact_cards", "events", "teaching_rule"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_173_CARD_EIGHTH_DICTIONARY.tsv", card_rows, ["exact_card_id", "registered_surfaces", "component_recipe", "eighth_grammar_reading_de", "events", "card_tier", "core33_components", "core33_touch", "fully_core33", "remainder_components"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_381_EVENT_REPARSE.tsv", event_rows, ["event_id", "page", "record", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "eighth_grammar_reading_de", "card_tier", "core33_touch", "fully_core33", "form_owner_boundary_status"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_116_STATEMENT_REPARSE.tsv", statement_rows, ["statement_id", "page", "record", "owner_noun_de", "events", "surface_sequence", "component_sequence", "eighth_grammar_literal_de", "working_reading_de", "fully_core33_events", "remainder_events", "revision_sources"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_60_Y_CARDS.tsv", y_card_rows, ["exact_card_id", "surfaces", "component_recipe", "events", "old_reading_de", "new_reading_de"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_124_Y_EVENTS.tsv", y_event_rows, ["event_id", "page", "statement_id", "surface", "component_recipe", "old_reading_de", "new_reading_de"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_60_Y_STATEMENTS.tsv", y_statement_rows, ["statement_id", "page", "record", "y_events", "posten_tokens", "revision", "working_reading_de"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_6_EXCEPTIONS.tsv", exception_rows, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "exception_component", "exception_type", "short_value_de", "learning_rule"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_76_UNATTESTED_PREDICTIONS.tsv", prediction_rows, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_30_ACTIVE_PREDICTION_SURFACES.tsv", active_rows, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition", "recipe_rank", "selection_reason"])
    write("EIGHT_HUNDRED_THIRTY_FIRST_19_TEACHING_RULES.tsv", rule_rows, ["priority", "rule", "instruction"])
    summary = {
        "status": "PASS",
        "decision": "EIGHTH_GRAMMAR_REVISES_Y_FROM_DIES_TO_POSTEN",
        "components": len(component_rows),
        "cards": len(card_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "y_cards": len(y_card_rows),
        "y_events": len(y_event_rows),
        "y_statements": len(y_statement_rows),
        "y_statements_with_posten": sum(int(row["posten_tokens"]) > 0 for row in y_statement_rows),
        "fluent_statement_revisions": sum(row["revision"] != "NONE" for row in y_statement_rows),
        "prediction_rows": len(prediction_rows),
        "changed_predictions": changed_predictions,
        "active_prediction_recipes": len(high_by_recipe),
        "active_prediction_surfaces": len(active_rows),
        "exceptions": len(exception_rows),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_THIRTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
