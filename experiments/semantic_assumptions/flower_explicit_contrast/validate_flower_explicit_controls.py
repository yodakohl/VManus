#!/usr/bin/env python3
"""Independently reconstruct FLOWER001 controls without production imports."""

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
from scipy.optimize import linear_sum_assignment


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/flower_explicit_contrast")
DESIGN = BASE / "SOURCE_AND_METHOD_FREEZE.md"
RUNNER = BASE / "run_flower_explicit_contrast.py"
CONTROL = BASE / "CONTROL_RESULT.json"
TARGET = BASE / "TARGET_RESULT.json"
SHARED = Path("experiments/semantic_assumptions/berry_explicit_contrast/run_berry_explicit_contrast.py")
PAGES = Path("experiments/semantic_assumptions/results/existing_human_page_annotations.tsv")
INTERLINEAR = Path("experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv")
EDITIONS = ("ZL3b", "IT2a", "RF1b")
POS = "α: flower(s) seen from the side"
NEG = "α: no fruits or flowers"
BLOCKS = (
    ("f3r", "f2r", "f4v"),
    ("f7r", "f10v", "f11v"),
    ("f8r", "f17r", "f19r"),
    ("f25v", "f24v", "f27r"),
    ("f42r", "f32r", "f38r"),
    ("f47r", "f29v", "f44r"),
    ("f52v", "f49r", "f54r"),
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(131072), b""):
            value.update(chunk)
    return value.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def folio(page: str) -> int:
    match = re.match(r"^f(\d+)", page)
    assert match
    return int(match.group(1))


def literal(token: str) -> set[str]:
    result = {"LIT_TOKEN:" + token}
    for size in (2, 3, 4):
        if len(token) > size:
            result.add(f"LIT_PREFIX{size}:" + token[:size])
            result.add(f"LIT_SUFFIX{size}:" + token[-size:])
            result.update(
                f"LIT_INFIX{size}:" + token[start:start + size]
                for start in range(1, len(token) - size)
            )
    return result


def root(token: str) -> set[str]:
    atoms = token.split("+")
    result = {
        "ROOT_TOKEN:" + token,
        "ROOT_PREFIX:" + atoms[0],
        "ROOT_SUFFIX:" + atoms[-1],
    }
    result.update("ROOT_ATOM:" + atom for atom in atoms)
    result.update(
        "ROOT_BIGRAM:" + left + "+" + right
        for left, right in zip(atoms, atoms[1:])
    )
    return result


def feature_domain(feature: str) -> str:
    return "LIT" if feature.startswith("LIT_") else "ROOT"


def source_panel() -> dict[str, object]:
    page_rows = rows(ROOT / PAGES)
    all_positive = sorted(row["page"] for row in page_rows if POS in row["illustrations"])
    all_negative = sorted(row["page"] for row in page_rows if NEG in row["illustrations"])
    assert len(all_positive) == 19 and len(all_negative) == 7
    assert not set(all_positive) & set(all_negative)
    chosen_positive = [page for block in BLOCKS for page in block[1:]]
    chosen_negative = [block[0] for block in BLOCKS]
    assert set(chosen_negative) == set(all_negative)
    assert len(set(chosen_positive)) == 14 and set(chosen_positive) <= set(all_positive)
    unused = sorted(set(all_positive) - set(chosen_positive))

    slots = [page for page in sorted(all_negative, key=lambda item: (folio(item), item)) for _ in range(2)]
    negative_folios = {folio(page) for page in all_negative}
    representative_by_folio = {}
    for page in sorted(all_positive, key=lambda item: (folio(item), item)):
        if folio(page) not in negative_folios:
            representative_by_folio.setdefault(folio(page), page)
    candidates = list(representative_by_folio.values())
    costs = np.array([
        [abs(folio(negative) - folio(positive)) for positive in candidates]
        for negative in slots
    ])
    row_indices, columns = linear_sum_assignment(costs)
    minimum_distance = int(costs[row_indices, columns].sum())
    frozen_distance = sum(
        abs(folio(block[0]) - folio(page)) for block in BLOCKS for page in block[1:]
    )
    assert minimum_distance == frozen_distance == 72
    pages = [page for block in BLOCKS for page in block]
    return {
        "blocks": [list(block) for block in BLOCKS],
        "pages": pages,
        "positive": chosen_positive,
        "negative": chosen_negative,
        "all_source_positive": all_positive,
        "unused_source_positive": unused,
        "total_absolute_folio_distance": frozen_distance,
    }


def reconstruct() -> dict[str, object]:
    panel = source_panel()
    pages = panel["pages"]
    page_set = set(pages)
    selected = [
        row for row in rows(ROOT / INTERLINEAR)
        if row["page"] in page_set and row["grammar_scope"] == "CONFIRMED_PROSE"
    ]
    tokens: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    metadata: dict[tuple[str, str], set[tuple[str, str, str]]] = defaultdict(set)
    for row in selected:
        edition, page = row["edition"], row["page"]
        metadata[(edition, page)].add((row["section"], row["currier"], row["hand"]))
        tokens[(edition, page, "LIT")].extend(row["surface"].split())
        tokens[(edition, page, "ROOT")].extend(row["root_sequence"].split())
    assert set(metadata) == {(edition, page) for edition in EDITIONS for page in pages}
    assert all(value == {("H", "A", "1")} for value in metadata.values())

    hits: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    type_support: dict[tuple[str, str], set[str]] = defaultdict(set)
    length_den: dict[tuple[str, str, str], Counter[int]] = defaultdict(Counter)
    length_num: dict[tuple[str, str, str, str], Counter[int]] = defaultdict(Counter)
    edition_features = {}
    for edition in EDITIONS:
        found = set()
        for page in pages:
            for domain_name, extractor, size_fn in (
                ("LIT", literal, len),
                ("ROOT", root, lambda token: len(token.split("+"))),
            ):
                for token in tokens[(edition, page, domain_name)]:
                    size = size_fn(token)
                    length_den[(edition, page, domain_name)][size] += 1
                    for feature in extractor(token):
                        found.add(feature)
                        hits[(edition, page, domain_name)][feature] += 1
                        type_support[(edition, feature)].add(token)
                        length_num[(edition, page, domain_name, feature)][size] += 1
        edition_features[edition] = found
    common = set.intersection(*(edition_features[edition] for edition in EDITIONS))
    features = []
    for feature in sorted(common):
        domain_name = feature_domain(feature)
        accepted = True
        for edition in EDITIONS:
            values = [hits[(edition, page, domain_name)][feature] for page in pages]
            if sum(values) < 8 or sum(value > 0 for value in values) < 4:
                accepted = False
            if feature.startswith(("LIT_PREFIX", "LIT_SUFFIX", "LIT_INFIX")):
                if len(type_support[(edition, feature)]) < 4:
                    accepted = False
        if accepted:
            features.append(feature)

    page_order = np.array([folio(page) for page in pages], dtype=np.float64)
    page_order = (page_order - page_order.mean()) / page_order.std()
    nuisance = np.column_stack((np.ones(len(pages)), page_order))
    projection = np.eye(len(pages)) - nuisance @ np.linalg.inv(nuisance.T @ nuisance) @ nuisance.T
    raw = {}
    adjusted = {}
    canonical = []
    for edition in EDITIONS:
        raw_values = np.zeros((len(pages), len(features)))
        adjusted_values = np.zeros_like(raw_values)
        global_den = {"LIT": Counter(), "ROOT": Counter()}
        for domain_name in global_den:
            for page in pages:
                global_den[domain_name].update(length_den[(edition, page, domain_name)])
        global_num: dict[str, Counter[int]] = defaultdict(Counter)
        for feature in features:
            domain_name = feature_domain(feature)
            for page in pages:
                global_num[feature].update(length_num[(edition, page, domain_name, feature)])
        for column, feature in enumerate(features):
            domain_name = feature_domain(feature)
            for row_index, page in enumerate(pages):
                denominator = len(tokens[(edition, page, domain_name)])
                observed = hits[(edition, page, domain_name)][feature]
                expected = sum(
                    count * global_num[feature][size] / global_den[domain_name][size]
                    for size, count in length_den[(edition, page, domain_name)].items()
                )
                raw_values[row_index, column] = observed / denominator
                adjusted_values[row_index, column] = (observed - expected) / denominator
                canonical.append([edition, page, feature, observed, denominator])
        raw[edition] = projection @ raw_values
        adjusted[edition] = projection @ adjusted_values
    canonical_text = json.dumps(canonical, separators=(",", ":"), ensure_ascii=False)
    return {
        "panel": panel,
        "selected_rows": len(selected),
        "tokens": tokens,
        "features": features,
        "canonical_hash": hashlib.sha256(canonical_text.encode()).hexdigest(),
        "raw": raw,
        "adjusted": adjusted,
    }


def orbit() -> tuple[list[tuple[int, ...]], np.ndarray]:
    choices = list(itertools.product(range(3), repeat=7))
    weights = np.zeros((len(choices), 21))
    for row, assignment in enumerate(choices):
        for block, negative in enumerate(assignment):
            start = block * 3
            weights[row, start:start + 3] = .5 / 7
            weights[row, start + negative] = -1 / 7
    return choices, weights


def standardized(weights: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    effects = weights @ matrix
    scale = np.sqrt(np.mean(effects * effects, axis=0))
    output = np.zeros_like(effects)
    movable = scale > 1e-14
    output[:, movable] = effects[:, movable] / scale[movable]
    return output


def robust(weights: np.ndarray, matrices: dict[str, np.ndarray]) -> np.ndarray:
    stack = np.stack([standardized(weights, matrices[edition]) for edition in EDITIONS])
    return np.maximum(np.maximum(stack.min(axis=0), (-stack).min(axis=0)), 0)


def synthetic(choice: tuple[int, ...]) -> np.ndarray:
    values = np.ones((21, 1))
    for block, negative in enumerate(choice):
        values[block * 3 + negative, 0] = -1
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not (ROOT / TARGET).exists()
    control = json.loads((ROOT / CONTROL).read_text(encoding="utf-8"))
    rebuilt = reconstruct()
    checks = []

    expected_inputs = {str(path): digest(ROOT / path) for path in (DESIGN, SHARED, PAGES, INTERLINEAR)}
    assert control["inputs"] == expected_inputs
    assert control["implementation_sha256"] == digest(ROOT / RUNNER)
    checks.extend(["four input bindings", "runner binding", "target artifact absent"])

    assert control["panel"] == rebuilt["panel"]
    assert rebuilt["panel"]["total_absolute_folio_distance"] == 72
    assert control["confirmed_prose_locus_rows"] == rebuilt["selected_rows"] == 843
    assert control["metadata_state"] == "all 21 pages are section H Currier A hand 1 in every reading"
    checks.extend(["literal 19/7 source census", "minimum-distance frozen triplets", "843 confirmed-prose rows", "uniform H-A-hand1 metadata"])

    token_totals = {
        edition: {
            "literal": sum(len(rebuilt["tokens"][(edition, page, "LIT")]) for page in rebuilt["panel"]["pages"]),
            "root": sum(len(rebuilt["tokens"][(edition, page, "ROOT")]) for page in rebuilt["panel"]["pages"]),
        }
        for edition in EDITIONS
    }
    assert control["token_totals"] == token_totals
    assert control["eligible_features"] == rebuilt["features"]
    assert control["eligible_feature_count"] == len(rebuilt["features"]) == 430
    assert control["canonical_counts_sha256"] == rebuilt["canonical_hash"]
    checks.extend(["six token totals", "430-feature identity", "canonical count-matrix hash"])

    choices, weights = orbit()
    adjusted = robust(weights, rebuilt["adjusted"])
    raw = robust(weights, rebuilt["raw"])
    adjusted_family = adjusted.max(axis=1)
    raw_family = raw.max(axis=1)
    quantiles = lambda values: {
        key: f"{np.quantile(values, probability):.12f}"
        for key, probability in (("p90", .90), ("p95", .95), ("p99", .99))
    }
    assert control["controls"]["assignment_count"] == len(choices) == 2187
    assert control["controls"]["adjusted_family_max_quantiles"] == quantiles(adjusted_family)
    assert control["controls"]["raw_family_max_quantiles"] == quantiles(raw_family)
    checks.extend(["complete 2187 blocked orbit", "adjusted family-null quantiles", "raw family-null quantiles"])

    planted_choice = tuple(control["controls"]["planted_assignment"])
    planted_index = choices.index(planted_choice)
    planted = synthetic(planted_choice)
    planted_scores = robust(weights, {edition: planted for edition in EDITIONS})[:, 0]
    assert control["controls"]["planted_unique_tail"] == int(np.sum(planted_scores >= planted_scores[planted_index] - 1e-12)) == 1
    assert control["controls"]["planted_score"] == f"{planted_scores[planted_index]:.12f}"
    disagreement = robust(weights, {"ZL3b": planted, "IT2a": planted, "RF1b": -planted})[:, 0]
    assert control["controls"]["reading_disagreement_max"] == f"{disagreement.max():.12f}" == "0.000000000000"
    checks.extend(["unique synthetic plant", "synthetic score", "reading-disagreement collapse"])

    constant = np.concatenate([np.full(3, block) for block in range(7)]).reshape(-1, 1)
    constant_scores = robust(weights, {edition: constant for edition in EDITIONS})[:, 0]
    assert control["controls"]["block_constant_max"] == f"{constant_scores.max():.12f}" == "0.000000000000"
    tie = np.zeros((21, 1))
    for block in range(6):
        tie[block * 3:block * 3 + 3, 0] = (1, 0, 0)
    tie_scores = robust(weights, {edition: tie for edition in EDITIONS})[:, 0]
    tie_top = tie_scores.max()
    assert control["controls"]["tie_top_count_inclusive"] == int(np.sum(tie_scores >= tie_top - 1e-12)) == 3
    assert control["controls"]["tie_strict_above_top"] == int(np.sum(tie_scores > tie_top + 1e-12)) == 0
    one_block = np.zeros((21, 1))
    one_block[:3, 0] = (1, 0, 0)
    assert control["controls"]["one_block_deleted_max"] == f"{np.max(np.abs(one_block[3:])):.12f}" == "0.000000000000"
    checks.extend(["block-constant cancellation", "inclusive three-way tie", "one-block deletion rejection"])

    assert control["mode"] == "controls"
    assert control["status"] == "PASS_ANONYMOUS_BLOCKED_FLOWER_CONTROLS_TARGET_UNRUN"
    assert control["controls"]["target_assignment_extracted"] is False
    checks.extend(["controls-only mode", "target extraction false", "control status"])

    result = {
        "status": "PASS_INDEPENDENT_FLOWER_CONTROLS_TARGET_AUTHORIZED_UNRUN",
        "imports_production_code": False,
        "control_sha256": digest(ROOT / CONTROL),
        "runner_sha256": digest(ROOT / RUNNER),
        "shared_dependency_sha256": digest(ROOT / SHARED),
        "check_count": len(checks),
        "checks": checks,
        "eligible_feature_count": len(rebuilt["features"]),
        "assignment_count": len(choices),
        "target_artifact_exists": False,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
