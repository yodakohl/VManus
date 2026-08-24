#!/usr/bin/env python3

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


words = rows("THREE_HUNDRED_FORTY_SECOND_FIVE_RESULT_WORDS.tsv")
assignments = rows("THREE_HUNDRED_FORTY_SECOND_SIX_RECORD_RESULT_ASSIGNMENTS.tsv")
events = rows("THREE_HUNDRED_FORTY_SECOND_TERMINAL_WINDOW_EVENTS.tsv")
counts = Counter(row["result_id"] for row in assignments)
checks = {
    "five_result_words": len(words) == 5 and len({row["result_id"] for row in words}) == 5,
    "six_bio_records": len(assignments) == 6 and {row["record_unit_id"] for row in assignments} == {"B1", "B2", "B3", "B4", "B5", "B6"},
    "one_shared_class": sum(count > 1 for count in counts.values()) == 1,
    "klarabzug_shared_by_b2_b4": next(row for row in words if row["result_word_de"] == "Klarabzug")["records"] == "B2|B4",
    "four_application_shelves": sum(row["shelf_type"] == "APPLICATION_SHELF" for row in assignments) == 4,
    "two_work_shelves": sum(row["shelf_type"] == "WORK_SHELF" for row in assignments) == 2,
    "four_cycles_each": all(row["terminal_microcycle_count"] == "4" for row in assignments),
    "terminal_events_unique": len(events) == len({row["event_id"] for row in events}),
    "no_next_pointer": all(row["next_pointer"] == "NONE_VISIBLE__LOCAL_SHELF" for row in assignments),
    "fixed_pages_only": {row["page"] for row in assignments} == {"f81v", "f82r", "f83r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in assignments),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_FORTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
