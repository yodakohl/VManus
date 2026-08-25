#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirty_first.py")], check=True)
    components = read("EIGHT_HUNDRED_THIRTY_FIRST_39_COMPONENT_EIGHTH_GRAMMAR.tsv")
    cards = read("EIGHT_HUNDRED_THIRTY_FIRST_173_CARD_EIGHTH_DICTIONARY.tsv")
    events = read("EIGHT_HUNDRED_THIRTY_FIRST_381_EVENT_REPARSE.tsv")
    statements = read("EIGHT_HUNDRED_THIRTY_FIRST_116_STATEMENT_REPARSE.tsv")
    y_cards = read("EIGHT_HUNDRED_THIRTY_FIRST_60_Y_CARDS.tsv")
    y_events = read("EIGHT_HUNDRED_THIRTY_FIRST_124_Y_EVENTS.tsv")
    y_statements = read("EIGHT_HUNDRED_THIRTY_FIRST_60_Y_STATEMENTS.tsv")
    exceptions = read("EIGHT_HUNDRED_THIRTY_FIRST_6_EXCEPTIONS.tsv")
    predictions = read("EIGHT_HUNDRED_THIRTY_FIRST_76_UNATTESTED_PREDICTIONS.tsv")
    active = read("EIGHT_HUNDRED_THIRTY_FIRST_30_ACTIVE_PREDICTION_SURFACES.tsv")
    rules = read("EIGHT_HUNDRED_THIRTY_FIRST_19_TEACHING_RULES.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_THIRTY_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_card = {row["exact_card_id"]: row for row in cards}
    card_counts = Counter(row["exact_card_id"] for row in events)
    statement_counts = Counter(row["statement_id"] for row in events)
    checks = {
        "complete_inventory": len(components) == 39 and len(cards) == 173 and len(events) == 381 and len(statements) == 116,
        "unique_ids": len({row["exact_card_id"] for row in cards}) == 173 and len({row["event_id"] for row in events}) == 381 and len({row["statement_id"] for row in statements}) == 116,
        "counts_match": all(card_counts[row["exact_card_id"]] == int(row["events"]) for row in cards) and all(statement_counts[row["statement_id"]] == int(row["events"]) for row in statements),
        "event_dictionary_match": all(row["eighth_grammar_reading_de"] == by_card[row["exact_card_id"]]["eighth_grammar_reading_de"] for row in events),
        "y_value_posten": next(row for row in components if row["component"] == "Y")["short_value_de"] == "POSTEN",
        "y_scope_exact": len(y_cards) == 60 and len(y_events) == 124 and len(y_statements) == 60 and next(row for row in components if row["component"] == "Y")["exact_cards"] == "60" and next(row for row in components if row["component"] == "Y")["events"] == "124",
        "every_y_statement_has_posten": all(int(row["posten_tokens"]) > 0 for row in y_statements) and summary["fluent_statement_revisions"] == 1,
        "all_y_literals_changed": all("POSTEN" in row["new_reading_de"] and "DIES" not in row["new_reading_de"] for row in y_cards + y_events),
        "exceptions_preserved": len(exceptions) == 6,
        "predictions_recomputed": len(predictions) == 76 and summary["changed_predictions"] > 0 and all(row["edition"] == "EIGHTH_GRAMMAR_RECOMPUTED" for row in predictions),
        "active_deck_preserved": len(active) == 30 and len({row["component_recipe"] for row in active}) == 24,
        "teaching_rule_updated": len(rules) == 19 and any("POSTEN" in row["instruction"] for row in rules),
        "allowed_pages": {row["page"] for row in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_THIRTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
