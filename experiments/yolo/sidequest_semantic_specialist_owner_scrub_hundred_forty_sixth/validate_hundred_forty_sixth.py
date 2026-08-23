#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    audit = rows("HUNDRED_FORTY_SIXTH_132_SPECIALIST_AUDIT.tsv")
    cards = rows("HUNDRED_FORTY_SIXTH_173_SHORT_DICTIONARY.tsv")
    events = rows("HUNDRED_FORTY_SIXTH_381_SHORT_EVENTS.tsv")
    statements = rows("HUNDRED_FORTY_SIXTH_116_SHORT_STATEMENTS.tsv")
    card_by_id = {row["master_card_id"]: row for row in cards}
    forbidden = re.compile(r"Wurzel|Zutat|Gefäß|Tuch|Flüssigkeitslauf|Zielstelle|Ausgang|Durchgang|Ansatz")
    specialist = [row for row in cards if row["portable_scope"] == "LOCAL_LEARNED_WHOLE_CARD"]
    checks = {
        "audit_132": len(audit) == 132,
        "cards_173": len(cards) == 173,
        "specialists_132": len(specialist) == 132,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "changed_52": sum(row["old_value_de"] != row["short_value_de"] for row in audit) == 52,
        "changed_events_54": sum(int(row["event_count"]) for row in audit if row["old_value_de"] != row["short_value_de"]) == 54,
        "owner_nouns_removed_from_specialists": all(not forbidden.search(row["portable_card_value_de"]) for row in specialist),
        "specialist_values_max_three_words": all(len(re.findall(r"[A-Za-zÄÖÜäöüß]+", row["portable_card_value_de"])) <= 3 for row in specialist),
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
