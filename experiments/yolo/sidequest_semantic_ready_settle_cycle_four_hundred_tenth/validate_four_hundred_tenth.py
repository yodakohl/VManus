#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("FOUR_HUNDRED_TENTH_READY_SETTLE_OCCURRENCES.tsv")
    progressions = read("FOUR_HUNDRED_TENTH_FIVE_STATE_PROGRESSIONS.tsv")
    machine = read("FOUR_HUNDRED_TENTH_FIVE_STATE_MACHINE.tsv")
    counts = Counter(row["family"] for row in events)
    checks = {
        "family_counts": counts == {"SHED_SETTLE": 17, "CTH_READY": 9},
        "twenty_six_events": len(events) == 26,
        "ready_never_terminal": all(row["terminal"] == "NO" for row in events if row["family"] == "CTH_READY"),
        "settle_has_terminal_majority": sum(row["family"] == "SHED_SETTLE" and row["terminal"] == "YES" for row in events) == 15,
        "shedal_two_nonterminal": sum(row["surface"] == "shedal" and row["terminal"] == "NO" for row in events) == 2,
        "five_progressions": len(progressions) == 5,
        "b3_s034_has_both": next(row for row in progressions if row["progression"] == "B3-S034")["settle_position"] == "TERMINAL_AFTER_OPERATION",
        "h2_ready_precedes_work": next(row for row in progressions if row["progression"] == "H2-S001")["ready_position"] == "MATERIAL_RELEASE_BEFORE_WORK",
        "five_machine_states": len(machine) == 5,
        "ready_and_settling_distinct": {row["state"] for row in machine} >= {"READY", "SETTLING"},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_TENTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
