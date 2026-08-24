#!/usr/bin/env python3
"""Validate the all-record core and specialist trays."""

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
    subprocess.run(["python3", str(HERE / "build_six_hundred_eighty_eighth.py")], check=True)
    roots = read("SIX_HUNDRED_EIGHTY_EIGHTH_39_ROOT_ECOLOGY.tsv")
    trays = read("SIX_HUNDRED_EIGHTY_EIGHTH_11_RECORD_SPECIALIST_TRAYS.tsv")
    recipes = read("SIX_HUNDRED_EIGHTY_EIGHTH_163_RECIPE_ECOLOGY.tsv")
    unique = read("SIX_HUNDRED_EIGHTY_EIGHTH_9_UNIQUE_ROOTS.tsv")
    tiers = read("SIX_HUNDRED_EIGHTY_EIGHTH_4_SHARED_TIERS.tsv")
    tier_counts = Counter(row["shared_tier"] for row in roots)
    checks = {
        "thirty_nine_roots": len(roots) == 39,
        "universal_three": {row["component"] for row in roots if row["records_used"] == "11"} == {"AIIN", "OL", "Y"},
        "thirteen_pocket_core": sum(int(row["records_used"]) >= 8 for row in roots) == 13,
        "tier_counts": tier_counts == Counter({"UNIVERSAL_11": 3, "COMMON_8_TO_10": 10, "EXTENDED_5_TO_7": 10, "SPECIALIST_1_TO_4": 16}),
        "eleven_trays": len(trays) == 11,
        "three_roots_in_every_tray": all(set(row["universal_roots"].split()) == {"AIIN", "OL", "Y"} for row in trays),
        "one_hundred_sixty_three_recipes": len(recipes) == 163,
        "one_universal_recipe": sum(row["records_used"] == "11" for row in recipes) == 1 and next(row["component_recipe"] for row in recipes if row["records_used"] == "11") == "AIIN",
        "nine_unique_roots": len(unique) == 9,
        "four_tiers": len(tiers) == 4 and sum(int(row["root_count"]) for row in tiers) == 39,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
