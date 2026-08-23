#!/usr/bin/env python3
"""Validate the creative 28-card program-composition edition."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_variant_selector_completion"
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


outputs = [
    HERE / "SELECTED_173_PROGRAM_COMPOSITION_DICTIONARY.tsv",
    HERE / "SELECTED_381_PROGRAM_COMPOSITION_INTERLINEAR.tsv",
    HERE / "SELECTED_116_PROGRAM_COMPOSITION_SENTENCES.tsv",
    HERE / "SELECTED_11_PROGRAM_COMPOSITION_RECORDS.md",
    HERE / "PROGRAM_COMPOSITION_REGISTER.tsv",
    HERE / "PROGRAM_COMPONENT_LEXICON.tsv",
    HERE / "PROGRAM_FAMILY_GRID.tsv",
    HERE / "BUILD_CHECK.json",
]
before = {path.name: sha(path) for path in outputs}
subprocess.run([sys.executable, str(HERE / "build_program_composition_edition.py")], check=True, capture_output=True, text=True)
after = {path.name: sha(path) for path in outputs}

dictionary = rows(outputs[0])
events = rows(outputs[1])
sentences = rows(outputs[2])
register = rows(outputs[4])
components = rows(outputs[5])
families = rows(outputs[6])
base_dictionary = rows(BASE / "SELECTED_173_VARIANT_SELECTOR_DICTIONARY.tsv")
base_events = rows(BASE / "SELECTED_381_VARIANT_SELECTOR_INTERLINEAR.tsv")
base_sentences = rows(BASE / "SELECTED_116_VARIANT_SELECTOR_SENTENCES.tsv")
base_programs = rows(BASE / "PROGRAM_CARD_DECK.tsv")

dmap = {row["joint_tuple_id"]: row for row in dictionary}
smap = {row["statement_id"]: row for row in sentences}
rmap = {row["program_card_id"]: row for row in register}
program_ids = set(rmap)
mapped_events = [row for row in events if row["joint_tuple_id"] in program_ids]
card_status = Counter(row["composition_status"] for row in register)
event_status = Counter(row["program_composition_status"] for row in mapped_events)
selector_status = Counter()
for row in register:
    selector_status[row["composition_status"]] += int(row["occurrence_count"])
sentence_status = Counter(row["program_composition_status"] for row in sentences)

checks = {
    "deterministic_rebuild": before == after,
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "program_cards_28": len(register) == 28,
    "components_15": len(components) == 15,
    "families_8": len(families) == 8,
    "same_program_inventory": program_ids == {row["program_card_id"] for row in base_programs},
    "card_status_20_4_4": card_status == Counter({"PRODUCTIVE_COMPOSITION": 20, "LICENSED_PARTIAL": 4, "MEMORIZED_WHOLE_CARD": 4}),
    "event_status_69_5_4": event_status == Counter({"PRODUCTIVE_COMPOSITION": 69, "LICENSED_PARTIAL": 5, "MEMORIZED_WHOLE_CARD": 4}),
    "selector_status_55_5_4": selector_status == Counter({"PRODUCTIVE_COMPOSITION": 55, "LICENSED_PARTIAL": 5, "MEMORIZED_WHOLE_CARD": 4}),
    "mapped_events_78": len(mapped_events) == 78,
    "mapped_sentences_78": sum(sentence_status[k] for k in ("PRODUCTIVE_COMPOSITION", "LICENSED_PARTIAL", "MEMORIZED_WHOLE_CARD")) == 78,
    "remaining_terminal_11": sentence_status["OTHER_TERMINAL_CARD"] == 11,
    "open_handoff_19": sentence_status["OPEN_HANDOFF"] == 19,
    "record_release_8": sentence_status["RECORD_LAYOUT_RELEASE"] == 8,
    "all_program_occurrences_commit": all(row["step_closure_role"] == "COMMIT_CELL" for row in mapped_events),
    "all_program_occurrences_statement_final": all(row["event_id"] == smap[row["statement_id"]]["event_ids"].split("|")[-1] for row in mapped_events),
    "all_28_exact_close": all(row["close_construction"] == "EXACT_CARD_CLOSE" and "CLOSE_EXACT" in row["component_ids"].split("|") for row in register),
    "no_blank_compositions": all(all(row[key] for key in ("component_parse", "component_ids", "composed_reading_de", "exception_note_de")) for row in register),
    "component_ids_valid": all(set(row["component_ids"].split("|")) <= {item["component_id"] for item in components} for row in register),
    "program_action_preserved": all(row["program_action_de"] == next(item["program_action_de"] for item in base_programs if item["program_card_id"] == row["program_card_id"]) for row in register),
    "dictionary_values_preserved": all(all(new[key] == old[key] for key in old) for new, old in zip(dictionary, base_dictionary)),
    "event_values_preserved": all(all(new[key] == old[key] for key in old) for new, old in zip(events, base_events)),
    "sentence_values_preserved": all(all(new[key] == old[key] for key in old) for new, old in zip(sentences, base_sentences)),
    "dictionary_event_reading_agreement": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in events),
    "grade_rows_exact": {
        row["surfaces"] for row in register if row["grade_de"] != "KEIN"
    } == {"qokedy", "qokeedy", "otedy", "qoteedy", "chkeedy", "olkeedy"},
    "four_whole_cards_exact": {
        row["surfaces"] for row in register if row["composition_status"] == "MEMORIZED_WHOLE_CARD"
    } == {"sshkchdy", "rshedy", "lkedy", "qokylddy"},
    "four_partial_cards_exact": {
        row["surfaces"] for row in register if row["composition_status"] == "LICENSED_PARTIAL"
    } == {"ldy", "daldy", "dairydy", "lochedy"},
    "close_is_whole_card_role_not_suffix": all("kein global" in row["teaching_rule_de"].lower() for row in components if row["component_id"] == "CLOSE_EXACT"),
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
        "program_cards": len(register),
        "program_components": len(components),
        "program_families": len(families),
        "mapped_occurrences": len(mapped_events),
        "card_status": dict(sorted(card_status.items())),
        "event_status": dict(sorted(event_status.items())),
        "selector_status": dict(sorted(selector_status.items())),
    },
    "sealed": {"f84": True, "f84r": True},
}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
