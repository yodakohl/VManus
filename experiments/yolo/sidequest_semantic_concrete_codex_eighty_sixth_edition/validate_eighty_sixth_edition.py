#!/usr/bin/env python3
"""Validate the combined concrete ten-page codex edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    words = read_tsv("EIGHTY_SIXTH_44_CONCRETE_SOURCE_WORDS.tsv")
    units = read_tsv("EIGHTY_SIXTH_14_CONCRETE_CODEX_UNITS.tsv")
    binding = read_tsv("EIGHTY_SIXTH_776_CONCRETE_CODEX_BINDING.tsv")
    purposes = read_tsv("EIGHTY_SIXTH_3_BOOK_PURPOSE_COMPARISON.tsv")
    domains = Counter(row["domain"] for row in binding)
    checks = {
        "source_words_44": len(words) == 44 and len({row["codex_word_id"] for row in words}) == 44,
        "all_words_source_only": all(row["portable_card_or_root_meaning"] == "NO__SOURCE_PROGRAM_ONLY" for row in words),
        "units_14": len(units) == 14 and len({row["unit_id"] for row in units}) == 14,
        "unit_split": sum(row["domain"] == "HERBAL_RECIPE" for row in units) == 5 and sum(row["domain"] == "BATH_AND_SERVICE" for row in units) == 6 and sum(row["domain"] == "CELESTIAL_ALMANAC" for row in units) == 3,
        "unit_group_sum_776": sum(int(row["group_count"]) for row in units) == 776,
        "binding_776": len(binding) == 776 and [int(row["unified_serial"]) for row in binding] == list(range(1, 777)),
        "binding_split": domains == {"HERBAL_RECIPE": 100, "BATH_AND_SERVICE": 281, "CELESTIAL_ALMANAC": 395},
        "three_purposes": len(purposes) == 3 and len({row["purpose_id"] for row in purposes}) == 3,
        "ten_pages": len({row["page"] for row in units}) == 10,
        "sealed_pages_absent": all(not row["page"].lower().startswith("f84") for row in units + binding),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
