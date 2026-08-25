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
    subprocess.run(["python", str(HERE / "build_eight_hundred_nineteenth.py")], check=True)
    components = read("EIGHT_HUNDRED_NINETEENTH_39_COMPONENT_SIXTH_GRAMMAR.tsv")
    cards = read("EIGHT_HUNDRED_NINETEENTH_173_CARD_SIXTH_DICTIONARY.tsv")
    events = read("EIGHT_HUNDRED_NINETEENTH_381_EVENT_REPARSE.tsv")
    statements = read("EIGHT_HUNDRED_NINETEENTH_116_STATEMENT_REPARSE.tsv")
    exceptions = read("EIGHT_HUNDRED_NINETEENTH_6_EXCEPTIONS.tsv")
    predictions = read("EIGHT_HUNDRED_NINETEENTH_76_UNATTESTED_PREDICTIONS.tsv")
    rules = read("EIGHT_HUNDRED_NINETEENTH_19_TEACHING_RULES.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_NINETEENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_card = {row["exact_card_id"]: row for row in cards}
    event_counts = Counter(row["exact_card_id"] for row in events)
    statement_event_counts = Counter(row["statement_id"] for row in events)
    whole = {row["component"]: row["short_value_de"] for row in components if row["component"] in {"OS", "RESUME_CARD", "TALAM"}}
    checks = {
        "inventory_39_173_381_116": len(components) == 39 and len(cards) == 173 and len(events) == 381 and len(statements) == 116,
        "unique_primary_ids": len({row["exact_card_id"] for row in cards}) == 173 and len({row["event_id"] for row in events}) == 381 and len({row["statement_id"] for row in statements}) == 116,
        "card_event_counts": all(event_counts[row["exact_card_id"]] == int(row["events"]) for row in cards),
        "statement_event_counts": all(statement_event_counts[row["statement_id"]] == int(row["events"]) for row in statements),
        "event_dictionary_match": all(row["sixth_grammar_reading_de"] == by_card[row["exact_card_id"]]["sixth_grammar_reading_de"] for row in events),
        "whole_values_exact": whole == {"OS": "DAZU", "RESUME_CARD": "DAVON", "TALAM": "BEISEITESTELLEN"},
        "revised_statements_present": any("dazu Wasser entnehmen" in row["working_reading_de"] for row in statements) and sum("Davon" in row["working_reading_de"] for row in statements) == 2 and any("beiseitestellen" in row["working_reading_de"] for row in statements),
        "exception_inventory_6_7": len(exceptions) == 6 and sum(int(row["events"]) for row in exceptions) == 7,
        "exception_values_complete": all(row["short_value_de"] and row["short_value_de"] not in {"UNKNOWN", "NONE"} for row in exceptions),
        "core_coverage_unchanged": summary["core_components"] == 33 and summary["core_touch_cards"] == 170 and summary["core_touch_events"] == 377 and summary["fully_core_cards"] == 167 and summary["fully_core_events"] == 374,
        "predictions_76_no_collision": len(predictions) == 76 and all(row["attested_on_fixed_pages"] == "NO" for row in predictions),
        "teaching_rules_19": len(rules) == 19,
        "allowed_pages_only": {row["page"] for row in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_NINETEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
