#!/usr/bin/env python3
"""Validate the OK/CHD two-verb cycle."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    statements = rows("SIX_HUNDRED_FIFTY_NINTH_18_JOINT_STATEMENT_TRACES.tsv")
    transitions = rows("SIX_HUNDRED_FIFTY_NINTH_11_IMMEDIATE_TRANSITIONS.tsv")
    fused = rows("SIX_HUNDRED_FIFTY_NINTH_5_FUSED_SHORTCUTS.tsv")
    patterns = rows("SIX_HUNDRED_FIFTY_NINTH_10_VERB_SKELETONS.tsv")
    rules = rows("SIX_HUNDRED_FIFTY_NINTH_6_CYCLE_RULES.tsv")
    checks = {
        "eighteen_statements": len(statements) == 18,
        "ninety_four_statement_events": sum(int(row["statement_events"]) for row in statements) == 94,
        "forty_two_root_events": sum(int(row["root_events"]) for row in statements) == 42,
        "ten_patterns": len(patterns) == 10,
        "eleven_transitions": len(transitions) == 11,
        "five_set_to_transfer": sum(row["transition"] == "SET_TO_TRANSFER" for row in transitions) == 5,
        "six_transfer_to_set": sum(row["transition"] == "TRANSFER_TO_SET" for row in transitions) == 6,
        "five_fused": len(fused) == 5,
        "all_fused_final": all(row["statement_final"] == "YES" for row in fused),
        "six_rules": len(rules) == 6,
        "five_fused_pattern_statements": sum(row["verb_skeleton"] == "FUSED_SET_TRANSFER_CLOSE" for row in statements) == 5,
        "four_alternating_triples": sum(row["cycle_class"] == "ALTERNATING_CYCLE" for row in statements) == 4,
        "four_single_handoffs": sum(row["cycle_class"] == "SINGLE_HANDOFF" for row in statements) == 4,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
