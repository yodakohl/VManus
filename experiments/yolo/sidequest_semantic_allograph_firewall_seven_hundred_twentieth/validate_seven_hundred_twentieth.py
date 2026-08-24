#!/usr/bin/env python3
"""Validate Pass 720 allograph/card firewall."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cases = read("SEVEN_HUNDRED_TWENTIETH_4_FIREWALL_CASES.tsv")
    trace = read("SEVEN_HUNDRED_TWENTIETH_27_CORRECTOR_TRACE.tsv")
    lines = read("SEVEN_HUNDRED_TWENTIETH_5_SUPPLIED_AND_CORRECTED_LINES.tsv")
    harmless = [row for row in cases if row["case_kind"] == "HARMLESS_ALLOGRAPH"]
    dangerous = [row for row in cases if row["case_kind"] == "DANGEROUS_OTHER_CARD"]
    checks = {
        "cases_2_plus_2": len(cases) == 4 and len(harmless) == 2 and len(dangerous) == 2,
        "trace_27": len(trace) == 27 and len({row["master_event_id"] for row in trace}) == 27,
        "lines_5": len(lines) == 5 and sum(int(row["events"]) for row in lines) == 27,
        "harmless_same_card": all(row["expected_card"] == row["decoded_card"] and row["corrector_verdict"] == "KEEP_AS_LICENSED_ALLOGRAPH" for row in harmless),
        "dangerous_other_recipe": all(row["expected_card"] != row["decoded_card"] and row["expected_recipe"] != row["decoded_recipe"] for row in dangerous),
        "dangerous_rejected": all(row["corrector_verdict"] == "REJECT_AND_RESTORE_EXPECTED_CARD" for row in dangerous),
        "all_final_cards_correct": all(row["corrected_exact_match"] == "YES" for row in trace),
        "target_source_case": any(row["expected_recipe"] == "OK+AL" and row["decoded_recipe"] == "OK+AR" for row in dangerous),
        "open_close_case": any(row["expected_recipe"] == "CHD+Y" and row["decoded_recipe"] == "SHED+DY" for row in dangerous),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTIETH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
