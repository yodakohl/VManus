#!/usr/bin/env python3
"""Validate the two-layer productive/whole-card workshop edition."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "sidequest_semantic_nomenclator_family_completion"
DICT_IN = SOURCE / "COMPACT_173_CARD_DICTIONARY.tsv"
EVENTS_IN = SOURCE / "COMPACT_381_EVENT_INTERLINEAR.tsv"
PHRASES_IN = SOURCE / "COMPACT_116_PHRASES.tsv"

LEXICON = HERE / "BOUND_CARRIER_8_LEXICON.tsv"
CLOSURE = HERE / "PARTIAL_20_CLOSURE.tsv"
DICTIONARY = HERE / "CLOSED_173_CARD_DICTIONARY.tsv"
EVENTS = HERE / "CLOSED_381_EVENT_INTERLINEAR.tsv"
PHRASES = HERE / "CLOSED_116_PHRASES.tsv"
DRILLS = HERE / "CARRIER_8_DRILLS.tsv"
RECORDS = HERE / "CLOSED_11_RECORDS.md"
MANUAL = HERE / "BOUND_CARRIER_LEAF.md"
SUMMARY = HERE / "BUILD_SUMMARY.json"
VALIDATION = HERE / "VALIDATION.json"
BUILDER = HERE / "build_bound_carrier_closure.py"
OUTPUTS = [LEXICON, CLOSURE, DICTIONARY, EVENTS, PHRASES, DRILLS, RECORDS, MANUAL, SUMMARY]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    source_dictionary = read_tsv(DICT_IN)
    source_events = read_tsv(EVENTS_IN)
    source_phrases = read_tsv(PHRASES_IN)
    carriers = read_tsv(LEXICON)
    closures = read_tsv(CLOSURE)
    dictionary = read_tsv(DICTIONARY)
    events = read_tsv(EVENTS)
    phrases = read_tsv(PHRASES)
    drills = read_tsv(DRILLS)

    check("source_counts", (len(source_dictionary), len(source_events), len(source_phrases)) == (173, 381, 116),
          f"cards={len(source_dictionary)}, events={len(source_events)}, statements={len(source_phrases)}")
    partial_source = [row for row in source_dictionary if row["compact_architecture"] == "PARTIAL_COMPOSITION"]
    partial_ids = {row["joint_tuple_id"] for row in partial_source}
    partial_events = [row for row in source_events if row["joint_tuple_id"] in partial_ids]
    check("source_partial_layer", len(partial_source) == 20 and len(partial_events) == 21,
          f"partial_types={len(partial_source)}, partial_events={len(partial_events)}")

    check("carrier_inventory", len(carriers) == 8 and len({row["carrier_rule_id"] for row in carriers}) == 8,
          f"rows={len(carriers)}, unique_rules={len({row['carrier_rule_id'] for row in carriers})}")
    carrier_kinds = Counter(row["carrier_kind"] for row in carriers)
    check("carrier_kinds", carrier_kinds == Counter({"LEXICAL_MICROCORE": 3, "BOUND_CLASSIFIER": 3, "FORMAL_FRAME": 2}),
          ", ".join(f"{key}={carrier_kinds[key]}" for key in sorted(carrier_kinds)))

    closure_ids = {row["joint_tuple_id"] for row in closures}
    check("closure_inventory", len(closures) == 20 and closure_ids == partial_ids
          and all(row["closure_status"] == "PROMOTED_TO_PRODUCTIVE_COMPOSITION" for row in closures),
          "all twenty and only the partial card types are promoted")
    closure_event_ids = {event_id for row in closures for event_id in row["event_ids"].split("|")}
    check("closure_event_coverage", len(closure_event_ids) == 21
          and closure_event_ids == {row["event_id"] for row in partial_events},
          "all twenty-one partial occurrences are covered once")
    check("carrier_assignment", sum(row["carrier_rule_ids"] == "NONE_ALREADY_COMPOSED" for row in closures) == 4
          and sum(row["carrier_rule_ids"] != "NONE_ALREADY_COMPOSED" for row in closures) == 16,
          "four cards needed no new carrier and sixteen use the eight-rule sheet")

    check("closed_dictionary_inventory", len(dictionary) == 173 and len({row["joint_tuple_id"] for row in dictionary}) == 173,
          f"rows={len(dictionary)}, unique_ids={len({row['joint_tuple_id'] for row in dictionary})}")
    type_architecture = Counter(row["closed_architecture"] for row in dictionary)
    check("two_type_architecture", type_architecture == Counter({"PRODUCTIVE_COMPOSITION": 151, "MEMORIZED_WHOLE_CARD": 22}),
          f"productive={type_architecture['PRODUCTIVE_COMPOSITION']}, whole={type_architecture['MEMORIZED_WHOLE_CARD']}")
    check("no_partial_types", "PARTIAL_COMPOSITION" not in type_architecture
          and all(row["closed_parse"] and row["closed_reading_de"] for row in dictionary),
          "no card remains partially parsed or empty")

    source_event_map = {row["event_id"]: row for row in source_events}
    event_map = {row["event_id"]: row for row in events}
    event_binding_ok = len(events) == 381 and set(event_map) == set(source_event_map) and all(
        event_map[event_id]["joint_tuple_id"] == source["joint_tuple_id"]
        and event_map[event_id]["surface_display"] == source["surface_display"]
        and event_map[event_id]["statement_id"] == source["statement_id"]
        and event_map[event_id]["contextual_event_reading_de"] == source["compact_contextual_event_de"]
        for event_id, source in source_event_map.items()
    )
    check("event_binding", event_binding_ok, "all 381 event identities, surfaces, order, statements, and contextual readings are unchanged")
    event_architecture = Counter(row["closed_architecture"] for row in events)
    check("two_event_architecture", event_architecture == Counter({"PRODUCTIVE_COMPOSITION": 353, "MEMORIZED_WHOLE_CARD": 28}),
          f"productive={event_architecture['PRODUCTIVE_COMPOSITION']}, whole={event_architecture['MEMORIZED_WHOLE_CARD']}")
    check("no_partial_events", all(row["teaching_symbol"] in {"P", "W"} for row in events)
          and Counter(row["teaching_symbol"] for row in events) == Counter({"P": 353, "W": 28}),
          "the former p layer has disappeared from all event rows")
    check("page_scope", {row["page"] for row in events} <= ALLOWED_PAGES,
          "only the seven fixed prose pages occur")

    source_phrase_map = {row["statement_id"]: row for row in source_phrases}
    phrase_map = {row["statement_id"]: row for row in phrases}
    phrase_binding_ok = len(phrases) == 116 and set(phrase_map) == set(source_phrase_map) and all(
        phrase_map[statement_id]["fluent_workshop_sentence_de"] == source["compact_fluent_sentence_de"]
        and int(phrase_map[statement_id]["event_count"]) == int(source["event_count"])
        for statement_id, source in source_phrase_map.items()
    )
    check("phrase_binding", phrase_binding_ok, "all 116 fluent instructions and event counts are unchanged")
    lesson_counts = Counter(row["lesson_level"] for row in phrases)
    check("lesson_levels", lesson_counts == Counter({"L1_FULLY_COMPOSED": 94, "L2_CODEBOOK": 22}),
          f"fully_composed={lesson_counts['L1_FULLY_COMPOSED']}, codebook={lesson_counts['L2_CODEBOOK']}")
    symbol_count = sum(len(row["architecture_sequence"].split()) for row in phrases)
    check("phrase_event_coverage", symbol_count == 381
          and sum(row["architecture_sequence"].split().count("W") for row in phrases) == 28,
          f"symbols={symbol_count}, whole_symbols={sum(row['architecture_sequence'].split().count('W') for row in phrases)}")

    check("drill_inventory", len(drills) == 8
          and {row["carrier_rule_id"] for row in drills} == {row["carrier_rule_id"] for row in carriers},
          "each carrier rule has one concrete workshop drill")
    record_text = RECORDS.read_text(encoding="utf-8")
    check("record_inventory", record_text.count("\n## ") == 11,
          "the readable edition contains all eleven prose records")
    manual_text = MANUAL.read_text(encoding="utf-8")
    check("manual_contract", all(token in manual_text for token in ["FORMAL_FRAME", "BOUND_CLASSIFIER", "LEXICAL_MICROCORE", "keine teilweise"]),
          "the manual distinguishes frames, classifiers, and microcores")
    selected_pages = (
        [page for row in closures for page in row["pages"].split("|")]
        + [page for row in dictionary for page in row["pages"].split("|")]
        + [row["page"] for row in events]
        + [row["page"] for row in phrases]
        + [row["page"] for row in drills]
    )
    check("sealed_selectors_absent", not any(page.startswith("f84") for page in selected_pages),
          "no sealed page selector occurs in generated tables; tuple hashes are not treated as selectors")

    before = {path.name: digest(path) for path in OUTPUTS}
    rebuilt = subprocess.run([sys.executable, str(BUILDER)], cwd=HERE, capture_output=True, text=True)
    after = {path.name: digest(path) for path in OUTPUTS}
    check("deterministic_rebuild", rebuilt.returncode == 0 and before == after,
          "all generated artifacts rebuilt byte-identically")

    status = "PASS" if all(row["passed"] for row in checks) else "FAIL"
    result = {
        "status": status,
        "checks_passed": sum(bool(row["passed"]) for row in checks),
        "checks_total": len(checks),
        "counts": {
            "carrier_rules": len(carriers),
            "promoted_card_types": len(closures),
            "promoted_events": len(closure_event_ids),
            "productive_card_types": type_architecture["PRODUCTIVE_COMPOSITION"],
            "whole_card_types": type_architecture["MEMORIZED_WHOLE_CARD"],
            "productive_events": event_architecture["PRODUCTIVE_COMPOSITION"],
            "whole_events": event_architecture["MEMORIZED_WHOLE_CARD"],
            "fully_composed_statements": lesson_counts["L1_FULLY_COMPOSED"],
            "codebook_statements": lesson_counts["L2_CODEBOOK"],
        },
        "checks": checks,
        "artifact_sha256": {path.name: digest(path) for path in OUTPUTS},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
