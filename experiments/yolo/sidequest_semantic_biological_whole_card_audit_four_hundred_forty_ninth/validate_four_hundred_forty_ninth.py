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
    dictionary = read("FOUR_HUNDRED_FORTY_NINTH_124_CARD_DICTIONARY.tsv")
    events = read("FOUR_HUNDRED_FORTY_NINTH_281_EVENT_EDITION.tsv")
    statements = read("FOUR_HUNDRED_FORTY_NINTH_97_STATEMENT_EDITION.tsv")
    promotions = read("FOUR_HUNDRED_FORTY_NINTH_SEVEN_PROMOTIONS.tsv")
    residual = read("FOUR_HUNDRED_FORTY_NINTH_SIX_WHOLE_CARDS.tsv")
    paradigms = read("FOUR_HUNDRED_FORTY_NINTH_THREE_CLOSING_PARADIGMS.tsv")
    checks = {
        "dictionary_124": len(dictionary) == 124,
        "events_281": len(events) == 281,
        "statements_97": len(statements) == 97,
        "promotions_7": len(promotions) == 7,
        "residual_6": len(residual) == 6,
        "paradigms_3": len(paradigms) == 3,
        "drawers_118_3_3": [sum(row["union_drawer"] == drawer for row in dictionary) for drawer in ("PRODUCTIVE_COMPOSITION", "PORTABLE_LEARNED_WHOLE_CARD", "RECORD_LOCAL_LEARNED_WHOLE_CARD")] == [118, 3, 3],
        "productive_events_270": sum(row["union_drawer"] == "PRODUCTIVE_COMPOSITION" for row in events) == 270,
        "whole_events_11": sum(row["union_drawer"] != "PRODUCTIVE_COMPOSITION" for row in events) == 11,
        "dictionary_event_agreement": all(next(card for card in dictionary if card["joint_tuple_id"] == row["joint_tuple_id"])["small_value_de"] == row["small_value_de"] for row in events),
        "all_events_once": [row["event_id"] for row in events] == [f"E{n}" for n in range(101, 382)],
        "statement_events_once": sorted((event_id for row in statements for event_id in row["event_ids"].split("|")), key=lambda event_id: int(event_id[1:])) == [f"E{n}" for n in range(101, 382)],
        "no_empty_values": all(row["small_value_de"].strip() for row in events),
        "fixed_pages_only": {row["page"] for row in events} == {"f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
