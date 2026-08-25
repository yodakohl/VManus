#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    assignments = read("SEVEN_HUNDRED_SEVENTY_SECOND_39_COMPONENT_ASSIGNMENT.tsv")
    rules = read("SEVEN_HUNDRED_SEVENTY_SECOND_9_RULE_COMPONENT_NEEDS.tsv")
    cards = read("SEVEN_HUNDRED_SEVENTY_SECOND_173_CARD_RECIPE_ACCESS.tsv")
    statements = read("SEVEN_HUNDRED_SEVENTY_SECOND_116_STATEMENT_ACCESS.tsv")
    options = read("SEVEN_HUNDRED_SEVENTY_SECOND_6_VOCABULARY_OPTIONS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTY_SECOND_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    tiers = {name: [row for row in assignments if row["new_tier"] == name] for name in {row["new_tier"] for row in assignments}}
    choice = next(row for row in options if row["decision"] == "SELECT")
    checks = {
        "counts_39_9_173_116_6": (len(assignments), len(rules), len(cards), len(statements), len(options)) == (39, 9, 173, 116, 6),
        "tier_partition_12_21_6": (len(tiers["FAST_12_ORAL_CORE"]), len(tiers["WALL_21_RULE_STRIP"]), len(tiers["MODEL_ONLY_6_RARE_VALUES"])) == (12, 21, 6),
        "model_components_exact": {row["component"] for row in tiers["MODEL_ONLY_6_RARE_VALUES"]} == {"LSH", "CFH", "DA", "LD", "OS", "TALAM"},
        "all_nine_rules_usable": all(row["usable_with_33_rule_vocabulary"] == "YES" and row["model_only_components"] == "0" for row in rules),
        "card_partition_63_103_7": (sum(row["access_mode"] == "FAST_ORAL_COMPOSITION" for row in cards), sum(row["access_mode"] == "WALL_STRIP_COMPOSITION" for row in cards), sum(row["access_mode"] == "REGISTERED_WHOLE_CARD_MODEL_LOOKUP" for row in cards)) == (63, 103, 7),
        "event_partition_213_160_8": (sum(int(row["events"]) for row in cards if row["access_mode"] == "FAST_ORAL_COMPOSITION"), sum(int(row["events"]) for row in cards if row["access_mode"] == "WALL_STRIP_COMPOSITION"), sum(int(row["events"]) for row in cards if row["access_mode"] == "REGISTERED_WHOLE_CARD_MODEL_LOOKUP")) == (213, 160, 8),
        "statement_partition_41_68_7": (sum(row["access_mode"] == "FAST_ONLY" for row in statements), sum(row["access_mode"] == "FAST_PLUS_WALL_STRIP" for row in statements), sum(row["access_mode"] == "USES_RARE_MODEL_CARD" for row in statements)) == (41, 68, 7),
        "rule33_option_exact": (choice["components"], choice["composable_cards"], choice["composable_events"], choice["fully_composable_statements"], choice["usable_parameterized_rules"]) == ("33", "166", "373", "109", "9"),
        "readings_unchanged": all(row["reading_changed"] == "NO" and row["rebuilt_reading_de"] for row in cards),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (assignments, rules, cards, statements, options) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["rules_usable"] == 9,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
