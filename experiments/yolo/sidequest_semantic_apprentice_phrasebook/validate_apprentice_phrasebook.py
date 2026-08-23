#!/usr/bin/env python3
"""Validate the compact apprentice phrasebook and its learning counts."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_open_middle_lexicon"
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


outputs = [
    HERE / "APPRENTICE_CORE_16.tsv",
    HERE / "APPRENTICE_68_WHOLE_WORD_DECK.tsv",
    HERE / "APPRENTICE_55_LOCAL_HEADWORDS.tsv",
    HERE / "APPRENTICE_LEXICAL_DRAWERS.tsv",
    HERE / "APPRENTICE_9_PHRASE_TEMPLATES.tsv",
    HERE / "APPRENTICE_116_PHRASES.tsv",
    HERE / "APPRENTICE_11_RECORDS.md",
    HERE / "BUILD_CHECK.json",
    HERE / "BUILD_SUMMARY.json",
]
before = {path.name: sha(path) for path in outputs}
subprocess.run(
    [sys.executable, str(HERE / "build_apprentice_phrasebook.py")],
    check=True,
    capture_output=True,
    text=True,
)
after = {path.name: sha(path) for path in outputs}

core = rows(outputs[0])
words = rows(outputs[1])
local = rows(outputs[2])
drawers = rows(outputs[3])
templates = rows(outputs[4])
phrases = rows(outputs[5])
source_dictionary = rows(BASE / "SELECTED_173_OPEN_MIDDLE_DICTIONARY.tsv")
source_events = rows(BASE / "SELECTED_381_OPEN_MIDDLE_INTERLINEAR.tsv")
source_sentences = rows(BASE / "SELECTED_116_OPEN_MIDDLE_SENTENCES.tsv")

word_class_types = Counter(row["word_class"] for row in words)
word_class_events = Counter()
for row in words:
    word_class_events[row["word_class"]] += int(row["occurrence_count"])
template_counts = Counter(row["template_id"] for row in phrases)
coverage_counts = Counter(row["coverage_class"] for row in phrases)
duplicate_heads = Counter(row["apprentice_headword_de"].casefold() for row in words)

checks = {
    "deterministic_rebuild": before == after,
    "source_cards_173": len(source_dictionary) == 173,
    "source_events_381": len(source_events) == 381,
    "source_sentences_116": len(source_sentences) == 116,
    "core_types_16": len(core) == 16,
    "core_events_148": sum(int(row["occurrence_count"]) for row in core) == 148,
    "core_15_rules_1_word": Counter(row["learning_mode"] for row in core) == Counter({"PRODUCTIVE_RULE": 15, "WHOLE_WORD": 1}),
    "whole_word_types_68": len(words) == 68,
    "whole_word_events_75": sum(int(row["occurrence_count"]) for row in words) == 75,
    "whole_word_type_classes": word_class_types == Counter({
        "LOCAL_EXEMPLAR_SINGLETON": 55,
        "MEMORIZED_RECURRENT_CARD": 5,
        "TERMINAL_SPECIALIST_WHOLE_CARD": 8,
    }),
    "whole_word_event_classes": word_class_events == Counter({
        "LOCAL_EXEMPLAR_SINGLETON": 55,
        "MEMORIZED_RECURRENT_CARD": 12,
        "TERMINAL_SPECIALIST_WHOLE_CARD": 8,
    }),
    "whole_word_distinct_heads_55": len(duplicate_heads) == 55,
    "ten_shared_headword_groups": sum(value > 1 for value in duplicate_heads.values()) == 10,
    "context_removed_25": sum(row["context_was_removed"] == "YES" for row in words) == 25,
    "local_types_55": len(local) == 55,
    "local_events_55": sum(int(row["occurrence_count"]) for row in local) == 55,
    "local_distinct_heads_45": len({row["apprentice_headword_de"].casefold() for row in local}) == 45,
    "drawers_13": len(drawers) == 13,
    "drawer_type_total_68": sum(int(row["exact_card_types"]) for row in drawers) == 68,
    "drawer_event_total_75": sum(int(row["occurrences"]) for row in drawers) == 75,
    "templates_9": len(templates) == 9,
    "template_statement_total_116": sum(int(row["statement_count"]) for row in templates) == 116,
    "template_counts_exact": template_counts == Counter({
        "P00_PROGRAM_ONLY": 40,
        "P01_ARGUMENT": 9,
        "P02_ACTION": 8,
        "P03_GRADED_ACTION": 1,
        "P04_MEASURE_ACTION": 1,
        "P05_TARGET_ACTION": 2,
        "P06_TRANSFER": 2,
        "P07_MATERIAL_PROCESS": 26,
        "P08_FULL_REGISTER": 27,
    }),
    "phrases_116": len(phrases) == 116,
    "phrase_ids_unique": len({row["statement_id"] for row in phrases}) == 116,
    "phrase_ids_match_source": {row["statement_id"] for row in phrases} == {row["statement_id"] for row in source_sentences},
    "all_381_events_bound": sum(int(row["event_count"]) for row in phrases) == 381,
    "coverage_counts_exact": coverage_counts == Counter({
        "DIRECT_PROGRAM_ONLY": 40,
        "CORE_16_ONLY": 13,
        "PRODUCTIVE_EXTENDED": 19,
        "RECURRENT_WORD_DECK_NEEDED": 2,
        "LOCAL_GLOSSARY_NEEDED": 42,
    }),
    "statements_without_local_74": sum(row["local_word_events"] == "0" for row in phrases) == 74,
    "statements_with_local_42": sum(int(row["local_word_events"]) > 0 for row in phrases) == 42,
    "every_phrase_nonempty": all(row["headword_sequence_de"] and row["fluent_workshop_sentence_de"] for row in phrases),
    "fixed_pages_only": {row["page"] for row in source_events} == ALLOWED,
    "sealed_absent": not any(row["page"].startswith("f84") for row in source_events),
    "records_11": len({row["record_unit_id"] for row in phrases}) == 11,
    "records_markdown_complete": all(f"## {record} —" in outputs[6].read_text(encoding="utf-8") for record in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6")),
}

result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "core_types": len(core),
        "whole_word_types": len(words),
        "whole_word_events": sum(int(row["occurrence_count"]) for row in words),
        "distinct_apprentice_headwords": len(duplicate_heads),
        "local_exact_types": len(local),
        "local_distinct_headwords": len({row["apprentice_headword_de"].casefold() for row in local}),
        "context_details_removed": sum(row["context_was_removed"] == "YES" for row in words),
        "drawers": len(drawers),
        "templates": len(templates),
        "coverage_counts": dict(sorted(coverage_counts.items())),
    },
    "interpretation": "A SMALL RULE DECK READS MOST INSTRUCTIONS; CONTEXTUAL DETAIL BELONGS TO IMAGE/PHRASE, NOT THE WHOLE-WORD HEADWORD",
    "sealed": {"f84": True, "f84r": True},
}
(HERE / "VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
