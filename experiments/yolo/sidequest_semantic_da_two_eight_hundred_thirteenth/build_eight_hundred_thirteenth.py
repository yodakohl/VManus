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
    event = next(row for row in events if "DA" in row["component_recipe"].split("+"))
    statement = statements[event["statement_id"]]
    observed = {row["surface"] for row in events}

    candidates = [
        {"candidate": "ZWEI", "combined_reading": "ZWEI · STUFE", "sentence_reading": "bis zur zweiten Stufe fuehren", "overlap": "NONE", "repair": 0, "decision": "SELECT_BOUND"},
        {"candidate": "ZWEIT", "combined_reading": "ZWEIT · STUFE", "sentence_reading": "bis zur zweiten Stufe fuehren", "overlap": "NONE", "repair": 1, "decision": "REVISE_TO_ATOMIC_NUMBER"},
        {"candidate": "ERNEUT", "combined_reading": "ERNEUT · STUFE", "sentence_reading": "erneut bis zur Stufe fuehren", "overlap": "OKOK/OT repetition-flow", "repair": 3, "decision": "REJECT"},
        {"candidate": "NAECHST", "combined_reading": "NAECHST · STUFE", "sentence_reading": "bis zur naechsten Stufe fuehren", "overlap": "OT next-flow", "repair": 2, "decision": "REJECT"},
        {"candidate": "DOPPELT", "combined_reading": "DOPPELT · STUFE", "sentence_reading": "mit doppelter Stufe fuehren", "overlap": "NONE", "repair": 4, "decision": "REJECT"},
    ]
    event_row = {
        "event_id": event["event_id"],
        "page": event["page"],
        "statement_id": event["statement_id"],
        "owner_de": event["owner_de"],
        "surface": event["surface"],
        "component_recipe": event["component_recipe"],
        "old_reading_de": event["fourth_grammar_reading_de"],
        "selected_reading_de": "ZWEI · STUFE",
        "classification": "BOUND_NUMERAL_TWO_BEFORE_IIN",
    }
    revised = statement["working_reading_de"].replace("fuer den zweiten Durchgang bis zur Stufe fuehren", "bis zur zweiten Stufe fuehren")
    statement_row = {
        "statement_id": statement["statement_id"],
        "page": statement["page"],
        "owner_noun_de": statement["owner_noun_de"],
        "surface_sequence": statement["surface_sequence"],
        "old_reading_de": statement["working_reading_de"],
        "revised_reading_de": revised,
    }

    extension_rows = [
        {"hypothetical_recipe": "DA+AIN", "naive_surface": "dain", "reading_de": "ZWEI · PORTION", "surface_observed": "YES", "observed_value": "AIN · PORTION", "decision": "DO_NOT_GENERALIZE"},
        {"hypothetical_recipe": "DA+AIIN", "naive_surface": "daiin", "reading_de": "ZWEI · SOLLMASS", "surface_observed": "YES", "observed_value": "AIIN · SOLLMASS", "decision": "DO_NOT_GENERALIZE"},
        {"hypothetical_recipe": "DA+Y", "naive_surface": "day", "reading_de": "ZWEI · DIES", "surface_observed": "NO", "observed_value": "NONE", "decision": "WITHHOLD"},
        {"hypothetical_recipe": "DA+O", "naive_surface": "dao", "reading_de": "ZWEI · VORGANG", "surface_observed": "NO", "observed_value": "NONE", "decision": "WITHHOLD"},
    ]
    for row in extension_rows:
        actual = "YES" if row["naive_surface"] in observed else "NO"
        if actual != row["surface_observed"]:
            raise ValueError((row, actual))

    write("EIGHT_HUNDRED_THIRTEENTH_5_DA_CANDIDATES.tsv", candidates, ["candidate", "combined_reading", "sentence_reading", "overlap", "repair", "decision"])
    write("EIGHT_HUNDRED_THIRTEENTH_DA_EVENT.tsv", [event_row], list(event_row))
    write("EIGHT_HUNDRED_THIRTEENTH_REVISED_STATEMENT.tsv", [statement_row], list(statement_row))
    write("EIGHT_HUNDRED_THIRTEENTH_4_EXTENSION_TESTS.tsv", extension_rows, ["hypothetical_recipe", "naive_surface", "reading_de", "surface_observed", "observed_value", "decision"])
    summary = {
        "status": "PASS",
        "decision": "DA_REVISED_TO_BOUND_ZWEI_BEFORE_IIN__NOT_PROMOTED",
        "events": 1,
        "statements": 1,
        "candidates": len(candidates),
        "extension_tests": len(extension_rows),
        "surface_collisions": sum(row["surface_observed"] == "YES" for row in extension_rows),
        "core_size": 33,
        "bound_components": 2,
        "remaining_local_singletons": 1,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_THIRTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
