#!/usr/bin/env python3
"""Independently reconstruct the consensus structural record interlinear."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
ATLAS = RESULTS / "drawing_reset_segment_atlas.tsv"
ATLAS_VALIDATION = RESULTS / "drawing_reset_segment_atlas_validation.json"
SPEC = BASE / "CONSENSUS_STRUCTURAL_RECORD_INTERLINEAR_SPEC.md"
BUILDER = BASE / "build_consensus_structural_record_interlinear.py"
PRODUCER_TSV = RESULTS / "consensus_structural_record_interlinear_v1.tsv"
PRODUCER_PACKET = RESULTS / "consensus_structural_record_packet_v1.tsv"
PRODUCER_JSON = RESULTS / "consensus_structural_record_interlinear_v1.json"
PRODUCER_REPORT = RESULTS / "consensus_structural_record_interlinear_v1_report.md"
VALIDATOR = Path(__file__).resolve()
OUT_JSON = RESULTS / "consensus_structural_record_interlinear_v1_validation.json"
OUT_REPORT = RESULTS / "consensus_structural_record_interlinear_v1_validation_report.md"

FROZEN = {
    ATLAS: "e303f9298e5d76473e7ddd311370e3486cb9997dfb58c05df40c3fb3b4de2486",
    ATLAS_VALIDATION: "6bca45bd2cdc01eb2c3d6cad6ad8f0999e9fb6b2ecc0237d9552f33316f97442",
    SPEC: "d97c9d81188223c22d2f471bd41da84b53a73db099519ab9931f6275602222f3",
    BUILDER: "d5782c75314c257875f535ce736c269776b807005b90bad29d2da803f17cf9e3",
    PRODUCER_TSV: "7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387",
    PRODUCER_PACKET: "25ef54867d564b9e08662dba4b31eb5d8161c56a5748f973d58d360490def291",
    PRODUCER_JSON: "c344c7cf71855f11c5ab3c9cc4efe6a0b5ec7b649483c085a0c957cf116a842f",
    PRODUCER_REPORT: "0e274cd8d76885fddfa21cd02c601d15f4af2733a15fefd7027475d58e052d34",
}
RESOLVED = {"FIRST_ASSOCIATED", "LAST_ASSOCIATED", "EDGE_ASSOCIATED", "CORE_ASSOCIATED"}
POS = {"SINGLE": "S", "FIRST": "F", "CORE": "C", "LAST": "L"}
FL = {"FIRST_ASSOCIATED": "F", "LAST_ASSOCIATED": "L", "UNRESOLVED": "U",
      "INSUFFICIENT": "I", "NOT_IN_PROSE_ATLAS": "N"}
EC = {"EDGE_ASSOCIATED": "E", "CORE_ASSOCIATED": "C", "UNRESOLVED": "U",
      "INSUFFICIENT": "I", "NOT_IN_PROSE_ATLAS": "N"}
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
    "formal_expression", "packet_eligible", "packet_cell", "packet_rank", "packet_selected",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def items(text: str) -> list[str]:
    return [item for item in text.split(";") if item]


def decimal_ratio(numerator: int, denominator: int, vacuous: bool = False) -> str:
    if denominator == 0:
        if vacuous:
            return "1.000000"
        raise AssertionError("zero denominator")
    return f"{numerator / denominator:.6f}"


def segment_position(index: int, count: int) -> str:
    if not 1 <= index <= count:
        raise AssertionError("bad segment coordinate")
    if count == 1:
        return "SINGLE"
    if index == 1:
        return "FIRST"
    if index == count:
        return "LAST"
    return "CORE"


def adjacency(row: dict[str, str]) -> str:
    surface = row["family_surface"]
    total = max(0, len(surface) - 1)
    found: dict[int, str] = {}
    for field, code in (("favored_transition_hits", "F"),
                        ("disfavored_transition_hits", "D"),
                        ("unresolved_transition_hits", "U")):
        for value in items(row[field]):
            raw_index, pair = value.split(":", 1)
            index = int(raw_index)
            assert 1 <= index <= total
            assert pair == surface[index - 1:index + 1]
            assert index not in found
            found[index] = code
    assert set(found) == set(range(1, total + 1))
    return "".join(found[index] for index in range(1, total + 1)) or "-"


def expression(row: dict[str, str]) -> str:
    path = row["longest_path_anywhere"]
    return (
        f"{POS[row['segment_position']]}:{row['family_surface']}"
        f"{{adj={adjacency(row)};fl={FL[row['exact_first_last_label']]};"
        f"ec={EC[row['exact_edge_core_label']]};o={len(items(row['opening_feature_hits']))};"
        f"c={len(items(row['closing_feature_hits']))};p={'-' if path == 'NONE' else path}}}"
    )


def reconstruct(order: int, source: list[dict[str, str]]) -> dict[str, object]:
    source = sorted(source, key=lambda row: int(row["segment_group_index"]))
    n = len(source)
    assert [int(row["segment_group_index"]) for row in source] == list(range(1, n + 1))
    assert all(int(row["segment_group_count"]) == n for row in source)
    fixed = ("segment_id", "locus", "page", "section", "currier", "hand", "code", "kind",
             "grammar_scope", "segment_index", "segment_count", "starts_after_drawing",
             "ends_before_drawing")
    assert all(all(row[field] == source[0][field] for field in fixed) for row in source)

    member = sum(row["zl_sta_codes"] == row["it_sta_codes"] == row["rf_sta_codes"] for row in source)
    eva = sum(row["zl_basic_eva_lossy"] == row["it_basic_eva_lossy"] == row["rf_basic_eva_lossy"]
              for row in source)
    internal = n - 1
    boundaries = sum(int(row["right_boundary_support"]) == 3 for row in source[:-1])
    favored = sum(len(items(row["favored_transition_hits"])) for row in source)
    disfavored = sum(len(items(row["disfavored_transition_hits"])) for row in source)
    unresolved = sum(len(items(row["unresolved_transition_hits"])) for row in source)
    transition_total = sum(max(0, len(row["family_surface"]) - 1) for row in source)
    assert favored + disfavored + unresolved == transition_total
    tendency_total = 2 * n
    tendency = sum(row[field] in RESOLVED for row in source
                   for field in ("exact_first_last_label", "exact_edge_core_label"))
    resolved, opportunities = favored + disfavored + tendency, transition_total + tendency_total
    first = source[0]
    seg_index, seg_count = int(first["segment_index"]), int(first["segment_count"])
    stable = member == n and boundaries == internal
    return {
        "record_order": order, "segment_id": first["segment_id"], "locus": first["locus"],
        "page": first["page"], "section": first["section"], "currier": first["currier"],
        "hand": first["hand"], "code": first["code"], "kind": first["kind"],
        "grammar_scope": first["grammar_scope"], "segment_index": seg_index,
        "segment_count": seg_count, "physical_line_segment_position": segment_position(seg_index, seg_count),
        "starts_after_drawing": int(first["starts_after_drawing"]),
        "ends_before_drawing": int(first["ends_before_drawing"]), "group_count": n,
        "symbol_count": sum(int(row["symbol_count"]) for row in source),
        "family_expression": " ".join(row["family_surface"] for row in source),
        "zl_sta_expression": " | ".join(row["zl_sta_codes"] for row in source),
        "it_sta_expression": " | ".join(row["it_sta_codes"] for row in source),
        "rf_sta_expression": " | ".join(row["rf_sta_codes"] for row in source),
        "zl_basic_eva_lossy_expression": " ".join(row["zl_basic_eva_lossy"] for row in source),
        "it_basic_eva_lossy_expression": " ".join(row["it_basic_eva_lossy"] for row in source),
        "rf_basic_eva_lossy_expression": " ".join(row["rf_basic_eva_lossy"] for row in source),
        "member_exact_agreement_groups": member, "member_exact_agreement_rate": decimal_ratio(member, n),
        "lossy_eva_exact_agreement_groups": eva, "lossy_eva_exact_agreement_rate": decimal_ratio(eva, n),
        "internal_boundaries": internal, "unanimous_internal_boundaries": boundaries,
        "boundary_consensus_rate": decimal_ratio(boundaries, internal, True),
        "favored_transitions": favored, "disfavored_transitions": disfavored,
        "unresolved_transitions": unresolved, "transition_opportunities": transition_total,
        "resolved_transition_rate": decimal_ratio(favored + disfavored, transition_total)
        if transition_total else "NA", "resolved_tendency_slots": tendency,
        "tendency_opportunities": tendency_total,
        "tendency_resolution_rate": decimal_ratio(tendency, tendency_total),
        "opening_feature_groups": sum(bool(row["opening_feature_hits"]) for row in source),
        "closing_feature_groups": sum(bool(row["closing_feature_hits"]) for row in source),
        "favored_path_groups": sum(row["longest_path_anywhere"] != "NONE" for row in source),
        "formal_resolved_units": resolved, "formal_opportunities": opportunities,
        "formal_resolution_rate": decimal_ratio(resolved, opportunities),
        "transcription_consensus_status": "ALL_MEMBER_AND_BOUNDARY_STABLE" if stable
        else "READING_OR_BOUNDARY_VARIANT",
        "formal_expression": " | ".join(expression(row) for row in source),
        "packet_eligible": int(first["grammar_scope"] == "CONFIRMED_PROSE" and 5 <= n <= 12 and stable),
        "packet_cell": f"{first['section']}|{first['currier']}", "packet_rank": 0,
        "packet_selected": 0,
    }


def tsv_bytes(rows: list[dict[str, object]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def report_text(result: dict[str, object]) -> str:
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
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite consensus validation")
    for path, expected in FROZEN.items():
        assert digest(path) == expected, path.name
    atlas_validation = json.loads(ATLAS_VALIDATION.read_text(encoding="utf-8"))
    assert atlas_validation["status"] == "PASS" and atlas_validation["discrepancies"] == []

    grouped: dict[str, list[dict[str, str]]] = {}
    source_count = 0
    with ATLAS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            grouped.setdefault(row["segment_id"], []).append(row)
            source_count += 1
    records = [reconstruct(index, rows) for index, rows in enumerate(grouped.values(), 1)]
    cells: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in records:
        if row["packet_eligible"]:
            cells[str(row["packet_cell"])].append(row)
    for rows in cells.values():
        rows.sort(key=lambda row: (-Fraction(int(row["formal_resolved_units"]),
                                                int(row["formal_opportunities"])),
                                   -int(row["group_count"]),
                                   str(row["segment_id"]).encode("utf-8")))
        for rank, row in enumerate(rows, 1):
            row["packet_rank"] = rank
            row["packet_selected"] = int(rank <= 3)
    packet = [row for row in records if row["packet_selected"]]

    main_bytes, packet_bytes = tsv_bytes(records), tsv_bytes(packet)
    assert main_bytes == PRODUCER_TSV.read_bytes()
    assert packet_bytes == PRODUCER_PACKET.read_bytes()
    scopes = Counter(str(row["grammar_scope"]) for row in records)
    consensus = Counter(str(row["transcription_consensus_status"]) for row in records)
    selected_cells = Counter(str(row["packet_cell"]) for row in packet)
    expected_result = {
        "experiment": "CONSENSUS_STRUCTURAL_RECORD_INTERLINEAR_V1",
        "status": "PASS_COMPLETE_RECORD_LEVEL_CONSENSUS_STRUCTURAL_RENDER",
        "inputs": {path.name: digest(path) for path in (ATLAS, ATLAS_VALIDATION, SPEC, BUILDER)},
        "counts": {"groups": source_count, "records": len(records),
                   "physical_loci": len({row["locus"] for row in records}),
                   "pages": len({row["page"] for row in records}),
                   "records_by_scope": dict(sorted(scopes.items())),
                   "consensus_status": dict(sorted(consensus.items())),
                   "formal_resolved_units": sum(int(row["formal_resolved_units"]) for row in records),
                   "formal_opportunities": sum(int(row["formal_opportunities"]) for row in records),
                   "packet_candidates": sum(int(row["packet_eligible"]) for row in records),
                   "packet_selected": len(packet),
                   "packet_selected_by_cell": dict(sorted(selected_cells.items()))},
        "packet_segments": [str(row["segment_id"]) for row in packet],
        "tsv_sha256": hashlib.sha256(main_bytes).hexdigest(),
        "packet_sha256": hashlib.sha256(packet_bytes).hexdigest(),
        "english_glosses": 0, "nearest_basic_eva_marked_lossy": True,
        "claim_ceiling": ("Record-level consensus structural interlinear over already validated "
                          "source-native evidence. Position, adjacency, boundary, path, coverage, "
                          "and packet tags are not words, parts of speech, meanings, sounds, "
                          "morphemes, lexemes, plaintext, language, cipher, or translation; basic "
                          "EVA is explicitly lossy."),
    }
    expected_json = (json.dumps(expected_result, indent=2, sort_keys=True) + "\n").encode()
    assert expected_json == PRODUCER_JSON.read_bytes()
    expected_report = report_text(expected_result).encode("utf-8")
    assert expected_report == PRODUCER_REPORT.read_bytes()
    assert not any("gloss" in field.lower() for field in FIELDS)

    assertions = {
        "frozen_input_and_producer_hashes": len(FROZEN),
        "source_group_rows_reconstructed": source_count,
        "record_rows_reconstructed": len(records),
        "packet_rows_reconstructed": len(packet),
        "exact_main_tsv_bytes": 1, "exact_packet_tsv_bytes": 1,
        "exact_result_json_bytes": 1, "exact_report_bytes": 1,
        "zero_gloss_columns": 1,
    }
    result = {
        "experiment": "CONSENSUS_STRUCTURAL_RECORD_INTERLINEAR_V1_VALIDATION",
        "status": "PASS_INDEPENDENT_RECORD_LEVEL_CONSENSUS_RECONSTRUCTION",
        "validated_experiment": expected_result["experiment"],
        "inputs": {path.name: digest(path) for path in (*FROZEN, VALIDATOR)},
        "assertions": assertions, "check_count": sum(assertions.values()),
        "discrepancies": [], "reconstructed_counts": expected_result["counts"],
        "source_result_sha256": digest(PRODUCER_JSON),
        "source_report_sha256": digest(PRODUCER_REPORT),
        "english_glosses": 0,
        "claim_ceiling": expected_result["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Consensus structural record interlinear v1 validation

Status: **{result['status']}**

Independent code reconstructed all **{source_count:,}** source groups,
**{len(records):,}** record rows, and **{len(packet)}** packet rows.  The main
TSV, packet TSV, producer JSON, and report match byte-for-byte with zero
discrepancies across **{result['check_count']:,}** checks.

This validates the descriptive consolidation only.  The formal fields and
packet are not words, parts of speech, meanings, plaintext, language, cipher,
or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": result["check_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
