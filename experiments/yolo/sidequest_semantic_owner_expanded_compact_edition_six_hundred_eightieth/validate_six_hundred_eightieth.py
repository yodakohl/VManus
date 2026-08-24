#!/usr/bin/env python3
"""Validate the compact owner-expanded statement edition."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_eightieth.py")], check=True)
    statements = read("SIX_HUNDRED_EIGHTIETH_116_COMPACT_OWNER_STATEMENTS.tsv")
    records = read("SIX_HUNDRED_EIGHTIETH_11_CONTINUOUS_OWNER_RECORDS.tsv")
    owners = read("SIX_HUNDRED_EIGHTIETH_20_OWNER_NOUNS.tsv")
    checks = {
        "one_hundred_sixteen_statements": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "three_hundred_eighty_one_events": sum(int(row["events"]) for row in statements) == 381,
        "eleven_records": len(records) == 11 and {row["record"] for row in records} == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"},
        "record_event_total": sum(int(row["events"]) for row in records) == 381,
        "twenty_owner_nouns": len(owners) == 20,
        "all_owner_nouns_present": all(row["owner_noun_de"] for row in statements),
        "all_compact_readings_present": all(row["compact_atomic_sequence_de"] and row["compact_owner_reading_de"] for row in statements),
        "surface_event_counts_match": all(len(row["surface_sequence"].split()) == int(row["events"]) for row in statements),
        "compact_event_counts_match": all(len(row["compact_atomic_sequence_de"].split(" | ")) == int(row["events"]) for row in statements),
        "fixed_pages_only": {row["page"] for row in statements} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
