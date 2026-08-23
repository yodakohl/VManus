#!/usr/bin/env python3
"""Completeness checks for the creative state/product edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = read_tsv("SELECTED_173_STATE_PRODUCT_DICTIONARY.tsv")
events = read_tsv("SELECTED_381_STATE_PRODUCT_INTERLINEAR.tsv")
sentences = read_tsv("SELECTED_116_STATE_PRODUCT_SENTENCES.tsv")
paradigm = read_tsv("STATE_PRODUCT_PARADIGM.tsv")
register = read_tsv("STATE_PRODUCT_REGISTER.tsv")
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
    "revised_cards_5": sum(row["state_product_revision"] == "REVISED" for row in dictionary) == 5,
    "revised_events_8": sum(row["state_product_revision"] == "REVISED" for row in events) == 8,
    "paradigm_5": len(paradigm) == 5,
    "register_19": len(register) == 19,
    "clear_state": dmap["d788d8d72d41b25a3c71"]["concrete_word_reading_de"] == "klar",
    "clear_product": dmap["b5df9126607030b95175"]["concrete_word_reading_de"] == "Klarflüssigkeit",
    "warm_pair": dmap["1496a731803a9f48d2e1"]["concrete_word_reading_de"] == dmap["8c97dfde96fbc78e3355"]["concrete_word_reading_de"] == "warm",
    "handwarm_state": dmap["cb57b696b815fdef9cb7"]["concrete_word_reading_de"] == "handwarm",
    "warm_pour_action": dmap["883a6708116c342cb10b"]["concrete_word_reading_de"] == "warm ausgießen",
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
