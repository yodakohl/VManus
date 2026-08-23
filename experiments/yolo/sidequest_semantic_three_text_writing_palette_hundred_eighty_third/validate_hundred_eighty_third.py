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
    usage = read("HUNDRED_EIGHTY_THIRD_48_TOKEN_PALETTE_USAGE.tsv")
    cards = read("HUNDRED_EIGHTY_THIRD_25_CARD_WRITING_PALETTE.tsv")
    slots = read("HUNDRED_EIGHTY_THIRD_6_SLOT_WRITING_PALETTE.tsv")
    substitutions = read("HUNDRED_EIGHTY_THIRD_12_SUBSTITUTION_RULES.tsv")
    class_counts = Counter(row["teaching_class"] for row in cards)
    checks = {
        "48_uses": len(usage) == 48 and [int(row["use_order"]) for row in usage] == list(range(1, 49)),
        "25_cards": len(cards) == 25 and len({row["master_card_id"] for row in cards}) == 25,
        "usage_card_union": {row["master_card_id"] for row in usage} == {row["master_card_id"] for row in cards},
        "six_slots": [row["slot_id"] for row in slots] == [f"G{i}" for i in range(1, 7)],
        "slot_card_counts": [int(row["distinct_cards_used"]) for row in slots] == [2, 7, 4, 5, 5, 3],
        "slot_use_counts": [int(row["token_uses"]) for row in slots] == [4, 12, 8, 8, 11, 5],
        "talam_is_only_multislot_card": [row["master_card_id"] for row in cards if "|" in row["palette_slots"]] == ["MC160"],
        "rare_teaching_split": class_counts["FULLY_COMPOSED_FROM_OTHER_CARDS"] == 6 and class_counts["COMPOSED_FRAME_PLUS_MEMORIZED_BODY"] == 3 and class_counts["MEMORIZED_WHOLE_CARD"] == 4 and class_counts["COMMON_WORKSHOP_CARD"] == 12,
        "twelve_substitutions": len(substitutions) == 12 and [row["substitution_id"] for row in substitutions] == [f"P{i:02d}" for i in range(1, 13)],
        "not_all_same_slot_cards_synonyms": any(row["status"] == "NOT_SUBSTITUTABLE" for row in substitutions) and any(row["status"] == "UNSAFE_SEQUENCE_CHANGE" for row in substitutions),
        "no_empty_values": all(row["portable_value_de"] for row in cards),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [usage, cards, slots, substitutions] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "decision": "THREE_TEXTS_SHARE_A_25_CARD_SIX_SLOT_WRITING_PALETTE",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
