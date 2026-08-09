#!/usr/bin/env python3
"""Integrity and provenance checks for the clean pre-grounding package."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
SEMANTIC = HERE.parent
BASE = SEMANTIC.parents[1]
ARCHIVE = BASE / "archive_pre_reset_2026-08-06" / "semantic_assumptions"
RESULTS = SEMANTIC / "results"
MANIFEST = RESULTS / "pre_grounding_package_manifest.json"
COVERAGE = RESULTS / "pre_grounding_surface_coverage_audit.json"
RESIDUAL = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
sys.path.insert(0, str(ARCHIVE))

from common import parse_rows  # noqa: E402


SOURCES = {
    "ZL3b": BASE / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": BASE / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": BASE / "transcription" / "sources" / "RF1b-e.txt",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or ()), list(reader)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    for name, item in manifest["outputs"].items():
        path = RESULTS / name
        assert path.exists(), name
        assert sha256(path) == item["sha256"], name
        assert path.stat().st_size == item["bytes"], name

    fields, rows = load_tsv(RESULTS / "pre_grounding_interlinear.tsv")
    forbidden_fields = {"translation", "gloss", "meaning", "contextual_overlay", "read"}
    assert not (set(fields) & forbidden_fields), set(fields) & forbidden_fields
    expected = {
        edition: {(edition, row.locus) for row in parse_rows(path)}
        for edition, path in SOURCES.items()
    }
    source_rows = {
        (edition, row.locus): row
        for edition, path in SOURCES.items()
        for row in parse_rows(path)
    }
    observed = Counter((row["edition"], row["locus"]) for row in rows)
    assert all(count == 1 for count in observed.values())
    for edition in SOURCES:
        assert {key for key in observed if key[0] == edition} == expected[edition]
        assert sha256(SOURCES[edition]) == manifest["inputs"][edition]
    for row in rows:
        source = source_rows[(row["edition"], row["locus"])]
        assert row["surface"] == " ".join(source.words)
        assert row["page"] == source.page
        assert row["section"] == source.section
        assert row["currier"] == source.language
        assert row["hand"] == source.hand
        assert row["code"] == source.code
        assert row["kind"] == source.kind
        expected_scope = (
            "CONFIRMED_PROSE"
            if source.kind == "P" and source.language in {"A", "B"}
            else "DIAGNOSTIC_NONPROSE"
        )
        assert row["grammar_scope"] == expected_scope
        node_count = len(row["formal_interlinear"].split(" | ")) if row["formal_interlinear"] else 0
        assert int(row["word_count"]) == node_count
        assert len(row["root_sequence"].split()) == node_count
        assert len(row["role_sequence"].split()) == node_count
    assert len(rows) == manifest["interlinear_rows"]
    assert Counter(row["grammar_scope"] for row in rows) == Counter(manifest["scope_counts"])

    allowed_edges = set(manifest["confirmed_role_edges"])
    for row in rows:
        for value in filter(None, row["confirmed_edges"].split(";")):
            edge = value.split(":", 1)[1]
            assert edge in allowed_edges, value
        if row["grammar_scope"] != "CONFIRMED_PROSE":
            assert not row["confirmed_edges"]
            assert not row["line_carrier"]

    _locus_fields, loci = load_tsv(RESULTS / "pre_grounding_locus_atlas.tsv")
    assert len(loci) == manifest["physical_loci"]
    assert len({row["locus"] for row in loci}) == len(loci)
    assert Counter(row["reading_status"] for row in loci) == Counter(manifest["reading_status_counts"])

    _root_fields, roots = load_tsv(RESULTS / "pre_grounding_root_atlas.tsv")
    _tuple_fields, tuples = load_tsv(RESULTS / "pre_grounding_tuple_atlas.tsv")
    _relation_fields, relations = load_tsv(RESULTS / "pre_grounding_relation_atlas.tsv")
    assert len(roots) == manifest["root_types"]
    assert len(tuples) == manifest["tuple_types"]
    assert len(relations) == manifest["adjacent_tuple_relations"]
    assert sum(row["hybrid_class"] == "SUPPORTED_COMPONENT" for row in roots) == 21
    assert sum(row["hybrid_class"] == "SPARSE_CORE_ATOM" for row in roots) == 13

    assert coverage["status"] == "PASS_COMPLETE_SURFACE_PARTIAL_FORMAL_COVERAGE"
    assert coverage["decision"] == "CORRECT_PRE_GROUNDING_COMPLETENESS_CLAIM"
    assert coverage["inputs"]["experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"] == sha256(
        RESULTS / "pre_grounding_interlinear.tsv"
    )
    assert coverage["totals"] == {
        "affected_rows": 2833,
        "omitted_characters": 5237,
        "omitted_tokens": 3838,
        "parsed_characters": 568072,
        "parsed_nodes": 114173,
        "rows": 15960,
        "surface_characters": 573309,
        "surface_tokens": 118011,
    }
    assert coverage["residual_atlas"] == {
        "path": "experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv",
        "rows": 2833,
        "sha256": sha256(RESIDUAL),
    }

    print(json.dumps({
        "status": "PRE_GROUNDING_PACKAGE_VALIDATED_COMPLETE_SURFACE_PARTIAL_FORMAL",
        "interlinear_rows": len(rows),
        "physical_loci": len(loci),
        "root_types": len(roots),
        "tuple_types": len(tuples),
        "relations": len(relations),
        "confirmed_edges": len(allowed_edges),
        "formal_coverage": {
            "surface_tokens": 118011,
            "parsed_nodes": 114173,
            "unparsed_surface_tokens": 3838,
            "affected_rows": 2833,
        },
        "english_lexical_glosses": 0,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
