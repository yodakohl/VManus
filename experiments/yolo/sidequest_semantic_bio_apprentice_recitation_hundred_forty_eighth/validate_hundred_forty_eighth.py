#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = rows("HUNDRED_FORTY_EIGHTH_281_EVENT_RECITATION.tsv")
    statements = rows("HUNDRED_FORTY_EIGHTH_97_STATEMENT_RECITATION.tsv")
    records = rows("HUNDRED_FORTY_EIGHTH_SIX_RECORD_SUMMARY.tsv")
    checks = {
        "events_281": len(events) == 281,
        "event_serials_101_381": [int(row["event_serial"]) for row in events] == list(range(101, 382)),
        "statements_97": len(statements) == 97,
        "records_6": len(records) == 6,
        "shared_events_196": sum(row["apprentice_layer"] == "LEHRWORT" for row in events) == 196,
        "local_events_85": sum(row["apprentice_layer"] == "LOKALKARTE" for row in events) == 85,
        "shared_types_43": len({row["master_card_id"] for row in events if row["apprentice_layer"] == "LEHRWORT"}) == 43,
        "local_types_81": len({row["master_card_id"] for row in events if row["apprentice_layer"] == "LOKALKARTE"}) == 81,
        "statement_event_totals": sum(int(row["shared_card_count"]) + int(row["local_card_count"]) for row in statements) == 281,
        "record_event_totals": sum(int(row["event_count"]) for row in records) == 281,
        "owner_present": all(row["local_image_owner"] and row["local_owner_label"] for row in events),
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
