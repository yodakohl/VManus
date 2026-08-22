#!/usr/bin/env python3
"""Build R4's independent physical-line/statement audit for V61."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V59 = ROOT / "experiments/yolo/sidequest_theory_candidates_v59"
V60 = ROOT / "experiments/yolo/sidequest_theory_candidates_v60"
FIELDS_IN = V59 / "V59_R1_FINAL_135_FIELD_EDITION.tsv"
EVENTS_IN = V60 / "V60_SELECTED_381_EVENT_LEDGER.tsv"

C = "CONTINUE_SAME_CLAUSE"
S = "START_NEW_CLAUSE"
R = "RESUME_ACTIVE_ITEM"
N = "NEXT_PARALLEL_CELL"
U = "UNRESOLVED"

# Frozen before sibling V61 outputs were read.  Keys are record-unit and
# consecutive physical loci.  The classification is a source-text hypothesis,
# never a new card meaning.
BOUNDARY_CLASS = {
    ("H1", "f10r.2", "f10r.5"): C,
    ("H2", "f10r.6", "f10r.8"): C,
    ("H2", "f10r.8", "f10r.9"): C,
    ("H3", "f11r.1", "f11r.4"): S,
    ("H3", "f11r.4", "f11r.7"): C,
    ("H4", "f55v.5", "f55v.11"): S,
    ("H5", "f56r.5", "f56r.7"): C,
    ("H5", "f56r.7", "f56r.8"): C,
    ("H5", "f56r.8", "f56r.12"): S,
    ("H5", "f56r.12", "f56r.13"): C,
    ("H5", "f56r.13", "f56r.18"): C,
    ("H5", "f56r.18", "f56r.19"): C,
    ("B1", "f81v.2", "f81v.7"): R,
    ("B1", "f81v.7", "f81v.17"): N,
    ("B1", "f81v.17", "f81v.18"): N,
    ("B1", "f81v.18", "f81v.21"): N,
    ("B1", "f81v.21", "f81v.24"): N,
    ("B1", "f81v.24", "f81v.27"): N,
    ("B2", "f82r.2", "f82r.3"): N,
    ("B2", "f82r.3", "f82r.4"): C,
    ("B2", "f82r.4", "f82r.7"): N,
    ("B2", "f82r.7", "f82r.19"): N,
    ("B2", "f82r.19", "f82r.23"): N,
    ("B2", "f82r.23", "f82r.26"): N,
    ("B2", "f82r.26", "f82r.27"): N,
    ("B3", "f83r.3", "f83r.6"): N,
    ("B3", "f83r.6", "f83r.8"): C,
    ("B3", "f83r.8", "f83r.11"): S,
    ("B3", "f83r.11", "f83r.14"): N,
    ("B3", "f83r.14", "f83r.15"): C,
    ("B3", "f83r.15", "f83r.16"): N,
    ("B3", "f83r.16", "f83r.20"): N,
    ("B3", "f83r.20", "f83r.22"): N,
    ("B3", "f83r.22", "f83r.24"): N,
    ("B4", "f83r.25", "f83r.26"): C,
    ("B4", "f83r.26", "f83r.27"): N,
    ("B4", "f83r.27", "f83r.28"): N,
    ("B4", "f83r.28", "f83r.35"): S,
    ("B4", "f83r.35", "f83r.37"): C,
    ("B4", "f83r.37", "f83r.38"): S,
    ("B4", "f83r.38", "f83r.39"): S,
    ("B4", "f83r.39", "f83r.41"): C,
    ("B4", "f83r.41", "f83r.44"): S,
    ("B5", "f83r.47", "f83r.48"): C,
    ("B5", "f83r.48", "f83r.49"): C,
    ("B6", "f83r.52", "f83r.54"): C,
}


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    fields = read_tsv(FIELDS_IN)
    events = read_tsv(EVENTS_IN)
    events_by_field = defaultdict(list)
    for row in events:
        events_by_field[row["field_id"]].append(row)
    fields_by_record = defaultdict(list)
    for row in fields:
        fields_by_record[row["record_unit_id"]].append(row)

    boundary_rows = []
    statement_rows = []
    assignment_rows = []
    observed_keys = set()

    for record_unit, record_fields in fields_by_record.items():
        loci = []
        fields_by_locus = defaultdict(list)
        for field in record_fields:
            if field["locus"] not in fields_by_locus:
                loci.append(field["locus"])
            fields_by_locus[field["locus"]].append(field)

        for left, right in zip(loci, loci[1:]):
            key = (record_unit, left, right)
            observed_keys.add(key)
            category = BOUNDARY_CLASS[key]
            left_fields = fields_by_locus[left]
            right_fields = fields_by_locus[right]
            left_events = events_by_field[left_fields[-1]["field_id"]]
            right_events = events_by_field[right_fields[0]["field_id"]]
            left_surface = left_events[-1]["surface"]
            right_surface = right_events[0]["surface"]
            exact_carry = left_events[-1]["joint_tuple_id"] == right_events[0]["joint_tuple_id"]
            if exact_carry:
                rationale = "Exact atomic card repeats at line edge and next line onset; read once as anticipatory copy/catchword before testing ordinary repetition."
                confidence = "HIGH"
            elif category == C:
                rationale = "Open or argument-incomplete source expansion is most economical as the same clause after physical reflow."
                confidence = "MEDIUM"
            elif category == R:
                rationale = "The next line explicitly reopens the previous active working item rather than introducing a new owner."
                confidence = "MEDIUM_HIGH"
            elif category == N:
                rationale = "Bio stencil changes to another complete or parallel work cell; active page owner persists but source transaction advances."
                confidence = "MEDIUM"
            elif category == S:
                rationale = "A completed preparation or topic phase precedes a new source clause; the record owner remains unchanged."
                confidence = "MEDIUM_LOW"
            else:
                rationale = "Available structure does not choose continuation or restart."
                confidence = "LOW"
            boundary_rows.append({
                "record_unit_id": record_unit,
                "left_locus": left,
                "right_locus": right,
                "left_last_field": left_fields[-1]["field_id"],
                "left_last_field_closure": left_fields[-1]["closure_status"],
                "left_edge_surface": left_surface,
                "right_edge_surface": right_surface,
                "exact_joint_tuple_edge_repeat": str(exact_carry).upper(),
                "classification": category,
                "confidence": confidence,
                "rationale": rationale,
            })

        statement_number = 0
        current_statement = None
        for locus_index, locus in enumerate(loci):
            if locus_index == 0:
                statement_number += 1
            else:
                category = BOUNDARY_CLASS[(record_unit, loci[locus_index - 1], locus)]
                if category != C:
                    statement_number += 1
            current_statement = f"{record_unit}_S{statement_number:02d}"
            for field in fields_by_locus[locus]:
                assignment_rows.append({
                    "field_id": field["field_id"],
                    "record_unit_id": record_unit,
                    "locus": locus,
                    "statement_id": current_statement,
                    "field_ordinal_in_record": field["field_ordinal_in_record"],
                    "closure_status": field["closure_status"],
                })

        assigned_by_statement = defaultdict(list)
        for row in assignment_rows:
            if row["record_unit_id"] == record_unit:
                assigned_by_statement[row["statement_id"]].append(row["field_id"])
        field_lookup = {row["field_id"]: row for row in record_fields}
        for statement_id, field_ids in assigned_by_statement.items():
            selected = []
            surfaces = []
            expansions = []
            loci_here = []
            for field_id in field_ids:
                field = field_lookup[field_id]
                surfaces.append(field["surface_sequence"])
                expansions.append(field["LOCAL_IATROMEDICAL_EXPANSION"])
                if field["locus"] not in loci_here:
                    loci_here.append(field["locus"])
                for event in events_by_field[field_id]:
                    value = event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
                    if value != "UNKNOWN":
                        selected.append(value)
            statement_rows.append({
                "statement_id": statement_id,
                "record_unit_id": record_unit,
                "page": record_fields[0]["page"],
                "loci": "|".join(loci_here),
                "crosses_physical_line": str(len(loci_here) > 1).upper(),
                "field_ids": "|".join(field_ids),
                "surface_fields": " || ".join(surfaces),
                "selected_short_card_skeleton": " | ".join(selected) if selected else "NO_SELECTED_SHORT_CARD",
                "creative_source_clause": " ; ".join(expansions),
                "strongest_segmentation_rival": "ONE_STATEMENT_PER_PHYSICAL_LOCUS" if len(loci_here) > 1 else "MERGE_WITH_NEIGHBOURING_LOCUS",
            })

    outputs = {
        "boundaries": HERE / "V61_R4_46_PHYSICAL_LINE_BOUNDARIES.tsv",
        "statements": HERE / "V61_R4_SOURCE_STATEMENT_MAP.tsv",
        "assignments": HERE / "V61_R4_135_FIELD_STATEMENT_ASSIGNMENT.tsv",
    }
    write_tsv(outputs["boundaries"], boundary_rows, list(boundary_rows[0]))
    write_tsv(outputs["statements"], statement_rows, list(statement_rows[0]))
    write_tsv(outputs["assignments"], assignment_rows, list(assignment_rows[0]))
    checks = {
        "all_46_line_boundaries": len(boundary_rows) == 46,
        "boundary_key_contract_exact": observed_keys == set(BOUNDARY_CLASS),
        "all_135_fields_assigned_once": len(assignment_rows) == 135 and len({r["field_id"] for r in assignment_rows}) == 135,
        "all_11_records": len({r["record_unit_id"] for r in assignment_rows}) == 11,
        "at_least_one_cross_line_statement": any(r["crosses_physical_line"] == "TRUE" for r in statement_rows),
        "f82_exact_carry_preserved": any(r["left_locus"] == "f82r.3" and r["right_locus"] == "f82r.4" and r["exact_joint_tuple_edge_repeat"] == "TRUE" and r["classification"] == C for r in boundary_rows),
        "no_f84": all(not r["page"].startswith("f84") for r in statement_rows),
    }
    validation = {
        "schema": "SIDEQUEST_V61_R4_LINE_CONTINUATION_AUDIT_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "boundaries": len(boundary_rows),
            "statements": len(statement_rows),
            "cross_line_statements": sum(r["crosses_physical_line"] == "TRUE" for r in statement_rows),
            "boundary_classes": {c: sum(r["classification"] == c for r in boundary_rows) for c in (C, S, R, N, U)},
        },
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (FIELDS_IN, EVENTS_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs.values()},
    }
    (HERE / "V61_R4_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit("V61 R4 validation failed")


if __name__ == "__main__":
    main()
