#!/usr/bin/env python3
"""Validate the compact apprentice manual."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SIX_HUNDRED_SEVENTY_SIXTH_39_ROOT_TEACHING_ORDER.tsv")
    rules = read("SIX_HUNDRED_SEVENTY_SIXTH_16_APPRENTICE_RULES.tsv")
    signatures = read("SIX_HUNDRED_SEVENTY_SIXTH_RECIPE_SIGNATURES.tsv")
    predictions = read("SIX_HUNDRED_SEVENTY_SIXTH_12_PREDICTED_COMPOSITIONS.tsv")
    exceptions = read("SIX_HUNDRED_SEVENTY_SIXTH_3_WHOLE_COMMAND_EXCEPTIONS.tsv")
    checks = {
        "thirty_nine_roots": len(roots) == 39 and len({row["component"] for row in roots}) == 39,
        "nine_lessons": {int(row["lesson"]) for row in roots} == set(range(1, 10)),
        "sixteen_rules": len(rules) == 16 and [int(row["rule_no"]) for row in rules] == list(range(1, 17)),
        "signatures_cover_cards": sum(int(row["card_types"]) for row in signatures) == 173,
        "signatures_cover_events": sum(int(row["events"]) for row in signatures) == 381,
        "twelve_predictions": len(predictions) == 12,
        "all_predictions_absent": all(row["present_on_fixed_pages"] == "NO" for row in predictions),
        "all_predictions_nonspelling": all("DO_NOT_GENERATE" in row["surface_policy"] for row in predictions),
        "three_exceptions": len(exceptions) == 3 and {row["card_no"] for row in exceptions} == {"PROC005", "PROC034", "PROC043"},
        "endpoint_rule_present": any(row["rule_id"] == "ENDPOINT_LAST" for row in rules),
        "line_rule_present": any(row["rule_id"] == "LINE_IS_SPACE" for row in rules),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
