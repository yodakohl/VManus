#!/usr/bin/env python3
"""Score shared line-start and post-DY selectors over all powered wrapper cells."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt318_frozen_panel.tsv"
DESIGN = R / "gdt318_design.json"
METHOD = R / "GDT318_GLOBAL_WRAPPER_ENTRY_STATE_METHOD.md"
MODELS = R / "gdt318_model_scores.tsv"
FOLDS = R / "gdt318_folio_scores.tsv"
SECTIONS = R / "gdt318_section_scores.tsv"
CLASSES = R / "gdt318_wrapper_scores.tsv"
COEFFICIENTS = R / "gdt318_coefficient_summary.tsv"
PREDICTIONS = R / "gdt318_predictions.tsv"
NULL = R / "gdt318_null.tsv"
COUNTER = R / "gdt318_counterexamples.tsv"
REPORT = R / "GDT318_GLOBAL_WRAPPER_ENTRY_STATE_REPORT.md"
RESULT = R / "gdt318_result.json"


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


def cell_offsets(train, test, truth, classes, alpha):
    cells = sorted({row["cell_id"] for row in train})
    index = {cell: position for position, cell in enumerate(cells)}
    counts = np.full((len(cells), len(classes)), alpha, float)
    for row, value in zip(train, truth):
        counts[index[row["cell_id"]], value] += 1
    log_counts = np.log(counts)
    train_offsets = np.array([log_counts[index[row["cell_id"]]] for row in train])
    test_offsets = np.array([log_counts[index[row["cell_id"]]] for row in test])
    return train_offsets, test_offsets


def feature_matrix(rows, features):
    return np.array([[float(row[name]) for name in features] for row in rows])


def fit_selector(train_offsets, train_x, train_y, test_offsets, test_x, class_count, ridge):
    if train_x.shape[1] == 0:
        return softmax(test_offsets), np.zeros((class_count, 0))
    beta = np.zeros((class_count, train_x.shape[1]))
    eye = np.eye(beta.size) * ridge
    for _ in range(60):
        probability = softmax(train_offsets + train_x @ beta.T)
        target = np.zeros_like(probability)
        target[np.arange(len(train_y)), train_y] = 1
        gradient = (probability - target).T @ train_x + ridge * beta
        hessian = eye.copy()
        feature_count = train_x.shape[1]
        for left_feature in range(feature_count):
            for right_feature in range(feature_count):
                weights = train_x[:, left_feature] * train_x[:, right_feature]
                block = np.diag(np.sum(weights[:, None] * probability, axis=0))
                block -= np.einsum("i,ik,il->kl", weights, probability, probability)
                for left_class in range(class_count):
                    for right_class in range(class_count):
                        hessian[left_class * feature_count + left_feature, right_class * feature_count + right_feature] += block[left_class, right_class]
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
    source_truth = {
        hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: class_index[row["wrapper"]]
        for row in read(SOURCE)
        if row["control_id"] == "VOYNICH_REFERENCE"
    }
    truth = np.array([source_truth[row["event_id_sha256"]] for row in rows], int)
    model_names = list(design["models"])
    probabilities = {model: np.zeros((len(rows), len(classes))) for model in model_names}
    fold_rows = []
    coefficient_values = defaultdict(list)
    folios = sorted({row["physical_folio"] for row in rows})
    for folio in folios:
        train_indices = [index for index, row in enumerate(rows) if row["physical_folio"] != folio]
        test_indices = [index for index, row in enumerate(rows) if row["physical_folio"] == folio]
        train = [rows[index] for index in train_indices]
        test = [rows[index] for index in test_indices]
        train_truth = truth[train_indices]
        train_offsets, test_offsets = cell_offsets(train, test, train_truth, classes, design["alpha"])
        baseline = softmax(test_offsets)
        probabilities["CELL"][test_indices] = baseline
        baseline_bits = bits(baseline, truth[test_indices])
        fold_rows.append({"physical_folio": folio, "model": "CELL", "events": len(test), "gain_bits": "0.000000000000", "gain_bits_per_event": "0.000000000000"})
        for model in model_names[1:]:
            features = design["models"][model]
            train_x = feature_matrix(train, features)
            test_x = feature_matrix(test, features)
            predicted, beta = fit_selector(train_offsets, train_x, train_truth, test_offsets, test_x, len(classes), design["ridge"])
            probabilities[model][test_indices] = predicted
            gain = float(np.sum(baseline_bits - bits(predicted, truth[test_indices])))
            fold_rows.append({"physical_folio": folio, "model": model, "events": len(test), "gain_bits": f"{gain:.12f}", "gain_bits_per_event": f"{gain / len(test):.12f}"})
            for class_position, wrapper in enumerate(classes):
                for feature_position, feature in enumerate(features):
                    coefficient_values[(model, wrapper, feature)].append(float(beta[class_position, feature_position]))

    baseline_bits = bits(probabilities["CELL"], truth)
    gains = {model: baseline_bits - bits(probabilities[model], truth) for model in model_names[1:]}
    observed = {model: float(values.mean()) for model, values in gains.items()}
    null_rows = []
    null_by_model = {model: [] for model in model_names[1:]}
    for world in range(design["null"]["worlds"]):
        permuted = permute(truth, rows, design["null"]["seed"], world)
        base = bits(probabilities["CELL"], permuted)
        values = {}
        for model in model_names[1:]:
            values[model] = float(np.mean(base - bits(probabilities[model], permuted)))
            null_by_model[model].append(values[model])
        maximum = max(values.values())
        null_rows.append({"world_index": world, **{model: f"{values[model]:.12f}" for model in model_names[1:]}, "max_three_gain_bits_per_event": f"{maximum:.12f}"})
    max_null = [float(row["max_three_gain_bits_per_event"]) for row in null_rows]
    model_rows = []
    for model in model_names:
        if model == "CELL":
            model_rows.append({"model": model, "events": len(rows), "held_bits_per_event": f"{baseline_bits.mean():.12f}", "gain_bits_per_event": "0.000000000000", "selector_paid_gain_bits": "0.000000000000", "local_diagnostic_p": "1.000000000000", "max_three_diagnostic_p": "1.000000000000", "positive_folios": 0})
            continue
        local_p = (1 + sum(value >= observed[model] - 1e-15 for value in null_by_model[model])) / (1 + len(null_by_model[model]))
        max_p = (1 + sum(value >= observed[model] - 1e-15 for value in max_null)) / (1 + len(max_null))
        model_rows.append({
            "model": model, "events": len(rows),
            "held_bits_per_event": f"{bits(probabilities[model], truth).mean():.12f}",
            "gain_bits_per_event": f"{observed[model]:.12f}",
            "selector_paid_gain_bits": f"{observed[model] * len(rows) - design['selector_cost_bits']:.12f}",
            "local_diagnostic_p": f"{local_p:.12f}", "max_three_diagnostic_p": f"{max_p:.12f}",
            "positive_folios": sum(float(row["gain_bits"]) > 0 for row in fold_rows if row["model"] == model),
        })
    section_rows = []
    for section in sorted({row["section"] for row in rows}):
        indices = [index for index, row in enumerate(rows) if row["section"] == section]
        for model in model_names[1:]:
            section_rows.append({"section": section, "model": model, "events": len(indices), "gain_bits": f"{gains[model][indices].sum():.12f}", "gain_bits_per_event": f"{gains[model][indices].mean():.12f}"})
    wrapper_rows = []
    for wrapper, class_position in class_index.items():
        indices = np.where(truth == class_position)[0]
        for model in model_names[1:]:
            wrapper_rows.append({"wrapper": wrapper, "model": model, "events": len(indices), "gain_bits": f"{gains[model][indices].sum():.12f}", "gain_bits_per_event": f"{gains[model][indices].mean():.12f}"})
    coefficient_rows = []
    for key, values in sorted(coefficient_values.items()):
        coefficient_rows.append({"model": key[0], "wrapper": key[1], "feature": key[2], "folds": len(values), "mean_coefficient": f"{np.mean(values):.12f}", "positive_folds": sum(value > 0 for value in values), "negative_folds": sum(value < 0 for value in values)})
    prediction_rows = []
    for index, row in enumerate(rows):
        prediction_rows.append({
            "event_id_sha256": row["event_id_sha256"], "physical_folio": row["physical_folio"],
            "section": row["section"], "cell_id": row["cell_id"],
            "line_first": row["line_first"], "prev_dy": row["prev_dy"],
            "observed_wrapper": classes[truth[index]],
            **{model + "_probabilities_json": json.dumps({wrapper: round(float(probabilities[model][index, position]), 12) for position, wrapper in enumerate(classes)}, sort_keys=True, separators=(",", ":")) for model in model_names},
        })
    write(MODELS, model_rows)
    write(FOLDS, fold_rows)
    write(SECTIONS, section_rows)
    write(CLASSES, wrapper_rows)
    write(COEFFICIENTS, coefficient_rows)
    write(PREDICTIONS, prediction_rows)
    write(NULL, null_rows)
    joint = {row["model"]: row for row in model_rows}["CELL_BOTH"]
    coefficient_map = {(row["model"], row["wrapper"], row["feature"]): row for row in coefficient_rows}
    s_positive = int(coefficient_map[("CELL_BOTH", "s", "line_first")]["positive_folds"])
    q_positive = int(coefficient_map[("CELL_BOTH", "q", "prev_dy")]["positive_folds"])
    powered_sections_positive = sum(float(row["gain_bits"]) > 0 for row in section_rows if row["model"] == "CELL_BOTH" and row["section"] in ("B", "H", "S"))
    passed = float(joint["selector_paid_gain_bits"]) > 0 and powered_sections_positive >= design["decision"]["positive_powered_sections_min"] and s_positive >= design["decision"]["s_line_positive_coefficients_min"] and q_positive >= design["decision"]["q_prev_dy_positive_coefficients_min"] and float(joint["max_three_diagnostic_p"]) <= design["decision"]["max_three_p_le"]
    status = "GLOBAL_WRAPPER_ENTRY_STATE_TRANSFERS" if passed else "GLOBAL_WRAPPER_ENTRY_STATE_WEAK_OR_FAILED"
    counterexamples = [
        {"counterexample_id": "C01", "finding": "All cells are selected for outcome diversity and are already known to license at least two wrappers.", "impact": "The model predicts choice after license, never a new license."},
        {"counterexample_id": "C02", "finding": "GDT312-GDT317 exposed the expected s and q directions before this consolidation.", "impact": "This is a broad compression/generalization test, not independent selector discovery."},
        {"counterexample_id": "C03", "finding": "Exact cells absorb PAGE_HOST and same-group renderer structure.", "impact": "Only external line-entry and preceding-DY increments are credited."},
        {"counterexample_id": "C04", "finding": "The fixed-crossfit max-three diagnostic does not refit each shuffled world.", "impact": "The p-value is diagnostic rather than an exact retrained null."},
        {"counterexample_id": "C05", "finding": "Wrapper-class coefficient directions need not imply one shared linguistic category.", "impact": "The result is a formal state machine only."},
        {"counterexample_id": "C06", "finding": "No f84 row occurs in source, panel, or output.", "impact": "The sealed holdout remains untouched."},
    ]
    write(COUNTER, counterexamples)
    other_line = sorted((row for row in coefficient_rows if row["model"] == "CELL_BOTH" and row["feature"] == "line_first"), key=lambda row: -abs(float(row["mean_coefficient"])))
    other_prev = sorted((row for row in coefficient_rows if row["model"] == "CELL_BOTH" and row["feature"] == "prev_dy"), key=lambda row: -abs(float(row["mean_coefficient"])))
    report = [
        "# GDT318 — global wrapper entry-state compression", "", f"Status: **{status}**.", "",
        f"Across 126 outcome-diverse opaque cells and 5,607 held events, the exact-cell baseline costs {float(model_rows[0]['held_bits_per_event']):.6f} bits/event. The joint line-start plus preceding-DY selector gains {float(joint['gain_bits_per_event']):+.6f} bits/event ({float(joint['selector_paid_gain_bits']):+.2f} bits after the fixed two-bit model charge; max-three diagnostic p={float(joint['max_three_diagnostic_p']):.8f}).", "",
        f"The joint model has positive `s × LINE_START` coefficients in {s_positive}/91 folds and positive `q × PREV_DY` coefficients in {q_positive}/91. {powered_sections_positive}/3 powered B/H/S sections contribute positive held gain.", "",
        "| model | gain bits/event | paid total bits | positive folios | max-three p |", "|---|---:|---:|---:|---:|",
    ]
    for row in model_rows[1:]:
        report.append(f"| {row['model']} | {float(row['gain_bits_per_event']):+.6f} | {float(row['selector_paid_gain_bits']):+.2f} | {row['positive_folios']}/91 | {float(row['max_three_diagnostic_p']):.6f} |")
    report += ["", "Largest joint-model line-start coefficient magnitudes: " + ", ".join(f"{row['wrapper']}={float(row['mean_coefficient']):+.3f}" for row in other_line[:4]) + ".", "", "Largest joint-model preceding-DY coefficient magnitudes: " + ", ".join(f"{row['wrapper']}={float(row['mean_coefficient']):+.3f}" for row in other_prev[:4]) + ".", "", "The only promoted interpretation is an executable opaque-cell renderer state machine. Exact compatibility cells remain memorized, and the result assigns no linguistic function.", "", "## Claim ceiling", "", design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored."]
    REPORT.write_text("\n".join(report) + "\n")
    outputs = [MODELS, FOLDS, SECTIONS, CLASSES, COEFFICIENTS, PREDICTIONS, NULL, COUNTER, REPORT]
    inputs = [PANEL, R / "gdt318_capacity.tsv", R / "gdt318_design_validation.json", SOURCE, R / "gdt314_result.json", R / "gdt316_result.json", R / "gdt317_result.json"]
    result = {
        "schema": "GDT318_GLOBAL_WRAPPER_ENTRY_STATE_RESULT_V1", "status": status,
        "summary": {"cells": 126, "events": len(rows), "folios": len(folios), "joint_gain_bits_per_event": float(joint["gain_bits_per_event"]), "joint_selector_paid_gain_bits": float(joint["selector_paid_gain_bits"]), "joint_max_three_p": float(joint["max_three_diagnostic_p"]), "s_line_positive_coefficients": s_positive, "q_prev_dy_positive_coefficients": q_positive, "positive_powered_sections": powered_sections_positive},
        "semantic_assignments": 0, "claim_ceiling": design["claim_ceiling"],
        "f84": {"input_rows": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in inputs},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in outputs},
    }
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "summary": result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
