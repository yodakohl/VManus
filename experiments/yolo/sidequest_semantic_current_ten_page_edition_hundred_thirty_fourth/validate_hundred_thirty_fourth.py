#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_THIRTY_FOURTH_173_CARD_DICTIONARY.tsv")
    surfaces = rows("HUNDRED_THIRTY_FOURTH_230_SURFACE_REVERSE_KEY.tsv")
    events = rows("HUNDRED_THIRTY_FOURTH_381_PROSE_EVENTS.tsv")
    statements = rows("HUNDRED_THIRTY_FOURTH_116_PROSE_STATEMENTS.tsv")
    astro = rows("HUNDRED_THIRTY_FOURTH_395_ASTRO_GROUPS.tsv")
    ledger = rows("HUNDRED_THIRTY_FOURTH_776_UNIFIED_LEDGER.tsv")
    jobs = rows("HUNDRED_THIRTY_FOURTH_FOUR_JOBS.tsv")
    card_by_id = {row["master_card_id"]: row for row in cards}
    checks = {
        "cards_173": len(cards) == 173,
        "surfaces_230": len(surfaces) == 230,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "astro_395": len(astro) == 395,
        "ledger_776": len(ledger) == 776,
        "jobs_4": len(jobs) == 4,
        "surface_values_match_cards": all(row["current_spoken_default_de"] == card_by_id[row["master_card_id"]]["current_spoken_default_de"] for row in surfaces),
        "event_values_match_cards": all(row["current_spoken_default_de"] == card_by_id[row["master_card_id"]]["current_spoken_default_de"] for row in events),
        "card_ids_unique": len(card_by_id) == 173,
        "surface_forms_unique": len({row["visible_surface"] for row in surfaces}) == 230,
        "event_serials_unique": len({row["event_serial"] for row in events}) == 381,
        "all_values_nonempty": all(row["current_spoken_default_de"] for row in cards),
        "no_empty_cells": all(all(value for value in row.values()) for table in (cards, surfaces, events, statements, astro, ledger, jobs) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
