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
    substitutions = read("SEVEN_HUNDRED_NINETY_EIGHTH_6_OPERATION_SUBSTITUTIONS.tsv")
    substitution_traces = read("SEVEN_HUNDRED_NINETY_EIGHTH_12_SUBSTITUTION_TRACES.tsv")
    stacked = read("SEVEN_HUNDRED_NINETY_EIGHTH_14_STACKED_CARD_TRACES.tsv")
    transitions = read("SEVEN_HUNDRED_NINETY_EIGHTH_42_AUTOMATON_TRANSITIONS.tsv")
    states = read("SEVEN_HUNDRED_NINETY_EIGHTH_8_STATES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETY_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_6_12_14_42_8": (len(substitutions), len(substitution_traces), len(stacked), len(transitions), len(states)) == (6, 12, 14, 42, 8),
        "two_substitution_traces_each": all(sum(row["exercise"] == item["exercise"] for row in substitution_traces) == 2 for item in substitutions),
        "all_other_events_kept": all(row["other_events_unchanged"] == "YES" for row in substitutions),
        "stack_counts_1_12_1": Counter(row["operation_stack"] for row in stacked) == {"K+CHD": 1, "L+CHD": 12, "L+K": 1},
        "three_transitions_each": all(sum(row["event_id"] == item["event_id"] for row in transitions) == 3 for item in stacked),
        "operation_then_endpoint": all([row["transition_type"] for row in transitions if row["event_id"] == item["event_id"]] == ["OPERATION", "OPERATION", "ENDPOINT"] for item in stacked),
        "state_inventory": {row["state"] for row in states} == {"ACTIVE_ITEM", "MATERIAL_ADDED", "PATH_ENGAGED", "ITEM_TRANSFERRED", "STEP_CLOSED", "AT_OWNER_TARGET", "FROM_OWNER_SOURCE", "ACTIVE_ITEM_RETAINED"},
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (substitutions, substitution_traces, stacked, transitions, states) for row in rows),
        "summary_pass": summary == {
            "status": "PASS",
            "operation_substitutions": 6,
            "substitution_traces": 12,
            "stacked_card_traces": 14,
            "automaton_transitions": 42,
            "states": 8,
            "other_events_preserved": 6,
            "decision": "STACKED_K_L_CHD_CARDS_EXECUTE_OWNER_LOCAL_TRANSFER_AUTOMATON",
        },
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
