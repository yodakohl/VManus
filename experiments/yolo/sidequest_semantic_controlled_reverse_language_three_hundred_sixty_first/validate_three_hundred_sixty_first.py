#!/usr/bin/env python3
"""Validate exact reverse parsing of the controlled workshop language."""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    phrases = read_tsv("THREE_HUNDRED_SIXTY_FIRST_159_CONTROLLED_PHRASES.tsv")
    cards = read_tsv("THREE_HUNDRED_SIXTY_FIRST_380_CONTROLLED_SOURCE_CARDS.tsv")
    statements = read_tsv("THREE_HUNDRED_SIXTY_FIRST_116_REVERSE_PARSED_STATEMENTS.tsv")
    checks = {
        "159_phrases": len(phrases) == 159,
        "phrases_unique": len({row["controlled_phrase"] for row in phrases}) == 159,
        "reverse_keys_unique": len({row["reverse_key"] for row in phrases}) == 159,
        "all_phrase_mappings_unique": all(row["unique_reverse_mapping"] == "YES" for row in phrases),
        "380_cards": len(cards) == 380 and len({row["source_position_id"] for row in cards}) == 380,
        "all_cards_reverse_exact": all(row["slot_code"] == row["recovered_slot_code"] and row["atomic_value_de"] == row["recovered_atomic_value_de"] and row["exact_reverse_parse"] == "YES" for row in cards),
        "116_statements": len(statements) == 116,
        "all_statements_reverse_exact": all(row["controlled_reverse_status"] == "EXACT" and row["source_values_de"] == row["recovered_values_de"] for row in statements),
        "event_coverage_once": sorted(event for row in statements for event in row["source_event_ids"].split("|")) == sorted(row["event_id"] for row in cards),
        "all_free_layers_declared_aligned": all(row["free_layer_reverse_status"] == "NEEDS_EVENT_ALIGNMENT_LEDGER" for row in statements),
        "six_slot_words": {row["controlled_phrase"].split("[", 1)[0] for row in phrases} == {"BEZUG", "MASS", "TRANSFER", "ZUSTAND", "ZIEL", "SCHLUSS"},
        "seven_pages_implicit_by_records": {row["record_unit_id"] for row in cards} == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
