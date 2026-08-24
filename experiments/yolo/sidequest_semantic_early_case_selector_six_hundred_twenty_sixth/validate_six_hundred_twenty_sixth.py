#!/usr/bin/env python3
"""Validate the five-event case selector and full branch trace."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    selectors = read("SIX_HUNDRED_TWENTY_SIXTH_5_FIRST_FIVE_SELECTORS.tsv")
    trace = read("SIX_HUNDRED_TWENTY_SIXTH_372_EVENT_BRANCH_TRACE.tsv")
    audit = read("SIX_HUNDRED_TWENTY_SIXTH_5_BRANCH_CONFIRMATION_AUDIT.tsv")
    by_case = {row["actual_case_id"]: row for row in selectors}
    trace_ids = [row["event_id"] for row in trace]
    checks = {
        "five_selectors": len(selectors) == 5 and {row["actual_case_id"] for row in selectors} == {f"C{i}" for i in range(1, 6)},
        "all_correct": all(row["actual_case_id"] == row["selected_case_id"] and row["selector_result"] == "CORRECT" for row in selectors),
        "all_by_event_five": all(int(row["decision_event_index"]) <= 5 for row in selectors),
        "decision_indices": {case: int(row["decision_event_index"]) for case, row in by_case.items()} == {"C1": 5, "C2": 5, "C3": 3, "C4": 4, "C5": 1},
        "c2_positive_cth_rule": by_case["C2"]["cth_count_first_five"] == "3" and by_case["C2"]["selector_signal"].startswith("CTH=BEREIT x3"),
        "trace372": len(trace) == 372 and len(trace_ids) == len(set(trace_ids)),
        "five_audits": len(audit) == 5,
        "no_foreign_markers": all(row["foreign_branch_marker_hits"] == "NONE" for row in trace),
        "no_branch_switch": all(row["branch_switch"] == "NO" for row in trace) and all(row["branch_switches"] == "0" for row in audit),
        "all_final_states_correct": all(row["selector_state_after"] == row["case_id"] for row in trace if int(row["case_event_index"]) >= int(by_case[row["case_id"]]["decision_event_index"])),
        "c2_unique_marker_at74": next(row for row in audit if row["case_id"] == "C2")["first_exclusive_marker"].startswith("74|E216|"),
        "no_sealed_pages": not any(row["page"].startswith("f84") for row in trace),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
