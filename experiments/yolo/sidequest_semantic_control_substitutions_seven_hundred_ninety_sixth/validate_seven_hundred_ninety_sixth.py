#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    substitutions = read("SEVEN_HUNDRED_NINETY_SIXTH_8_CONTROL_SUBSTITUTIONS.tsv")
    traces = read("SEVEN_HUNDRED_NINETY_SIXTH_16_BEFORE_AFTER_TRACES.tsv")
    invariants = read("SEVEN_HUNDRED_NINETY_SIXTH_8_TAIL_INVARIANTS.tsv")
    rules = read("SEVEN_HUNDRED_NINETY_SIXTH_5_CONTROL_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETY_SIXTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_8_16_8_5": (len(substitutions), len(traces), len(invariants), len(rules)) == (8, 16, 8, 5),
        "two_traces_each": all(sum(row["exercise"] == item["exercise"] for row in traces) == 2 for item in substitutions),
        "before_after_each": all({row["phase"] for row in traces if row["exercise"] == item["exercise"]} == {"BEFORE", "AFTER"} for item in substitutions),
        "six_continue_two_next": sum(row["control_change"] == "OK→OL" for row in substitutions) == 6 and sum(row["control_change"] == "OK→OT" for row in substitutions) == 2,
        "tails_match8": all(row["tail_invariant"] == "YES" and row["source_tail"] == row["target_tail"] for row in invariants),
        "other_events_kept": all(row["other_events_unchanged"] == "YES" for row in substitutions),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (substitutions, traces, invariants, rules) for row in rows),
        "summary_pass": summary == {
            "status": "PASS",
            "substitutions": 8,
            "before_after_traces": 16,
            "tail_invariants": 8,
            "tail_matches": 8,
            "ok_to_ol": 6,
            "ok_to_ot": 2,
            "decision": "CONTROL_SWAP_CHANGES_FLOW_MODE_AND_PRESERVES_TAIL",
        },
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETY_SIXTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
