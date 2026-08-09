#!/usr/bin/env python3
"""Independent reconstruction of the exhaustive F69C001 corrected control."""

from __future__ import annotations

import importlib.util
import itertools
import json
import math
import statistics
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
INDEPENDENT_PATH = HERE / "validate_f69c001_target.py"
ARTIFACT = HERE / "results" / "f69c001_nondihedral_control.json"
REPORT = HERE / "results" / "f69c001_nondihedral_control_validation.md"


def load_independent_engine():
    spec = importlib.util.spec_from_file_location(
        "f69c001_independent_control_engine", INDEPENDENT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def histogram(ranks: list[int]) -> dict[str, int]:
    counts = Counter(ranks)
    return {str(rank): counts[rank] for rank in range(1, 61)}


def main() -> None:
    engine = load_independent_engine()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rows = {
        reading: engine.read_rows(path)
        for reading, path in engine.SOURCES.items()
    }
    chunks, _provenance = engine.bind_target(rows)
    chunks = dict(chunks)
    chunks["IT2a"] = tuple(
        "ed" if index == 4 else surface
        for index, surface in enumerate(chunks["IT2a"])
    )
    corpora = {
        reading: engine.build_corpus(rows[reading]) for reading in engine.SOURCES
    }
    orders = tuple(itertools.permutations(range(6)))
    truth = engine.normalize_cycle(tuple(range(6)))
    orbits = tuple(sorted({engine.normalize_cycle(order) for order in orders}))

    zscores = {}
    score_hashes = {}
    for reading in engine.SOURCES:
        candidates = {
            "".join(chunks[reading][index] for index in order)
            for order in orders
        }
        events, contexts = engine.train_excluding(corpora[reading], candidates)
        raw = {
            order: engine.likelihood(
                "".join(chunks[reading][index] for index in order),
                events, contexts,
            )
            for order in orders
        }
        mean = statistics.fmean(raw.values())
        spread = statistics.pstdev(raw.values())
        zscores[reading] = {
            order: (value - mean) / spread for order, value in raw.items()
        }
        score_hashes[reading] = engine.score_hash(zscores[reading])

    def alignment_rank(assignment: tuple[int, ...]) -> int:
        grouped = {orbit: -math.inf for orbit in orbits}
        for order in orders:
            remapped = tuple(assignment[index] for index in order)
            value = min(
                zscores["ZL3b"][order], zscores["IT2a"][remapped],
                zscores["RF1b"][order],
            )
            orbit = engine.normalize_cycle(order)
            grouped[orbit] = max(grouped[orbit], value)
        return engine.inclusive_rank(grouped, truth)

    symmetries = [order for order in orders if engine.normalize_cycle(order) == truth]
    negative = [order for order in orders if engine.normalize_cycle(order) != truth]
    observed_rank = alignment_rank(tuple(range(6)))
    ranks = [alignment_rank(assignment) for assignment in negative]
    rank1_count = sum(rank == 1 for rank in ranks)
    gates = {
        "observed_physical_alignment_rank1": observed_rank == 1,
        "non_dihedral_rank1_count_at_most_35": rank1_count <= 35,
    }
    expected_status = (
        "POSTHOC_SPECIFICITY_PASS" if all(gates.values())
        else "POSTHOC_SPECIFICITY_FAIL"
    )

    checks = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    check("720 complete assignments", len(orders) == 720)
    check("12 dihedral symmetry exclusions", len(symmetries) == 12)
    check("708 non-dihedral controls", len(negative) == 708)
    check("independent z-score tables", stored["score_table_sha256"] == score_hashes)
    check("observed physical rank", (
        stored["observed_physical_alignment_rank"] == observed_rank
    ))
    check("complete rank histogram", (
        stored["non_dihedral_rank_histogram"] == histogram(ranks)
    ))
    check("rank vector digest", (
        stored["non_dihedral_rank_vector_sha256"] == engine.digest_json(ranks)
    ))
    check("rank-1 count and fraction", (
        stored["non_dihedral_rank1_count"] == rank1_count
        and math.isclose(
            stored["non_dihedral_rank1_fraction"], rank1_count / len(ranks),
            rel_tol=0.0, abs_tol=1e-15,
        )
    ))
    check("gates and decision", (
        stored["gates"] == gates and stored["status"] == expected_status
    ))

    probe = negative[0]
    explicit_chunks = dict(chunks)
    explicit_chunks["IT2a"] = tuple(chunks["IT2a"][index] for index in probe)
    explicit_result, _ = engine.evaluate(explicit_chunks, corpora)
    check("algebraic action equals explicit relabeling", (
        alignment_rank(probe) == explicit_result["combined_target_inclusive_rank"]
    ))
    check("validated observed failure profile", (
        observed_rank == 1 and rank1_count == 66
        and expected_status == "POSTHOC_SPECIFICITY_FAIL"
    ))

    REPORT.write_text(
        "# F69C001 non-dihedral control validation\n\n"
        f"Status: **PASS — {len(checks)} checks**\n\n"
        "An implementation independent of the control runner reconstructs the "
        "three score tables, exact 720 assignments, 12 symmetry exclusions, "
        "all 708 adjacency-breaking ranks, histogram, digest, gates, and "
        "decision. A direct explicit relabeling also matches the algebraic "
        "permutation action.\n\n"
        f"The physical alignment ranks {observed_rank}/60, but {rank1_count}/708 "
        "non-dihedral relabelings also rank first (9.32%), exceeding the frozen "
        "35/708 limit. The validated result is **POSTHOC_SPECIFICITY_FAIL**. "
        "No joined surface, start, handedness, word, lexeme, language, plaintext, "
        "direction name, or translation follows.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "PASS", "checks": len(checks),
        "decision": expected_status, "observed_rank": observed_rank,
        "rank1_count": rank1_count, "total": len(ranks),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
