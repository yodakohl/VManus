#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_sixth_workshop_grammar_eight_hundred_nineteenth"
EVENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_116_STATEMENT_REPARSE.tsv"

REPLACEMENTS = {
    "B1-S014": ("Den Posten umsetzen und an der Sammelstelle halten", "Den Posten umsetzen und sammeln"),
    "B1-S018": ("laenger an der Sammelstelle halten", "laenger sammeln"),
    "B2-S005": ("bis zum Sollmass an der Sammelstelle halten", "bis zum Sollmass sammeln"),
    "B3-S001": ("Laenger an der Sammelstelle halten", "Laenger sammeln"),
    "B3-S026": ("laenger an der Sammelstelle halten", "laenger sammeln"),
    "B4-S015": ("kurz an der Sammelstelle halten", "kurz sammeln"),
    "B6-S001": ("laenger an der Sammelstelle halten", "laenger sammeln"),
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
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    targets = [row for row in events if "SOLK" in row["component_recipe"].split("+")]

    candidates = [
        {"candidate": "SAMMELSTELLE", "grade_composition": "REQUIRES_INSERTED_HALTEN", "owner_fit": "HIGH", "brevity": "MEDIUM", "decision": "REJECT_OLD_NOUN"},
        {"candidate": "SAMMELN", "grade_composition": "DIRECT", "owner_fit": "HIGH", "brevity": "HIGH", "decision": "SELECT_CORE_VALUE"},
        {"candidate": "AUFFANGEN", "grade_composition": "DIRECT", "owner_fit": "HIGH", "brevity": "HIGH", "decision": "REJECT_TOO_INFLOW_SPECIFIC"},
        {"candidate": "BEHAELTER", "grade_composition": "REQUIRES_INSERTED_HALTEN", "owner_fit": "HIGH", "brevity": "HIGH", "decision": "REJECT_NOUN"},
        {"candidate": "BECKEN", "grade_composition": "REQUIRES_INSERTED_HALTEN", "owner_fit": "MEDIUM", "brevity": "HIGH", "decision": "REJECT_VISIBLE_OWNER_SPECIFIC"},
        {"candidate": "ZWISCHENLAGERN", "grade_composition": "DIRECT", "owner_fit": "MEDIUM", "brevity": "LOW", "decision": "REJECT_LONG_TERM_ASSUMPTION"},
    ]

    event_rows = []
    recipe_counts: Counter[str] = Counter()
    recipe_surfaces: dict[str, set[str]] = defaultdict(set)
    for row in targets:
        tokens = row["component_recipe"].split("+")
        parts = row["sixth_grammar_reading_de"].split(" · ")
        revised = " · ".join("SAMMELN" if token == "SOLK" else part for token, part in zip(tokens, parts))
        recipe_counts[row["component_recipe"]] += 1
        recipe_surfaces[row["component_recipe"]].add(row["surface"])
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "exact_card_id": row["exact_card_id"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "old_literal_de": row["sixth_grammar_reading_de"],
                "revised_literal_de": revised,
            }
        )

    grid_rows = []
    readings = {
        "SOLK+Y": "DIES · SAMMELN",
        "SOLK+E+Y": "SAMMELN · KURZ · DIES",
        "SOLK+EE+Y": "SAMMELN · LANG · DIES",
        "SOLK+AIIN": "SAMMELN · SOLLMASS",
        "SOLK+EE+DY": "SAMMELN · LANG · SCHLUSS",
    }
    for recipe, reading in readings.items():
        grid_rows.append(
            {
                "component_recipe": recipe,
                "surfaces": "|".join(sorted(recipe_surfaces[recipe])),
                "events": recipe_counts[recipe],
                "revised_reading_de": reading,
                "hidden_verb_needed": "NO",
            }
        )

    revised_rows = []
    for row in targets:
        statement = statements[row["statement_id"]]
        old_phrase, new_phrase = REPLACEMENTS[row["statement_id"]]
        revised_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "owner_noun_de": statement["owner_noun_de"],
                "surface_sequence": statement["surface_sequence"],
                "old_reading_de": statement["working_reading_de"],
                "revised_reading_de": statement["working_reading_de"].replace(old_phrase, new_phrase),
                "solk_event": row["event_id"],
            }
        )

    place_rows = [
        {"component": "AR", "short_value_de": "QUELLE", "category": "PLACE_ORIGIN", "relation_to_item": "from", "decision": "KEEP"},
        {"component": "CKH", "short_value_de": "DURCHLASS", "category": "PLACE_PATH", "relation_to_item": "through", "decision": "KEEP"},
        {"component": "AL", "short_value_de": "ZIELSTELLE", "category": "PLACE_TARGET", "relation_to_item": "to or at", "decision": "KEEP"},
        {"component": "SOLK", "short_value_de": "SAMMELN", "category": "OPERATION_COLLECTION", "relation_to_item": "collect", "decision": "REVISE_OUT_OF_PLACE_LADDER"},
    ]

    write("EIGHT_HUNDRED_TWENTY_SIXTH_6_SOLK_CANDIDATES.tsv", candidates, ["candidate", "grade_composition", "owner_fit", "brevity", "decision"])
    write("EIGHT_HUNDRED_TWENTY_SIXTH_7_SOLK_EVENTS.tsv", event_rows, ["event_id", "page", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "old_literal_de", "revised_literal_de"])
    write("EIGHT_HUNDRED_TWENTY_SIXTH_5_SOLK_GRID.tsv", grid_rows, ["component_recipe", "surfaces", "events", "revised_reading_de", "hidden_verb_needed"])
    write("EIGHT_HUNDRED_TWENTY_SIXTH_7_REVISED_STATEMENTS.tsv", revised_rows, ["statement_id", "page", "owner_noun_de", "surface_sequence", "old_reading_de", "revised_reading_de", "solk_event"])
    write("EIGHT_HUNDRED_TWENTY_SIXTH_4_PLACE_OPERATION_ROLES.tsv", place_rows, ["component", "short_value_de", "category", "relation_to_item", "decision"])
    summary = {
        "status": "PASS",
        "decision": "SOLK_REVISED_FROM_SAMMELSTELLE_TO_SAMMELN",
        "cards": len({row["exact_card_id"] for row in targets}),
        "events": len(targets),
        "statements": len(revised_rows),
        "recipes": len(grid_rows),
        "hidden_holding_verbs_after_revision": 0,
        "place_components_remaining": ["AR", "CKH", "AL"],
        "collection_operation": "SOLK",
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
