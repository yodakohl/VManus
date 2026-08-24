#!/usr/bin/env python3
"""Validate the recipe-indexed copybook layout."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_eighty_first.py")], check=True)
    recipes = read("SIX_HUNDRED_EIGHTY_FIRST_163_RECIPE_COPYBOOK.tsv")
    tabs = read("SIX_HUNDRED_EIGHTY_FIRST_34_FIRST_COMPONENT_TABS.tsv")
    variants = read("SIX_HUNDRED_EIGHTY_FIRST_20_DOUBLE_RECIPE_VARIANTS.tsv")
    sheets = read("SIX_HUNDRED_EIGHTY_FIRST_6_COPYBOOK_SHEETS.tsv")
    checks = {
        "one_hundred_sixty_three_recipes": len(recipes) == 163 and len({row["component_recipe"] for row in recipes}) == 163,
        "one_hundred_seventy_three_cards": sum(int(row["exact_card_variants"]) for row in recipes) == 173,
        "two_hundred_thirty_surfaces": sum(int(row["surface_exemplars"]) for row in recipes) == 230,
        "one_hundred_fifty_three_direct": sum(row["lookup_result"] == "DIRECT_CARD" for row in recipes) == 153,
        "ten_double_recipes": sum(row["lookup_result"] == "CHOOSE_LOCAL_CARD_VARIANT" for row in recipes) == 10,
        "twenty_variant_rows": len(variants) == 20,
        "thirty_four_tabs": len(tabs) == 34 and sum(int(row["recipe_rows"]) for row in tabs) == 163,
        "largest_tab_twenty": max(int(row["recipe_rows"]) for row in tabs) == 20,
        "six_sheets": len(sheets) == 6,
        "three_whole_commands": sum("WHOLE_NOMENCLATOR" in row["historical_layers"] for row in recipes) == 3,
        "addresses_complete": [row["recipe_address"] for row in recipes] == [f"A{index:03d}" for index in range(1, 164)],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
