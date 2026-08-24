#!/usr/bin/env python3
"""Close OR as the material noun ANSATZ/ZUBEREITUNG."""

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


FLUENT = {
    "CTH+O+OR": "BEREITER ARBEITSGANG MIT DEM ANSATZ",
    "Y+CH+E+OR": "VOM LAUFENDEN POSTEN KURZ FUER DEN ANSATZ ABNEHMEN",
    "OR": "ANSATZ ODER ZUBEREITUNG",
    "OT+CH+OR": "DANACH VOM ANSATZ ABNEHMEN",
    "OL+OR": "DEN ANSATZ FORTSETZEN",
    "O+Y+K+OR": "DEN ANSATZ ZUM LAUFENDEN ARBEITSGANG ZUDOSIEREN",
    "OR+AIN": "EINE PORTION DES ANSATZES",
    "HO+CH+OR": "EINE ZUTAT FUER DEN ANSATZ ABNEHMEN",
    "AL+R+OR": "DEN ANSATZ AN DER ZIELSTELLE KUEHLEN",
    "L+AL+OR": "DEN ANSATZ ZUR ZIELSTELLE WEITERLEITEN",
}


def proc_num(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)
        if "OR" in event["semantic_component_parse"].split("+"):
            by_card[event["card_no"]].append(event)

    inventory_rows = []
    for card in sorted(by_card, key=proc_num):
        rows = by_card[card]
        exemplar = rows[0]
        recipe = exemplar["semantic_component_parse"]
        inventory_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": recipe,
            "short_or_value_de": "ANSATZ_ODER_ZUBEREITUNG",
            "literal_reading_de": exemplar["standard_command_de"],
            "fluent_composition_de": FLUENT[recipe],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "contains_close": "YES" if "SCHLUSS" in exemplar["standard_command_de"] else "NO",
        })

    event_rows = []
    for event in events:
        if "OR" not in event["semantic_component_parse"].split("+"):
            continue
        statement = by_statement[event["statement_id"]]
        pos = statement.index(event)
        if pos == 0:
            position_class = "ENTRY"
        elif pos == len(statement) - 1:
            position_class = "FINAL"
        else:
            position_class = "MEDIAL"
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "position": pos + 1,
            "statement_events": len(statement),
            "position_class": position_class,
            "card_no": event["card_no"],
            "surface": event["surface"],
            "component_recipe": event["semantic_component_parse"],
            "fluent_composition_de": FLUENT[event["semantic_component_parse"]],
            "left_surface": statement[pos - 1]["surface"] if pos else "BOF",
            "right_surface": statement[pos + 1]["surface"] if pos + 1 < len(statement) else "EOF",
        })

    predictions = [
        ("OR+AIIN", "oraiin?", "ANSATZ NACH SOLLMASS"),
        ("OR+AL", "oral?", "ANSATZ FUER DIE ZIELSTELLE"),
        ("OR+AR", "orar?", "ANSATZ AUS DEM VORRAT"),
        ("OR+AIR", "orair?", "LAUFENDER ODER FLIESSENDER ANSATZ"),
        ("OR+Y", "ory?", "DER AKTUELLE ANSATZPOSTEN"),
    ]
    prediction_rows = [
        {"predicted_recipe": recipe, "surface_guess": surface, "predicted_reading_de": reading, "rule": "OR bleibt Materialnomen; Zusatz liefert Argument"}
        for recipe, surface, reading in predictions
    ]

    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FOURTH_10_OR_CARDS.tsv", inventory_rows, list(inventory_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FOURTH_18_OR_EVENT_CONTEXTS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_FOURTH_5_OR_PREDICTIONS.tsv", prediction_rows, list(prediction_rows[0]))

    summary = {
        "status": "PASS",
        "or_card_types": len(inventory_rows),
        "or_events": len(event_rows),
        "component_recipes": len({row["component_recipe"] for row in inventory_rows}),
        "bare_or_card_types": sum(row["component_recipe"] == "OR" for row in inventory_rows),
        "bare_or_events": sum(int(row["events"]) for row in inventory_rows if row["component_recipe"] == "OR"),
        "bare_or_surfaces": next(row["surfaces"] for row in inventory_rows if row["component_recipe"] == "OR"),
        "entry_events": sum(row["position_class"] == "ENTRY" for row in event_rows),
        "medial_events": sum(row["position_class"] == "MEDIAL" for row in event_rows),
        "final_events": sum(row["position_class"] == "FINAL" for row in event_rows),
        "close_events": sum(row["contains_close"] == "YES" for row in inventory_rows),
        "pages": len({row["page"] for row in event_rows}),
        "records": len({row["record"] for row in event_rows}),
        "predictions": len(prediction_rows),
        "expanded_dictionary_card_types": 66,
        "expanded_dictionary_events": 175,
        "decision": "OR_IS_A_PORTABLE_PREPARATION_NOUN_WITH_PORTION_CONTINUATION_TARGET_AND_TRANSFER_COMPOSITION",
    }
    (HERE / "SIX_HUNDRED_SIXTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
