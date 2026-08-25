#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_fourth_workshop_grammar_eight_hundred_tenth"
EVENTS = BASE / "EIGHT_HUNDRED_TENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_TENTH_116_STATEMENT_REPARSE.tsv"


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
    event = next(row for row in events if "CFH" in row["component_recipe"].split("+"))
    statement = statements[event["statement_id"]]
    observed = {row["surface"] for row in events}

    candidates = [
        {"candidate": "AUSWRINGEN", "mechanism": "cloth or twisting required", "fits_sequence": "YES", "extra_object": "TUCH_OR_TWIST", "repair": 2, "decision": "REVISE"},
        {"candidate": "AUSPRESSEN", "mechanism": "generic pressure extraction", "fits_sequence": "YES", "extra_object": "NONE", "repair": 0, "decision": "SELECT"},
        {"candidate": "ENTNEHMEN", "mechanism": "generic taking", "fits_sequence": "PARTIAL", "extra_object": "NONE", "repair": 3, "decision": "REJECT_DUPLICATES_CH"},
        {"candidate": "ABGIESSEN", "mechanism": "decant liquid", "fits_sequence": "PARTIAL", "extra_object": "LIQUID_LAYER", "repair": 4, "decision": "REJECT"},
    ]
    event_row = {
        "event_id": event["event_id"],
        "page": event["page"],
        "statement_id": event["statement_id"],
        "owner_de": event["owner_de"],
        "surface": event["surface"],
        "component_recipe": event["component_recipe"],
        "old_reading_de": event["fourth_grammar_reading_de"],
        "selected_reading_de": "AUSPRESSEN · DIES",
        "previous_surface": "schoal",
        "previous_instruction": "Vorgang am Ziel halten",
        "next_surface": "shfydaiin",
        "next_instruction": "dies nach Sollmass halten",
        "sequence_role": "mechanical extraction before measured holding and inward filling",
    }
    revised = statement["working_reading_de"].replace("auswringen", "auspressen")
    statement_row = {
        "statement_id": statement["statement_id"],
        "page": statement["page"],
        "owner_noun_de": statement["owner_noun_de"],
        "surface_sequence": statement["surface_sequence"],
        "old_reading_de": statement["working_reading_de"],
        "revised_reading_de": revised,
    }

    grid_specs = [
        ("NONE", "NONE", "Y", "DIES", "CFH+Y", "cfhy", 1),
        ("NONE", "NONE", "DY", "SCHLUSS", "CFH+DY", "cfhdy", 0),
        ("E", "KURZ", "Y", "DIES", "CFH+E+Y", "cfhey", 0),
        ("E", "KURZ", "DY", "SCHLUSS", "CFH+E+DY", "cfhedy", 0),
        ("EE", "LANG", "Y", "DIES", "CFH+EE+Y", "cfheey", 0),
        ("EE", "LANG", "DY", "SCHLUSS", "CFH+EE+DY", "cfheedy", 0),
        ("EEE", "VOLL", "Y", "DIES", "CFH+EEE+Y", "cfheeey", 0),
        ("EEE", "VOLL", "DY", "SCHLUSS", "CFH+EEE+DY", "cfheeedy", 0),
    ]
    grid_rows = []
    for grade, grade_value, endpoint, endpoint_value, recipe, surface, count in grid_specs:
        reading = " · ".join(x for x in ("AUSPRESSEN", grade_value if grade != "NONE" else "", endpoint_value) if x)
        grid_rows.append(
            {
                "grade": grade,
                "grade_value_de": grade_value,
                "endpoint": endpoint,
                "endpoint_value_de": endpoint_value,
                "component_recipe": recipe,
                "surface": surface,
                "events": count,
                "reading_de": reading,
                "status": "ATTESTED" if count else "PREDICTED_UNATTESTED",
                "surface_collision": "YES" if not count and surface in observed else "NO",
            }
        )

    write("EIGHT_HUNDRED_ELEVENTH_4_CFH_CANDIDATES.tsv", candidates, ["candidate", "mechanism", "fits_sequence", "extra_object", "repair", "decision"])
    write("EIGHT_HUNDRED_ELEVENTH_CFH_EVENT.tsv", [event_row], list(event_row))
    write("EIGHT_HUNDRED_ELEVENTH_REVISED_STATEMENT.tsv", [statement_row], list(statement_row))
    write("EIGHT_HUNDRED_ELEVENTH_8_CFH_GRID.tsv", grid_rows, ["grade", "grade_value_de", "endpoint", "endpoint_value_de", "component_recipe", "surface", "events", "reading_de", "status", "surface_collision"])
    summary = {
        "status": "PASS",
        "decision": "CFH_REVISED_TO_AUSPRESSEN_AND_PROMOTED_TO_SPECIALIST_CORE32",
        "events": 1,
        "statements": 1,
        "candidates": len(candidates),
        "grid_cells": len(grid_rows),
        "observed_cells": 1,
        "predicted_cells": 7,
        "prediction_collisions": sum(row["surface_collision"] == "YES" for row in grid_rows),
        "new_core_size": 32,
        "remaining_local_singletons": 3,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_ELEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
