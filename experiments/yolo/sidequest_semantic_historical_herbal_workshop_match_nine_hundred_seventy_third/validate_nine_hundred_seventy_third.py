#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    sources = read("PASS973_HISTORICAL_SOURCES.tsv")
    cross = read("PASS973_SIX_PAGE_HISTORICAL_CROSSWALK.tsv")
    checks = {
        "at_least_ten_sources": len(sources) >= 10,
        "four_visual_comparators": sum(r["weight"] == "DIRECT_VISUAL_COMPARATOR" for r in sources) == 4,
        "six_pages": len(cross) == 6,
        "exact_pages": {r["physical_page"] for r in cross} == {"f10r", "f11r", "f13r", "f55v", "f56r", "f88r"},
        "urls_present": all(r["url"].startswith("https://") for r in sources),
        "limits_present": all(r["still_unlicensed"] for r in cross),
        "no_empty_cells": all(all(v for v in row.values()) for row in sources + cross),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in sources + cross),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS973_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
