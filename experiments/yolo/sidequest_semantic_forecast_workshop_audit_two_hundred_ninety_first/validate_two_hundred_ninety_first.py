#!/usr/bin/env python3
"""Validate the bounded ten-page workshop forecast audit."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    audit = read_tsv("TWO_HUNDRED_NINETY_FIRST_12_FORECAST_AUDIT.tsv")
    near = read_tsv("TWO_HUNDRED_NINETY_FIRST_OBSERVED_NEAR_MATCHES.tsv")
    counts = Counter(row["workshop_decision"] for row in audit)
    checks = {
        "twelve_forecasts": len(audit) == 12,
        "forecast_numbers": [int(row["forecast"]) for row in audit] == list(range(1, 13)),
        "no_exact_old_predicted_surface": all(row["old_predicted_surface_exact_hits"] == "0" for row in audit),
        "four_already_split": counts["ALREADY_REALIZED_AS_TWO_CARDS"] == 4,
        "five_new_members": counts["KEEP_AS_NEW_COMPOUND"] + counts["KEEP_AS_NEW_GRADE_MEMBER"] == 5,
        "three_rewritten_split": counts["REWRITE_AS_TWO_CARD_WORKSTEP"] == 3,
        "all_have_anchors": all(row["anchor_events"] and row["anchor_surfaces"] for row in audit),
        "all_have_concrete_output": all(row["revised_writer_output"] not in {"", "NONE", "UNKNOWN"} for row in audit),
        "near_matches_cover_all": {row["forecast"] for row in near} == {str(i) for i in range(1, 13)},
        "ledger_776_checked": json.loads((HERE / "BUILD_SUMMARY.json").read_text())["ledger_rows_checked"] == 776,
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "TWO_HUNDRED_NINETY_FIRST_12_FORECAST_AUDIT.tsv", HERE / "TWO_HUNDRED_NINETY_FIRST_OBSERVED_NEAR_MATCHES.tsv", HERE / "TWO_HUNDRED_NINETY_FIRST_WORKSHOP_FORECAST_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
