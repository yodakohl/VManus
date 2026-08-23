#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    customs = rows("HUNDRED_SIXTY_FIRST_13_RECURRENT_CUSTOMS.tsv")
    trace = rows("HUNDRED_SIXTY_FIRST_251_CUSTOM_RENDER_TRACE.tsv")
    records = rows("HUNDRED_SIXTY_FIRST_11_RECORD_CUSTOM_SUMMARY.tsv")
    checks = {
        "customs_13": len(customs) == 13,
        "record_accents_3": sum(row["custom_type"] == "RECORD_ACCENT" for row in customs) == 3,
        "card_position_customs_7": sum(row["custom_type"] == "CARD_POSITION_CUSTOM" for row in customs) == 7,
        "record_card_customs_3": sum(row["custom_type"] == "RECORD_CARD_CUSTOM" for row in customs) == 3,
        "events_251": len(trace) == 251,
        "events_unique": len({row["event_serial"] for row in trace}) == 251,
        "records_11": len(records) == 11,
        "habit_matches_209": sum(row["habit_match"] == "YES" for row in trace) == 209,
        "remaining_habit_overrides_42": sum(row["habit_match"] == "NO" for row in trace) == 42,
        "exact_surfaces_187": sum(row["exact_surface_match"] == "YES" for row in trace) == 187,
        "second_spellings_22": sum(row["apprentice_treatment"] == "SECOND_REGISTERED_SPELLING_IN_CORRECT_HABIT" for row in trace) == 22,
        "all_master_recovery_exact": all(row["master_recovery"] == "EXACT" for row in trace),
        "record_counts_reconcile": sum(int(row["shared_events"]) for row in records) == 251,
        "no_empty_cells": all(all(value for value in row.values()) for table in (customs, trace, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
