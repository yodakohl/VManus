#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_THIRTY_THIRD"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_thirty_third.py")], check=True)
    components = read("39_COMPONENT_NINTH_GRAMMAR.tsv")
    cards = read("173_CARD_NINTH_DICTIONARY.tsv")
    events = read("381_EVENT_REPARSE.tsv")
    statements = read("116_STATEMENT_REPARSE.tsv")
    o_cards = read("18_O_CARDS.tsv")
    o_events = read("19_O_EVENTS.tsv")
    o_statements = read("17_O_STATEMENTS.tsv")
    exceptions = read("6_EXCEPTIONS.tsv")
    predictions = read("76_UNATTESTED_PREDICTIONS.tsv")
    active = read("30_ACTIVE_PREDICTION_SURFACES.tsv")
    rules = read("19_TEACHING_RULES.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    by_card = {row["exact_card_id"]: row for row in cards}
    card_counts = Counter(row["exact_card_id"] for row in events)
    statement_counts = Counter(row["statement_id"] for row in events)
    event_by_statement: dict[str, list[dict[str, str]]] = {}
    for row in statements:
        event_by_statement[row["statement_id"]] = [event for event in events if event["statement_id"] == row["statement_id"]]
    o_component = next(row for row in components if row["component"] == "O")
    expected_revisions = {"H2-S001", "H3-S001", "B1-S012"}

    checks = {
        "complete_inventory": len(components) == 39 and len(cards) == 173 and len(events) == 381 and len(statements) == 116,
        "unique_ids": len({row["exact_card_id"] for row in cards}) == 173 and len({row["event_id"] for row in events}) == 381 and len({row["statement_id"] for row in statements}) == 116,
        "counts_match": all(card_counts[row["exact_card_id"]] == int(row["events"]) for row in cards) and all(statement_counts[row["statement_id"]] == int(row["events"]) for row in statements),
        "event_dictionary_match": all(row["ninth_grammar_reading_de"] == by_card[row["exact_card_id"]]["ninth_grammar_reading_de"] for row in events),
        "statement_literals_match": all(row["ninth_grammar_literal_de"] == " | ".join(event["ninth_grammar_reading_de"] for event in event_by_statement[row["statement_id"]]) for row in statements),
        "o_value_workstep": o_component["short_value_de"] == "ARBEITSGANG" and o_component["exact_cards"] == "18" and o_component["events"] == "19",
        "o_scope_exact": len(o_cards) == 18 and len(o_events) == 19 and len(o_statements) == 17,
        "all_o_readings_changed": all("ARBEITSGANG" in row["new_reading_de"] and "VORGANG" not in row["new_reading_de"] for row in o_cards + o_events),
        "every_o_statement_has_workstep": all(int(row["arbeitsgang_tokens"]) > 0 and "arbeitsgang" in row["working_reading_de"].lower() for row in o_statements),
        "exact_three_fluent_revisions": {row["statement_id"] for row in o_statements if row["revision"] != "NONE"} == expected_revisions and summary["fluent_statement_revisions"] == 3,
        "exceptions_preserved": len(exceptions) == 6,
        "predictions_recomputed": len(predictions) == 76 and summary["changed_predictions"] > 0 and all(row["edition"] == "NINTH_GRAMMAR_RECOMPUTED" for row in predictions),
        "active_deck_preserved": len(active) == 30 and len({row["component_recipe"] for row in active}) == 24 and all(row["edition"] == "NINTH_GRAMMAR_RECOMPUTED" for row in active),
        "teaching_rule_updated": len(rules) == 19 and any(row["rule"] == "PATH_PLACE" and row["instruction"] == "CKH passage; O work step" for row in rules),
        "no_old_o_value": all("VORGANG" not in row["ninth_grammar_reading_de"] for row in cards + events) and all("VORGANG" not in row["ninth_grammar_literal_de"] for row in statements),
        "allowed_pages": {row["page"] for row in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
