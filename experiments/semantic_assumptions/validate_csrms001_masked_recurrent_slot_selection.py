#!/usr/bin/env python3
"""Independent reconstruction of the CSRMS001 filler-blind selection."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "consensus_structural_record_interlinear_v1.tsv"
SOURCE_VALIDATION = RESULTS / "consensus_structural_record_interlinear_v1_validation.json"
METHOD = BASE / "CSRMS001_MASKED_RECURRENT_SLOT_SELECTION_METHOD.md"
PRODUCER = BASE / "build_csrms001_masked_recurrent_slot_selection.py"
RESULT = RESULTS / "csrms001_masked_recurrent_slot_selection.json"
TABLE = RESULTS / "csrms001_masked_recurrent_slot_selection.tsv"
REPORT = RESULTS / "csrms001_masked_recurrent_slot_selection_report.md"
OUT_JSON = RESULTS / "csrms001_masked_recurrent_slot_selection_validation.json"
OUT_REPORT = RESULTS / "csrms001_masked_recurrent_slot_selection_validation_report.md"

RX = re.compile(
    r"^([SFCL]):[^{}]+\{adj=([^;]+);fl=([^;]+);ec=([^;]+);"
    r"o=([0-9]+);c=([0-9]+);p=[^{};]+\}$"
)
FOLIO = re.compile(r"^f([0-9]+)")
LEVELS = ("FULL", "COMPOSITION", "TENDENCY_COUNTS_BINARY", "TENDENCY_EDGE", "EDGE_ONLY")
FIELDS = (
    "occurrence_order", "record_order", "segment_id", "page", "physical_folio",
    "section", "currier", "hand", "record_length", "occupant_ordinal",
    "selected_level", "context_sha256",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canon(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False) + "\n").encode()


def shape(group: tuple[str, str, str, str, int, int], level: str) -> tuple[object, ...]:
    pos, adj, fl, ec, opening, closing = group
    choices = {
        "FULL": (pos, adj, fl, ec, opening, closing),
        "COMPOSITION": (pos, adj.count("F"), adj.count("D"), adj.count("U"),
                        fl, ec, int(opening != 0), int(closing != 0)),
        "TENDENCY_COUNTS_BINARY": (pos, fl, ec, int(opening != 0), int(closing != 0)),
        "TENDENCY_EDGE": (pos, fl, ec),
        "EDGE_ONLY": (pos, ec),
    }
    return choices[level]


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite CSRMS001 validation")
    checks: list[str] = []

    expected_hashes = {
        SOURCE: "7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387",
        SOURCE_VALIDATION: "368d1be6a70c403f77abb5f87e3c0635bea1cf084c6b7408530cbf857c2e1533",
    }
    for path, expected in expected_hashes.items():
        assert digest(path) == expected
    checks.append("frozen_inputs")

    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    accessed = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            if isinstance(node.slice.value, str):
                accessed.add(node.slice.value)
    forbidden = {
        "family_expression", "zl_sta_expression", "it_sta_expression", "rf_sta_expression",
        "zl_basic_eva_lossy_expression", "it_basic_eva_lossy_expression",
        "rf_basic_eva_lossy_expression",
    }
    assert not accessed.intersection(forbidden)
    checks.append("producer_forbidden_field_static_absence")

    eligible = []
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if (row["grammar_scope"], row["transcription_consensus_status"]) != (
                    "CONFIRMED_PROSE", "ALL_MEMBER_AND_BOUNDARY_STABLE"):
                continue
            groups = []
            for expression in row["formal_expression"].split(" | "):
                match = RX.fullmatch(expression)
                assert match
                pos, adj, fl, ec, opening, closing = match.groups()
                groups.append((pos, adj, fl, ec, int(opening), int(closing)))
            assert len(groups) == int(row["group_count"])
            if not 5 <= len(groups) <= 12:
                continue
            match = FOLIO.match(row["page"])
            assert match
            eligible.append((row, groups, int(match.group(1))))
    assert len(eligible) == 641
    assert sum(len(groups) - 4 for _, groups, _ in eligible) == 2191
    checks.append("eligible_scope")

    summaries = []
    chosen = None
    chosen_rows = []
    for level in LEVELS:
        contexts = defaultdict(list)
        for row, groups, folio in eligible:
            for index in range(2, len(groups) - 2):
                key = (row["currier"], len(groups), index + 1,
                       shape(groups[index - 1], level), shape(groups[index + 1], level))
                contexts[key].append({
                    "record_order": int(row["record_order"]), "segment_id": row["segment_id"],
                    "page": row["page"], "physical_folio": folio,
                    "section": row["section"], "currier": row["currier"],
                    "hand": row["hand"], "record_length": len(groups),
                    "occupant_ordinal": index + 1,
                })
        passing = []
        for key, rows in contexts.items():
            nf = len({row["physical_folio"] for row in rows})
            ns = len({row["section"] for row in rows})
            nh = len({row["hand"] for row in rows})
            if len(rows) >= 10 and nf >= 8 and ns >= 2:
                key_bytes = json.dumps(key, separators=(",", ":"), ensure_ascii=False).encode()
                passing.append((-nf, -len(rows), -ns, -nh, key_bytes, key, rows))
        summaries.append({
            "level": level, "unique_contexts": len(contexts),
            "passing_contexts": len(passing),
            "maximum_physical_folios": max(len({r["physical_folio"] for r in rows})
                                           for rows in contexts.values()),
            "maximum_occurrences": max(map(len, contexts.values())),
        })
        if passing:
            passing.sort()
            *_, chosen, chosen_rows = passing[0]
            break
    assert summaries == [
        {"level": "FULL", "unique_contexts": 2183, "passing_contexts": 0,
         "maximum_physical_folios": 2, "maximum_occurrences": 2},
        {"level": "COMPOSITION", "unique_contexts": 2177, "passing_contexts": 0,
         "maximum_physical_folios": 2, "maximum_occurrences": 2},
        {"level": "TENDENCY_COUNTS_BINARY", "unique_contexts": 2018, "passing_contexts": 0,
         "maximum_physical_folios": 4, "maximum_occurrences": 4},
        {"level": "TENDENCY_EDGE", "unique_contexts": 1383, "passing_contexts": 1,
         "maximum_physical_folios": 9, "maximum_occurrences": 12},
    ]
    assert chosen == ("A", 5, 3, ("C", "I", "U"), ("C", "I", "I"))
    checks.append("coarsening_ladder_and_unique_selection")

    key_bytes = json.dumps(chosen, separators=(",", ":"), ensure_ascii=False).encode()
    context_hash = hashlib.sha256(key_bytes).hexdigest()
    assert context_hash == "f3f01eff8d68b91ac36c224c6965a622e817997b56ab4fca507a6041dda0ae96"
    chosen_rows.sort(key=lambda row: (row["record_order"], row["segment_id"]))
    assert len(chosen_rows) == 10
    assert len({row["physical_folio"] for row in chosen_rows}) == 9
    assert {row["section"] for row in chosen_rows} == {"H", "P"}
    checks.append("selected_support")

    with TABLE.open(encoding="utf-8", newline="") as handle:
        actual_table = list(csv.DictReader(handle, delimiter="\t"))
    expected_table = []
    for order, row in enumerate(chosen_rows, 1):
        expected_table.append({k: str(v) for k, v in {
            "occurrence_order": order, **row, "selected_level": "TENDENCY_EDGE",
            "context_sha256": context_hash,
        }.items()})
    assert actual_table == expected_table
    assert tuple(actual_table[0]) == FIELDS
    checks.append("masked_table_exact")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert RESULT.read_bytes() == canon(result)
    assert result["status"] == "PASS_MASKED_RECURRENT_SLOT_SELECTED"
    assert result["coarsening_ladder"] == summaries
    assert result["selection"]["context_sha256"] == context_hash
    assert result["selection"]["occurrences"] == 10
    assert result["filler_identity_accessed"] is False
    assert result["forbidden_fields_accessed"] == []
    assert result["outputs"] == {TABLE.name: digest(TABLE)}
    checks.append("canonical_result_and_bindings")

    assert "**10** occurrences" in REPORT.read_text(encoding="utf-8")
    assert "**9** physical" in REPORT.read_text(encoding="utf-8")
    checks.append("report_claims")

    validation = {
        "experiment": "CSRMS001_MASKED_RECURRENT_SLOT_SELECTION_VALIDATION",
        "status": "PASS_INDEPENDENT_FILLER_BLIND_SELECTION_RECONSTRUCTION",
        "validated_result_sha256": digest(RESULT),
        "validated_table_sha256": digest(TABLE),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed": {"eligible_records": 641, "masked_candidate_slots": 2191,
                            "selected_occurrences": 10, "physical_folios": 9,
                            "sections": 2, "context_sha256": context_hash},
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT_JSON.write_bytes(canon(validation))
    OUT_REPORT.write_text(
        "# CSRMS001 masked selection validation\n\n"
        "Status: **PASS_INDEPENDENT_FILLER_BLIND_SELECTION_RECONSTRUCTION**\n\n"
        f"All **{len(checks)}** checks pass. Independent code reconstructs the 641-record, "
        "2,191-slot coarsening ladder, the unique ten-occurrence selection on nine physical "
        "folios, the masked table, and all result bindings. Static inspection confirms that "
        "the producer does not access family, member, or lossy-EVA fields.\n\n"
        "This validates a masked structural selection only. It supplies no word, part of "
        "speech, morpheme, sound, language, cipher operation, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
