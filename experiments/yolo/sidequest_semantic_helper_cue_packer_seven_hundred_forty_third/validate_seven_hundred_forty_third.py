#!/usr/bin/env python3
"""Validate Pass 743 helper-cue packer."""

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
    rules = read("SEVEN_HUNDRED_FORTY_THIRD_9_HELPER_RULES.tsv")
    audit = read("SEVEN_HUNDRED_FORTY_THIRD_116_REFINED_PACKING_AUDIT.tsv")
    gaps = read("SEVEN_HUNDRED_FORTY_THIRD_COMPONENT_GAPS.tsv")
    errors = read("SEVEN_HUNDRED_FORTY_THIRD_PACKING_ERRORS.tsv")
    deltas = read("SEVEN_HUNDRED_FORTY_THIRD_CARD_COUNT_DELTAS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTY_THIRD_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    rule_uses = {row["rule"]: int(row["uses"]) for row in rules}
    delta_counts = {int(row["card_count_delta"]): int(row["statements"]) for row in deltas}
    checks = {
        "inventory_9_116_3_42": (len(rules), len(audit), len(gaps), len(errors)) == (9, 116, 3, 42),
        "rule_uses_exact": rule_uses == {
            "ADD_AIN_IN_ANSATZPORTION": 1, "ADD_OT_IN_NAECHST": 2,
            "DROP_SH_AFTER_BEREITET": 9, "DROP_SH_AFTER_SAMMELSTELLE": 7,
            "DROP_SH_IN_WORKFLOW_DURCHLASS": 1, "DROP_CTH_AFTER_ZUTAT": 1,
            "DROP_OT_ABSORBED_BY_PHRASE": 5, "DROP_OL_ABSORBED_BY_PHRASE": 4,
            "DROP_OR_AS_FLUENT_OBJECT": 1,
        },
        "component_sets_113": sum(row["exact_component_set"] == "YES" for row in audit) == 113,
        "three_gaps_exact": {(row["statement_id"], row["missing_components"], row["extra_components"]) for row in gaps} == {("H1-S001", "OS", "NONE"), ("H2-S001", "O", "NONE"), ("H3-S001", "O+T+Y", "NONE")},
        "recipes_74_errors_42": sum(row["exact_recipe_sequence"] == "YES" for row in audit) == 74 and len(errors) == 42,
        "card_counts_368_381_equal91": sum(int(row["predicted_cards"]) for row in audit) == 368 and sum(int(row["observed_cards"]) for row in audit) == 381 and sum(int(row["card_count_delta"]) == 0 for row in audit) == 91,
        "delta_rows_sum_116": sum(delta_counts.values()) == 116,
        "register_exact_4_70": summary["herbal_exact"] == 4 and summary["biological_exact"] == 70,
        "generation_contract_fixed": all(row["generation_contract"] == "CLEAN_INSTRUCTION_PLUS_HELPER_RULES_PLUS_UNCHANGED_173_CARD_DECK" for row in audit),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "all_statement_ids_unique": len({row["statement_id"] for row in audit}) == 116,
        "fixed_pages_only": {row["page"] for row in audit} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in [rules, audit, gaps, errors, deltas] for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
