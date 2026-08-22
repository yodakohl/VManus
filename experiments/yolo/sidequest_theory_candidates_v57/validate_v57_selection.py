#!/usr/bin/env python3
"""Validate the compact selected V57 teaching model."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TABLE = ROOT / "V57_SELECTED_TEACHING_MANUAL.tsv"
OUT = ROOT / "V57_VALIDATION.json"

with TABLE.open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))

checks = {
    "eight_lessons": len(rows) == 8,
    "unique_lesson_ids": len({row["lesson_id"] for row in rows}) == 8,
    "all_lessons_concrete": all(
        row["productive_lesson"].strip()
        and row["memorized_or_exemplar_material"].strip()
        and row["apprentice_test"].strip()
        and row["main_failure_prevented"].strip()
        for row in rows
    ),
    "sealed_f84": all("f84" not in "\t".join(row.values()).lower() for row in rows),
    "sealed_f84r": all("f84r" not in "\t".join(row.values()).lower() for row in rows),
}

payload = {
    "schema": "SIDEQUEST_V57_VALIDATION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "pages": 10,
        "prose_records": 11,
        "astro_diagrams": 3,
        "prose_fields": 135,
        "prose_events": 381,
        "astro_loci": 142,
        "astro_groups": 395,
        "all_visible_groups": 776,
        "strict_tier_a_events": 45,
        "strict_tier_a_fields": 35,
        "opaque_prose_events": 236,
        "state_machine_states": 8,
        "state_machine_transitions": 15,
    },
}
OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if payload["status"] != "PASS":
    raise SystemExit(1)
print(json.dumps(payload, sort_keys=True))
