#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    units = read("TWO_HUNDRED_EIGHTY_FIFTH_258_COMPLETE_READING_UNITS.tsv")
    pages = read("TWO_HUNDRED_EIGHTY_FIFTH_TEN_PAGE_SYNOPSIS.tsv")
    page_units = Counter(r["page"] for r in units)
    page_groups = {r["page"]: int(r["visible_group_count"]) for r in pages}
    checks = {
        "reading_units_258": len(units) == 258,
        "visible_groups_776": sum(int(r["visible_group_count"]) for r in units) == 776,
        "register_units_exact": Counter(r["register"] for r in units) == Counter({"HERBAL": 19, "BIO": 97, "ASTRO": 142}),
        "pages_10": len(pages) == 10,
        "page_units_exact": page_units == Counter({"f10r": 5, "f11r": 4, "f55v": 4, "f56r": 6, "f81v": 21, "f82r": 22, "f83r": 54, "f67r2": 74, "f68r1": 37, "f69v": 31}),
        "page_groups_exact": page_groups == {"f10r": 38, "f11r": 17, "f55v": 18, "f56r": 27, "f81v": 66, "f82r": 62, "f83r": 153, "f67r2": 190, "f68r1": 65, "f69v": 140},
        "unit_ids_unique_with_register": len({(r["register"], r["reading_unit_id"]) for r in units}) == 258,
        "all_readings_present": all(r["complete_reading_de"].strip() for r in units),
        "all_page_synopses_present": all(r["continuous_page_reading_de"].strip() for r in pages),
        "page_order_1_10": [int(r["page_order"]) for r in pages] == list(range(1, 11)),
        "no_sealed_page": all("f84" not in "\t".join(r.values()).lower() for r in units + pages),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
