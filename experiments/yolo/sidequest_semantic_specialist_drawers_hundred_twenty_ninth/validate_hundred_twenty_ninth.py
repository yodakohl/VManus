#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    specialist = rows("HUNDRED_TWENTY_NINTH_132_SPECIALIST_CARDS.tsv")
    drawers = rows("HUNDRED_TWENTY_NINTH_EIGHT_SPECIALIST_DRAWERS.tsv")
    cards = rows("HUNDRED_TWENTY_NINTH_COMPLETE_173_CARD_DICTIONARY.tsv")
    events = rows("HUNDRED_TWENTY_NINTH_COMPLETE_381_EVENT_DICTIONARY.tsv")
    statements = rows("HUNDRED_TWENTY_NINTH_COMPLETE_116_CARD_CHAINS.tsv")
    checks = {
        "specialist_cards_132": len(specialist) == 132,
        "drawers_8": len(drawers) == 8,
        "cards_173": len(cards) == 173,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "specialist_events_142": sum(int(row["event_count"]) for row in specialist) == 142,
        "drawer_card_sum": sum(int(row["card_types"]) for row in drawers) == 132,
        "drawer_event_sum": sum(int(row["events"]) for row in drawers) == 142,
        "card_ids_unique": len({row["master_card_id"] for row in cards}) == 173,
        "event_serials_unique": len({row["event_serial"] for row in events}) == 381,
        "no_plus_in_spoken_specialist_values": all("+" not in row["spoken_whole_card_value_de"] for row in specialist),
        "no_empty_cells": all(all(value for value in row.values()) for table in (specialist, drawers, cards, events, statements) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
