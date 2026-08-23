#!/usr/bin/env python3
"""Validate the unified apprentice grammar."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    primitives = rows("NINETY_THIRD_20_UNIFIED_SOURCE_PRIMITIVES.tsv")
    rules = rows("NINETY_THIRD_12_APPRENTICE_RULES.tsv")
    statements = rows("NINETY_THIRD_116_UNIFIED_STATEMENT_GRAMMAR.tsv")
    records = rows("NINETY_THIRD_11_RECORD_ROUNDTRIP.tsv")
    used = Counter(part for row in statements for part in row["unified_primitive_sequence"].split(">"))
    checks = {
        "primitives_20": len(primitives) == 20,
        "all_primitives_used": set(used) == {row["primitive_id"] for row in primitives},
        "rules_12": len(rules) == 12,
        "statements_116": len(statements) == 116,
        "statement_order_complete": [int(row["statement_order"]) for row in statements] == list(range(1, 117)),
        "events_381": sum(int(row["event_count"]) for row in statements) == 381,
        "records_11": len(records) == 11,
        "record_statements_116": sum(int(row["statement_count"]) for row in records) == 116,
        "record_events_381": sum(int(row["event_count"]) for row in records) == 381,
        "owner_selected_each_record": all(int(row["owner_select_count"]) >= 1 for row in records),
        "all_roundtrips_complete": all(row["forward_status"].endswith("COMPLETE") and row["backward_status"].endswith("COMPLETE") for row in records),
        "fixed_pages_only": set(row["page"] for row in statements) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in statements + records),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "primitive_occurrences": dict(used)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
