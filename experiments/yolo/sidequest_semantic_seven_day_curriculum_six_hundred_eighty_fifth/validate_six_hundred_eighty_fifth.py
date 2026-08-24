#!/usr/bin/env python3
"""Validate the seven-day curriculum inventory."""

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
    subprocess.run(["python3", str(HERE / "build_six_hundred_eighty_fifth.py")], check=True)
    days = read("SIX_HUNDRED_EIGHTY_FIFTH_7_DAY_CURRICULUM.tsv")
    sessions = read("SIX_HUNDRED_EIGHTY_FIFTH_21_TWO_HOUR_SESSIONS.tsv")
    trials = read("SIX_HUNDRED_EIGHTY_FIFTH_3_FINAL_RECORD_TRIALS.tsv")
    errors = read("SIX_HUNDRED_EIGHTY_FIFTH_10_ERROR_RUBRIC.tsv")
    introduced = [component for row in days for component in row["new_components"].split() if component != "NONE_NEW"]
    checks = {
        "seven_days": len(days) == 7 and [int(row["day"]) for row in days] == list(range(1, 8)),
        "thirty_nine_roots_once": len(introduced) == 39 and len(set(introduced)) == 39,
        "twenty_one_sessions": len(sessions) == 21 and sum(int(row["duration_hours"]) for row in sessions) == 42,
        "three_sessions_per_day": all(sum(row["day"] == str(day) for row in sessions) == 3 for day in range(1, 8)),
        "copybook_always_open": all(row["copybook_open"] == "YES" for row in sessions),
        "three_trials": len(trials) == 3 and {row["record"] for row in trials} == {"H3", "B1", "B6"},
        "ninety_two_trial_events": sum(int(row["events"]) for row in trials) == 92,
        "ten_error_classes": len(errors) == 10,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
