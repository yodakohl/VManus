#!/usr/bin/env python3
"""Validate the complete creative terminal-card deck."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_program_composition_completion"
STEP_BASE = HERE.parent / "sidequest_semantic_step_closure_completion"
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


outputs = [
    HERE / "SELECTED_173_COMPLETE_TERMINAL_DICTIONARY.tsv",
    HERE / "SELECTED_381_COMPLETE_TERMINAL_INTERLINEAR.tsv",
    HERE / "SELECTED_116_COMPLETE_TERMINAL_SENTENCES.tsv",
    HERE / "SELECTED_11_COMPLETE_TERMINAL_RECORDS.md",
    HERE / "COMPLETE_TERMINAL_CARD_DECK.tsv",
    HERE / "COMPLETE_TERMINAL_COMPONENT_LEXICON.tsv",
    HERE / "COMPLETE_TERMINAL_FAMILY_GRID.tsv",
    HERE / "ELEVEN_REMAINING_TERMINAL_INSTRUCTIONS.tsv",
    HERE / "BUILD_CHECK.json",
]
before = {path.name: sha(path) for path in outputs}
subprocess.run([sys.executable, str(HERE / "build_complete_terminal_deck.py")], check=True, capture_output=True, text=True)
after = {path.name: sha(path) for path in outputs}

dictionary = rows(outputs[0])
events = rows(outputs[1])
sentences = rows(outputs[2])
deck = rows(outputs[4])
components = rows(outputs[5])
families = rows(outputs[6])
remainder = rows(outputs[7])
base_dictionary = rows(BASE / "SELECTED_173_PROGRAM_COMPOSITION_DICTIONARY.tsv")
base_events = rows(BASE / "SELECTED_381_PROGRAM_COMPOSITION_INTERLINEAR.tsv")
base_sentences = rows(BASE / "SELECTED_116_PROGRAM_COMPOSITION_SENTENCES.tsv")
step_deck = rows(STEP_BASE / "STEP_CLOSURE_DECK.tsv")

dmap = {row["joint_tuple_id"]: row for row in dictionary}
smap = {row["statement_id"]: row for row in sentences}
deck_map = {row["terminal_card_id"]: row for row in deck}
terminal_ids = set(deck_map)
terminal_events = [row for row in events if row["joint_tuple_id"] in terminal_ids]
card_status = Counter(row["composition_status"] for row in deck)
event_status = Counter(row["complete_terminal_status"] for row in terminal_events)
sentence_status = Counter(row["complete_terminal_status"] for row in sentences)

checks = {
    "deterministic_rebuild": before == after,
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "terminal_types_37": len(deck) == 37,
    "terminal_events_89": len(terminal_events) == 89,
    "components_17": len(components) == 17,
    "families_9": len(families) == 9,
    "remainder_instructions_11": len(remainder) == 11,
    "remainder_types_9": len({row["terminal_card_id"] for row in remainder}) == 9,
    "terminal_inventory_matches_step_deck": terminal_ids == {row["joint_tuple_id"] for row in step_deck},
    "card_status_25_4_8": card_status == Counter({"PRODUCTIVE_COMPOSITION": 25, "LICENSED_PARTIAL": 4, "MEMORIZED_WHOLE_CARD": 8}),
    "event_status_76_5_8": event_status == Counter({"PRODUCTIVE_COMPOSITION": 76, "LICENSED_PARTIAL": 5, "MEMORIZED_WHOLE_CARD": 8}),
    "sentence_status_76_5_8_19_8": sentence_status == Counter({"PRODUCTIVE_COMPOSITION": 76, "LICENSED_PARTIAL": 5, "MEMORIZED_WHOLE_CARD": 8, "OPEN_HANDOFF": 19, "RECORD_LAYOUT_RELEASE": 8}),
    "all_terminal_events_commit": all(row["step_closure_role"] == "COMMIT_CELL" for row in terminal_events),
    "all_terminal_events_final": all(row["event_id"] == smap[row["statement_id"]]["event_ids"].split("|")[-1] for row in terminal_events),
    "all_deck_rows_have_close": all(row["close_construction"] == "EXACT_CARD_CLOSE" and "CLOSE_EXACT" in row["component_ids"].split("|") for row in deck),
    "component_ids_valid": all(set(row["component_ids"].split("|")) <= {item["component_id"] for item in components} for row in deck),
    "new_components_exact": {row["component_id"] for row in components} - {row["component_id"] for row in rows(BASE / "PROGRAM_COMPONENT_LEXICON.tsv")} == {"CORE_LSH", "GRADE_EEE"},
    "five_new_productive_types": len({row["terminal_card_id"] for row in remainder if row["composition_status"] == "PRODUCTIVE_COMPOSITION"}) == 5,
    "four_new_whole_types": {row["surface"] for row in remainder if row["composition_status"] == "MEMORIZED_WHOLE_CARD"} == {"tchody", "cheeckhody", "ody", "dshedy"},
    "all_nine_new_types_have_one_status": all(len({row["composition_status"] for row in remainder if row["terminal_card_id"] == card_id}) == 1 for card_id in {row["terminal_card_id"] for row in remainder}),
    "dictionary_preserved": all(all(new[key] == old[key] for key in old) for new, old in zip(dictionary, base_dictionary)),
    "events_preserved": all(all(new[key] == old[key] for key in old) for new, old in zip(events, base_events)),
    "sentences_preserved": all(all(new[key] == old[key] for key in old) for new, old in zip(sentences, base_sentences)),
    "dictionary_event_agreement": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in events),
    "fixed_pages_only": {row["page"] for row in events} == ALLOWED,
    "sealed_absent": not any(row["page"].startswith("f84") for row in events),
    "records_markdown_complete": all(f"## {record} —" in outputs[3].read_text(encoding="utf-8") for record in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6")),
}

result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "cards": len(dictionary),
        "events": len(events),
        "sentences": len(sentences),
        "terminal_card_types": len(deck),
        "terminal_events": len(terminal_events),
        "components": len(components),
        "families": len(families),
        "remaining_instructions": len(remainder),
        "remaining_types": len({row["terminal_card_id"] for row in remainder}),
        "card_status": dict(sorted(card_status.items())),
        "event_status": dict(sorted(event_status.items())),
    },
    "sealed": {"f84": True, "f84r": True},
}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
