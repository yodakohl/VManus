#!/usr/bin/env python3
"""Validate clause-to-owner bindings."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    clauses = rows("HUNDRED_SIXTH_254_CLAUSE_OWNER_BINDING.tsv")
    statements = rows("HUNDRED_SIXTH_116_STATEMENT_OWNER_BINDING.tsv")
    summary = rows("HUNDRED_SIXTH_OWNER_SUMMARY.tsv")
    events = [event for row in clauses for event in row["member_event_ids"].split("|")]
    checks = {
        "clauses_254": len(clauses) == 254,
        "fusion_ids_unique": len({row["fusion_unit_id"] for row in clauses}) == 254,
        "events_381_once": len(events) == 381 and len(set(events)) == 381,
        "statements_116": len(statements) == 116,
        "clause_sum_254": sum(int(row["clause_count"]) for row in statements) == 254,
        "owners_nonempty": all(row["selected_visible_owners"] for row in clauses),
        "noun_sources_known": set(row["primary_noun_source"] for row in clauses) <= {"TEXT_NAMES_OBJECT__OWNER_LIMITS_REFERENT", "OWNER_RESOLVES_GENERIC_TEXT_ITEM", "OWNER_SUPPLIES_ELLIPTIC_PRIMARY_NOUN", "MIXED_TEXT_AND_OWNER_OBJECT"},
        "summary_covers_two_dimensions": {row["dimension"] for row in summary} == {"PRIMARY_NOUN_SOURCE", "OWNER_ACCESSIBILITY"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in clauses),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
