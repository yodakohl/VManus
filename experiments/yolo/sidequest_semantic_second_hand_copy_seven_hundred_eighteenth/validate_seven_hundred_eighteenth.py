#!/usr/bin/env python3
"""Validate Pass 718 second-hand copy."""

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
    trace = read("SEVEN_HUNDRED_EIGHTEENTH_27_PARALLEL_HAND_TRACE.tsv")
    lines = read("SEVEN_HUNDRED_EIGHTEENTH_5_PARALLEL_LINES.tsv")
    rules = read("SEVEN_HUNDRED_EIGHTEENTH_4_SECOND_HAND_RULES.tsv")
    changes = Counter(row["second_hand_rule"] for row in trace)
    checks = {
        "events_27": len(trace) == 27 and len({row["master_event_id"] for row in trace}) == 27,
        "lines_5": len(lines) == 5 and sum(int(row["events"]) for row in lines) == 27,
        "changed_14_unchanged_13": sum(row["surface_changed"] == "YES" for row in trace) == 14 and sum(row["surface_changed"] == "NO" for row in trace) == 13,
        "change_profile_10_2_2": changes["H2_CH_ENTRY_FRAME"] == 10 and changes["H1_EXTENDED_E_JOINT"] == 2 and changes["H3_Q_ENTRY_FRAME"] == 2,
        "all_second_surfaces_unique": all(row["second_surface_unique_to_card"] == "YES" for row in trace),
        "all_cards_same": all(row["same_exact_card"] == "YES" for row in trace),
        "all_owners_same": all(row["same_owner"] == "YES" for row in trace),
        "all_boundaries_same": all(row["same_statement_boundary"] == "YES" and row["same_line_boundary"] == "YES" for row in trace),
        "four_rule_rows": len(rules) == 4 and sum(int(row["events"]) for row in rules) == 27,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTEENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
