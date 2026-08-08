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
    observed = Counter((row["edition"], row["locus"]) for row in rows)
    assert all(count == 1 for count in observed.values())
    for edition in SOURCES:
        assert {key for key in observed if key[0] == edition} == expected[edition]
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

    print(json.dumps({
        "status": "PRE_GROUNDING_PACKAGE_VALIDATED",
        "interlinear_rows": len(rows),
        "physical_loci": len(loci),
        "root_types": len(roots),
        "tuple_types": len(tuples),
        "relations": len(relations),
        "confirmed_edges": len(allowed_edges),
        "english_lexical_glosses": 0,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
