#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("FOUR_HUNDRED_SIXTEENTH_TWO_OPENING_CARDS.tsv")
    image = read("FOUR_HUNDRED_SIXTEENTH_F10_IMAGE_ANCHORS.tsv")
    operations = read("FOUR_HUNDRED_SIXTEENTH_FIVE_PREPARATION_OPERATIONS.tsv")
    trace = read("FOUR_HUNDRED_SIXTEENTH_H1_FOURTEEN_CARD_READING.tsv")
    checks = {
        "two_opening_cards": len(cards) == 2,
        "opening_values": [row["selected_value_de"] for row in cards] == ["Knolle", "abschaben"],
        "distinct_exact_cards": len({row["joint_tuple_id"] for row in cards}) == 2,
        "five_visual_anchors": len(image) == 5,
        "red_swellings_visible": any(row["feature"] == "TWO_RED_TERMINAL_SWELLINGS" and row["visible"] == "YES" for row in image),
        "no_visible_tool_claim": any(row["feature"] == "SCRAPING_TOOL" and row["visible"] == "NO" for row in image),
        "five_operations": len(operations) == 5,
        "wash_distinct_from_scrape": len({row["small_value_de"] for row in operations[:3]}) == 3,
        "fourteen_h1_events": len(trace) == 14,
        "exact_h1_order": [row["event_id"] for row in trace] == [f"E{i:03d}" for i in range(1, 15)],
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (cards, image, operations, trace) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
