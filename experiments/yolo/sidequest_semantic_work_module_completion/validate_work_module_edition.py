#!/usr/bin/env python3
"""Validate the creative work-module edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_handoff_resolution_completion"
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = rows(HERE / "SELECTED_173_WORK_MODULE_DICTIONARY.tsv")
events = rows(HERE / "SELECTED_381_WORK_MODULE_INTERLINEAR.tsv")
sentences = rows(HERE / "SELECTED_116_WORK_MODULE_SENTENCES.tsv")
modules = rows(HERE / "WORK_MODULE_REGISTER.tsv")
edges = rows(HERE / "STATEMENT_RELATION_REGISTER.tsv")
base_dictionary = rows(BASE / "SELECTED_173_HANDOFF_DICTIONARY.tsv")
base_events = rows(BASE / "SELECTED_381_HANDOFF_INTERLINEAR.tsv")
base_sentences = rows(BASE / "SELECTED_116_HANDOFF_SENTENCES.tsv")

dmap = {row["joint_tuple_id"]: row for row in dictionary}
smap = {row["statement_id"]: row for row in sentences}
module_map = {row["module_id"]: row for row in modules}
edge_counts = Counter(row["edge_class"] for row in edges)
module_counts = Counter(row["module_type"] for row in modules)

checks = {
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "modules_37": len(modules) == 37,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "edges_105": len(edges) == 105,
    "module_ids_unique": len(module_map) == 37,
    "statement_ids_unique": len(smap) == 116,
    "all_statement_modules_exist": all(row["work_module_id"] in module_map for row in sentences),
    "all_event_modules_exist": all(row["work_module_id"] in module_map for row in events),
    "event_statement_module_agreement": all(
        row["work_module_id"] == smap[row["statement_id"]]["work_module_id"] for row in events
    ),
    "dictionary_event_agreement": all(
        row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in events
    ),
    "dictionary_unchanged": all(
        row["concrete_word_reading_de"] == old["concrete_word_reading_de"]
        for row, old in zip(dictionary, base_dictionary)
    ),
    "event_readings_unchanged": all(
        row["contextual_event_reading_de"] == old["contextual_event_reading_de"]
        for row, old in zip(events, base_events)
    ),
    "sentence_readings_unchanged": all(
        row["workshop_sentence_de"] == old["workshop_sentence_de"]
        for row, old in zip(sentences, base_sentences)
    ),
    "module_statement_total_116": sum(int(row["statement_count"]) for row in modules) == 116,
    "module_event_total_381": sum(int(row["event_count"]) for row in modules) == 381,
    "handoff_edges_19": edge_counts["EXPLICIT_HANDOFF_SAME_OWNER"] + edge_counts["EXPLICIT_HANDOFF_CROSS_OWNER"] == 19,
    "handoff_same_owner_14": edge_counts["EXPLICIT_HANDOFF_SAME_OWNER"] == 14,
    "handoff_cross_owner_5": edge_counts["EXPLICIT_HANDOFF_CROSS_OWNER"] == 5,
    "parallel_edges_60": edge_counts["PARALLEL_OR_EDITORIAL_WITHIN_MODULE"] == 60,
    "module_boundaries_26": edge_counts["NEW_MODULE_BOUNDARY_SAME_OWNER"] + edge_counts["NEW_MODULE_BOUNDARY_OWNER_CHANGE"] == 26,
    "edge_partition_105": sum(edge_counts.values()) == 105,
    "owner_breaks_exact": {
        row["statement_id"] for row in sentences if row["work_module_owner_break"] == "YES"
    } == {"B2-S012", "B3-S016", "B3-S026", "B4-S015"},
    "module_types_expected": set(module_counts) == {
        "CONTINUOUS_MATERIAL_CHAIN",
        "SELF_CONTAINED_ROUTINE",
        "LOCAL_STATION_VARIANTS",
        "LOCAL_ROUTINE_WITH_HANDOFF",
        "CROSS_STATION_HANDOFF",
        "OWNER_BREAK_COMPOSITE",
    },
    "all_module_text_concrete": all(row["workshop_module_reading_de"].strip() for row in modules),
    "fixed_pages_only": {row["page"] for row in events} == ALLOWED,
    "sealed_pages_absent": not any(row["page"].startswith("f84") for row in events),
    "record_markdown_complete": all(
        f"## {record} —" in (HERE / "SELECTED_11_WORK_MODULE_RECORDS.md").read_text(encoding="utf-8")
        for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    ),
}

result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "cards": len(dictionary),
        "events": len(events),
        "sentences": len(sentences),
        "records": len({row["record_unit_id"] for row in sentences}),
        "modules": len(modules),
        "edges": len(edges),
        "module_types": dict(sorted(module_counts.items())),
        "edge_classes": dict(sorted(edge_counts.items())),
    },
}
(HERE / "VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
