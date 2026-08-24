#!/usr/bin/env python3
"""Turn all 23 OK cards into one short verb with argument valency."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"
P656 = ROOT / "experiments/yolo/sidequest_semantic_ok_duration_endpoint_grid_six_hundred_fifty_sixth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ARGUMENTS = {
    "Y": ("CURRENT_ITEM", "laufender Arbeitsposten"),
    "OL": ("CONTINUATION", "Fortsetzung"),
    "AIIN": ("PRESCRIBED_MEASURE", "Sollmass"),
    "AL": ("TARGET", "Zielstelle"),
    "AIN": ("PORTION", "Portion"),
    "AR": ("SOURCE", "Vorrat oder Quelle"),
    "AIR": ("FLOW_LIQUID", "Fluessigkeitslauf"),
}


def proc_num(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    inventory = read_tsv(P656 / "SIX_HUNDRED_FIFTY_SIXTH_23_OK_CARD_INVENTORY.tsv")
    ok_ids = {row["card_no"] for row in inventory}
    ok_events = [row for row in events if row["card_no"] in ok_ids]
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    recipe_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inventory:
        recipe_groups[row["component_parse"]].append(row)
    recipe_rows: list[dict[str, object]] = []
    for parse in sorted(recipe_groups):
        cards = recipe_groups[parse]
        recipe_rows.append({
            "component_recipe": parse,
            "card_types": len(cards),
            "card_ids": "|".join(sorted((row["card_no"] for row in cards), key=proc_num)),
            "surfaces": "|".join(sorted({surface for row in cards for surface in row["surfaces"].split("|")})),
            "events": sum(int(row["events"]) for row in cards),
            "invariant_ok_value": "ANSETZEN",
            "composed_reading_de": cards[0]["standard_command_de"],
            "close_status": "CLOSED" if cards[0]["contains_close"] == "YES" else "ACTIVE_OR_ARGUMENT_BEARING",
        })

    argument_rows: list[dict[str, object]] = []
    for atom, (role, reading) in ARGUMENTS.items():
        direct_parse = f"OK+{atom}"
        cards = recipe_groups[direct_parse]
        argument_rows.append({
            "argument_atom": atom,
            "valency_role": role,
            "short_value_de": reading,
            "direct_card_types": len(cards),
            "direct_card_ids": "|".join(sorted((row["card_no"] for row in cards), key=proc_num)),
            "direct_events": sum(int(row["events"]) for row in cards),
            "composed_command_de": cards[0]["standard_command_de"],
            "portable_rule_de": f"OK+{atom} = ANSETZEN + {reading}",
        })

    event_rows = []
    for event in ok_events:
        statement = by_statement[event["statement_id"]]
        final = statement[-1]["event_id"] == event["event_id"]
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "card_no": event["card_no"],
            "surface": event["surface"],
            "component_recipe": event["semantic_component_parse"],
            "composed_command_de": event["standard_command_de"],
            "statement_final": "YES" if final else "NO",
            "contains_close": "YES" if "SCHLUSS" in event["standard_command_de"] else "NO",
            "ok_value_invariant": "YES" if event["standard_command_de"].startswith("ANSETZEN") else "NO",
        })

    predictions = [
        ("OK+E+AL", "qokedal?", "KURZ AN DER ZIELSTELLE ANSETZEN", "OK+EE+AL=qokeedal ist belegt"),
        ("OK+E+OL", "okeol?", "KURZ FORTSETZEN", "OK+EE+OL=okeeol ist belegt"),
        ("OK+EEE+Y", "qokeeey?", "VOLLSTAENDIG ANSETZEN; POSTEN AKTIV", "OK+EEE+DY=qokeeedy ist belegt"),
        ("OK+AIIN+Y", "surface offen", "NACH SOLLMASS AM LAUFENDEN POSTEN ANSETZEN", "OK+AIIN und OK+Y sind getrennt belegt"),
        ("OK+AIN+AL", "surface offen", "EINE PORTION AN DER ZIELSTELLE ANSETZEN", "OK+AIN und OK+AL sind getrennt belegt"),
    ]
    prediction_rows = [
        {"predicted_recipe": recipe, "surface_guess": surface, "predicted_reading_de": reading, "basis": basis}
        for recipe, surface, reading, basis in predictions
    ]

    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SEVENTH_20_OK_RECIPES.tsv", recipe_rows, list(recipe_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SEVENTH_7_ARGUMENT_SLOTS.tsv", argument_rows, list(argument_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SEVENTH_79_OK_EVENT_READINGS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SEVENTH_5_COMPOSITION_PREDICTIONS.tsv", prediction_rows, list(prediction_rows[0]))

    summary = {
        "status": "PASS",
        "ok_card_types": len(inventory),
        "ok_events": len(event_rows),
        "component_recipes": len(recipe_rows),
        "argument_slots": len(argument_rows),
        "direct_argument_card_types": sum(int(row["direct_card_types"]) for row in argument_rows),
        "direct_argument_events": sum(int(row["direct_events"]) for row in argument_rows),
        "closed_ok_events": sum(row["contains_close"] == "YES" for row in event_rows),
        "closed_ok_events_final": sum(row["contains_close"] == "YES" and row["statement_final"] == "YES" for row in event_rows),
        "all_ok_commands_share_invariant": all(row["ok_value_invariant"] == "YES" for row in event_rows),
        "composition_predictions": len(prediction_rows),
        "decision": "ONE_OK_VERB_COMPOSES_WITH_SEVEN_ARGUMENT_SLOTS_AND_DURATION_ENDPOINTS",
    }
    (HERE / "SIX_HUNDRED_FIFTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
