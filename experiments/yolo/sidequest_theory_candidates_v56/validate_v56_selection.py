#!/usr/bin/env python3
"""Validate the compact selected V56 cross-register phrasebook."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TABLE = ROOT / "V56_SELECTED_SHARED_PHRASEBOOK.tsv"
OUT = ROOT / "V56_VALIDATION.json"

with TABLE.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))

checks = {
    "twelve_selected_rows": len(rows) == 12,
    "four_primary": sum(row["status"] == "KEEP_PRIMARY" for row in rows) == 4,
    "eight_exploratory": sum(row["status"] == "EXPLORATORY_SHARED_MNEMONIC" for row in rows) == 8,
    "both_register_expansions": all(row["herbal_default_expansion"].strip() and row["bio_default_expansion"].strip() for row in rows),
    "all_have_limits": all(row["main_limit"].strip() for row in rows),
    "sealed_f84": all("f84" not in "\t".join(row.values()).lower() for row in rows),
    "sealed_f84r": all("f84r" not in "\t".join(row.values()).lower() for row in rows),
}
payload = {
    "schema": "SIDEQUEST_V56_VALIDATION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "shared_exact_joint_tuple_types_audited": 17,
        "shared_herbal_events": 44,
        "shared_bio_events": 92,
        "shared_events": 136,
        "tier_a_events_all_prose": 45,
        "tier_a_fields_all_prose": 35,
        "tier_b_bridge_events": 96,
    },
}
OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if payload["status"] != "PASS":
    raise SystemExit(1)
print(json.dumps(payload, sort_keys=True))
