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
    preferences = read("HUNDRED_EIGHTY_EIGHTH_227_POSITION_PREFERENCES.tsv")
    tokens = read("HUNDRED_EIGHTY_EIGHTH_73_TOKEN_HAND_C_RENDERING.tsv")
    fields = read("HUNDRED_EIGHTY_EIGHTH_18_FIELD_HAND_C_EDITION.tsv")
    fallbacks = read("HUNDRED_EIGHTY_EIGHTH_12_POSITION_FALLBACKS.tsv")
    cards = read("HUNDRED_EIGHTY_EIGHTH_11_CHANGED_CARD_MAP.tsv")
    readable = (HERE / "HUNDRED_EIGHTY_EIGHTH_HAND_C_READABLE_EDITION.md").read_text(encoding="utf-8")
    readable_sequences = re.findall(r"^`([^`]+)`$", readable, flags=re.MULTILINE)
    expected_sections = [
        " | ".join(row["hand_c_sequence"] for row in fields if row["section"] == section)
        for section in ["A", "C", "B", "D"]
    ]
    maximum_order = {}
    for row in tokens:
        maximum_order[row["global_field_id"]] = max(maximum_order.get(row["global_field_id"], 0), int(row["global_token_order"]))
    checks = {
        "227_preferences": len(preferences) == 227,
        "preference_events_reconcile": sum(int(row["observed_events"]) for row in preferences) == 381,
        "73_tokens": len(tokens) == 73 and [int(row["global_token_order"]) for row in tokens] == list(range(1, 74)),
        "18_fields": len(fields) == 18,
        "61_exact_12_fallback": sum(row["position_fallback"] == "NO" for row in tokens) == 61 and len(fallbacks) == 12,
        "16_changed_57_unchanged": sum(row["surface_changed"] == "YES" for row in tokens) == 16 and sum(row["surface_changed"] == "NO" for row in tokens) == 57,
        "11_changed_cards": len(cards) == 11,
        "exact_card_readback": all(row["master_card_id"] == row["decoded_card_id"] for row in tokens),
        "field_card_sequences_exact": all(row["card_id_sequence"] == row["decoded_card_id_sequence"] for row in fields),
        "terminal_positions_preserved": all(row["finality_rule"] != "ALWAYS_FIELD_FINAL" or int(row["global_token_order"]) == maximum_order[row["global_field_id"]] for row in tokens),
        "readable_edition_exact": readable_sequences == expected_sections,
        "all_support_positive": all(int(row["support_events"]) > 0 for row in tokens),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [preferences, tokens, fields, fallbacks, cards] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "decision": "POSITIONAL_HAND_C_CHANGES_16_SURFACES_WITH_EXACT_READBACK",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
