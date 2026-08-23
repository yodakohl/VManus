#!/usr/bin/env python3
"""Completeness checks for the creative Biological operation edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = read_tsv("SELECTED_173_BIOLOGICAL_OPERATION_DICTIONARY.tsv")
events = read_tsv("SELECTED_381_BIOLOGICAL_OPERATION_INTERLINEAR.tsv")
sentences = read_tsv("SELECTED_116_BIOLOGICAL_OPERATION_SENTENCES.tsv")
paradigm = read_tsv("BIOLOGICAL_OPERATION_PARADIGM.tsv")
alphabet = read_tsv("BIOLOGICAL_OPERATION_ALPHABET.tsv")
dmap = {row["joint_tuple_id"]: row for row in dictionary}

checks = {
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in events}) == 11,
    "dictionary_ids_unique": len(dmap) == 173,
    "event_ids_unique": len({row["event_id"] for row in events}) == 381,
    "all_cards_concrete": all(row["concrete_word_reading_de"].strip() for row in dictionary),
    "all_events_readable": all(row["contextual_event_reading_de"].strip() for row in events),
    "event_dictionary_match": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in events),
    "sentence_partition_381": sum(int(row["event_count"]) for row in sentences) == 381,
    "biological_sentences_97": sum(row["record_unit_id"].startswith("B") for row in sentences) == 97,
    "revised_cards_16": sum(row["biological_operation_revision"] == "REVISED" for row in dictionary) == 16,
    "revised_events_21": sum(row["biological_operation_revision"] == "REVISED" for row in events) == 21,
    "paradigm_16": len(paradigm) == 16,
    "alphabet_20": len(alphabet) == 20,
    "qokchdy_compact": dmap["87411f84689b4f93a303"]["concrete_word_reading_de"] == "umsetzen; Schluss",
    "otedy_short": dmap["c45ebac60774620561e2"]["concrete_word_reading_de"] == "kurze Folge; Schluss",
    "qoteedy_long": dmap["ff178343c18e287ce3b7"]["concrete_word_reading_de"] == "lange Folge; Schluss",
    "lkedy_rewash": dmap["b958a512ca6a3559e86e"]["concrete_word_reading_de"] == "nachwaschen; Schluss",
    "lddy_fastens": dmap["eb2e4bc143f623ee03ac"]["concrete_word_reading_de"] == "befestigen; Schluss",
    "no_sentence_sized_old_gloss": all(
        phrase not in row["concrete_word_reading_de"]
        for row in dictionary
        for phrase in ("unter besonderer Bedingung", "dieselbe örtliche Einstellung", "zweite Waschung", "mit Vorigem länger")
    ),
    "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(not row["page"].startswith("f84") for row in events),
}

result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "cards": len(dictionary),
        "events": len(events),
        "sentences": len(sentences),
        "paradigm_rows": len(paradigm),
        "alphabet_rows": len(alphabet),
    },
}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
