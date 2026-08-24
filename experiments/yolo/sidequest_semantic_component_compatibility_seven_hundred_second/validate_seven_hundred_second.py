#!/usr/bin/env python3
"""Validate Pass 702 compatibility outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    profiles = read("SEVEN_HUNDRED_SECOND_36_COMPONENT_PROFILES.tsv")
    adj = read("SEVEN_HUNDRED_SECOND_161_LICENSED_ADJACENCIES.tsv")
    gaps = read("SEVEN_HUNDRED_SECOND_8_GAP_CLASSIFICATIONS.tsv")
    rules = read("SEVEN_HUNDRED_SECOND_10_COMPATIBILITY_RULES.tsv")
    s_rows = [row for row in profiles if row["component"] == "S"]
    checks = {
        "profiles_36": len(profiles) == 36,
        "components_unique": len({row["component"] for row in profiles}) == 36,
        "adjacencies_161": len(adj) == 161,
        "adjacencies_unique": len({(row["left_component"], row["right_component"]) for row in adj}) == 161,
        "all_adjacencies_supported": all(int(row["card_type_support"]) >= 1 and int(row["event_support"]) >= 1 for row in adj),
        "gaps_8": len(gaps) == 8,
        "gaps_no_new_surface": all(row["new_surface_allowed"] == "NO" for row in gaps),
        "five_likely_unused": sum(row["classification"] == "LIKELY_LICENSED_UNUSED_CELL" for row in gaps) == 5,
        "three_blocked": sum(row["classification"].startswith("BLOCKED") for row in gaps) == 3,
        "rules_10": len(rules) == 10,
        "s_revised_once": len(s_rows) == 1 and s_rows[0]["working_value_de"] == "GETEILT" and s_rows[0]["first_positions"] == "0",
        "dy_hard_final_rule": any(row["rule_id"] == "G04" and "37/37" in row["scope"] for row in rules),
        "measure_relation_zero_rule": any(row["rule_id"] == "G06" and row["scope"].startswith("0 ") for row in rules),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SECOND_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
