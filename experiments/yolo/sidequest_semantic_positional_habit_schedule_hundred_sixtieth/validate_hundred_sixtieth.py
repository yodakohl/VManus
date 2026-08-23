#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    rules = rows("HUNDRED_SIXTIETH_9_POSITIONAL_RULES.tsv")
    trace = rows("HUNDRED_SIXTIETH_251_POSITIONAL_RENDER_TRACE.tsv")
    records = rows("HUNDRED_SIXTIETH_11_RECORD_POSITIONAL_SCHEDULE.tsv")
    checks = {
        "rules_9": len(rules) == 9,
        "events_251": len(trace) == 251,
        "events_unique": len({row["event_serial"] for row in trace}) == 251,
        "records_11": len(records) == 11,
        "habit_matches_182": sum(row["habit_match"] == "YES" for row in trace) == 182,
        "habit_local_choices_69": sum(row["habit_match"] == "NO" for row in trace) == 69,
        "exact_surface_matches_160": sum(row["exact_surface_match"] == "YES" for row in trace) == 160,
        "second_spellings_22": sum(row["apprentice_treatment"] == "USE_REGISTERED_SECOND_SPELLING_IN_PREDICTED_HABIT" for row in trace) == 22,
        "local_habit_choices_69": sum(row["apprentice_treatment"] == "USE_LOCAL_REGISTERED_HABIT_AND_SPELLING" for row in trace) == 69,
        "all_master_recovery_exact": all(row["master_recovery"] == "EXACT" for row in trace),
        "record_counts_reconcile": sum(int(row["shared_events"]) for row in records) == 251,
        "no_empty_cells": all(all(value for value in row.values()) for table in (rules, trace, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
