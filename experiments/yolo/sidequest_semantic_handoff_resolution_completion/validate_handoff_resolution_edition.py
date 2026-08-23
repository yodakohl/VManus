#!/usr/bin/env python3
"""Validate the creative handoff-resolution edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = rows("SELECTED_173_HANDOFF_DICTIONARY.tsv")
events = rows("SELECTED_381_HANDOFF_INTERLINEAR.tsv")
sentences = rows("SELECTED_116_HANDOFF_SENTENCES.tsv")
handoffs = rows("HANDOFF_REGISTER.tsv")
releases = rows("RECORD_RELEASE_REGISTER.tsv")
dmap = {row["joint_tuple_id"]: row for row in dictionary}
smap = {row["statement_id"]: row for row in sentences}
categories = Counter(row["handoff_category"] for row in handoffs)

checks = {
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in sentences}) == 11,
    "handoffs_19": len(handoffs) == 19,
    "unique_sources_19": len({row["source_statement_id"] for row in handoffs}) == 19,
    "unique_targets_19": len({row["target_statement_id"] for row in handoffs}) == 19,
    "direct_material_16": categories["DIRECT_MATERIAL"] == 16,
    "named_reserve_2": categories["NAMED_RESERVE"] == 2,
    "apparatus_state_1": categories["APPARATUS_STATE"] == 1,
    "releases_8": len(releases) == 8,
    "targets_rewritten_19": sum(row["handoff_resolution"] == "TARGET_REWRITTEN" for row in sentences) == 19,
    "source_target_register_agreement": all(
        smap[row["source_statement_id"]]["handoff_out_register_de"] == row["carried_register_de"]
        and smap[row["target_statement_id"]]["handoff_in_register_de"] == row["carried_register_de"]
        for row in handoffs
    ),
    "target_text_agreement": all(
        smap[row["target_statement_id"]]["workshop_sentence_de"] == row["target_reading_de"]
        for row in handoffs
    ),
    "dictionary_event_agreement": all(
        row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"]
        for row in events
    ),
    "all_cards_concrete": all(row["concrete_word_reading_de"].strip() for row in dictionary),
    "all_events_concrete": all(row["contextual_event_reading_de"].strip() for row in events),
    "fixed_pages_only": {row["page"] for row in events} == ALLOWED,
    "sealed_pages_absent": not any(row["page"].startswith("f84") for row in events),
    "records_complete": all(
        f"## {record} —" in (HERE / "SELECTED_11_HANDOFF_RECORDS.md").read_text(encoding="utf-8")
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
        "handoffs": len(handoffs),
        "categories": dict(sorted(categories.items())),
        "record_releases": len(releases),
    },
}
(HERE / "VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result["status"] != "PASS":
    raise SystemExit(1)
