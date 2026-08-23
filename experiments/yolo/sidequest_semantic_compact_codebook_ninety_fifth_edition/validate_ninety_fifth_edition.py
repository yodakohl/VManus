#!/usr/bin/env python3
"""Validate the compact ten-page codebook."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    primitives = rows("NINETY_FIFTH_20_PROSE_PRIMITIVES.tsv")
    cards = rows("NINETY_FIFTH_43_CARD_CODEBOOK.tsv")
    words = rows("NINETY_FIFTH_44_SOURCE_WORDS.tsv")
    astro = rows("NINETY_FIFTH_8_ASTRO_RULES.tsv")
    coverage = rows("NINETY_FIFTH_776_COMPLETE_COVERAGE.tsv")
    modes = Counter(row["compiler_mode"] for row in coverage)
    checks = {
        "primitives_20": len(primitives) == 20,
        "cards_43": len(cards) == 43,
        "card_entries_unique": len({row["entry_id"] for row in cards}) == 43,
        "words_44": len(words) == 44,
        "word_ids_unique": len({row["codex_word_id"] for row in words}) == 44,
        "astro_rules_8": len(astro) == 8,
        "coverage_776": len(coverage) == 776,
        "serial_complete": [int(row["unified_serial"]) for row in coverage] == list(range(1, 777)),
        "mode_counts": modes == Counter({"COMBINATORIAL_PROSE": 381, "LOCAL_ASTRO_NOMENCLATOR": 395}),
        "all_have_primitives": all(row["primitive_sequence"] for row in coverage),
        "all_have_source_words": all(row["source_word_ids"] and row["source_words_de"] for row in coverage),
        "fixed_pages_only": set(row["page"] for row in coverage) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in coverage + words),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
