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
    cards = read("THREE_HUNDRED_NINETY_SEVENTH_SEVEN_SECOND_HAND_CARDS.tsv")
    lines = read("THREE_HUNDRED_NINETY_SEVENTH_THREE_REFLOWED_LINES.tsv")
    comparison = read("THREE_HUNDRED_NINETY_SEVENTH_SEVEN_COPY_COMPARISON.tsv")
    checks = {
        "seven_cards": len(cards) == 7,
        "four_surface_changes": sum(row["surface_changed"] == "YES" for row in cards) == 4,
        "all_registered": all(row["second_hand_surface"] in row["registered_palette"].split("|") for row in cards),
        "identities_preserved": all(row["identity_preserved"] == "YES" for row in cards),
        "three_lines": len(lines) == 3,
        "line_card_sum": sum(int(row["card_count"]) for row in lines) == 7,
        "first_two_open": [row["syntax_after_line"] for row in lines[:2]] == ["OPEN", "OPEN"],
        "last_closes": lines[-1]["syntax_after_line"] == "CLOSED",
        "same_owner_then_reset": [row["owner_after_line"] for row in lines] == ["CONTINUE_SAME_OWNER", "OWNER_RESET_AFTER_LARGE_GAP", "CLOSE"],
        "no_arrows": all(row["connection_arrow"] == "NONE" for row in lines),
        "comparison_exact": len(comparison) == 7 and all(row["same_joint_tuple_id"] == row["same_component_reading"] == row["same_visible_owner_zone"] == row["same_syntax_order"] == "YES" for row in comparison),
        "event_order": [row["event_id"] for row in cards] == [f"E{number:03d}" for number in range(285, 292)],
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_NINETY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
