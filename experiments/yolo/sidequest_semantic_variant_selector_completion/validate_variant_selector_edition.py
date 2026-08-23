#!/usr/bin/env python3
"""Validate the creative local-variant selector edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_work_module_completion"
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = rows(HERE / "SELECTED_173_VARIANT_SELECTOR_DICTIONARY.tsv")
events = rows(HERE / "SELECTED_381_VARIANT_SELECTOR_INTERLINEAR.tsv")
sentences = rows(HERE / "SELECTED_116_VARIANT_SELECTOR_SENTENCES.tsv")
selectors = rows(HERE / "VARIANT_SELECTOR_REGISTER.tsv")
module_summary = rows(HERE / "MODULE_SELECTOR_SUMMARY.tsv")
programs = rows(HERE / "PROGRAM_CARD_DECK.tsv")
axes = rows(HERE / "SELECTOR_AXIS_LEXICON.tsv")
base_dictionary = rows(BASE / "SELECTED_173_WORK_MODULE_DICTIONARY.tsv")
base_events = rows(BASE / "SELECTED_381_WORK_MODULE_INTERLINEAR.tsv")
base_sentences = rows(BASE / "SELECTED_116_WORK_MODULE_SENTENCES.tsv")

dmap = {row["joint_tuple_id"]: row for row in dictionary}
smap = {row["statement_id"]: row for row in sentences}
selector_map = {row["statement_id"]: row for row in selectors}
program_map = {row["program_card_id"]: row for row in programs}
axis_counts = Counter(row["selector_axis"] for row in selectors)

checks = {
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "selectors_66": len(selectors) == 66,
    "selector_ids_unique": len(selector_map) == 66,
    "variant_modules_13": len(module_summary) == 13,
    "program_cards_28": len(programs) == 28,
    "selector_axes_11": len(axes) == 11,
    "variant_events_183": sum(row["variant_selector_status"] == "LOCAL_VARIANT_EVENT" for row in events) == 183,
    "program_events_64": sum(row["variant_program_card"] == "YES" for row in events) == 64,
    "record_layout_2": sum(row["program_card_id"] == "RECORD_LAYOUT" for row in selectors) == 2,
    "program_dictionary_rows_28": sum(row["variant_program_card_usage"] == "YES" for row in dictionary) == 28,
    "program_reuse_agreement": all(
        int(row["program_reuse_count"]) == int(program_map[row["program_card_id"]]["occurrence_count"])
        for row in selectors if row["program_card_id"] != "RECORD_LAYOUT"
    ),
    "program_event_is_final": all(
        row["program_card_id"] == "RECORD_LAYOUT"
        or row["program_event_id"] == smap[row["statement_id"]]["event_ids"].split("|")[-1]
        for row in selectors
    ),
    "program_action_invariant": all(
        len({row["selector_value_de"] for row in selectors if row["program_card_id"] == card_id}) == 1
        for card_id in program_map
    ),
    "dictionary_event_agreement": all(
        row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in events
    ),
    "dictionary_values_unchanged": all(
        row["concrete_word_reading_de"] == old["concrete_word_reading_de"] for row, old in zip(dictionary, base_dictionary)
    ),
    "event_values_unchanged": all(
        row["contextual_event_reading_de"] == old["contextual_event_reading_de"] for row, old in zip(events, base_events)
    ),
    "sentence_repairs_exact_5": {
        row["statement_id"] for row in sentences if row["variant_selector_sentence_revision"] == "REMOVE_POSITIONAL_CHRONOLOGY"
    } == {"B1-S001", "B1-S010", "B1-S021", "B2-S009", "B4-S007"},
    "other_111_sentence_values_unchanged": all(
        row["workshop_sentence_de"] == old["workshop_sentence_de"]
        for row, old in zip(sentences, base_sentences)
        if row["variant_selector_sentence_revision"] == "UNCHANGED"
    ),
    "axis_counts_total_66": sum(axis_counts.values()) == 66,
    "fixed_pages_only": {row["page"] for row in events} == ALLOWED,
    "sealed_absent": not any(row["page"].startswith("f84") for row in events),
    "records_markdown_complete": all(
        f"## {record} —" in (HERE / "SELECTED_11_VARIANT_SELECTOR_RECORDS.md").read_text(encoding="utf-8")
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
        "variant_modules": len(module_summary),
        "variant_entries": len(selectors),
        "program_cards": len(programs),
        "axes": len(axes),
        "axis_counts": dict(sorted(axis_counts.items())),
    },
}
(HERE / "VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
