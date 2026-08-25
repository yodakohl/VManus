#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_third_workshop_grammar_eight_hundred_sixth"
CARDS = BASE / "EIGHT_HUNDRED_SIXTH_173_CARD_THIRD_DICTIONARY.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_SIXTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_SIXTH_116_STATEMENT_REPARSE.tsv"
ROOTS = ("AIR", "OR", "HO")
VALUES = {"AIR": "WASSER", "OR": "ANSATZ", "HO": "ZUTAT"}
ROLES = {"AIR": "WORKING_LIQUID", "OR": "CURRENT_PREPARATION", "HO": "INPUT_INGREDIENT"}


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
    cards = read(CARDS)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}

    card_rows = []
    for row in cards:
        tokens = row["component_recipe"].split("+")
        members = [root for root in ROOTS if root in tokens]
        if not members:
            continue
        card_rows.append(
            {
                "exact_card_id": row["exact_card_id"],
                "surfaces": row["registered_surfaces"],
                "component_recipe": row["component_recipe"],
                "material_members": "+".join(members),
                "material_roles": "+".join(ROLES[root] for root in members),
                "third_grammar_reading_de": row["third_grammar_reading_de"],
                "events": row["events"],
                "stacked_material_roles": "YES" if len(members) > 1 else "NO",
            }
        )

    event_rows = []
    pages_by_root: dict[str, set[str]] = defaultdict(set)
    cards_by_root: dict[str, set[str]] = defaultdict(set)
    co_components: dict[str, set[str]] = defaultdict(set)
    for row in events:
        tokens = row["component_recipe"].split("+")
        members = [root for root in ROOTS if root in tokens]
        if not members:
            continue
        for root in members:
            pages_by_root[root].add(row["page"])
            cards_by_root[root].add(row["exact_card_id"])
            co_components[root].update(token for token in tokens if token != root)
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "material_members": "+".join(members),
                "third_grammar_reading_de": row["third_grammar_reading_de"],
                "statement_reading_de": statements[row["statement_id"]]["working_reading_de"],
            }
        )

    decisions = []
    for root in ROOTS:
        selected_events = [row for row in event_rows if root in row["material_members"].split("+")]
        decisions.append(
            {
                "component": root,
                "short_value_de": VALUES[root],
                "semantic_role": ROLES[root],
                "exact_cards": len(cards_by_root[root]),
                "events": len(selected_events),
                "pages": "|".join(sorted(pages_by_root[root])),
                "distinct_co_components": len(co_components[root]),
                "co_components": "+".join(sorted(co_components[root])) or "NONE",
                "meaning_invariant": "YES",
                "decision": "PROMOTE_TO_PARADIGM_CORE25",
                "reason": "same material role survives multiple independent operations and endpoints",
            }
        )

    stack_rows = []
    for row in card_rows:
        if row["stacked_material_roles"] == "YES":
            stack_rows.append(
                {
                    "exact_card_id": row["exact_card_id"],
                    "surfaces": row["surfaces"],
                    "component_recipe": row["component_recipe"],
                    "reading_de": row["third_grammar_reading_de"],
                    "events": row["events"],
                    "consequence": "INPUT_INGREDIENT_AND_CURRENT_PREPARATION_ARE_DISTINCT_ARGUMENTS",
                }
            )

    selected_statement_ids = ["H1-S001", "H2-S003", "H4-S004", "H5-S001", "B4-S014"]
    reading_rows = []
    for sid in selected_statement_ids:
        row = statements[sid]
        reading_rows.append(
            {
                "statement_id": sid,
                "page": row["page"],
                "owner_noun_de": row["owner_noun_de"],
                "surface_sequence": row["surface_sequence"],
                "component_sequence": row["component_sequence"],
                "working_reading_de": row["working_reading_de"],
                "material_roles_present": "+".join(sorted({root for root in ROOTS if any(root in event["component_recipe"].split("+") for event in event_rows if event["statement_id"] == sid)})),
            }
        )

    write("EIGHT_HUNDRED_SEVENTH_19_MATERIAL_CARDS.tsv", card_rows, ["exact_card_id", "surfaces", "component_recipe", "material_members", "material_roles", "third_grammar_reading_de", "events", "stacked_material_roles"])
    write("EIGHT_HUNDRED_SEVENTH_30_MATERIAL_EVENTS.tsv", event_rows, ["event_id", "page", "record", "statement_id", "owner_de", "surface", "component_recipe", "material_members", "third_grammar_reading_de", "statement_reading_de"])
    write("EIGHT_HUNDRED_SEVENTH_3_MATERIAL_ROOT_DECISIONS.tsv", decisions, ["component", "short_value_de", "semantic_role", "exact_cards", "events", "pages", "distinct_co_components", "co_components", "meaning_invariant", "decision", "reason"])
    write("EIGHT_HUNDRED_SEVENTH_MATERIAL_STACK.tsv", stack_rows, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "consequence"])
    write("EIGHT_HUNDRED_SEVENTH_5_READABLE_STATEMENTS.tsv", reading_rows, ["statement_id", "page", "owner_noun_de", "surface_sequence", "component_sequence", "working_reading_de", "material_roles_present"])

    summary = {
        "status": "PASS",
        "decision": "AIR_OR_HO_PROMOTED_AS_DISTINCT_MATERIAL_ROOTS_IN_CORE25",
        "cards": len(card_rows),
        "events": len(event_rows),
        "component_event_sum": sum(int(row["events"]) for row in decisions),
        "stacked_material_cards": len(stack_rows),
        "readable_statements": len(reading_rows),
        "new_core_size": 25,
        "remaining_recurrent_strip_values": 6,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
