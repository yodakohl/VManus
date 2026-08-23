#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    audit = rows("HUNDRED_FIFTY_FOURTH_45_HERBAL_ATOMIC_CARDS.tsv")
    cards = rows("HUNDRED_FIFTY_FOURTH_173_REVISED_DICTIONARY.tsv")
    events = rows("HUNDRED_FIFTY_FOURTH_381_REVISED_EVENTS.tsv")
    clauses = rows("HUNDRED_FIFTY_FOURTH_19_ATOMIC_HERBAL_CLAUSES.tsv")
    records = rows("HUNDRED_FIFTY_FOURTH_FIVE_ATOMIC_HERBAL_RECORDS.tsv")
    card_by_id = {row["master_card_id"]: row for row in cards}
    checks = {
        "atomic_cards_45": len(audit) == 45,
        "cards_173": len(cards) == 173,
        "events_381": len(events) == 381,
        "herbal_clauses_19": len(clauses) == 19,
        "herbal_records_5": len(records) == 5,
        "all_old_composites_removed": all(" · " not in row["atomic_whole_card_default_de"] for row in audit),
        "all_memorized_as_whole": all(row["teaching_rule"] == "MEMORIZE_AS_ONE_HERBAL_CARD__DO_NOT_DECOMPOSE" for row in audit),
        "event_values_match": all(row["portable_card_value_de"] == card_by_id[row["master_card_id"]]["portable_card_value_de"] for row in events),
        "record_statement_total": sum(int(row["statement_count"]) for row in records) == 19,
        "all_concrete": all(row["portable_card_value_de"] for row in cards),
        "no_empty_cells": all(all(v for v in row.values()) for table in (audit, cards, events, clauses, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
