#!/usr/bin/env python3
"""Validate the compact KCH/TY and remaining-nomenclator edition."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
PREVIOUS = PARENT / "sidequest_semantic_singleton_composition_rescue"
VALIDATION_OUT = HERE / "VALIDATION.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict[str, object]:
    previous_words = rows(PREVIOUS / "APPRENTICE_68_RECOMPOSED_WORD_DECK.tsv")
    tail = rows(HERE / "REMAINING_27_FAMILY_DISPOSITION.tsv")
    paradigms = rows(HERE / "KCH_TY_PARADIGMS.tsv")
    families = rows(HERE / "COMPACT_FAMILY_DECKS.tsv")
    dictionary = rows(HERE / "COMPACT_173_CARD_DICTIONARY.tsv")
    events = rows(HERE / "COMPACT_381_EVENT_INTERLINEAR.tsv")
    phrases = rows(HERE / "COMPACT_116_PHRASES.tsv")
    records = (HERE / "COMPACT_11_RECORDS.md").read_text(encoding="utf-8")

    checks: dict[str, bool] = {}
    checks["previous_tail_count_27"] = sum(r["singleton_composition_status"] == "WHOLE_RETAIN" for r in previous_words) == 27
    checks["tail_count_27"] = len(tail) == 27
    checks["tail_unique_cards"] = len({r["joint_tuple_id"] for r in tail}) == 27
    checks["tail_unique_surfaces"] = len({r["surface_family"] for r in tail}) == 27
    checks["tail_unique_events"] = len({r["event_id"] for r in tail}) == 27
    tail_counts = Counter(r["family_disposition"] for r in tail)
    checks["tail_status_counts"] = tail_counts == Counter({
        "PRODUCTIVE_RECOMPOSITION": 7,
        "PARTIAL_RECOMPOSITION": 10,
        "SHARED_WHOLE_HEADWORD": 3,
        "WHOLE_RETAIN": 7,
    })
    checks["paradigm_count_9"] = len(paradigms) == 9
    checks["paradigm_split_4_5"] = Counter(r["paradigm"] for r in paradigms) == Counter({"KCH_PROCESS": 4, "TY_PART": 5})
    checks["paradigm_occurrences_10"] = sum(int(r["occurrences"]) for r in paradigms) == 10
    checks["family_decks_7"] = len(families) == 7
    checks["dictionary_173"] = len(dictionary) == 173
    checks["dictionary_unique_cards"] = len({r["joint_tuple_id"] for r in dictionary}) == 173
    checks["events_381"] = len(events) == 381
    checks["events_unique"] = len({r["event_id"] for r in events}) == 381
    checks["phrases_116"] = len(phrases) == 116
    checks["phrases_unique"] = len({r["statement_id"] for r in phrases}) == 116
    checks["phrase_event_sum_381"] = sum(int(r["event_count"]) for r in phrases) == 381
    checks["records_11"] = sum(line.startswith("## ") for line in records.splitlines()) == 11
    checks["revised_statements_20"] = sum(r["compact_statement_revised"] == "YES" for r in phrases) == 20

    card_arch = Counter(r["compact_architecture"] for r in dictionary)
    event_arch = Counter(r["compact_architecture"] for r in events)
    open_arch = Counter(r["compact_architecture"] for r in events if r["step_closure_role"] != "COMMIT_CELL")
    checks["card_architecture_131_20_22"] = card_arch == Counter({
        "PRODUCTIVE_COMPOSITION": 131,
        "PARTIAL_COMPOSITION": 20,
        "MEMORIZED_WHOLE_CARD": 22,
    })
    checks["event_architecture_332_21_28"] = event_arch == Counter({
        "PRODUCTIVE_COMPOSITION": 332,
        "PARTIAL_COMPOSITION": 21,
        "MEMORIZED_WHOLE_CARD": 28,
    })
    checks["open_architecture_256_16_20"] = open_arch == Counter({
        "PRODUCTIVE_COMPOSITION": 256,
        "PARTIAL_COMPOSITION": 16,
        "MEMORIZED_WHOLE_CARD": 20,
    })
    card_map = {r["joint_tuple_id"]: r for r in dictionary}
    checks["event_dictionary_readings_match"] = all(
        r["compact_card_reading_de"] == card_map[r["joint_tuple_id"]]["compact_reading_de"] for r in events
    )
    checks["event_dictionary_architecture_match"] = all(
        r["compact_architecture"] == card_map[r["joint_tuple_id"]]["compact_architecture"] for r in events
    )
    by_surface = {r["surface_family"]: r for r in dictionary}
    expected = {
        "kchy": "diesen Posten bearbeiten",
        "kchey": "diesen Posten kurz bearbeiten",
        "kchal": "an der Zielstelle bearbeiten",
        "kchol": "weiter bearbeiten",
        "chety|chty": "Teil abtrennen",
        "shoyty": "Zutatenteil",
        "etyd": "kleiner Restteil",
        "cheeety": "ganzen Teilposten",
        "otytchol": "naechsten Teilposten weiterfuehren",
        "ly": "Gefaess",
        "oykchor": "Gefaess",
    }
    checks["key_readings_exact"] = all(by_surface[s]["compact_reading_de"] == v for s, v in expected.items())
    checks["no_empty_compact_values"] = all(r["compact_parse"].strip() and r["compact_reading_de"].strip() for r in dictionary)
    checks["allowed_pages_only"] = {r["page"] for r in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}

    outputs = [
        HERE / "REMAINING_27_FAMILY_DISPOSITION.tsv",
        HERE / "KCH_TY_PARADIGMS.tsv",
        HERE / "COMPACT_FAMILY_DECKS.tsv",
        HERE / "COMPACT_173_CARD_DICTIONARY.tsv",
        HERE / "COMPACT_381_EVENT_INTERLINEAR.tsv",
        HERE / "COMPACT_116_PHRASES.tsv",
        HERE / "COMPACT_11_RECORDS.md",
    ]
    sealed_page = re.compile(r"(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", re.IGNORECASE)
    checks["sealed_page_selectors_absent"] = all(
        sealed_page.search(path.read_text(encoding="utf-8")) is None for path in outputs
    )
    before = {path.name: sha256(path) for path in outputs}
    spec = importlib.util.spec_from_file_location("nomenclator_builder", HERE / "build_nomenclator_family_completion.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.build()
    after = {path.name: sha256(path) for path in outputs}
    checks["deterministic_rebuild"] = before == after

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "checks": checks,
        "counts": {
            "tail_dispositions": dict(tail_counts),
            "card_architecture": dict(card_arch),
            "event_architecture": dict(event_arch),
            "open_event_architecture": dict(open_arch),
            "dictionary": len(dictionary),
            "events": len(events),
            "phrases": len(phrases),
            "records": 11,
        },
        "output_sha256": {path.name: sha256(path) for path in outputs},
    }
    VALIDATION_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
