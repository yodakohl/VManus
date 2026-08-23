#!/usr/bin/env python3
"""Validate the complete continuous prose translation."""

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
    statements = rows("EIGHTY_NINTH_116_CONTINUOUS_STATEMENT_TRANSLATION.tsv")
    events = rows("EIGHTY_NINTH_381_EVENT_STATEMENT_BINDING.tsv")
    crossing = rows("EIGHTY_NINTH_18_LINE_CROSSING_STATEMENTS.tsv")
    record_counts = Counter(row["record_unit_id"] for row in statements)
    event_serials = [int(row["event_serial"]) for row in events]
    statement_event_serials = [int(value) for row in statements for value in row["event_serials"].split("|")]
    checks = {
        "statement_count_116": len(statements) == 116,
        "statement_ids_unique": len({row["statement_id"] for row in statements}) == 116,
        "event_count_381": len(events) == 381,
        "event_serial_complete": event_serials == list(range(1, 382)),
        "statement_event_partition": sorted(statement_event_serials) == list(range(1, 382)),
        "line_crossing_count_18": len(crossing) == 18,
        "eleven_records": len(record_counts) == 11,
        "expected_record_counts": record_counts == Counter({"H1": 2, "H2": 3, "H3": 4, "H4": 4, "H5": 6, "B1": 21, "B2": 22, "B3": 34, "B4": 16, "B5": 3, "B6": 1}),
        "all_translations_complete": all(row["status"] == "COMPLETE_WORKING_TRANSLATION" and row["card_near_workshop_reading_de"] and row["concrete_source_expansion_de"] for row in statements),
        "line_end_rule_fixed": all(row["sentence_boundary_rule"] == "STATEMENT_BOUNDARY__NEVER_INFERRED_FROM_LINE_END" for row in statements),
        "fixed_pages_only": set(row["page"] for row in statements) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in statements + events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "record_statement_counts": dict(record_counts)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
