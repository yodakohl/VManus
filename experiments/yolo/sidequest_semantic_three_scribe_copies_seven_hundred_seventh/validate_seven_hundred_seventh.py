#!/usr/bin/env python3
"""Validate Pass 707 three-scribe copies."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    copies = read("SEVEN_HUNDRED_SEVENTH_3_HAND_COPIES.tsv")
    trace = read("SEVEN_HUNDRED_SEVENTH_42_SURFACE_BACKREAD_TRACE.tsv")
    differences = read("SEVEN_HUNDRED_SEVENTH_3_HAND_DIFFERENCES.tsv")
    components = {row["semantic_component_sequence"] for row in copies}
    checks = {
        "hands_3": len(copies) == 3,
        "trace_42": len(trace) == 42,
        "fourteen_per_hand": all(sum(row["hand_id"] == hand["hand_id"] for row in trace) == 14 for hand in copies),
        "three_lines_each": all(len(row["line_1"].split()) == 5 and len(row["line_2"].split()) == 6 and len(row["line_3"].split()) == 3 for row in copies),
        "one_component_sequence": len(components) == 1,
        "exact_card_recovery_42": all(row["exact_card_recovery"] == "YES" for row in trace),
        "exact_component_recovery_42": all(row["exact_component_recovery"] == "YES" for row in trace),
        "surface_unambiguous_42": all(row["surface_card_ambiguity"] == "1" for row in trace),
        "pairwise_comparisons_3": len(differences) == 3,
        "visible_differences_exist": all(int(row["different_card_positions"]) >= 1 for row in differences),
        "no_identity_changes": all(row["card_identity_changes"] == "0" and row["component_changes"] == "0" and row["owner_changes"] == "0" for row in differences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
