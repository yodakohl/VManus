#!/usr/bin/env python3
"""Validate the compact selected V54 Biological edition."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TABLE = ROOT / "V54_SELECTED_SIX_BIO_RECORDS.tsv"
OUT = ROOT / "V54_VALIDATION.json"

with TABLE.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))

checks = {
    "six_records": len(rows) == 6,
    "expected_folios": {row["folio"] for row in rows} == {"f81v", "f82r", "f83r"},
    "one_hundred_fifteen_fields": sum(int(row["field_count"]) for row in rows) == 115,
    "two_hundred_eighty_one_events": sum(int(row["event_count"]) for row in rows) == 281,
    "complete_readings": all(row["complete_working_translation_German"].strip() for row in rows),
    "explicit_rivals": all(row["strongest_rival"].strip() for row in rows),
    "sealed_f84": all("f84" not in row["folio"].lower() for row in rows),
    "sealed_f84r": all("f84r" not in row["folio"].lower() for row in rows),
}
payload = {
    "schema": "SIDEQUEST_V54_VALIDATION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "records": len(rows),
        "fields": sum(int(row["field_count"]) for row in rows),
        "events": sum(int(row["event_count"]) for row in rows),
        "formal_closed_fields": 85,
        "formal_open_fields": 30,
        "selected_anchor_events": 113,
        "opaque_events": 168,
    },
}
OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if payload["status"] != "PASS":
    raise SystemExit(1)
print(json.dumps(payload, sort_keys=True))
