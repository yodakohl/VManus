#!/usr/bin/env python3
"""Validate the compact creative step-closure edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = rows("SELECTED_173_STEP_CLOSURE_DICTIONARY.tsv")
events = rows("SELECTED_381_STEP_CLOSURE_INTERLINEAR.tsv")
sentences = rows("SELECTED_116_STEP_CLOSURE_SENTENCES.tsv")
deck = rows("STEP_CLOSURE_DECK.tsv")
endings = rows("STATEMENT_ENDINGS.tsv")
line_carry = rows("LINE_CARRY.tsv")
counters = rows("OPEN_DY_COUNTERCARDS.tsv")
dmap = {row["joint_tuple_id"]: row for row in dictionary}
by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
for event in events:
    by_statement[event["statement_id"]].append(event)

ending_counts = Counter(row["ending_class"] for row in endings)
visible_dy = [row for row in events if row["surface_display"].lower().endswith("dy")]
visible_dy_close = [row for row in visible_dy if row["step_closure_role"] == "COMMIT_CELL"]
visible_dy_open = [row for row in visible_dy if row["step_closure_role"] != "COMMIT_CELL"]
close_events = [row for row in events if row["step_closure_role"] == "COMMIT_CELL"]

checks = {
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "close_deck_37": len(deck) == 37,
    "close_events_89": len(close_events) == 89,
    "committed_89": ending_counts["COMMIT_CELL"] == 89,
    "handoff_19": ending_counts["HANDOFF_OPEN"] == 19,
    "release_8": ending_counts["RELEASE_RECORD"] == 8,
    "line_carry_18": len(line_carry) == 18,
    "visible_dy_105": len(visible_dy) == 105,
    "visible_dy_close_89": len(visible_dy_close) == 89,
    "visible_dy_open_16": len(visible_dy_open) == 16,
    "counter_rows_16": len(counters) == 16,
    "two_open_countercards": len({row["joint_tuple_id"] for row in counters}) == 2,
    "close_is_last": all(
        sum(row["step_closure_role"] == "COMMIT_CELL" for row in group) == 1
        and group[-1]["step_closure_role"] == "COMMIT_CELL"
        for group in by_statement.values()
        if any(row["step_closure_role"] == "COMMIT_CELL" for row in group)
    ),
    "dictionary_event_match": all(
        row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"]
        for row in events
    ),
    "all_cards_concrete": all(row["concrete_word_reading_de"].strip() for row in dictionary),
    "all_events_concrete": all(row["contextual_event_reading_de"].strip() for row in events),
    "all_endings_assigned": len(endings) == 116 and all(row["ending_class"] for row in endings),
    "fixed_pages_only": {row["page"] for row in events} == ALLOWED,
    "sealed_pages_absent": not any(row["page"].startswith("f84") for row in events),
    "record_reading_complete": all(
        f"## {record} —" in (HERE / "SELECTED_11_STEP_CLOSURE_RECORDS.md").read_text(encoding="utf-8")
        for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    ),
}

result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "cards": len(dictionary),
        "events": len(events),
        "sentences": len(sentences),
        "records": len({row["record_unit_id"] for row in sentences}),
        "close_card_types": len(deck),
        "close_events": len(close_events),
        "ending_classes": dict(sorted(ending_counts.items())),
        "line_carries": len(line_carry),
        "visible_dy": len(visible_dy),
        "visible_dy_open": len(visible_dy_open),
    },
}
(HERE / "VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
