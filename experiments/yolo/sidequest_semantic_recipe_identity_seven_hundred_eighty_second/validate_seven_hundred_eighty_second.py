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
    recipes = read("SEVEN_HUNDRED_EIGHTY_SECOND_163_RECIPE_DICTIONARY.tsv")
    pairs = read("SEVEN_HUNDRED_EIGHTY_SECOND_10_TWO_CARD_RECIPE_FAMILIES.tsv")
    trace = read("SEVEN_HUNDRED_EIGHTY_SECOND_381_TWO_LEVEL_IDENTITY.tsv")
    paired = read("SEVEN_HUNDRED_EIGHTY_SECOND_71_PAIRED_RECIPE_EVENTS.tsv")
    rules = read("SEVEN_HUNDRED_EIGHTY_SECOND_7_MARGIN_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTY_SECOND_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_163_10_381_71_7": (len(recipes), len(pairs), len(trace), len(paired), len(rules)) == (163, 10, 381, 71, 7),
        "exact_cards173": len({row["exact_copy_identity"] for row in trace}) == 173,
        "all_pairs_two_cards": all(row["card_a"] != row["card_b"] and int(row["pair_events"]) == int(row["card_a_events"]) + int(row["card_b_events"]) for row in pairs),
        "twenty_cards_in_pairs": len({row[key] for row in pairs for key in ("card_a", "card_b")}) == 20,
        "one_cross_hand_exclusive_okol": [(row["component_recipe"], row["ecology"]) for row in pairs if row["ecology"] == "CROSS_HAND_EXCLUSIVE_PAIR"] == [("OK+OL", "CROSS_HAND_EXCLUSIVE_PAIR")],
        "recipe_readings_nonempty": all(row["workshop_reading_de"].strip() for row in recipes),
        "trace_two_level_rules": all(row["spoken_readback_rule"] == "READ_RECIPE_IDENTITY" and row["copy_rule"] == "COPY_EXACT_CARD_IDENTITY" for row in trace),
        "paired_subset_exact": {row["event_id"] for row in paired} == {row["event_id"] for row in trace if row["recipe_has_two_card_realizations"] == "YES"},
        "new_margin_rule": rules[-1]["short_mark"] == "SPRICH/KOPIERE",
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (recipes, pairs, trace, paired, rules) for row in rows),
        "summary_pass": summary["status"] == "PASS" and (summary["exact_cards"], summary["semantic_recipes"], summary["paired_cards"], summary["paired_events"]) == (173, 163, 20, 71),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTY_SECOND_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
