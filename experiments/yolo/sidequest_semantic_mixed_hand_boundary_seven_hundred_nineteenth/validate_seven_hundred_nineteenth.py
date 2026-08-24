#!/usr/bin/env python3
"""Validate Pass 719 mixed-hand boundary."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    trace = read("SEVEN_HUNDRED_NINETEENTH_27_MIXED_HAND_TRACE.tsv")
    candidates = read("SEVEN_HUNDRED_NINETEENTH_28_BOUNDARY_CANDIDATES.tsv")
    lines = read("SEVEN_HUNDRED_NINETEENTH_5_MIXED_LINES.tsv")
    anchors = read("SEVEN_HUNDRED_NINETEENTH_27_ANCHOR_ROLES.tsv")
    perfect = [row for row in candidates if row["perfect_profile_fit"] == "YES"]
    checks = {
        "events_27": len(trace) == 27 and [int(row["position"]) for row in trace] == list(range(1, 28)),
        "candidates_28": len(candidates) == 28 and [int(row["split_after_position"]) for row in candidates] == list(range(28)),
        "unique_boundary_after_13": len(perfect) == 1 and perfect[0]["split_after_position"] == "13",
        "boundary_mid_line3": next(row for row in lines if row["line_no"] == "3")["contains_hand_boundary"] == "YES",
        "only_one_mixed_line": sum(row["contains_hand_boundary"] == "YES" for row in lines) == 1,
        "markers_14_anchors_13": sum(row["anchor_kind"] == "VARIABLE_HAND_MARKER" for row in anchors) == 14 and sum(row["anchor_kind"] == "INVARIANT_CARD_ANCHOR" for row in anchors) == 13,
        "content_invariant": all(row["card_backread_unchanged"] == "YES" and row["owner_unchanged"] == "YES" and row["statement_unchanged"] == "YES" for row in trace),
        "boundary_inside_fd03_basin": trace[12]["docket_id"] == "FD03" and trace[13]["docket_id"] == "FD03" and trace[12]["owner"] == trace[13]["owner"] == "BASIN",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETEENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
