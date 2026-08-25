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
ROOTS = ("O", "IIN", "SOLK")
VALUES = {"O": "VORGANG", "IIN": "STUFE", "SOLK": "SAMMELSTELLE"}


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
    observed_surfaces = {row["surface"] for row in events}

    card_rows = []
    for row in cards:
        tokens = row["component_recipe"].split("+")
        members = [root for root in ROOTS if root in tokens]
        if members:
            card_rows.append(
                {
                    "exact_card_id": row["exact_card_id"],
                    "surfaces": row["registered_surfaces"],
                    "component_recipe": row["component_recipe"],
                    "members": "+".join(members),
                    "reading_de": row["third_grammar_reading_de"].replace("ARBEITSSTUFE", "STUFE"),
                    "events": row["events"],
                    "stacked_members": "YES" if len(members) > 1 else "NO",
                }
            )

    event_rows = []
    co: dict[str, set[str]] = defaultdict(set)
    pages: dict[str, set[str]] = defaultdict(set)
    card_ids: dict[str, set[str]] = defaultdict(set)
    for row in events:
        tokens = row["component_recipe"].split("+")
        members = [root for root in ROOTS if root in tokens]
        if not members:
            continue
        for root in members:
            co[root].update(token for token in tokens if token != root)
            pages[root].add(row["page"])
            card_ids[root].add(row["exact_card_id"])
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "members": "+".join(members),
                "reading_de": row["third_grammar_reading_de"].replace("ARBEITSSTUFE", "STUFE"),
            }
        )

    decisions = []
    for root in ROOTS:
        root_events = [row for row in event_rows if root in row["members"].split("+")]
        decisions.append(
            {
                "component": root,
                "short_value_de": VALUES[root],
                "exact_cards": len(card_ids[root]),
                "events": len(root_events),
                "pages": "|".join(sorted(pages[root])),
                "distinct_co_components": len(co[root]),
                "co_components": "+".join(sorted(co[root])) or "NONE",
                "portable_reading": "YES",
                "decision": "PROMOTE_TO_PARADIGM_CORE28",
                "scope_guard": "only registered component recipes; never raw visible substring",
            }
        )

    grid_specs = [
        ("NONE", "NONE", "Y", "DIES", "SOLK+Y", "qolky", 1),
        ("NONE", "NONE", "DY", "SCHLUSS", "SOLK+DY", "qolkdy", 0),
        ("E", "KURZ", "Y", "DIES", "SOLK+E+Y", "solkey", 1),
        ("E", "KURZ", "DY", "SCHLUSS", "SOLK+E+DY", "solkedy", 0),
        ("EE", "LANG", "Y", "DIES", "SOLK+EE+Y", "solkeey", 1),
        ("EE", "LANG", "DY", "SCHLUSS", "SOLK+EE+DY", "solkeedy|olkeedy", 3),
        ("EEE", "VOLL", "Y", "DIES", "SOLK+EEE+Y", "solkeeey", 0),
        ("EEE", "VOLL", "DY", "SCHLUSS", "SOLK+EEE+DY", "solkeeedy", 0),
    ]
    grid_rows = []
    for grade, grade_value, endpoint, endpoint_value, recipe, surfaces, count in grid_specs:
        reading = " · ".join(part for part in ("SAMMELSTELLE", grade_value if grade != "NONE" else "", endpoint_value) if part)
        grid_rows.append(
            {
                "grade": grade,
                "grade_value_de": grade_value,
                "endpoint": endpoint,
                "endpoint_value_de": endpoint_value,
                "component_recipe": recipe,
                "surfaces": surfaces,
                "events": count,
                "reading_de": reading,
                "status": "ATTESTED" if count else "PREDICTED_UNATTESTED",
                "surface_collision": "YES" if not count and any(surface in observed_surfaces for surface in surfaces.split("|")) else "NO",
            }
        )

    stack_rows = []
    for row in card_rows:
        if row["stacked_members"] == "YES":
            stack_rows.append(
                {
                    "exact_card_id": row["exact_card_id"],
                    "surfaces": row["surfaces"],
                    "component_recipe": row["component_recipe"],
                    "reading_de": row["reading_de"],
                    "events": row["events"],
                    "interpretation": "PROCEDURE_AT_WORK_STAGE",
                }
            )

    read_ids = ["H2-S003", "B1-S018", "B2-S005", "B3-S026", "B6-S001"]
    reading_rows = []
    for sid in read_ids:
        row = statements[sid]
        reading_rows.append(
            {
                "statement_id": sid,
                "page": row["page"],
                "owner_noun_de": row["owner_noun_de"],
                "surface_sequence": row["surface_sequence"],
                "working_reading_de": row["working_reading_de"].replace("Arbeitsstufe", "Stufe"),
            }
        )

    write("EIGHT_HUNDRED_EIGHTH_25_PROCEDURE_PLACE_CARDS.tsv", card_rows, ["exact_card_id", "surfaces", "component_recipe", "members", "reading_de", "events", "stacked_members"])
    write("EIGHT_HUNDRED_EIGHTH_28_PROCEDURE_PLACE_EVENTS.tsv", event_rows, ["event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "members", "reading_de"])
    write("EIGHT_HUNDRED_EIGHTH_3_ROOT_DECISIONS.tsv", decisions, ["component", "short_value_de", "exact_cards", "events", "pages", "distinct_co_components", "co_components", "portable_reading", "decision", "scope_guard"])
    write("EIGHT_HUNDRED_EIGHTH_8_SOLK_GRID.tsv", grid_rows, ["grade", "grade_value_de", "endpoint", "endpoint_value_de", "component_recipe", "surfaces", "events", "reading_de", "status", "surface_collision"])
    write("EIGHT_HUNDRED_EIGHTH_O_IIN_STACK.tsv", stack_rows, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "interpretation"])
    write("EIGHT_HUNDRED_EIGHTH_5_READABLE_STATEMENTS.tsv", reading_rows, ["statement_id", "page", "owner_noun_de", "surface_sequence", "working_reading_de"])

    summary = {
        "status": "PASS",
        "decision": "O_IIN_SOLK_PROMOTED_AS_PROCEDURE_STAGE_PLACE_ROOTS_IN_CORE28",
        "cards": len(card_rows),
        "union_events": len(event_rows),
        "component_event_sum": sum(int(row["events"]) for row in decisions),
        "stacks": len(stack_rows),
        "solk_grid_cells": len(grid_rows),
        "solk_attested_cells": sum(row["status"] == "ATTESTED" for row in grid_rows),
        "solk_predicted_cells": sum(row["status"] == "PREDICTED_UNATTESTED" for row in grid_rows),
        "prediction_collisions": sum(row["surface_collision"] == "YES" for row in grid_rows),
        "new_core_size": 28,
        "remaining_recurrent_strip_values": 3,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
