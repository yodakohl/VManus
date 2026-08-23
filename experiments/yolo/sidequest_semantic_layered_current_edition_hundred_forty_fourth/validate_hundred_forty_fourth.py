#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_FORTY_FOURTH_173_LAYERED_DICTIONARY.tsv")
    events = rows("HUNDRED_FORTY_FOURTH_381_LAYERED_EVENTS.tsv")
    statements = rows("HUNDRED_FORTY_FOURTH_116_LAYERED_STATEMENTS.tsv")
    moulds = rows("HUNDRED_FORTY_FOURTH_TEN_REVISED_MOULDS.tsv")
    owners = rows("HUNDRED_FORTY_FOURTH_ELEVEN_OWNER_REGISTERS.tsv")
    card_by_id = {r["master_card_id"]: r for r in cards}
    checks = {
        "cards_173": len(cards) == 173,
        "active_cards_41": sum(r["portable_scope"] == "ACTIVE_CROSS_RECORD" for r in cards) == 41,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "moulds_10": len(moulds) == 10,
        "owners_11": len(owners) == 11,
        "event_values_match": all(r["portable_card_value_de"] == card_by_id[r["master_card_id"]]["portable_card_value_de"] for r in events),
        "owner_terms_not_portable": all(r["owner_terms_are_portable"] == "NO" for r in statements),
        "all_cards_scoped": all(r["owner_argument_policy"] and r["fluent_do_not_auto_add"] for r in cards),
        "no_empty_cells": all(all(v for v in r.values()) for table in (cards, events, statements, moulds, owners) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
