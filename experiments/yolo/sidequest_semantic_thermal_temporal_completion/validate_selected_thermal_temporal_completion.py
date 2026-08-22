#!/usr/bin/env python3
"""Validate the selected thermal/temporal sidequest edition."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import build_selected_thermal_temporal_completion as builder


HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


dictionary = read_tsv("SELECTED_173_THERMAL_TEMPORAL_DICTIONARY.tsv")
events = read_tsv("SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv")
sentences = read_tsv("SELECTED_116_THERMAL_TEMPORAL_SENTENCES.tsv")
paradigm = read_tsv("SELECTED_THERMAL_TEMPORAL_PARADIGM.tsv")
components = read_tsv("THERMAL_TEMPORAL_COMPONENTS.tsv")
models = read_tsv("THERMAL_TEMPORAL_MODEL_COMPARISON.tsv")
summary = json.loads((HERE / "SELECTED_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
dmap = {row["joint_tuple_id"]: row for row in dictionary}
event_map = {row["event_id"]: row for row in events}

checks = {
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "paradigm_106": len(paradigm) == 106,
    "components_19": len(components) == 19,
    "models_5": len(models) == 5,
    "dictionary_ids_unique": len(dmap) == 173,
    "event_ids_unique": len(event_map) == 381,
    "statement_ids_unique": len({row["statement_id"] for row in sentences}) == 116,
    "event_dictionary_binding": all(
        event["joint_tuple_id"] in dmap
        and event["concrete_word_reading_de"] == dmap[event["joint_tuple_id"]]["concrete_word_reading_de"]
        for event in events
    ),
    "sentence_event_partition": all(
        int(row["event_count"]) == len(row["event_ids"].split("|"))
        and all(event_id in event_map for event_id in row["event_ids"].split("|"))
        for row in sentences
    ) and sum(int(row["event_count"]) for row in sentences) == 381,
    "defaults_nonempty": all(row["concrete_word_reading_de"] for row in dictionary),
    "contexts_nonempty": all(row["contextual_event_reading_de"] for row in events),
    "fixed_pages_only": {row["page"] for row in events}
    == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_pages_absent": all(not row["page"].startswith("f84") for row in events),
    "exact_repair_inventory": {
        row["joint_tuple_id"] for row in dictionary
        if row["selected_thermal_source"] == "FOUR_ROLE_LEXICAL_REPAIR"
    } == set(builder.REPAIRS),
    "aiin_is_sollmass": dmap["2f1c5e56e8f0ff459065"]["concrete_word_reading_de"] == "Sollmaß",
    "iin_is_target_grade": dmap["2c82523794dcb7d2b343"]["concrete_word_reading_de"] == "Zielstufe",
    "oldy_invariant": dmap["1b1ffdd869fb1429ad03"]["concrete_word_reading_de"] == "fortsetzen; Schluss",
    "bare_dy_not_close": dmap["b921a237be883a820352"]["concrete_word_reading_de"] != "Schluss",
    "thermal_atoms_selected": all(
        dmap[ident]["concrete_word_reading_de"] == value
        for ident, value in {
            "e8a6105b5c3a6220b440": "anwärmen",
            "204b04837409088c48f9": "anwärmen",
            "1496a731803a9f48d2e1": "noch warm",
            "8c97dfde96fbc78e3355": "warm",
            "43eb9aa12959b4d5cdc9": "roh",
            "d788d8d72d41b25a3c71": "Klarpunkt",
        }.items()
    ),
    "summary_input_hashes_current": all(
        (HERE / name).exists() and sha256(HERE / name) == digest
        for name, digest in summary["input_hashes"].items()
    ),
    "summary_output_hashes_current": all(
        (HERE / name).exists() and sha256(HERE / name) == digest
        for name, digest in summary["output_hashes"].items()
    ),
}

result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "cards": len(dictionary),
        "events": len(events),
        "sentences": len(sentences),
        "paradigm_rows": len(paradigm),
        "components": len(components),
        "lexical_repairs": len(builder.REPAIRS),
    },
    "sealed": {"f84": True, "f84r": True},
}
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
raise SystemExit(0 if result["status"] == "PASS" else 1)
