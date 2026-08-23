#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    audit = rows("HUNDRED_FIFTY_FIRST_13_OPEN_CARRY_AUDIT.tsv")
    clauses = rows("HUNDRED_FIFTY_FIRST_116_CARRY_AWARE_CLAUSES.tsv")
    records = rows("HUNDRED_FIFTY_FIRST_ELEVEN_CARRY_AWARE_RECORDS.tsv")
    checks = {
        "carries_13": len(audit) == 13,
        "unique_next_statements": len({row["next_statement_id"] for row in audit}) == 13,
        "clauses_116": len(clauses) == 116,
        "records_11": len(records) == 11,
        "all_open_boundaries_named": {row["statement_id"] for row in clauses if row["boundary_from_previous"] == "CONTINUE_SAME_OWNER_OPEN"} == {row["next_statement_id"] for row in audit},
        "carry_connectives_replaced": all(row["connective_de"] != "weiter:" for row in clauses if row["boundary_from_previous"] == "CONTINUE_SAME_OWNER_OPEN"),
        "other_boundaries_unchanged": all(row["connective_de"] in {"Neuer Schritt:", "weiter:"} or row["connective_de"].startswith("Besitzer »") or row["connective_de"].startswith("Neuer Besitzer »") for row in clauses if row["boundary_from_previous"] != "CONTINUE_SAME_OWNER_OPEN"),
        "record_carry_totals": sum(int(row["explicit_carry_count"]) for row in records) == 13,
        "all_registers_concrete": all(row["carried_registers"] and row["spoken_carry_de"] for row in audit),
        "no_empty_cells": all(all(v for v in row.values()) for table in (audit, clauses, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
