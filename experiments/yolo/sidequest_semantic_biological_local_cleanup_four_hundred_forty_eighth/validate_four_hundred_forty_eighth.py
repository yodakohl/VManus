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
    dictionary = read("FOUR_HUNDRED_FORTY_EIGHTH_124_CARD_DICTIONARY.tsv")
    events = read("FOUR_HUNDRED_FORTY_EIGHTH_281_EVENT_EDITION.tsv")
    statements = read("FOUR_HUNDRED_FORTY_EIGHTH_97_STATEMENT_EDITION.tsv")
    promoted = read("FOUR_HUNDRED_FORTY_EIGHTH_24_PROMOTED_COMPOSITIONS.tsv")
    wholes = read("FOUR_HUNDRED_FORTY_EIGHTH_SEVEN_LOCAL_WHOLE_CARDS.tsv")
    roots = read("FOUR_HUNDRED_FORTY_EIGHTH_LOCAL_ROOT_CARD.tsv")
    checks = {
        "dictionary_124": len(dictionary) == 124,
        "events_281": len(events) == 281,
        "statements_97": len(statements) == 97,
        "promoted_24": len(promoted) == 24,
        "wholes_7": len(wholes) == 7,
        "roots_10": len(roots) == 10,
        "drawers_111_6_7": [sum(row["union_drawer"] == drawer for row in dictionary) for drawer in ("PRODUCTIVE_COMPOSITION", "PORTABLE_LEARNED_WHOLE_CARD", "RECORD_LOCAL_LEARNED_WHOLE_CARD")] == [111, 6, 7],
        "event_drawers_254_20_7": [sum(row["union_drawer"] == drawer for row in events) for drawer in ("PRODUCTIVE_COMPOSITION", "PORTABLE_LEARNED_WHOLE_CARD", "RECORD_LOCAL_LEARNED_WHOLE_CARD")] == [254, 20, 7],
        "dictionary_event_agreement": all(next(card for card in dictionary if card["joint_tuple_id"] == row["joint_tuple_id"])["small_value_de"] == row["small_value_de"] for row in events),
        "all_events_once": [row["event_id"] for row in events] == [f"E{n}" for n in range(101, 382)],
        "statement_events_once": sorted((event_id for row in statements for event_id in row["event_ids"].split("|")), key=lambda event_id: int(event_id[1:])) == [f"E{n}" for n in range(101, 382)],
        "stale_opening_removed": all("Oeffnung" not in row["small_value_de"] for row in events),
        "stale_water_compounds_removed": all(value not in {row["small_value_de"] for row in events} for value in ("Frischwasser; Schluss", "Spuelwasser")),
        "no_empty_values": all(row["small_value_de"].strip() for row in events),
        "fixed_pages_only": {row["page"] for row in events} == {"f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
