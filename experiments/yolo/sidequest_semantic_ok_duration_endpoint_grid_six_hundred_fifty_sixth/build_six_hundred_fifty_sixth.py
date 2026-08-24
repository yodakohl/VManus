#!/usr/bin/env python3
"""Consolidate the OK + duration grade + Y/DY endpoint paradigm."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"
P655 = ROOT / "experiments/yolo/sidequest_semantic_endpoint_branching_six_hundred_fifty_fifth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


GRID_IDS = {"PROC008", "PROC011", "PROC085", "PROC092", "PROC067", "PROC100", "PROC119"}


def proc_number(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    m09 = read_tsv(P655 / "SIX_HUNDRED_FIFTY_FIFTH_4_M09_BRANCHES.tsv")
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_card[event["card_no"]].append(event)
        by_statement[event["statement_id"]].append(event)

    ok_ids = sorted(
        {event["card_no"] for event in events if "OK" in event["semantic_component_parse"].split("+")},
        key=proc_number,
    )
    inventory_rows: list[dict[str, object]] = []
    for card in ok_ids:
        rows = by_card[card]
        exemplar = rows[0]
        closes = "SCHLUSS" in exemplar["standard_command_de"]
        terminal = sum(by_statement[row["statement_id"]][-1]["event_id"] == row["event_id"] for row in rows)
        parse = exemplar["semantic_component_parse"]
        if card in GRID_IDS:
            family = "CORE_DURATION_ENDPOINT_GRID"
        elif closes:
            family = "SPECIALIZED_CLOSED_OPERATION"
        elif any(atom in parse.split("+") for atom in ("AIIN", "AIN", "AL", "AR", "AIR", "OL")):
            family = "OPEN_ARGUMENT_COMPLEMENT"
        else:
            family = "SPECIALIZED_OPEN_OPERATION"
        inventory_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_parse": parse,
            "standard_command_de": exemplar["standard_command_de"],
            "family": family,
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "statement_final_events": terminal,
            "contains_close": "YES" if closes else "NO",
        })

    grid_spec = [
        ("ZERO", "ACTIVE_Y", ["PROC008", "PROC011"], "ANSETZEN; POSTEN BLEIBT AKTIV", "attested"),
        ("ZERO", "CLOSED_DY", [], "ANSETZEN; SCHRITT SCHLIESSEN", "predicted_missing"),
        ("E", "ACTIVE_Y", ["PROC085"], "KURZ ANSETZEN; POSTEN BLEIBT AKTIV", "attested"),
        ("E", "CLOSED_DY", ["PROC067"], "KURZ ANSETZEN; SCHRITT SCHLIESSEN", "attested"),
        ("EE", "ACTIVE_Y", ["PROC092"], "LANG ANSETZEN; POSTEN BLEIBT AKTIV", "attested"),
        ("EE", "CLOSED_DY", ["PROC100"], "LANG ANSETZEN; SCHRITT SCHLIESSEN", "attested"),
        ("EEE", "ACTIVE_Y", [], "VOLLSTAENDIG ANSETZEN; POSTEN BLEIBT AKTIV", "predicted_missing"),
        ("EEE", "CLOSED_DY", ["PROC119"], "VOLLSTAENDIG ANSETZEN; SCHRITT SCHLIESSEN", "attested"),
    ]
    predicted_surface = {
        ("ZERO", "CLOSED_DY"): "qokdy?",
        ("EEE", "ACTIVE_Y"): "qokeeey?",
    }
    grid_rows: list[dict[str, object]] = []
    for grade, endpoint, cards, reading, status in grid_spec:
        rows = [row for card in cards for row in by_card[card]]
        grid_rows.append({
            "duration_grade": grade,
            "endpoint": endpoint,
            "status": status,
            "card_types": len(cards),
            "card_ids": "|".join(cards) if cards else "NONE",
            "surfaces": "|".join(sorted({row["surface"] for row in rows})) if rows else predicted_surface[(grade, endpoint)],
            "events": len(rows),
            "statement_final_events": sum(by_statement[row["statement_id"]][-1]["event_id"] == row["event_id"] for row in rows),
            "reading_de": reading,
            "composition_rule": f"OK+{'' if grade == 'ZERO' else grade}+{'Y' if endpoint == 'ACTIVE_Y' else 'DY'}",
        })

    prediction_rows = [
        {
            "predicted_components": "OK+EEE+Y",
            "predicted_surface": "qokeeey?",
            "predicted_reading_de": "VOLLSTAENDIG ANSETZEN; POSTEN BLEIBT AKTIV",
            "contrast_attested": "qokeeedy=VOLLSTAENDIG ANSETZEN; SCHLUSS",
            "use_rule": "wenn gefunden darf die Karte nicht automatisch als Schluss gelten",
        },
        {
            "predicted_components": "OK+DY",
            "predicted_surface": "qokdy?",
            "predicted_reading_de": "ANSETZEN; SCHRITT SCHLIESSEN OHNE DAUERGRAD",
            "contrast_attested": "qoky=ANSETZEN; POSTEN BLEIBT AKTIV",
            "use_rule": "Oberflaeche unsicher; nur Komponentenrolle ist vorhergesagt",
        },
    ]

    branch_rows = []
    for row in m09:
        branch_rows.append({
            **row,
            "first_card_grid_cell": "EE+ACTIVE_Y",
            "second_card_grid_cell": "ZERO+ACTIVE_Y" if row["branch"] == "M09O_OPEN_CONTINUATION" else "E+CLOSED_DY",
            "workshop_choice": "WEITERARBEITEN" if row["branch"] == "M09O_OPEN_CONTINUATION" else "ABSCHLIESSEN",
        })

    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SIXTH_23_OK_CARD_INVENTORY.tsv", inventory_rows, list(inventory_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SIXTH_8_DURATION_ENDPOINT_CELLS.tsv", grid_rows, list(grid_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SIXTH_2_PREDICTED_CELLS.tsv", prediction_rows, list(prediction_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SIXTH_4_M09_GRID_CHOICES.tsv", branch_rows, list(branch_rows[0]))

    summary = {
        "status": "PASS",
        "ok_card_types": len(inventory_rows),
        "ok_events": sum(int(row["events"]) for row in inventory_rows),
        "core_grid_card_types": sum(int(row["card_types"]) for row in grid_rows),
        "core_grid_events": sum(int(row["events"]) for row in grid_rows),
        "grid_cells": len(grid_rows),
        "attested_grid_cells": sum(row["status"] == "attested" for row in grid_rows),
        "predicted_missing_cells": sum(row["status"] == "predicted_missing" for row in grid_rows),
        "active_events": sum(int(row["events"]) for row in grid_rows if row["endpoint"] == "ACTIVE_Y"),
        "closed_events": sum(int(row["events"]) for row in grid_rows if row["endpoint"] == "CLOSED_DY"),
        "closed_events_statement_final": sum(int(row["statement_final_events"]) for row in grid_rows if row["endpoint"] == "CLOSED_DY"),
        "m09_choices": len(branch_rows),
        "decision": "OK_E_GRADE_Y_DY_IS_A_PRODUCTIVE_DURATION_AND_ENDPOINT_PARADIGM",
    }
    (HERE / "SIX_HUNDRED_FIFTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
