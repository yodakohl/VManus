#!/usr/bin/env python3
"""Clean-room validation of the target-blind zodiac-opposition controls."""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
METHOD = BASE / "ZODIAC_OPPOSITION_PROFILE_METHOD.md"
PRODUCER = BASE / "run_zodiac_opposition_profile.py"
CONTROL = RESULTS / "zodiac_opposition_profile_controls.json"
CONTROL_REPORT = RESULTS / "zodiac_opposition_profile_controls_report.md"
TARGET = RESULTS / "zodiac_opposition_profile.json"
TARGET_REPORT = RESULTS / "zodiac_opposition_profile_report.md"
OUT = RESULTS / "zodiac_opposition_profile_controls_validation.json"
REPORT = RESULTS / "zodiac_opposition_profile_controls_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
TOL = 1e-15


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def edge(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a < b else (b, a)


def canonical_matching(pairs: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(edge(a, b) for a, b in pairs))


def enumerate_matchings(nodes: tuple[str, ...]) -> list[tuple[tuple[str, str], ...]]:
    def rec(remaining: tuple[str, ...]) -> list[tuple[tuple[str, str], ...]]:
        if not remaining:
            return [tuple()]
        anchor = remaining[0]
        rows = []
        for j in range(1, len(remaining)):
            rest = remaining[1:j] + remaining[j + 1:]
            for suffix in rec(rest):
                rows.append(canonical_matching(((anchor, remaining[j]),) + suffix))
        return rows

    rows = sorted(set(rec(nodes)))
    assert all(len(row) * 2 == len(nodes) and sorted(x for pair in row for x in pair) == sorted(nodes) for row in rows)
    return rows


def score(matrix: dict, nodes: tuple[str, ...], truth: tuple[tuple[str, str], ...]) -> dict[str, object]:
    all_edges = [edge(nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes))]
    z: dict[str, dict[str, dict[tuple[str, str], float]]] = {
        reading: {view: {} for view in VIEWS} for reading in READINGS
    }
    diagnostics: dict[str, dict[str, dict[str, float]]] = {reading: {} for reading in READINGS}
    for reading in READINGS:
        for view in VIEWS:
            values = [matrix[reading][view][pair] for pair in all_edges]
            center = statistics.fmean(values)
            scale = math.sqrt(statistics.fmean((value - center) ** 2 for value in values))
            diagnostics[reading][view] = {"mean": center, "population_sd": scale}
            if not math.isfinite(scale) or scale <= 0:
                return {"eligible": False, "reason": f"zero_or_nonfinite_sd:{reading}:{view}"}
            z[reading][view] = {pair: (value - center) / scale for pair, value in zip(all_edges, values)}

    orbit = []
    matchings = enumerate_matchings(nodes)
    observed = canonical_matching(truth)
    assert observed in matchings
    for matching in matchings:
        reading_scores = {
            reading: statistics.fmean(z[reading][view][pair] for view in VIEWS for pair in matching)
            for reading in READINGS
        }
        orbit.append({
            "matching": [list(pair) for pair in matching],
            "edition_scores": reading_scores,
            "robust_score": min(reading_scores.values()),
        })
    observed_row = next(row for row in orbit if tuple(tuple(pair) for pair in row["matching"]) == observed)
    observed_score = float(observed_row["robust_score"])
    contributions = {
        reading: {
            "|".join(pair): statistics.fmean(z[reading][view][pair] for view in VIEWS)
            for pair in observed
        }
        for reading in READINGS
    }
    return {
        "eligible": True,
        "matching_count": len(matchings),
        "observed_matching": [list(pair) for pair in observed],
        "observed_edition_scores": observed_row["edition_scores"],
        "observed_robust_score": observed_score,
        "inclusive_rank": 1 + sum(float(row["robust_score"]) > observed_score + TOL for row in orbit),
        "tied": sum(abs(float(row["robust_score"]) - observed_score) <= TOL for row in orbit),
        "exact_one_sided_p": sum(float(row["robust_score"]) >= observed_score - TOL for row in orbit) / len(orbit),
        "positive_pair_support": {reading: sum(value > 0 for value in contributions[reading].values()) for reading in READINGS},
        "observed_pair_contributions": contributions,
        "standardization_diagnostics": diagnostics,
        "orbit_sha256": object_hash(orbit),
        "orbit_robust_scores": [float(row["robust_score"]) for row in orbit],
    }


def planted_matrix(nodes: tuple[str, ...], favored: tuple[tuple[str, str], ...], low: float = .1, high: float = .9) -> dict:
    all_edges = [edge(nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes))]
    marked = set(canonical_matching(favored))
    return {
        reading: {view: {pair: high if pair in marked else low for pair in all_edges} for view in VIEWS}
        for reading in READINGS
    }


def reconstruct() -> tuple[dict[str, object], int]:
    nodes = tuple(f"S{i}" for i in range(8))
    truth = (("S0", "S1"), ("S2", "S3"), ("S4", "S5"), ("S6", "S7"))
    alternate = (("S0", "S2"), ("S1", "S3"), ("S4", "S6"), ("S5", "S7"))
    base = planted_matrix(nodes, truth)
    summaries = {
        "planted": score(base, nodes, truth),
        "constant": score(planted_matrix(nodes, truth, .5, .5), nodes, truth),
        "one_pair": score(planted_matrix(nodes, (("S0", "S1"),)), nodes, truth),
    }
    disagreement = planted_matrix(nodes, truth)
    disagreement["RF1b"] = planted_matrix(nodes, alternate)["RF1b"]
    summaries["reading_disagreement"] = score(disagreement, nodes, truth)
    affine = {
        reading: {
            view: {
                pair: value * (1.3 + .1 * vi) + (ri - 2.0)
                for pair, value in base[reading][view].items()
            }
            for vi, view in enumerate(VIEWS)
        }
        for ri, reading in enumerate(READINGS)
    }
    summaries["affine"] = score(affine, nodes, truth)
    rename = {node: nodes[-i - 1] for i, node in enumerate(nodes)}
    renamed_matrix = {
        reading: {
            view: {edge(rename[pair[0]], rename[pair[1]]): value for pair, value in base[reading][view].items()}
            for view in VIEWS
        }
        for reading in READINGS
    }
    renamed_truth = tuple(edge(rename[a], rename[b]) for a, b in truth)
    summaries["relabeled"] = score(renamed_matrix, tuple(sorted(rename.values())), renamed_truth)
    checks = {
        "exact_105_matchings": summaries["planted"].get("matching_count") == 105,
        "distributed_plant_unique_rank_one": summaries["planted"].get("inclusive_rank") == summaries["planted"].get("tied") == 1,
        "distributed_plant_all_pairs_positive": all(v == 4 for v in summaries["planted"].get("positive_pair_support", {}).values()),
        "constant_null_ineligible": summaries["constant"] == {"eligible": False, "reason": "zero_or_nonfinite_sd:ZL3b:FAMILY_N2"},
        "one_pair_rejected_by_support": any(v < 3 for v in summaries["one_pair"].get("positive_pair_support", {}).values()),
        "reading_disagreement_rejected": summaries["reading_disagreement"].get("exact_one_sided_p", 1.0) > .05 or any(v <= 0 for v in summaries["reading_disagreement"].get("observed_edition_scores", {}).values()),
        "positive_affine_rank_invariant": summaries["affine"].get("inclusive_rank") == summaries["planted"].get("inclusive_rank") and summaries["affine"].get("tied") == summaries["planted"].get("tied") and abs(float(summaries["affine"].get("exact_one_sided_p", 1)) - float(summaries["planted"].get("exact_one_sided_p", 0))) <= TOL,
        "sign_relabeling_invariant": summaries["relabeled"].get("inclusive_rank") == summaries["planted"].get("inclusive_rank") and summaries["relabeled"].get("tied") == summaries["planted"].get("tied") and abs(float(summaries["relabeled"].get("observed_robust_score", 0)) - float(summaries["planted"].get("observed_robust_score", 1))) <= 1e-12,
    }
    expected = {
        "experiment": "ZODIAC_OPPOSITION_PROFILE_CONTROLS",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "inputs": {METHOD.name: file_hash(METHOD), PRODUCER.name: file_hash(PRODUCER)},
        "checks": checks,
        "summaries": summaries,
        "target_accessed": False,
        "claim_ceiling": "Synthetic scorer validation only; no manuscript opposition result or meaning.",
    }
    assertions = 105 + sum(len(item.get("orbit_robust_scores", [])) for item in summaries.values()) + len(checks)
    return expected, assertions


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if TARGET.exists() or TARGET_REPORT.exists():
        raise SystemExit("target artifacts already exist")
    stored = json.loads(CONTROL.read_text(encoding="utf-8"))
    expected, assertions = reconstruct()
    assert stored == expected, "control result differs from clean-room reconstruction"
    expected_report = (
        "# Zodiac-opposition profile controls\n\n"
        "Status: **PASS**\n\n"
        "The exact 105-matching scorer recovers the distributed plant, rejects constant, one-pair, and reading-disagreement controls, and is invariant to positive affine transforms and sign relabeling. No manuscript source was opened.\n"
    )
    assert CONTROL_REPORT.read_text(encoding="utf-8") == expected_report
    result = {
        "experiment": "ZODIAC_OPPOSITION_PROFILE_CONTROLS_VALIDATION",
        "status": "PASS",
        "assertions": assertions,
        "bindings": {
            CONTROL.name: file_hash(CONTROL),
            CONTROL_REPORT.name: file_hash(CONTROL_REPORT),
            METHOD.name: file_hash(METHOD),
            PRODUCER.name: file_hash(PRODUCER),
        },
        "target_artifacts_absent": True,
        "production_module_imported": False,
        "claim_ceiling": "Independent reconstruction of synthetic controls only; no manuscript result or meaning.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Zodiac-opposition control validation\n\n"
        f"Status: **PASS** ({assertions} checks). The clean-room validator reconstructed the full 105-matching orbit and all six synthetic worlds without importing the producer. Target artifacts were absent.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "assertions": assertions}, sort_keys=True))


if __name__ == "__main__":
    main()
