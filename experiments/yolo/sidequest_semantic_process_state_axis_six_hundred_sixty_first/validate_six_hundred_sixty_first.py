#!/usr/bin/env python3
"""Validate the process/state axis."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    inventory = rows("SIX_HUNDRED_SIXTY_FIRST_15_STATE_CARD_INVENTORY.tsv")
    roots = rows("SIX_HUNDRED_SIXTY_FIRST_3_STATE_ROOTS.tsv")
    traces = rows("SIX_HUNDRED_SIXTY_FIRST_17_PROCESS_STATE_TRACES.tsv")
    transitions = rows("SIX_HUNDRED_SIXTY_FIRST_11_IMMEDIATE_TRANSITIONS.tsv")
    rules = rows("SIX_HUNDRED_SIXTY_FIRST_6_STATE_RULES.tsv")
    checks = {
        "fifteen_state_cards": len(inventory) == 15,
        "thirty_seven_state_events": sum(int(row["events"]) for row in inventory) == 37,
        "fourteen_recipes": len({row["component_recipe"] for row in inventory}) == 14,
        "three_roots": len(roots) == 3,
        "root_event_counts": {row["state_root"]: int(row["events"]) for row in roots} == {"SHED": 15, "CHK": 7, "CTH": 15},
        "fourteen_closed_state_events": sum(int(row["events"]) for row in inventory if row["contains_close"] == "YES") == 14,
        "all_closed_state_final": sum(int(row["statement_final_events"]) for row in inventory if row["contains_close"] == "YES") == 14,
        "seventeen_joint_statements": len(traces) == 17,
        "ninety_nine_joint_events": sum(int(row["statement_events"]) for row in traces) == 99,
        "thirty_one_process_events": sum(int(row["process_events"]) for row in traces) == 31,
        "twenty_one_state_events": sum(int(row["state_events"]) for row in traces) == 21,
        "eleven_transitions": len(transitions) == 11,
        "six_process_to_state": sum(row["direction"] == "PROCESS_TO_STATE" for row in transitions) == 6,
        "five_state_to_process": sum(row["direction"] == "STATE_TO_PROCESS" for row in transitions) == 5,
        "six_rules": len(rules) == 6,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
