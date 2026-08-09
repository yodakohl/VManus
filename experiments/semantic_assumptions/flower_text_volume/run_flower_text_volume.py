#!/usr/bin/env python3
"""Run controls or the frozen FLOWERVOL001 root-free target."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/flower_text_volume")
DESIGN = BASE / "SOURCE_AND_METHOD_FREEZE.md"
PARENT = Path("experiments/semantic_assumptions/flower_explicit_contrast/run_flower_explicit_contrast.py")
INTERLINEAR = Path("experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv")
TARGET = BASE / "TARGET_RESULT.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
MEASURES = ("LINE_COUNT", "TOKEN_COUNT", "TOKENS_PER_LINE")
MATERIAL = {"LINE_COUNT": 1.0, "TOKEN_COUNT": 5.0, "TOKENS_PER_LINE": .25}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def load_parent():
    spec = importlib.util.spec_from_file_location("flower_parent", ROOT / PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen FLOWER001 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def build_measures(panel: dict[str, object]) -> tuple[dict[str, np.ndarray], str, int]:
    pages = panel["pages"]
    page_set = set(pages)
    selected = [
        row for row in read_tsv(ROOT / INTERLINEAR)
        if row["page"] in page_set and row["grammar_scope"] == "CONFIRMED_PROSE"
    ]
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in selected:
        grouped[(row["edition"], row["page"])].append(row)
    if set(grouped) != {(edition, page) for edition in EDITIONS for page in pages}:
        raise RuntimeError("volume panel coverage drift")
    matrices = {}
    canonical = []
    for edition in EDITIONS:
        values = np.zeros((len(pages), len(MEASURES)), dtype=np.float64)
        for index, page in enumerate(pages):
            page_rows = grouped[(edition, page)]
            lines = len(page_rows)
            tokens = sum(int(row["word_count"]) for row in page_rows)
            row_values = (float(lines), float(tokens), tokens / lines)
            values[index] = row_values
            canonical.append([edition, page, *[f"{value:.12f}" for value in row_values]])
        matrices[edition] = values
    text = json.dumps(canonical, separators=(",", ":"))
    return matrices, hashlib.sha256(text.encode()).hexdigest(), len(selected)


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


def controls(parent, matrices: dict[str, np.ndarray]) -> dict[str, object]:
    choices, weights = parent.orbit()
    scores = robust(weights, matrices)
    family = scores.max(axis=1)
    planted_choice = (2, 1, 0, 2, 1, 0, 2)
    planted_index = choices.index(planted_choice)
    planted = parent.synthetic_matrix(planted_choice)
    planted_scores = robust(weights, {edition: planted for edition in EDITIONS})[:, 0]
    disagreement = robust(weights, {"ZL3b": planted, "IT2a": planted, "RF1b": -planted})[:, 0]
    constant = np.concatenate([np.full(3, block) for block in range(7)]).reshape(-1, 1)
    constant_scores = robust(weights, {edition: constant for edition in EDITIONS})[:, 0]
    result = {
        "assignment_count": len(choices),
        "measure_count": len(MEASURES),
        "family_max_quantiles": {
            key: f"{np.quantile(family, probability):.12f}"
            for key, probability in (("p90", .90), ("p95", .95), ("p99", .99))
        },
        "planted_assignment": list(planted_choice),
        "planted_unique_tail": int(np.sum(planted_scores >= planted_scores[planted_index] - 1e-12)),
        "planted_score": f"{planted_scores[planted_index]:.12f}",
        "reading_disagreement_max": f"{disagreement.max():.12f}",
        "block_constant_max": f"{constant_scores.max():.12f}",
        "target_assignment_extracted": False,
    }
    if result["planted_unique_tail"] != 1:
        raise RuntimeError("synthetic volume plant is not unique")
    if disagreement.max() > 1e-12 or constant_scores.max() > 1e-12:
        raise RuntimeError("volume negative control failed")
    return result


def target_result(parent, matrices: dict[str, np.ndarray]) -> dict[str, object]:
    choices, weights = parent.orbit()
    target_index = choices.index((0, 0, 0, 0, 0, 0, 0))
    scores = robust(weights, matrices)
    family = scores.max(axis=1)
    rows = []
    for column, measure in enumerate(MEASURES):
        observed = scores[target_index, column]
        p_value = np.sum(family >= observed - 1e-12) / len(choices)
        effects = {
            edition: float(weights[target_index] @ matrices[edition][:, column])
            for edition in EDITIONS
        }
        signs = [np.sign(value) for value in effects.values()]
        same_sign = all(value > 0 for value in signs) or all(value < 0 for value in signs)
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
        passed = (
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
            "all_block_deletions_same_direction": deletion_pass,
            "minimum_directional_blocks": block_min,
            "passes_all_gates": passed,
        })
    passes = [row for row in rows if row["passes_all_gates"]]
    return {
        "status": "PROVISIONAL_FLOWER_TEXT_VOLUME_ASSOCIATION" if passes else "FINAL_NONCONFIRMATION_FLOWER_TEXT_VOLUME",
        "target_assignment_index": target_index,
        "measure_rows": rows,
        "pass_count": len(passes),
        "passes": passes,
        "claim_ceiling": "whole-page text-volume association only; no FLOWER FRUIT NO lexeme plaintext or translation",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("controls", "target"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    parent = load_parent()
    panel = parent.build_panel()
    matrices, matrix_hash, selected_rows = build_measures(panel)
    base = {
        "mode": args.mode,
        "inputs": {str(path): digest(ROOT / path) for path in (DESIGN, PARENT, INTERLINEAR)},
        "implementation_sha256": digest(Path(__file__)),
        "panel": panel,
        "measures": list(MEASURES),
        "measure_matrix_sha256": matrix_hash,
        "confirmed_prose_locus_rows": selected_rows,
        "alternate_reading_rule": "synchronized minimum effect; alternate readings are not replications",
    }
    if args.mode == "controls":
        if (ROOT / TARGET).exists():
            raise RuntimeError("target artifact exists during controls")
        base["controls"] = controls(parent, matrices)
        base["status"] = "PASS_FLOWER_TEXT_VOLUME_CONTROLS_TARGET_UNRUN"
    else:
        base["target"] = target_result(parent, matrices)
        base["status"] = base["target"]["status"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(base, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
