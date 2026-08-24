#!/usr/bin/env python3
"""Validate the bounded junction-card tray."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninety_fourth.py")], check=True)
    occurrences = read("SIX_HUNDRED_NINETY_FOURTH_22_JUNCTION_OCCURRENCES.tsv")
    cards = read("SIX_HUNDRED_NINETY_FOURTH_20_JUNCTION_CARD_TRAY.tsv")
    pairs = read("SIX_HUNDRED_NINETY_FOURTH_4_DESK_PAIR_RULES.tsv")
    records = read("SIX_HUNDRED_NINETY_FOURTH_11_RECORD_JUNCTION_BURDEN.tsv")
    burden = read("SIX_HUNDRED_NINETY_FOURTH_4_ROLE_REFERENCE_BURDEN.tsv")
    checks = {
        "twenty_two_occurrences": len(occurrences) == 22,
        "twenty_exact_cards": len(cards) == 20 and len({row["card_no"] for row in cards}) == 20,
        "four_pair_rules": len(pairs) == 4,
        "pair_event_counts": Counter(row["desk_pair"] for row in occurrences) == Counter({"S02_PREPARATION_WET>S03_TRANSFER": 11, "S02_PREPARATION_WET>S04_STATE_CONTROL": 5, "S03_TRANSFER>S04_STATE_CONTROL": 5, "S01_MASTER_CORRECTOR>S04_STATE_CONTROL": 1}),
        "downstream_event_storage": Counter(row["downstream_storage_desk"] for row in occurrences) == Counter({"S03_TRANSFER": 11, "S04_STATE_CONTROL": 11}),
        "downstream_card_storage": Counter(row["stored_at_desk"] for row in cards) == Counter({"S03_TRANSFER": 11, "S04_STATE_CONTROL": 9}),
        "eight_records_with_junctions": sum(int(row["junction_events"]) > 0 for row in records) == 8,
        "eleven_record_rows": len(records) == 11 and sum(int(row["junction_events"]) for row in records) == 22,
        "b3_five_preserved": next(int(row["junction_events"]) for row in records if row["record"] == "B3") == 5,
        "role_burdens": {row["scribe_role"]: int(row["total_reference_cards"]) for row in burden} == {"S01_MASTER_CORRECTOR": 18, "S02_PREPARATION_WET": 23, "S03_TRANSFER": 28, "S04_STATE_CONTROL": 29},
        "all_whole_card_rules": all("ganze" in row["copy_rule_de"] for row in occurrences),
        "largest_deck_below_thirty": max(int(row["total_reference_cards"]) for row in burden) == 29,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_NINETY_FOURTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
