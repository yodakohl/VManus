#!/usr/bin/env python3
"""Validate BERRY001 target using the independent control reconstruction."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/berry_explicit_contrast")
INDEPENDENT = BASE / "validate_berry_explicit_controls.py"
RUNNER = BASE / "run_berry_explicit_contrast.py"
CONTROL = BASE / "CONTROL_RESULT.json"
TARGET = BASE / "TARGET_RESULT.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def load_independent():
    spec = importlib.util.spec_from_file_location("berry_independent", ROOT / INDEPENDENT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load independent reconstruction")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    independent = load_independent()
    rebuilt = independent.reconstruct()
    combinations, weights = independent.orbit()
    target = json.loads((ROOT / TARGET).read_text(encoding="utf-8"))
    control = json.loads((ROOT / CONTROL).read_text(encoding="utf-8"))
    checks = []

    assert target["mode"] == "target"
    assert target["inputs"] == control["inputs"]
    assert target["implementation_sha256"] == control["implementation_sha256"] == sha256(ROOT / RUNNER)
    assert target["panel"] == control["panel"] == rebuilt["panel"]
    assert target["eligible_features"] == control["eligible_features"] == rebuilt["features"]
    assert target["canonical_counts_sha256"] == control["canonical_counts_sha256"] == rebuilt["canonical_hash"]
    checks.extend(["target mode", "input and runner bindings", "source panel", "359-feature identity", "count-matrix identity"])

    pages = rebuilt["panel"]["pages"]
    page_index = {page: index for index, page in enumerate(pages)}
    observed = tuple(sorted(page_index[page] for page in rebuilt["panel"]["positive"]))
    target_index = combinations.index(observed)
    assert target_index == target["target"]["target_assignment_index"] == 4897
    checks.append("source-positive assignment index")

    adjusted = independent.robust(weights, rebuilt["adjusted"])
    raw = independent.robust(weights, rebuilt["raw"])
    adjusted_family = adjusted.max(axis=1)
    raw_family = raw.max(axis=1)
    candidate_rows = []
    for column, feature in enumerate(rebuilt["features"]):
        adjusted_value = adjusted[target_index, column]
        raw_value = raw[target_index, column]
        adjusted_p = np.sum(adjusted_family >= adjusted_value - 1e-12) / len(combinations)
        raw_p = np.sum(raw_family >= raw_value - 1e-12) / len(combinations)
        effects = {
            edition: float(weights[target_index] @ rebuilt["adjusted"][edition][:, column])
            for edition in EDITIONS
        }
        raw_effects = {
            edition: float(weights[target_index] @ rebuilt["raw"][edition][:, column])
            for edition in EDITIONS
        }
        signs = [np.sign(value) for value in effects.values()] + [
            np.sign(value) for value in raw_effects.values()
        ]
        same_sign = all(value > 0 for value in signs) or all(value < 0 for value in signs)
        direction = 1 if all(value > 0 for value in signs) else -1 if all(value < 0 for value in signs) else 0
        enriched = rebuilt["panel"]["positive"] if direction > 0 else rebuilt["panel"]["negative"]
        feature_domain = independent.feature_domain(feature)
        extractor = independent.lit if feature_domain == "LIT" else independent.roots
        support_min = 0
        if direction:
            support_min = min(
                sum(
                    any(feature in extractor(token) for token in rebuilt["tokens"][(edition, page, feature_domain)])
                    for page in enriched
                )
                for edition in EDITIONS
            )
        loo = bool(direction)
        if direction:
            for edition in EDITIONS:
                vector = rebuilt["adjusted"][edition][:, column]
                for deleted in range(15):
                    positives = [index for index in observed if index != deleted]
                    negatives = [
                        index
                        for index in range(15)
                        if index not in observed and index != deleted
                    ]
                    effect = vector[positives].mean() - vector[negatives].mean()
                    if direction * effect <= 0:
                        loo = False
        passed = (
            adjusted_p <= .05
            and raw_p <= .10
            and same_sign
            and min(abs(value) for value in effects.values()) >= .015
            and support_min >= 4
            and loo
        )
        if adjusted_p <= .20 or passed:
            candidate_rows.append(
                {
                    "feature": feature,
                    "adjusted_robust_score": f"{adjusted_value:.12f}",
                    "adjusted_familywise_p": f"{adjusted_p:.12f}",
                    "raw_robust_score": f"{raw_value:.12f}",
                    "raw_familywise_p": f"{raw_p:.12f}",
                    "adjusted_effects": {
                        key: f"{value:.12f}" for key, value in effects.items()
                    },
                    "raw_effects": {
                        key: f"{value:.12f}" for key, value in raw_effects.items()
                    },
                    "same_direction_all_views": same_sign,
                    "enriched_class_min_page_support": support_min,
                    "all_page_deletions_same_direction": loo,
                    "passes_all_gates": passed,
                }
            )
    candidate_rows.sort(
        key=lambda row: (
            float(row["adjusted_familywise_p"]),
            -float(row["adjusted_robust_score"]),
            row["feature"],
        )
    )
    assert target["target"]["candidate_rows_p_le_0_20"] == candidate_rows
    checks.extend(["all primary feature scores", "all raw sensitivity scores", "inclusive familywise tails", "candidate row reconstruction"])

    passes = [row for row in candidate_rows if row["passes_all_gates"]]
    assert passes == target["target"]["passes"] == []
    assert target["target"]["pass_count"] == 0
    assert target["status"] == target["target"]["status"] == "FINAL_NONCONFIRMATION_EXPLICIT_BERRY_PAGE_MORPHOLOGY"
    checks.extend(["zero all-gate passes", "final nonconfirmation decision"])

    assert len(candidate_rows) == 1
    near = candidate_rows[0]
    assert near["feature"] == "ROOT_PREFIX:oii"
    assert near["adjusted_familywise_p"] == "0.080963480963"
    assert near["raw_familywise_p"] == "0.139238539239"
    assert near["enriched_class_min_page_support"] == 6
    assert near["all_page_deletions_same_direction"] is True
    assert not bool(near["passes_all_gates"])
    checks.extend(["sole near-miss identity", "near-miss exact tails", "near-miss support and deletion", "near-miss rejection"])

    result = {
        "status": "PASS_INDEPENDENT_BERRY_TARGET_NONCONFIRMATION",
        "imports_production_runner": False,
        "independent_reconstruction_sha256": sha256(ROOT / INDEPENDENT),
        "runner_sha256": sha256(ROOT / RUNNER),
        "target_sha256": sha256(ROOT / TARGET),
        "check_count": len(checks),
        "checks": checks,
        "assignment_count": len(combinations),
        "feature_count": len(rebuilt["features"]),
        "pass_count": 0,
        "near_miss": "ROOT_PREFIX:oii",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
