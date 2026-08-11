#!/usr/bin/env python3
"""Build a record-level consensus view over the validated drawing segments."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
ATLAS = RESULTS / "drawing_reset_segment_atlas.tsv"
ATLAS_VALIDATION = RESULTS / "drawing_reset_segment_atlas_validation.json"
SPEC = BASE / "CONSENSUS_STRUCTURAL_RECORD_INTERLINEAR_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "consensus_structural_record_interlinear_v1.tsv"
OUT_PACKET = RESULTS / "consensus_structural_record_packet_v1.tsv"
OUT_JSON = RESULTS / "consensus_structural_record_interlinear_v1.json"
OUT_REPORT = RESULTS / "consensus_structural_record_interlinear_v1_report.md"

FROZEN = {
    ATLAS: "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486",
    ATLAS_VALIDATION: "6bca45bd2cdc01eb2c3d6cad6ad8f0999e9fb6b2ecc0237d9552f33316f97442",
}
RESOLVED_TENDENCIES = {
    "FIRST_ASSOCIATED", "LAST_ASSOCIATED", "EDGE_ASSOCIATED", "CORE_ASSOCIATED",
}
POSITION_CODE = {"SINGLE": "S", "FIRST": "F", "CORE": "C", "LAST": "L"}
FIRST_LAST_CODE = {
    "FIRST_ASSOCIATED": "F", "LAST_ASSOCIATED": "L", "UNRESOLVED": "U",
    "INSUFFICIENT": "I", "NOT_IN_PROSE_ATLAS": "N",
}
EDGE_CORE_CODE = {
    "EDGE_ASSOCIATED": "E", "CORE_ASSOCIATED": "C", "UNRESOLVED": "U",
    "INSUFFICIENT": "I", "NOT_IN_PROSE_ATLAS": "N",
}
FIELDS = [
    "record_order", "segment_id", "locus", "page", "section", "currier", "hand",
    "code", "kind", "grammar_scope", "segment_index", "segment_count",
    "physical_line_segment_position", "starts_after_drawing", "ends_before_drawing",
    "group_count", "symbol_count", "family_expression", "zl_sta_expression",
    "it_sta_expression", "rf_sta_expression", "zl_basic_eva_lossy_expression",
    "it_basic_eva_lossy_expression", "rf_basic_eva_lossy_expression",
    "member_exact_agreement_groups", "member_exact_agreement_rate",
    "lossy_eva_exact_agreement_groups", "lossy_eva_exact_agreement_rate",
    "internal_boundaries", "unanimous_internal_boundaries", "boundary_consensus_rate",
    "favored_transitions", "disfavored_transitions", "unresolved_transitions",
    "transition_opportunities", "resolved_transition_rate", "resolved_tendency_slots",
    "tendency_opportunities", "tendency_resolution_rate", "opening_feature_groups",
    "closing_feature_groups", "favored_path_groups", "formal_resolved_units",
    "formal_opportunities", "formal_resolution_rate", "transcription_consensus_status",
    "formal_expression", "packet_eligible", "packet_cell", "packet_rank",
    "packet_selected",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def values(field: str) -> list[str]:
    return [value for value in field.split(";") if value]


def rate(numerator: int, denominator: int, *, empty_complete: bool = False) -> str:
    if denominator == 0:
        if empty_complete:
            return "1.000000"
        raise ValueError("undefined rate")
    return f"{numerator / denominator:.6f}"


def line_segment_position(index: int, count: int) -> str:
    if not 1 <= index <= count:
        raise ValueError("segment index drift")
    if count == 1:
        return "SINGLE"
    if index == 1:
        return "FIRST"
    if index == count:
        return "LAST"
    return "CORE"


def transition_signature(row: dict[str, str]) -> str:
    surface = row["family_surface"]
    opportunities = max(0, len(surface) - 1)
    labels: dict[int, str] = {}
    for field, label in (
        ("favored_transition_hits", "F"),
        ("disfavored_transition_hits", "D"),
        ("unresolved_transition_hits", "U"),
    ):
        for hit in values(row[field]):
            offset_text, pair = hit.split(":", 1)
            offset = int(offset_text)
            if not 1 <= offset <= opportunities:
                raise ValueError("transition offset drift")
            if pair != surface[offset - 1:offset + 1] or offset in labels:
                raise ValueError("transition label drift")
            labels[offset] = label
    if set(labels) != set(range(1, opportunities + 1)):
        raise ValueError("incomplete transition signature")
    return "".join(labels[index] for index in range(1, opportunities + 1)) or "-"


def group_expression(row: dict[str, str]) -> str:
    opening = len(values(row["opening_feature_hits"]))
    closing = len(values(row["closing_feature_hits"]))
    path = row["longest_path_anywhere"]
    if path == "NONE":
        path = "-"
    return (
        f"{POSITION_CODE[row['segment_position']]}:{row['family_surface']}"
        f"{{adj={transition_signature(row)};fl={FIRST_LAST_CODE[row['exact_first_last_label']]};"
        f"ec={EDGE_CORE_CODE[row['exact_edge_core_label']]};o={opening};c={closing};p={path}}}"
    )


def build_record(order: int, rows: list[dict[str, str]]) -> dict[str, object]:
    rows.sort(key=lambda row: int(row["segment_group_index"]))
    count = len(rows)
    if [int(row["segment_group_index"]) for row in rows] != list(range(1, count + 1)):
        raise ValueError("nonconsecutive segment groups")
    if any(int(row["segment_group_count"]) != count for row in rows):
        raise ValueError("segment group count drift")
    invariant = (
        "segment_id", "locus", "page", "section", "currier", "hand", "code", "kind",
        "grammar_scope", "segment_index", "segment_count", "starts_after_drawing",
        "ends_before_drawing",
    )
    if any(any(row[field] != rows[0][field] for field in invariant) for row in rows[1:]):
        raise ValueError("segment metadata drift")

    member_agree = sum(
        row["zl_sta_codes"] == row["it_sta_codes"] == row["rf_sta_codes"] for row in rows
    )
    eva_agree = sum(
        row["zl_basic_eva_lossy"] == row["it_basic_eva_lossy"] == row["rf_basic_eva_lossy"]
        for row in rows
    )
    internal = max(0, count - 1)
    unanimous = sum(int(row["right_boundary_support"]) == 3 for row in rows[:-1])
    favored = sum(len(values(row["favored_transition_hits"])) for row in rows)
    disfavored = sum(len(values(row["disfavored_transition_hits"])) for row in rows)
    unresolved = sum(len(values(row["unresolved_transition_hits"])) for row in rows)
    transition_total = sum(max(0, len(row["family_surface"]) - 1) for row in rows)
    if favored + disfavored + unresolved != transition_total:
        raise ValueError("transition opportunity drift")
    tendency_total = 2 * count
    tendency_resolved = sum(
        row[field] in RESOLVED_TENDENCIES for row in rows
        for field in ("exact_first_last_label", "exact_edge_core_label")
    )
    formal_resolved = favored + disfavored + tendency_resolved
    formal_total = transition_total + tendency_total
    stable = member_agree == count and unanimous == internal
    first = rows[0]
    segment_index, segment_count = int(first["segment_index"]), int(first["segment_count"])
    return {
        "record_order": order, "segment_id": first["segment_id"], "locus": first["locus"],
        "page": first["page"], "section": first["section"], "currier": first["currier"],
        "hand": first["hand"], "code": first["code"], "kind": first["kind"],
        "grammar_scope": first["grammar_scope"], "segment_index": segment_index,
        "segment_count": segment_count,
        "physical_line_segment_position": line_segment_position(segment_index, segment_count),
        "starts_after_drawing": int(first["starts_after_drawing"]),
        "ends_before_drawing": int(first["ends_before_drawing"]), "group_count": count,
        "symbol_count": sum(int(row["symbol_count"]) for row in rows),
        "family_expression": " ".join(row["family_surface"] for row in rows),
        "zl_sta_expression": " | ".join(row["zl_sta_codes"] for row in rows),
        "it_sta_expression": " | ".join(row["it_sta_codes"] for row in rows),
        "rf_sta_expression": " | ".join(row["rf_sta_codes"] for row in rows),
        "zl_basic_eva_lossy_expression": " ".join(row["zl_basic_eva_lossy"] for row in rows),
        "it_basic_eva_lossy_expression": " ".join(row["it_basic_eva_lossy"] for row in rows),
        "rf_basic_eva_lossy_expression": " ".join(row["rf_basic_eva_lossy"] for row in rows),
        "member_exact_agreement_groups": member_agree,
        "member_exact_agreement_rate": rate(member_agree, count),
        "lossy_eva_exact_agreement_groups": eva_agree,
        "lossy_eva_exact_agreement_rate": rate(eva_agree, count),
        "internal_boundaries": internal, "unanimous_internal_boundaries": unanimous,
        "boundary_consensus_rate": rate(unanimous, internal, empty_complete=True),
        "favored_transitions": favored, "disfavored_transitions": disfavored,
        "unresolved_transitions": unresolved, "transition_opportunities": transition_total,
        "resolved_transition_rate": rate(favored + disfavored, transition_total)
        if transition_total else "NA",
        "resolved_tendency_slots": tendency_resolved, "tendency_opportunities": tendency_total,
        "tendency_resolution_rate": rate(tendency_resolved, tendency_total),
        "opening_feature_groups": sum(bool(row["opening_feature_hits"]) for row in rows),
        "closing_feature_groups": sum(bool(row["closing_feature_hits"]) for row in rows),
        "favored_path_groups": sum(row["longest_path_anywhere"] != "NONE" for row in rows),
        "formal_resolved_units": formal_resolved, "formal_opportunities": formal_total,
        "formal_resolution_rate": rate(formal_resolved, formal_total),
        "transcription_consensus_status": (
            "ALL_MEMBER_AND_BOUNDARY_STABLE" if stable else "READING_OR_BOUNDARY_VARIANT"
        ),
        "formal_expression": " | ".join(group_expression(row) for row in rows),
        "packet_eligible": int(first["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= count <= 12 and stable),
        "packet_cell": f"{first['section']}|{first['currier']}", "packet_rank": 0,
        "packet_selected": 0,
    }


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_report(result: dict[str, object]) -> str:
    counts = result["counts"]
    return f"""# Consensus structural record interlinear v1

Status: **{result['status']}**

The record-level table condenses **{counts['groups']:,}** validated source-native
groups into **{counts['records']:,}** unanimous drawing-reset segments across
**{counts['physical_loci']:,}** physical loci and **{counts['pages']}** pages.
It preserves separate ZL/IT/RF renderings and marks
**{counts['consensus_status']['ALL_MEMBER_AND_BOUNDARY_STABLE']:,}** records as
member-and-boundary stable; the remaining
**{counts['consensus_status']['READING_OR_BOUNDARY_VARIANT']:,}** retain explicit
reading or boundary variation.

Formal association evidence resolves **{counts['formal_resolved_units']:,}** of
**{counts['formal_opportunities']:,}** registered transition/tendency
opportunities.  This is annotation coverage, not translation confidence.

The compact inspection packet contains **{counts['packet_selected']}** records
selected deterministically from **{counts['packet_candidates']}** eligible
confirmed-prose records, with at most three per observed section/Currier cell.

The formal expressions expose positions, family surfaces, adjacency labels,
position tendencies, edge features, and favored paths.  They contain zero
English glosses.  No field is a word, part of speech, meaning, sound, morpheme,
lexeme, plaintext, language, cipher, or translation; basic EVA remains an
explicitly lossy display convenience.
"""


def main() -> None:
    outputs = (OUT_TSV, OUT_PACKET, OUT_JSON, OUT_REPORT)
    if any(path.exists() for path in outputs):
        raise SystemExit("refusing to overwrite consensus structural interlinear")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    validation = json.loads(ATLAS_VALIDATION.read_text(encoding="utf-8"))
    if validation.get("status") != "PASS" or validation.get("discrepancies") != []:
        raise SystemExit("drawing-reset atlas validation is not clean")

    grouped: dict[str, list[dict[str, str]]] = {}
    group_rows = 0
    with ATLAS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            grouped.setdefault(row["segment_id"], []).append(row)
            group_rows += 1
    records = [build_record(index, rows) for index, rows in enumerate(grouped.values(), 1)]
    cells: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        if record["packet_eligible"]:
            cells[str(record["packet_cell"])].append(record)
    for cell_records in cells.values():
        cell_records.sort(key=lambda row: (
            -Fraction(int(row["formal_resolved_units"]), int(row["formal_opportunities"])),
            -int(row["group_count"]), str(row["segment_id"]).encode("utf-8"),
        ))
        for rank_value, record in enumerate(cell_records, 1):
            record["packet_rank"] = rank_value
            record["packet_selected"] = int(rank_value <= 3)
    packet = [record for record in records if record["packet_selected"]]

    if group_rows != 23281 or len(records) != 4012 or len({r["locus"] for r in records}) != 3572:
        raise ValueError("record scope drift")
    write_tsv(OUT_TSV, records)
    write_tsv(OUT_PACKET, packet)

    consensus = Counter(str(row["transcription_consensus_status"]) for row in records)
    scopes = Counter(str(row["grammar_scope"]) for row in records)
    selected_cells = Counter(str(row["packet_cell"]) for row in packet)
    result = {
        "experiment": "CONSENSUS_STRUCTURAL_RECORD_INTERLINEAR_V1",
        "status": "PASS_COMPLETE_RECORD_LEVEL_CONSENSUS_STRUCTURAL_RENDER",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER)},
        "counts": {
            "groups": group_rows, "records": len(records),
            "physical_loci": len({row["locus"] for row in records}),
            "pages": len({row["page"] for row in records}),
            "records_by_scope": dict(sorted(scopes.items())),
            "consensus_status": dict(sorted(consensus.items())),
            "formal_resolved_units": sum(int(row["formal_resolved_units"]) for row in records),
            "formal_opportunities": sum(int(row["formal_opportunities"]) for row in records),
            "packet_candidates": sum(int(row["packet_eligible"]) for row in records),
            "packet_selected": len(packet),
            "packet_selected_by_cell": dict(sorted(selected_cells.items())),
        },
        "packet_segments": [str(row["segment_id"]) for row in packet],
        "tsv_sha256": sha(OUT_TSV), "packet_sha256": sha(OUT_PACKET),
        "english_glosses": 0, "nearest_basic_eva_marked_lossy": True,
        "claim_ceiling": (
            "Record-level consensus structural interlinear over already validated source-native "
            "evidence. Position, adjacency, boundary, path, coverage, and packet tags are not "
            "words, parts of speech, meanings, sounds, morphemes, lexemes, plaintext, language, "
            "cipher, or translation; basic EVA is explicitly lossy."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(make_report(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
