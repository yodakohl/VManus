#!/usr/bin/env python3
"""Validate the long-card scope audit."""

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def words(text: str) -> list[str]:
    for char in "[];":
        text = text.replace(char, " ")
    return [part for part in text.replace("·", " ").split() if part not in {"IM", "BIS"}]


def main() -> None:
    cards = read("SIX_HUNDRED_SEVENTH_173_RECITATION_DICTIONARY.tsv")
    long_cards = read("SIX_HUNDRED_SEVENTH_TWENTY_FIVE_LONG_CARD_AUDIT.tsv")
    hard = read("SIX_HUNDRED_SEVENTH_TWELVE_HARD_STATEMENTS.tsv")
    rules = read("SIX_HUNDRED_SEVENTH_SIX_SCOPE_RULES.tsv")
    long_by_id = {row["card_no"]: row for row in long_cards}
    checks = {
        "cards173": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "long_cards25": len(long_cards) == 25 and len(long_by_id) == 25,
        "four_five_split": Counter(int(row["component_count"]) for row in long_cards) == Counter({4: 21, 5: 4}),
        "five_special_notes": sum(int(row["scope_repair_cost"]) for row in cards) == 5,
        "all_component_order_declared_preserved": all(row["component_order_preserved"] == "YES" for row in cards),
        "no_new_whole_meaning": all(row["new_whole_card_semantic_value"] == "NO" for row in cards),
        "long_card_component_inventory_preserved": all(Counter(row["short_surface_order_de"].split("·")) == Counter(words(row["spoken_recitation_de"])) for row in long_cards),
        "hard12": len(hard) == 12 and len({row["statement_id"] for row in hard}) == 12,
        "hard_order_preserved": all(row["source_event_order_preserved"] == "YES" and row["new_semantic_word_added"] == "NO" for row in hard),
        "six_rules": len(rules) == 6,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
