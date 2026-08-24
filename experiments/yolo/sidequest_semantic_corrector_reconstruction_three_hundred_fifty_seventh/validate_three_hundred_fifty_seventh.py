#!/usr/bin/env python3
"""Validate corrector reconstruction of physical layouts."""

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
    cards = read_tsv("THREE_HUNDRED_FIFTY_SEVENTH_FORTY_FOUR_CORRECTED_SOURCE_CARDS.tsv")
    breaks = read_tsv("THREE_HUNDRED_FIFTY_SEVENTH_THIRTEEN_BREAK_DECISIONS.tsv")
    boundaries = read_tsv("THREE_HUNDRED_FIFTY_SEVENTH_TWELVE_LOGICAL_BOUNDARIES.tsv")
    transcripts = read_tsv("THREE_HUNDRED_FIFTY_SEVENTH_FOUR_CORRECTOR_TRANSCRIPTS.tsv")
    decision_counts = Counter(row["corrector_decision"] for row in breaks)
    checks = {
        "forty_four_cards": len(cards) == 44,
        "eleven_per_hand": all(sum(row["hand"] == hand for row in cards) == 11 for hand in {row["hand"] for row in cards}),
        "thirteen_breaks": len(breaks) == 13,
        "four_collapse_nine_keep": decision_counts == {"COLLAPSE_READ_ONCE": 4, "KEEP_SEPARATE_NO_COPY": 9},
        "collapsed_pairs_match_surface": all(row["margin_surface"] == row["next_line_first_surface"] and row["same_owner"] == "YES" and row["slot_order_nondecreasing"] == "YES" for row in breaks if row["corrector_decision"] == "COLLAPSE_READ_ONCE"),
        "twelve_boundaries": len(boundaries) == 12,
        "three_boundaries_per_hand": all(sum(row["hand"] == hand for row in boundaries) == 3 for hand in {row["hand"] for row in cards}),
        "four_owner_handoffs": sum(row["owner_change"] == "YES" for row in boundaries) == 4,
        "four_transcripts": len(transcripts) == 4,
        "all_exact": all(row["recovered_source_cards"] == "11" and row["recovered_microcycles"] == "4" and row["exact_reconstruction"] == "YES" for row in transcripts),
        "visible_48_source_44": sum(int(row["visible_surface_instances"]) for row in transcripts) == 48 and len(cards) == 44,
        "all_cards_count_once": all(row["card_count_after_read_once"] == "1" for row in cards),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
