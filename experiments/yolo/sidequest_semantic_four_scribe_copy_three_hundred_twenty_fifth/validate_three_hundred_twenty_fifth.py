#!/usr/bin/env python3
"""Validate all four scribe renderings."""

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
    rendered = read("THREE_HUNDRED_TWENTY_FIFTH_56_RENDERED_EVENTS.tsv")
    editions = read("THREE_HUNDRED_TWENTY_FIFTH_EIGHT_SCRIBE_PASSAGES.tsv")
    rules = read("THREE_HUNDRED_TWENTY_FIFTH_FOUR_HAND_RULES.tsv")
    hand_counts = Counter(x["hand_id"] for x in rendered)
    checks = {
        "four_hands": len(rules) == 4 and len(hand_counts) == 4,
        "fourteen_each": set(hand_counts.values()) == {14},
        "fifty_six_events": len(rendered) == 56,
        "all_identity_matches": all(x["identity_match"] == "YES" for x in rendered),
        "eight_passages": len(editions) == 8,
        "eight_distinct_surface_copies": len({(x["line_1"], x["line_2"]) for x in editions}) == 8,
        "all_cross_line": all(x["logical_statement_crosses_line"] == "YES" for x in editions),
        "all_meanings_preserved": all(x["meaning_sequence_preserved"] == "YES" for x in editions),
        "no_sealed_page": all("f84" not in "\t".join(x.values()).lower() for rows in [rendered, editions, rules] for x in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTY_FIFTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
