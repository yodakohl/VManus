#!/usr/bin/env python3
"""Completeness checks for the creative parameter/setting edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = read_tsv("SELECTED_173_PARAMETER_SETTING_DICTIONARY.tsv")
events = read_tsv("SELECTED_381_PARAMETER_SETTING_INTERLINEAR.tsv")
sentences = read_tsv("SELECTED_116_PARAMETER_SETTING_SENTENCES.tsv")
paradigm = read_tsv("PARAMETER_SETTING_PARADIGM.tsv")
register = read_tsv("PARAMETER_SETTING_REGISTER.tsv")
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
    "revised_cards_8": sum(row["parameter_revision"] == "REVISED" for row in dictionary) == 8,
    "revised_events_9": sum(row["parameter_revision"] == "REVISED" for row in events) == 9,
    "paradigm_8": len(paradigm) == 8,
    "register_21": len(register) == 21,
    "aiin_base_measure": dmap["2f1c5e56e8f0ff459065"]["concrete_word_reading_de"] == "Sollmaß",
    "ain_base_portion": dmap["9da1b6ac2c929daea697"]["concrete_word_reading_de"] == "eine Portion",
    "iin_base_stage": dmap["2c82523794dcb7d2b343"]["concrete_word_reading_de"] == "Sollstufe",
    "stand_measure": dmap["a8af08e69edab8e54f15"]["concrete_word_reading_de"] == "Standmaß",
    "settle_measure": dmap["d72f71baff01cd0a0406"]["concrete_word_reading_de"] == "Absetzmaß",
    "soft_stage": dmap["409de02322e7b2ca0c62"]["concrete_word_reading_de"] == "Weichstufe",
    "opening_stage_retained": dmap["fcc1deda9e24ec268eb0"]["concrete_word_reading_de"] == "Öffnungsstufe",
    "dose_short": dmap["9bb7122b386ebbc6138f"]["concrete_word_reading_de"] == "Gabe",
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
        "register_rows": len(register),
    },
}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
