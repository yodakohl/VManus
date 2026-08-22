#!/usr/bin/env python3
"""Validate the selected creative medium/substance completion."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILDER = HERE / "build_selected_medium_substance_completion.py"
DICT = HERE / "SELECTED_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
EVENTS = HERE / "SELECTED_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"
SENTENCES = HERE / "SELECTED_116_MEDIUM_SUBSTANCE_SENTENCES.tsv"
RECORDS = HERE / "SELECTED_11_MEDIUM_SUBSTANCE_RECORDS.md"
COMPONENTS = HERE / "SELECTED_MEDIUM_SUBSTANCE_COMPONENTS.tsv"
PARADIGM = HERE / "SELECTED_MEDIUM_SUBSTANCE_PARADIGM.tsv"
COMPARISON = HERE / "MEDIUM_SUBSTANCE_MODEL_COMPARISON.tsv"
SUMMARY = HERE / "SELECTED_BUILD_SUMMARY.json"
VALIDATION = HERE / "validation.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
EXPECTED_RECORDS = {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"}
EXPECTED_AIR = {
    "12efe866f335461823a6", "22fb87a5a83e5c3fb510", "7d2404c835b10a2c06af",
    "b154ff779abe5f196c80", "8aedd154964a78e555d6",
}
EXPECTED_CHEO = {"087a47b5423438cd6b6a", "807591efc3d3f7ddbfab"}
EXPECTED_OR = {
    "7a4bb8136330ee4e6e56", "10488b911aae52b3b334", "dec401773c1f0347793d",
    "b9d7b6d68209a9019e7a", "6afeb5c9ab9f6cbdea0d",
}
EXPECTED_HO = "2cc054357a929df85f64"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict[str, object]:
    outputs = [DICT, EVENTS, SENTENCES, RECORDS, COMPONENTS, PARADIGM, COMPARISON, SUMMARY]
    before = {path.name: sha256(path) for path in outputs}
    subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = {path.name: sha256(path) for path in outputs}

    dictionary = read_tsv(DICT)
    events = read_tsv(EVENTS)
    sentences = read_tsv(SENTENCES)
    components = read_tsv(COMPONENTS)
    paradigm = read_tsv(PARADIGM)
    comparison = read_tsv(COMPARISON)
    dmap = {row["joint_tuple_id"]: row for row in dictionary}
    event_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    event_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        event_by_card[row["joint_tuple_id"]].append(row)
        event_by_statement[row["statement_id"]].append(row)

    checks: dict[str, bool] = {
        "deterministic_rebuild": before == after,
        "dictionary_rows_173": len(dictionary) == 173,
        "dictionary_ids_unique": len(dmap) == 173,
        "event_rows_381": len(events) == 381,
        "event_ids_unique": len({row["event_id"] for row in events}) == 381,
        "sentence_rows_116": len(sentences) == 116,
        "sentence_ids_unique": len({row["statement_id"] for row in sentences}) == 116,
        "records_exact_11": {row["record_unit_id"] for row in events} == EXPECTED_RECORDS,
        "pages_allowlisted": {row["page"] for row in events} <= ALLOWED_PAGES,
        "dictionary_defaults_nonempty": all(
            row["semantic_segmentation"] and row["stable_concrete_nucleus_de"] and row["concrete_word_reading_de"]
            for row in dictionary
        ),
        "event_defaults_nonempty": all(
            row["semantic_segmentation"] and row["stable_concrete_nucleus_de"]
            and row["concrete_word_reading_de"] and row["contextual_event_reading_de"]
            for row in events
        ),
        "every_event_card_exists": all(row["joint_tuple_id"] in dmap for row in events),
        "event_card_defaults_match": all(
            row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"]
            and row["semantic_segmentation"] == dmap[row["joint_tuple_id"]]["semantic_segmentation"]
            for row in events
        ),
        "every_dictionary_card_occurs": set(dmap) == set(event_by_card),
        "dictionary_occurrence_counts_match": all(
            int(row["occurrences"]) == len(event_by_card[row["joint_tuple_id"]]) for row in dictionary
        ),
        "sentence_event_partition_exact": sum(len(rows) for rows in event_by_statement.values()) == 381
        and set(event_by_statement) == {row["statement_id"] for row in sentences},
        "sentence_event_ids_match": all(
            row["event_ids"].split("|") == [event["event_id"] for event in event_by_statement[row["statement_id"]]]
            for row in sentences
        ),
        "sentence_counts_match": all(
            int(row["event_count"]) == len(event_by_statement[row["statement_id"]]) for row in sentences
        ),
        "sentences_have_readings": all(row["card_sequence_de"] and row["workshop_sentence_de"] for row in sentences),
        "selected_cards_23": len({row["joint_tuple_id"] for row in paradigm}) == 23,
        "paradigm_rows_23": len(paradigm) == 23,
        "paradigm_counts_match": all(int(row["occurrences"]) == len(event_by_card[row["joint_tuple_id"]]) for row in paradigm),
        "component_ids_unique": len({row["component_id"] for row in components}) == len(components),
        "component_rows_14": len(components) == 14,
        "comparison_rows_9": len(comparison) == 9,
        "air_exact_inventory": {row["joint_tuple_id"] for row in paradigm if row["stage"] == "01_WATER_ROOT"} == EXPECTED_AIR,
        "air_all_water": all("AIR=Wasser" in dmap[ident]["stable_concrete_nucleus_de"] for ident in EXPECTED_AIR),
        "cheo_exact_inventory": {row["joint_tuple_id"] for row in paradigm if row["stage"] == "02_EXTRACT_ROOT"} == EXPECTED_CHEO,
        "cheo_all_extract": all("CHEO=Auszug" in dmap[ident]["stable_concrete_nucleus_de"] for ident in EXPECTED_CHEO),
        "or_exact_inventory": {row["joint_tuple_id"] for row in paradigm if row["stage"] == "03_BATCH_ROOT"} == EXPECTED_OR,
        "or_all_batch": all("OR=Ansatz" in dmap[ident]["stable_concrete_nucleus_de"] for ident in EXPECTED_OR),
        "ho_exact_four_events": len(event_by_card[EXPECTED_HO]) == 4,
        "ho_invariant_ingredient": dmap[EXPECTED_HO]["concrete_word_reading_de"] == "Zutat"
        and {row["concrete_word_reading_de"] for row in event_by_card[EXPECTED_HO]} == {"Zutat"},
        "ho_or_predicts_ingredient_batch": dmap["b9d7b6d68209a9019e7a"]["concrete_word_reading_de"] == "Zutatenansatz",
        "shecthy_is_state_not_liquid": dmap["cb57b696b815fdef9cb7"]["concrete_word_reading_de"] == "temperiert",
        "specific_water_deck_present": {
            dmap["d4a31dbcf1ed6d9e5aa9"]["concrete_word_reading_de"],
            dmap["cbb42a4fe68068325d6b"]["concrete_word_reading_de"],
            dmap["98bdc4244c84cbef3321"]["concrete_word_reading_de"],
        } == {"Spülwasser", "Frischwasser; Schluss", "Warmwasser"},
        "wine_is_one_whole_card": dmap["428a5e3662aa57b4b256"]["concrete_word_reading_de"] == "Weinsud",
        "oil_not_dictionary_default": all("Öl" not in row["concrete_word_reading_de"] and "Oel" not in row["concrete_word_reading_de"] for row in dictionary),
        "honey_not_dictionary_default": all("Honig" not in row["concrete_word_reading_de"] for row in dictionary),
        "no_sentence_sized_selected_card_gloss": all(
            len(row["card_default_de"].replace(";", "").split()) <= 4 for row in paradigm
        ),
        "summary_built": json.loads(SUMMARY.read_text(encoding="utf-8"))["status"] == "BUILT",
        "record_markdown_has_11_sections": sum(1 for line in RECORDS.read_text(encoding="utf-8").splitlines() if line.startswith("## ")) == 11,
        "no_sealed_page_in_rows": all(not row["page"].startswith("f84") for row in events),
    }

    result: dict[str, object] = {
        "schema": "SIDEQUEST_SELECTED_MEDIUM_SUBSTANCE_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "check_count": len(checks),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "counts": {
            "cards": len(dictionary),
            "events": len(events),
            "statements": len(sentences),
            "records": len({row["record_unit_id"] for row in events}),
            "selected_cards": len(paradigm),
            "selected_events": sum(int(row["occurrences"]) for row in paradigm),
            "selected_family_counts": dict(sorted(Counter(row["stage"] for row in paradigm).items())),
        },
        "hashes": {path.name: sha256(path) for path in [DICT, EVENTS, SENTENCES, RECORDS, COMPONENTS, PARADIGM, COMPARISON, SUMMARY, BUILDER]},
        "sealed": {"f84": True, "f84r": True},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
