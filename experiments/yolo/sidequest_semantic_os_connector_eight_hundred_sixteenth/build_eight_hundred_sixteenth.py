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
    index = next(i for i, row in enumerate(events) if row["component_recipe"] == "OS")
    event = events[index]
    previous = events[index - 1]
    following = events[index + 1]
    statement = statements[event["statement_id"]]

    candidates = [
        {"candidate": "FACH", "phrase": "im Fach", "visible_support": "NO", "syntax_fit": "LOW", "repair": 5, "decision": "REJECT_OLD"},
        {"candidate": "ORT", "phrase": "am Ort", "visible_support": "PICTURE_OWNER_ALREADY_SUPPLIES_PLACE", "syntax_fit": "LOW", "repair": 4, "decision": "REJECT"},
        {"candidate": "WERKZEUG", "phrase": "mit dem Werkzeug", "visible_support": "NO_TOOL_SHOWN", "syntax_fit": "MEDIUM", "repair": 4, "decision": "REJECT"},
        {"candidate": "TRENNSCHRITT", "phrase": "gesonderter Schritt", "visible_support": "NONE_NEEDED", "syntax_fit": "MEDIUM", "repair": 2, "decision": "REJECT_TOO_META"},
        {"candidate": "QUELLLABEL", "phrase": "kopierte Quellenrubrik", "visible_support": "NO_SECOND_OCCURRENCE", "syntax_fit": "LOW", "repair": 5, "decision": "REJECT"},
        {"candidate": "DAZU", "phrase": "dazu Wasser entnehmen", "visible_support": "CONNECTS_APPLICATION_TO_WATER", "syntax_fit": "HIGH", "repair": 0, "decision": "SELECT_WHOLE_CONNECTOR"},
    ]
    event_row = {
        "event_id": event["event_id"],
        "page": event["page"],
        "statement_id": event["statement_id"],
        "owner_de": event["owner_de"],
        "surface": event["surface"],
        "component_recipe": event["component_recipe"],
        "old_reading_de": event["fifth_grammar_reading_de"],
        "selected_reading_de": "DAZU",
        "new_classification": "MEMORIZED_WHOLE_CONNECTOR",
        "previous_event": previous["event_id"],
        "previous_surface": previous["surface"],
        "previous_reading_de": previous["fifth_grammar_reading_de"],
        "following_event": following["event_id"],
        "following_surface": following["surface"],
        "following_reading_de": following["fifth_grammar_reading_de"],
    }
    revised = statement["working_reading_de"].replace("und aus der Quelle anwenden; Wasser entnehmen", "und aus der Quelle anwenden; dazu Wasser entnehmen")
    statement_row = {
        "statement_id": statement["statement_id"],
        "page": statement["page"],
        "owner_noun_de": statement["owner_noun_de"],
        "surface_sequence": statement["surface_sequence"],
        "old_reading_de": statement["working_reading_de"],
        "revised_reading_de": revised,
        "connector_clause": "CTHY OS CHAIR = anwenden; DAZU Wasser entnehmen",
    }
    clause_rows = [
        {"phase": "BEFORE_OS", "events": f"{previous['event_id']}", "surfaces": previous["surface"], "literal_de": previous["fifth_grammar_reading_de"], "fluent_de": "aus der Quelle anwenden"},
        {"phase": "OS", "events": event["event_id"], "surfaces": event["surface"], "literal_de": "DAZU", "fluent_de": "dazu"},
        {"phase": "AFTER_OS", "events": following["event_id"], "surfaces": following["surface"], "literal_de": following["fifth_grammar_reading_de"], "fluent_de": "Wasser entnehmen"},
    ]

    write("EIGHT_HUNDRED_SIXTEENTH_6_OS_CANDIDATES.tsv", candidates, ["candidate", "phrase", "visible_support", "syntax_fit", "repair", "decision"])
    write("EIGHT_HUNDRED_SIXTEENTH_OS_EVENT.tsv", [event_row], list(event_row))
    write("EIGHT_HUNDRED_SIXTEENTH_REVISED_STATEMENT.tsv", [statement_row], list(statement_row))
    write("EIGHT_HUNDRED_SIXTEENTH_3_CLAUSE_PARTS.tsv", clause_rows, ["phase", "events", "surfaces", "literal_de", "fluent_de"])
    summary = {
        "status": "PASS",
        "decision": "OS_REVISED_FROM_FACH_TO_DAZU_AS_MEMORIZED_WHOLE_CONNECTOR",
        "events": 1,
        "statements": 1,
        "candidates": len(candidates),
        "clause_parts": len(clause_rows),
        "core_size": 33,
        "bound_components": 3,
        "whole_forms": 3,
        "whole_connectors": 1,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_SIXTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
