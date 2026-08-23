#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = rows("HUNDRED_FORTY_NINTH_100_EVENT_RECITATION.tsv")
    statements = rows("HUNDRED_FORTY_NINTH_19_STATEMENT_RECITATION.tsv")
    records = rows("HUNDRED_FORTY_NINTH_FIVE_RECORD_SUMMARY.tsv")
    checks = {
        "events_100": len(events) == 100,
        "event_serials_1_100": [int(row["event_serial"]) for row in events] == list(range(1, 101)),
        "statements_19": len(statements) == 19,
        "records_5": len(records) == 5,
        "shared_events_55": sum(row["apprentice_layer"] == "LEHRWORT" for row in events) == 55,
        "local_events_45": sum(row["apprentice_layer"] == "LOKALKARTE" for row in events) == 45,
        "shared_types_21": len({row["master_card_id"] for row in events if row["apprentice_layer"] == "LEHRWORT"}) == 21,
        "local_types_45": len({row["master_card_id"] for row in events if row["apprentice_layer"] == "LOKALKARTE"}) == 45,
        "statement_event_totals": sum(int(row["shared_card_count"]) + int(row["local_card_count"]) for row in statements) == 100,
        "record_event_totals": sum(int(row["event_count"]) for row in records) == 100,
        "one_owner_per_record": all(len({row["whole_plant_owner"] for row in events if row["record_unit_id"] == record["record_unit_id"]}) == 1 for record in records),
        "all_event_tokens_spoken": all(row["spoken_token_de"] for row in events),
        "all_statements_recited": all(row["terse_apprentice_recitation_de"] for row in statements),
        "no_empty_cells": all(all(v for v in row.values()) for table in (events, statements, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
