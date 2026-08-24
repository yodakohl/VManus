#!/usr/bin/env python3
"""Validate the repaired Biological edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    changed = read("THREE_HUNDRED_THIRTY_SECOND_18_CHANGED_BIO_CARDS.tsv")
    events = read("THREE_HUNDRED_THIRTY_SECOND_281_REPAIRED_BIO_EVENTS.tsv")
    statements = read("THREE_HUNDRED_THIRTY_SECOND_97_REPAIRED_BIO_STATEMENTS.tsv")
    records = read("THREE_HUNDRED_THIRTY_SECOND_SIX_REPAIRED_RECORDS.tsv")
    checks = {
        "eighteen_changed_cards": len(changed) == 18,
        "eighty_two_changed_events": sum(int(x["event_count"]) for x in changed) == 82,
        "two_hundred_eighty_one_events": len(events) == 281 and len({x["event_id"] for x in events}) == 281,
        "ninety_seven_statements": len(statements) == 97 and sum(len(x["event_ids"].split("|")) for x in statements) == 281,
        "six_records": len(records) == 6 and {x["record_unit_id"] for x in records} == {"B1", "B2", "B3", "B4", "B5", "B6"},
        "record_counts_reconcile": sum(int(x["event_count"]) for x in records) == 281 and sum(int(x["statement_count"]) for x in records) == 97,
        "all_events_owned": all(x["owner_id"] and x["station_role"] for x in events),
        "all_statements_translated": all(x["fluent_station_translation_de"] for x in statements),
        "no_global_flow": all(x["global_flow_claim"] == "NONE" for x in statements + records),
        "no_superseded_values": not any(x["atomic_value_de"] in {"Frischspülung", "Vollwaschung", "Langbearbeitung"} for x in events),
        "no_sealed_page": all("f84" not in x["page"].lower() for x in events + records),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_THIRTY_SECOND_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
