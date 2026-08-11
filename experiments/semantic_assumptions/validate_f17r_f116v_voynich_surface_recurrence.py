#!/usr/bin/env python3
"""Independent reconstruction of the f17r/f116v exact-surface result."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
INPUT = BASE / "results" / "pre_grounding_interlinear.tsv"
RESULT = BASE / "results" / "f17r_f116v_voynich_surface_recurrence.json"
EXPECTED_INPUT_SHA256 = "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43"
TARGETS = ("oror", "sheey", "oteeeon", "oiil")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric(hits: list[tuple[dict[str, str], int]]) -> dict[str, int]:
    return {
        "occurrences": sum(n for _, n in hits),
        "pages": len({r["page"] for r, _ in hits}),
        "physical_loci": len({r["locus"] for r, _ in hits}),
        "reading_rows": len(hits),
    }


assert file_hash(INPUT) == EXPECTED_INPUT_SHA256
with INPUT.open(encoding="utf-8", newline="") as handle:
    source = list(csv.DictReader(handle, delimiter="\t"))
assert len(source) == 15_960

observed = json.loads(RESULT.read_text(encoding="utf-8"))
assert RESULT.read_bytes() == (json.dumps(observed, indent=2, sort_keys=True) + "\n").encode()
assert observed["input"] == {
    "path": "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv",
    "row_count": 15_960,
    "sha256": EXPECTED_INPUT_SHA256,
}

for token in TARGETS:
    hits = []
    for row in source:
        n = row["surface"].split().count(token)
        if n:
            hits.append((row, n))
    actual = observed["token_recurrence"][token]
    assert actual["all"] == metric(hits)
    for edition in ("ZL3b", "IT2a", "RF1b"):
        assert actual["by_edition"][edition] == metric(
            [(row, n) for row, n in hits if row["edition"] == edition]
        )
    scopes = sorted({row["grammar_scope"] for row, _ in hits})
    assert set(actual["by_scope"]) == set(scopes)
    for scope in scopes:
        assert actual["by_scope"][scope] == metric(
            [(row, n) for row, n in hits if row["grammar_scope"] == scope]
        )
    if token != "sheey":
        assert actual["physical_locus_list"] == sorted({row["locus"] for row, _ in hits})

for phrase in ("oror sheey", "oteeeon oiil"):
    pair = phrase.split()
    adjacent = []
    same_row = []
    for row in source:
        words = row["surface"].split()
        n = sum(words[i:i + 2] == pair for i in range(len(words) - 1))
        if n:
            adjacent.append((row, n))
        if all(token in words for token in pair):
            same_row.append((row, 1))
    actual = observed["pair_recurrence"][phrase]
    assert actual["adjacent"] == metric(adjacent)
    assert actual["adjacent_loci"] == sorted({row["locus"] for row, _ in adjacent})
    assert actual["adjacent_whole_row_exact"] is all(
        row["surface"] == phrase for row, _ in adjacent
    )
    assert actual["unordered_same_row"] == metric(same_row)
    assert actual["unordered_same_row_loci"] == sorted({row["locus"] for row, _ in same_row})

for locus, phrase in (("f116v.1", "oror sheey"), ("f17r.13", "oteeeon oiil")):
    rows = [row for row in source if row["locus"] == locus and row["surface"] == phrase]
    assert len(rows) == 2
    assert sorted(row["edition"] for row in rows) == ["RF1b", "ZL3b"]
    assert {(row["grammar_scope"], row["kind"], row["code"]) for row in rows} == {
        ("DIAGNOSTIC_NONPROSE", "L", "@Lx")
    }
    assert observed["target_rows"][locus]["editions_present"] == ["RF1b", "ZL3b"]

assert observed["token_recurrence"]["oror"]["by_scope"]["CONFIRMED_PROSE"]["physical_loci"] == 6
assert observed["token_recurrence"]["sheey"]["by_scope"]["CONFIRMED_PROSE"]["physical_loci"] == 146
assert observed["token_recurrence"]["oteeeon"]["all"]["physical_loci"] == 1
assert observed["token_recurrence"]["oiil"]["all"]["physical_loci"] == 1
assert observed["gates"] == {
    "exact_pairs_recur_elsewhere": False,
    "f116v_both_components_have_confirmed_prose_recurrence": True,
    "f17r_either_component_recurs_elsewhere": False,
    "plain_script_equivalence_authorized": False,
}
assert observed["decision"] == "PASS_F116V_COMPONENT_RECURRENCE_F17R_UNIQUE_HOLD_EQUIVALENCE"

print(json.dumps({
    "checks": 42,
    "decision": "PASS_INDEPENDENT_LITERAL_SURFACE_RECONSTRUCTION",
    "input_sha256": EXPECTED_INPUT_SHA256,
    "result_sha256": file_hash(RESULT),
}, sort_keys=True))
