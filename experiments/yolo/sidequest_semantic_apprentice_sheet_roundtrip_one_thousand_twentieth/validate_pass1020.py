#!/usr/bin/env python3
"""Validate the compact Pass 1020 apprentice sheet release."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    categories = read_tsv("PASS1020_31_CATEGORY_LEXICON.tsv")
    coverage = read_tsv("PASS1020_627_SHEET_COVERAGE.tsv")
    f13r = read_tsv("F13R_COMPLETE_ROUNDTRIP.tsv")
    f67r2 = read_tsv("F67R2_COMPLETE_ROUNDTRIP.tsv")
    type_counts = Counter(row["category_type"] for row in categories)
    graphic_signs = {
        sign for row in categories for sign in row["graphic_signs"].split("|")
    }
    checks = {
        "thirty_one_categories": len(categories) == 31,
        "nineteen_portable_cores": type_counts["PORTABLE_CORE"] == 19,
        "eight_formal_controls": type_counts["FORMAL_CONTROL"] == 8,
        "four_local_channels": type_counts["LOCAL_CHANNEL"] == 4,
        "forty_six_graphic_signs": len(graphic_signs) == 46,
        "revised_three_values_present": all(
            any(r["graphic_signs"] == sign and r["short_value_de"] == value for r in categories)
            for sign, value in (("AIIN", "WERT"), ("AIN", "ANTEIL"), ("OR", "EINHEIT"))
        ),
        "six_hundred_twenty_seven_statements": len(coverage) == 627,
        "three_thousand_eight_hundred_eighty_eight_events": sum(int(r["event_count"]) for r in coverage) == 3888,
        "all_statements_covered": all(r["sheet_result"] == "FULLY_READABLE_FROM_ONE_SHEET" for r in coverage),
        "no_unknown_atoms": all(r["unknown_atoms"] == "NONE" for r in coverage),
        "all_four_registers": {r["register"] for r in coverage} == {"HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"},
        "sealed_pages_absent": all(not r["page"].startswith("f84") for r in coverage),
        "one_page_sheet_present": (OUT / "PASS1020_ONE_PAGE_APPRENTICE_SHEET.md").is_file(),
        "historical_one_page_sheet_present": (OUT / "HISTORICAL_ONE_PAGE_MASTER_SHEET.md").is_file(),
        "f13r_complete_roundtrip": len(f13r) == 5 and sum(int(r["event_count"]) for r in f13r) == 77,
        "f67r2_complete_roundtrip": len(f67r2) == 11 and sum(int(r["event_count"]) for r in f67r2) == 126,
        "roundtrip_rows_complete": all(
            r["roundtrip_status"].startswith("COMPLETE_CARD_COVERAGE")
            for r in f13r + f67r2
        ),
        "roundtrip_statement_sets": (
            {r["statement_id"] for r in f13r} == {f"P1009-S{i:03d}" for i in range(5, 10)}
            and {r["statement_id"] for r in f67r2} == {f"P1009-S{i:03d}" for i in range(31, 42)}
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failures else "FAIL", "checks": checks, "failures": failures}
    (OUT / "PASS1020_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
