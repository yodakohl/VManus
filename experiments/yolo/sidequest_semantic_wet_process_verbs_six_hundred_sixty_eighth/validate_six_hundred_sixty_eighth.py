#!/usr/bin/env python3
"""Validate the P/LSH/CFH wet-process set."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("SIX_HUNDRED_SIXTY_EIGHTH_6_WET_PROCESS_CARDS.tsv")
    events = read("SIX_HUNDRED_SIXTY_EIGHTH_7_WET_PROCESS_EVENTS.tsv")
    statements = read("SIX_HUNDRED_SIXTY_EIGHTH_5_COMPLETE_STATEMENTS.tsv")
    repairs = read("SIX_HUNDRED_SIXTY_EIGHTH_4_OVERREADING_REPAIRS.tsv")
    expected = {"P": (3, 3, "EINFUELLEN"), "LSH": (2, 3, "WASCHEN"), "CFH": (1, 1, "AUSWRINGEN")}
    checks = {
        "six_cards": len(cards) == 6,
        "seven_events": len(events) == 7,
        "five_statements": len(statements) == 5,
        "four_repairs": len(repairs) == 4,
        "three_roots": {row["root"] for row in cards} == set(expected),
        "root_counts": all(sum(row["root"] == root for row in cards) == values[0] and sum(row["root"] == root for row in events) == values[1] for root, values in expected.items()),
        "root_values_invariant": all(row["portable_root_value_de"] == expected[row["root"]][2] for row in cards),
        "all_target_events_unique": len({row["event_id"] for row in events}) == 7,
        "h3_chain_complete": any(row["statement_id"] == "H3-S001" and all(word in row["fluent_workshop_reading_de"] for word in ["auswringen", "Sollmass", "fuellen", "halten", "schliessen"]) for row in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
