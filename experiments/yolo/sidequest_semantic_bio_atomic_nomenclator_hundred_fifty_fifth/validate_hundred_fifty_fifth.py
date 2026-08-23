#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    audit = rows("HUNDRED_FIFTY_FIFTH_81_BIO_ATOMIC_CARDS.tsv")
    cards = rows("HUNDRED_FIFTY_FIFTH_173_COMPLETE_ATOMIC_DICTIONARY.tsv")
    events = rows("HUNDRED_FIFTY_FIFTH_381_COMPLETE_ATOMIC_EVENTS.tsv")
    clauses = rows("HUNDRED_FIFTY_FIFTH_97_ATOMIC_BIO_CLAUSES.tsv")
    records = rows("HUNDRED_FIFTY_FIFTH_SIX_ATOMIC_BIO_RECORDS.tsv")
    card_by_id = {row["master_card_id"]: row for row in cards}
    local = [row for row in cards if row["portable_scope"] == "LOCAL_LEARNED_WHOLE_CARD"]
    checks = {
        "atomic_bio_cards_81": len(audit) == 81,
        "cards_173": len(cards) == 173,
        "local_atomic_126": len(local) == 126,
        "active_47": sum(row["portable_scope"].startswith("ACTIVE") for row in cards) == 47,
        "events_381": len(events) == 381,
        "bio_clauses_97": len(clauses) == 97,
        "bio_records_6": len(records) == 6,
        "all_new_bio_composites_removed": all(" · " not in row["atomic_whole_card_default_de"] for row in audit),
        "all_local_composites_removed": all(" · " not in row["portable_card_value_de"] for row in local),
        "all_memorized_as_whole": all(row["teaching_rule"] == "MEMORIZE_AS_ONE_BIO_CARD__DO_NOT_DECOMPOSE" for row in audit),
        "event_values_match": all(row["portable_card_value_de"] == card_by_id[row["master_card_id"]]["portable_card_value_de"] for row in events),
        "record_statement_total": sum(int(row["statement_count"]) for row in records) == 97,
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
