#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_SIXTY_FOURTH_173_ATOMIC_DICTIONARY.tsv")
    surfaces = rows("HUNDRED_SIXTY_FOURTH_230_SURFACE_READER.tsv")
    events = rows("HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv")
    clauses = rows("HUNDRED_SIXTY_FOURTH_116_ATOMIC_CLAUSES.tsv")
    records = rows("HUNDRED_SIXTY_FOURTH_11_ATOMIC_RECORDS.tsv")
    astro = rows("HUNDRED_SIXTY_FOURTH_395_ASTRO_OWNER_MENU.tsv")
    ledger = rows("HUNDRED_SIXTY_FOURTH_776_ATOMIC_LEDGER.tsv")
    pressure = rows("HUNDRED_SIXTY_FOURTH_90_CLAUSE_PROCESS_PRESSURE.tsv")
    revision = rows("HUNDRED_SIXTY_FOURTH_1_CARD_REVISION.tsv")
    checks = {
        "cards_173": len(cards) == 173,
        "surfaces_230": len(surfaces) == 230,
        "events_381": len(events) == 381,
        "clauses_116": len(clauses) == 116,
        "records_11": len(records) == 11,
        "astro_395": len(astro) == 395,
        "ledger_776": len(ledger) == 776,
        "pressure_90": len(pressure) == 90,
        "compatible_76": sum(row["pressure_status"] == "KEEP_PROCESS_COMPATIBLE" for row in pressure) == 76,
        "owner_unresolved_11": sum(row["pressure_status"] == "KEEP_PROCESS_VALUE_OWNER_UNRESOLVED" for row in pressure) == 11,
        "revised_clauses_3": sum(row["pressure_status"] == "REVISED_OVERLITERAL_FILTER_TO_TECHNICAL_PASSAGE" for row in pressure) == 3,
        "one_card_revision": len(revision) == 1 and revision[0]["master_card_id"] == "MC143",
        "three_revised_events": sum(row["master_card_id"] == "MC143" for row in events) == 3,
        "new_value_everywhere": all(row["card_value_de"] == "durchlassen; Schluss" for row in events if row["master_card_id"] == "MC143"),
        "old_value_absent_tables": all("seihen; Schluss" not in value for table in (cards, surfaces, events, clauses, records, ledger) for row in table for value in row.values()),
        "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "no_empty_cells": all(all(value for value in row.values()) for table in (cards, surfaces, events, clauses, records, astro, ledger, pressure, revision) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
