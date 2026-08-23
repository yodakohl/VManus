#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = rows("HUNDRED_TWENTY_SEVENTH_381_REVISED_EVENT_INTERLINEAR.tsv")
    statements = rows("HUNDRED_TWENTY_SEVENTH_116_REVISED_STATEMENTS.tsv")
    records = rows("HUNDRED_TWENTY_SEVENTH_ELEVEN_REVISED_RECORDS.tsv")
    checks = {
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "records_11": len(records) == 11,
        "event_serials_unique": len({row["event_serial"] for row in events}) == 381,
        "statement_ids_unique": len({row["statement_id"] for row in statements}) == 116,
        "shared_overlays_136": sum(row["reading_layer"] == "REVISED_SHARED_17" for row in events) == 136,
        "shared_statements_57": sum(row["shared_master_forms"] != "NONE" for row in statements) == 57,
        "all_records_have_text": all(row["continuous_record_de"] for row in records),
        "no_empty_cells": all(all(value for value in row.values()) for table in (events, statements, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
