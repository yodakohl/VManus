#!/usr/bin/env python3
"""Validate the short workshop dictionary."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SIX_HUNDRED_SIXTH_THIRTY_EIGHT_ONE_WORD_COMPONENTS.tsv")
    cards = read("SIX_HUNDRED_SIXTH_173_SHORT_CARD_DICTIONARY.tsv")
    events = read("SIX_HUNDRED_SIXTH_381_SHORT_EVENT_EDITION.tsv")
    statements = read("SIX_HUNDRED_SIXTH_116_SHORT_STATEMENT_EDITION.tsv")
    component_words = {row["component"]: row["short_workshop_word_de"] for row in components}
    card_by_id = {row["card_no"]: row for row in cards}
    checks = {
        "components38": len(components) == 38 and len(component_words) == 38,
        "all_components_one_word": all(len(row["short_workshop_word_de"].split()) == 1 for row in components),
        "cards173": len(cards) == 173 and len(card_by_id) == 173,
        "all_card_parts_known": all(all(part in component_words for part in row["component_parse"].split("+")) for row in cards),
        "all_short_cards_composed_exactly": all(row["short_card_default_de"] == "·".join(component_words[part] for part in row["component_parse"].split("+")) for row in cards),
        "max_five_components": max(int(row["component_count"]) for row in cards) <= 5,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "event_dictionary_consistent": all(row["short_card_default_de"] == card_by_id[row["card_no"]]["short_card_default_de"] for row in events),
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "statement_events381": sum(int(row["event_count"]) for row in statements) == 381,
        "case_expansions_separate": all(row["case_expansion_policy"] == "USE_OWNER_AND_CASE_LEDGER__NOT_CARD_DICTIONARY" for row in cards),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
