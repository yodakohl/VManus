#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_sixth_workshop_grammar_eight_hundred_nineteenth"
COMPONENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_39_COMPONENT_SIXTH_GRAMMAR.tsv"
CARDS = BASE / "EIGHT_HUNDRED_NINETEENTH_173_CARD_SIXTH_DICTIONARY.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_116_STATEMENT_REPARSE.tsv"
EXCEPTIONS = BASE / "EIGHT_HUNDRED_NINETEENTH_6_EXCEPTIONS.tsv"
PREDICTIONS = BASE / "EIGHT_HUNDRED_NINETEENTH_76_UNATTESTED_PREDICTIONS.tsv"
RULES = BASE / "EIGHT_HUNDRED_NINETEENTH_19_TEACHING_RULES.tsv"
REVISIONS = [
    ROOT / "sidequest_semantic_t_work_eight_hundred_twenty_first" / "EIGHT_HUNDRED_TWENTY_FIRST_7_REVISED_STATEMENTS.tsv",
    ROOT / "sidequest_semantic_p_bring_in_eight_hundred_twenty_second" / "EIGHT_HUNDRED_TWENTY_SECOND_3_REVISED_STATEMENTS.tsv",
    ROOT / "sidequest_semantic_solk_collect_eight_hundred_twenty_sixth" / "EIGHT_HUNDRED_TWENTY_SIXTH_7_REVISED_STATEMENTS.tsv",
]
NEW_VALUES = {"T": "BEARBEITEN", "P": "EINBRINGEN", "SOLK": "SAMMELN"}


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
        if row["component"] in NEW_VALUES:
            item["short_value_de"] = NEW_VALUES[row["component"]]
            item["teaching_rule"] = "compose freely with revised concrete workshop value"
        component_rows.append(item)
    by_component = {row["component"]: row for row in component_rows}

    card_rows = []
    changed_cards = []
    for row in old_cards:
        tokens = row["component_recipe"].split("+")
        reading = " · ".join(by_component[token]["short_value_de"] for token in tokens)
        item = {
            "exact_card_id": row["exact_card_id"],
            "registered_surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "seventh_grammar_reading_de": reading,
            "events": row["events"],
            "card_tier": row["card_tier"],
            "core33_components": row["core33_components"],
            "core33_touch": row["core33_touch"],
            "fully_core33": row["fully_core33"],
            "remainder_components": row["remainder_components"],
        }
        card_rows.append(item)
        if reading != row["sixth_grammar_reading_de"]:
            changed_cards.append(
                {
                    "exact_card_id": row["exact_card_id"],
                    "surfaces": row["registered_surfaces"],
                    "component_recipe": row["component_recipe"],
                    "events": row["events"],
                    "old_reading_de": row["sixth_grammar_reading_de"],
                    "new_reading_de": reading,
                    "changed_components": "+".join(token for token in tokens if token in NEW_VALUES),
                }
            )
    by_card = {row["exact_card_id"]: row for row in card_rows}

    event_rows = []
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
            "seventh_grammar_reading_de": card["seventh_grammar_reading_de"],
            "card_tier": card["card_tier"],
            "core33_touch": card["core33_touch"],
            "fully_core33": card["fully_core33"],
            "form_owner_boundary_status": row["form_owner_boundary_status"],
        }
        event_rows.append(item)
        by_statement[row["statement_id"]].append(item)

    revised = {row["statement_id"]: row["working_reading_de"] for row in old_statements}
    sources: dict[str, list[str]] = defaultdict(list)
    for path in REVISIONS:
        for row in read(path):
            revised[row["statement_id"]] = row["revised_reading_de"]
            sources[row["statement_id"]].append(path.parent.name)
    statement_rows = []
    for row in old_statements:
        selected = by_statement[row["statement_id"]]
        old_sources = [] if row["revision_sources"] == "PASS739_UNCHANGED" else row["revision_sources"].split(",")
        statement_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "owner_noun_de": row["owner_noun_de"],
                "events": row["events"],
                "surface_sequence": row["surface_sequence"],
                "component_sequence": row["component_sequence"],
                "seventh_grammar_literal_de": " | ".join(str(event["seventh_grammar_reading_de"]) for event in selected),
                "working_reading_de": revised[row["statement_id"]],
                "fully_core33_events": row["fully_core33_events"],
                "remainder_events": row["remainder_events"],
                "revision_sources": ",".join(old_sources + sources[row["statement_id"]]) or "PASS739_UNCHANGED",
            }
        )

    exception_rows = []
    for row in read(EXCEPTIONS):
        item = dict(row)
        card = by_card[row["exact_card_id"]]
        item["reading_de"] = card["seventh_grammar_reading_de"]
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
                "edition": "SEVENTH_GRAMMAR_RECOMPUTED",
            }
        )

    rule_rows = read(RULES)
    for row in rule_rows:
        if row["rule"] == "ACTION":
            row["instruction"] = "CH take; SH hold; CTH prepare; T work"
        elif row["rule"] == "TRANSFER":
            row["instruction"] = "K add; L guide; CHD transfer; P bring inward"
        elif row["rule"] == "PROCESS":
            row["instruction"] = "CHK warm; SHED leave standing; LSH rinse; R cool; CFH press out; SOLK collect"
        elif row["rule"] == "PATH_PLACE":
            row["instruction"] = "CKH passage; O procedure"

    write("EIGHT_HUNDRED_TWENTY_SEVENTH_39_COMPONENT_SEVENTH_GRAMMAR.tsv", component_rows, ["component_no", "component", "short_value_de", "grammar_tier", "exact_cards", "events", "teaching_rule"])
    write("EIGHT_HUNDRED_TWENTY_SEVENTH_173_CARD_SEVENTH_DICTIONARY.tsv", card_rows, ["exact_card_id", "registered_surfaces", "component_recipe", "seventh_grammar_reading_de", "events", "card_tier", "core33_components", "core33_touch", "fully_core33", "remainder_components"])
    write("EIGHT_HUNDRED_TWENTY_SEVENTH_381_EVENT_REPARSE.tsv", event_rows, ["event_id", "page", "record", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "seventh_grammar_reading_de", "card_tier", "core33_touch", "fully_core33", "form_owner_boundary_status"])
    write("EIGHT_HUNDRED_TWENTY_SEVENTH_116_STATEMENT_REPARSE.tsv", statement_rows, ["statement_id", "page", "record", "owner_noun_de", "events", "surface_sequence", "component_sequence", "seventh_grammar_literal_de", "working_reading_de", "fully_core33_events", "remainder_events", "revision_sources"])
    write("EIGHT_HUNDRED_TWENTY_SEVENTH_17_CHANGED_CARDS.tsv", changed_cards, ["exact_card_id", "surfaces", "component_recipe", "events", "old_reading_de", "new_reading_de", "changed_components"])
    write("EIGHT_HUNDRED_TWENTY_SEVENTH_6_EXCEPTIONS.tsv", exception_rows, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "exception_component", "exception_type", "short_value_de", "learning_rule"])
    write("EIGHT_HUNDRED_TWENTY_SEVENTH_76_UNATTESTED_PREDICTIONS.tsv", prediction_rows, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition"])
    write("EIGHT_HUNDRED_TWENTY_SEVENTH_19_TEACHING_RULES.tsv", rule_rows, ["priority", "rule", "instruction"])

    changed_event_ids = {row["event_id"] for row in event_rows if by_card[row["exact_card_id"]]["exact_card_id"] in {item["exact_card_id"] for item in changed_cards}}
    summary = {
        "status": "PASS",
        "decision": "SEVENTH_GRAMMAR_INTEGRATES_WORK_BRING_IN_AND_COLLECT",
        "components": len(component_rows),
        "cards": len(card_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "changed_components": sorted(NEW_VALUES),
        "changed_cards": len(changed_cards),
        "changed_events": len(changed_event_ids),
        "changed_statements": len({row["statement_id"] for row in event_rows if row["event_id"] in changed_event_ids}),
        "exceptions": len(exception_rows),
        "predictions": len(prediction_rows),
        "changed_predictions": changed_predictions,
        "teaching_rules": len(rule_rows),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
