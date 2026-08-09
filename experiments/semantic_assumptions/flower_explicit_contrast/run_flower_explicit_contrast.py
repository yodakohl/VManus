#!/usr/bin/env python3
"""Run controls or the frozen FLOWER001 blocked morphology target."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import re
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/flower_explicit_contrast")
DESIGN = BASE / "SOURCE_AND_METHOD_FREEZE.md"
SHARED = Path("experiments/semantic_assumptions/berry_explicit_contrast/run_berry_explicit_contrast.py")
PAGES = Path("experiments/semantic_assumptions/results/existing_human_page_annotations.tsv")
INTERLINEAR = Path("experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv")
TARGET = BASE / "TARGET_RESULT.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
POSITIVE_PHRASE = "α: flower(s) seen from the side"
NEGATIVE_PHRASE = "α: no fruits or flowers"
BLOCKS = (
    ("f3r", "f2r", "f4v"),
    ("f7r", "f10v", "f11v"),
    ("f8r", "f17r", "f19r"),
    ("f25v", "f24v", "f27r"),
    ("f42r", "f32r", "f38r"),
    ("f47r", "f29v", "f44r"),
    ("f52v", "f49r", "f54r"),
)
EXPECTED_UNUSED = ("f2v", "f32v", "f87r", "f8v", "f90v2")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def load_shared():
    spec = importlib.util.spec_from_file_location("berry_feature_builder", ROOT / SHARED)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen shared feature builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def build_panel() -> dict[str, object]:
    rows = read_tsv(ROOT / PAGES)
    positives = sorted(row["page"] for row in rows if POSITIVE_PHRASE in row["illustrations"])
    negatives = sorted(row["page"] for row in rows if NEGATIVE_PHRASE in row["illustrations"])
    if len(positives) != 19 or len(negatives) != 7 or set(positives) & set(negatives):
        raise RuntimeError("literal 19/7 source panel drift")
    frozen_negative = tuple(block[0] for block in BLOCKS)
    frozen_positive = tuple(page for block in BLOCKS for page in block[1:])
    if set(frozen_negative) != set(negatives):
        raise RuntimeError("frozen negative pages drift")
    if not set(frozen_positive).issubset(positives) or len(set(frozen_positive)) != 14:
        raise RuntimeError("frozen positive pages drift")
    unused = tuple(sorted(set(positives) - set(frozen_positive)))
    if unused != EXPECTED_UNUSED:
        raise RuntimeError("excluded positive pages drift")
    pages = [page for block in BLOCKS for page in block]
    folios = [int(re.match(r"^f(\d+)", page).group(1)) for page in pages]
    if len(set(folios)) != len(folios):
        raise RuntimeError("blocked panel repeats a physical folio")
    return {
        "blocks": [list(block) for block in BLOCKS],
        "pages": pages,
        "positive": list(frozen_positive),
        "negative": list(frozen_negative),
        "all_source_positive": positives,
        "unused_source_positive": list(unused),
        "total_absolute_folio_distance": 72,
    }


def orbit() -> tuple[list[tuple[int, ...]], np.ndarray]:
    choices = list(itertools.product(range(3), repeat=7))
    weights = np.zeros((len(choices), 21), dtype=np.float64)
    for row, assignment in enumerate(choices):
        for block, negative in enumerate(assignment):
            start = block * 3
            weights[row, start:start + 3] = .5 / 7
            weights[row, start + negative] = -1 / 7
    if len(choices) != 2187 or len({choice for choice in choices}) != 2187:
        raise RuntimeError("blocked orbit is incomplete")
    return choices, weights


def standardized(weights: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    effects = weights @ matrix
    scales = np.sqrt(np.mean(effects * effects, axis=0))
    result = np.zeros_like(effects)
    movable = scales > 1e-14
    result[:, movable] = effects[:, movable] / scales[movable]
    return result


def robust_scores(weights: np.ndarray, matrices: dict[str, np.ndarray]) -> np.ndarray:
    stack = np.stack([standardized(weights, matrices[edition]) for edition in EDITIONS])
    forward = np.min(stack, axis=0)
    reverse = np.min(-stack, axis=0)
    return np.maximum(np.maximum(forward, reverse), 0)


def synthetic_matrix(choice: tuple[int, ...]) -> np.ndarray:
    values = np.ones((21, 1), dtype=np.float64)
    for block, negative in enumerate(choice):
        values[block * 3 + negative, 0] = -1
    return values


def controls(feature_data: dict[str, object]) -> dict[str, object]:
    choices, weights = orbit()
    adjusted = robust_scores(weights, feature_data["adjusted"])
    raw = robust_scores(weights, feature_data["raw"])
    adjusted_family = adjusted.max(axis=1)
    raw_family = raw.max(axis=1)

    planted_choice = (2, 1, 0, 2, 1, 0, 2)
    planted_index = choices.index(planted_choice)
    planted = synthetic_matrix(planted_choice)
    planted_scores = robust_scores(weights, {edition: planted for edition in EDITIONS})[:, 0]
    planted_tail = int(np.sum(planted_scores >= planted_scores[planted_index] - 1e-12))

    disagreement = robust_scores(
        weights, {"ZL3b": planted, "IT2a": planted, "RF1b": -planted}
    )[:, 0]
    constant = np.concatenate(
        [np.full(3, block, dtype=np.float64) for block in range(7)]
    ).reshape(-1, 1)
    constant_scores = robust_scores(
        weights, {edition: constant for edition in EDITIONS}
    )[:, 0]

    tie = np.zeros((21, 1), dtype=np.float64)
    for block in range(6):
        tie[block * 3:block * 3 + 3, 0] = (1, 0, 0)
    tie_scores = robust_scores(weights, {edition: tie for edition in EDITIONS})[:, 0]
    tie_top = float(tie_scores.max())
    tie_count = int(np.sum(tie_scores >= tie_top - 1e-12))
    tie_strict = int(np.sum(tie_scores > tie_top + 1e-12))

    one_block = np.zeros((21, 1), dtype=np.float64)
    one_block[:3, 0] = (1, 0, 0)
    one_block_deleted_max = float(np.max(np.abs(one_block[3:])))

    result = {
        "assignment_count": len(choices),
        "feature_count": len(feature_data["features"]),
        "adjusted_family_max_quantiles": {
            key: f"{np.quantile(adjusted_family, value):.12f}"
            for key, value in (("p90", .90), ("p95", .95), ("p99", .99))
        },
        "raw_family_max_quantiles": {
            key: f"{np.quantile(raw_family, value):.12f}"
            for key, value in (("p90", .90), ("p95", .95), ("p99", .99))
        },
        "planted_assignment": list(planted_choice),
        "planted_unique_tail": planted_tail,
        "planted_score": f"{planted_scores[planted_index]:.12f}",
        "reading_disagreement_max": f"{disagreement.max():.12f}",
        "block_constant_max": f"{constant_scores.max():.12f}",
        "tie_top_count_inclusive": tie_count,
        "tie_strict_above_top": tie_strict,
        "one_block_deleted_max": f"{one_block_deleted_max:.12f}",
        "target_assignment_extracted": False,
    }
    if planted_tail != 1:
        raise RuntimeError("synthetic planted assignment is not unique")
    if disagreement.max() > 1e-12 or constant_scores.max() > 1e-12:
        raise RuntimeError("negative control did not collapse")
    if tie_count != 3 or tie_strict != 0:
        raise RuntimeError("inclusive tie fixture drift")
    if one_block_deleted_max != 0:
        raise RuntimeError("one-block leverage fixture drift")
    return result


def target_result(panel: dict[str, object], feature_data: dict[str, object]) -> dict[str, object]:
    choices, weights = orbit()
    observed_choice = (0, 0, 0, 0, 0, 0, 0)
    target_index = choices.index(observed_choice)
    adjusted = robust_scores(weights, feature_data["adjusted"])
    raw = robust_scores(weights, feature_data["raw"])
    adjusted_family = adjusted.max(axis=1)
    raw_family = raw.max(axis=1)
    page_index = {page: index for index, page in enumerate(panel["pages"])}
    candidates = []

    for column, feature in enumerate(feature_data["features"]):
        adjusted_value = adjusted[target_index, column]
        raw_value = raw[target_index, column]
        adjusted_p = np.sum(adjusted_family >= adjusted_value - 1e-12) / len(choices)
        raw_p = np.sum(raw_family >= raw_value - 1e-12) / len(choices)
        effects = {
            edition: float(weights[target_index] @ feature_data["adjusted"][edition][:, column])
            for edition in EDITIONS
        }
        raw_effects = {
            edition: float(weights[target_index] @ feature_data["raw"][edition][:, column])
            for edition in EDITIONS
        }
        signs = [np.sign(value) for value in effects.values()] + [
            np.sign(value) for value in raw_effects.values()
        ]
        same_sign = all(value > 0 for value in signs) or all(value < 0 for value in signs)
        direction = 1 if all(value > 0 for value in signs) else -1 if all(value < 0 for value in signs) else 0
        enriched = panel["positive"] if direction > 0 else panel["negative"]
        support_min = 0
        if direction:
            support_min = min(
                sum(feature_data["support"][feature][edition][page_index[page]] for page in enriched)
                for edition in EDITIONS
            )

        deletion_pass = bool(direction)
        block_direction_min = 0
        if direction:
            per_reading_counts = []
            for edition in EDITIONS:
                vector = feature_data["adjusted"][edition][:, column]
                block_effects = np.array([
                    .5 * (vector[block * 3 + 1] + vector[block * 3 + 2]) - vector[block * 3]
                    for block in range(7)
                ])
                per_reading_counts.append(int(np.sum(direction * block_effects > 0)))
                for deleted in range(7):
                    if direction * np.delete(block_effects, deleted).mean() <= 0:
                        deletion_pass = False
            block_direction_min = min(per_reading_counts)

        passed = (
            adjusted_p <= .025
            and raw_p <= .05
            and same_sign
            and min(abs(value) for value in effects.values()) >= .015
            and support_min >= 4
            and deletion_pass
            and block_direction_min >= 5
        )
        if adjusted_p <= .20 or passed:
            candidates.append({
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
            })
    candidates.sort(key=lambda row: (
        float(row["adjusted_familywise_p"]),
        -float(row["adjusted_robust_score"]),
        row["feature"],
    ))
    passes = [row for row in candidates if row["passes_all_gates"]]
    status = (
        "PROVISIONAL_SIDE_VIEW_FLOWER_PAGE_PATTERN_CANDIDATE"
        if passes else "FINAL_NONCONFIRMATION_SIDE_VIEW_FLOWER_PAGE_MORPHOLOGY"
    )
    return {
        "status": status,
        "observed_negative_choice": list(observed_choice),
        "target_assignment_index": target_index,
        "candidate_rows_p_le_0_20": candidates,
        "pass_count": len(passes),
        "passes": passes,
        "decision_ceiling": "page-field association only; no FLOWER FRUIT NO plant word language plaintext or translation",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("controls", "target"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    shared = load_shared()
    panel = build_panel()
    feature_data = shared.build_features(panel)
    base = {
        "mode": args.mode,
        "inputs": {
            str(path): digest(ROOT / path)
            for path in (DESIGN, SHARED, PAGES, INTERLINEAR)
        },
        "implementation_sha256": digest(Path(__file__)),
        "panel": panel,
        "metadata_state": "all 21 pages are section H Currier A hand 1 in every reading",
        "confirmed_prose_locus_rows": len(feature_data["rows"]),
        "token_totals": feature_data["token_totals"],
        "eligible_feature_count": len(feature_data["features"]),
        "eligible_features": feature_data["features"],
        "canonical_counts_sha256": feature_data["canonical_counts_sha256"],
        "alternate_reading_rule": "synchronized minimum effect across alternate readings; not independent replication",
    }
    if args.mode == "controls":
        if (ROOT / TARGET).exists():
            raise RuntimeError("target artifact already exists during controls")
        base["controls"] = controls(feature_data)
        base["status"] = "PASS_ANONYMOUS_BLOCKED_FLOWER_CONTROLS_TARGET_UNRUN"
    else:
        base["target"] = target_result(panel, feature_data)
        base["status"] = base["target"]["status"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(base, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
