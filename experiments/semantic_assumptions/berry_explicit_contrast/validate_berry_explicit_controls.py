#!/usr/bin/env python3
"""Independent reconstruction of berry explicit-contrast controls.

This module imports no production experiment code and never scores the source
positive assignment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/berry_explicit_contrast")
DESIGN = BASE / "SOURCE_AND_METHOD_FREEZE.md"
RUNNER = BASE / "run_berry_explicit_contrast.py"
CONTROL = BASE / "CONTROL_RESULT.json"
TARGET = BASE / "TARGET_RESULT.json"
PAGES_PATH = Path("experiments/semantic_assumptions/results/existing_human_page_annotations.tsv")
INTERLINEAR = Path("experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv")
EDITIONS = ("ZL3b", "IT2a", "RF1b")
POS = "α: berries that have no added circles"
NEG = "α: no fruits or flowers"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(131072), b""):
            value.update(chunk)
    return value.hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def page_number(page: str) -> int:
    match = re.match(r"^f(\d+)", page)
    assert match
    return int(match.group(1))


def lit(token: str) -> set[str]:
    output = {"LIT_TOKEN:" + token}
    for size in (2, 3, 4):
        if len(token) > size:
            output.add(f"LIT_PREFIX{size}:" + token[:size])
            output.add(f"LIT_SUFFIX{size}:" + token[-size:])
            output.update(
                f"LIT_INFIX{size}:" + token[start:start + size]
                for start in range(1, len(token) - size)
            )
    return output


def roots(token: str) -> set[str]:
    atoms = token.split("+")
    output = {
        "ROOT_TOKEN:" + token,
        "ROOT_PREFIX:" + atoms[0],
        "ROOT_SUFFIX:" + atoms[-1],
    }
    output.update("ROOT_ATOM:" + atom for atom in atoms)
    output.update(
        "ROOT_BIGRAM:" + left + "+" + right
        for left, right in zip(atoms, atoms[1:])
    )
    return output


def feature_domain(feature: str) -> str:
    return "LIT" if feature[:4] == "LIT_" else "ROOT"


def reconstruct() -> dict[str, object]:
    page_rows = load_tsv(ROOT / PAGES_PATH)
    positive = sorted(row["page"] for row in page_rows if POS in row["illustrations"])
    negative = sorted(row["page"] for row in page_rows if NEG in row["illustrations"])
    pages = sorted(positive + negative, key=lambda page: (page_number(page), page))
    assert len(positive) == 8 and len(negative) == 7 and not set(positive) & set(negative)

    selected = [
        row
        for row in load_tsv(ROOT / INTERLINEAR)
        if row["page"] in set(pages) and row["grammar_scope"] == "CONFIRMED_PROSE"
    ]
    tokens: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    metadata: dict[tuple[str, str], set[tuple[str, str, str]]] = defaultdict(set)
    for row in selected:
        key = (row["edition"], row["page"])
        metadata[key].add((row["section"], row["currier"], row["hand"]))
        tokens[(row["edition"], row["page"], "LIT")].extend(row["surface"].split())
        tokens[(row["edition"], row["page"], "ROOT")].extend(row["root_sequence"].split())
    assert set(metadata) == {(edition, page) for edition in EDITIONS for page in pages}
    assert all(value == {("H", "A", "1")} for value in metadata.values())

    feature_hits: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    type_support: dict[tuple[str, str], set[str]] = defaultdict(set)
    length_den: dict[tuple[str, str, str], Counter[int]] = defaultdict(Counter)
    length_num: dict[tuple[str, str, str, str], Counter[int]] = defaultdict(Counter)
    edition_features = {}
    for edition in EDITIONS:
        found = set()
        for page in pages:
            for domain_name, extractor, size_fn in (
                ("LIT", lit, len),
                ("ROOT", roots, lambda token: len(token.split("+"))),
            ):
                for token in tokens[(edition, page, domain_name)]:
                    size = size_fn(token)
                    length_den[(edition, page, domain_name)][size] += 1
                    for feature in extractor(token):
                        found.add(feature)
                        feature_hits[(edition, page, domain_name)][feature] += 1
                        type_support[(edition, feature)].add(token)
                        length_num[(edition, page, domain_name, feature)][size] += 1
        edition_features[edition] = found
    common = set.intersection(*(edition_features[edition] for edition in EDITIONS))
    eligible = []
    for feature in sorted(common):
        domain_name = feature_domain(feature)
        okay = True
        for edition in EDITIONS:
            values = [feature_hits[(edition, page, domain_name)][feature] for page in pages]
            if sum(values) < 8 or sum(value > 0 for value in values) < 4:
                okay = False
            if feature.startswith(("LIT_PREFIX", "LIT_SUFFIX", "LIT_INFIX")):
                if len(type_support[(edition, feature)]) < 4:
                    okay = False
        if okay:
            eligible.append(feature)

    order = np.array([page_number(page) for page in pages], dtype=np.float64)
    order = (order - order.mean()) / order.std()
    nuisance = np.column_stack((np.ones(15), order))
    residualizer = np.eye(15) - nuisance @ np.linalg.inv(nuisance.T @ nuisance) @ nuisance.T
    raw = {}
    adjusted = {}
    canonical = []
    for edition in EDITIONS:
        raw_values = np.zeros((15, len(eligible)))
        adjusted_values = np.zeros_like(raw_values)
        global_den = {"LIT": Counter(), "ROOT": Counter()}
        for domain_name in global_den:
            for page in pages:
                global_den[domain_name].update(length_den[(edition, page, domain_name)])
        global_num: dict[str, Counter[int]] = defaultdict(Counter)
        for feature in eligible:
            domain_name = feature_domain(feature)
            for page in pages:
                global_num[feature].update(length_num[(edition, page, domain_name, feature)])
        for column, feature in enumerate(eligible):
            domain_name = feature_domain(feature)
            for row_index, page in enumerate(pages):
                denominator = len(tokens[(edition, page, domain_name)])
                observed = feature_hits[(edition, page, domain_name)][feature]
                expectation = sum(
                    count * global_num[feature][length] / global_den[domain_name][length]
                    for length, count in length_den[(edition, page, domain_name)].items()
                )
                raw_values[row_index, column] = observed / denominator
                adjusted_values[row_index, column] = (observed - expectation) / denominator
                canonical.append([edition, page, feature, observed, denominator])
        raw[edition] = residualizer @ raw_values
        adjusted[edition] = residualizer @ adjusted_values

    canonical_text = json.dumps(canonical, separators=(",", ":"), ensure_ascii=False)
    return {
        "panel": {"pages": pages, "positive": positive, "negative": negative},
        "selected_rows": len(selected),
        "tokens": tokens,
        "features": eligible,
        "canonical_hash": hashlib.sha256(canonical_text.encode()).hexdigest(),
        "raw": raw,
        "adjusted": adjusted,
    }


def orbit() -> tuple[list[tuple[int, ...]], np.ndarray]:
    combos = list(itertools.combinations(range(15), 8))
    weights = np.full((len(combos), 15), -1 / 7)
    for index, combo in enumerate(combos):
        weights[index, list(combo)] = 1 / 8
    return combos, weights


def zscores(weights: np.ndarray, values: np.ndarray) -> np.ndarray:
    effects = weights @ values
    scale = np.sqrt(np.mean(effects ** 2, axis=0))
    result = np.zeros_like(effects)
    good = scale > 1e-14
    result[:, good] = effects[:, good] / scale[good]
    return result


def robust(weights: np.ndarray, matrices: dict[str, np.ndarray]) -> np.ndarray:
    stack = np.stack([zscores(weights, matrices[edition]) for edition in EDITIONS])
    forward = np.min(stack, axis=0)
    reverse = np.min(-stack, axis=0)
    return np.maximum(np.maximum(forward, reverse), 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    assert not (ROOT / TARGET).exists()
    control = json.loads((ROOT / CONTROL).read_text(encoding="utf-8"))
    rebuilt = reconstruct()
    checks = []

    assert control["inputs"] == {
        str(path): digest(ROOT / path) for path in (DESIGN, PAGES_PATH, INTERLINEAR)
    }
    assert control["implementation_sha256"] == digest(ROOT / RUNNER)
    checks.extend(["three input hashes", "runner hash", "target artifact absent"])

    assert control["panel"] == rebuilt["panel"]
    assert control["confirmed_prose_locus_rows"] == rebuilt["selected_rows"] == 663
    assert control["metadata_state"] == "all 15 pages are section H Currier A hand 1 in every reading"
    checks.extend(["literal 8/7 source panel", "663 confirmed-prose rows", "uniform H-A-hand1 metadata"])

    token_totals = {
        edition: {
            "literal": sum(len(rebuilt["tokens"][(edition, page, "LIT")]) for page in rebuilt["panel"]["pages"]),
            "root": sum(len(rebuilt["tokens"][(edition, page, "ROOT")]) for page in rebuilt["panel"]["pages"]),
        }
        for edition in EDITIONS
    }
    assert control["token_totals"] == token_totals
    assert control["eligible_features"] == rebuilt["features"]
    assert control["eligible_feature_count"] == len(rebuilt["features"]) == 359
    assert control["canonical_counts_sha256"] == rebuilt["canonical_hash"]
    checks.extend(["six token totals", "359 exact eligible features", "canonical count-matrix hash"])

    combos, weights = orbit()
    adjusted = robust(weights, rebuilt["adjusted"])
    raw = robust(weights, rebuilt["raw"])
    adjusted_max = adjusted.max(axis=1)
    raw_max = raw.max(axis=1)
    expected_quantiles = lambda values: {
        "p90": f"{np.quantile(values, .90):.12f}",
        "p95": f"{np.quantile(values, .95):.12f}",
        "p99": f"{np.quantile(values, .99):.12f}",
    }
    assert control["controls"]["assignment_count"] == len(combos) == 6435
    assert control["controls"]["adjusted_family_max_quantiles"] == expected_quantiles(adjusted_max)
    assert control["controls"]["raw_family_max_quantiles"] == expected_quantiles(raw_max)
    checks.extend(["complete 6435 orbit", "adjusted family-null quantiles", "raw family-null quantiles"])

    planted = np.zeros((15, 1))
    planted[list(combos[0]), 0] = 1
    planted_scores = robust(weights, {edition: planted for edition in EDITIONS})[:, 0]
    planted_tail = int(np.sum(planted_scores >= planted_scores[0] - 1e-12))
    disagreement = robust(weights, {"ZL3b": planted, "IT2a": planted, "RF1b": -planted})
    assert control["controls"]["planted_unique_tail"] == planted_tail == 1
    assert control["controls"]["planted_score"] == f"{planted_scores[0]:.12f}"
    assert disagreement.max() == 0
    checks.extend(["unique planted assignment", "planted score", "reading-disagreement collapse"])

    x = np.column_stack((np.ones(15), np.arange(15, dtype=np.float64)))
    projection = np.eye(15) - x @ np.linalg.inv(x.T @ x) @ x.T
    assert np.abs(projection @ np.ones((15, 1))).max() < 1e-12
    assert np.abs(projection @ np.arange(15, dtype=np.float64).reshape(-1, 1)).max() < 1e-12
    assert control["controls"]["projected_constant_max_abs"] == "0.000000000000"
    assert control["controls"]["projected_linear_order_max_abs"] == "0.000000000000"
    checks.extend(["constant nuisance removal", "linear-folio nuisance removal"])

    assert control["mode"] == "controls"
    assert control["status"] == "PASS_ANONYMOUS_CONTROLS_TARGET_UNRUN"
    assert control["controls"]["target_assignment_computed"] is False
    checks.extend(["controls-only mode", "target-computation false", "control status"])

    result = {
        "status": "PASS_INDEPENDENT_BERRY_CONTROLS_TARGET_AUTHORIZED_UNRUN",
        "imports_production_code": False,
        "control_sha256": digest(ROOT / CONTROL),
        "runner_sha256": digest(ROOT / RUNNER),
        "check_count": len(checks),
        "checks": checks,
        "eligible_feature_count": 359,
        "assignment_count": 6435,
        "target_artifact_exists": False,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
