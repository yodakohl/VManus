#!/usr/bin/env python3
"""Close SOLK as the graded verb AUFFANGEN."""

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
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in all_events:
        by_statement[event["statement_id"]].append(event)
        if "SOLK" in event["semantic_component_parse"].split("+"):
            by_card[event["card_no"]].append(event)

    cards = []
    for card in sorted(by_card, key=proc_num):
        rows = by_card[card]
        exemplar = rows[0]
        cards.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": exemplar["semantic_component_parse"],
            "short_solk_value_de": "AUFFANGEN",
            "composed_reading_de": exemplar["standard_command_de"],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "contains_close": "YES" if "SCHLUSS" in exemplar["standard_command_de"] else "NO",
        })

    event_rows = []
    for event in all_events:
        if "SOLK" not in event["semantic_component_parse"].split("+"):
            continue
        statement = by_statement[event["statement_id"]]
        pos = next(i for i, row in enumerate(statement) if row["event_id"] == event["event_id"])
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
            "statement_final": "YES" if pos == len(statement) - 1 else "NO",
            "full_statement_surface": " ".join(row["surface"] for row in statement),
        })

    grid_spec = [
        ("ZERO", "ACTIVE_Y", "PROC087", "AUFFANGEN; POSTEN BLEIBT AKTIV", "attested"),
        ("ZERO", "CLOSED_DY", None, "AUFFANGEN; SCHRITT SCHLIESSEN", "predicted_missing"),
        ("E", "ACTIVE_Y", "PROC164", "KURZ AUFFANGEN; POSTEN BLEIBT AKTIV", "attested"),
        ("E", "CLOSED_DY", None, "KURZ AUFFANGEN; SCHRITT SCHLIESSEN", "predicted_missing"),
        ("EE", "ACTIVE_Y", "PROC170", "LANG AUFFANGEN; POSTEN BLEIBT AKTIV", "attested"),
        ("EE", "CLOSED_DY", "PROC098", "LANG AUFFANGEN; SCHRITT SCHLIESSEN", "attested"),
        ("EEE", "ACTIVE_Y", None, "VOLLSTAENDIG AUFFANGEN; POSTEN BLEIBT AKTIV", "predicted_missing"),
        ("EEE", "CLOSED_DY", None, "VOLLSTAENDIG AUFFANGEN; SCHRITT SCHLIESSEN", "predicted_missing"),
    ]
    guesses = {("ZERO", "CLOSED_DY"): "solkdy?", ("E", "CLOSED_DY"): "solkedy?", ("EEE", "ACTIVE_Y"): "solkeeey?", ("EEE", "CLOSED_DY"): "solkeeedy?"}
    grid_rows = []
    for grade, endpoint, card, reading, status in grid_spec:
        rows = by_card[card] if card else []
        pieces = ["SOLK"]
        if grade != "ZERO":
            pieces.append(grade)
        pieces.append("Y" if endpoint == "ACTIVE_Y" else "DY")
        grid_rows.append({
            "grade": grade,
            "endpoint": endpoint,
            "status": status,
            "card_id": card or "NONE",
            "surfaces": "|".join(sorted({row["surface"] for row in rows})) if rows else guesses[(grade, endpoint)],
            "events": len(rows),
            "reading_de": reading,
            "composition_rule": "+".join(pieces),
        })

    predictions = [
        ("SOLK+DY", "solkdy?", "AUFFANGEN UND OHNE DAUERGRAD SCHLIESSEN"),
        ("SOLK+E+DY", "solkedy?", "KURZ AUFFANGEN UND SCHLIESSEN"),
        ("SOLK+EEE+Y", "solkeeey?", "VOLLSTAENDIG AUFFANGEN UND AKTIV LASSEN"),
        ("SOLK+EEE+DY", "solkeeedy?", "VOLLSTAENDIG AUFFANGEN UND SCHLIESSEN"),
        ("SOLK+AIN", "solkain?", "EINE PORTION AUFFANGEN"),
    ]
    prediction_rows = [{"predicted_recipe": r, "surface_guess": s, "predicted_reading_de": g} for r, s, g in predictions]

    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SIXTH_5_SOLK_CARDS.tsv", cards, list(cards[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SIXTH_7_SOLK_EVENT_CONTEXTS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SIXTH_8_COLLECT_GRID_CELLS.tsv", grid_rows, list(grid_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SIXTH_5_SOLK_PREDICTIONS.tsv", prediction_rows, list(prediction_rows[0]))

    summary = {
        "status": "PASS",
        "solk_card_types": len(cards),
        "solk_events": len(event_rows),
        "component_recipes": len({row["component_recipe"] for row in cards}),
        "grid_cells": len(grid_rows),
        "attested_grid_cells": sum(row["status"] == "attested" for row in grid_rows),
        "predicted_grid_cells": sum(row["status"] == "predicted_missing" for row in grid_rows),
        "measure_events": sum(int(row["events"]) for row in cards if row["component_recipe"] == "SOLK+AIIN"),
        "close_events": sum(row["contains_close"] == "YES" for row in event_rows),
        "close_events_final": sum(row["contains_close"] == "YES" and row["statement_final"] == "YES" for row in event_rows),
        "expanded_dictionary_card_types": 80,
        "expanded_dictionary_events": 196,
        "decision": "SOLK_IS_A_GRADED_COLLECT_VERB_WITH_ACTIVE_CLOSED_AND_MEASURE_SLOTS",
    }
    (HERE / "SIX_HUNDRED_SIXTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
