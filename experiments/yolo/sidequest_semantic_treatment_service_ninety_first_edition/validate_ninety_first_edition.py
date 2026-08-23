#!/usr/bin/env python3
"""Validate the treatment/service split."""

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
    statements = rows("NINETY_FIRST_97_TREATMENT_SERVICE_MAP.tsv")
    records = rows("NINETY_FIRST_6_RECORD_DUAL_MODE_EDITION.tsv")
    cross = rows("NINETY_FIRST_MODE_BY_MACRO_CROSSTAB.tsv")
    rules = rows("NINETY_FIRST_5_MODE_RULES.tsv")
    modes = Counter(row["primary_mode"] for row in statements)
    checks = {
        "statements_97": len(statements) == 97,
        "events_281": sum(int(row["event_count"]) for row in statements) == 281,
        "records_6": len(records) == 6,
        "record_counts_match": sum(int(row["statement_count"]) for row in records) == 97 and sum(int(row["event_count"]) for row in records) == 281,
        "treatment_87": modes["TREATMENT_FACING_VISIBLE_HUMAN_OWNER"] == 87,
        "service_10": modes["SERVICE_FACING_NO_HUMAN_OWNER"] == 10,
        "b4_split_10_6": next(row for row in records if row["record_unit_id"] == "B4")["treatment_statement_count"] == "10" and next(row for row in records if row["record_unit_id"] == "B4")["service_statement_count"] == "6",
        "b5_b6_service_only": all(row["treatment_statement_count"] == "0" for row in records if row["record_unit_id"] in {"B5", "B6"}),
        "rules_5": len(rules) == 5,
        "cross_sum_97": sum(int(row["statement_count"]) for row in cross) == 97,
        "no_disease_or_anatomy": all(row["disease_or_named_body_part"] == "NONE" for row in statements),
        "fixed_pages_only": set(row["page"] for row in statements) == {"f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in statements + records),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
