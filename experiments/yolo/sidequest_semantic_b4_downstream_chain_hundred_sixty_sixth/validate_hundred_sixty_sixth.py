#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = rows("HUNDRED_SIXTY_SIXTH_30_EVENT_B4_DOWNSTREAM.tsv")
    clauses = rows("HUNDRED_SIXTY_SIXTH_9_CLAUSE_B4_DOWNSTREAM.tsv")
    phases = rows("HUNDRED_SIXTY_SIXTH_3_B4_DOWNSTREAM_PHASES.tsv")
    checks = {
        "events_30": len(events) == 30,
        "serial_range_332_361": [int(row["event_serial"]) for row in events] == list(range(332, 362)),
        "clauses_9": len(clauses) == 9,
        "statement_ids_exact": [row["statement_id"] for row in clauses] == [f"B4-S{i:03d}" for i in range(8, 17)],
        "phases_3": len(phases) == 3,
        "phase_events_reconcile": sum(int(row["event_count"]) for row in phases) == 30,
        "all_events_translated": all(row["complete_clause_translation_de"] for row in events),
        "all_clauses_translated": all(row["fluent_downstream_translation_de"] for row in clauses),
        "fixed_page": {row["page"] for row in events} == {"f83r"},
        "no_empty_cells": all(all(value for value in row.values()) for table in (events, clauses, phases) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
