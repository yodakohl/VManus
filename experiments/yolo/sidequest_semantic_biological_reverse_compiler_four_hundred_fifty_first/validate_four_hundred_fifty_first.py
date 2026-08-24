#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    dictionary = read("FOUR_HUNDRED_FIFTY_FIRST_124_CARD_DICTIONARY.tsv")
    events = read("FOUR_HUNDRED_FIFTY_FIRST_281_EVENT_EDITION.tsv")
    statements = read("FOUR_HUNDRED_FIFTY_FIRST_97_STATEMENT_EDITION.tsv")
    aliases = read("FOUR_HUNDRED_FIFTY_FIRST_FIVE_ALIAS_FAMILIES.tsv")
    trace = read("FOUR_HUNDRED_FIFTY_FIRST_281_REVERSE_TRACE.tsv")
    rules = read("FOUR_HUNDRED_FIFTY_FIRST_FIVE_REVERSE_RULES.tsv")
    checks = {
        "dictionary_124": len(dictionary) == 124,
        "events_281": len(events) == 281,
        "statements_97": len(statements) == 97,
        "aliases_5": len(aliases) == 5,
        "rules_5": len(rules) == 5,
        "trace_281": len(trace) == 281,
        "trace_event_order": [row["event_id"] for row in trace] == [f"E{n}" for n in range(101, 382)],
        "exact_recovery_281": all(row["exact_recovery"] == "PASS" and row["selected_joint_tuple_id"] == row["expected_joint_tuple_id"] for row in trace),
        "candidate_counts_positive": all(int(row["global_candidates"]) >= int(row["record_candidates"]) >= 1 for row in trace),
        "all_five_rules_used": {row["selection_rule"] for row in trace} == {row["rule"] for row in rules},
        "dictionary_event_agreement": all(next(card for card in dictionary if card["joint_tuple_id"] == row["joint_tuple_id"])["small_value_de"] == row["small_value_de"] for row in events),
        "statement_events_once": sorted((event_id for row in statements for event_id in row["event_ids"].split("|")), key=lambda event_id: int(event_id[1:])) == [f"E{n}" for n in range(101, 382)],
        "three_refined_values_present": {"dies kurz im Durchlass halten", "weiter hinausfuehren; Schluss", "absetzen; Schluss"} <= {row["small_value_de"] for row in events},
        "no_empty_values": all(row["small_value_de"].strip() for row in events),
        "fixed_pages_only": {row["page"] for row in events} == {"f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
