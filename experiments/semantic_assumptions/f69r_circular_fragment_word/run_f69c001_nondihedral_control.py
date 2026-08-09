#!/usr/bin/env python3
"""Exhaustive corrected non-dihedral control for the post-hoc F69C001 lead."""

from __future__ import annotations

import importlib.util
import itertools
import json
import math
import statistics
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUNNER_PATH = HERE / "run_f69c001_target.py"
SENSITIVITY = HERE / "results" / "f69c001_ed_resolved_sensitivity.json"
OUTPUT = HERE / "results" / "f69c001_nondihedral_control.json"
REPORT = HERE / "results" / "f69c001_nondihedral_control_report.md"


def load_frozen_engine():
    spec = importlib.util.spec_from_file_location("f69c001_frozen_engine", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def rank_histogram(ranks: list[int]) -> dict[str, int]:
    counts = Counter(ranks)
    return {str(rank): counts[rank] for rank in range(1, 61)}


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("non-dihedral control artifact exists; rerun forbidden")
    engine = load_frozen_engine()
    sensitivity = json.loads(SENSITIVITY.read_text(encoding="utf-8"))
    if sensitivity["status"] != "POSTHOC_DIAGNOSTIC_NOT_CONFIRMATION":
        raise AssertionError("unexpected sensitivity status")

    stored, _provenance = engine.validate_binding()
    chunks = dict(stored)
    chunks["IT2a"] = tuple(
        "ed" if index == 4 else surface
        for index, surface in enumerate(stored["IT2a"])
    )
    tables = {
        reading: engine.prose_tables(path)
        for reading, path in engine.SOURCES.items()
    }
    orders = tuple(itertools.permutations(range(6)))
    target_orbit = engine.canonical_cycle(tuple(range(6)))
    orbit_keys = tuple(sorted({engine.canonical_cycle(order) for order in orders}))
    if len(orders) != 720 or len(orbit_keys) != 60:
        raise AssertionError("primary permutation space mismatch")

    zscores = {}
    score_hashes = {}
    for reading in engine.SOURCES:
        raw, _candidate_count = engine.reading_orientation_scores(
            chunks[reading], tables[reading], orders
        )
        mean = statistics.fmean(raw.values())
        spread = statistics.pstdev(raw.values())
        zscores[reading] = {
            order: (value - mean) / spread for order, value in raw.items()
        }
        score_hashes[reading] = engine.score_digest(zscores[reading])

    def alignment_rank(assignment: tuple[int, ...]) -> int:
        orbit_scores = {orbit: -math.inf for orbit in orbit_keys}
        for order in orders:
            remapped_it_order = tuple(assignment[index] for index in order)
            value = min(
                zscores["ZL3b"][order],
                zscores["IT2a"][remapped_it_order],
                zscores["RF1b"][order],
            )
            orbit = engine.canonical_cycle(order)
            orbit_scores[orbit] = max(orbit_scores[orbit], value)
        return engine.rank_of(orbit_scores, target_orbit)

    identity = tuple(range(6))
    observed_rank = alignment_rank(identity)
    if observed_rank != sensitivity["resolved_primary"]["combined_target_inclusive_rank"]:
        raise AssertionError("identity action does not reconstruct sensitivity")

    symmetries = []
    non_dihedral = []
    for assignment in orders:
        if engine.canonical_cycle(assignment) == target_orbit:
            symmetries.append(assignment)
        else:
            non_dihedral.append(assignment)
    if len(symmetries) != 12 or len(non_dihedral) != 708:
        raise AssertionError("symmetry exclusion mismatch")

    ranks = [alignment_rank(assignment) for assignment in non_dihedral]
    rank1_count = sum(rank == 1 for rank in ranks)
    gates = {
        "observed_physical_alignment_rank1": observed_rank == 1,
        "non_dihedral_rank1_count_at_most_35": rank1_count <= 35,
    }
    payload = {
        "experiment": "F69C001_POSTHOC_NONDIHEDRAL_CONTROL",
        "status": (
            "POSTHOC_SPECIFICITY_PASS" if all(gates.values())
            else "POSTHOC_SPECIFICITY_FAIL"
        ),
        "score_table_sha256": score_hashes,
        "total_assignments": len(orders),
        "excluded_dihedral_symmetries": len(symmetries),
        "tested_non_dihedral_relabelings": len(non_dihedral),
        "observed_physical_alignment_rank": observed_rank,
        "non_dihedral_rank_histogram": rank_histogram(ranks),
        "non_dihedral_rank_vector_sha256": engine.json_hash(ranks),
        "non_dihedral_rank1_count": rank1_count,
        "non_dihedral_rank1_fraction": rank1_count / len(ranks),
        "gates": gates,
        "claim_ceiling": (
            "post-hoc circular-order specificity under one model only; cannot "
            "confirm F69C001, choose a start or handedness, emit a joined "
            "surface, or establish sound, word, root, lexeme, language, "
            "plaintext, direction name, or translation"
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    REPORT.write_text(
        "# F69C001 exhaustive non-dihedral control\n\n"
        f"Status: **{payload['status']}**\n\n"
        "The prior one-slot cyclic fixture was invalid because it preserved the "
        "circular order. This corrected census excludes all 12 rotations and "
        "reflections and tests every one of the 708 adjacency-breaking IT2a "
        "slot relabelings.\n\n"
        f"- Physical alignment rank: {observed_rank}/60\n"
        f"- Non-dihedral relabelings at rank 1: {rank1_count}/708 "
        f"({rank1_count / len(ranks):.4%})\n"
        f"- Frozen maximum: 35/708 (5%)\n\n"
        "This target-exposed control can retain only a post-hoc structural lead. "
        "It cannot confirm F69C001, choose a joined orientation, or establish a "
        "word, lexeme, language, plaintext, direction name, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": payload["status"],
        "observed_rank": observed_rank,
        "non_dihedral_rank1_count": rank1_count,
        "non_dihedral_total": len(ranks),
        "gates": gates,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
