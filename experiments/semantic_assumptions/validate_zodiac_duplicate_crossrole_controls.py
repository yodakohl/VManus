#!/usr/bin/env python3
"""Clean-room validation of duplicated-zodiac cross-role controls."""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
METHOD = BASE / "ZODIAC_DUPLICATE_CROSSROLE_METHOD.md"
PRODUCER = BASE / "run_zodiac_duplicate_crossrole.py"
CONTROL = RESULTS / "zodiac_duplicate_crossrole_controls.json"
CONTROL_REPORT = RESULTS / "zodiac_duplicate_crossrole_controls_report.md"
TARGET = RESULTS / "zodiac_duplicate_crossrole.json"
TARGET_REPORT = RESULTS / "zodiac_duplicate_crossrole_report.md"
OUT = RESULTS / "zodiac_duplicate_crossrole_controls_validation.json"
REPORT = RESULTS / "zodiac_duplicate_crossrole_controls_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
TOL = 1e-15


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def edge(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a < b else (b, a)


def canon(pairs) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(edge(*pair) for pair in pairs))


def pair_list(pages: tuple[str, ...]) -> list[tuple[str, str]]:
    return [edge(pages[i], pages[j]) for i in range(len(pages)) for j in range(i + 1, len(pages))]


def matchings(pages: tuple[str, ...]) -> list[tuple[tuple[str, str], ...]]:
    output = set()
    for first in pair_list(pages):
        remaining = tuple(page for page in pages if page not in first)
        for second in pair_list(remaining):
            output.add(canon((first, second)))
    rows = sorted(output)
    assert len(rows) == 1485 and all(len({page for pair in row for page in pair}) == 4 for row in rows)
    return rows


def score(matrix: dict, pages: tuple[str, ...], truth, views: tuple[str, ...] = VIEWS) -> dict[str, object]:
    pairs = pair_list(pages)
    z = defaultdict(lambda: defaultdict(dict))
    diagnostics = {}
    for reading in READINGS:
        diagnostics[reading] = {}
        for view in views:
            values = [matrix[reading][view][pair] for pair in pairs]
            mean = statistics.fmean(values)
            sd = math.sqrt(statistics.fmean((value - mean) ** 2 for value in values))
            diagnostics[reading][view] = {"mean": mean, "population_sd": sd}
            if not math.isfinite(sd) or sd <= 0:
                return {"eligible": False, "reason": f"zero_or_nonfinite_sd:{reading}:{view}"}
            z[reading][view] = {pair: (value - mean) / sd for pair, value in zip(pairs, values)}
    observed = canon(truth)
    orbit = []
    for candidate in matchings(pages):
        reading_scores = {
            reading: statistics.fmean(z[reading][view][pair] for view in views for pair in candidate)
            for reading in READINGS
        }
        orbit.append({"matching": [list(pair) for pair in candidate], "reading_scores": reading_scores, "robust_score": min(reading_scores.values())})
    observed_row = next(row for row in orbit if canon(row["matching"]) == observed)
    observed_score = float(observed_row["robust_score"])
    contributions = {
        reading: {"|".join(pair): statistics.fmean(z[reading][view][pair] for view in views) for pair in observed}
        for reading in READINGS
    }
    pair_ranks = {}
    for reading in READINGS:
        values = {pair: statistics.fmean(z[reading][view][pair] for view in views) for pair in pairs}
        pair_ranks[reading] = {}
        for pair in observed:
            value = values[pair]
            pair_ranks[reading]["|".join(pair)] = {
                "value": value,
                "inclusive_rank": 1 + sum(other > value + TOL for other in values.values()),
                "tied": sum(abs(other - value) <= TOL for other in values.values()),
                "inclusive_one_sided_p": sum(other >= value - TOL for other in values.values()) / len(values),
            }
    return {
        "eligible": True,
        "views": list(views),
        "pair_count": len(pairs),
        "matching_count": len(orbit),
        "observed_matching": [list(pair) for pair in observed],
        "observed_reading_scores": observed_row["reading_scores"],
        "observed_pair_contributions": contributions,
        "observed_pair_ranks": pair_ranks,
        "observed_robust_score": observed_score,
        "inclusive_rank": 1 + sum(float(row["robust_score"]) > observed_score + TOL for row in orbit),
        "tied": sum(abs(float(row["robust_score"]) - observed_score) <= TOL for row in orbit),
        "exact_one_sided_p": sum(float(row["robust_score"]) >= observed_score - TOL for row in orbit) / len(orbit),
        "standardization_diagnostics": diagnostics,
        "orbit_sha256": json_digest(orbit),
        "orbit_robust_scores": [float(row["robust_score"]) for row in orbit],
    }


def matrix(pages: tuple[str, ...], favored, low: float = .1, high: float = .9) -> dict:
    marked = set(canon(favored))
    return {
        reading: {view: {pair: high if pair in marked else low for pair in pair_list(pages)} for view in VIEWS}
        for reading in READINGS
    }


def complete_pass(item: dict[str, object]) -> bool:
    return item.get("eligible") is True and item.get("exact_one_sided_p", 1.0) <= .01 and all(value > 0 for value in item.get("observed_reading_scores", {}).values()) and all(value > 0 for row in item.get("observed_pair_contributions", {}).values() for value in row.values()) and all(cell.get("inclusive_one_sided_p", 1.0) <= .10 for row in item.get("observed_pair_ranks", {}).values() for cell in row.values())


def reconstruct() -> dict[str, object]:
    pages = tuple(f"S{i:02d}" for i in range(12))
    truth = (("S00", "S01"), ("S02", "S03"))
    alternate = (("S04", "S05"), ("S06", "S07"))
    base = matrix(pages, truth)
    planted = score(base, pages, truth)
    constant = score(matrix(pages, truth, .5, .5), pages, truth)
    one_pair = score(matrix(pages, (truth[0],)), pages, truth)
    hub = score(matrix(pages, tuple(("S00", page) for page in pages if page != "S00")), pages, truth)
    disagreement_matrix = matrix(pages, truth)
    disagreement_matrix["RF1b"] = matrix(pages, alternate)["RF1b"]
    disagreement = score(disagreement_matrix, pages, truth)
    affine_matrix = {
        reading: {view: {pair: value * (1.2 + .1 * vi) + ri for pair, value in base[reading][view].items()} for vi, view in enumerate(VIEWS)}
        for ri, reading in enumerate(READINGS)
    }
    affine = score(affine_matrix, pages, truth)
    rename = {page: pages[-i - 1] for i, page in enumerate(pages)}
    renamed_matrix = {
        reading: {view: {edge(rename[pair[0]], rename[pair[1]]): value for pair, value in base[reading][view].items()} for view in VIEWS}
        for reading in READINGS
    }
    renamed_truth = tuple(edge(rename[a], rename[b]) for a, b in truth)
    relabeled = score(renamed_matrix, tuple(sorted(rename.values())), renamed_truth)
    delta = max(abs(a - b) for a, b in zip(affine["orbit_robust_scores"], planted["orbit_robust_scores"]))
    checks = {
        "exact_66_page_pairs": planted.get("pair_count") == 66,
        "exact_1485_disjoint_two_pair_matchings": planted.get("matching_count") == 1485,
        "distributed_plant_unique_rank_one": planted.get("inclusive_rank") == planted.get("tied") == 1,
        "distributed_plant_passes_complete_gate": complete_pass(planted),
        "constant_null_ineligible": constant == {"eligible": False, "reason": "zero_or_nonfinite_sd:ZL3b:FAMILY_N2"},
        "one_pair_plant_rejected": not complete_pass(one_pair),
        "one_page_hub_rejected": not complete_pass(hub),
        "third_reading_disagreement_rejected": not complete_pass(disagreement),
        "positive_affine_invariant": affine.get("inclusive_rank") == planted.get("inclusive_rank") and affine.get("tied") == planted.get("tied") and affine.get("exact_one_sided_p") == planted.get("exact_one_sided_p") and delta <= 1e-12,
        "page_relabeling_invariant": relabeled.get("inclusive_rank") == planted.get("inclusive_rank") and relabeled.get("tied") == planted.get("tied") and relabeled.get("exact_one_sided_p") == planted.get("exact_one_sided_p") and abs(float(relabeled.get("observed_robust_score", 0)) - float(planted.get("observed_robust_score", 1))) <= 1e-12,
    }
    return {
        "experiment": "ZODIAC_DUPLICATE_CROSSROLE_CONTROLS",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "inputs": {METHOD.name: digest(METHOD), PRODUCER.name: digest(PRODUCER)},
        "checks": checks,
        "affine_max_abs_orbit_delta": delta,
        "summaries": {"planted": planted, "constant": constant, "one_pair": one_pair, "hub": hub, "reading_disagreement": disagreement, "affine": affine, "relabeled": relabeled},
        "target_accessed": False,
        "claim_ceiling": "Synthetic cross-role scorer validation only; no manuscript relation, sign field, word, meaning, or translation.",
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    assert not TARGET.exists() and not TARGET_REPORT.exists()
    expected = reconstruct()
    assert json.loads(CONTROL.read_text(encoding="utf-8")) == expected
    expected_report = (
        "# Zodiac duplicate cross-role controls\n\n"
        "Status: **PASS**\n\n"
        "The 1,485-matching scorer recovers a distributed two-pair plant, rejects constant, one-pair, hub, and reading-disagreement controls, and preserves affine and page-relabeling invariance. No manuscript target source was opened.\n"
    )
    assert CONTROL_REPORT.read_text(encoding="utf-8") == expected_report
    assertions = 1485 * 6 + len(expected["checks"]) + 66
    result = {
        "experiment": "ZODIAC_DUPLICATE_CROSSROLE_CONTROLS_VALIDATION",
        "status": "PASS",
        "assertions": assertions,
        "bindings": {path.name: digest(path) for path in (METHOD, PRODUCER, CONTROL, CONTROL_REPORT)},
        "target_artifacts_absent": True,
        "production_module_imported": False,
        "claim_ceiling": "Independent synthetic scorer reconstruction only; no manuscript relation, sign field, word, meaning, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Zodiac duplicate cross-role control validation\n\n"
        f"Status: **PASS** ({assertions} checks). The nonimporting validator reconstructed all seven synthetic worlds, all 1,485-match orbits, pair ranks, decisions, exact JSON, and report while target artifacts were absent.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "assertions": assertions}, sort_keys=True))


if __name__ == "__main__":
    main()
