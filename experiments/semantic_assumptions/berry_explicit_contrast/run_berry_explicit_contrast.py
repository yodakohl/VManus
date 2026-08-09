#!/usr/bin/env python3
"""Build controls or score the frozen explicit berry/no-fruit contrast."""

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
PAGES_PATH = Path("experiments/semantic_assumptions/results/existing_human_page_annotations.tsv")
INTERLINEAR = Path("experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv")
EDITIONS = ("ZL3b", "IT2a", "RF1b")
POSITIVE_PHRASE = "α: berries that have no added circles"
NEGATIVE_PHRASE = "α: no fruits or flowers"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def literal_features(token: str) -> set[str]:
    features = {f"LIT_TOKEN:{token}"}
    for length in (2, 3, 4):
        if len(token) <= length:
            continue
        features.add(f"LIT_PREFIX{length}:{token[:length]}")
        features.add(f"LIT_SUFFIX{length}:{token[-length:]}")
        for start in range(1, len(token) - length):
            features.add(f"LIT_INFIX{length}:{token[start:start + length]}")
    return features


def root_features(token: str) -> set[str]:
    atoms = token.split("+")
    features = {
        f"ROOT_TOKEN:{token}",
        f"ROOT_PREFIX:{atoms[0]}",
        f"ROOT_SUFFIX:{atoms[-1]}",
    }
    features.update(f"ROOT_ATOM:{atom}" for atom in atoms)
    features.update(
        f"ROOT_BIGRAM:{left}+{right}" for left, right in zip(atoms, atoms[1:])
    )
    return features


def domain(feature: str) -> str:
    return "LIT" if feature.startswith("LIT_") else "ROOT"


def folio_number(page: str) -> int:
    match = re.fullmatch(r"f(\d+)[rv](?:\d+)?", page)
    if not match:
        raise ValueError(f"nonordinary Herbal page ID {page}")
    return int(match.group(1))


def build_panel() -> dict[str, object]:
    page_rows = read_tsv(ROOT / PAGES_PATH)
    positive = sorted(
        row["page"] for row in page_rows if POSITIVE_PHRASE in row["illustrations"]
    )
    negative = sorted(
        row["page"] for row in page_rows if NEGATIVE_PHRASE in row["illustrations"]
    )
    if set(positive) & set(negative) or len(positive) != 8 or len(negative) != 7:
        raise ValueError("explicit source panel is not disjoint 8/7")
    pages = sorted(positive + negative, key=lambda value: (folio_number(value), value))
    return {"pages": pages, "positive": positive, "negative": negative}


def build_features(panel: dict[str, object]) -> dict[str, object]:
    pages = panel["pages"]
    page_set = set(pages)
    rows = [
        row
        for row in read_tsv(ROOT / INTERLINEAR)
        if row["page"] in page_set and row["grammar_scope"] == "CONFIRMED_PROSE"
    ]
    metadata: dict[tuple[str, str], set[tuple[str, str, str]]] = defaultdict(set)
    counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    length_counts: dict[tuple[str, str, str], Counter[int]] = defaultdict(Counter)
    length_hits: dict[tuple[str, str, str], dict[str, Counter[int]]] = defaultdict(
        lambda: defaultdict(Counter)
    )
    token_types: dict[tuple[str, str], set[str]] = defaultdict(set)
    locus_counts = Counter()

    for row in rows:
        edition, page = row["edition"], row["page"]
        metadata[(edition, page)].add((row["section"], row["currier"], row["hand"]))
        locus_counts[(edition, page)] += 1
        for token in row["surface"].split():
            key = (edition, page, "LIT")
            size = len(token)
            length_counts[key][size] += 1
            for feature in literal_features(token):
                counts[key][feature] += 1
                length_hits[key][feature][size] += 1
                token_types[(edition, feature)].add(token)
        for token in row["root_sequence"].split():
            key = (edition, page, "ROOT")
            size = len(token.split("+"))
            length_counts[key][size] += 1
            for feature in root_features(token):
                counts[key][feature] += 1
                length_hits[key][feature][size] += 1
                token_types[(edition, feature)].add(token)

    expected_keys = {(edition, page) for edition in EDITIONS for page in pages}
    if set(metadata) != expected_keys:
        raise ValueError("missing edition/page in explicit source panel")
    if any(values != {("H", "A", "1")} for values in metadata.values()):
        raise ValueError("source panel metadata is not uniformly H/A/1")

    all_features: dict[str, set[str]] = {}
    for edition in EDITIONS:
        present = set()
        for page in pages:
            present.update(counts[(edition, page, "LIT")])
            present.update(counts[(edition, page, "ROOT")])
        all_features[edition] = present
    common = set.intersection(*(all_features[edition] for edition in EDITIONS))
    eligible = []
    for feature in sorted(common):
        feature_domain = domain(feature)
        accepted = True
        for edition in EDITIONS:
            total_hits = sum(counts[(edition, page, feature_domain)][feature] for page in pages)
            page_hits = sum(counts[(edition, page, feature_domain)][feature] > 0 for page in pages)
            if total_hits < 8 or page_hits < 4:
                accepted = False
            if feature.startswith(("LIT_PREFIX", "LIT_SUFFIX", "LIT_INFIX")) and len(token_types[(edition, feature)]) < 4:
                accepted = False
        if accepted:
            eligible.append(feature)

    page_index = {page: index for index, page in enumerate(pages)}
    order = np.array([folio_number(page) for page in pages], dtype=np.float64)
    order = (order - order.mean()) / order.std()
    design = np.column_stack([np.ones(len(pages)), order])
    projector = np.eye(len(pages)) - design @ np.linalg.inv(design.T @ design) @ design.T

    raw: dict[str, np.ndarray] = {}
    adjusted: dict[str, np.ndarray] = {}
    support: dict[str, dict[str, list[int]]] = defaultdict(dict)
    canonical_counts = []
    for edition in EDITIONS:
        raw_matrix = np.zeros((len(pages), len(eligible)), dtype=np.float64)
        adjusted_matrix = np.zeros_like(raw_matrix)
        global_lengths: dict[str, Counter[int]] = defaultdict(Counter)
        global_feature_lengths: dict[str, Counter[int]] = defaultdict(Counter)
        for feature_domain in ("LIT", "ROOT"):
            for page in pages:
                global_lengths[feature_domain].update(
                    length_counts[(edition, page, feature_domain)]
                )
        for feature in eligible:
            feature_domain = domain(feature)
            for page in pages:
                global_feature_lengths[feature].update(
                    length_hits[(edition, page, feature_domain)][feature]
                )
        for column, feature in enumerate(eligible):
            feature_domain = domain(feature)
            presence = []
            for page in pages:
                row_index = page_index[page]
                denominator = sum(length_counts[(edition, page, feature_domain)].values())
                observed = counts[(edition, page, feature_domain)][feature]
                expected = 0.0
                for size, number in length_counts[(edition, page, feature_domain)].items():
                    global_denominator = global_lengths[feature_domain][size]
                    probability = global_feature_lengths[feature][size] / global_denominator
                    expected += number * probability
                raw_matrix[row_index, column] = observed / denominator
                adjusted_matrix[row_index, column] = (observed - expected) / denominator
                presence.append(int(observed > 0))
                canonical_counts.append(
                    [edition, page, feature, observed, denominator]
                )
            support[feature][edition] = presence
        raw[edition] = projector @ raw_matrix
        adjusted[edition] = projector @ adjusted_matrix

    canonical = json.dumps(canonical_counts, separators=(",", ":"), ensure_ascii=False)
    result = {
        "rows": rows,
        "metadata": metadata,
        "locus_counts": locus_counts,
        "features": eligible,
        "raw": raw,
        "adjusted": adjusted,
        "support": support,
        "canonical_counts_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "token_totals": {
            edition: {
                "literal": sum(sum(length_counts[(edition, page, "LIT")].values()) for page in pages),
                "root": sum(sum(length_counts[(edition, page, "ROOT")].values()) for page in pages),
            }
            for edition in EDITIONS
        },
    }
    return result


def assignments(page_count: int = 15, positive_count: int = 8) -> tuple[list[tuple[int, ...]], np.ndarray]:
    combinations = list(itertools.combinations(range(page_count), positive_count))
    weights = np.full((len(combinations), page_count), -1 / (page_count - positive_count))
    for row, combination in enumerate(combinations):
        weights[row, list(combination)] = 1 / positive_count
    return combinations, weights


def standardized(weights: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    differences = weights @ matrix
    scales = np.sqrt(np.mean(differences * differences, axis=0))
    output = np.zeros_like(differences)
    movable = scales > 1e-14
    output[:, movable] = differences[:, movable] / scales[movable]
    return output


def robust_scores(weights: np.ndarray, matrices: dict[str, np.ndarray]) -> np.ndarray:
    values = np.stack([standardized(weights, matrices[edition]) for edition in EDITIONS])
    return np.maximum(np.minimum.reduce(values), np.minimum.reduce(-values)).clip(min=0)


def controls(feature_data: dict[str, object]) -> dict[str, object]:
    combinations, weights = assignments()
    adjusted_scores = robust_scores(weights, feature_data["adjusted"])
    raw_scores = robust_scores(weights, feature_data["raw"])
    adjusted_max = adjusted_scores.max(axis=1)
    raw_max = raw_scores.max(axis=1)

    planted = np.zeros((15, 1), dtype=np.float64)
    planted[list(combinations[0]), 0] = 1.0
    planted_scores = robust_scores(weights, {edition: planted for edition in EDITIONS})[:, 0]
    planted_value = planted_scores[0]
    planted_tail = int(np.sum(planted_scores >= planted_value - 1e-12))
    disagreement = robust_scores(
        weights,
        {"ZL3b": planted, "IT2a": planted, "RF1b": -planted},
    )[:, 0]
    order = np.arange(15, dtype=np.float64).reshape(-1, 1)
    x = np.column_stack([np.ones(15), np.arange(15, dtype=np.float64)])
    projection = np.eye(15) - x @ np.linalg.inv(x.T @ x) @ x.T
    projected_order = projection @ order
    projected_constant = projection @ np.ones((15, 1))
    result = {
        "assignment_count": len(combinations),
        "feature_count": len(feature_data["features"]),
        "adjusted_family_max_quantiles": {
            "p90": f"{np.quantile(adjusted_max, .90):.12f}",
            "p95": f"{np.quantile(adjusted_max, .95):.12f}",
            "p99": f"{np.quantile(adjusted_max, .99):.12f}",
        },
        "raw_family_max_quantiles": {
            "p90": f"{np.quantile(raw_max, .90):.12f}",
            "p95": f"{np.quantile(raw_max, .95):.12f}",
            "p99": f"{np.quantile(raw_max, .99):.12f}",
        },
        "planted_unique_tail": planted_tail,
        "planted_score": f"{planted_value:.12f}",
        "reading_disagreement_max": f"{disagreement.max():.12f}",
        "projected_linear_order_max_abs": f"{np.abs(projected_order).max():.12f}",
        "projected_constant_max_abs": f"{np.abs(projected_constant).max():.12f}",
        "target_assignment_computed": False,
    }
    if result["assignment_count"] != 6435:
        raise ValueError("incomplete exact assignment space")
    if planted_tail != 1:
        raise ValueError("planted assignment is not unique")
    if disagreement.max() > 1e-12:
        raise ValueError("reading-disagreement control did not collapse")
    if np.abs(projected_order).max() > 1e-12 or np.abs(projected_constant).max() > 1e-12:
        raise ValueError("nuisance projection control failed")
    return result


def target_result(panel: dict[str, object], feature_data: dict[str, object]) -> dict[str, object]:
    combinations, weights = assignments()
    page_index = {page: index for index, page in enumerate(panel["pages"])}
    observed = tuple(sorted(page_index[page] for page in panel["positive"]))
    target_index = combinations.index(observed)
    adjusted = robust_scores(weights, feature_data["adjusted"])
    raw = robust_scores(weights, feature_data["raw"])
    family_adjusted = adjusted.max(axis=1)
    family_raw = raw.max(axis=1)
    candidates = []
    for column, feature in enumerate(feature_data["features"]):
        adjusted_value = adjusted[target_index, column]
        raw_value = raw[target_index, column]
        adjusted_p = int(np.sum(family_adjusted >= adjusted_value - 1e-12)) / len(combinations)
        raw_p = int(np.sum(family_raw >= raw_value - 1e-12)) / len(combinations)
        effects = {
            edition: float(weights[target_index] @ feature_data["adjusted"][edition][:, column])
            for edition in EDITIONS
        }
        raw_effects = {
            edition: float(weights[target_index] @ feature_data["raw"][edition][:, column])
            for edition in EDITIONS
        }
        signs = [np.sign(value) for value in effects.values()] + [np.sign(value) for value in raw_effects.values()]
        same_sign = all(value > 0 for value in signs) or all(value < 0 for value in signs)
        direction = 1 if all(value > 0 for value in signs) else -1 if all(value < 0 for value in signs) else 0
        enriched_pages = panel["positive"] if direction > 0 else panel["negative"]
        support_min = min(
            sum(feature_data["support"][feature][edition][page_index[page]] for page in enriched_pages)
            for edition in EDITIONS
        ) if direction else 0
        loo_pass = True
        if direction:
            for edition in EDITIONS:
                vector = feature_data["adjusted"][edition][:, column]
                for deleted in range(15):
                    positives = [index for index in observed if index != deleted]
                    negatives = [index for index in range(15) if index not in observed and index != deleted]
                    difference = vector[positives].mean() - vector[negatives].mean()
                    if direction * difference <= 0:
                        loo_pass = False
        else:
            loo_pass = False
        passed = (
            adjusted_p <= .05
            and raw_p <= .10
            and same_sign
            and min(abs(value) for value in effects.values()) >= .015
            and support_min >= 4
            and loo_pass
        )
        if adjusted_p <= .20 or passed:
            candidates.append(
                {
                    "feature": feature,
                    "adjusted_robust_score": f"{adjusted_value:.12f}",
                    "adjusted_familywise_p": f"{adjusted_p:.12f}",
                    "raw_robust_score": f"{raw_value:.12f}",
                    "raw_familywise_p": f"{raw_p:.12f}",
                    "adjusted_effects": {key: f"{value:.12f}" for key, value in effects.items()},
                    "raw_effects": {key: f"{value:.12f}" for key, value in raw_effects.items()},
                    "same_direction_all_views": same_sign,
                    "enriched_class_min_page_support": support_min,
                    "all_page_deletions_same_direction": loo_pass,
                    "passes_all_gates": passed,
                }
            )
    candidates.sort(key=lambda row: (float(row["adjusted_familywise_p"]), -float(row["adjusted_robust_score"]), row["feature"]))
    passes = [row for row in candidates if row["passes_all_gates"]]
    status = "PROVISIONAL_EXPLICIT_BERRY_PAGE_PATTERN_CANDIDATE" if passes else "FINAL_NONCONFIRMATION_EXPLICIT_BERRY_PAGE_MORPHOLOGY"
    return {
        "status": status,
        "observed_positive_pages": panel["positive"],
        "observed_negative_pages": panel["negative"],
        "target_assignment_index": target_index,
        "candidate_rows_p_le_0_20": candidates,
        "pass_count": len(passes),
        "passes": passes,
        "decision_ceiling": "a pass is a page-field candidate only; no berry word negation noun plant language plaintext or translation",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("controls", "target"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    panel = build_panel()
    feature_data = build_features(panel)
    base = {
        "mode": args.mode,
        "inputs": {
            str(path): sha256(ROOT / path)
            for path in (DESIGN, PAGES_PATH, INTERLINEAR)
        },
        "implementation_sha256": sha256(Path(__file__)),
        "panel": panel,
        "metadata_state": "all 15 pages are section H Currier A hand 1 in every reading",
        "confirmed_prose_locus_rows": len(feature_data["rows"]),
        "token_totals": feature_data["token_totals"],
        "eligible_feature_count": len(feature_data["features"]),
        "eligible_features": feature_data["features"],
        "canonical_counts_sha256": feature_data["canonical_counts_sha256"],
        "alternate_reading_rule": "synchronized minimum effect across alternate readings; not independent replication",
    }
    if args.mode == "controls":
        base["controls"] = controls(feature_data)
        base["status"] = "PASS_ANONYMOUS_CONTROLS_TARGET_UNRUN"
    else:
        base["target"] = target_result(panel, feature_data)
        base["status"] = base["target"]["status"]
    data = json.dumps(base, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(data, encoding="utf-8")


if __name__ == "__main__":
    main()
