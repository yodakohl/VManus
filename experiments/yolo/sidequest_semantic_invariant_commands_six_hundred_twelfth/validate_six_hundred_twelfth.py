#!/usr/bin/env python3
"""Validate invariant command substitution across all cases."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    commands = read("SIX_HUNDRED_TWELFTH_161_STANDARD_COMMANDS.tsv")
    cards = read("SIX_HUNDRED_TWELFTH_173_CARD_COMMAND_MAP.tsv")
    events = read("SIX_HUNDRED_TWELFTH_381_INVARIANT_EVENT_COMMANDS.tsv")
    statements = read("SIX_HUNDRED_TWELFTH_116_CASE_COMMAND_SEQUENCES.tsv")
    command_by_id = {row["command_id"]: row for row in commands}
    card_by_id = {row["card_no"]: row for row in cards}
    checks = {
        "commands161": len(commands) == 161 and len(command_by_id) == 161,
        "cards173": len(cards) == 173 and len(card_by_id) == 173,
        "cards_sum_to_commands": sum(int(row["card_types"]) for row in commands) == 173,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "event_command_matches_card": all(row["command_id"] == card_by_id[row["card_no"]]["command_id"] and row["standard_command_de"] == card_by_id[row["card_no"]]["standard_command_de"] for row in events),
        "same_parse_same_command": all(len({row["standard_command_de"] for row in events if row["semantic_component_parse"] == parse}) == 1 for parse in {row["semantic_component_parse"] for row in events}),
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "statement_events381": sum(int(row["event_count"]) for row in statements) == 381,
        "six_cases": {row["case_id"] for row in statements} == {f"C{i}" for i in range(1, 7)},
        "all_meaning_invariant": all(row["meaning_invariant_across_occurrences"] == "YES" for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWELFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
