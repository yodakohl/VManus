#!/usr/bin/env python3
"""Validate residual line layouts and read-once copies."""

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
    lines = read_tsv("THREE_HUNDRED_FIFTY_SIXTH_SEVENTEEN_PHYSICAL_LINES.tsv")
    breaks = read_tsv("THREE_HUNDRED_FIFTY_SIXTH_THIRTEEN_LINE_BREAKS.tsv")
    copies = read_tsv("THREE_HUNDRED_FIFTY_SIXTH_FOUR_READ_ONCE_COPIES.tsv")
    break_counts = Counter(row["break_type"] for row in breaks)
    hands = {row["hand"] for row in lines}
    checks = {
        "four_hands": len(hands) == 4,
        "seventeen_lines": len(lines) == 17,
        "thirteen_breaks": len(breaks) == 13,
        "break_types_4_5_4": break_counts == {"INTRA_MICROCYCLE_LINE_BREAK": 4, "MICROCYCLE_BOUNDARY": 5, "OWNER_HANDOFF": 4},
        "four_read_once_copies": len(copies) == 4,
        "copies_only_intra_cycle": all(row["carry_status"] == ("ANTICIPATION_COPY_USED" if row["break_type"] == "INTRA_MICROCYCLE_LINE_BREAK" else "COPY_FORBIDDEN") for row in breaks),
        "all_lines_fit": all(int(row["ink_units"]) <= int(row["residual_width"]) for row in lines),
        "source_positions_once_per_hand": all(sorted(int(position) for row in lines if row["hand"] == hand for position in row["source_positions"].split("|")) == list(range(1, 12)) for hand in hands),
        "copies_read_once": all(row["source_card_count"] == "1" and row["visible_surface_count"] == "2" and row["read_once_rule"] == "READ_MARGIN_ANTICIPATION_AND_LINE_START_AS_ONE_CARD" for row in copies),
        "visible_instances_48": sum(len(row["source_positions"].split("|")) for row in lines) + len(copies) == 48,
        "owner_handoffs_never_copied": all(row["carry_status"] == "COPY_FORBIDDEN" for row in breaks if row["break_type"] == "OWNER_HANDOFF"),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
