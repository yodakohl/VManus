#!/usr/bin/env python3
"""Validate the independently recovered FLOWERVOL001 target result."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/flower_text_volume")
INDEPENDENT = BASE / "validate_flower_text_volume_controls.py"
RUNNER = BASE / "run_flower_text_volume.py"
CONTROL = BASE / "CONTROL_RESULT.json"
RECOVERED = BASE / "RECOVERED_TARGET_RESULT.json"
PRODUCTION_TARGET = BASE / "TARGET_RESULT.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
MEASURES = ("LINE_COUNT", "TOKEN_COUNT", "TOKENS_PER_LINE")
MATERIAL = (1.0, 5.0, .25)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(131072), b""):
            value.update(chunk)
    return value.hexdigest()


def load_independent():
    spec = importlib.util.spec_from_file_location("volume_matrix_source", ROOT / INDEPENDENT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load validated matrix source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not (ROOT / PRODUCTION_TARGET).exists()
    result = json.loads((ROOT / RECOVERED).read_text(encoding="utf-8"))
    control = json.loads((ROOT / CONTROL).read_text(encoding="utf-8"))
    module = load_independent()
    panel, matrices, matrix_hash, selected_rows = module.reconstruct()
    checks = []

    assert result["production_target_artifact_exists"] is False
    assert result["production_failure"] == "numpy_boolean_json_serialization_after_score"
    assert result["production_runner_sha256"] == control["implementation_sha256"] == digest(ROOT / RUNNER)
    assert result["control_sha256"] == digest(ROOT / CONTROL)
    assert result["panel"] == panel and result["measure_matrix_sha256"] == matrix_hash
    assert result["confirmed_prose_locus_rows"] == selected_rows == 843
    checks.extend(["production target absent", "failure mode", "runner binding", "control binding", "panel and matrix binding", "843 prose rows"])

    choices = list(itertools.product(range(3), repeat=7))
    effects = {edition: np.zeros((len(choices), 3)) for edition in EDITIONS}
    for assignment_index, assignment in enumerate(choices):
        for edition in EDITIONS:
            for measure in range(3):
                total = 0.0
                for block, negative in enumerate(assignment):
                    values = matrices[edition][block * 3:block * 3 + 3, measure]
                    total += (values.sum() - values[negative]) / 2 - values[negative]
                effects[edition][assignment_index, measure] = total / 7
    standardized = {}
    for edition in EDITIONS:
        scale = np.sqrt(np.mean(effects[edition] ** 2, axis=0))
        standardized[edition] = effects[edition] / scale
    stack = np.stack([standardized[edition] for edition in EDITIONS])
    scores = np.maximum(np.maximum(stack.min(axis=0), (-stack).min(axis=0)), 0)
    family = scores.max(axis=1)
    target_index = choices.index((0, 0, 0, 0, 0, 0, 0))
    assert result["target_assignment_index"] == target_index == 0
    checks.extend(["independent scalar 2187 orbit", "target assignment"])

    rebuilt_rows = []
    for column, measure in enumerate(MEASURES):
        p_value = np.sum(family >= scores[target_index, column] - 1e-12) / len(choices)
        observed_effects = {edition: float(effects[edition][target_index, column]) for edition in EDITIONS}
        signs = [np.sign(value) for value in observed_effects.values()]
        same_sign = bool(all(value > 0 for value in signs) or all(value < 0 for value in signs))
        direction = 1 if all(value > 0 for value in signs) else -1 if all(value < 0 for value in signs) else 0
        deletion_pass = bool(direction)
        minimum_blocks = 0
        if direction:
            counts = []
            for edition in EDITIONS:
                vector = matrices[edition][:, column]
                block_effects = np.array([
                    .5 * (vector[block * 3 + 1] + vector[block * 3 + 2]) - vector[block * 3]
                    for block in range(7)
                ])
                counts.append(int(np.sum(direction * block_effects > 0)))
                for deleted in range(7):
                    if direction * np.delete(block_effects, deleted).mean() <= 0:
                        deletion_pass = False
            minimum_blocks = min(counts)
        passed = bool(
            p_value <= .05
            and same_sign
            and min(abs(value) for value in observed_effects.values()) >= MATERIAL[column]
            and deletion_pass
            and minimum_blocks >= 5
        )
        rebuilt_rows.append({
            "measure": measure,
            "robust_score": f"{scores[target_index, column]:.12f}",
            "familywise_p": f"{p_value:.12f}",
            "effects": {key: f"{value:.12f}" for key, value in observed_effects.items()},
            "same_direction_all_readings": same_sign,
            "material_threshold": f"{MATERIAL[column]:.12f}",
            "all_block_deletions_same_direction": bool(deletion_pass),
            "minimum_directional_blocks": int(minimum_blocks),
            "passes_all_gates": passed,
        })
    assert result["measure_rows"] == rebuilt_rows
    assert result["pass_count"] == 0 and result["passes"] == []
    assert result["status"] == "RECOVERED_NONCONFIRMATION_FLOWER_TEXT_VOLUME"
    assert rebuilt_rows[0]["familywise_p"] == "0.469593049840"
    assert rebuilt_rows[1]["familywise_p"] == "0.325560128029"
    assert rebuilt_rows[2]["familywise_p"] == "1.000000000000"
    checks.extend(["three exact recovered rows", "zero passes", "recovered decision", "line tail", "token tail", "density tail"])

    output = {
        "status": "PASS_VALIDATED_RECOVERED_FLOWER_TEXT_VOLUME_NONCONFIRMATION",
        "imports_production_runner": False,
        "recovered_result_sha256": digest(ROOT / RECOVERED),
        "matrix_source_sha256": digest(ROOT / INDEPENDENT),
        "runner_sha256": digest(ROOT / RUNNER),
        "check_count": len(checks),
        "checks": checks,
        "assignment_count": len(choices),
        "measure_count": 3,
        "pass_count": 0,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
