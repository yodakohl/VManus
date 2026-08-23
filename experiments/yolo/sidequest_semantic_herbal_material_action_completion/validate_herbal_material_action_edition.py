#!/usr/bin/env python3
"""Mechanical completeness checks for the creative Herbal edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = read_tsv("SELECTED_173_HERBAL_MATERIAL_DICTIONARY.tsv")
events = read_tsv("SELECTED_381_HERBAL_MATERIAL_INTERLINEAR.tsv")
sentences = read_tsv("SELECTED_116_HERBAL_MATERIAL_SENTENCES.tsv")
paradigm = read_tsv("HERBAL_MATERIAL_PARADIGM.tsv")
components = read_tsv("HERBAL_MATERIAL_COMPONENTS.tsv")
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
    "herbal_sentences_19": sum(row["record_unit_id"].startswith("H") for row in sentences) == 19,
    "revised_cards_19": sum(row["herbal_revision"] == "REVISED" for row in dictionary) == 19,
    "revised_events_19": sum(row["herbal_revision"] == "REVISED" for row in events) == 19,
    "paradigm_19": len(paradigm) == 19,
    "components_23": len(components) == 23,
    "cth_or_composes": dmap["dedc383b600397a301ee"]["concrete_word_reading_de"] == "Ansatz bereit",
    "cth_aiin_composes": dmap["f3c23f42baf625639e1e"]["concrete_word_reading_de"] == "Bereitmaß",
    "ho_aiin_composes": dmap["834825c61d048a6b5628"]["concrete_word_reading_de"] == "Zutatenmaß",
    "ho_al_y_composes": dmap["0ec6a45e2950e8e7061d"]["concrete_word_reading_de"] == "Zutat dorthin",
    "y_cheo_or_composes": dmap["7249edc4df3419c26999"]["concrete_word_reading_de"] == "Auszugsansatz",
    "disease_overreads_removed": all(word not in row["concrete_word_reading_de"] for row in dictionary for word in ("Geschwür", "Husten", "Leibstechen")),
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
        "component_rows": len(components),
    },
}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
