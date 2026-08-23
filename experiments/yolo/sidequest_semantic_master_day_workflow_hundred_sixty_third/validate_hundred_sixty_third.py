#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = rows("HUNDRED_SIXTY_THIRD_79_EVENT_MASTER_DAY_INTERLINEAR.tsv")
    clauses = rows("HUNDRED_SIXTY_THIRD_26_CLAUSE_MASTER_DAY_EDITION.tsv")
    phases = rows("HUNDRED_SIXTY_THIRD_6_WORKFLOW_PHASES.tsv")
    checks = {
        "events_79": len(events) == 79,
        "events_unique": len({row["event_serial"] for row in events}) == 79,
        "H3_events_17": sum(row["record_unit_id"] == "H3" for row in events) == 17,
        "B2_events_62": sum(row["record_unit_id"] == "B2" for row in events) == 62,
        "clauses_26": len(clauses) == 26,
        "H3_clauses_4": sum(row["record_unit_id"] == "H3" for row in clauses) == 4,
        "B2_clauses_22": sum(row["record_unit_id"] == "B2" for row in clauses) == 22,
        "phases_6": len(phases) == 6,
        "all_clauses_translated": all(row["fluent_workshop_translation_de"] for row in clauses),
        "all_events_bound_to_translation": all(row["complete_clause_translation_de"] for row in events),
        "day_link_marked_speculative": all(row["speculative_day_link"] == "WORKSHOP_SCENARIO_NOT_VISIBLE_CROSS_PAGE_POINTER" for row in clauses),
        "fixed_pages_only": {row["page"] for row in events} == {"f11r", "f82r"},
        "no_empty_cells": all(all(value for value in row.values()) for table in (events, clauses, phases) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
