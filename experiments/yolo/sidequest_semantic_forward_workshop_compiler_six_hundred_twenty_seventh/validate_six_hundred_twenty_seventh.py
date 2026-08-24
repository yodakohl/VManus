#!/usr/bin/env python3
"""Validate forward compilation through commands, cards, and surfaces."""

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
    events = read("SIX_HUNDRED_TWENTY_SEVENTH_372_FORWARD_EVENT_COMPILATION.tsv")
    statements = read("SIX_HUNDRED_TWENTY_SEVENTH_115_FORWARD_STATEMENT_COMPILATION.tsv")
    exemplar = read("SIX_HUNDRED_TWENTY_SEVENTH_179_SURFACE_EXEMPLAR_CHOICES.tsv")
    rules = read("SIX_HUNDRED_TWENTY_SEVENTH_10_CARD_CHOICE_RULES.tsv")
    card_modes = Counter(row["card_selection_mode"] for row in events)
    surface_modes = Counter(row["surface_selection_mode"] for row in events)
    checks = {
        "events372": len(events) == 372 and len({row["event_id"] for row in events}) == 372,
        "statements115": len(statements) == 115 and len({row["statement_id"] for row in statements}) == 115,
        "ten_card_rules": len(rules) == 10 and len({row["semantic_component_parse"] for row in rules}) == 10,
        "cards_match_observed": all(row["selected_card_no"] == row["observed_card_no"] for row in events),
        "event_surface_roundtrip": all(row["surface_roundtrip"] == "YES" for row in events),
        "statement_surface_roundtrip": all(row["exact_roundtrip"] == "YES" for row in statements),
        "card_mode_counts": card_modes == {"UNIQUE_COMMAND_TO_CARD": 303, "CONTEXT_RULE_TO_CARD": 69},
        "surface_mode_counts": surface_modes == {"UNIQUE_CARD_SURFACE": 174, "DESK_RULE_UNIQUE": 19, "LOCAL_EXEMPLAR_REQUIRED": 179},
        "exemplar179": len(exemplar) == 179 and {row["event_id"] for row in exemplar} == {row["event_id"] for row in events if row["local_exemplar_needed"] == "YES"},
        "all_selected_surfaces_are_candidates": all(row["selected_surface"] in row["desk_surface_candidates"].split("|") for row in events),
        "five_cases": {row["case_id"] for row in events} == {f"C{i}" for i in range(1, 6)},
        "no_c6": not any(row["case_id"] == "C6" for row in events),
        "no_sealed_pages": not any(row["page"].startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
