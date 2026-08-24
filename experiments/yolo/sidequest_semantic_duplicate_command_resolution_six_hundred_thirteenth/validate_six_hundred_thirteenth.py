#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    groups = read("SIX_HUNDRED_THIRTEENTH_11_DUPLICATE_GROUP_AUDIT.tsv")
    contexts = read("SIX_HUNDRED_THIRTEENTH_75_DUPLICATE_EVENT_CONTEXTS.tsv")
    words = read("SIX_HUNDRED_THIRTEENTH_39_WORD_PARADIGM.tsv")
    cards = read("SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv")
    events = read("SIX_HUNDRED_THIRTEENTH_381_REVISED_EVENT_COMMANDS.tsv")
    statements = read("SIX_HUNDRED_THIRTEENTH_116_REVISED_CASE_COMMANDS.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    command_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        command_groups[(row["semantic_component_parse"], row["standard_command_de"])].append(row)
    duplicates = [rows for rows in command_groups.values() if len(rows) > 1]
    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        statement_events[row["statement_id"]].append(row)
    checks = {
        "old_groups11": len(groups) == 11 and len({row["old_command_id"] for row in groups}) == 11,
        "contexts75": len(contexts) == 75 and len({row["event_id"] for row in contexts}) == 75,
        "two_splits": {row["split_card_ids"] for row in groups if row["split_card_ids"] != "NONE"} == {"PROC034", "PROC040"},
        "words39": len(words) == 39 and {row["canonical_component"] for row in words} >= {"AN", "RESUME_CARD"},
        "cards173": len(cards) == 173 and len(card_by_id) == 173,
        "commands163": len(command_groups) == 163,
        "remaining_duplicates10": len(duplicates) == 10 and sum(len(rows) - 1 for rows in duplicates) == 10,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "event_card_match": all(row["command_id"] == card_by_id[row["card_no"]]["command_id"] and row["standard_command_de"] == card_by_id[row["card_no"]]["standard_command_de"] for row in events),
        "resume_two": sum(row["standard_command_de"] == "WIEDERAUFNEHMEN" for row in events) == 2,
        "resume_first": all(row["position_in_statement"] == "FIRST" for row in contexts if row["card_no"] == "PROC034"),
        "portion_pair": [(row["card_no"], row["standard_command_de"]) for row in statement_events["H4-S001"]][2:4] == [("PROC039", "DIES · ZUFUEHREN · PORTION"), ("PROC040", "DIES · ZUFUEHREN · NACHPORTION")],
        "statements116": len(statements) == 116 and sum(int(row["event_count"]) for row in statements) == 381,
        "two_revised_statements": sum(row["semantic_revision"] == "YES" for row in statements) == 3,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
