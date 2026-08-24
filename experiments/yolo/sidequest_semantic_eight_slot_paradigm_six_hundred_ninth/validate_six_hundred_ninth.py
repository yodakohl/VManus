#!/usr/bin/env python3
"""Validate the eight-drawer workshop paradigm."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    drawers = read("SIX_HUNDRED_NINTH_EIGHT_SLOT_DRAWERS.tsv")
    words = read("SIX_HUNDRED_NINTH_THIRTY_SEVEN_WORD_PARADIGM.tsv")
    cards = read("SIX_HUNDRED_NINTH_173_CARD_SLOT_PARSE.tsv")
    signatures = read("SIX_HUNDRED_NINTH_SLOT_SIGNATURE_INVENTORY.tsv")
    statements = read("SIX_HUNDRED_NINTH_116_STATEMENT_SLOT_EDITION.tsv")
    slot_names = {row["slot"] for row in drawers}
    checks = {
        "drawers8": len(drawers) == 8 and len(slot_names) == 8,
        "drawer_words37": sum(int(row["word_count"]) for row in drawers) == 37,
        "words37_once": len(words) == 37 and len({row["canonical_component"] for row in words}) == 37,
        "every_word_in_drawer": all(row["paradigm_slot"] in slot_names for row in words),
        "cards173": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "every_card_slot_known": all(all(slot in slot_names for slot in row["slot_signature"].split(">")) for row in cards),
        "signature_inventory_complete": sum(int(row["card_types"]) for row in signatures) == 173 and sum(int(row["events"]) for row in signatures) == 381,
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "statement_events381": sum(int(row["event_count"]) for row in statements) == 381,
        "all_statements_have_slots": all(row["card_slot_signatures"] for row in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
