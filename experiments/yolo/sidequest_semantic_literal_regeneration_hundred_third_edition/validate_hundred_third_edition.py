#!/usr/bin/env python3
"""Validate the regenerated literal clauses and statements."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    clauses = rows("HUNDRED_THIRD_254_ATOMIC_CLAUSES.tsv")
    statements = rows("HUNDRED_THIRD_116_REGENERATED_STATEMENTS.tsv")
    repairs = rows("HUNDRED_THIRD_FORWARD_OBJECT_REPAIRS.tsv")
    member_events = [event for row in clauses for event in row["member_event_ids"].split("|")]
    checks = {
        "clauses_254": len(clauses) == 254,
        "fusion_ids_unique": len({row["fusion_unit_id"] for row in clauses}) == 254,
        "member_events_381": len(member_events) == 381,
        "member_events_unique": len(set(member_events)) == 381,
        "statements_116": len(statements) == 116,
        "statement_clause_sum_254": sum(int(row["fusion_unit_count"]) for row in statements) == 254,
        "forward_repairs_present": len(repairs) > 0,
        "all_literal_complete": all(row["literal_workshop_clause_de"].startswith("Vorgang=") for row in clauses),
        "all_statements_complete": all(row["generated_atomic_literal_de"].endswith(".") for row in statements),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in clauses),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
