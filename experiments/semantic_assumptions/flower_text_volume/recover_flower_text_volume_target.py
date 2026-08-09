#!/usr/bin/env python3
"""Recover FLOWERVOL001 after production JSON serialization failure."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/flower_text_volume")
INDEPENDENT = BASE / "validate_flower_text_volume_controls.py"
RUNNER = BASE / "run_flower_text_volume.py"
CONTROL = BASE / "CONTROL_RESULT.json"
PRODUCTION_TARGET = BASE / "TARGET_RESULT.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
MEASURES = ("LINE_COUNT", "TOKEN_COUNT", "TOKENS_PER_LINE")
MATERIAL = {"LINE_COUNT": 1.0, "TOKEN_COUNT": 5.0, "TOKENS_PER_LINE": .25}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(131072), b""):
            value.update(chunk)
    return value.hexdigest()


def load_independent():
    spec = importlib.util.spec_from_file_location("volume_independent", ROOT / INDEPENDENT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load independent controls")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if (ROOT / PRODUCTION_TARGET).exists():
        raise RuntimeError("unexpected production target artifact")
    independent = load_independent()
    panel, matrices, matrix_hash, selected_rows = independent.reconstruct()
    choices, weights = independent.orbit()
    scores = independent.robust(weights, matrices)
    family = scores.max(axis=1)
    target_index = choices.index((0, 0, 0, 0, 0, 0, 0))
    rows = []
    for column, measure in enumerate(MEASURES):
        observed = scores[target_index, column]
        p_value = np.sum(family >= observed - 1e-12) / len(choices)
        effects = {
            edition: float(weights[target_index] @ matrices[edition][:, column])
            for edition in EDITIONS
        }
        signs = [np.sign(value) for value in effects.values()]
        same_sign = bool(all(value > 0 for value in signs) or all(value < 0 for value in signs))
        direction = 1 if all(value > 0 for value in signs) else -1 if all(value < 0 for value in signs) else 0
        deletion_pass = bool(direction)
        block_min = 0
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
            block_min = min(counts)
        passed = bool(
            p_value <= .05
            and same_sign
            and min(abs(value) for value in effects.values()) >= MATERIAL[measure]
            and deletion_pass
            and block_min >= 5
        )
        rows.append({
            "measure": measure,
            "robust_score": f"{observed:.12f}",
            "familywise_p": f"{p_value:.12f}",
            "effects": {key: f"{value:.12f}" for key, value in effects.items()},
            "same_direction_all_readings": same_sign,
            "material_threshold": f"{MATERIAL[measure]:.12f}",
            "all_block_deletions_same_direction": bool(deletion_pass),
            "minimum_directional_blocks": int(block_min),
            "passes_all_gates": passed,
        })
    passes = [row for row in rows if row["passes_all_gates"]]
    status = (
        "RECOVERED_PROVISIONAL_FLOWER_TEXT_VOLUME_ASSOCIATION"
        if passes else "RECOVERED_NONCONFIRMATION_FLOWER_TEXT_VOLUME"
    )
    control = json.loads((ROOT / CONTROL).read_text(encoding="utf-8"))
    result = {
        "status": status,
        "production_target_artifact_exists": False,
        "production_failure": "numpy_boolean_json_serialization_after_score",
        "production_runner_sha256": digest(ROOT / RUNNER),
        "control_sha256": digest(ROOT / CONTROL),
        "independent_implementation_sha256": digest(ROOT / INDEPENDENT),
        "inputs": control["inputs"],
        "panel": panel,
        "measure_matrix_sha256": matrix_hash,
        "confirmed_prose_locus_rows": selected_rows,
        "target_assignment_index": target_index,
        "measure_rows": rows,
        "pass_count": len(passes),
        "passes": passes,
        "claim_ceiling": "recovered whole-page volume result only; no FLOWER FRUIT NO lexeme plaintext or translation",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
