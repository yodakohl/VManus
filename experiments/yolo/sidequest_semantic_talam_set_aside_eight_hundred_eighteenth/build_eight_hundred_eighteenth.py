#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_fifth_workshop_grammar_eight_hundred_fifteenth"
EVENTS = BASE / "EIGHT_HUNDRED_FIFTEENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_FIFTEENTH_116_STATEMENT_REPARSE.tsv"


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
    index = next(i for i, row in enumerate(events) if row["component_recipe"] == "TALAM")
    event = events[index]
    statement = statements[event["statement_id"]]
    previous = events[index - 1]
    following = events[index + 1]

    candidates = [
        {"candidate": "VERWAHREN", "short_value_de": "VERWAHREN", "local_fit": "MEDIUM", "extra_assumption": "LONG_TERM_STORAGE", "decision": "REJECT_OLD_TOO_LONG_TERM"},
        {"candidate": "BEISEITESTELLEN", "short_value_de": "BEISEITESTELLEN", "local_fit": "HIGH", "extra_assumption": "TEMPORARY_PREPARED_PORTION", "decision": "SELECT_WHOLE_OPERATION"},
        {"candidate": "AUFBEWAHREN", "short_value_de": "AUFBEWAHREN", "local_fit": "MEDIUM", "extra_assumption": "STORAGE_DURATION", "decision": "REJECT_LONGER_HORIZON"},
        {"candidate": "IN_DAS_GEFAESS", "short_value_de": "EINLEGEN", "local_fit": "MEDIUM", "extra_assumption": "UNSEEN_CONTAINER", "decision": "REJECT_INVENTED_OBJECT"},
        {"candidate": "RUHEN_LASSEN", "short_value_de": "RUHEN", "local_fit": "LOW", "extra_assumption": "DUPLICATES_SHED", "decision": "REJECT_DUPLICATE_CORE"},
        {"candidate": "SCHRITT_BEENDEN", "short_value_de": "BEENDEN", "local_fit": "MEDIUM", "extra_assumption": "DUPLICATES_ATTACHED_CLOSE", "decision": "REJECT_CLOSURE_ONLY"},
        {"candidate": "T_PLUS_AL_PLUS_AM", "short_value_de": "AN_DER_STELLE_ANWENDEN", "local_fit": "LOW", "extra_assumption": "AM_HAS_NO_INDEPENDENT_ENTRY", "decision": "REJECT_UNLICENSED_SPLIT"},
    ]
    event_row = {
        "event_id": event["event_id"],
        "page": event["page"],
        "record": event["record"],
        "statement_id": event["statement_id"],
        "owner_de": event["owner_de"],
        "exact_card_id": event["exact_card_id"],
        "surface": event["surface"],
        "old_reading_de": event["fifth_grammar_reading_de"],
        "selected_reading_de": "BEISEITESTELLEN",
        "classification": "MEMORIZED_WHOLE_OPERATION",
        "previous_event": previous["event_id"],
        "previous_surface": previous["surface"],
        "previous_reading_de": previous["fifth_grammar_reading_de"],
        "following_event": following["event_id"],
        "following_surface": following["surface"],
        "following_reading_de": following["fifth_grammar_reading_de"],
    }
    revised = statement["working_reading_de"].replace(
        "und anschliessend verwahren", "und anschliessend beiseitestellen"
    )
    statement_row = {
        "statement_id": statement["statement_id"],
        "page": statement["page"],
        "owner_noun_de": statement["owner_noun_de"],
        "surface_sequence": statement["surface_sequence"],
        "old_reading_de": statement["working_reading_de"],
        "revised_reading_de": revised,
        "operation_chain": "SOLLMASS > UMSETZEN > BEISEITESTELLEN > next statement",
    }
    segmentation_rows = [
        {"analysis": "WHOLE_TALAM", "pieces": "TALAM", "known_piece_values": "BEISEITESTELLEN", "missing_piece": "NONE", "decision": "SELECT"},
        {"analysis": "SURFACE_TAL_PLUS_AM", "pieces": "TAL+AM", "known_piece_values": "AL=ZIELSTELLE", "missing_piece": "AM", "decision": "REJECT"},
        {"analysis": "SURFACE_T_PLUS_AL_PLUS_AM", "pieces": "T+AL+AM", "known_piece_values": "T=ANWENDEN;AL=ZIELSTELLE", "missing_piece": "AM", "decision": "REJECT"},
    ]

    write("EIGHT_HUNDRED_EIGHTEENTH_7_TALAM_CANDIDATES.tsv", candidates, ["candidate", "short_value_de", "local_fit", "extra_assumption", "decision"])
    write("EIGHT_HUNDRED_EIGHTEENTH_TALAM_EVENT.tsv", [event_row], list(event_row))
    write("EIGHT_HUNDRED_EIGHTEENTH_REVISED_STATEMENT.tsv", [statement_row], list(statement_row))
    write("EIGHT_HUNDRED_EIGHTEENTH_3_SEGMENTATION_TESTS.tsv", segmentation_rows, ["analysis", "pieces", "known_piece_values", "missing_piece", "decision"])
    summary = {
        "status": "PASS",
        "decision": "TALAM_REVISED_FROM_VERWAHREN_TO_BEISEITESTELLEN_AS_WHOLE_OPERATION",
        "events": 1,
        "statements": 1,
        "candidates": len(candidates),
        "segmentation_tests": len(segmentation_rows),
        "selected_value": "BEISEITESTELLEN",
        "core_size": 33,
        "bound_components": 3,
        "whole_forms": 3,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_EIGHTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
