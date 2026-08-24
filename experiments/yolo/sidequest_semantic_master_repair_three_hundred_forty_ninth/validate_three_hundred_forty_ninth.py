#!/usr/bin/env python3
"""Validate the three concrete master repairs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cases = read_tsv("THREE_HUNDRED_FORTY_NINTH_THREE_MISCOPIES.tsv")
    diffs = read_tsv("THREE_HUNDRED_FORTY_NINTH_EVENT_DIFFS.tsv")
    channels = read_tsv("THREE_HUNDRED_FORTY_NINTH_REDUNDANCY_CHANNELS.tsv")
    checks = {
        "three_distinct_cases": len(cases) == 3 and len({row["case_id"] for row in cases}) == 3,
        "three_layers": {row["layer"] for row in cases} == {"CARD_IDENTITY", "MATERIAL_THREAD", "SIX_SLOT_ORDER"},
        "three_event_diffs": len(diffs) == 3 and {row["case_id"] for row in diffs} == {row["case_id"] for row in cases},
        "six_redundancy_channels": len(channels) == 6,
        "each_case_has_two_channels": all(sum(row["detects_case"] == case["case_id"] for row in channels) == 2 for case in cases),
        "all_exactly_recovered": all(row["recovered_exactly"] == "YES" for row in cases),
        "no_new_meanings": all(row["new_meaning_needed"] == "NO" for row in cases),
        "surface_error_is_real_substitution": next(row for row in diffs if row["case_id"] == "M01_WRONG_CARD_SURFACE")["source_value"] == "Klarauszug" and next(row for row in diffs if row["case_id"] == "M01_WRONG_CARD_SURFACE")["miscopied_decode"] == "Kurzkontakt",
        "thread_repair_is_measured_portion": "Bemessene Portion" in next(row for row in cases if row["case_id"] == "M02_LOST_MATERIAL_THREAD")["exact_repair"],
        "reset_inserted_before_E182": "E181 und E182" in next(row for row in cases if row["case_id"] == "M03_MISSED_MICROCYCLE_RESET")["exact_repair"],
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FORTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
