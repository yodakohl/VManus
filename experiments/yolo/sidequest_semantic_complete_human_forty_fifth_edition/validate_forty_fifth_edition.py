#!/usr/bin/env python3
"""Consistency checks for the integrated ten-page human edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    units = read("FORTY_FIFTH_258_READING_UNITS.tsv")
    pages = read("FORTY_FIFTH_TEN_PAGE_SUMMARY.tsv")
    kit = read("FORTY_FIFTH_CURRENT_TEACHING_KIT.tsv")
    checks = {
        "ten_pages": len(pages) == 10 and {row["page"] for row in pages} == PAGES,
        "units_258": len(units) == 258,
        "unit_ids_unique": len({row["unit_id"] for row in units}) == 258,
        "prose_116": sum(row["unit_kind"] == "PROSE_STATEMENT" for row in units) == 116,
        "astro_142": sum(row["unit_kind"] == "ASTRO_LOCUS" for row in units) == 142,
        "groups_776": sum(int(row["group_count"]) for row in units) == 776,
        "prose_groups_381": sum(int(row["group_count"]) for row in units if row["unit_kind"] == "PROSE_STATEMENT") == 381,
        "astro_groups_395": sum(int(row["group_count"]) for row in units if row["unit_kind"] == "ASTRO_LOCUS") == 395,
        "page_counts_match": all(int(page["reading_units"]) == sum(row["page"] == page["page"] for row in units) and int(page["visible_groups"]) == sum(int(row["group_count"]) for row in units if row["page"] == page["page"]) for page in pages),
        "all_have_short_reading": all(row["short_workshop_reading_de"] for row in units),
        "all_have_full_reading": all(row["fully_spoken_reading_de"] for row in units),
        "nine_teaching_layers": len(kit) == 9,
        "all_source_hashes": all(len(row["source_sha256"]) == 64 for row in kit),
        "human_edition_exists": (OUT / "FORTY_FIFTH_COMPLETE_TEN_PAGE_HUMAN_EDITION.md").exists(),
        "sealed_absent": not any(row["page"] in {"f84", "f84r"} for row in units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
