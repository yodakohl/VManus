#!/usr/bin/env python3
"""Validate the FLOWER001 target from the independent control reconstruction."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/flower_explicit_contrast")
INDEPENDENT = BASE / "validate_flower_explicit_controls.py"
RUNNER = BASE / "run_flower_explicit_contrast.py"
CONTROL = BASE / "CONTROL_RESULT.json"
TARGET = BASE / "TARGET_RESULT.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(131072), b""):
            value.update(chunk)
    return value.hexdigest()


def load_independent():
    spec = importlib.util.spec_from_file_location("flower_independent", ROOT / INDEPENDENT)
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
    choices, weights = independent.orbit()
    target = json.loads((ROOT / TARGET).read_text(encoding="utf-8"))
    control = json.loads((ROOT / CONTROL).read_text(encoding="utf-8"))
    checks = []

    assert target["mode"] == "target"
    assert target["inputs"] == control["inputs"]
    assert target["implementation_sha256"] == control["implementation_sha256"] == digest(ROOT / RUNNER)
    assert target["panel"] == control["panel"] == rebuilt["panel"]
    assert target["eligible_features"] == control["eligible_features"] == rebuilt["features"]
    assert target["canonical_counts_sha256"] == control["canonical_counts_sha256"] == rebuilt["canonical_hash"]
    checks.extend(["target mode", "input and runner bindings", "source panel", "430-feature identity", "count-matrix identity"])

    observed_choice = (0, 0, 0, 0, 0, 0, 0)
    target_index = choices.index(observed_choice)
    assert target_index == target["target"]["target_assignment_index"] == 0
    assert target["target"]["observed_negative_choice"] == list(observed_choice)
    checks.append("source-negative blocked assignment")

    adjusted = independent.robust(weights, rebuilt["adjusted"])
    raw = independent.robust(weights, rebuilt["raw"])
    adjusted_family = adjusted.max(axis=1)
    raw_family = raw.max(axis=1)
    panel = rebuilt["panel"]
    page_index = {page: index for index, page in enumerate(panel["pages"])}
    candidate_rows = []
    diagnostics = []

    for column, feature in enumerate(rebuilt["features"]):
        adjusted_value = adjusted[target_index, column]
        raw_value = raw[target_index, column]
        adjusted_p = np.sum(adjusted_family >= adjusted_value - 1e-12) / len(choices)
        raw_p = np.sum(raw_family >= raw_value - 1e-12) / len(choices)
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
        enriched = panel["positive"] if direction > 0 else panel["negative"]
        extractor = independent.literal if independent.feature_domain(feature) == "LIT" else independent.root
        domain_name = independent.feature_domain(feature)
        support_min = 0
        if direction:
            support_min = min(
                sum(
                    any(feature in extractor(token) for token in rebuilt["tokens"][(edition, page, domain_name)])
                    for page in enriched
                )
                for edition in EDITIONS
            )

        deletion_pass = bool(direction)
        block_direction_min = 0
        if direction:
            reading_counts = []
            for edition in EDITIONS:
                vector = rebuilt["adjusted"][edition][:, column]
                block_effects = np.array([
                    .5 * (vector[block * 3 + 1] + vector[block * 3 + 2]) - vector[block * 3]
                    for block in range(7)
                ])
                reading_counts.append(int(np.sum(direction * block_effects > 0)))
                for deleted in range(7):
                    if direction * np.delete(block_effects, deleted).mean() <= 0:
                        deletion_pass = False
            block_direction_min = min(reading_counts)

        passed = (
            adjusted_p <= .025
            and raw_p <= .05
            and same_sign
            and min(abs(value) for value in effects.values()) >= .015
            and support_min >= 4
            and deletion_pass
            and block_direction_min >= 5
        )
        row = {
            "feature": feature,
            "adjusted_robust_score": f"{adjusted_value:.12f}",
            "adjusted_familywise_p": f"{adjusted_p:.12f}",
            "raw_robust_score": f"{raw_value:.12f}",
            "raw_familywise_p": f"{raw_p:.12f}",
            "adjusted_effects": {key: f"{value:.12f}" for key, value in effects.items()},
            "raw_effects": {key: f"{value:.12f}" for key, value in raw_effects.items()},
            "same_direction_all_views": same_sign,
            "enriched_class_min_page_support": support_min,
            "all_block_deletions_same_direction": deletion_pass,
            "minimum_directional_blocks": block_direction_min,
            "passes_all_gates": passed,
        }
        diagnostics.append(row)
        if adjusted_p <= .20 or passed:
            candidate_rows.append(row)

    candidate_rows.sort(key=lambda row: (
        float(row["adjusted_familywise_p"]),
        -float(row["adjusted_robust_score"]),
        row["feature"],
    ))
    diagnostics.sort(key=lambda row: (
        float(row["adjusted_familywise_p"]),
        -float(row["adjusted_robust_score"]),
        row["feature"],
    ))
    assert target["target"]["candidate_rows_p_le_0_20"] == candidate_rows == []
    checks.extend(["all adjusted feature scores", "all raw sensitivity scores", "inclusive familywise tails", "empty diagnostic candidate table"])

    passes = [row for row in diagnostics if row["passes_all_gates"]]
    assert passes == target["target"]["passes"] == []
    assert target["target"]["pass_count"] == 0
    assert target["status"] == target["target"]["status"] == "FINAL_NONCONFIRMATION_SIDE_VIEW_FLOWER_PAGE_MORPHOLOGY"
    checks.extend(["zero all-gate passes", "final nonconfirmation decision"])

    best = diagnostics[0]
    assert float(best["adjusted_familywise_p"]) > .20
    checks.append("best diagnostic remains above p .20")

    result = {
        "status": "PASS_INDEPENDENT_FLOWER_TARGET_NONCONFIRMATION",
        "imports_production_runner": False,
        "independent_reconstruction_sha256": digest(ROOT / INDEPENDENT),
        "runner_sha256": digest(ROOT / RUNNER),
        "target_sha256": digest(ROOT / TARGET),
        "check_count": len(checks),
        "checks": checks,
        "assignment_count": len(choices),
        "feature_count": len(rebuilt["features"]),
        "pass_count": 0,
        "candidate_count_p_le_0_20": 0,
        "best_adjusted_diagnostic": {
            "feature": best["feature"],
            "adjusted_familywise_p": best["adjusted_familywise_p"],
            "raw_familywise_p": best["raw_familywise_p"],
        },
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
