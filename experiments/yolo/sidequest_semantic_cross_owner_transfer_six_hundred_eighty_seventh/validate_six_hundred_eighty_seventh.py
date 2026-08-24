#!/usr/bin/env python3
"""Validate H3-to-B1 cross-owner transfer accounting."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_eighty_seventh.py")], check=True)
    roots = read("SIX_HUNDRED_EIGHTY_SEVENTH_31_ROOT_TRANSFER.tsv")
    recipes = read("SIX_HUNDRED_EIGHTY_SEVENTH_2_EXACT_RECIPE_TRANSFERS.tsv")
    events = read("SIX_HUNDRED_EIGHTY_SEVENTH_83_EVENT_TRANSFER_CLASSES.tsv")
    levels = read("SIX_HUNDRED_EIGHTY_SEVENTH_4_TRANSFER_LEVELS.tsv")
    counts = Counter(row["transfer_class"] for row in events)
    checks = {
        "thirty_one_union_roots": len(roots) == 31,
        "twelve_shared_roots": sum(row["transfer_class"] == "SHARED_ROOT" for row in roots) == 12,
        "two_shared_recipes": len(recipes) == 2 and {row["component_recipe"] for row in recipes} == {"AIIN", "Y"},
        "eighty_three_events": len(events) == 83 and len({row["event_id"] for row in events}) == 83,
        "seven_exact_recipe_events": counts["EXACT_RECIPE_TRANSFER"] == 7,
        "seventy_two_root_recombinations": counts["SHARED_ROOT_RECOMBINATION"] == 72,
        "four_owner_local_events": counts["OWNER_LOCAL_ROOT_RECIPE"] == 4,
        "four_transfer_levels": len(levels) == 4,
        "fixed_pages": {row["page"] for row in events} == {"f11r", "f81v"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
