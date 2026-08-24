#!/usr/bin/env python3
"""Validate the twelve concealed-card drills."""

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
    drills = read_tsv("THREE_HUNDRED_FIFTY_SECOND_TWELVE_HIDDEN_CARD_DRILLS.tsv")
    ladder = read_tsv("THREE_HUNDRED_FIFTY_SECOND_CUE_LADDER.tsv")
    counts = Counter(row["decisive_cue"] for row in drills)
    checks = {
        "twelve_drills": len(drills) == 12,
        "twelve_tablet_ids": {row["tablet_no"] for row in drills} == {f"T{i:02d}" for i in range(1, 13)},
        "all_guesses_wrong": all(row["hidden_target_surface"] != row["apprentice_first_guess_surface"] and row["hidden_target_value_de"] != row["apprentice_first_guess_value_de"] for row in drills),
        "no_false_allographs": all(row["guess_is_useful_allograph"] == "NO" for row in drills),
        "all_exactly_recovered": all(row["exact_recovery"] == "YES" and row["apprentice_final_surface"] == row["hidden_target_surface"] for row in drills),
        "cue_counts_8_1_3_0": counts == {"CUE1_VISIBLE_OWNER": 8, "CUE2_SLOT": 1, "CUE3_RIGHT_NEIGHBOR": 3},
        "four_ladder_rows": len(ladder) == 4,
        "ladder_matches": {row["decisive_cue"]: int(row["cards_repaired"]) for row in ladder} == {"CUE1_VISIBLE_OWNER": 8, "CUE2_SLOT": 1, "CUE3_RIGHT_NEIGHBOR": 3, "CUE4_MASTER_TABLET": 0},
        "all_cues_present": all(row["visible_owner"] and row["slot_cue"] and row["left_value_cue"] and row["right_value_cue"] for row in drills),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
