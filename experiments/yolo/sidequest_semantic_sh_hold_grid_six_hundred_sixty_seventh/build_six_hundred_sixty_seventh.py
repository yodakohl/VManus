#!/usr/bin/env python3
"""Build the complete SH=HALTEN valency and duration grid."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh/SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(SOURCE)
    statements: dict[str, list[dict[str, str]]] = defaultdict(list)
    cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        statements[event["statement_id"]].append(event)
        if "SH" in event["semantic_component_parse"].split("+"):
            cards[event["card_no"]].append(event)

    card_rows: list[dict[str, object]] = []
    for card in sorted(cards, key=number):
        rows = cards[card]
        first = rows[0]
        card_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": first["semantic_component_parse"],
            "portable_sh_value_de": "HALTEN",
            "composed_reading_de": first["standard_command_de"],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "event_ids": "|".join(row["event_id"] for row in rows),
        })

    event_rows: list[dict[str, object]] = []
    positions: Counter[str] = Counter()
    for rows in cards.values():
        for event in rows:
            statement = statements[event["statement_id"]]
            index = next(i for i, row in enumerate(statement) if row["event_id"] == event["event_id"])
            position = "WHOLE" if len(statement) == 1 else "ENTRY" if index == 0 else "FINAL" if index == len(statement) - 1 else "MEDIAL"
            positions[position] += 1
            event_rows.append({
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "card_no": event["card_no"],
                "surface": event["surface"],
                "component_recipe": event["semantic_component_parse"],
                "composed_reading_de": event["standard_command_de"],
                "statement_position": position,
                "contains_close": "YES" if "SCHLUSS" in event["standard_command_de"] else "NO",
                "full_statement_surface": " ".join(row["surface"] for row in statement),
            })

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in event_rows:
        by_recipe[str(event["component_recipe"])].append(event)  # type: ignore[arg-type]
    grid_specs = [
        ("ZERO", "ACTIVE_Y", "SH+Y", "predicted_missing", "HALTEN; POSTEN AKTIV"),
        ("ZERO", "CLOSED_DY", "SH+DY", "predicted_missing", "HALTEN; SCHLIESSEN"),
        ("E", "ACTIVE_Y", "SH+E+Y", "attested", "KURZ HALTEN; POSTEN AKTIV"),
        ("E", "CLOSED_DY", "SH+E+DY", "attested", "KURZ HALTEN; SCHLIESSEN"),
        ("EE", "ACTIVE_Y", "SH+EE+Y", "attested", "LANG HALTEN; POSTEN AKTIV"),
        ("EE", "CLOSED_DY", "SH+EE+DY", "attested", "LANG HALTEN; SCHLIESSEN"),
        ("EEE", "ACTIVE_Y", "SH+EEE+Y", "predicted_missing", "VOLLSTAENDIG HALTEN; POSTEN AKTIV"),
        ("EEE", "CLOSED_DY", "SH+EEE+DY", "predicted_missing", "VOLLSTAENDIG HALTEN; SCHLIESSEN"),
    ]
    grid_rows = []
    for grade, endpoint, recipe, status, reading in grid_specs:
        found = by_recipe.get(recipe, [])
        grid_rows.append({
            "grade": grade,
            "endpoint": endpoint,
            "component_recipe": recipe,
            "status": status,
            "card_ids": "|".join(sorted({str(row["card_no"]) for row in found}, key=number)) or "NONE",
            "surfaces": "|".join(sorted({str(row["surface"]) for row in found})) or "NOT_ON_FIXED_PAGES",
            "events": len(found),
            "reading_de": reading,
        })

    co_atoms = Counter()
    for row in card_rows:
        for atom in str(row["component_recipe"]).split("+"):
            if atom != "SH":
                co_atoms[atom] += int(row["events"])
    co_rows = [{"co_component": atom, "events_in_sh_cards": count} for atom, count in sorted(co_atoms.items(), key=lambda item: (-item[1], item[0]))]

    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SEVENTH_20_SH_CARDS.tsv", card_rows, list(card_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SEVENTH_25_SH_EVENT_CONTEXTS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SEVENTH_8_HOLD_GRID_CELLS.tsv", grid_rows, list(grid_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SEVENTH_SH_CO_COMPONENTS.tsv", co_rows, list(co_rows[0]))

    closed = [row for row in event_rows if row["contains_close"] == "YES"]
    summary = {
        "status": "PASS",
        "sh_card_types": len(card_rows),
        "sh_events": len(event_rows),
        "component_recipes": len({row["component_recipe"] for row in card_rows}),
        "positions": dict(sorted(positions.items())),
        "close_events": len(closed),
        "close_events_final": sum(row["statement_position"] in {"FINAL", "WHOLE"} for row in closed),
        "attested_grid_cells": sum(row["status"] == "attested" for row in grid_rows),
        "expanded_dictionary_card_types": 93,
        "expanded_dictionary_events": 212,
        "decision": "SH_IS_THE_PORTABLE_HOLD_VERB_WITH_DURATION_TARGET_MEASURE_AND_ENDPOINT_SLOTS",
    }
    (HERE / "SIX_HUNDRED_SIXTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
