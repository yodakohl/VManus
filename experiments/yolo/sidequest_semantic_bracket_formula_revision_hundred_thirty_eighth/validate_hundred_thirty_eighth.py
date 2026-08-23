#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_THIRTY_EIGHTH_173_FORMULA_REVISED_DICTIONARY.tsv")
    events = rows("HUNDRED_THIRTY_EIGHTH_381_FORMULA_REVISED_EVENTS.tsv")
    statements = rows("HUNDRED_THIRTY_EIGHTH_116_FORMULA_STATEMENTS.tsv")
    formulae = rows("HUNDRED_THIRTY_EIGHTH_FIVE_FORMULA_OCCURRENCES.tsv")
    records = rows("HUNDRED_THIRTY_EIGHTH_11_REVISED_RECORDS.tsv")
    counts = Counter(r["formula_id"] for r in formulae)
    checks = {
        "cards_173": len(cards) == 173,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "records_11": len(records) == 11,
        "formula_occurrences_5": len(formulae) == 5,
        "formula_counts_3_and_2": counts == {"F1_PAIRED_MEASURE": 3, "F2_CARRIED_PREPARATION": 2},
        "cholor_two_events": sum(r["master_card_id"] == "MC157" and r["current_spoken_default_de"] == "derselbe Ansatz" for r in events) == 2,
        "formula_statement_ids": {r["statement_id"] for r in formulae} == {"H2-S001", "H2-S002", "B1-S002", "B3-S003", "B3-S021"},
        "no_empty_cells": all(all(v for v in r.values()) for table in (cards, events, statements, formulae, records) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
