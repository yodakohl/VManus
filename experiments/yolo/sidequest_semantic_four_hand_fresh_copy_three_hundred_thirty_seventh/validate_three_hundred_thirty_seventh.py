#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


events = rows("THREE_HUNDRED_THIRTY_SEVENTH_64_RENDERED_EVENTS.tsv")
passages = rows("THREE_HUNDRED_THIRTY_SEVENTH_EIGHT_SCRIBE_PASSAGES.tsv")
rules = rows("THREE_HUNDRED_THIRTY_SEVENTH_FOUR_HAND_RULES.tsv")
checks = {
    "four_hands": len(rules) == 4 and len({row["hand_id"] for row in rules}) == 4,
    "sixty_four_events": len(events) == 64,
    "sixteen_per_hand": all(sum(row["hand_id"] == hand["hand_id"] for row in events) == 16 for hand in rules),
    "eight_passages": len(passages) == 8,
    "all_registered": all(row["surface_registered_for_identity"] == "YES" for row in events),
    "all_identities_preserved": all(row["identity_preserved_by_registered_palette"] == "YES" for row in events),
    "all_slots_preserved": all(row["slot_sequence_preserved"] == "YES" for row in passages),
    "all_cycles_preserved": all(row["microcycle_sequence_preserved"] == "YES" for row in passages),
    "all_meanings_preserved": all(row["meaning_sequence_preserved"] == "YES" for row in passages),
    "all_cross_line": all(row["logical_statement_crosses_line"] == "YES" for row in passages),
    "eight_distinct_copies": len({(row["line_1"], row["line_2"]) for row in passages}) == 8,
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_THIRTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
