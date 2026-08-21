#!/usr/bin/env python3
"""Render the selected translation at grammar-derived field and record level."""

from __future__ import annotations

import csv
import json
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
V16 = HERE.parent / "sidequest_theory_candidates_v16"
V25 = HERE.parent / "sidequest_theory_candidates_v25"
PROSE = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    meta = [row for row in read(V16 / "V16_R2_COMPLETE_TRANSLATION_LEDGER.tsv")
            if row["scope"] == "PROSE_GDT327"]
    ledger = [row for row in read(V25 / "V25_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
              if row["page"] in PROSE]
    assert len(meta) == len(ledger) == 381

    # Match only within already authorized loci; no spelling decomposition.
    metadata = {}
    for page in PROSE:
        loci = sorted({row["locus"] for row in ledger if row["page"] == page},
                      key=lambda value: int(value.split(".")[-1]))
        for locus in loci:
            current = [row for row in ledger if row["locus"] == locus]
            source = [row for row in meta if row["locus"] == locus]
            assert [row["surface"] for row in current] == [row["surface"] for row in source]
            for target, structure in zip(current, source):
                metadata[target["exact_tuple_id"], target["source_event_serial"]] = structure

    fields: OrderedDict[tuple[str, str, str, str], list[dict[str, str]]] = OrderedDict()
    for row in ledger:
        structure = metadata[row["exact_tuple_id"], row["source_event_serial"]]
        key = (row["page"], row["record"], row["locus"], structure["field_ordinal"])
        fields.setdefault(key, []).append({"meaning": row["default_English"],
                                           "surface": row["surface"],
                                           "closure": structure["closure"]})
    assert len(fields) == 135

    field_rows = []
    for (page, record, locus, ordinal), rows in fields.items():
        closure = rows[-1]["closure"]
        boundary = {"DY": "COMMIT_LOCAL_STEP", "B3": "COMMIT_RECORD_OR_MAJOR_STEP",
                    "OPEN": "CONTINUE_WITHOUT_FORCED_SENTENCE_END"}[closure]
        literal = "; ".join(row["meaning"] for row in rows)
        field_rows.append({
            "page": page, "record": record, "locus": locus,
            "field_ordinal": ordinal, "visible_source_field": " ".join(
                row["surface"] for row in rows),
            "closure": closure, "boundary_reading": boundary,
            "complete_field_translation": literal,
            "editorial_sentence_rendering": (
                literal + (". [step committed]" if closure == "DY" else
                           ". [major step committed]" if closure == "B3" else
                           "; [continue]")),
        })
    write(HERE / "V26_COMPLETE_135_FIELD_TRANSLATION.tsv", field_rows)

    records: OrderedDict[tuple[str, str], list[dict[str, str]]] = OrderedDict()
    for row in field_rows:
        records.setdefault((row["page"], row["record"]), []).append(row)
    assert len(records) == 11
    record_rows = []
    for (page, record), rows in records.items():
        record_rows.append({
            "page": page, "record": record,
            "field_count": str(len(rows)),
            "committed_step_count": str(sum(row["closure"] in {"DY", "B3"} for row in rows)),
            "open_continuation_count": str(sum(row["closure"] == "OPEN" for row in rows)),
            "complete_record_translation": " ".join(
                row["editorial_sentence_rendering"] for row in rows),
            "register_reading": (
                "ILLUSTRATED_CONTINUOUS_ARTICLE" if page in {"f10r", "f11r", "f55v", "f56r"}
                else "COMMITTED_APPLICATION_WORKSHEET"
            ),
        })
    write(HERE / "V26_COMPLETE_11_RECORD_TRANSLATION.tsv", record_rows)

    result = {
        "schema": "SIDEQUEST_V26_FIELD_RECORD_TRANSLATION_V1", "status": "PASS",
        "prose_events": 381, "grammar_fields": 135, "records": 11,
        "herbal_fields": sum(row["page"] in {"f10r", "f11r", "f55v", "f56r"}
                             for row in field_rows),
        "bio_fields": sum(row["page"] in {"f81v", "f82r", "f83r"} for row in field_rows),
        "dy_or_b3_committed_fields": sum(row["closure"] in {"DY", "B3"} for row in field_rows),
        "open_fields": sum(row["closure"] == "OPEN" for row in field_rows),
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
    }
    (HERE / "V26_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
