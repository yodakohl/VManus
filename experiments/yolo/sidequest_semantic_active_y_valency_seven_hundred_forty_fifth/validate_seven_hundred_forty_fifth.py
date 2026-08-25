#!/usr/bin/env python3
"""Validate Pass 745 active-Y valency packer."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    valency = read("SEVEN_HUNDRED_FORTY_FIFTH_55_Y_VALENCY_BASES.tsv")
    audit = read("SEVEN_HUNDRED_FORTY_FIFTH_116_Y_PACKING_AUDIT.tsv")
    changed = read("SEVEN_HUNDRED_FORTY_FIFTH_26_CHANGED_STATEMENTS.tsv")
    fixed = read("SEVEN_HUNDRED_FORTY_FIFTH_10_NEWLY_FIXED.tsv")
    residual = read("SEVEN_HUNDRED_FORTY_FIFTH_32_RESIDUAL_ERRORS.tsv")
    components = read("SEVEN_HUNDRED_FORTY_FIFTH_RESIDUAL_COMPONENT_COUNTS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTY_FIFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory_55_116_26_10_32": (len(valency), len(audit), len(changed), len(fixed), len(residual)) == (55, 116, 26, 10, 32),
        "deck_y_inventory_exact": summary["deck_cards"] == 173 and summary["y_cards"] == 60 and summary["y_card_events"] == 124 and summary["written_y_slots"] == 125,
        "valency_split_7_48": summary["optional_y_bases"] == 7 and summary["y_required_bases"] == 48,
        "exact_84_equal95": sum(row["y_valent_exact"] == "YES" for row in audit) == 84 and sum(int(row["y_valent_cards"]) == int(row["observed_cards"]) for row in audit) == 95,
        "copied_y_38": sum(int(row["copied_y"]) for row in audit) == 38,
        "fix10_harm0": sum(row["newly_fixed"] == "YES" for row in audit) == 10 and all(row["newly_harmed"] == "NO" for row in audit),
        "cards_345_381": sum(int(row["y_valent_cards"]) for row in audit) == 345 and sum(int(row["observed_cards"]) for row in audit) == 381,
        "fixed_ids_exact": {row["statement_id"] for row in fixed} == {"H1-S002", "H3-S002", "H4-S003", "B1-S011", "B1-S014", "B2-S006", "B3-S026", "B3-S034", "B4-S008", "B4-S015"},
        "all_rules_y_only": all(row["rule"] == "COPY_Y_ONLY_INSIDE_ATTESTED_Y_VALENT_RECIPE" for row in audit),
        "all_statement_ids_unique": len({row["statement_id"] for row in audit}) == 116,
        "fixed_pages_only": {row["page"] for row in audit} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in [valency, audit, changed, fixed, residual, components] for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTY_FIFTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
