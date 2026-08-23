#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


event_patterns = read("TWENTY_EIGHTH_EVENT_IDIOMS.tsv")
event_occurrences = read("TWENTY_EIGHTH_EVENT_IDIOM_OCCURRENCES.tsv")
clause_patterns = read("TWENTY_EIGHTH_CLAUSE_IDIOMS.tsv")
clause_occurrences = read("TWENTY_EIGHTH_CLAUSE_IDIOM_OCCURRENCES.tsv")
statements = read("TWENTY_EIGHTH_116_STATEMENT_IDIOM_INDEX.tsv")
checks = {
    "seventeen_event_idioms": len(event_patterns) == 17,
    "seventeen_clause_idioms": len(clause_patterns) == 17,
    "all_event_idioms_recur": all(int(row["occurrence_count"]) >= 2 and int(row["record_count"]) >= 2 for row in event_patterns),
    "all_clause_idioms_recur": all(int(row["occurrence_count"]) >= 2 and int(row["record_count"]) >= 2 for row in clause_patterns),
    "event_occurrence_ids_unique": len({row["occurrence_id"] for row in event_occurrences}) == len(event_occurrences),
    "clause_occurrence_ids_unique": len({row["occurrence_id"] for row in clause_occurrences}) == len(clause_occurrences),
    "116_statements": len(statements) == 116,
    "381_groups": sum(int(row["group_count"]) for row in statements) == 381,
    "residual_bounds": all(0 <= int(row["residual_events"]) <= int(row["group_count"]) for row in statements),
    "phrasebook": (HERE / "TWENTY_EIGHTH_WORKSHOP_PHRASEBOOK.md").exists(),
    "report": (HERE / "TWENTY_EIGHTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(
    sealed not in path.read_text(encoding="utf-8").lower()
    for path in HERE.iterdir()
    if path.is_file()
)
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
