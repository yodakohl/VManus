#!/usr/bin/env python3
"""Compact integrity check for the creative reference/continuity edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = rows("SELECTED_173_REFERENCE_CONTINUITY_DICTIONARY.tsv")
events = rows("SELECTED_381_REFERENCE_CONTINUITY_INTERLINEAR.tsv")
sentences = rows("SELECTED_116_REFERENCE_CONTINUITY_SENTENCES.tsv")
paradigm = rows("REFERENCE_CONTINUITY_PARADIGM.tsv")
register = rows("REFERENCE_CONTINUITY_REGISTER.tsv")
dmap = {row["joint_tuple_id"]: row for row in dictionary}
smap = {row["statement_id"]: row for row in sentences}

checks = {
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "paradigm_6": len(paradigm) == 6,
    "register_25": len(register) == 25,
    "revised_events_25": sum(row["reference_revision"] == "REVISED" for row in events) == 25,
    "rewritten_sentences_7": sum(
        row["workshop_sentence_de"] != row["reference_previous_workshop_sentence_de"]
        for row in sentences
    ) == 7,
    "unique_dictionary": len(dmap) == 173,
    "unique_events": len({row["event_id"] for row in events}) == 381,
    "unique_sentences": len(smap) == 116,
    "all_concrete_defaults": all(row["concrete_word_reading_de"].strip() for row in dictionary),
    "all_event_defaults": all(row["contextual_event_reading_de"].strip() for row in events),
    "dictionary_event_agreement": all(
        row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"]
        for row in events
    ),
    "event_coverage": sum(int(row["event_count"]) for row in sentences) == 381,
    "current_item": dmap["b921a237be883a820352"]["concrete_word_reading_de"] == "dieser Posten",
    "previous_item": dmap["d665560c8ff80799a82c"]["concrete_word_reading_de"] == "Vorposten",
    "source": dmap["4d4559019a961b834aa1"]["concrete_word_reading_de"] == "daraus",
    "target": dmap["dd0ecaf5e27d81befffc"]["concrete_word_reading_de"] == "dorthin",
    "continue": dmap["dcda95c81a5460feb191"]["concrete_word_reading_de"] == "fortsetzen",
    "next": dmap["a48efd6c4491a046ba78"]["concrete_word_reading_de"] == "Folgeposten",
    "next_source": dmap["b6b654722e55729cc947"]["concrete_word_reading_de"] == "danach von dort",
    "lower_target": dmap["7811a7daff25d476e28d"]["concrete_word_reading_de"] == "untere Zielstelle",
    "final_target": dmap["97ddca78c9ebcc956d04"]["concrete_word_reading_de"] == "Endziel",
    "fixed_pages_only": {row["page"] for row in events} == ALLOWED,
    "sealed_pages_absent": not any(row["page"].startswith("f84") for row in events),
    "records_file_complete": all(f"## {record} —" in (HERE / "SELECTED_11_REFERENCE_CONTINUITY_RECORDS.md").read_text(encoding="utf-8") for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]),
}

result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "cards": len(dictionary),
        "events": len(events),
        "sentences": len(sentences),
        "records": len({row["record_unit_id"] for row in sentences}),
        "revised_cards": len(paradigm),
        "revised_events": sum(row["reference_revision"] == "REVISED" for row in events),
        "register_rows": len(register),
    },
}
(HERE / "VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
