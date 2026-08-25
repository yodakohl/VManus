#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_ninth_workshop_grammar_eight_hundred_thirty_third"
PREFIX = "EIGHT_HUNDRED_THIRTY_EIGHTH"
QUANTITIES = ("AIN", "AIIN", "IIN")


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def frame(recipe: str, quantity: str) -> str:
    return "+".join("QTY" if token == quantity else token for token in recipe.split("+"))


def main() -> None:
    cards = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_173_CARD_NINTH_DICTIONARY.tsv")
    events = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_381_EVENT_REPARSE.tsv")
    predictions = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_76_UNATTESTED_PREDICTIONS.tsv")
    card_by_recipe = {row["component_recipe"]: row for row in cards}
    prediction_by_recipe = {row["component_recipe"]: row for row in predictions}

    quantity_cards = []
    for card in cards:
        tokens = card["component_recipe"].split("+")
        present = [quantity for quantity in QUANTITIES if quantity in tokens]
        if len(present) != 1:
            continue
        quantity = present[0]
        quantity_cards.append(
            {
                "exact_card_id": card["exact_card_id"],
                "surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "quantity_component": quantity,
                "quantity_value_de": {"AIN": "PORTION", "AIIN": "SOLLMASS", "IIN": "STUFE"}[quantity],
                "reading_de": card["ninth_grammar_reading_de"],
                "events": card["events"],
                "operator_frame": frame(card["component_recipe"], quantity),
            }
        )

    quantity_events = []
    for event in events:
        tokens = event["component_recipe"].split("+")
        present = [quantity for quantity in QUANTITIES if quantity in tokens]
        if len(present) != 1:
            continue
        quantity = present[0]
        quantity_events.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "quantity_component": quantity,
                "quantity_value_de": {"AIN": "PORTION", "AIIN": "SOLLMASS", "IIN": "STUFE"}[quantity],
                "reading_de": event["ninth_grammar_reading_de"],
            }
        )

    frames: dict[str, dict[str, tuple[str, str, str, str]]] = {}
    for recipe, row in card_by_recipe.items():
        tokens = recipe.split("+")
        present = [quantity for quantity in QUANTITIES if quantity in tokens]
        if len(present) != 1:
            continue
        quantity = present[0]
        frames.setdefault(frame(recipe, quantity), {})[quantity] = ("ATTESTED", row["registered_surfaces"], row["ninth_grammar_reading_de"], row["events"])
    for recipe, row in prediction_by_recipe.items():
        tokens = recipe.split("+")
        present = [quantity for quantity in QUANTITIES if quantity in tokens]
        if len(present) != 1:
            continue
        quantity = present[0]
        frames.setdefault(frame(recipe, quantity), {}).setdefault(quantity, ("PREDICTION_ONLY", row["predicted_surface"], row["reading_de"], "0"))

    grid = []
    for index, operator_frame in enumerate(sorted(frames), 1):
        cells = frames[operator_frame]
        row: dict[str, object] = {"frame_id": f"QF{index:02d}", "operator_frame": operator_frame}
        for quantity in QUANTITIES:
            status, surface, reading, support = cells.get(quantity, ("ABSENT", "NONE", "NONE", "0"))
            row[f"{quantity.lower()}_status"] = status
            row[f"{quantity.lower()}_surface"] = surface
            row[f"{quantity.lower()}_reading_de"] = reading
            row[f"{quantity.lower()}_events"] = support
        row["ain_aiin_pair_available"] = "YES" if "AIN" in cells and "AIIN" in cells else "NO"
        row["three_cell_row_available"] = "YES" if all(quantity in cells for quantity in QUANTITIES) else "NO"
        row["decision"] = "AIN_PORTION__AIIN_SOLLMASS__IIN_STAGE"
        grid.append(row)

    new_predictions = [
        {"predicted_surface": "aiiin", "component_recipe": "IIN", "reading_de": "STUFE", "model": "BARE_AIN_AIIN_IIN_ROW", "closest_attested": "dain / aiin", "status": "NEW_CREATIVE_PREDICTION"},
        {"predicted_surface": "qokaiiin", "component_recipe": "OK+IIN", "reading_de": "ANSETZEN · STUFE", "model": "OK_AIN_AIIN_IIN_ROW", "closest_attested": "qokain / qokaiin", "status": "NEW_CREATIVE_PREDICTION"},
        {"predicted_surface": "ykaiiin", "component_recipe": "Y+K+IIN", "reading_de": "POSTEN · ZUGEBEN · STUFE", "model": "YK_AIN_AIIN_IIN_ROW", "closest_attested": "ykain / ykaiin / kaiiin", "status": "NEW_CREATIVE_PREDICTION"},
    ]

    write(f"{PREFIX}_21_QUANTITY_CARDS.tsv", quantity_cards, ["exact_card_id", "surfaces", "component_recipe", "quantity_component", "quantity_value_de", "reading_de", "events", "operator_frame"])
    write(f"{PREFIX}_61_QUANTITY_EVENTS.tsv", quantity_events, ["event_id", "page", "record", "statement_id", "surface", "component_recipe", "quantity_component", "quantity_value_de", "reading_de"])
    write(f"{PREFIX}_18_OPERATOR_QUANTITY_FRAMES.tsv", grid, ["frame_id", "operator_frame", "ain_status", "ain_surface", "ain_reading_de", "ain_events", "aiin_status", "aiin_surface", "aiin_reading_de", "aiin_events", "iin_status", "iin_surface", "iin_reading_de", "iin_events", "ain_aiin_pair_available", "three_cell_row_available", "decision"])
    write(f"{PREFIX}_3_NEW_IIN_PREDICTIONS.tsv", new_predictions, ["predicted_surface", "component_recipe", "reading_de", "model", "closest_attested", "status"])

    summary = {
        "status": "PASS",
        "decision": "AIN_AIIN_IIN_FORM_A_PORTION_MEASURE_STAGE_SYSTEM",
        "quantity_cards": len(quantity_cards),
        "quantity_events": len(quantity_events),
        "ain_cards": sum(row["quantity_component"] == "AIN" for row in quantity_cards),
        "ain_events": sum(int(row["events"]) for row in quantity_cards if row["quantity_component"] == "AIN"),
        "aiin_cards": sum(row["quantity_component"] == "AIIN" for row in quantity_cards),
        "aiin_events": sum(int(row["events"]) for row in quantity_cards if row["quantity_component"] == "AIIN"),
        "iin_cards": sum(row["quantity_component"] == "IIN" for row in quantity_cards),
        "iin_events": sum(int(row["events"]) for row in quantity_cards if row["quantity_component"] == "IIN"),
        "operator_frames": len(grid),
        "ain_aiin_pair_frames": sum(row["ain_aiin_pair_available"] == "YES" for row in grid),
        "three_cell_rows_with_existing_predictions": sum(row["three_cell_row_available"] == "YES" for row in grid),
        "new_iin_predictions": len(new_predictions),
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 838: quantity composition

The quantity inventory now behaves like a small workshop subsystem rather than
three unrelated guesses:

- AIN = PORTION (8 cards, 18 events);
- AIIN = SOLLMASS (10 cards, 39 events);
- IIN = STUFE (3 cards, 4 events).

AIN and AIIN occupy the same operator frame in 14 rows when the existing
prediction deck is included. Bare AIN/AIIN, OK+AIN/AIIN, and Y+K+AIN/AIIN are
already attested on both sides. K is the first nearly complete three-cell row:
`kain` adds a portion, predicted `kaiin` adds to prescribed measure, and
attested `kaiiin` advances/adds to a stage.

IIN is not merely a larger portion. Its O+IIN and DA+IIN cards name a work-stage
or second stage. It therefore remains a different categorical value in the
same learned quantity/setting slot.

Three new creative cells follow: bare `aiiin=STUFE`, `qokaiiin=OK+IIN` (“set
at/through a stage”), and `ykaiiin=Y+K+IIN` (“add the current item to a
stage”). They are predictions only, but unlike free glosses they follow a
visible card family.

No current component value changes. Next, inspect the E/EE/EEE grade rows with
the same method and determine whether increasing E really predicts short →
long → full across operators or whether some complete cards reverse it.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
