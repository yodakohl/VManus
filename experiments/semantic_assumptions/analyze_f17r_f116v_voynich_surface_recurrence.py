#!/usr/bin/env python3
"""Reconstruct the bounded f17r/f116v literal-surface recurrence result."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
INPUT = BASE / "results" / "pre_grounding_interlinear.tsv"
EXPECTED_INPUT_SHA256 = "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43"
TOKENS = ("oror", "sheey", "oteeeon", "oiil")
PAIRS = (("oror", "sheey"), ("oteeeon", "oiil"))
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(hits: list[tuple[dict[str, str], int]]) -> dict[str, int]:
    return {
        "occurrences": sum(number for _, number in hits),
        "pages": len({row["page"] for row, _ in hits}),
        "physical_loci": len({row["locus"] for row, _ in hits}),
        "reading_rows": len(hits),
    }


def token_summary(rows: list[dict[str, str]], token: str) -> dict[str, object]:
    hits = []
    for row in rows:
        number = row["surface"].split().count(token)
        if number:
            hits.append((row, number))
    scopes = sorted({row["grammar_scope"] for row, _ in hits})
    summary: dict[str, object] = {
        "all": counts(hits),
        "by_edition": {
            edition: counts([(row, n) for row, n in hits if row["edition"] == edition])
            for edition in EDITIONS
        },
        "by_scope": {
            scope: counts([(row, n) for row, n in hits if row["grammar_scope"] == scope])
            for scope in scopes
        },
    }
    if token != "sheey":
        summary["physical_locus_list"] = sorted({row["locus"] for row, _ in hits})
    return summary


def pair_summary(rows: list[dict[str, str]], pair: tuple[str, str]) -> dict[str, object]:
    adjacent = []
    cooccurring = []
    for row in rows:
        words = row["surface"].split()
        number = sum(words[index:index + 2] == list(pair) for index in range(len(words) - 1))
        if number:
            adjacent.append((row, number))
        if all(token in words for token in pair):
            cooccurring.append((row, 1))
    return {
        "adjacent": counts(adjacent),
        "adjacent_loci": sorted({row["locus"] for row, _ in adjacent}),
        "adjacent_whole_row_exact": all(row["surface"] == " ".join(pair) for row, _ in adjacent),
        "unordered_same_row": counts(cooccurring),
        "unordered_same_row_loci": sorted({row["locus"] for row, _ in cooccurring}),
    }


def reconstruct() -> dict[str, object]:
    assert digest(INPUT) == EXPECTED_INPUT_SHA256
    with INPUT.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 15_960

    targets = {}
    for locus, surface in (("f116v.1", "oror sheey"), ("f17r.13", "oteeeon oiil")):
        matches = [row for row in rows if row["locus"] == locus and row["surface"] == surface]
        targets[locus] = {
            "code": "@Lx",
            "editions_present": sorted(row["edition"] for row in matches),
            "grammar_scope": "DIAGNOSTIC_NONPROSE",
            "kind": "L",
            "surface": surface,
        }

    token_recurrence = {token: token_summary(rows, token) for token in TOKENS}
    pair_recurrence = {" ".join(pair): pair_summary(rows, pair) for pair in PAIRS}

    return {
        "claim_ceiling": (
            "The f116v marginal span consists of two exact surfaces that also occur in the "
            "main manuscript, while the two f17r surfaces are unique to their marginal locus "
            "in this frozen interlinear. Neither exact pair recurs elsewhere. This establishes "
            "manuscript-internal surface reuse only, not an equivalence with adjacent plain "
            "script, a gloss, word meaning, language, cipher, plaintext, or translation."
        ),
        "decision": "PASS_F116V_COMPONENT_RECURRENCE_F17R_UNIQUE_HOLD_EQUIVALENCE",
        "experiment": "F17R_F116V_VOYNICH_SURFACE_RECURRENCE",
        "gates": {
            "exact_pairs_recur_elsewhere": False,
            "f116v_both_components_have_confirmed_prose_recurrence": True,
            "f17r_either_component_recurs_elsewhere": False,
            "plain_script_equivalence_authorized": False,
        },
        "input": {
            "path": "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv",
            "row_count": len(rows),
            "sha256": EXPECTED_INPUT_SHA256,
        },
        "method": "EXACT_WHITESPACE_DELIMITED_LITERAL_SURFACE_PHYSICAL_LOCUS_UNIT",
        "pair_recurrence": pair_recurrence,
        "schema": "F17R_F116V_VOYNICH_SURFACE_RECURRENCE_V1",
        "status": "DESCRIPTIVE_MANUSCRIPT_INTERNAL_REUSE_NO_LEXICAL_TRANSFER",
        "target_rows": targets,
        "token_recurrence": token_recurrence,
    }


if __name__ == "__main__":
    print(json.dumps(reconstruct(), indent=2, sort_keys=True, ensure_ascii=False))
