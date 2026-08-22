#!/usr/bin/env python3
"""Validate the compact V53 selected Herbal edition."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TABLE = ROOT / "V53_SELECTED_FIVE_ARTICLES.tsv"
OUT = ROOT / "V53_VALIDATION.json"

with TABLE.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))

checks = {
    "five_articles": len(rows) == 5,
    "expected_folios": {row["folio_record"].split("_")[0] for row in rows}
    == {"f10r", "f11r", "f55v", "f56r"},
    "twenty_fields": sum(int(row["field_count"]) for row in rows) == 20,
    "one_hundred_events": sum(int(row["event_count"]) for row in rows) == 100,
    "all_have_complete_reading": all(row["selected_complete_working_translation_German"].strip() for row in rows),
    "all_have_contradiction": all(row["main_contradiction"].strip() for row in rows),
    "sealed_f84": all("f84" not in row["folio_record"].lower() for row in rows),
    "sealed_f84r": all("f84r" not in row["folio_record"].lower() for row in rows),
}
payload = {
    "schema": "SIDEQUEST_V53_VALIDATION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "articles": len(rows),
        "fields": sum(int(row["field_count"]) for row in rows),
        "events": sum(int(row["event_count"]) for row in rows),
    },
}
OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if payload["status"] != "PASS":
    raise SystemExit(1)
print(json.dumps(payload, sort_keys=True))
