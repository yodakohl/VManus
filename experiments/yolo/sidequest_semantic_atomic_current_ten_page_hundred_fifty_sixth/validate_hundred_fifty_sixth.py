#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_FIFTY_SIXTH_173_ATOMIC_DICTIONARY.tsv")
    surfaces = rows("HUNDRED_FIFTY_SIXTH_230_SURFACE_READER.tsv")
    events = rows("HUNDRED_FIFTY_SIXTH_381_ATOMIC_EVENTS.tsv")
    clauses = rows("HUNDRED_FIFTY_SIXTH_116_ATOMIC_CLAUSES.tsv")
    records = rows("HUNDRED_FIFTY_SIXTH_ELEVEN_ATOMIC_RECORDS.tsv")
    astro = rows("HUNDRED_FIFTY_SIXTH_395_ASTRO_OWNER_MENU.tsv")
    unified = rows("HUNDRED_FIFTY_SIXTH_776_ATOMIC_LEDGER.tsv")
    jobs = rows("HUNDRED_FIFTY_SIXTH_FOUR_OPTIONAL_JOBS.tsv")
    card_by_id = {row["master_card_id"]: row for row in cards}
    checks = {
        "cards_173": len(cards) == 173,
        "surfaces_230": len(surfaces) == 230,
        "shared_cards_47": sum(row["portable_scope"].startswith("ACTIVE") for row in cards) == 47,
        "local_cards_126": sum(row["portable_scope"] == "LOCAL_LEARNED_WHOLE_CARD" for row in cards) == 126,
        "all_local_atomic": all(" · " not in row["portable_card_value_de"] for row in cards if row["portable_scope"] == "LOCAL_LEARNED_WHOLE_CARD"),
        "events_381": len(events) == 381,
        "shared_events_251": sum(row["teaching_layer"] == "SHARED_DECK" for row in events) == 251,
        "local_events_130": sum(row["teaching_layer"] == "ATOMIC_LOCAL_NOMENCLATOR" for row in events) == 130,
        "event_values_match": all(row["card_value_de"] == card_by_id[row["master_card_id"]]["portable_card_value_de"] for row in events),
        "clauses_116": len(clauses) == 116,
        "records_11": len(records) == 11,
        "record_events_381": sum(int(row["event_count"]) for row in records) == 381,
        "astro_395": len(astro) == 395,
        "unified_776": len(unified) == 776,
        "jobs_4": len(jobs) == 4,
        "ledger_layers": sum(row["reading_layer"] == "SHARED_DECK" for row in unified) == 251 and sum(row["reading_layer"] == "ATOMIC_LOCAL_NOMENCLATOR" for row in unified) == 130 and sum(row["reading_layer"] == "ASTRO_OWNER_LOCAL_MENU" for row in unified) == 395,
        "no_crosspage_keys": all(row["crosspage_key"] == "NONE" for row in unified),
        "no_empty_cells": all(all(v for v in row.values()) for table in (cards, surfaces, events, clauses, records, astro, unified, jobs) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
