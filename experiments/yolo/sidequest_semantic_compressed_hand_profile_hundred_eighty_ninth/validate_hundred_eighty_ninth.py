#!/usr/bin/env python3
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
    tokens = read("HUNDRED_EIGHTY_NINTH_73_TOKEN_COMPRESSED_PROFILE.tsv")
    rules = read("HUNDRED_EIGHTY_NINTH_5_HAND_RULES.tsv")
    cards = read("HUNDRED_EIGHTY_NINTH_11_RULE_CARD_PROFILES.tsv")
    rule_counts = Counter(row["rule_applied"] for row in tokens)
    checks = {
        "73_tokens": len(tokens) == 73 and [int(row["global_token_order"]) for row in tokens] == list(range(1, 74)),
        "five_rules": [row["rule_id"] for row in rules] == [f"R{i}" for i in range(1, 6)],
        "coverage_7_3_2_2_2": [int(row["actual_changed_tokens"]) for row in rules] == [7, 3, 2, 2, 2],
        "16_changed_57_default": sum(row["rule_applied"] != "DEFAULT_KEEP" for row in tokens) == 16 and rule_counts["DEFAULT_KEEP"] == 57,
        "11_cards": len(cards) == 11,
        "all_73_match_hand_c": {row["matches_hand_c"] for row in tokens} == {"YES"},
        "all_surfaces_registered": {row["surface_registered"] for row in tokens} == {"YES"},
        "no_false_change": all(row["compressed_profile_surface"] == row["hand_c_surface"] for row in tokens),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [tokens, rules, cards] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "decision": "FIVE_HAND_RULES_REPRODUCE_ALL_73_POSITIONAL_SURFACES",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
