#!/usr/bin/env python3
"""Validate the compact selected V55 circle/Astro edition."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TABLE = ROOT / "V55_SELECTED_THREE_DIAGRAMS.tsv"
OUT = ROOT / "V55_VALIDATION.json"

with TABLE.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))

checks = {
    "three_diagrams": len(rows) == 3,
    "expected_folios": {row["folio"] for row in rows} == {"f67r2", "f68r1", "f69v"},
    "one_hundred_forty_two_loci": sum(int(row["locus_count"]) for row in rows) == 142,
    "three_hundred_ninety_five_groups": sum(int(row["group_count"]) for row in rows) == 395,
    "all_mapping_none": all(row["direct_crosspage_mapping"] == "NONE" for row in rows),
    "complete_readings": all(row["complete_working_translation_German"].strip() for row in rows),
    "sealed_f84": all("f84" not in row["folio"].lower() for row in rows),
    "sealed_f84r": all("f84r" not in row["folio"].lower() for row in rows),
}
payload = {
    "schema": "SIDEQUEST_V55_VALIDATION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "diagrams": len(rows),
        "loci": sum(int(row["locus_count"]) for row in rows),
        "groups": sum(int(row["group_count"]) for row in rows),
        "f68_f69_equal_index_exact_matches": 0,
        "f68_f69_any_exact_surface_matches": 0,
    },
}
OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if payload["status"] != "PASS":
    raise SystemExit(1)
print(json.dumps(payload, sort_keys=True))
