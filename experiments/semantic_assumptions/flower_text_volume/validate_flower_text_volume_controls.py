#!/usr/bin/env python3
"""Independently validate FLOWERVOL001 controls without production imports."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/flower_text_volume")
DESIGN = BASE / "SOURCE_AND_METHOD_FREEZE.md"
RUNNER = BASE / "run_flower_text_volume.py"
CONTROL = BASE / "CONTROL_RESULT.json"
TARGET = BASE / "TARGET_RESULT.json"
PARENT = Path("experiments/semantic_assumptions/flower_explicit_contrast/run_flower_explicit_contrast.py")
PANEL_SOURCE = Path("experiments/semantic_assumptions/flower_explicit_contrast/validate_flower_explicit_controls.py")
INTERLINEAR = Path("experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv")
EDITIONS = ("ZL3b", "IT2a", "RF1b")
MEASURES = ("LINE_COUNT", "TOKEN_COUNT", "TOKENS_PER_LINE")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(131072), b""):
            value.update(chunk)
    return value.hexdigest()


def load_panel_source():
    spec = importlib.util.spec_from_file_location("independent_flower_panel", ROOT / PANEL_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load independent panel source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def reconstruct() -> tuple[dict[str, object], dict[str, np.ndarray], str, int]:
    panel = load_panel_source().source_panel()
    pages = panel["pages"]
    selected = [
        row for row in rows(ROOT / INTERLINEAR)
        if row["page"] in set(pages) and row["grammar_scope"] == "CONFIRMED_PROSE"
    ]
    grouped = defaultdict(list)
    for row in selected:
        grouped[(row["edition"], row["page"])].append(row)
    assert set(grouped) == {(edition, page) for edition in EDITIONS for page in pages}
    matrices = {}
    canonical = []
    for edition in EDITIONS:
        values = np.zeros((21, 3))
        for index, page in enumerate(pages):
            page_rows = grouped[(edition, page)]
            line_count = len(page_rows)
            token_count = sum(int(row["word_count"]) for row in page_rows)
            row_values = (float(line_count), float(token_count), token_count / line_count)
            values[index] = row_values
            canonical.append([edition, page, *[f"{value:.12f}" for value in row_values]])
        matrices[edition] = values
    text = json.dumps(canonical, separators=(",", ":"))
    return panel, matrices, hashlib.sha256(text.encode()).hexdigest(), len(selected)


def orbit() -> tuple[list[tuple[int, ...]], np.ndarray]:
    choices = list(itertools.product(range(3), repeat=7))
    weights = np.zeros((2187, 21))
    for row, assignment in enumerate(choices):
        for block, negative in enumerate(assignment):
            start = block * 3
            weights[row, start:start + 3] = .5 / 7
            weights[row, start + negative] = -1 / 7
    return choices, weights


def standardized(weights: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    effect = weights @ matrix
    scale = np.sqrt(np.mean(effect * effect, axis=0))
    output = np.zeros_like(effect)
    movable = scale > 1e-14
    output[:, movable] = effect[:, movable] / scale[movable]
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
    panel, matrices, matrix_hash, selected_rows = reconstruct()
    checks = []

    assert control["inputs"] == {str(path): digest(ROOT / path) for path in (DESIGN, PARENT, INTERLINEAR)}
    assert control["implementation_sha256"] == digest(ROOT / RUNNER)
    assert control["panel"] == panel
    checks.extend(["three input bindings", "runner binding", "independent source panel", "target absent"])
    assert control["measures"] == list(MEASURES)
    assert control["measure_matrix_sha256"] == matrix_hash
    assert control["confirmed_prose_locus_rows"] == selected_rows == 843
    checks.extend(["three-measure identity", "measure-matrix hash", "843 prose rows"])

    choices, weights = orbit()
    scores = robust(weights, matrices)
    family = scores.max(axis=1)
    quantiles = {
        key: f"{np.quantile(family, probability):.12f}"
        for key, probability in (("p90", .90), ("p95", .95), ("p99", .99))
    }
    assert control["controls"]["assignment_count"] == len(choices) == 2187
    assert control["controls"]["family_max_quantiles"] == quantiles
    checks.extend(["complete 2187 orbit", "family-null quantiles"])

    planted_choice = tuple(control["controls"]["planted_assignment"])
    planted_index = choices.index(planted_choice)
    planted = synthetic(planted_choice)
    planted_scores = robust(weights, {edition: planted for edition in EDITIONS})[:, 0]
    assert control["controls"]["planted_unique_tail"] == int(np.sum(planted_scores >= planted_scores[planted_index] - 1e-12)) == 1
    disagreement = robust(weights, {"ZL3b": planted, "IT2a": planted, "RF1b": -planted})[:, 0]
    constant = np.concatenate([np.full(3, block) for block in range(7)]).reshape(-1, 1)
    constant_scores = robust(weights, {edition: constant for edition in EDITIONS})[:, 0]
    assert control["controls"]["reading_disagreement_max"] == f"{disagreement.max():.12f}" == "0.000000000000"
    assert control["controls"]["block_constant_max"] == f"{constant_scores.max():.12f}" == "0.000000000000"
    checks.extend(["unique synthetic plant", "reading-disagreement collapse", "block-constant cancellation"])

    assert control["mode"] == "controls"
    assert control["status"] == "PASS_FLOWER_TEXT_VOLUME_CONTROLS_TARGET_UNRUN"
    assert control["controls"]["target_assignment_extracted"] is False
    checks.extend(["controls-only mode", "target extraction false", "control status"])
    result = {
        "status": "PASS_INDEPENDENT_FLOWER_TEXT_VOLUME_CONTROLS_TARGET_AUTHORIZED_UNRUN",
        "imports_production_code": False,
        "control_sha256": digest(ROOT / CONTROL),
        "runner_sha256": digest(ROOT / RUNNER),
        "panel_source_sha256": digest(ROOT / PANEL_SOURCE),
        "check_count": len(checks),
        "checks": checks,
        "assignment_count": len(choices),
        "measure_count": len(MEASURES),
        "target_artifact_exists": False,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
