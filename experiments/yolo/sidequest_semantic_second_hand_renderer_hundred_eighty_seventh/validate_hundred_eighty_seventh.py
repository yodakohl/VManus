#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    tokens = read("HUNDRED_EIGHTY_SEVENTH_73_TOKEN_HAND_B_RENDERING.tsv")
    fields = read("HUNDRED_EIGHTY_SEVENTH_18_FIELD_HAND_B_EDITION.tsv")
    cards = read("HUNDRED_EIGHTY_SEVENTH_23_CARD_ALLOGRAPH_MAP.tsv")
    rules = read("HUNDRED_EIGHTY_SEVENTH_5_RENDERER_RULES.tsv")
    readable = (HERE / "HUNDRED_EIGHTY_SEVENTH_HAND_B_READABLE_EDITION.md").read_text(encoding="utf-8")
    readable_sequences = re.findall(r"^`([^`]+)`$", readable, flags=re.MULTILINE)
    expected_sections = [
        " | ".join(row["hand_b_sequence"] for row in fields if row["section"] == section)
        for section in ["A", "C", "B", "D"]
    ]
    maximum_order = {}
    for row in tokens:
        maximum_order[row["global_field_id"]] = max(maximum_order.get(row["global_field_id"], 0), int(row["global_token_order"]))
    checks = {
        "73_tokens": len(tokens) == 73 and [int(row["global_token_order"]) for row in tokens] == list(range(1, 74)),
        "18_fields": len(fields) == 18 and [row["global_field_id"] for row in fields] == [f"N{i:02d}" for i in range(1, 19)],
        "45_cards": len({row["master_card_id"] for row in tokens}) == 45,
        "40_changed_33_unchanged": sum(row["surface_changed"] == "YES" for row in tokens) == 40 and sum(row["surface_changed"] == "NO" for row in tokens) == 33,
        "23_changed_cards": len(cards) == 23,
        "all_hand_b_surfaces_registered": all(row["hand_b_surface"] in row["registered_surface_inventory"].split("|") for row in tokens),
        "exact_card_readback": all(row["master_card_id"] == row["decoded_card_id"] for row in tokens),
        "exact_value_readback": all(row["hand_a_value_de"] == row["hand_b_decoded_value_de"] for row in tokens),
        "exact_field_card_sequences": all(row["card_id_sequence"] == row["decoded_card_id_sequence"] for row in fields),
        "readable_edition_exact": readable_sequences == expected_sections,
        "terminal_positions_preserved": all(row["finality_rule"] != "ALWAYS_FIELD_FINAL" or int(row["global_token_order"]) == maximum_order[row["global_field_id"]] for row in tokens),
        "five_rules": [row["rule_id"] for row in rules] == [f"H{i}" for i in range(1, 6)],
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [tokens, fields, cards, rules] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "decision": "SECOND_HAND_CHANGES_40_SURFACES_WITH_EXACT_73_CARD_READBACK",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
