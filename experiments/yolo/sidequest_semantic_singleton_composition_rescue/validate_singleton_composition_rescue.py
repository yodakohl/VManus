#!/usr/bin/env python3
"""Validate completeness and internal consistency of the singleton rescue edition."""

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
SOURCE = PARENT / "sidequest_semantic_shared_headword_resolution"
LEXICON = PARENT / "sidequest_semantic_open_middle_lexicon"
VALIDATION_OUT = HERE / "VALIDATION.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict[str, object]:
    words_in = rows(SOURCE / "APPRENTICE_68_RESOLVED_WORD_DECK.tsv")
    events = rows(LEXICON / "SELECTED_381_OPEN_MIDDLE_INTERLINEAR.tsv")
    dispositions = rows(HERE / "SINGLETON_55_DISPOSITION.tsv")
    components = rows(HERE / "RESCUED_COMPONENT_LEXICON.tsv")
    words = rows(HERE / "APPRENTICE_68_RECOMPOSED_WORD_DECK.tsv")
    phrases = rows(HERE / "APPRENTICE_116_RECOMPOSED_PHRASES.tsv")
    records_text = (HERE / "APPRENTICE_11_RECOMPOSED_RECORDS.md").read_text(encoding="utf-8")

    checks: dict[str, bool] = {}
    checks["source_counts_68_381"] = len(words_in) == 68 and len(events) == 381
    checks["disposition_count_55"] = len(dispositions) == 55
    checks["disposition_unique_cards"] = len({r["joint_tuple_id"] for r in dispositions}) == 55
    checks["disposition_unique_surfaces"] = len({r["surface_family"] for r in dispositions}) == 55
    checks["disposition_unique_events"] = len({r["event_id"] for r in dispositions}) == 55
    status_counts = Counter(r["composition_status"] for r in dispositions)
    checks["status_counts_22_6_27"] = status_counts == Counter({
        "PRODUCTIVE_RESCUE": 22,
        "PARTIAL_RESCUE": 6,
        "WHOLE_RETAIN": 27,
    })
    input_singletons = {r["joint_tuple_id"] for r in words_in if r["word_class"] == "LOCAL_EXEMPLAR_SINGLETON"}
    checks["all_and_only_local_singletons"] = input_singletons == {r["joint_tuple_id"] for r in dispositions}
    checks["all_singleton_occurrences_one"] = all(r["occurrence_count"] == "1" for r in words_in if r["joint_tuple_id"] in input_singletons)
    checks["word_deck_count_68"] = len(words) == 68
    checks["word_deck_unique_cards"] = len({r["joint_tuple_id"] for r in words}) == 68
    checks["phrase_count_116"] = len(phrases) == 116
    checks["phrase_unique_statements"] = len({r["statement_id"] for r in phrases}) == 116
    checks["phrase_event_sum_381"] = sum(int(r["event_count"]) for r in phrases) == 381
    checks["record_count_11"] = sum(1 for line in records_text.splitlines() if line.startswith("## ")) == 11
    checks["component_count_18"] = len(components) == 18
    rescued = [r for r in dispositions if r["composition_status"] != "WHOLE_RETAIN"]
    checks["rescued_count_28"] = len(rescued) == 28
    checks["rescued_readings_changed"] = all(r["previous_reading_de"] != r["recomposed_reading_de"] for r in rescued)
    checks["whole_readings_preserved"] = all(r["previous_reading_de"] == r["recomposed_reading_de"] for r in dispositions if r["composition_status"] == "WHOLE_RETAIN")
    changed_cards = {r["joint_tuple_id"] for r in rescued}
    changed_statements = {e["statement_id"] for e in events if e["joint_tuple_id"] in changed_cards}
    output_changed_statements = {r["statement_id"] for r in phrases if r["recomposition_changed_statement"] == "YES"}
    checks["changed_statement_set_exact"] = changed_statements == output_changed_statements and len(changed_statements) == 25
    word_map = {r["joint_tuple_id"]: r for r in words}
    checks["word_and_disposition_readings_match"] = all(
        word_map[r["joint_tuple_id"]]["recomposed_reading_de"] == r["recomposed_reading_de"] for r in dispositions
    )
    expected = {
        "solkaiin": "bis Sollmass sammeln",
        "sheckhy": "kurz durchleiten",
        "qockhey": "kurzen Durchlauf ansetzen",
        "chary": "daraus",
        "raly": "diesen Posten dorthin",
        "choy": "diese Zutat",
        "lcheey": "Klarlauf abfuehren",
        "shecthy": "kurz bereit halten",
        "qotedaiin": "kurzes Folgemass",
    }
    by_surface = {r["surface_family"]: r for r in dispositions}
    checks["key_recompositions_exact"] = all(by_surface[s]["recomposed_reading_de"] == v for s, v in expected.items())
    checks["no_empty_selected_values"] = all(r["recomposed_reading_de"].strip() and r["selected_composition"].strip() for r in dispositions)
    checks["allowed_pages_only"] = {r["page"] for r in dispositions} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
    output_files = [
        HERE / "SINGLETON_55_DISPOSITION.tsv",
        HERE / "RESCUED_COMPONENT_LEXICON.tsv",
        HERE / "APPRENTICE_68_RECOMPOSED_WORD_DECK.tsv",
        HERE / "APPRENTICE_116_RECOMPOSED_PHRASES.tsv",
        HERE / "APPRENTICE_11_RECOMPOSED_RECORDS.md",
    ]
    sealed_page = re.compile(r"(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", re.IGNORECASE)
    checks["sealed_page_selectors_absent"] = all(
        sealed_page.search(path.read_text(encoding="utf-8")) is None for path in output_files
    )

    before = {path.name: digest(path) for path in output_files}
    spec = importlib.util.spec_from_file_location("singleton_builder", HERE / "build_singleton_composition_rescue.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.build()
    after = {path.name: digest(path) for path in output_files}
    checks["deterministic_rebuild"] = before == after

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "checks": checks,
        "counts": {
            "local_singletons": len(dispositions),
            "productive_rescues": status_counts["PRODUCTIVE_RESCUE"],
            "partial_rescues": status_counts["PARTIAL_RESCUE"],
            "whole_cards_retained": status_counts["WHOLE_RETAIN"],
            "changed_statements": len(changed_statements),
            "word_deck": len(words),
            "phrases": len(phrases),
            "source_events": len(events),
        },
        "output_sha256": {path.name: digest(path) for path in output_files},
    }
    VALIDATION_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
