#!/usr/bin/env python3
"""Validate the new in-deck apprentice order."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    forward = read("SIX_HUNDRED_THIRTIETH_6_STEP_FORWARD_ORDER.tsv")
    backward = read("SIX_HUNDRED_THIRTIETH_6_STEP_BACKWARD_READ.tsv")
    prefixes = read("SIX_HUNDRED_THIRTIETH_6_PREFIX_NOVELTY_AUDIT.tsv")
    bigrams = read("SIX_HUNDRED_THIRTIETH_5_BIGRAM_NOVELTY_AUDIT.tsv")
    checks = {
        "six_steps": len(forward) == 6 and len(backward) == 6,
        "expected_surfaces": [row["selected_surface"] for row in forward] == ["qokaiin", "qokain", "qokal", "cheey", "ol", "shedy"],
        "all_surfaces_unique_to_card": all(row["surface_uniquely_identifies_card"] == "YES" for row in forward),
        "all_surfaces_licensed": all(row["surface_licensed_for_card"] == "YES" for row in forward),
        "no_new_word_card_surface": all(row["new_word"] == row["new_card"] == row["new_surface"] == "NO" for row in forward),
        "all_backward_exact": all(row["exact_backward_read"] == "YES" for row in backward),
        "six_prefixes": len(prefixes) == 6,
        "full_sequence_absent": prefixes[-1]["source_occurrences"] == "0",
        "first_bigram_absent": prefixes[1]["source_occurrences"] == "0",
        "five_bigrams": len(bigrams) == 5,
        "four_novel_bigrams": sum(row["source_occurrences"] == "0" for row in bigrams) == 4,
        "one_attested_bigram": sum(row["source_occurrences"] != "0" for row in bigrams) == 1,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
