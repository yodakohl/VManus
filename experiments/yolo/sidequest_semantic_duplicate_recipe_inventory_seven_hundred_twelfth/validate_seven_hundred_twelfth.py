#!/usr/bin/env python3
"""Validate Pass 712 semantic-family inventory."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    families = read("SEVEN_HUNDRED_TWELFTH_163_SEMANTIC_CARD_FAMILIES.tsv")
    mapping = read("SEVEN_HUNDRED_TWELFTH_173_EXACT_TO_SEMANTIC_MAP.tsv")
    duplicates = read("SEVEN_HUNDRED_TWELFTH_10_DUPLICATE_RECIPE_FAMILIES.tsv")
    occurrences = read("SEVEN_HUNDRED_TWELFTH_71_DUPLICATE_OCCURRENCES.tsv")
    rules = read("SEVEN_HUNDRED_TWELFTH_10_COPY_SUBFAMILY_RULES.tsv")
    checks = {
        "families_163": len(families) == 163,
        "family_ids_unique": len({row["semantic_family"] for row in families}) == 163,
        "mapping_173": len(mapping) == 173,
        "exact_cards_unique": len({row["exact_card_id"] for row in mapping}) == 173,
        "all_mapping_families_exist": {row["semantic_family"] for row in mapping} <= {row["semantic_family"] for row in families},
        "duplicate_families_10": len(duplicates) == 10,
        "duplicate_cards_20": sum(len(row["exact_card_ids"].split("|")) for row in duplicates) == 20,
        "duplicate_occurrences_71": len(occurrences) == 71,
        "copy_rules_10": len(rules) == 10,
        "safe_merges_6": sum(row["merge_status"] == "SEMANTIC_MERGE__OWNER_RECORD_SUBFAMILIES" for row in duplicates) == 6,
        "provisional_merges_4": sum(row["merge_status"] == "PROVISIONAL_SEMANTIC_MERGE__EXEMPLAR_CHOICE_REQUIRED" for row in duplicates) == 4,
        "no_semantic_splits": all(row["semantic_split_selected"] == "NO" for row in duplicates),
        "all_copy_ids_preserved": all(row["copy_subfamily_preserved"] == "YES" for row in mapping),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWELFTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
