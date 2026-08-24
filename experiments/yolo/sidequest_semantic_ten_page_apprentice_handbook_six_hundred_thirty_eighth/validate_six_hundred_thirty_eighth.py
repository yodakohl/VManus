#!/usr/bin/env python3
"""Validate the complete ten-page apprentice handbook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    ledger = read("SIX_HUNDRED_THIRTY_EIGHTH_776_TEN_PAGE_APPRENTICE_LEDGER.tsv")
    lessons = read("SIX_HUNDRED_THIRTY_EIGHTH_13_ASTRO_NAMESPACE_LESSONS.tsv")
    loci = read("SIX_HUNDRED_THIRTY_EIGHTH_142_ASTRO_LOCUS_COPY_TRACE.tsv")
    pages = read("SIX_HUNDRED_THIRTY_EIGHTH_10_PAGE_CURRICULUM.tsv")
    prose = [row for row in ledger if row["section"] == "PROSE_WORKSHOP"]
    astro = [row for row in ledger if row["section"] == "ASTRO_COPIED_LOOKUP"]
    checks = {
        "ten_pages": len(pages) == 10 and len({row["page"] for row in pages}) == 10,
        "seven_plus_three_pages": sum(row["section"] == "PROSE_WORKSHOP" for row in pages) == 7 and sum(row["section"] == "ASTRO_COPIED_LOOKUP" for row in pages) == 3,
        "seven_hundred_seventy_six_groups": len(ledger) == 776 and len({row["unified_id"] for row in ledger}) == 776,
        "three_eighty_one_plus_three_ninety_five": len(prose) == 381 and len(astro) == 395,
        "thirteen_namespace_lessons": len(lessons) == 13 and len({row["namespace_id"] for row in lessons}) == 13,
        "one_hundred_forty_two_loci": len(loci) == 142 and len({(row["page"], row["locus"]) for row in loci}) == 142,
        "astro_all_whole_copy": all(row["learning_layer"] == "WHOLE_LOCAL_ASTRO_LABEL" and row["writing_or_copy_rule"] == "COPY_COMPLETE_LABEL_FROM_LOCAL_CELESTIAL_EXEMPLAR" for row in astro),
        "astro_optional": all(row["required_for_case"] == "NO" for row in astro),
        "no_orientation_or_key": all(row["orientation"] == "NONE" and row["cross_page_key"] == "NONE" for row in astro),
        "no_prose_import": all(row["prose_word_import"] == "NONE" for row in lessons),
        "page_totals_match": sum(int(row["visible_groups"]) for row in pages) == 776,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
