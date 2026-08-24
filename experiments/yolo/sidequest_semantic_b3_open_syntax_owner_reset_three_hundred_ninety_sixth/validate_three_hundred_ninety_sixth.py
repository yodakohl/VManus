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
    layout = read("THREE_HUNDRED_NINETY_SIXTH_TWO_REGION_LAYOUT.tsv")
    steps = read("THREE_HUNDRED_NINETY_SIXTH_EIGHT_READER_STEPS.tsv")
    registers = read("THREE_HUNDRED_NINETY_SIXTH_FOUR_REGISTER_RULES.tsv")
    checks = {
        "two_regions": len(layout) == 2,
        "seven_cards": Counter(row["item_type"] for row in steps)["CARD"] == 7,
        "one_gap": Counter(row["item_type"] for row in steps)["VISUAL_GAP"] == 1,
        "eight_steps": len(steps) == 8,
        "four_registers": len(registers) == 4,
        "syntax_open_at_gap": next(row for row in steps if row["item_type"] == "VISUAL_GAP")["syntax_before"] == next(row for row in steps if row["item_type"] == "VISUAL_GAP")["syntax_after"] == "OPEN",
        "owner_resets_at_gap": next(row for row in steps if row["item_type"] == "VISUAL_GAP")["owner_after"] == "RESET_TO_STATION_B",
        "only_last_closes": [row["event_id"] for row in steps if row["syntax_after"] == "CLOSED"] == ["E291"],
        "no_arrows": all(row["connection_arrow"] == "NONE" for row in layout),
        "event_order": [row["event_id"] for row in steps if row["item_type"] == "CARD"] == [f"E{number:03d}" for number in range(285, 292)],
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_NINETY_SIXTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
