#!/usr/bin/env python3
"""Validate Pass 742 attested card packer."""

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
    inventory = read("SEVEN_HUNDRED_FORTY_SECOND_162_ATTESTED_RECIPE_BAGS.tsv")
    audit = read("SEVEN_HUNDRED_FORTY_SECOND_116_PACKING_AUDIT.tsv")
    steps = read("SEVEN_HUNDRED_FORTY_SECOND_402_PACKED_CARD_STEPS.tsv")
    deltas = read("SEVEN_HUNDRED_FORTY_SECOND_CARD_COUNT_DELTAS.tsv")
    errors = read("SEVEN_HUNDRED_FORTY_SECOND_48_PACKING_ERRORS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTY_SECOND_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    delta_counts = {int(row["predicted_minus_observed_cards"]): int(row["statements"]) for row in deltas}
    checks = {
        "inventory_162_116_402_48": (len(inventory), len(audit), len(steps), len(errors)) == (162, 116, 402, 48),
        "deck_recipe_counts": summary["cards_in_deck"] == 173 and summary["ordered_recipes"] == 163 and summary["component_bags"] == 162 and summary["max_recipe_components"] == 5,
        "exact_recipe_sequences_68": sum(row["exact_recipe_sequence"] == "YES" for row in audit) == 68,
        "exact_recipe_multisets_68": sum(row["exact_recipe_multiset"] == "YES" for row in audit) == 68,
        "equal_card_count_85": sum(int(row["card_count_delta"]) == 0 for row in audit) == 85,
        "card_totals_402_381": sum(int(row["predicted_cards"]) for row in audit) == len(steps) == 402 and sum(int(row["observed_cards"]) for row in audit) == 381,
        "attested_and_fallback_334_68": sum(row["attested"] == "YES" for row in steps) == 334 and sum(row["attested"] == "NO" for row in steps) == 68,
        "delta_distribution_exact": delta_counts == {-4: 1, -3: 3, -2: 1, -1: 6, 0: 85, 1: 7, 2: 7, 3: 4, 4: 1, 5: 1},
        "register_exact_2_66": summary["herbal_exact"] == 2 and summary["biological_exact"] == 66,
        "generation_contract_fixed": all(row["generation_contract"] == "RECODED_COMPONENTS_PLUS_ATTESTED_173_CARD_DECK_ONLY" for row in audit),
        "all_statement_ids_unique": len({row["statement_id"] for row in audit}) == 116,
        "fixed_pages_only": {row["page"] for row in audit} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in [inventory, audit, steps, deltas, errors] for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTY_SECOND_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
