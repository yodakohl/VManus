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
    rules = read("THREE_HUNDRED_NINETY_EIGHTH_THREE_BOUNDARY_RULES.tsv")
    lines = read("THREE_HUNDRED_NINETY_EIGHTH_FIVE_COPY_LINES.tsv")
    cards = read("THREE_HUNDRED_NINETY_EIGHTH_14_CARD_RECONSTRUCTION.tsv")
    boundaries = read("THREE_HUNDRED_NINETY_EIGHTH_FIVE_BOUNDARY_DECISIONS.tsv")
    sequences = {
        copy: [(row["reconstructed_event_id"], row["reconstructed_joint_tuple_id"]) for row in cards if row["copy"] == copy]
        for copy in {row["copy"] for row in cards}
    }
    checks = {
        "three_rules": len(rules) == 3,
        "rule_types": {row["boundary_type"] for row in rules} == {"ORDINARY_REFLOW", "OWNER_RESET_GAP", "TERMINAL_CLOSE"},
        "five_lines": len(lines) == 5,
        "line_split": Counter(row["copy"] for row in lines) == {"COPY_A": 2, "COPY_B": 3},
        "fourteen_reconstructions": len(cards) == 14,
        "seven_each": Counter(row["copy"] for row in cards) == {"COPY_A": 7, "COPY_B": 7},
        "same_sequences": sequences["COPY_A"] == sequences["COPY_B"],
        "all_identity_matches": all(row["identity_match_to_other_copy"] == "YES" for row in cards),
        "five_boundaries": len(boundaries) == 5,
        "boundary_profile": Counter(row["boundary_type"] for row in boundaries) == {"OWNER_RESET_GAP": 2, "TERMINAL_CLOSE": 2, "ORDINARY_REFLOW": 1},
        "only_reset_changes_owner": all((row["owner_action"] == "RESET") == (row["boundary_type"] == "OWNER_RESET_GAP") for row in boundaries),
        "only_terminal_closes": all((row["syntax_action"] == "CLOSE") == (row["boundary_type"] == "TERMINAL_CLOSE") for row in boundaries),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_NINETY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
