#!/usr/bin/env python3
"""Validate Pass 701 contrast coverage and bounded prompt encoding."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    contrasts = read("SEVEN_HUNDRED_FIRST_18_CONTRAST_PAIRS.tsv")
    tree = read("SEVEN_HUNDRED_FIRST_8_DECISION_TREE_STEPS.tsv")
    prompts = read("SEVEN_HUNDRED_FIRST_24_FRESH_PROMPT_ENCODINGS.tsv")
    components = [row[key] for row in contrasts for key in ("component_a", "component_b")]
    checks = {
        "contrast_pairs_18": len(contrasts) == 18,
        "components_36": len(components) == 36,
        "each_component_once": all(count == 1 for count in Counter(components).values()),
        "decision_steps_8": len(tree) == 8,
        "prompts_24": len(prompts) == 24,
        "exact_16": sum(row["encoding_status"] == "EXACT_EXISTING_RECIPE" for row in prompts) == 16,
        "missing_8": sum(row["encoding_status"] == "NO_EXACT_CARD__NEAREST_FAMILY_ONLY" for row in prompts) == 8,
        "all_components_known": all(row["requested_components_known"] == "YES" for row in prompts),
        "exact_have_cards": all(bool(row["exact_card_numbers"]) for row in prompts if row["encoding_status"] == "EXACT_EXISTING_RECIPE"),
        "exact_need_no_master": all(row["master_approval"] == "NO" for row in prompts if row["encoding_status"] == "EXACT_EXISTING_RECIPE"),
        "missing_have_no_exact_surface": all(not row["exact_surfaces"] for row in prompts if row["encoding_status"].startswith("NO_EXACT")),
        "missing_distance_one": all(row["nearest_edit_distance"] == "1" for row in prompts if row["encoding_status"].startswith("NO_EXACT")),
        "missing_have_candidates": all(int(row["nearest_recipe_count"]) >= 1 for row in prompts if row["encoding_status"].startswith("NO_EXACT")),
        "missing_require_master": all(row["master_approval"] == "REQUIRED" for row in prompts if row["encoding_status"].startswith("NO_EXACT")),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FIRST_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
