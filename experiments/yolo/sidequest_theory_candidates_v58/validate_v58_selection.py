#!/usr/bin/env python3
"""Validate compact V58 adversarial selection and four complete rival panels."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SELECTED = ROOT / "V58_SELECTED_MODEL_COMPARISON.tsv"
PANELS = {
    "R1": ROOT / "V58_R1_COMPLETE_NONMEDICAL_READINGS.tsv",
    "R2": ROOT / "V58_R2_COMPLETE_NONMEDICAL_RIVAL.tsv",
    "R3": ROOT / "V58_R3_FOURTEEN_OPERATING_ENTRIES.tsv",
    "R4": ROOT / "V58_R4_COMPLETE_RIVAL.tsv",
}
OUT = ROOT / "V58_VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


selected = read_tsv(SELECTED)
panel_rows = {name: read_tsv(path) for name, path in PANELS.items()}
checks = {
    "ten_selected_axes": len(selected) == 10,
    "four_complete_fourteen_unit_panels": all(len(rows) == 14 for rows in panel_rows.values()),
    "all_selected_axes_decided": all(row["selection"].strip() for row in selected),
    "pure_waterwork_withdrawn": any(
        row["axis"] == "pure_waterwork" and row["selection"] == "WITHDRAW_PURE_WATERWORK"
        for row in selected
    ),
    "architecture_domain_neutral": any(
        row["axis"] == "architecture" and row["selection"] == "DOMAIN_NEUTRAL_ARCHITECTURE"
        for row in selected
    ),
    "sealed_f84": all("f84" not in "\t".join(row.values()).lower() for row in selected),
    "sealed_f84r": all("f84r" not in "\t".join(row.values()).lower() for row in selected),
}
payload = {
    "schema": "SIDEQUEST_V58_VALIDATION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "role_panels": 4,
        "units_per_panel": 14,
        "herbal_records": 5,
        "biological_records": 6,
        "astro_diagrams": 3,
        "prose_events": 381,
        "astro_groups": 395,
        "all_visible_groups": 776,
    },
    "native_role_scores": {
        "R1": {"rival": 82, "medical": 84, "scale": 100},
        "R2": {"rival": 80, "medical": 86, "scale": 100},
        "R3": {"rival": 10, "medical": 12, "scale": 16},
        "R4": {"rival": 28, "medical": 32, "scale": 40},
    },
}
OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if payload["status"] != "PASS":
    raise SystemExit(1)
print(json.dumps(payload, sort_keys=True))
