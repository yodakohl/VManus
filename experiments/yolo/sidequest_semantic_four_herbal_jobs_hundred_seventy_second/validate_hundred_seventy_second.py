#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    jobs = read("HUNDRED_SEVENTY_SECOND_4_HERBAL_JOBS.tsv")
    clauses = read("HUNDRED_SEVENTY_SECOND_11_NEW_JOB_CLAUSES.tsv")
    events = read("HUNDRED_SEVENTY_SECOND_65_EVENT_F10R_F56R_READING.tsv")
    sources = read("HUNDRED_SEVENTY_SECOND_HISTORICAL_ARTICLE_ARCHITECTURES.tsv")
    checks = {
        "four_distinct_jobs": len(jobs) == 4 and len({row["selected_job"] for row in jobs}) == 4,
        "all_herbal_event_count": sum(int(row["event_count"]) for row in jobs) == 100,
        "new_event_count": len(events) == 65,
        "new_event_serials": [int(row["event_serial"]) for row in events] == list(range(1, 39)) + list(range(74, 101)),
        "eleven_clauses": len(clauses) == 11,
        "all_selected_records": {row["record_unit_id"] for row in events} == {"H1", "H2", "H5"},
        "all_concrete": all(row["complete_clause_translation_de"].strip() for row in events),
        "no_dictionary_change": {row["dictionary_change"] for row in events} == {"NO"},
        "three_historical_architectures": len(sources) == 3,
        "sealed_absent": all(row["page"] in {"f10r", "f56r"} for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
