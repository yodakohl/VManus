#!/usr/bin/env python3
"""Validate the finite source lexicon and fourteen programs."""

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
    lexicon = read_tsv("SEVENTY_FOURTH_54_FINITE_SOURCE_WORDS.tsv")
    programs = read_tsv("SEVENTY_FOURTH_14_FINITE_SOURCE_PROGRAMS.tsv")
    binding = read_tsv("SEVENTY_FOURTH_776_FINITE_SOURCE_BINDING.tsv")
    slots = {row["source_slot"] for row in lexicon}
    counts = Counter(row["register"] for row in lexicon)
    checks = {
        "fifty_four_source_words": len(lexicon) == 54 and len(slots) == 54,
        "register_partition": counts == Counter({"SHARED": 6, "HERBAL": 16, "BIO": 16, "ASTRO": 16}),
        "source_words_not_visible_words": all(row["visible_card_word"] == "NO__SOURCE_LEXICON_ONLY" for row in lexicon),
        "fourteen_programs": len(programs) == 14 and len({row["unit_id"] for row in programs}) == 14,
        "all_program_tokens_licensed": all(set(row["finite_source_program"].split(">")) <= slots for row in programs),
        "no_free_nouns": all(row["free_nouns_outside_lexicon"] == "NONE" for row in programs),
        "776_bindings": len(binding) == 776 and len({row["unified_serial"] for row in binding}) == 776,
        "no_free_master_noun_allowed": all(row["free_master_noun_allowed"] == "NO" for row in binding),
        "unit_group_counts": sum(int(row["group_count"]) for row in programs) == 776,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in lexicon + programs + binding),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
