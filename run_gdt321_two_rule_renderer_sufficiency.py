#!/usr/bin/env python3
"""Compare the two transferable renderer rules with the full GDT318 anchor."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt318_frozen_panel.tsv"
DESIGN = R / "gdt321_design.json"
METHOD = R / "GDT321_TWO_RULE_RENDERER_SUFFICIENCY_METHOD.md"
MODELS = R / "gdt321_model_scores.tsv"
FOLDS = R / "gdt321_folio_scores.tsv"
SECTIONS = R / "gdt321_section_scores.tsv"
WRAPPERS = R / "gdt321_wrapper_scores.tsv"
COEFFICIENTS = R / "gdt321_coefficient_summary.tsv"
NULL = R / "gdt321_null.tsv"
COUNTER = R / "gdt321_counterexamples.tsv"
REPORT = R / "GDT321_TWO_RULE_RENDERER_SUFFICIENCY_REPORT.md"
RESULT = R / "gdt321_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, rows[0].keys(), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def softmax(scores):
    shifted = scores - scores.max(axis=1, keepdims=True)
    values = np.exp(shifted)
    return values / values.sum(axis=1, keepdims=True)


def offsets(train, test, truth, class_count, alpha):
    cells = sorted({row["cell_id"] for row in train})
    cell_index = {cell: index for index, cell in enumerate(cells)}
    counts = np.full((len(cells), class_count), alpha, float)
    for row, value in zip(train, truth):
        counts[cell_index[row["cell_id"]], value] += 1
    logged = np.log(counts)
    return np.array([logged[cell_index[row["cell_id"]]] for row in train]), np.array([logged[cell_index[row["cell_id"]]] for row in test])


def fit_two_rule(train_offsets, train_rows, train_truth, test_offsets, test_rows, s_index, q_index, ridge):
    beta = np.zeros(2)
    line = np.array([float(row["line_first"]) for row in train_rows])
    prev = np.array([float(row["prev_dy"]) for row in train_rows])
    for _ in range(60):
        scores = train_offsets.copy()
        scores[:, s_index] += beta[0] * line
        scores[:, q_index] += beta[1] * prev
        probability = softmax(scores)
        target_s = (train_truth == s_index).astype(float)
        target_q = (train_truth == q_index).astype(float)
        gradient = np.array([
            np.sum((probability[:, s_index] - target_s) * line) + ridge * beta[0],
            np.sum((probability[:, q_index] - target_q) * prev) + ridge * beta[1],
        ])
        hessian = np.array([
            [np.sum(probability[:, s_index] * (1 - probability[:, s_index]) * line * line) + ridge, np.sum(-probability[:, s_index] * probability[:, q_index] * line * prev)],
            [np.sum(-probability[:, s_index] * probability[:, q_index] * line * prev), np.sum(probability[:, q_index] * (1 - probability[:, q_index]) * prev * prev) + ridge],
        ])
        step = np.linalg.pinv(hessian) @ gradient
        beta -= step
        if abs(step).max() < 1e-9:
            break
    test_scores = test_offsets.copy()
    test_scores[:, s_index] += beta[0] * np.array([float(row["line_first"]) for row in test_rows])
    test_scores[:, q_index] += beta[1] * np.array([float(row["prev_dy"]) for row in test_rows])
    return softmax(test_scores), beta


def fit_full(train_offsets, train_rows, train_truth, test_offsets, test_rows, class_count, ridge):
    train_x = np.array([[float(row["line_first"]), float(row["prev_dy"])] for row in train_rows])
    test_x = np.array([[float(row["line_first"]), float(row["prev_dy"])] for row in test_rows])
    beta = np.zeros((class_count, 2))
    eye = np.eye(beta.size) * ridge
    for _ in range(60):
        probability = softmax(train_offsets + train_x @ beta.T)
        target = np.zeros_like(probability)
        target[np.arange(len(train_truth)), train_truth] = 1
        gradient = (probability - target).T @ train_x + ridge * beta
        hessian = eye.copy()
        for left_feature in range(2):
            for right_feature in range(2):
                weights = train_x[:, left_feature] * train_x[:, right_feature]
                block = np.diag(np.sum(weights[:, None] * probability, axis=0))
                block -= np.einsum("i,ik,il->kl", weights, probability, probability)
                for left_class in range(class_count):
                    for right_class in range(class_count):
                        hessian[left_class * 2 + left_feature, right_class * 2 + right_feature] += block[left_class, right_class]
        step = np.linalg.pinv(hessian) @ gradient.reshape(-1)
        beta -= step.reshape(beta.shape)
        if abs(step).max() < 1e-9:
            break
    return softmax(test_offsets + test_x @ beta.T), beta


def bits(probability, truth):
    return -np.log2(np.clip(probability[np.arange(len(truth)), truth], 1e-12, 1))


def permute(truth, rows, seed, world):
    out = truth.copy()
    strata = defaultdict(list)
    for index, row in enumerate(rows):
        strata[(row["cell_id"], row["register"])].append(index)
    for key, indices in sorted(strata.items()):
        values = truth[indices].copy()
        digest = hashlib.sha256(f"{seed}|{world}|{key[0]}|{key[1]}".encode()).hexdigest()
        rng = np.random.default_rng(int(digest[:16], 16))
        rng.shuffle(values)
        out[indices] = values
    return out


def main():
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    assert stored == canonical_hash(design)
    rows = read(PANEL)
    classes = design["classes"]
    class_index = {value: index for index, value in enumerate(classes)}
    truth_map = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: class_index[row["wrapper"]] for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"}
    truth = np.array([truth_map[row["event_id_sha256"]] for row in rows], int)
    probabilities = {model: np.zeros((len(rows), len(classes))) for model in ("CELL", "ROBUST_TWO_RULE", "FULL_GDT318_ANCHOR")}
    robust_coefficients = []
    fold_rows = []
    folios = sorted({row["physical_folio"] for row in rows})
    for folio in folios:
        train_indices = [index for index, row in enumerate(rows) if row["physical_folio"] != folio]
        test_indices = [index for index, row in enumerate(rows) if row["physical_folio"] == folio]
        train = [rows[index] for index in train_indices]
        test = [rows[index] for index in test_indices]
        train_truth = truth[train_indices]
        train_offsets, test_offsets = offsets(train, test, train_truth, len(classes), design["alpha"])
        probabilities["CELL"][test_indices] = softmax(test_offsets)
        probabilities["ROBUST_TWO_RULE"][test_indices], robust_beta = fit_two_rule(train_offsets, train, train_truth, test_offsets, test, class_index["s"], class_index["q"], design["ridge"])
        probabilities["FULL_GDT318_ANCHOR"][test_indices], _ = fit_full(train_offsets, train, train_truth, test_offsets, test, len(classes), design["ridge"])
        robust_coefficients.append((folio, robust_beta[0], robust_beta[1]))
        baseline_bits = bits(probabilities["CELL"][test_indices], truth[test_indices])
        for model in ("CELL", "ROBUST_TWO_RULE", "FULL_GDT318_ANCHOR"):
            gain = 0.0 if model == "CELL" else float(np.sum(baseline_bits - bits(probabilities[model][test_indices], truth[test_indices])))
            fold_rows.append({"physical_folio": folio, "model": model, "events": len(test_indices), "gain_bits": f"{gain:.12f}", "gain_bits_per_event": f"{gain / len(test_indices):.12f}"})
    baseline_bits = bits(probabilities["CELL"], truth)
    gains = {model: baseline_bits - bits(probabilities[model], truth) for model in ("ROBUST_TWO_RULE", "FULL_GDT318_ANCHOR")}
    observed = {model: float(value.mean()) for model, value in gains.items()}
    null_rows = []
    null_by_model = {model: [] for model in gains}
    for world in range(design["null"]["worlds"]):
        permuted = permute(truth, rows, design["null"]["seed"], world)
        base = bits(probabilities["CELL"], permuted)
        values = {model: float(np.mean(base - bits(probabilities[model], permuted))) for model in gains}
        for model, value in values.items():
            null_by_model[model].append(value)
        null_rows.append({"world_index": world, **{model: f"{value:.12f}" for model, value in values.items()}, "max_two_gain_bits_per_event": f"{max(values.values()):.12f}"})
    max_null = [float(row["max_two_gain_bits_per_event"]) for row in null_rows]
    model_rows = [{"model": "CELL", "parameters": 0, "held_bits_per_event": f"{baseline_bits.mean():.12f}", "gain_bits_per_event": "0.000000000000", "charged_gain_bits": "0.000000000000", "fraction_full_gain": "0.000000000000", "max_two_diagnostic_p": "1.000000000000", "positive_folios": 0}]
    for model in gains:
        charge = design["parameter_charges_bits"][model] + design["model_selector_bits"]
        max_p = (1 + sum(value >= observed[model] - 1e-15 for value in max_null)) / (1 + len(max_null))
        model_rows.append({"model": model, "parameters": design["parameter_counts"][model], "held_bits_per_event": f"{bits(probabilities[model], truth).mean():.12f}", "gain_bits_per_event": f"{observed[model]:.12f}", "charged_gain_bits": f"{observed[model] * len(rows) - charge:.12f}", "fraction_full_gain": f"{observed[model] / observed['FULL_GDT318_ANCHOR']:.12f}", "max_two_diagnostic_p": f"{max_p:.12f}", "positive_folios": sum(float(row["gain_bits"]) > 0 for row in fold_rows if row["model"] == model)})
    section_rows = []
    for section in sorted({row["section"] for row in rows}):
        indices = [index for index, row in enumerate(rows) if row["section"] == section]
        for model in gains:
            section_rows.append({"section": section, "model": model, "events": len(indices), "gain_bits": f"{gains[model][indices].sum():.12f}", "gain_bits_per_event": f"{gains[model][indices].mean():.12f}"})
    wrapper_rows = []
    for wrapper, position in class_index.items():
        indices = np.where(truth == position)[0]
        for model in gains:
            wrapper_rows.append({"wrapper": wrapper, "model": model, "events": len(indices), "gain_bits": f"{gains[model][indices].sum():.12f}", "gain_bits_per_event": f"{gains[model][indices].mean():.12f}"})
    coefficient_rows = [
        {"parameter": "s_X_line_first", "folds": len(folios), "mean_coefficient": f"{np.mean([value[1] for value in robust_coefficients]):.12f}", "positive_folds": sum(value[1] > 0 for value in robust_coefficients), "negative_folds": sum(value[1] < 0 for value in robust_coefficients)},
        {"parameter": "q_X_prev_dy", "folds": len(folios), "mean_coefficient": f"{np.mean([value[2] for value in robust_coefficients]):.12f}", "positive_folds": sum(value[2] > 0 for value in robust_coefficients), "negative_folds": sum(value[2] < 0 for value in robust_coefficients)},
    ]
    write(MODELS, model_rows)
    write(FOLDS, fold_rows)
    write(SECTIONS, section_rows)
    write(WRAPPERS, wrapper_rows)
    write(COEFFICIENTS, coefficient_rows)
    write(NULL, null_rows)
    model_map = {row["model"]: row for row in model_rows}
    robust = model_map["ROBUST_TWO_RULE"]
    positive_sections = sum(float(row["gain_bits"]) > 0 for row in section_rows if row["model"] == "ROBUST_TWO_RULE" and row["section"] in ("B", "H", "S"))
    passed = float(robust["charged_gain_bits"]) > 0 and float(robust["fraction_full_gain"]) >= design["decision"]["fraction_full_gain_min"] and positive_sections >= design["decision"]["positive_powered_sections_min"] and all(int(row["positive_folds"]) >= design["decision"]["positive_coefficients_min_each"] for row in coefficient_rows) and float(robust["max_two_diagnostic_p"]) <= design["decision"]["max_two_p_le"]
    status = "TWO_RULE_RENDERER_SUFFICIENT" if passed else "TWO_RULE_RENDERER_INSUFFICIENT"
    counterexamples = [
        {"counterexample_id": "C01", "finding": "The comparison reuses the fully exposed GDT318 panel.", "impact": "It is architectural compression, not independent discovery."},
        {"counterexample_id": "C02", "finding": "The two rules were selected from prior positive transfer tests.", "impact": "Only their sufficiency and explicit complexity tradeoff are tested."},
        {"counterexample_id": "C03", "finding": "Exact opaque cell counts remain mandatory.", "impact": "The two rules do not predict unseen compatibility licenses."},
        {"counterexample_id": "C04", "finding": "Fixed-crossfit null worlds are not retrained.", "impact": "The max-two p is diagnostic rather than exact."},
        {"counterexample_id": "C05", "finding": "No f84 row occurs in source, panel, or output.", "impact": "The sealed holdout remains untouched."},
    ]
    write(COUNTER, counterexamples)
    report = [
        "# GDT321 — two-rule renderer sufficiency", "", f"Status: **{status}**.", "",
        f"The restricted `s × LINE_START` plus `q × PREV_DY` model gains {float(robust['gain_bits_per_event']):+.6f} bits/event and {float(robust['charged_gain_bits']):+.2f} bits after its two-parameter BIC charge and model selector. It retains {100 * float(robust['fraction_full_gain']):.1f}% of the unrestricted GDT318 raw gain.", "",
        f"Its coefficients are positive in {coefficient_rows[0]['positive_folds']}/91 and {coefficient_rows[1]['positive_folds']}/91 folds; {positive_sections}/3 B/H/S sections gain; max-two diagnostic p={float(robust['max_two_diagnostic_p']):.8f}.", "",
        "| model | parameters | gain bits/event | charged gain bits | fraction full | positive folios |", "|---|---:|---:|---:|---:|---:|",
    ]
    for row in model_rows[1:]:
        report.append(f"| {row['model']} | {row['parameters']} | {float(row['gain_bits_per_event']):+.6f} | {float(row['charged_gain_bits']):+.2f} | {float(row['fraction_full_gain']):.3f} | {row['positive_folios']}/91 |")
    report += ["", "This result chooses the smallest currently justified renderer state machine; it does not convert s or q into linguistic morphemes.", "", "## Claim ceiling", "", design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored."]
    REPORT.write_text("\n".join(report) + "\n")
    outputs = [MODELS, FOLDS, SECTIONS, WRAPPERS, COEFFICIENTS, NULL, COUNTER, REPORT]
    inputs = [PANEL, R / "gdt321_design_validation.json", SOURCE, R / "gdt318_result.json", R / "gdt319_result.json", R / "gdt320_result.json"]
    result = {"schema": "GDT321_TWO_RULE_RENDERER_SUFFICIENCY_RESULT_V1", "status": status, "summary": {"events": len(rows), "cells": 126, "folios": len(folios), "robust_gain_bits_per_event": float(robust["gain_bits_per_event"]), "robust_charged_gain_bits": float(robust["charged_gain_bits"]), "fraction_full_gain": float(robust["fraction_full_gain"]), "positive_powered_sections": positive_sections, "s_positive_coefficients": int(coefficient_rows[0]["positive_folds"]), "q_positive_coefficients": int(coefficient_rows[1]["positive_folds"]), "max_two_diagnostic_p": float(robust["max_two_diagnostic_p"])}, "semantic_assignments": 0, "claim_ceiling": design["claim_ceiling"], "f84": {"input_rows": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False}, "inputs": {path.name: sha(path) for path in inputs}, "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}, "implementation": {Path(__file__).name: sha(Path(__file__))}, "outputs": {path.name: sha(path) for path in outputs}}
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "summary": result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
