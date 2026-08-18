#!/usr/bin/env python3
"""Independently rebuild GDT316 labels, LOFO scores, and alignment diagnostic."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt316_frozen_panel.tsv"
DESIGN = R / "gdt316_design.json"
PREDICTIONS = R / "gdt316_predictions.tsv"
FOLDS = R / "gdt316_folio_scores.tsv"
SECTIONS = R / "gdt316_section_scores.tsv"
NULL = R / "gdt316_null.tsv"
RESULT = R / "gdt316_result.json"
OUT = R / "gdt316_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    payload = json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b):
    return abs(float(a) - float(b)) < 5e-12


def matrices(train, test, include_prev_dy):
    cells = sorted({row["cell_id"] for row in train})

    def encode(rows):
        return np.array(
            [
                [1.0]
                + [float(row["cell_id"] == cell) for cell in cells]
                + ([float(row["prev_dy"])] if include_prev_dy else [])
                for row in rows
            ]
        )

    return encode(train), encode(test)


def fit(train_x, train_y, test_x, ridge):
    beta = np.zeros(train_x.shape[1])
    penalty = np.eye(len(beta)) * ridge
    penalty[0, 0] = 0
    for _ in range(100):
        p = 1 / (1 + np.exp(-np.clip(train_x @ beta, -30, 30)))
        weight = np.maximum(p * (1 - p), 1e-8)
        step = np.linalg.pinv(
            train_x.T @ (train_x * weight[:, None]) + penalty
        ) @ (train_x.T @ (train_y - p) - penalty @ beta)
        beta += step
        if abs(step).max() < 1e-10:
            break
    predicted = 1 / (1 + np.exp(-np.clip(test_x @ beta, -30, 30)))
    return np.clip(predicted, 0.01, 0.99), beta


def event_bits(probability, truth):
    return -(
        truth * np.log2(probability)
        + (1 - truth) * np.log2(1 - probability)
    )


def permute(truth, rows, seed, world):
    out = truth.copy()
    strata = defaultdict(list)
    for index, row in enumerate(rows):
        strata[(row["cell_id"], row["register"])].append(index)
    for key, indices in sorted(strata.items()):
        values = truth[indices].copy()
        digest = hashlib.sha256(
            f"{seed}|{world}|{key[0]}|{key[1]}".encode()
        ).hexdigest()
        rng = np.random.default_rng(int(digest[:16], 16))
        rng.shuffle(values)
        out[indices] = values
    return out


def matched_delta(rows, truth):
    strata = defaultdict(lambda: [[], []])
    for index, row in enumerate(rows):
        strata[(row["cell_id"], row["register"])][int(row["prev_dy"])].append(
            int(truth[index])
        )
    numerator = denominator = 0.0
    for absent, present in strata.values():
        if absent and present:
            weight = len(absent) * len(present) / (len(absent) + len(present))
            numerator += weight * (
                sum(present) / len(present) - sum(absent) / len(absent)
            )
            denominator += weight
    return numerator / denominator


def main():
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    design = json.loads(DESIGN.read_text())
    stored_design_hash = design.pop("content_sha256")
    check("design_content", stored_design_hash == canonical_hash(design))
    rows = read(PANEL)
    source_rows = read(SOURCE)
    truth_map = {
        hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: int(
            row["wrapper"] == "q"
        )
        for row in source_rows
        if row["control_id"] == "VOYNICH_REFERENCE"
    }
    check("source_join_complete", all(row["event_id_sha256"] in truth_map for row in rows))
    truth = np.array([truth_map[row["event_id_sha256"]] for row in rows], float)
    check("panel_counts", len(rows) == 450 and int(truth.sum()) == 137)
    check("cell_counts", len({row["cell_id"] for row in rows}) == 36)
    folios = sorted({row["physical_folio"] for row in rows})
    check("folio_counts", len(folios) == 82)
    check("sealed_holdout", not any(row["page"].startswith("f84") for row in rows))

    baseline = np.zeros(len(rows))
    candidate = np.zeros(len(rows))
    coefficients = {}
    exported_folds = {row["physical_folio"]: row for row in read(FOLDS)}
    for folio in folios:
        train = [row for row in rows if row["physical_folio"] != folio]
        test = [row for row in rows if row["physical_folio"] == folio]
        train_truth = np.array(
            [truth_map[row["event_id_sha256"]] for row in train], float
        )
        indices = [
            index
            for index, row in enumerate(rows)
            if row["physical_folio"] == folio
        ]
        train_x, test_x = matrices(train, test, False)
        baseline[indices], _ = fit(train_x, train_truth, test_x, design["ridge"])
        train_x, test_x = matrices(train, test, True)
        candidate[indices], beta = fit(
            train_x, train_truth, test_x, design["ridge"]
        )
        coefficients[folio] = beta[-1]
        fold_gain = float(
            np.sum(
                event_bits(baseline[indices], truth[indices])
                - event_bits(candidate[indices], truth[indices])
            )
        )
        exported = exported_folds[folio]
        check(
            f"fold_{folio}",
            close(exported["prev_dy_coefficient"], beta[-1])
            and close(exported["gain_bits"], fold_gain),
        )

    gains = event_bits(baseline, truth) - event_bits(candidate, truth)
    gain = float(gains.mean())
    delta = matched_delta(rows, truth)
    exported_predictions = {row["event_id_sha256"]: row for row in read(PREDICTIONS)}
    check("prediction_rows", len(exported_predictions) == len(rows))
    for index, row in enumerate(rows):
        exported = exported_predictions[row["event_id_sha256"]]
        check(
            "prediction_score",
            int(exported["observed_q"]) == int(truth[index])
            and close(exported["cell_probability"], baseline[index])
            and close(exported["cell_prev_dy_probability"], candidate[index])
            and close(exported["gain_bits"], gains[index]),
        )

    null_values = []
    for world in range(design["null"]["worlds"]):
        permuted = permute(truth, rows, design["null"]["seed"], world)
        null_values.append(
            float(
                np.mean(
                    event_bits(baseline, permuted)
                    - event_bits(candidate, permuted)
                )
            )
        )
    exported_null = read(NULL)
    check("null_rows", len(exported_null) == len(null_values))
    check(
        "null_values",
        all(
            close(row["alignment_gain_bits_per_event"], value)
            for row, value in zip(exported_null, null_values)
        ),
    )
    diagnostic_p = (
        1 + sum(value >= gain - 1e-15 for value in null_values)
    ) / (1 + len(null_values))

    exported_sections = {row["section"]: row for row in read(SECTIONS)}
    for section, exported in exported_sections.items():
        indices = [
            index for index, row in enumerate(rows) if row["section"] == section
        ]
        check(f"section_{section}", close(exported["gain_bits"], gains[indices].sum()))

    summary = {
        "cells": 36,
        "events": 450,
        "q_events": 137,
        "folios": 82,
        "gain_bits_per_event": gain,
        "matched_prev_dy_delta": delta,
        "positive_coefficients": int(sum(value > 0 for value in coefficients.values())),
        "positive_folios": int(
            sum(float(row["gain_bits"]) > 0 for row in exported_folds.values())
        ),
        "positive_powered_sections": int(
            sum(
                float(exported_sections[section]["gain_bits"]) > 0
                for section in ("B", "H", "S")
            )
        ),
        "alignment_diagnostic_p": diagnostic_p,
    }
    result = json.loads(RESULT.read_text())
    stored_result_hash = result.pop("content_sha256")
    check(
        "summary",
        all(
            close(result["summary"][key], value)
            if isinstance(value, float)
            else result["summary"][key] == value
            for key, value in summary.items()
        ),
    )
    check("result_content", stored_result_hash == canonical_hash(result))
    check("status", result["status"] == "Q_POST_DY_EXTENDS_TO_FRESH_SURFACES")
    check(
        "bindings",
        all(result["inputs"][name] == sha(R / name) for name in result["inputs"])
        and all(result["outputs"][name] == sha(R / name) for name in result["outputs"])
        and all(result["documents"][name] == sha(R / name) for name in result["documents"])
        and all(
            result["implementation"][name] == sha(R / name)
            for name in result["implementation"]
        ),
    )
    check("result_f84", not any(result["f84"].values()))
    validation = {
        "schema": "GDT316_FRESH_Q_POST_DY_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks": checks,
        "result_sha256": sha(RESULT),
        "f84_rows": 0,
        "scope": "INDEPENDENT_LABEL_CROSSFIT_SCORE_ALIGNMENT_AND_BINDING_RECONSTRUCTION",
    }
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
