#!/usr/bin/env python3
"""Validate the six-phrase process/state book."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    transitions = rows("SIX_HUNDRED_SIXTY_SECOND_11_FLUENT_TRANSITIONS.tsv")
    phrases = rows("SIX_HUNDRED_SIXTY_SECOND_6_TEACHING_PHRASES.tsv")
    checks = {
        "eleven_transitions": len(transitions) == 11,
        "six_phrases": len(phrases) == 6,
        "all_assigned": {row["phrase_id"] for row in transitions} == {row["phrase_id"] for row in phrases},
        "phrase_counts_sum": sum(int(row["instances"]) for row in phrases) == 11,
        "four_set_ready": sum(row["phrase_id"] == "P01_SET_TO_READY" for row in transitions) == 4,
        "two_set_settle": sum(row["phrase_id"] == "P02_SET_TO_SETTLE_CLOSE" for row in transitions) == 2,
        "two_ready_set": sum(row["phrase_id"] == "P03_READY_TO_GRADED_SET" for row in transitions) == 2,
        "three_singletons": sum(int(row["instances"]) == 1 for row in phrases) == 3,
        "all_source_cards_retained": all(row["source_cards_retained"] == "YES" for row in transitions),
        "no_placeholders": all("UNKNOWN" not in row["fluent_phrase_de"] for row in transitions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
