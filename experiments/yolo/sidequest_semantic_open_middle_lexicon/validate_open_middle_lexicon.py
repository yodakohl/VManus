#!/usr/bin/env python3
"""Validate the creative open-middle lexicon and its full 173-card architecture."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_complete_terminal_deck"
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


outputs = [
    HERE / "SELECTED_173_OPEN_MIDDLE_DICTIONARY.tsv",
    HERE / "SELECTED_381_OPEN_MIDDLE_INTERLINEAR.tsv",
    HERE / "SELECTED_116_OPEN_MIDDLE_SENTENCES.tsv",
    HERE / "SELECTED_11_OPEN_MIDDLE_RECORDS.md",
    HERE / "OPEN_MIDDLE_136_CARD_LEXICON.tsv",
    HERE / "OPEN_MIDDLE_CORE_16_DECK.tsv",
    HERE / "RECURRENT_WHOLE_WORD_DECK.tsv",
    HERE / "OPEN_MIDDLE_SLOT_SUMMARY.tsv",
    HERE / "UNIFIED_173_CARD_ARCHITECTURE.tsv",
    HERE / "BUILD_CHECK.json",
    HERE / "BUILD_SUMMARY.json",
]
before = {path.name: sha(path) for path in outputs}
subprocess.run(
    [sys.executable, str(HERE / "build_open_middle_lexicon.py")],
    check=True,
    capture_output=True,
    text=True,
)
after = {path.name: sha(path) for path in outputs}

dictionary = rows(outputs[0])
events = rows(outputs[1])
sentences = rows(outputs[2])
middle = rows(outputs[4])
core = rows(outputs[5])
whole = rows(outputs[6])
slots = rows(outputs[7])
unified = rows(outputs[8])

base_dictionary = rows(BASE / "SELECTED_173_COMPLETE_TERMINAL_DICTIONARY.tsv")
base_events = rows(BASE / "SELECTED_381_COMPLETE_TERMINAL_INTERLINEAR.tsv")
base_sentences = rows(BASE / "SELECTED_116_COMPLETE_TERMINAL_SENTENCES.tsv")

dmap = {row["joint_tuple_id"]: row for row in dictionary}
middle_ids = {row["joint_tuple_id"] for row in middle}
terminal_ids = {row["joint_tuple_id"] for row in unified if row["layer"] == "TERMINAL"}
middle_events = [row for row in events if row["step_closure_role"] != "COMMIT_CELL"]
terminal_events = [row for row in events if row["step_closure_role"] == "COMMIT_CELL"]

middle_type_status = Counter(row["middle_lexicon_status"] for row in middle)
middle_event_status = Counter(row["open_middle_status"] for row in middle_events)
unified_type_status = Counter(row["architecture_status"] for row in unified)
unified_event_status = Counter(row["unified_lexicon_architecture"] for row in events)
core_status = Counter(row["middle_lexicon_status"] for row in core)

expected_whole = {
    ("cheey|shey", "Klarflüssigkeit", 4),
    ("dl", "Badzusatz", 2),
    ("dain", "Tuch", 2),
    ("chety|chty", "zerkleinern", 2),
    ("dchol|schol", "Vorposten", 2),
}
actual_whole = {
    (row["surface_family"], row["concrete_reading_de"], int(row["occurrence_count"]))
    for row in whole
}

checks = {
    "deterministic_rebuild": before == after,
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "middle_types_136": len(middle) == 136,
    "middle_events_292": len(middle_events) == 292,
    "terminal_types_37": len(terminal_ids) == 37,
    "terminal_events_89": len(terminal_events) == 89,
    "middle_terminal_disjoint": middle_ids.isdisjoint(terminal_ids),
    "middle_terminal_complete": middle_ids | terminal_ids == set(dmap),
    "core_types_16": len(core) == 16,
    "core_events_148": sum(int(row["occurrence_count"]) for row in core) == 148,
    "core_status_7_8_1": core_status == Counter({"PRODUCTIVE_BASE": 7, "PRODUCTIVE_COMPOSITION": 8, "MEMORIZED_RECURRENT_CARD": 1}),
    "core_ranks_1_to_16": [int(row["core_rank"]) for row in core] == list(range(1, 17)),
    "core_cumulative_148": int(core[-1]["cumulative_events"]) == 148,
    "core_coverage_0506849": core[-1]["cumulative_middle_coverage"] == "0.506849",
    "whole_types_5": len(whole) == 5,
    "whole_events_12": sum(int(row["occurrence_count"]) for row in whole) == 12,
    "whole_inventory_exact": actual_whole == expected_whole,
    "middle_type_status_10_66_5_55": middle_type_status == Counter({
        "PRODUCTIVE_BASE": 10,
        "PRODUCTIVE_COMPOSITION": 66,
        "MEMORIZED_RECURRENT_CARD": 5,
        "LOCAL_EXEMPLAR_SINGLETON": 55,
    }),
    "middle_event_status_89_136_12_55": middle_event_status == Counter({
        "PRODUCTIVE_BASE": 89,
        "PRODUCTIVE_COMPOSITION": 136,
        "MEMORIZED_RECURRENT_CARD": 12,
        "LOCAL_EXEMPLAR_SINGLETON": 55,
    }),
    "middle_productive_225": sum(value for key, value in middle_event_status.items() if key.startswith("PRODUCTIVE")) == 225,
    "slot_rows_10": len(slots) == 10,
    "slot_inventory_exact": {row["slot"] for row in slots} == {
        "OWNER_ITEM", "SOURCE", "PREPARATION", "QUANTITY", "TARGET",
        "ORDER", "MEDIUM", "FLOW_TRANSFER", "OPERATION", "STATE_GRADE",
    },
    "slot_operation_143": next(row for row in slots if row["slot"] == "OPERATION")["event_memberships"] == "143",
    "unified_rows_173": len(unified) == 173,
    "unified_type_status_exact": unified_type_status == Counter({
        "PRODUCTIVE_COMPONENT_OR_COMPOSITION": 101,
        "LICENSED_PARTIAL_COMPOSITION": 4,
        "MEMORIZED_RECURRENT_CARD": 5,
        "TERMINAL_SPECIALIST_WHOLE_CARD": 8,
        "LOCAL_EXEMPLAR_SINGLETON": 55,
    }),
    "unified_event_status_exact": unified_event_status == Counter({
        "PRODUCTIVE_COMPONENT_OR_COMPOSITION": 301,
        "LICENSED_PARTIAL_COMPOSITION": 5,
        "MEMORIZED_RECURRENT_CARD": 12,
        "TERMINAL_SPECIALIST_WHOLE_CARD": 8,
        "LOCAL_EXEMPLAR_SINGLETON": 55,
    }),
    "dictionary_preserved": all(all(new[key] == old[key] for key in old) for new, old in zip(dictionary, base_dictionary)),
    "events_preserved": all(all(new[key] == old[key] for key in old) for new, old in zip(events, base_events)),
    "sentences_preserved": all(all(new[key] == old[key] for key in old) for new, old in zip(sentences, base_sentences)),
    "dictionary_event_agreement": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in events),
    "every_middle_event_classified": all(row["open_middle_status"] for row in middle_events),
    "every_terminal_event_not_middle": all(row["open_middle_status"] == "TERMINAL_CARD" for row in terminal_events),
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
        "open_middle_types": len(middle),
        "open_middle_events": len(middle_events),
        "core_types": len(core),
        "core_events": sum(int(row["occurrence_count"]) for row in core),
        "recurrent_whole_types": len(whole),
        "recurrent_whole_events": sum(int(row["occurrence_count"]) for row in whole),
        "middle_type_status": dict(sorted(middle_type_status.items())),
        "middle_event_status": dict(sorted(middle_event_status.items())),
        "unified_type_status": dict(sorted(unified_type_status.items())),
        "unified_event_status": dict(sorted(unified_event_status.items())),
    },
    "interpretation": "PRODUCTIVE TECHNICAL SHORTHAND + FIVE RECURRENT WHOLE CARDS + LOCAL EXEMPLAR TAIL",
    "sealed": {"f84": True, "f84r": True},
}
(HERE / "VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
