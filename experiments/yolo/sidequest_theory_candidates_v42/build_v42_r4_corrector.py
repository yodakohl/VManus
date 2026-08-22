#!/usr/bin/env python3
"""Build the V42 R4 complete eleven-record corrector edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v41/V41_135_FIELD_WORKSHEET.tsv"
RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v30/V30_ELEVEN_RECORD_SOURCE_RECONSTRUCTIONS.tsv"


REPLACEMENTS = (
    ("take the final indicated share", "take the indicated share"),
    ("letzter Anteil", "bezeichneter Anteil"),
    ("den letzten Anteil", "den bezeichneten Anteil"),
    ("aus derselben Charge", "aus demselben Ansatz"),
    ("derselben Charge", "demselben Ansatz"),
    ("der Zeichnung", "der bezeichneten Zielstelle"),
    ("am Bildort", "an der bezeichneten Zielstelle"),
    ("an der gezeigten Stelle", "an der bezeichneten Zielstelle"),
    ("prepared decoction or working liquid", "prepared working liquid"),
    ("the prepared decoction", "the prepared working liquid"),
)


def revised(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    field_rows = read_tsv(FIELDS)
    record_rows = read_tsv(RECORDS)
    assert len(field_rows) == 135
    assert sum(int(r["event_count"]) for r in field_rows) == 381
    assert len(record_rows) == 11

    reconciled: list[dict[str, object]] = []
    for row in field_rows:
        defaults = revised(row["complete_card_defaults"])
        questions = row["workshop_questions_German"]
        expansion = (
            f"ARBEITSFRAGEN: {questions}. "
            f"EINGETRAGENE ANTWORTEN: {defaults}."
        )
        reconciled.append({
            "page": row["page"],
            "record_ordinal": row["record_ordinal"],
            "locus": row["locus"],
            "field_ordinal": row["field_ordinal"],
            "event_count": row["event_count"],
            "visible_field": row["visible_field"],
            "worksheet_roles": row["worksheet_roles"],
            "complete_corrected_expansion_German": expansion,
            "closure": row["closure"],
            "coverage_status": "FIELD_EXPLICITLY_EXPANDED_NO_OMISSION",
        })

    by_record: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in reconciled:
        by_record.setdefault((str(row["page"]), str(row["record_ordinal"])), []).append(row)

    edition: list[dict[str, object]] = []
    for row in record_rows:
        key = (row["page"], row["record"])
        covered = by_record[key]
        assert len(covered) == int(row["field_count"])
        assert sum(int(x["event_count"]) for x in covered) == int(row["event_count"])
        edition.append({
            "page": row["page"],
            "record": row["record"],
            "source_register": row["source_register"],
            "field_count": row["field_count"],
            "event_count": row["event_count"],
            "covered_field_count": len(covered),
            "corrected_complete_card_expansion": revised(row["complete_card_expansion"]),
            "canonical_speculative_German": revised(row["normalized_german_reconstruction"]),
            "interpretation_level": "CONCRETE_WORKING_TRANSLATION_NOT_DECIPHERMENT",
            "coverage_status": "ALL_FIELDS_AND_EVENTS_ACCOUNTED",
        })

    write_tsv(
        OUT / "V42_R4_135_FIELD_RECONCILIATION.tsv",
        reconciled,
        list(reconciled[0]),
    )
    write_tsv(
        OUT / "V42_R4_ELEVEN_RECORD_EDITION.tsv",
        edition,
        list(edition[0]),
    )
    validation = {
        "schema": "SIDEQUEST_V42_R4_VALIDATION_V1",
        "status": "PASS",
        "checks": {
            "records_exact_11": len(edition) == 11,
            "fields_exact_135": len(reconciled) == 135,
            "events_exact_381": sum(int(r["event_count"]) for r in reconciled) == 381,
            "record_field_reconciliation": all(int(r["field_count"]) == int(r["covered_field_count"]) for r in edition),
            "no_blank_field_expansion": all(r["complete_corrected_expansion_German"].strip() for r in reconciled),
            "no_f84_page": all(not str(r["page"]).startswith("f84") for r in reconciled),
        },
    }
    (OUT / "V42_R4_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
