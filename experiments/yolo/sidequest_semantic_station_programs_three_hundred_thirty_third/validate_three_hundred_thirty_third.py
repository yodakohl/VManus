#!/usr/bin/env python3
"""Validate the twelve-program apprentice reduction."""

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


programs = rows("THREE_HUNDRED_THIRTY_THIRD_12_STATION_PROGRAMS.tsv")
mapping = rows("THREE_HUNDRED_THIRTY_THIRD_97_STATEMENT_PROGRAM_MAP.tsv")
owners = rows("THREE_HUNDRED_THIRTY_THIRD_16_OWNER_PROGRAM_PROFILES.tsv")
program_ids = {row["program_id"] for row in programs}

checks = {
    "exactly_12_programs": len(programs) == 12 and len(program_ids) == 12,
    "all_97_statements": len(mapping) == 97 and len({row["statement_id"] for row in mapping}) == 97,
    "all_281_events": sum(int(row["event_count"]) for row in mapping) == 281,
    "all_16_owners": len(owners) == 16 and len({row["owner_id"] for row in owners}) == 16,
    "every_program_primary": {row["primary_program_id"] for row in mapping} == program_ids,
    "primary_counts_reconcile": sum(int(row["primary_statement_count"]) for row in programs) == 97,
    "operation_counts_reconcile": sum(int(row["all_operation_count"]) for row in programs) == 281,
    "no_empty_reading": all(row["apprentice_reading_de"].strip() for row in mapping),
    "no_global_flow": all("global" not in row["apprentice_reading_de"].lower() for row in mapping),
    "no_sealed_page": all(row["page"] not in {"f84", "f84r"} for row in mapping),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_THIRTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
