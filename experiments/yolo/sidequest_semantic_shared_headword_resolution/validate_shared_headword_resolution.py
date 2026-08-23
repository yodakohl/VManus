#!/usr/bin/env python3
"""Validate the contextual resolution of the ten shared apprentice headwords."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PHRASEBOOK = HERE.parent / "sidequest_semantic_apprentice_phrasebook"
LEXICON = HERE.parent / "sidequest_semantic_open_middle_lexicon"
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


outputs = [
    HERE / "SHARED_HEADWORD_24_CARD_DECISIONS.tsv",
    HERE / "SHARED_HEADWORD_10_FAMILY_SUMMARY.tsv",
    HERE / "APPRENTICE_68_RESOLVED_WORD_DECK.tsv",
    HERE / "APPRENTICE_116_RESOLVED_PHRASES.tsv",
    HERE / "APPRENTICE_11_RESOLVED_RECORDS.md",
    HERE / "BUILD_CHECK.json",
    HERE / "BUILD_SUMMARY.json",
]
before = {path.name: sha(path) for path in outputs}
subprocess.run(
    [sys.executable, str(HERE / "build_shared_headword_resolution.py")],
    check=True,
    capture_output=True,
    text=True,
)
after = {path.name: sha(path) for path in outputs}

decisions = rows(outputs[0])
families = rows(outputs[1])
words = rows(outputs[2])
phrases = rows(outputs[3])
source_words = rows(PHRASEBOOK / "APPRENTICE_68_WHOLE_WORD_DECK.tsv")
source_phrases = rows(PHRASEBOOK / "APPRENTICE_116_PHRASES.tsv")
source_events = rows(LEXICON / "SELECTED_381_OPEN_MIDDLE_INTERLINEAR.tsv")

class_counts = Counter(row["decision_class"] for row in decisions)
family_map = {row["family_id"]: row for row in families}
word_map = {row["joint_tuple_id"]: row for row in words}
source_word_map = {row["joint_tuple_id"]: row for row in source_words}

checks = {
    "deterministic_rebuild": before == after,
    "source_words_68": len(source_words) == 68,
    "source_phrases_116": len(source_phrases) == 116,
    "source_events_381": len(source_events) == 381,
    "families_10": len(families) == 10,
    "family_ids_exact": set(family_map) == {f"F{i:02d}_{name}" for i, name in enumerate(("KUEHLEN", "ABLAUF", "WAERME", "BECKEN", "SPUEL", "STELLE", "TUCH", "WARM", "WASCH", "UEBERLAUF"), 1)},
    "decision_cards_24": len(decisions) == 24,
    "decision_cards_unique": len({row["joint_tuple_id"] for row in decisions}) == 24,
    "decision_occurrences_25": sum(int(row["occurrence_count"]) for row in decisions) == 25,
    "decision_classes_exact": class_counts == Counter({
        "CONTEXTUAL_SUBTYPE": 17,
        "TERMINAL_ROUTINE_VARIANT": 3,
        "STATION_LOCAL_SYNONYM": 4,
    }),
    "graphic_allographs_zero": not any(row["decision_class"] == "GRAPHIC_ALLOGRAPH" for row in decisions),
    "all_decisions_bound_to_word_deck": {row["joint_tuple_id"] for row in decisions} <= set(word_map),
    "word_deck_68": len(words) == 68,
    "word_ids_preserved": set(word_map) == set(source_word_map),
    "word_source_columns_preserved": all(all(word_map[card_id][key] == source[key] for key in source) for card_id, source in source_word_map.items()),
    "base_headwords_54": len({row["base_headword_de"].casefold() for row in words}) == 54,
    "resolved_readings_66": len({row["resolved_reading_de"].casefold() for row in words}) == 66,
    "two_remaining_duplicate_readings": sum(value > 1 for value in Counter(row["resolved_reading_de"].casefold() for row in words).values()) == 2,
    "ablauf_polarity_exact": set(family_map["F02_ABLAUF"]["resolved_readings_de"].split("|")) == {"Ablauf schließen", "Ablauf öffnen"},
    "ueberlauf_synonym_retained": family_map["F10_UEBERLAUF"]["resolved_readings_de"] == "Überlauf",
    "tuch_specialization_exact": set(family_map["F07_TUCH"]["resolved_readings_de"].split("|")) == {"Seihtuch", "Tuch"},
    "wash_action_program_exact": set(family_map["F09_WASCH"]["resolved_readings_de"].split("|")) == {"abwaschen", "Waschgang"},
    "phrases_116": len(phrases) == 116,
    "phrase_ids_unique": len({row["statement_id"] for row in phrases}) == 116,
    "phrase_ids_preserved": {row["statement_id"] for row in phrases} == {row["statement_id"] for row in source_phrases},
    "affected_statements_25": sum(row["shared_headword_card_count"] != "0" for row in phrases) == 25,
    "revised_sentences_11": sum(row["sentence_revised"] == "YES" for row in phrases) == 11,
    "all_381_events_bound": sum(int(row["event_count"]) for row in phrases) == 381,
    "all_resolved_sequences_nonempty": all(row["resolved_headword_sequence_de"] and row["resolved_fluent_sentence_de"] for row in phrases),
    "fixed_pages_only": {row["page"] for row in source_events} == ALLOWED,
    "sealed_absent": not any(row["page"].startswith("f84") for row in source_events),
    "records_11": len({row["record_unit_id"] for row in phrases}) == 11,
    "records_markdown_complete": all(f"## {record} —" in outputs[4].read_text(encoding="utf-8") for record in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6")),
}

result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "families": len(families),
        "decision_cards": len(decisions),
        "decision_occurrences": sum(int(row["occurrence_count"]) for row in decisions),
        "decision_classes": dict(sorted(class_counts.items())),
        "base_headwords": len({row["base_headword_de"].casefold() for row in words}),
        "resolved_readings": len({row["resolved_reading_de"].casefold() for row in words}),
        "affected_statements": sum(row["shared_headword_card_count"] != "0" for row in phrases),
        "revised_sentences": sum(row["sentence_revised"] == "YES" for row in phrases),
    },
    "interpretation": "NO PURE GRAPHIC ALLOGRAPHS; SHARED BASES SPLIT BY PROCESS PHASE, POLARITY, OWNER DOMAIN, TOOL ROLE, STATE GRADE OR PROGRAM SCOPE, WITH TWO LOCAL SYNONYM PAIRS RETAINED",
    "sealed": {"f84": True, "f84r": True},
}
(HERE / "VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
