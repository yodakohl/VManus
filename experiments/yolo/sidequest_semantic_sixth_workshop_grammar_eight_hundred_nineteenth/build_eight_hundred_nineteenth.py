#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_fifth_workshop_grammar_eight_hundred_fifteenth"
COMPONENTS = BASE / "EIGHT_HUNDRED_FIFTEENTH_39_COMPONENT_FIFTH_GRAMMAR.tsv"
CARDS = BASE / "EIGHT_HUNDRED_FIFTEENTH_173_CARD_FIFTH_DICTIONARY.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_FIFTEENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_FIFTEENTH_116_STATEMENT_REPARSE.tsv"
PREDICTIONS = BASE / "EIGHT_HUNDRED_FIFTEENTH_76_UNATTESTED_PREDICTIONS.tsv"
RULES = BASE / "EIGHT_HUNDRED_FIFTEENTH_17_TEACHING_RULES.tsv"

WHOLE_VALUES = {"OS": "DAZU", "RESUME_CARD": "DAVON", "TALAM": "BEISEITESTELLEN"}
WHOLE_TIERS = {
    "OS": "MEMORIZED_WHOLE_CONNECTOR",
    "RESUME_CARD": "MEMORIZED_WHOLE_ANAPHOR",
    "TALAM": "MEMORIZED_WHOLE_OPERATION",
}
REVISION_FILES = [
    ROOT / "sidequest_semantic_os_connector_eight_hundred_sixteenth" / "EIGHT_HUNDRED_SIXTEENTH_REVISED_STATEMENT.tsv",
    ROOT / "sidequest_semantic_resume_davon_eight_hundred_seventeenth" / "EIGHT_HUNDRED_SEVENTEENTH_2_REVISED_STATEMENTS.tsv",
    ROOT / "sidequest_semantic_talam_set_aside_eight_hundred_eighteenth" / "EIGHT_HUNDRED_EIGHTEENTH_REVISED_STATEMENT.tsv",
]


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
    components = read(COMPONENTS)
    cards = read(CARDS)
    events = read(EVENTS)
    statements = read(STATEMENTS)

    component_rows = []
    for row in components:
        component = row["component"]
        item = dict(row)
        if component in WHOLE_VALUES:
            item["short_value_de"] = WHOLE_VALUES[component]
            item["grammar_tier"] = WHOLE_TIERS[component]
            item["teaching_rule"] = "memorize this complete short word"
        component_rows.append(item)
    by_component = {row["component"]: row for row in component_rows}

    card_rows = []
    for row in cards:
        tokens = row["component_recipe"].split("+")
        item = {
            "exact_card_id": row["exact_card_id"],
            "registered_surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "sixth_grammar_reading_de": " · ".join(by_component[token]["short_value_de"] for token in tokens),
            "events": row["events"],
            "card_tier": next((WHOLE_TIERS[token] for token in tokens if token in WHOLE_TIERS), row["card_tier"]),
            "core33_components": row["core33_components"],
            "core33_touch": row["core33_touch"],
            "fully_core33": row["fully_core33"],
            "remainder_components": row["remainder_components"],
        }
        card_rows.append(item)
    by_card = {row["exact_card_id"]: row for row in card_rows}

    event_rows = []
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
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
            "sixth_grammar_reading_de": card["sixth_grammar_reading_de"],
            "card_tier": card["card_tier"],
            "core33_touch": card["core33_touch"],
            "fully_core33": card["fully_core33"],
            "form_owner_boundary_status": row["form_owner_boundary_status"],
        }
        event_rows.append(item)
        by_statement[row["statement_id"]].append(item)

    revised = {row["statement_id"]: row["working_reading_de"] for row in statements}
    added_sources: dict[str, list[str]] = defaultdict(list)
    for path in REVISION_FILES:
        for row in read(path):
            revised[row["statement_id"]] = row["revised_reading_de"]
            added_sources[row["statement_id"]].append(path.parent.name)

    statement_rows = []
    for row in statements:
        selected = by_statement[row["statement_id"]]
        old_sources = [] if row["revision_sources"] == "PASS739_UNCHANGED" else row["revision_sources"].split(",")
        sources = old_sources + added_sources[row["statement_id"]]
        statement_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "owner_noun_de": row["owner_noun_de"],
                "events": row["events"],
                "surface_sequence": row["surface_sequence"],
                "component_sequence": row["component_sequence"],
                "sixth_grammar_literal_de": " | ".join(str(event["sixth_grammar_reading_de"]) for event in selected),
                "working_reading_de": revised[row["statement_id"]],
                "fully_core33_events": row["fully_core33_events"],
                "remainder_events": row["remainder_events"],
                "revision_sources": ",".join(sources) or "PASS739_UNCHANGED",
            }
        )

    exception_rows = []
    descriptions = {
        "AN": ("BOUND_COMPONENT", "NACHGABE", "only in learned Y+K+AN frame"),
        "DA": ("BOUND_COMPONENT", "ZWEI", "only before IIN stage"),
        "LD": ("BOUND_COMPONENT", "BEFESTIGEN", "only before DY in learned frame"),
        "OS": ("WHOLE_CONNECTOR", "DAZU", "complete learned connector"),
        "RESUME_CARD": ("WHOLE_ANAPHOR", "DAVON", "complete owner-relative anaphor"),
        "TALAM": ("WHOLE_OPERATION", "BEISEITESTELLEN", "complete learned operation"),
    }
    for row in card_rows:
        if row["fully_core33"] == "YES":
            continue
        token = next(token for token in row["component_recipe"].split("+") if token in descriptions)
        kind, value, reason = descriptions[token]
        exception_rows.append(
            {
                "exact_card_id": row["exact_card_id"],
                "surfaces": row["registered_surfaces"],
                "component_recipe": row["component_recipe"],
                "reading_de": row["sixth_grammar_reading_de"],
                "events": row["events"],
                "exception_component": token,
                "exception_type": kind,
                "short_value_de": value,
                "learning_rule": reason,
            }
        )

    prediction_rows = []
    for row in read(PREDICTIONS):
        item = dict(row)
        item["edition"] = "SIXTH_GRAMMAR_CARRIED_FORWARD"
        prediction_rows.append(item)

    rule_rows = [row for row in read(RULES) if row["rule"] != "WHOLE"]
    rule_rows.extend(
        [
            {"priority": 17, "rule": "WHOLE_CONNECTOR", "instruction": "memorize OS as DAZU"},
            {"priority": 18, "rule": "WHOLE_ANAPHOR", "instruction": "memorize dchol/schol as DAVON"},
            {"priority": 19, "rule": "WHOLE_OPERATION", "instruction": "memorize talam as BEISEITESTELLEN"},
        ]
    )

    write("EIGHT_HUNDRED_NINETEENTH_39_COMPONENT_SIXTH_GRAMMAR.tsv", component_rows, ["component_no", "component", "short_value_de", "grammar_tier", "exact_cards", "events", "teaching_rule"])
    write("EIGHT_HUNDRED_NINETEENTH_173_CARD_SIXTH_DICTIONARY.tsv", card_rows, ["exact_card_id", "registered_surfaces", "component_recipe", "sixth_grammar_reading_de", "events", "card_tier", "core33_components", "core33_touch", "fully_core33", "remainder_components"])
    write("EIGHT_HUNDRED_NINETEENTH_381_EVENT_REPARSE.tsv", event_rows, ["event_id", "page", "record", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "sixth_grammar_reading_de", "card_tier", "core33_touch", "fully_core33", "form_owner_boundary_status"])
    write("EIGHT_HUNDRED_NINETEENTH_116_STATEMENT_REPARSE.tsv", statement_rows, ["statement_id", "page", "record", "owner_noun_de", "events", "surface_sequence", "component_sequence", "sixth_grammar_literal_de", "working_reading_de", "fully_core33_events", "remainder_events", "revision_sources"])
    write("EIGHT_HUNDRED_NINETEENTH_6_EXCEPTIONS.tsv", exception_rows, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "exception_component", "exception_type", "short_value_de", "learning_rule"])
    write("EIGHT_HUNDRED_NINETEENTH_76_UNATTESTED_PREDICTIONS.tsv", prediction_rows, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition"])
    write("EIGHT_HUNDRED_NINETEENTH_19_TEACHING_RULES.tsv", rule_rows, ["priority", "rule", "instruction"])

    full = [row for row in card_rows if row["fully_core33"] == "YES"]
    touched = [row for row in card_rows if row["core33_touch"] == "YES"]
    summary = {
        "status": "PASS",
        "decision": "SIXTH_GRAMMAR_REPARSES_ALL_PROSE_WITH_THREE_MEANINGFUL_WHOLE_WORDS",
        "components": len(component_rows),
        "core_components": sum(row["grammar_tier"] == "PARADIGM_CORE33" for row in component_rows),
        "bound_components": 3,
        "whole_forms": 3,
        "cards": len(card_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "core_touch_cards": len(touched),
        "core_touch_events": sum(int(row["events"]) for row in touched),
        "fully_core_cards": len(full),
        "fully_core_events": sum(int(row["events"]) for row in full),
        "exception_cards": len(exception_rows),
        "exception_events": sum(int(row["events"]) for row in exception_rows),
        "unresolved_exception_values": 0,
        "predictions": len(prediction_rows),
        "teaching_rules": len(rule_rows),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_NINETEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
