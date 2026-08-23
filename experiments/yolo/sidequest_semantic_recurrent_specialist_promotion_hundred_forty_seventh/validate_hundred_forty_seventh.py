#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    audit = rows("HUNDRED_FORTY_SEVENTH_132_RECURRENCE_AUDIT.tsv")
    cards = rows("HUNDRED_FORTY_SEVENTH_173_PROMOTED_DICTIONARY.tsv")
    events = rows("HUNDRED_FORTY_SEVENTH_381_PROMOTED_EVENTS.tsv")
    statements = rows("HUNDRED_FORTY_SEVENTH_116_PROMOTED_STATEMENTS.tsv")
    card_by_id = {row["master_card_id"]: row for row in cards}
    checks = {
        "audit_132": len(audit) == 132,
        "cards_173": len(cards) == 173,
        "active_47": sum(row["portable_scope"].startswith("ACTIVE") for row in cards) == 47,
        "promoted_6": sum(row["decision"] == "PROMOTE_TO_BIO_SHARED_DECK" for row in audit) == 6,
        "promoted_events_12": sum(int(row["event_count"]) for row in audit if row["decision"] == "PROMOTE_TO_BIO_SHARED_DECK") == 12,
        "singletons_122": sum(row["portability_class"] == "SINGLETON_NOMENCLATOR" for row in audit) == 122,
        "within_record_4": sum(row["portability_class"] == "REPEATED_ONE_RECORD" for row in audit) == 4,
        "cross_record_6": sum(row["portability_class"] == "CROSS_RECORD_SAME_SECTION" for row in audit) == 6,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "event_values_match": all(row["portable_card_value_de"] == card_by_id[row["master_card_id"]]["portable_card_value_de"] for row in events),
        "all_concrete": all(row["portable_card_value_de"] for row in cards),
        "no_empty_cells": all(all(v for v in row.values()) for table in (audit, cards, events, statements) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
