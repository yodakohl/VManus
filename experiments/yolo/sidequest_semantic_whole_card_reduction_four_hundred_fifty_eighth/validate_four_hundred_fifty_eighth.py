#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("FOUR_HUNDRED_FIFTY_EIGHTH_381_EVENT_REVISED_EDITION.tsv")
    cards = read("FOUR_HUNDRED_FIFTY_EIGHTH_173_CARD_REVISED_DICTIONARY.tsv")
    statements = read("FOUR_HUNDRED_FIFTY_EIGHTH_116_STATEMENT_REVISED_EDITION.tsv")
    tournament = read("FOUR_HUNDRED_FIFTY_EIGHTH_TEN_WHOLE_CARD_TOURNAMENT.tsv")
    audit = read("FOUR_HUNDRED_FIFTY_EIGHTH_18_WHOLE_OCCURRENCE_AUDIT.tsv")
    wholes = read("FOUR_HUNDRED_FIFTY_EIGHTH_SIX_REMAINING_WHOLE_CARDS.tsv")
    aliases = read("FOUR_HUNDRED_FIFTY_EIGHTH_ELEVEN_ALIAS_FAMILIES.tsv")
    by_id = {row["joint_tuple_id"]: row for row in cards}
    checks = {
        "events_381": len(events) == 381,
        "event_order": [row["event_id"] for row in events] == [f"E{n:03d}" for n in range(1, 382)],
        "cards_173": len(cards) == 173 and len(by_id) == 173,
        "statements_116": len(statements) == 116,
        "tournament_10": len(tournament) == 10,
        "audit_18": len(audit) == 18,
        "promotions_4": sum(row["decision"] == "PROMOTE_COMPONENT" for row in tournament) == 4,
        "promoted_events_9": sum(row["decision"] == "PROMOTE_COMPONENT" for row in audit) == 9,
        "productive_cards_167": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in cards) == 167,
        "productive_events_372": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in events) == 372,
        "whole_cards_6": len(wholes) == 6,
        "whole_events_9": sum(row["lexicon_class"] == "MEMORIZED_WHOLE_CARD" for row in events) == 9,
        "aliases_11": len(aliases) == 11,
        "removed_values": not ({"dasselbe", "Tuch", "warm", "roh"} & {row["small_value_de"] for row in cards}),
        "event_dictionary_match": all(by_id[row["joint_tuple_id"]]["small_value_de"] == row["small_value_de"] and by_id[row["joint_tuple_id"]]["component_parse"] == row["component_parse"] for row in events),
        "statement_events_once": sorted((event for row in statements for event in row["event_ids"].split("|")), key=lambda item: int(item[1:])) == [f"E{n:03d}" for n in range(1, 382)],
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
