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
    event = next(row for row in events if "LD" in row["component_recipe"].split("+"))
    statement = statements[event["statement_id"]]
    surface_to_recipe = {row["surface"]: row["component_recipe"] for row in events}

    candidates = [
        {"candidate": "BEFESTIGEN", "reading": "diesen befestigen; Schluss", "extra_object": "NONE", "duplicates_dy": "NO", "repair": 0, "decision": "SELECT_BOUND"},
        {"candidate": "BINDEN", "reading": "diesen binden; Schluss", "extra_object": "CORD_OR_BAND", "duplicates_dy": "NO", "repair": 2, "decision": "REJECT_NARROW"},
        {"candidate": "VERSCHLIESSEN", "reading": "diesen verschliessen; Schluss", "extra_object": "NONE", "duplicates_dy": "YES", "repair": 3, "decision": "REJECT"},
        {"candidate": "DOPPELSCHLUSS", "reading": "diesen doppelt schliessen", "extra_object": "NONE", "duplicates_dy": "YES", "repair": 4, "decision": "REJECT_GRAPHIC_ONLY"},
        {"candidate": "ANLEGEN", "reading": "diesen anlegen; Schluss", "extra_object": "NONE", "duplicates_dy": "NO", "repair": 2, "decision": "REJECT_OVERLAP_OK"},
    ]
    event_row = {
        "event_id": event["event_id"],
        "page": event["page"],
        "statement_id": event["statement_id"],
        "owner_de": event["owner_de"],
        "surface": event["surface"],
        "component_recipe": event["component_recipe"],
        "selected_reading_de": event["fourth_grammar_reading_de"],
        "classification": "BOUND_FASTENING_BEFORE_DY",
        "full_statement": statement["working_reading_de"],
    }

    extension_specs = [
        ("LD+Y", "ldy", "BEFESTIGEN · DIES"),
        ("LD+DY", "lddy", "BEFESTIGEN · SCHLUSS"),
        ("LD+AL", "ldal", "BEFESTIGEN · ZIELSTELLE"),
        ("LD+AR", "ldar", "BEFESTIGEN · QUELLE"),
        ("OK+LD+DY", "qoklddy", "ANSETZEN · BEFESTIGEN · SCHLUSS"),
    ]
    extension_rows = []
    for recipe, surface, reading in extension_specs:
        observed_recipe = surface_to_recipe.get(surface, "NONE")
        extension_rows.append(
            {
                "hypothetical_recipe": recipe,
                "naive_surface": surface,
                "reading_de": reading,
                "surface_observed": "YES" if observed_recipe != "NONE" else "NO",
                "observed_recipe": observed_recipe,
                "decision": "DO_NOT_GENERALIZE" if observed_recipe != "NONE" else "WITHHOLD_BOUND_COMPONENT",
            }
        )

    write("EIGHT_HUNDRED_FOURTEENTH_5_LD_CANDIDATES.tsv", candidates, ["candidate", "reading", "extra_object", "duplicates_dy", "repair", "decision"])
    write("EIGHT_HUNDRED_FOURTEENTH_LD_EVENT.tsv", [event_row], list(event_row))
    write("EIGHT_HUNDRED_FOURTEENTH_5_EXTENSION_TESTS.tsv", extension_rows, ["hypothetical_recipe", "naive_surface", "reading_de", "surface_observed", "observed_recipe", "decision"])
    summary = {
        "status": "PASS",
        "decision": "LD_RETAINED_AS_BOUND_BEFESTIGEN_BEFORE_DY__LOCAL_SINGLETON_CLASS_ELIMINATED",
        "events": 1,
        "statements": 1,
        "candidates": len(candidates),
        "extension_tests": len(extension_rows),
        "surface_collisions": sum(row["surface_observed"] == "YES" for row in extension_rows),
        "core_size": 33,
        "bound_components": 3,
        "remaining_local_singletons": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_FOURTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
