#!/usr/bin/env python3
"""Validate the continuous seven-page workshop reading."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    transitions = read_tsv("THREE_HUNDRED_FIFTY_EIGHTH_FORTY_SIX_LINE_TRANSITIONS.tsv")
    events = read_tsv("THREE_HUNDRED_FIFTY_EIGHTH_381_VISIBLE_380_SOURCE_EDITION.tsv")
    lines = read_tsv("THREE_HUNDRED_FIFTY_EIGHTH_FIFTY_SEVEN_PHYSICAL_LINES.tsv")
    counts = Counter(row["decision"] for row in transitions)
    carry = [row for row in transitions if row["decision"] == "READ_ONCE_CARRY"]
    checks = {
        "381_visible_events": len(events) == 381,
        "event_ids_exact": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "380_source_positions": sum(int(row["source_position_contribution"]) for row in events) == 380 and len({row["source_position_id"] for row in events}) == 380,
        "57_lines": len(lines) == 57 and len({(row["record_unit_id"], row["locus"]) for row in lines}) == 57,
        "46_transitions": len(transitions) == 46,
        "decision_counts_6_1_39": counts == {"CONTINUE_ACROSS_LINE": 6, "READ_ONCE_CARRY": 1, "REAL_CYCLE_OR_OWNER_RESET": 39},
        "sole_carry_E180_E181": len(carry) == 1 and carry[0]["left_event_id"] == "E180" and carry[0]["right_event_id"] == "E181",
        "carry_same_exact_owner_cycle": all(row["same_exact_card"] == "YES" and row["same_owner"] == "YES" and row["same_microcycle"] == "YES" for row in carry),
        "visible_roles_exact": next(row for row in events if row["event_id"] == "E180")["visible_role"] == "RIGHT_MARGIN_ANTICIPATION_COPY" and next(row for row in events if row["event_id"] == "E181")["visible_role"] == "LINE_START_EXECUTION_OF_READ_ONCE_CARD",
        "E180_E181_same_source": next(row for row in events if row["event_id"] == "E180")["source_position_id"] == next(row for row in events if row["event_id"] == "E181")["source_position_id"],
        "eleven_records": len({row["record_unit_id"] for row in events}) == 11,
        "seven_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "line_contribution_sum": sum(int(row["source_positions_contributed"]) for row in lines) == 380,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
