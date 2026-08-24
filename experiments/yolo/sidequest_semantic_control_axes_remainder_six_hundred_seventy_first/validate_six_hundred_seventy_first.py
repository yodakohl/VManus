#!/usr/bin/env python3
"""Validate the final control axes and three-command remainder."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("SIX_HUNDRED_SEVENTY_FIRST_67_CONTROL_CARDS.tsv")
    roots = read("SIX_HUNDRED_SEVENTY_FIRST_5_CONTROL_ROOTS.tsv")
    whole = read("SIX_HUNDRED_SEVENTY_FIRST_3_WHOLE_COMMANDS.tsv")
    dy = read("SIX_HUNDRED_SEVENTY_FIRST_89_DY_CLOSE_EVENTS.tsv")
    summary = json.loads((HERE / "SIX_HUNDRED_SEVENTY_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    expected = {"T": (9, 10), "CH": (15, 16), "O": (18, 19), "DY": (37, 89), "S": (1, 1)}
    checks = {
        "sixty_seven_control_cards": len(cards) == 67,
        "one_hundred_twenty_two_control_events": sum(int(row["events"]) for row in cards) == 122,
        "five_roots": len(roots) == 5 and {row["root"] for row in roots} == set(expected),
        "raw_root_counts": all((int(row["card_types"]), int(row["events"])) == expected[row["root"]] for row in roots),
        "three_whole_commands": len(whole) == 3,
        "four_whole_events": sum(int(row["events"]) for row in whole) == 4,
        "exact_whole_ids": {row["card_no"] for row in whole} == {"PROC005", "PROC034", "PROC043"},
        "eighty_nine_dy_events": len(dy) == 89,
        "all_dy_terminal": all(row["statement_position"] in {"FINAL", "WHOLE"} for row in dy),
        "s_only_in_ches": next(row for row in roots if row["root"] == "S")["card_types"] == "1",
        "zero_uncovered_events": summary["uncovered_events_after_controls_and_whole_commands"] == 0,
        "complete_deck_counts": summary["complete_dictionary_card_types"] == 173 and summary["complete_dictionary_events"] == 381,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
