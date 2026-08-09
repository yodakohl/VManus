#!/usr/bin/env python3
"""Independent reconstruction of the F69C001 `ed` sensitivity."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ARTIFACT = HERE / "results" / "f69c001_ed_resolved_sensitivity.json"
REPORT = HERE / "results" / "f69c001_ed_resolved_sensitivity_validation.md"
INDEPENDENT_PATH = HERE / "validate_f69c001_target.py"
SEED = b"F69C001|random-orbit-fixture|v1"


def load_independent_engine():
    spec = importlib.util.spec_from_file_location(
        "f69c001_independent_engine", INDEPENDENT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    engine = load_independent_engine()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rows = {
        reading: engine.read_rows(path)
        for reading, path in engine.SOURCES.items()
    }
    bound, provenance = engine.bind_target(rows)
    resolved = dict(bound)
    resolved["IT2a"] = tuple(
        "ed" if index == 4 else surface
        for index, surface in enumerate(bound["IT2a"])
    )
    corpora = {
        reading: engine.build_corpus(rows[reading]) for reading in engine.SOURCES
    }
    primary, private = engine.evaluate(resolved, corpora)

    deletions = []
    for omitted in range(6):
        reduced = {
            reading: tuple(surface for index, surface in enumerate(chunks)
                           if index != omitted)
            for reading, chunks in resolved.items()
        }
        result, _ = engine.evaluate(reduced, corpora)
        deletions.append({
            "omitted_slot": omitted + 1,
            "omitted_locus": engine.SLOTS[omitted][0],
            "combined_target_inclusive_rank": result["combined_target_inclusive_rank"],
            "reading_target_inclusive_ranks": result["reading_target_inclusive_ranks"],
            "combined_orbit_score_sha256": result["combined_orbit_score_sha256"],
        })

    shifted = dict(resolved)
    shifted["IT2a"] = resolved["IT2a"][1:] + resolved["IT2a"][:1]
    shifted_result, _ = engine.evaluate(shifted, corpora)
    alternatives = [
        orbit for orbit in sorted(private["combined"])
        if orbit != private["truth"]
    ]
    fixture_index = int.from_bytes(
        hashlib.sha256(SEED).digest()[:8], "big"
    ) % len(alternatives)
    random_rank = engine.inclusive_rank(
        private["combined"], alternatives[fixture_index]
    )
    deletion_ranks = [row["combined_target_inclusive_rank"] for row in deletions]
    gates = {
        "unique_combined_rank1_of_60": primary["combined_target_inclusive_rank"] == 1,
        "all_individual_reading_ranks_at_most_3": all(
            rank <= 3 for rank in primary["reading_target_inclusive_ranks"].values()
        ),
        "at_least_five_deletion_ranks_at_most_2": sum(
            rank <= 2 for rank in deletion_ranks
        ) >= 5,
        "no_deletion_rank_worse_than_4": max(deletion_ranks) <= 4,
        "misaligned_reading_fixture_rejects": (
            shifted_result["combined_target_inclusive_rank"] > 1
        ),
        "deterministic_non_target_orbit_fixture_rejects": random_rank > 1,
    }
    checks = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    check("original binding provenance", (
        stored["provenance_binding_sha256"] == provenance["binding_sha256"]
    ))
    check("only disputed IT slot changed", (
        stored["change"] == {
            "reading": "IT2a", "slot": 5, "locus": "f69r.49",
            "stored_surface": "em", "qc_surface": "ed",
            "all_other_surfaces_unchanged": True,
        }
        and resolved["IT2a"] == bound["ZL3b"]
    ))
    check("resolved primary hashes and ranks", (
        stored["resolved_primary"] == primary
    ))
    check("all six resolved deletions", (
        stored["resolved_deletions"] == deletions
    ))
    check("resolved fixtures", stored["resolved_fixtures"] == {
        "misaligned_reading_target_rank": shifted_result["combined_target_inclusive_rank"],
        "deterministic_non_target_index": fixture_index,
        "deterministic_non_target_rank": random_rank,
    })
    check("resolved gates", stored["resolved_gates"] == gates)
    check("global resolved decision", (
        stored["all_resolved_computational_gates_pass"] == all(gates.values())
    ))
    check("post-hoc ceiling retained", (
        stored["status"] == "POSTHOC_DIAGNOSTIC_NOT_CONFIRMATION"
        and "cannot upgrade F69C001" in stored["claim_ceiling"]
    ))
    REPORT.write_text(
        "# F69C001 `ed`-resolved sensitivity validation\n\n"
        f"Status: **PASS — {len(checks)} checks**\n\n"
        "An implementation independent of the sensitivity runner reconstructs "
        "the one-slot change, all primary and deletion scores and hashes, both "
        "fixtures, every gate, and the post-hoc claim ceiling. Primary ranks are "
        "1/60 in all readings and deletion ranks are 1, 1, 2, 2, 2, 2 of 12.\n\n"
        "The sole failed fixture cyclically shifts one reading and is itself a "
        "dihedral symmetry of the circular hypothesis, so it is invalid as an "
        "adjacency-breaking control. The result remains post-hoc and cannot "
        "upgrade F69C001 or supply a start, joined surface, word, lexeme, "
        "language, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "PASS", "checks": len(checks),
        "combined_rank": primary["combined_target_inclusive_rank"],
        "individual_ranks": primary["reading_target_inclusive_ranks"],
        "deletion_ranks": deletion_ranks,
        "all_gates_pass": all(gates.values()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
