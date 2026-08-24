#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_biological_apprentice_manual_four_hundred_fiftieth"

VALUE_REVISIONS = {
    "c1913ec4ff84148da6d3": "dies kurz im Durchlass halten",
    "f2af6326898fb5b490a4": "weiter hinausfuehren; Schluss",
    "bc4f1f5c006c74a4d26d": "absetzen; Schluss",
}

QOKCH_SHORT = "87411f84689b4f93a303"
OKCHED_EXPANDED = "07913ef9b1fb773cd325"
DCHED_DEFAULT = "259b2b3b0bf859882e2c"
DCH_AFTER_TARGET = "d225b7a7b95da7aee437"
CHD_CURRENT = "6f7ff8287eddf4da9fdb"
CHEDCHY_BEFORE_TARGET = "5e8441397e7c0faf042b"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_FIFTIETH_281_EVENT_EDITION.tsv")
    for row in events:
        if row["joint_tuple_id"] in VALUE_REVISIONS:
            row["small_value_de"] = VALUE_REVISIONS[row["joint_tuple_id"]]
    write("FOUR_HUNDRED_FIFTY_FIRST_281_EVENT_EDITION.tsv", events)

    values = {row["joint_tuple_id"]: row["small_value_de"] for row in events}
    dictionary = read("FOUR_HUNDRED_FIFTIETH_124_CARD_DICTIONARY.tsv")
    for row in dictionary:
        row["small_value_de"] = values[row["joint_tuple_id"]]
    write("FOUR_HUNDRED_FIFTY_FIRST_124_CARD_DICTIONARY.tsv", dictionary)

    event_by_id = {row["event_id"]: row for row in events}
    statements = read("FOUR_HUNDRED_FIFTIETH_97_STATEMENT_EDITION.tsv")
    base_settle_statements = {row["statement_id"] for row in events if row["joint_tuple_id"] == "bc4f1f5c006c74a4d26d"}
    for row in statements:
        statement_events = [event_by_id[event_id] for event_id in row["event_ids"].split("|")]
        row["card_sequence_de"] = " > ".join(event["small_value_de"] for event in statement_events)
        if row["statement_id"] in base_settle_statements:
            row["continuous_reading_de"] = row["continuous_reading_de"].replace("kurz absetzen", "absetzen").replace("Kurz absetzen", "Absetzen")
        if row["statement_id"] == "B2-S006":
            row["continuous_reading_de"] = "Dies kurz im Durchlass halten."
        if row["statement_id"] == "B2-S022":
            row["continuous_reading_de"] = "Weiter hinausfuehren und schliessen."
    write("FOUR_HUNDRED_FIFTY_FIRST_97_STATEMENT_EDITION.tsv", statements)

    cards_by_value: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in dictionary:
        cards_by_value[row["small_value_de"]].append(row)
    duplicate_before = []
    for value, cards in cards_by_value.items():
        if len(cards) > 1:
            duplicate_before.append({
                "small_value_de": value, "candidate_cards": len(cards),
                "card_nos": "|".join(card["card_no"] for card in cards),
                "joint_tuple_ids": "|".join(card["joint_tuple_id"] for card in cards),
                "surfaces": " || ".join(card["surfaces"] for card in cards),
                "selection_layer": "RECORD_THEN_LOCAL_CONTEXT",
            })
    write("FOUR_HUNDRED_FIFTY_FIRST_FIVE_ALIAS_FAMILIES.tsv", duplicate_before)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    trace = []
    for row in events:
        statement_events = by_statement[row["statement_id"]]
        position = statement_events.index(row)
        previous_value = statement_events[position - 1]["small_value_de"] if position else "START"
        next_value = statement_events[position + 1]["small_value_de"] if position + 1 < len(statement_events) else "END"
        global_candidates = cards_by_value[row["small_value_de"]]
        record_candidates = [card for card in global_candidates if row["record_unit_id"] in card["records"].split("|")]
        rule = "UNIQUE_VALUE"
        if len(record_candidates) == 1:
            selected = record_candidates[0]
            if len(global_candidates) > 1:
                rule = "RECORD_NAMESPACE"
        elif {card["joint_tuple_id"] for card in record_candidates} == {QOKCH_SHORT, OKCHED_EXPANDED}:
            selected_id = QOKCH_SHORT if position == 0 else OKCHED_EXPANDED
            selected = next(card for card in record_candidates if card["joint_tuple_id"] == selected_id)
            rule = "STATEMENT_INITIAL_SHORT_ELSE_EXPANDED"
        elif {card["joint_tuple_id"] for card in record_candidates} == {DCHED_DEFAULT, DCH_AFTER_TARGET}:
            selected_id = DCH_AFTER_TARGET if previous_value == "kurz fortsetzen" else DCHED_DEFAULT
            selected = next(card for card in record_candidates if card["joint_tuple_id"] == selected_id)
            rule = "SHORT_DCH_AFTER_SHORT_CONTINUE_ELSE_DEFAULT"
        elif {card["joint_tuple_id"] for card in record_candidates} == {CHD_CURRENT, CHEDCHY_BEFORE_TARGET}:
            selected_id = CHEDCHY_BEFORE_TARGET if next_value == "an die Stelle setzen" else CHD_CURRENT
            selected = next(card for card in record_candidates if card["joint_tuple_id"] == selected_id)
            rule = "CHEDCHY_BEFORE_TARGET_SET_ELSE_CURRENT_CHD"
        else:
            raise ValueError(f"unresolved reverse candidates for {row['event_id']}: {record_candidates}")
        trace.append({
            "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "statement_id": row["statement_id"],
            "statement_position": position + 1, "instruction_atom_de": row["small_value_de"],
            "global_candidates": len(global_candidates), "record_candidates": len(record_candidates),
            "previous_atom_de": previous_value, "next_atom_de": next_value, "selection_rule": rule,
            "selected_joint_tuple_id": selected["joint_tuple_id"], "expected_joint_tuple_id": row["joint_tuple_id"],
            "selected_surfaces": selected["surfaces"], "exact_recovery": "PASS" if selected["joint_tuple_id"] == row["joint_tuple_id"] else "FAIL",
        })
    write("FOUR_HUNDRED_FIFTY_FIRST_281_REVERSE_TRACE.tsv", trace)

    rules = [
        {"priority": 1, "rule": "UNIQUE_VALUE", "condition": "one global card has the instruction atom", "action": "write that card"},
        {"priority": 2, "rule": "RECORD_NAMESPACE", "condition": "aliases occur in different records", "action": "use the record card"},
        {"priority": 3, "rule": "STATEMENT_INITIAL_SHORT_ELSE_EXPANDED", "condition": "QOKCHDY versus OKCHEDY", "action": "short at statement start; expanded after prior action"},
        {"priority": 4, "rule": "SHORT_DCH_AFTER_SHORT_CONTINUE_ELSE_DEFAULT", "condition": "DCHDY versus DCHEDY", "action": "DCHDY only after KURZ FORTSETZEN"},
        {"priority": 5, "rule": "CHEDCHY_BEFORE_TARGET_SET_ELSE_CURRENT_CHD", "condition": "CHEDCHY versus CHDY/CHEDY", "action": "CHEDCHY immediately before AN DIE STELLE SETZEN"},
    ]
    write("FOUR_HUNDRED_FIFTY_FIRST_FIVE_REVERSE_RULES.tsv", rules)

    histogram = Counter((int(row["global_candidates"]), int(row["record_candidates"]), row["selection_rule"]) for row in trace)
    summary = {
        "status": "PASS" if all(row["exact_recovery"] == "PASS" for row in trace) else "FAIL",
        "events": len(events), "statements": len(statements), "cards": len(dictionary),
        "distinct_instruction_atoms": len(cards_by_value), "alias_families": len(duplicate_before),
        "globally_unique_events": sum(int(row["global_candidates"]) == 1 for row in trace),
        "record_resolved_events": sum(row["selection_rule"] == "RECORD_NAMESPACE" for row in trace),
        "context_resolved_events": sum(row["selection_rule"] not in {"UNIQUE_VALUE", "RECORD_NAMESPACE"} for row in trace),
        "exact_recovery_events": sum(row["exact_recovery"] == "PASS" for row in trace),
        "selection_histogram": {f"g{g}_r{r}_{rule}": count for (g, r, rule), count in sorted(histogram.items())},
    }
    (HERE / "FOUR_HUNDRED_FIFTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if summary["status"] != "PASS":
        raise SystemExit(summary)


if __name__ == "__main__":
    main()
