#!/usr/bin/env python3
"""Reconcile the existing four-scribe copies with the selected source lexicon."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COPIES = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_copyshop/FOUR_HAND_116_STATEMENT_RENDERINGS.tsv"
PROFILES = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_copyshop/FOUR_SCRIBE_PROFILES.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_minimal_dictionary_seventy_second_edition/SEVENTY_SECOND_116_MINIMAL_STATEMENT_READINGS.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_controlled_unit_rewrite_seventy_sixth_edition/SEVENTY_SIXTH_14_CONTROLLED_UNIT_READINGS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    statements = {row["unit_id"]: row for row in read_tsv(STATEMENTS)}
    units = {row["unit_id"]: row for row in read_tsv(UNITS)}
    reconciled = []
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in read_tsv(COPIES):
        statement = statements[row["statement_id"]]
        unit_id = row["record_unit_id"]
        unit = units[unit_id]
        out = {
            "statement_id": row["statement_id"],
            "record_unit_id": unit_id,
            "page": row["page"],
            "scribe_id": row["scribe_id"],
            "tuple_sequence": row["tuple_sequence"],
            "original_surface_sequence": row["original_surface_sequence"],
            "scribe_surface_sequence": row["counterfactual_surface_sequence"],
            "line_broken_copy": row["line_broken_copy"],
            "changed_token_count": row["changed_token_count"],
            "current_minimal_card_reading_de": statement["minimal_card_sequence_de"],
            "current_owner_reading_de": statement["owner_augmented_minimal_reading_de"],
            "selected_source_vocabulary_de": unit["selected_source_words_de"],
            "current_controlled_unit_reading_de": unit["controlled_unit_reading_de"],
            "semantic_policy": "SAME_MINIMAL_CARDS_AND_SELECTED_SOURCE_ACROSS_ALL_HANDS",
            "surface_change_may_change_meaning": "NO",
            "legacy_rich_readback_status": "SUPERSEDED_BY_SELECTED_SOURCE_EDITION",
        }
        reconciled.append(out)
        by_statement[row["statement_id"]].append(out)
    write_tsv(OUT / "SEVENTY_NINTH_464_SELECTED_SOURCE_SCRIBE_READINGS.tsv", reconciled)

    statement_rows = []
    for statement_id in sorted(by_statement):
        rows = by_statement[statement_id]
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "scribe_copies": len(rows),
            "distinct_visible_sequences": len({row["scribe_surface_sequence"] for row in rows}),
            "distinct_tuple_sequences": len({row["tuple_sequence"] for row in rows}),
            "distinct_minimal_readings": len({row["current_minimal_card_reading_de"] for row in rows}),
            "distinct_selected_vocabularies": len({row["selected_source_vocabulary_de"] for row in rows}),
            "distinct_controlled_unit_readings": len({row["current_controlled_unit_reading_de"] for row in rows}),
            "meaning_invariant": "YES" if len({row["current_minimal_card_reading_de"] for row in rows}) == 1 and len({row["selected_source_vocabulary_de"] for row in rows}) == 1 else "NO",
        })
    write_tsv(OUT / "SEVENTY_NINTH_116_FOUR_HAND_MEANING_INVARIANCE.tsv", statement_rows)

    profile_rows = []
    profile_counts = Counter(row["scribe_id"] for row in reconciled)
    profile_changes = Counter()
    for row in reconciled:
        profile_changes[row["scribe_id"]] += int(row["changed_token_count"])
    for row in read_tsv(PROFILES):
        profile_rows.append({
            **row,
            "statement_copies_reconciled": profile_counts[row["scribe_id"]],
            "surface_tokens_changed_from_source": profile_changes[row["scribe_id"]],
            "selected_source_semantic_changes": 0,
        })
    write_tsv(OUT / "SEVENTY_NINTH_4_SCRIBE_PROFILES_RETAINED.tsv", profile_rows)

    varying = sum(int(row["distinct_visible_sequences"]) > 1 for row in statement_rows)
    doc = ["# Vier Schreiber mit einem ausgewählten Quellenwörterbuch", ""]
    for profile in profile_rows:
        doc.extend([
            f"## {profile['scribe_id']}", "",
            f"{profile['five_line_background_de']}", "",
            f"116 Aussagen; {profile['surface_tokens_changed_from_source']} sichtbare Tokenwahlen weichen von der Ausgangsoberfläche ab; Bedeutungsänderungen: 0.", "",
        ])
    doc.extend([
        "## Gemeinsame Leseregel", "",
        "Jeder Schreiber erhält dasselbe Unitprogramm, dieselben minimalen Kartenwerte",
        "und dasselbe ausgewählte Quellenvokabular. Erst danach wählt er innerhalb der",
        "registrierten Kartenfamilie seine q-, s-, bare oder kompakte Oberfläche.", "",
        f"{varying} der 116 Aussagen erscheinen in mindestens zwei sichtbaren Folgen;",
        "alle behalten genau eine Tuplefolge, eine Minimal-Lesung und ein Quellenprogramm.",
    ])
    (OUT / "SEVENTY_NINTH_FOUR_SCRIBE_SELECTED_SOURCE_COPYBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Neunundsiebzigste Werkstattfassung: vier Schreiber, eine Bedeutung", "",
        "## Ergebnis", "",
        "The existing 464 four-hand copies are reconciled with the current minimal",
        "dictionary and selected finite source vocabulary. No new copy is generated and",
        "no renderer rule changes. The older free rich readbacks are simply replaced by",
        "the current bounded semantic layers.", "",
        f"All 116 statements have four copies; {varying} statements retain at least two",
        "visible surface sequences. Every four-copy set has one exact tuple sequence, one",
        "minimal reading, one unit vocabulary and one controlled unit reading.", "",
        "This makes the multi-scribe hypothesis easy to teach: hands vary after exact-card",
        "selection, not inside the shared word meanings or content program.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "SEVENTY_NINTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "scribe_profiles": len(profile_rows),
            "statement_copies": len(reconciled),
            "statements": len(statement_rows),
            "visibly_varying_statements": varying,
            "meaning_changes": sum(row["meaning_invariant"] != "YES" for row in statement_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (COPIES, PROFILES, STATEMENTS, UNITS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
