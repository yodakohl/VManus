#!/usr/bin/env python3
"""Validate source contact of the five composed case templates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    statements = read("SIX_HUNDRED_FORTY_NINTH_116_STATEMENT_CONTACT.tsv")
    positions = read("SIX_HUNDRED_FORTY_NINTH_30_TEMPLATE_POSITION_COUNTS.tsv")
    bigrams = read("SIX_HUNDRED_FORTY_NINTH_25_TEMPLATE_BIGRAM_COUNTS.tsv")
    distribution = read("SIX_HUNDRED_FORTY_NINTH_7_RUN_DISTRIBUTION.tsv")
    checks = {
        "one_hundred_sixteen_statements": len(statements) == 116,
        "three_hundred_eighty_one_events": sum(int(row["event_count"]) for row in statements) == 381,
        "thirty_template_positions": len(positions) == 30,
        "all_template_cards_source_attested": all(int(row["source_event_occurrences"]) >= 1 for row in positions),
        "twenty_five_bigrams": len(bigrams) == 25,
        "one_attested_bigram": sum(row["source_attested"] == "YES" for row in bigrams) == 1,
        "twenty_four_novel_bigrams": sum(row["source_attested"] == "NO" for row in bigrams) == 24,
        "longest_run_two": max(int(row["longest_contiguous_template_run"]) for row in statements) == 2,
        "one_statement_bigram_contact": sum(int(row["longest_contiguous_template_run"]) == 2 for row in statements) == 1,
        "no_full_template": all(row["full_six_card_template_present"] == "NO" for row in statements),
        "seven_distribution_rows": len(distribution) == 7 and sum(int(row["statements"]) for row in distribution) == 116,
        "attested_pair_cth": any(row["card_bigram"] == "PROC017|PROC018" and row["source_attested"] == "YES" for row in bigrams),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
