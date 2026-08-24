#!/usr/bin/env python3
"""Validate the fluent 116-statement edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    statements = read("SIX_HUNDRED_SEVENTY_THIRD_116_FLUENT_STATEMENTS.tsv")
    records = read("SIX_HUNDRED_SEVENTY_THIRD_11_FLUENT_RECORDS.tsv")
    checks = {
        "one_hundred_sixteen_statements": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "three_hundred_eighty_one_events": sum(int(row["events"]) for row in statements) == 381,
        "eleven_records": len(records) == 11 and len({row["record"] for row in records}) == 11,
        "record_event_sum": sum(int(row["events"]) for row in records) == 381,
        "every_event_has_phrase": all(len(row["event_phrases_de"].split(" | ")) == int(row["events"]) for row in statements),
        "every_event_has_card": all(len(row["card_sequence"].split("|")) == int(row["events"]) for row in statements),
        "every_statement_fluent": all(row["fluent_workshop_reading_de"].endswith(".") for row in statements),
        "thirteen_hand_polished": sum(row["reading_source"] == "HAND_POLISHED" for row in statements) == 13,
        "all_grades_named": all(row["fluency_grade"] in {"CLEAN", "WORKABLE", "DENSE"} for row in statements),
        "no_placeholders": not any(term in row["fluent_workshop_reading_de"] for row in statements for term in ["UNKNOWN", "EXEMPLAR", "FORMAL"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
