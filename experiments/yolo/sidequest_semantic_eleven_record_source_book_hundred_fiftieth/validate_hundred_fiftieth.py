#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = rows("HUNDRED_FIFTIETH_381_SOURCE_EVENTS.tsv")
    statements = rows("HUNDRED_FIFTIETH_116_SOURCE_CLAUSES.tsv")
    records = rows("HUNDRED_FIFTIETH_ELEVEN_CONTINUOUS_RECORDS.tsv")
    checks = {
        "events_381": len(events) == 381,
        "serials_1_381": [int(row["event_serial"]) for row in events] == list(range(1, 382)),
        "statements_116": len(statements) == 116,
        "records_11": len(records) == 11,
        "terminal_90": sum(row["terminal_status"] == "TERMINAL" for row in statements) == 90,
        "open_26": sum(row["terminal_status"] == "NONCLOSE" for row in statements) == 26,
        "starts_11": sum(row["boundary_from_previous"] == "RECORD_START" for row in statements) == 11,
        "fresh_after_close_86": sum(row["boundary_from_previous"] == "FRESH_AFTER_CLOSE" for row in statements) == 86,
        "open_continuations_13": sum(row["boundary_from_previous"] == "CONTINUE_SAME_OWNER_OPEN" for row in statements) == 13,
        "owner_resets_6": sum(row["boundary_from_previous"] == "OWNER_RESET" for row in statements) == 6,
        "boundary_total": len(statements) - 11 == 105,
        "shared_events_251": sum(row["apprentice_layer"] == "LEHRWORT" for row in events) == 251,
        "local_events_130": sum(row["apprentice_layer"] == "LOKALKARTE" for row in events) == 130,
        "record_event_totals": sum(int(row["event_count"]) for row in records) == 381,
        "record_statement_totals": sum(int(row["statement_count"]) for row in records) == 116,
        "all_spoken": all(row["source_book_clause_de"] for row in statements),
        "no_empty_cells": all(all(v for v in row.values()) for table in (events, statements, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
