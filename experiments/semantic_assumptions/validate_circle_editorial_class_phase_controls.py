#!/usr/bin/env python3
"""Clean-room reconstruction of the f67/f68 class-phase synthetic controls."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
METHOD = BASE / "CIRCLE_EDITORIAL_CLASS_PHASE_METHOD.md"
PRODUCER = BASE / "run_circle_editorial_class_phase.py"
CURRENT = RESULTS / "circle_editorial_class_phase_controls.json"
CURRENT_REPORT = RESULTS / "circle_editorial_class_phase_controls_report.md"
ATTEMPT = RESULTS / "circle_editorial_class_phase_controls_attempt1.json"
ATTEMPT_REPORT = RESULTS / "circle_editorial_class_phase_controls_report_attempt1.md"
TARGET = RESULTS / "circle_editorial_class_phase.json"
TARGET_REPORT = RESULTS / "circle_editorial_class_phase_report.md"
OUT = RESULTS / "circle_editorial_class_phase_controls_validation.json"
REPORT = RESULTS / "circle_editorial_class_phase_controls_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
FOLIO_PAGES = {
    "f67": ("f67r1", "f67r2", "f67v1", "f67v2"),
    "f68": ("f68r1", "f68r2", "f68r3", "f68v1", "f68v2", "f68v3"),
}
TRUTH = {"f67": ("A", "A", "A", "C"), "f68": ("A", "A", "A", "C", "A", "C")}
TOL = 1e-15


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def roll(values: tuple[str, ...], amount: int) -> tuple[str, ...]:
    return values[-amount:] + values[:-amount] if amount else values


def assignments(labels: dict[str, tuple[str, ...]]) -> list[dict[str, tuple[str, ...]]]:
    output = []
    for shift67, shift68 in itertools.product(range(4), range(6)):
        output.append({"f67": roll(labels["f67"], shift67), "f68": roll(labels["f68"], shift68)})
    assert len({tuple((folio, row[folio]) for folio in FOLIO_PAGES) for row in output}) == 24
    return output


def pairs(folio: str) -> list[tuple[str, str]]:
    pages = FOLIO_PAGES[folio]
    return [(pages[i], pages[j]) for i in range(len(pages)) for j in range(i + 1, len(pages))]


def score(matrix: dict, labels: dict[str, tuple[str, ...]], views: tuple[str, ...] = VIEWS) -> dict[str, object]:
    standardized = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    diagnostics = {}
    for reading in READINGS:
        diagnostics[reading] = {}
        for view in views:
            diagnostics[reading][view] = {}
            for folio in FOLIO_PAGES:
                values = [matrix[reading][view][folio][pair] for pair in pairs(folio)]
                mean = statistics.fmean(values)
                sd = math.sqrt(statistics.fmean((value - mean) ** 2 for value in values))
                diagnostics[reading][view][folio] = {"mean": mean, "population_sd": sd}
                if not math.isfinite(sd) or sd <= 0:
                    return {"eligible": False, "reason": f"zero_or_nonfinite_sd:{reading}:{view}:{folio}"}
                standardized[reading][view][folio] = {
                    pair: (value - mean) / sd for pair, value in zip(pairs(folio), values)
                }
    orbit = []
    for assignment in assignments(labels):
        reading_scores = {}
        folio_scores = {}
        for reading in READINGS:
            folio_scores[reading] = {}
            for folio, pages in FOLIO_PAGES.items():
                state = dict(zip(pages, assignment[folio]))
                view_scores = []
                for view in views:
                    same = [standardized[reading][view][folio][pair] for pair in pairs(folio) if state[pair[0]] == state[pair[1]]]
                    different = [standardized[reading][view][folio][pair] for pair in pairs(folio) if state[pair[0]] != state[pair[1]]]
                    assert same and different
                    view_scores.append(statistics.fmean(same) - statistics.fmean(different))
                folio_scores[reading][folio] = statistics.fmean(view_scores)
            reading_scores[reading] = statistics.fmean(folio_scores[reading].values())
        orbit.append({
            "assignment": {folio: list(assignment[folio]) for folio in FOLIO_PAGES},
            "reading_scores": reading_scores,
            "reading_folio_contributions": folio_scores,
            "robust_score": min(reading_scores.values()),
        })
    observed = next(row for row in orbit if all(tuple(row["assignment"][folio]) == labels[folio] for folio in FOLIO_PAGES))
    observed_score = float(observed["robust_score"])
    return {
        "eligible": True,
        "views": list(views),
        "phase_count": len(orbit),
        "observed_assignment": {folio: list(labels[folio]) for folio in FOLIO_PAGES},
        "observed_reading_scores": observed["reading_scores"],
        "observed_reading_folio_contributions": observed["reading_folio_contributions"],
        "observed_robust_score": observed_score,
        "inclusive_rank": 1 + sum(float(row["robust_score"]) > observed_score + TOL for row in orbit),
        "tied": sum(abs(float(row["robust_score"]) - observed_score) <= TOL for row in orbit),
        "exact_one_sided_p": sum(float(row["robust_score"]) >= observed_score - TOL for row in orbit) / len(orbit),
        "standardization_diagnostics": diagnostics,
        "orbit_sha256": object_hash(orbit),
        "orbit_robust_scores": [float(row["robust_score"]) for row in orbit],
    }


def matrix_for(labels: dict[str, tuple[str, ...]]) -> dict:
    result = {reading: {view: {} for view in VIEWS} for reading in READINGS}
    for reading in READINGS:
        for view in VIEWS:
            for folio, pages in FOLIO_PAGES.items():
                state = dict(zip(pages, labels[folio]))
                result[reading][view][folio] = {
                    pair: .9 if state[pair[0]] == state[pair[1]] else .1 for pair in pairs(folio)
                }
    return result


def complete_pass(item: dict[str, object]) -> bool:
    return (
        item.get("eligible") is True
        and item.get("inclusive_rank") == item.get("tied") == 1
        and all(value > 0 for value in item.get("observed_reading_scores", {}).values())
        and all(value > 0 for row in item.get("observed_reading_folio_contributions", {}).values() for value in row.values())
    )


def reconstruct() -> dict[str, object]:
    base_matrix = matrix_for(TRUTH)
    distributed = score(base_matrix, TRUTH)
    one_labels = {"f67": TRUTH["f67"], "f68": roll(TRUTH["f68"], 1)}
    one_folio = score(matrix_for(one_labels), TRUTH)
    disagreement_matrix = matrix_for(TRUTH)
    shifted = {folio: roll(TRUTH[folio], 1) for folio in FOLIO_PAGES}
    disagreement_matrix["RF1b"] = matrix_for(shifted)["RF1b"]
    disagreement = score(disagreement_matrix, TRUTH)
    ordinal_matrix = {reading: {view: {} for view in VIEWS} for reading in READINGS}
    for reading in READINGS:
        for view in VIEWS:
            for folio, pages in FOLIO_PAGES.items():
                ordinal_matrix[reading][view][folio] = {
                    pair: 1.0 / (1.0 + abs(pages.index(pair[0]) - pages.index(pair[1]))) for pair in pairs(folio)
                }
    ordinal = score(ordinal_matrix, TRUTH)
    affine_matrix = {
        reading: {
            view: {
                folio: {pair: value * (1.2 + .1 * vi) + ri for pair, value in base_matrix[reading][view][folio].items()}
                for folio in FOLIO_PAGES
            }
            for vi, view in enumerate(VIEWS)
        }
        for ri, reading in enumerate(READINGS)
    }
    affine = score(affine_matrix, TRUTH)
    complement = {folio: tuple("C" if value == "A" else "A" for value in TRUTH[folio]) for folio in FOLIO_PAGES}
    complemented = score(base_matrix, complement)
    checks = {
        "exact_24_unique_phases": distributed.get("phase_count") == 24,
        "distributed_plant_unique_rank_one": distributed.get("inclusive_rank") == distributed.get("tied") == 1,
        "distributed_plant_both_folios_all_readings": all(value > 0 for row in distributed.get("observed_reading_folio_contributions", {}).values() for value in row.values()),
        "one_folio_plant_rejected": not complete_pass(one_folio),
        "third_reading_disagreement_rejected": not complete_pass(disagreement),
        "ordinal_distance_rejected": not complete_pass(ordinal),
        "positive_affine_invariant": affine.get("inclusive_rank") == distributed.get("inclusive_rank") and affine.get("tied") == distributed.get("tied") and abs(float(affine.get("exact_one_sided_p", 1)) - float(distributed.get("exact_one_sided_p", 0))) <= TOL and max(abs(a - b) for a, b in zip(affine.get("orbit_robust_scores", []), distributed.get("orbit_robust_scores", []))) <= TOL,
        "class_complement_invariant": complemented.get("orbit_robust_scores") == distributed.get("orbit_robust_scores") and complemented.get("observed_robust_score") == distributed.get("observed_robust_score"),
    }
    return {
        "experiment": "CIRCLE_EDITORIAL_CLASS_PHASE_CONTROLS",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "inputs": {METHOD.name: file_hash(METHOD), PRODUCER.name: file_hash(PRODUCER)},
        "checks": checks,
        "summaries": {
            "distributed": distributed,
            "one_folio": one_folio,
            "reading_disagreement": disagreement,
            "ordinal_distance": ordinal,
            "affine": affine,
            "complemented": complemented,
        },
        "target_accessed": False,
        "claim_ceiling": "Synthetic class-phase scorer validation only; no manuscript class, object, word, meaning, or translation.",
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if TARGET.exists() or TARGET_REPORT.exists():
        raise SystemExit("target artifacts already exist")
    expected = reconstruct()
    stored = json.loads(CURRENT.read_text(encoding="utf-8"))
    assert stored == expected
    attempt = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    assert attempt["status"] == "FAIL"
    assert [key for key, value in attempt["checks"].items() if not value] == ["positive_affine_invariant"]
    a = attempt["summaries"]["affine"]
    b = attempt["summaries"]["distributed"]
    max_delta = max(abs(x - y) for x, y in zip(a["orbit_robust_scores"], b["orbit_robust_scores"]))
    assert max_delta == 4.440892098500626e-16
    assert (a["inclusive_rank"], a["tied"], a["exact_one_sided_p"]) == (b["inclusive_rank"], b["tied"], b["exact_one_sided_p"])
    expected_report = (
        "# Circle editorial-class phase controls\n\n"
        "Status: **PASS**\n\n"
        "The exact 24-phase scorer recovers a distributed two-folio plant, rejects one-folio, reading-disagreement, and ordinal-distance controls, and preserves positive-affine and class-complement invariance. No manuscript target source was opened.\n"
    )
    assert CURRENT_REPORT.read_text(encoding="utf-8") == expected_report
    validation = {
        "experiment": "CIRCLE_EDITORIAL_CLASS_PHASE_CONTROLS_VALIDATION",
        "status": "PASS",
        "assertions": 24 * 6 + len(expected["checks"]) + 8,
        "bindings": {path.name: file_hash(path) for path in (METHOD, PRODUCER, CURRENT, CURRENT_REPORT, ATTEMPT, ATTEMPT_REPORT)},
        "attempt1_numeric_delta": max_delta,
        "attempt1_rank_and_p_unchanged": True,
        "target_artifacts_absent": True,
        "production_module_imported": False,
        "claim_ceiling": "Independent reconstruction of synthetic controls only; no manuscript class, object, word, meaning, or translation.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Circle editorial-class control validation\n\n"
        f"Status: **PASS** ({validation['assertions']} checks). The nonimporting validator reconstructed all six 24-phase worlds and confirmed that attempt 1 failed only because exact float equality rejected a {max_delta:.17g} invariant delta with unchanged rank and p. Target artifacts were absent.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "assertions": validation["assertions"], "attempt1_delta": max_delta}, sort_keys=True))


if __name__ == "__main__":
    main()
