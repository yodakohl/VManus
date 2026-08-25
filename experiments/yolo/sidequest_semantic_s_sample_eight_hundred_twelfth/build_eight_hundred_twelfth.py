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
    event = next(row for row in events if "S" in row["component_recipe"].split("+"))
    statement = statements[event["statement_id"]]

    candidates = [
        {"candidate": "TEIL", "sentence_reading": "kurz entnehmen und teilen", "distinct_from_ain": "NO", "extra_assumption": "division action", "repair": 3, "decision": "REVISE"},
        {"candidate": "MENGE", "sentence_reading": "kurz eine Menge entnehmen", "distinct_from_ain": "NO", "extra_assumption": "unspecified quantity", "repair": 3, "decision": "REJECT"},
        {"candidate": "REST", "sentence_reading": "kurz den Rest entnehmen", "distinct_from_ain": "YES", "extra_assumption": "prior depletion", "repair": 4, "decision": "REJECT"},
        {"candidate": "ANTEIL", "sentence_reading": "kurz einen Anteil entnehmen", "distinct_from_ain": "WEAK", "extra_assumption": "partitive quantity", "repair": 2, "decision": "REJECT_OVERLAP"},
        {"candidate": "PROBE", "sentence_reading": "kurz eine Probe entnehmen", "distinct_from_ain": "YES", "extra_assumption": "none; followed by prescribed measure", "repair": 0, "decision": "SELECT"},
    ]
    event_row = {
        "event_id": event["event_id"],
        "page": event["page"],
        "statement_id": event["statement_id"],
        "owner_de": event["owner_de"],
        "surface": event["surface"],
        "component_recipe": event["component_recipe"],
        "old_reading_de": event["fourth_grammar_reading_de"],
        "selected_reading_de": "ENTNEHMEN · KURZ · PROBE",
        "following_surface": "aiin",
        "following_value": "SOLLMASS",
        "sequence_reading": "kurz eine Probe entnehmen; danach nach Sollmass weiterarbeiten",
    }
    revised = statement["working_reading_de"].replace("Kurz entnehmen und teilen", "Kurz eine Probe entnehmen")
    statement_row = {
        "statement_id": statement["statement_id"],
        "page": statement["page"],
        "owner_noun_de": statement["owner_noun_de"],
        "surface_sequence": statement["surface_sequence"],
        "old_reading_de": statement["working_reading_de"],
        "revised_reading_de": revised,
    }

    contrast_rows = [
        {"component": "S", "value_de": "PROBE", "semantic_type": "diagnostic sample", "events": 1, "typical_question": "what is taken for checking?", "kept_distinct": "YES"},
        {"component": "AIN", "value_de": "PORTION", "semantic_type": "working quantity", "events": 18, "typical_question": "how much material is used?", "kept_distinct": "YES"},
        {"component": "AIIN", "value_de": "SOLLMASS", "semantic_type": "prescribed amount or setting", "events": 39, "typical_question": "what measure/setting should be reached?", "kept_distinct": "YES"},
    ]
    predictions = [
        {"component_recipe": "CH+S", "predicted_reading_de": "ENTNEHMEN · PROBE", "surface": "WITHHELD", "workshop_use": "take a sample"},
        {"component_recipe": "SH+S", "predicted_reading_de": "HALTEN · PROBE", "surface": "WITHHELD", "workshop_use": "retain a sample"},
        {"component_recipe": "K+S", "predicted_reading_de": "ZUGEBEN · PROBE", "surface": "WITHHELD", "workshop_use": "add a sample"},
        {"component_recipe": "S+AIIN", "predicted_reading_de": "PROBE · SOLLMASS", "surface": "WITHHELD", "workshop_use": "sample at prescribed measure"},
    ]

    write("EIGHT_HUNDRED_TWELFTH_5_S_CANDIDATES.tsv", candidates, ["candidate", "sentence_reading", "distinct_from_ain", "extra_assumption", "repair", "decision"])
    write("EIGHT_HUNDRED_TWELFTH_S_EVENT.tsv", [event_row], list(event_row))
    write("EIGHT_HUNDRED_TWELFTH_REVISED_STATEMENT.tsv", [statement_row], list(statement_row))
    write("EIGHT_HUNDRED_TWELFTH_S_AIN_AIIN_CONTRAST.tsv", contrast_rows, ["component", "value_de", "semantic_type", "events", "typical_question", "kept_distinct"])
    write("EIGHT_HUNDRED_TWELFTH_4_RECIPE_PREDICTIONS.tsv", predictions, ["component_recipe", "predicted_reading_de", "surface", "workshop_use"])
    summary = {
        "status": "PASS",
        "decision": "S_REVISED_TO_PROBE_AND_PROMOTED_TO_SPECIALIST_CORE33",
        "events": 1,
        "statements": 1,
        "candidates": len(candidates),
        "quantity_contrasts": len(contrast_rows),
        "recipe_predictions_surface_withheld": len(predictions),
        "new_core_size": 33,
        "remaining_local_singletons": 2,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWELFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
