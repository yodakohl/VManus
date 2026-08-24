#!/usr/bin/env python3
"""Validate the integrated dictionary and complete prose edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("SIX_HUNDRED_SEVENTY_SECOND_39_ROOT_TABLET.tsv")
    cards = read("SIX_HUNDRED_SEVENTY_SECOND_173_CARD_DICTIONARY.tsv")
    events = read("SIX_HUNDRED_SEVENTY_SECOND_381_EVENT_INTERLINEAR.tsv")
    statements = read("SIX_HUNDRED_SEVENTY_SECOND_116_STATEMENT_EDITION.tsv")
    records = read("SIX_HUNDRED_SEVENTY_SECOND_11_RECORD_EDITION.tsv")
    root_set = {row["component"] for row in roots}
    checks = {
        "thirty_nine_roots": len(roots) == 39 and len(root_set) == 39,
        "one_hundred_seventy_three_cards": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "three_hundred_eighty_one_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "one_hundred_sixteen_statements": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "eleven_records": len(records) == 11 and len({row["record"] for row in records}) == 11,
        "card_event_sum": sum(int(row["events"]) for row in cards) == 381,
        "statement_event_sum": sum(int(row["events"]) for row in statements) == 381,
        "record_event_sum": sum(int(row["events"]) for row in records) == 381,
        "all_atoms_mapped": all(set(row["component_recipe"].split("+")) <= root_set for row in cards),
        "all_card_values_present": all(row["atomic_expansion_de"] and row["short_default_de"] for row in cards),
        "all_event_values_present": all(row["atomic_expansion_de"] and row["short_default_de"] for row in events),
        "all_statement_readings_present": all(row["complete_workshop_paraphrase_de"] for row in statements),
        "exact_three_whole_cards": {row["card_no"] for row in cards if row["composition_mode"] == "MEMORIZED_WHOLE_COMMAND"} == {"PROC005", "PROC034", "PROC043"},
        "no_placeholder_values": not any(term in (row["atomic_expansion_de"] + row["short_default_de"]) for row in cards for term in ["UNKNOWN", "EXEMPLAR", "FORMAL"]),
        "dy_root_is_licensed": next(row for row in roots if row["component"] == "DY")["category"] == "LICENSED_ENDPOINT",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
