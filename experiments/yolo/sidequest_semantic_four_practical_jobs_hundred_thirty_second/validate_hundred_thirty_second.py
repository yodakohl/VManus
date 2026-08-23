#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    jobs = rows("HUNDRED_THIRTY_SECOND_FOUR_JOB_PROFILES.tsv")
    steps = rows("HUNDRED_THIRTY_SECOND_ELEVEN_JOB_STEPS.tsv")
    events = rows("HUNDRED_THIRTY_SECOND_381_EVENT_JOB_LEDGER.tsv")
    checks = {
        "jobs_4": len(jobs) == 4,
        "steps_11": len(steps) == 11,
        "events_381": len(events) == 381,
        "record_ids_unique": len({row["record_unit_id"] for row in steps}) == 11,
        "event_serials_unique": len({row["event_serial"] for row in events}) == 381,
        "job_event_sum": sum(int(row["event_count"]) for row in jobs) == 381,
        "step_event_sum": sum(int(row["event_count"]) for row in steps) == 381,
        "each_job_has_what_and_how": all(row["herbal_records"] and row["biological_records"] for row in jobs),
        "all_links_provisional": all("NO_WRITTEN_CROSS_PAGE_POINTER" in row["link_status"] for row in jobs),
        "no_empty_cells": all(all(value for value in row.values()) for table in (jobs, steps, events) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
