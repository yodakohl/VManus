#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_THIRTY_SIXTH_173_CARD_DICTIONARY.tsv")
    surfaces = rows("HUNDRED_THIRTY_SIXTH_230_SURFACE_REVERSE_KEY.tsv")
    events = rows("HUNDRED_THIRTY_SIXTH_381_PROSE_EVENTS.tsv")
    statements = rows("HUNDRED_THIRTY_SIXTH_116_TERSE_STATEMENTS.tsv")
    records = rows("HUNDRED_THIRTY_SIXTH_11_TERSE_RECORDS.tsv")
    jobs = rows("HUNDRED_THIRTY_SIXTH_FOUR_TERSE_JOBS.tsv")
    by_card = {r["master_card_id"]: r for r in cards}
    checks = {
        "cards_173": len(cards) == 173,
        "surfaces_230": len(surfaces) == 230,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "records_11": len(records) == 11,
        "jobs_4": len(jobs) == 4,
        "changed_cards_29": sum(r["period_revision"] == "SHORTENED_ACTIVE_CARD" for r in cards) == 29,
        "surface_values_match": all(r["current_spoken_default_de"] == by_card[r["master_card_id"]]["current_spoken_default_de"] for r in surfaces),
        "event_values_match": all(r["current_spoken_default_de"] == by_card[r["master_card_id"]]["current_spoken_default_de"] for r in events),
        "event_counts_by_record": sum(int(r["event_count"]) for r in records) == 381,
        "no_empty_cells": all(all(v for v in r.values()) for table in (cards, surfaces, events, statements, records, jobs) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
