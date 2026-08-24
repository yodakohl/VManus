#!/usr/bin/env python3
"""Validate the consolidated five-root dictionary."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = rows("SIX_HUNDRED_SIXTY_THIRD_57_FIVE_ROOT_CARDS.tsv")
    events = rows("SIX_HUNDRED_SIXTY_THIRD_158_FIVE_ROOT_EVENTS.tsv")
    roots = rows("SIX_HUNDRED_SIXTY_THIRD_5_ROOT_ENTRIES.tsv")
    recipes = rows("SIX_HUNDRED_SIXTY_THIRD_50_COMPONENT_RECIPES.tsv")
    remainder = rows("SIX_HUNDRED_SIXTY_THIRD_116_REMAINING_CARDS.tsv")
    candidates = rows("SIX_HUNDRED_SIXTY_THIRD_5_NEXT_CONTENT_ROOTS.tsv")
    checks = {
        "five_roots": len(roots) == 5,
        "fifty_seven_cards": len(cards) == 57,
        "one_hundred_fifty_eight_events": len(events) == 158,
        "fifty_recipes": len(recipes) == 50,
        "card_partition_173": len(cards) + len(remainder) == 173,
        "event_partition_381": len(events) + sum(int(row["events"]) for row in remainder) == 381,
        "one_hundred_sixteen_remainder_cards": len(remainder) == 116,
        "two_hundred_twenty_three_remainder_events": sum(int(row["events"]) for row in remainder) == 223,
        "ninety_four_statements": len({row["statement_id"] for row in events}) == 94,
        "ten_records": len({row["record"] for row in events}) == 10,
        "seven_pages": len({row["page"] for row in events}) == 7,
        "sixty_three_closed": sum(row["contains_close"] == "YES" for row in events) == 63,
        "all_closed_final": all(row["statement_final"] == "YES" for row in events if row["contains_close"] == "YES"),
        "five_next_candidates": len(candidates) == 5,
        "or_is_next": min(candidates, key=lambda row: int(row["next_priority"]))["candidate_root"] == "OR",
        "event_ids_unique": len({row["event_id"] for row in events}) == 158,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
