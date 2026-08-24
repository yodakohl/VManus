#!/usr/bin/env python3
"""Validate the complete workshop board."""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    board = read_tsv("THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv")
    cells = read_tsv("THREE_HUNDRED_FIFTY_THIRD_THIRTY_BOARD_CELLS.tsv")
    pairs = read_tsv("THREE_HUNDRED_FIFTY_THIRD_FOURTEEN_PAIR_PLACARDS.tsv")
    pins = read_tsv("THREE_HUNDRED_FIFTY_THIRD_TWELVE_PINNED_MASTER_CARDS.tsv")
    checks = {
        "173_unique_cards": len(board) == 173 and len({row["joint_tuple_id"] for row in board}) == 173,
        "381_events": sum(int(row["events"]) for row in board) == 381,
        "thirty_cells": len(cells) == 30 and len({row["board_address"] for row in cells}) == 30,
        "cell_card_sum": sum(int(row["card_types"]) for row in cells) == 173,
        "cell_event_sum": sum(int(row["events"]) for row in cells) == 381,
        "every_card_has_board_address": all(row["board_address"] and row["primary_slot"] and row["primary_working_state"] for row in board),
        "five_states": len({row["primary_working_state"] for row in board}) == 5,
        "six_slots": len({row["primary_slot"] for row in board}) == 6,
        "fourteen_pairs": len(pairs) == 14 and len({row["pair_id"] for row in pairs}) == 14,
        "twenty_eight_pair_cards": sum(row["ambiguous_pair_id"] != "NONE" for row in board) == 28,
        "twelve_pins": len(pins) == 12 and len({row["joint_tuple_id"] for row in pins}) == 12,
        "pins_match_board": all(any(card["joint_tuple_id"] == pin["joint_tuple_id"] and card["board_address"] == pin["board_address"] for card in board) for pin in pins),
        "all_values_concrete": all(row["atomic_value_de"] and row["atomic_value_de"] not in {"UNKNOWN", "FORMAL"} for row in board),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
