#!/usr/bin/env python3
"""Build Pass 1002: a root-default plus local-expansion complete release."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
PAIR = ROOT / "experiments/yolo/sidequest_semantic_embedded_pair_grammar_one_thousandth"
CONTEXT = ROOT / "experiments/yolo/sidequest_semantic_contextual_composition_reconciliation_one_thousand_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def data_rows(path: Path) -> int:
    if path.suffix == ".tsv":
        return max(0, sum(1 for _ in path.open(encoding="utf-8")) - 1)
    return sum(1 for _ in path.open(encoding="utf-8"))


def main() -> None:
    root_rows = read_tsv(BASE / "PASS996_53_PORTABLE_ROOTS.tsv")
    event_rows = read_tsv(BASE / "PASS996_2511_EVENT_INTERLINEAR.tsv")
    clause_rows = read_tsv(BASE / "PASS996_354_NATURAL_CLAUSE_EDITION.tsv")
    contextual_rows = read_tsv(CONTEXT / "PASS1001_72_CONTEXTUAL_COMPOSITIONS.tsv")
    codebook_rows = read_tsv(CONTEXT / "PASS1001_175_REVISED_CODEBOOK.tsv")
    meaning = {row["recognition_form"]: row["atomic_meaning_de"] for row in root_rows}

    contextual_by_event: dict[str, dict[str, str]] = {}
    for row in contextual_rows:
        for event_id in row["event_ids"].split("|"):
            if event_id in contextual_by_event:
                raise ValueError(f"duplicate contextual event {event_id}")
            contextual_by_event[event_id] = row

    revised_events: list[dict[str, object]] = []
    revised_by_id: dict[str, dict[str, object]] = {}
    for event in event_rows:
        old_layer = event["primary_layer"]
        if event["event_id"] in contextual_by_event:
            contextual = contextual_by_event[event["event_id"]]
            layer = "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD"
            unit_ids = contextual["new_teaching_unit_id"]
            portable = contextual["root_sum_default_de"]
            source = "ROOT_SUM_PLUS_LOCAL_IMAGE_OR_EXEMPLAR_EXPANSION"
        elif old_layer == "MEMORIZED_SPECIALIST_WHOLE_WORD":
            tokens = event["component_recipe"].split("+")
            portable = " · ".join(meaning[token] for token in tokens)
            layer = "PRODUCTIVE_ROOT_COMPOSITION"
            unit_ids = event["primary_teaching_unit_ids"]
            source = "ROOT_SUM__OLD_SPECIALIST_LAYER_REMOVED"
        elif old_layer == "LOCAL_ADDRESS_OR_KENNING":
            portable = "LOKALE ADRESSE KOPIEREN"
            layer = old_layer
            unit_ids = event["primary_teaching_unit_ids"]
            source = "VISIBLE_LOCAL_ADDRESS"
        elif old_layer == "DRUG_LABEL_NOMENCLATOR":
            portable = "LOKALES DROGENETIKETT KOPIEREN"
            layer = old_layer
            unit_ids = event["primary_teaching_unit_ids"]
            source = "LOCAL_LABEL_DECK"
        else:
            tokens = event["component_recipe"].split("+")
            portable = " · ".join(meaning[token] for token in tokens)
            layer = old_layer
            unit_ids = event["primary_teaching_unit_ids"]
            source = "ROOT_SUM"

        row: dict[str, object] = {
            "event_id": event["event_id"],
            "physical_page": event["physical_page"],
            "locus": event["locus"],
            "surface": event["surface"],
            "component_recipe": event["component_recipe"],
            "primary_layer_revised": layer,
            "primary_teaching_unit_ids_revised": unit_ids,
            "portable_default_de": portable,
            "local_contextual_expansion_de": event["complete_working_reading_de"],
            "reading_source": source,
            "mnemonic_common_unit_ids": event["mnemonic_common_unit_ids"] or "KEINE",
        }
        revised_events.append(row)
        revised_by_id[event["event_id"]] = row

    event_path = OUT / "PASS1002_2511_DUAL_EVENT_INTERLINEAR.tsv"
    write_tsv(event_path, revised_events, list(revised_events[0]))

    revised_clauses: list[dict[str, object]] = []
    for clause in clause_rows:
        event_ids = clause["event_ids"].split("|")
        defaults = [str(revised_by_id[event_id]["portable_default_de"]) for event_id in event_ids]
        revised_clauses.append({
            "clause_id": clause["clause_id"],
            "physical_page": clause["physical_page"],
            "locus_span": clause["locus_span"],
            "visible_owner_or_namespace_de": clause["visible_owner_or_namespace_de"],
            "event_count": clause["event_count"],
            "surface_sequence": clause["surface_sequence"],
            "portable_root_sequence_de": " | ".join(defaults),
            "local_fluent_expansion_de": clause["complete_working_translation_de"],
            "reading_source": clause["reading_source"],
            "end_reason": clause["end_reason"],
            "event_ids": clause["event_ids"],
        })
    clause_path = OUT / "PASS1002_354_DUAL_CLAUSE_EDITION.tsv"
    write_tsv(clause_path, revised_clauses, list(revised_clauses[0]))

    codebook_path = OUT / "PASS1002_175_CURRENT_CODEBOOK.tsv"
    write_tsv(codebook_path, codebook_rows, list(codebook_rows[0]))

    bound = [
        BASE / "PASS996_53_PORTABLE_ROOTS.tsv",
        BASE / "PASS996_501_LOCAL_ADDRESS_LEDGER.tsv",
        BASE / "PASS996_14_PAGE_READABLE_EDITION.tsv",
        PAIR / "PASS1000_25_GAP_RECLASSIFICATION.tsv",
        PAIR / "PASS1000_7_REAL_ABSENCES_AND_PREDICTIONS.tsv",
        CONTEXT / "PASS1001_72_CONTEXTUAL_COMPOSITIONS.tsv",
        CONTEXT / "PASS1001_13_SPLIT_HEADWORD_GROUPS.tsv",
        codebook_path,
        event_path,
        clause_path,
        OUT / "PASS1002_ONE_PAGE_APPRENTICE_MANUAL.md",
        OUT / "PASS1002_CURRENT_WORKING_THEORY.md",
    ]
    manifest_rows = []
    for path in bound:
        manifest_rows.append({
            "artifact": str(path.relative_to(ROOT)),
            "role": "CURRENT_OUTPUT" if path.parent == OUT else "BOUND_INPUT",
            "data_rows_or_lines": data_rows(path),
            "sha256": sha256(path),
        })
    manifest_path = OUT / "PASS1002_RELEASE_MANIFEST.tsv"
    write_tsv(manifest_path, manifest_rows, list(manifest_rows[0]))

    layer_counts = Counter(str(row["primary_layer_revised"]) for row in revised_events)
    summary = {
        "pass": 1002,
        "codebook_units": len(codebook_rows),
        "portable_roots": 53,
        "root_or_local_sign_units": 56,
        "formula_ligatures": 30,
        "contextual_composition_spellings": 72,
        "local_drug_labels": 16,
        "copy_rules": 1,
        "events": len(revised_events),
        "running_text_events": sum(int(row["event_count"]) for row in revised_clauses),
        "clauses": len(revised_clauses),
        "local_addresses_and_labels": layer_counts["LOCAL_ADDRESS_OR_KENNING"] + layer_counts["DRUG_LABEL_NOMENCLATOR"],
        "layer_counts": dict(sorted(layer_counts.items())),
        "old_specialist_event_labels_remaining": 0,
        "genuine_absent_root_pairs": 7,
        "strongest_new_surface_prediction": "chain",
        "manifest_sha256": sha256(manifest_path),
    }
    (OUT / "PASS1002_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
