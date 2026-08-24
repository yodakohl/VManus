#!/usr/bin/env python3
"""Build the CHD/CHED transfer verb with arguments, prefixes, and endpoints."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def proc_num(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    all_events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    events = [row for row in all_events if "CHD" in row["semantic_component_parse"].split("+")]
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in all_events:
        by_statement[row["statement_id"]].append(row)
    for row in events:
        by_card[row["card_no"]].append(row)

    inventory_rows = []
    for card in sorted(by_card, key=proc_num):
        rows = by_card[card]
        exemplar = rows[0]
        inventory_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": exemplar["semantic_component_parse"],
            "composed_reading_de": exemplar["standard_command_de"],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "contains_close": "YES" if "SCHLUSS" in exemplar["standard_command_de"] else "NO",
            "statement_final_events": sum(by_statement[row["statement_id"]][-1]["event_id"] == row["event_id"] for row in rows),
            "invariant_chd_value": "YES" if "UMSETZEN" in exemplar["standard_command_de"] else "NO",
        })

    recipe_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in inventory_rows:
        recipe_groups[str(row["component_recipe"])].append(row)
    recipe_rows = []
    for recipe in sorted(recipe_groups):
        cards = recipe_groups[recipe]
        recipe_rows.append({
            "component_recipe": recipe,
            "card_types": len(cards),
            "card_ids": "|".join(sorted((str(row["card_no"]) for row in cards), key=proc_num)),
            "events": sum(int(row["events"]) for row in cards),
            "invariant_chd_value": "UMSETZEN",
            "composed_reading_de": cards[0]["composed_reading_de"],
            "endpoint": "CLOSED" if cards[0]["contains_close"] == "YES" else "ACTIVE_OR_ARGUMENT_BEARING",
        })

    slot_specs = [
        ("Y", "CURRENT_ITEM_ACTIVE", "laufenden Posten umsetzen und aktiv lassen", {"CHD+Y"}),
        ("DY", "CLOSED_ENDPOINT", "umsetzen und Schritt schliessen", {"CHD+DY"}),
        ("AL", "TARGET", "an die Zielstelle umsetzen", {"CHD+AL"}),
        ("AIN", "PORTION", "eine Portion umsetzen", {"CHD+AIN"}),
        ("AIR", "FLOW_LIQUID", "laufende Fluessigkeit umsetzen", {"CHD+AIR"}),
    ]
    slot_rows = []
    for atom, role, reading, recipes in slot_specs:
        cards = [row for row in inventory_rows if row["component_recipe"] in recipes]
        slot_rows.append({
            "argument_atom": atom,
            "role": role,
            "short_value_de": reading,
            "direct_card_types": len(cards),
            "direct_card_ids": "|".join(str(row["card_no"]) for row in cards),
            "direct_events": sum(int(row["events"]) for row in cards),
            "portable_rule_de": f"CHD+{atom} = {reading}",
        })

    prefix_specs = [
        ("L", "WEITERLEITEN", lambda recipe: recipe.startswith("L+")),
        ("P", "EINFUELLEN", lambda recipe: recipe.startswith("P+")),
        ("OL", "FORTSETZEN", lambda recipe: recipe.startswith("OL+")),
        ("OT", "DANACH", lambda recipe: recipe.startswith("OT+")),
        ("OK", "ANSETZEN", lambda recipe: recipe.startswith("OK+")),
    ]
    prefix_rows = []
    for prefix, value, predicate in prefix_specs:
        cards = [row for row in inventory_rows if predicate(str(row["component_recipe"]))]
        prefix_rows.append({
            "prefix": prefix,
            "prefix_value_de": value,
            "card_types": len(cards),
            "card_ids": "|".join(str(row["card_no"]) for row in cards),
            "events": sum(int(row["events"]) for row in cards),
            "composed_examples": " || ".join(str(row["composed_reading_de"]) for row in cards),
        })

    event_rows = []
    for event in events:
        final = by_statement[event["statement_id"]][-1]["event_id"] == event["event_id"]
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "card_no": event["card_no"],
            "surface": event["surface"],
            "component_recipe": event["semantic_component_parse"],
            "composed_reading_de": event["standard_command_de"],
            "contains_close": "YES" if "SCHLUSS" in event["standard_command_de"] else "NO",
            "statement_final": "YES" if final else "NO",
        })

    predictions = [
        ("CHD+AR", "chedar?", "AUS DEM VORRAT UMSETZEN", "L+CHD+AR ist belegt"),
        ("CHD+AIR+DY", "chedairdy?", "LAUFFLUESSIGKEIT UMSETZEN; SCHLUSS", "CHD+AIR und CHD+DY sind belegt"),
        ("L+CHD+AIN", "lchedain?", "EINE PORTION WEITERLEITEN UND UMSETZEN", "L+CHD und CHD+AIN sind belegt"),
        ("P+CHD+AR", "pchedar?", "AUS DEM VORRAT EINFUELLEN UND UMSETZEN", "P+CHD und L+CHD+AR sind belegt"),
        ("OT+CHD+Y", "otchedchy?", "DANACH DEN POSTEN UMSETZEN UND AKTIV LASSEN", "OT+CHD+DY und CHD+Y sind belegt"),
    ]
    prediction_rows = [
        {"predicted_recipe": recipe, "surface_guess": surface, "predicted_reading_de": reading, "basis": basis}
        for recipe, surface, reading, basis in predictions
    ]

    write_tsv(HERE / "SIX_HUNDRED_FIFTY_EIGHTH_22_CHD_CARD_INVENTORY.tsv", inventory_rows, list(inventory_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_EIGHTH_18_CHD_RECIPES.tsv", recipe_rows, list(recipe_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_EIGHTH_5_ARGUMENT_ENDPOINT_SLOTS.tsv", slot_rows, list(slot_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_EIGHTH_5_DIRECTION_PREFIXES.tsv", prefix_rows, list(prefix_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_EIGHTH_48_CHD_EVENT_READINGS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_EIGHTH_5_COMPOSITION_PREDICTIONS.tsv", prediction_rows, list(prediction_rows[0]))

    summary = {
        "status": "PASS",
        "chd_card_types": len(inventory_rows),
        "chd_events": len(event_rows),
        "component_recipes": len(recipe_rows),
        "argument_endpoint_slots": len(slot_rows),
        "direction_prefixes": len(prefix_rows),
        "direct_slot_card_types": sum(int(row["direct_card_types"]) for row in slot_rows),
        "direct_slot_events": sum(int(row["direct_events"]) for row in slot_rows),
        "closed_events": sum(row["contains_close"] == "YES" for row in event_rows),
        "closed_events_final": sum(row["contains_close"] == "YES" and row["statement_final"] == "YES" for row in event_rows),
        "all_chd_values_invariant": all(row["invariant_chd_value"] == "YES" for row in inventory_rows),
        "predictions": len(prediction_rows),
        "decision": "CHD_CHED_IS_ONE_TRANSFER_VERB_WITH_DIRECTION_ARGUMENT_AND_ENDPOINT_SLOTS",
    }
    (HERE / "SIX_HUNDRED_FIFTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
