#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rules = read("TWO_HUNDRED_EIGHTY_EIGHTH_TWO_FINAL_WRITER_RULES.tsv")
    recipes = read("TWO_HUNDRED_EIGHTY_EIGHTH_149_DETERMINISTIC_RECIPES.tsv")
    occurrences = read("TWO_HUNDRED_EIGHTY_EIGHTH_SIX_FINAL_OCCURRENCES.tsv")
    checks = {
        "rules_2": len(rules) == 2,
        "occurrences_6": len(occurrences) == 6,
        "recipes_149": len(recipes) == 149,
        "master_cards_149": len({r["master_card_id"] for r in recipes}) == 149,
        "recipes_unique": len({r["final_recipe"] for r in recipes}) == 149,
        "events_352": sum(int(r["event_support"]) for r in recipes) == 352,
        "all_rule_matches": all(r["rule_matches_observed_card"] == "YES" for r in occurrences),
        "cth_events_3": sum(r["resolved_subtype"] == "LOCAL_CTH_ALLOGRAPH" for r in occurrences) == 3,
        "ot_transfer_events_3": sum(r["resolved_subtype"] == "LOCAL_OT_TRANSFER_ALLOGRAPH" for r in occurrences) == 3,
        "no_sealed_page": all("f84" not in "\t".join(r.values()).lower() for r in rules + recipes + occurrences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
