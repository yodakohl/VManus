#!/usr/bin/env python3
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
    sources = read_tsv("PASS959_HISTORICAL_SOURCES.tsv")
    entries = read_tsv("PASS959_122_ENTRY_HISTORICAL_CROSSWALK.tsv")
    pages = read_tsv("PASS959_14_PAGE_HISTORICAL_CROSSWALK.tsv")
    checks = {
        "six_sources": len(sources) == 6,
        "all_sources_have_urls": all(row["url"].startswith("https://") for row in sources),
        "exact_122_entries": len(entries) == 122,
        "unique_entry_ids": len({row["codebook_entry_id"] for row in entries}) == 122,
        "exact_56_roots": Counter(row["entry_type"] for row in entries)["PRODUCTIVE_ROOT"] == 56,
        "exact_66_formulas": Counter(row["entry_type"] for row in entries)["LEARNED_FORMULA"] == 66,
        "every_entry_has_mechanism": all(row["historical_mechanism"] and row["source_ids"] for row in entries),
        "exact_14_pages": len(pages) == 14,
        "page_set": {row["physical_page"] for row in pages} == {"f10r", "f11r", "f13r", "f55v", "f56r", "f75r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v", "f70v", "f88r"},
        "no_sealed_pages": not any("f84" in str(row).lower() for row in sources + entries + pages),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS959_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
