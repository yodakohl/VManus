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
    subprocess.run(["python", str(HERE / "build_eight_hundred_twenty_seventh.py")], check=True)
    components = read("EIGHT_HUNDRED_TWENTY_SEVENTH_39_COMPONENT_SEVENTH_GRAMMAR.tsv")
    cards = read("EIGHT_HUNDRED_TWENTY_SEVENTH_173_CARD_SEVENTH_DICTIONARY.tsv")
    events = read("EIGHT_HUNDRED_TWENTY_SEVENTH_381_EVENT_REPARSE.tsv")
    statements = read("EIGHT_HUNDRED_TWENTY_SEVENTH_116_STATEMENT_REPARSE.tsv")
    changed = read("EIGHT_HUNDRED_TWENTY_SEVENTH_17_CHANGED_CARDS.tsv")
    exceptions = read("EIGHT_HUNDRED_TWENTY_SEVENTH_6_EXCEPTIONS.tsv")
    predictions = read("EIGHT_HUNDRED_TWENTY_SEVENTH_76_UNATTESTED_PREDICTIONS.tsv")
    rules = read("EIGHT_HUNDRED_TWENTY_SEVENTH_19_TEACHING_RULES.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_card = {row["exact_card_id"]: row for row in cards}
    component_values = {row["component"]: row["short_value_de"] for row in components}
    card_counts = Counter(row["exact_card_id"] for row in events)
    statement_counts = Counter(row["statement_id"] for row in events)
    checks = {
        "complete_inventory": len(components) == 39 and len(cards) == 173 and len(events) == 381 and len(statements) == 116,
        "unique_ids": len({row["exact_card_id"] for row in cards}) == 173 and len({row["event_id"] for row in events}) == 381 and len({row["statement_id"] for row in statements}) == 116,
        "counts_match": all(card_counts[row["exact_card_id"]] == int(row["events"]) for row in cards) and all(statement_counts[row["statement_id"]] == int(row["events"]) for row in statements),
        "event_dictionary_match": all(row["seventh_grammar_reading_de"] == by_card[row["exact_card_id"]]["seventh_grammar_reading_de"] for row in events),
        "three_values_revised": {key: component_values[key] for key in ("T", "P", "SOLK")} == {"T": "BEARBEITEN", "P": "EINBRINGEN", "SOLK": "SAMMELN"},
        "delta_counts": len(changed) == 17 and summary["changed_events"] == 20 and summary["changed_statements"] == 16,
        "working_readings_current": sum("bearbeit" in row["working_reading_de"].lower() for row in statements) >= 7 and sum("einbring" in row["working_reading_de"].lower() for row in statements) == 3 and sum("sammel" in row["working_reading_de"].lower() for row in statements) == 7,
        "exceptions_preserved": len(exceptions) == 6 and all(row["short_value_de"] not in {"", "NONE", "UNKNOWN"} for row in exceptions),
        "predictions_recomputed": len(predictions) == 76 and summary["changed_predictions"] > 0 and all(row["edition"] == "SEVENTH_GRAMMAR_RECOMPUTED" for row in predictions),
        "teaching_rules_updated": len(rules) == 19 and any("T work" in row["instruction"] for row in rules) and any("P bring inward" in row["instruction"] for row in rules) and any("SOLK collect" in row["instruction"] for row in rules),
        "allowed_pages": {row["page"] for row in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
