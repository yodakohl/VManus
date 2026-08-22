#!/usr/bin/env python3
"""Independent shape and consistency checks for the R4 candidate."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = rows("R4_173_DICTIONARY.tsv")
events = rows("R4_381_INTERLINEAR.tsv")
sentences = rows("R4_116_SENTENCES.tsv")
paradigm = rows("R4_PARADIGM.tsv")
dmap = {row["joint_tuple_id"]: row for row in dictionary}
revised_ids = {row["joint_tuple_id"] for row in paradigm}

checks = {
    "dictionary_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "card_ids_unique": len(dmap) == 173,
    "event_ids_unique": len({row["event_id"] for row in events}) == 381,
    "statement_ids_unique": len({row["statement_id"] for row in sentences}) == 116,
    "event_card_ids_known": all(row["joint_tuple_id"] in dmap for row in events),
    "event_defaults_match_dictionary": all(
        row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"]
        for row in events
    ),
    "all_revised_defaults_short": all(
        0 < len(row["concrete_word_reading_de"].replace(";", "").split()) <= 5
        for row in dictionary
        if row["joint_tuple_id"] in revised_ids
    ),
    "all_events_partitioned": sum(int(row["event_count"]) for row in sentences) == 381,
    "paradigm_cards_exist": all(row["joint_tuple_id"] in dmap for row in paradigm),
    "paradigm_counts_match": all(
        int(row["occurrences"])
        == sum(event["joint_tuple_id"] == row["joint_tuple_id"] for event in events)
        for row in paradigm
    ),
    "only_fixed_pages": {row["page"] for row in events}
    <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_pages_absent": all(not row["page"].startswith("f84") for row in events),
}
result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "cards": len(dictionary),
        "events": len(events),
        "sentences": len(sentences),
        "paradigm_cards": len(paradigm),
    },
}
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
raise SystemExit(0 if result["status"] == "PASS" else 1)
