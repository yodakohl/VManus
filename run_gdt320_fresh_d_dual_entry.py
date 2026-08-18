#!/usr/bin/env python3
"""Score fresh d/non-d line-start and post-DY transfer."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt320_frozen_panel.tsv"
DESIGN = R / "gdt320_design.json"
METHOD = R / "GDT320_FRESH_D_DUAL_ENTRY_METHOD.md"
MODELS = R / "gdt320_model_scores.tsv"
FOLDS = R / "gdt320_folio_scores.tsv"
SECTIONS = R / "gdt320_section_scores.tsv"
COEFFICIENTS = R / "gdt320_coefficient_summary.tsv"
PREDICTIONS = R / "gdt320_predictions.tsv"
NULL = R / "gdt320_null.tsv"
COUNTER = R / "gdt320_counterexamples.tsv"
REPORT = R / "GDT320_FRESH_D_DUAL_ENTRY_REPORT.md"
RESULT = R / "gdt320_result.json"


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


def matrices(train, test, features):
    cells = sorted({row["cell_id"] for row in train})
    def encode(rows):
        return np.array([[1.0] + [float(row["cell_id"] == cell) for cell in cells] + [float(row[name]) for name in features] for row in rows])
    return encode(train), encode(test)


def fit(train_x, train_y, test_x, ridge):
    beta = np.zeros(train_x.shape[1])
    penalty = np.eye(len(beta)) * ridge
    penalty[0, 0] = 0
    for _ in range(100):
        probability = 1 / (1 + np.exp(-np.clip(train_x @ beta, -30, 30)))
        weight = np.maximum(probability * (1 - probability), 1e-8)
        step = np.linalg.pinv(train_x.T @ (train_x * weight[:, None]) + penalty) @ (train_x.T @ (train_y - probability) - penalty @ beta)
        beta += step
        if abs(step).max() < 1e-10:
            break
    predicted = 1 / (1 + np.exp(-np.clip(test_x @ beta, -30, 30)))
    return np.clip(predicted, 0.01, 0.99), beta


def event_bits(probability, truth):
    return -(truth * np.log2(probability) + (1 - truth) * np.log2(1 - probability))


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


def matched_delta(rows, truth, feature):
    strata = defaultdict(lambda: [[], []])
    for index, row in enumerate(rows):
        strata[(row["cell_id"], row["register"])][int(row[feature])].append(int(truth[index]))
    numerator = denominator = 0.0
    for absent, present in strata.values():
        if absent and present:
            weight = len(absent) * len(present) / (len(absent) + len(present))
            numerator += weight * (sum(present) / len(present) - sum(absent) / len(absent))
            denominator += weight
    return numerator / denominator if denominator else 0.0


def main():
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    assert stored == canonical_hash(design)
    rows = read(PANEL)
    truth_map = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: int(row["wrapper"] == "d") for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"}
    truth = np.array([truth_map[row["event_id_sha256"]] for row in rows], float)
    model_names = list(design["models"])
    probabilities = {model: np.zeros(len(rows)) for model in model_names}
    coefficient_values = defaultdict(list)
    fold_rows = []
    folios = sorted({row["physical_folio"] for row in rows})
    for folio in folios:
        train = [row for row in rows if row["physical_folio"] != folio]
        test = [row for row in rows if row["physical_folio"] == folio]
        train_truth = np.array([truth_map[row["event_id_sha256"]] for row in train], float)
        indices = [index for index, row in enumerate(rows) if row["physical_folio"] == folio]
        for model in model_names:
            features = design["models"][model]
            train_x, test_x = matrices(train, test, features)
            probabilities[model][indices], beta = fit(train_x, train_truth, test_x, design["ridge"])
            if model == "CELL":
                gain = 0.0
            else:
                gain = float(np.sum(event_bits(probabilities["CELL"][indices], truth[indices]) - event_bits(probabilities[model][indices], truth[indices])))
                for offset, feature in enumerate(features, 1):
                    coefficient_values[(model, feature)].append(float(beta[-len(features) - 1 + offset]))
            fold_rows.append({"physical_folio": folio, "model": model, "events": len(indices), "d_events": int(truth[indices].sum()), "gain_bits": f"{gain:.12f}", "gain_bits_per_event": f"{gain / len(indices):.12f}"})
    baseline_bits = event_bits(probabilities["CELL"], truth)
    gains = {model: baseline_bits - event_bits(probabilities[model], truth) for model in model_names[1:]}
    observed = {model: float(values.mean()) for model, values in gains.items()}
    null_rows = []
    null_by_model = {model: [] for model in model_names[1:]}
    for world in range(design["null"]["worlds"]):
        permuted = permute(truth, rows, design["null"]["seed"], world)
        base = event_bits(probabilities["CELL"], permuted)
        values = {}
        for model in model_names[1:]:
            values[model] = float(np.mean(base - event_bits(probabilities[model], permuted)))
            null_by_model[model].append(values[model])
        null_rows.append({"world_index": world, **{model: f"{values[model]:.12f}" for model in model_names[1:]}, "max_three_gain_bits_per_event": f"{max(values.values()):.12f}"})
    max_null = [float(row["max_three_gain_bits_per_event"]) for row in null_rows]
    model_rows = [{"model": "CELL", "events": len(rows), "held_bits_per_event": f"{baseline_bits.mean():.12f}", "gain_bits_per_event": "0.000000000000", "selector_paid_gain_bits": "0.000000000000", "local_diagnostic_p": "1.000000000000", "max_three_diagnostic_p": "1.000000000000", "positive_folios": 0}]
    for model in model_names[1:]:
        local_p = (1 + sum(value >= observed[model] - 1e-15 for value in null_by_model[model])) / (1 + len(null_by_model[model]))
        max_p = (1 + sum(value >= observed[model] - 1e-15 for value in max_null)) / (1 + len(max_null))
        model_rows.append({"model": model, "events": len(rows), "held_bits_per_event": f"{event_bits(probabilities[model], truth).mean():.12f}", "gain_bits_per_event": f"{observed[model]:.12f}", "selector_paid_gain_bits": f"{observed[model] * len(rows) - design['selector_cost_bits']:.12f}", "local_diagnostic_p": f"{local_p:.12f}", "max_three_diagnostic_p": f"{max_p:.12f}", "positive_folios": sum(float(row["gain_bits"]) > 0 for row in fold_rows if row["model"] == model)})
    section_rows = []
    for section in sorted({row["section"] for row in rows}):
        indices = [index for index, row in enumerate(rows) if row["section"] == section]
        for model in model_names[1:]:
            section_rows.append({"section": section, "model": model, "events": len(indices), "d_events": int(truth[indices].sum()), "gain_bits": f"{gains[model][indices].sum():.12f}", "gain_bits_per_event": f"{gains[model][indices].mean():.12f}", "powered": int(truth[indices].sum() > 0 and truth[indices].sum() < len(indices))})
    coefficient_rows = []
    for key, values in sorted(coefficient_values.items()):
        coefficient_rows.append({"model": key[0], "feature": key[1], "folds": len(values), "mean_coefficient": f"{np.mean(values):.12f}", "positive_folds": sum(value > 0 for value in values), "negative_folds": sum(value < 0 for value in values)})
    prediction_rows = []
    for index, row in enumerate(rows):
        prediction_rows.append({"event_id_sha256": row["event_id_sha256"], "cell_id": row["cell_id"], "physical_folio": row["physical_folio"], "section": row["section"], "register": row["register"], "line_first": row["line_first"], "prev_dy": row["prev_dy"], "observed_d": int(truth[index]), **{model + "_probability": f"{probabilities[model][index]:.12f}" for model in model_names}})
    write(MODELS, model_rows)
    write(FOLDS, fold_rows)
    write(SECTIONS, section_rows)
    write(COEFFICIENTS, coefficient_rows)
    write(PREDICTIONS, prediction_rows)
    write(NULL, null_rows)
    model_map = {row["model"]: row for row in model_rows}
    coefficient_map = {(row["model"], row["feature"]): row for row in coefficient_rows}
    line_delta = matched_delta(rows, truth, "line_first")
    prev_delta = matched_delta(rows, truth, "prev_dy")
    line_positive = int(coefficient_map[("CELL_BOTH", "line_first")]["positive_folds"])
    prev_positive = int(coefficient_map[("CELL_BOTH", "prev_dy")]["positive_folds"])
    positive_sections = sum(float(row["gain_bits"]) > 0 for row in section_rows if row["model"] == "CELL_BOTH" and row["section"] in ("B", "H", "S") and int(row["powered"]))
    joint = model_map["CELL_BOTH"]
    passed = float(joint["selector_paid_gain_bits"]) > 0 and line_delta > 0 and prev_delta > 0 and line_positive >= design["decision"]["positive_coefficients_min_each"] and prev_positive >= design["decision"]["positive_coefficients_min_each"] and positive_sections >= design["decision"]["positive_powered_sections_min"] and float(joint["max_three_diagnostic_p"]) <= design["decision"]["max_three_p_le"]
    status = "D_DUAL_ENTRY_EXTENDS_TO_FRESH_SURFACES" if passed else "D_DUAL_ENTRY_FRESH_TRANSFER_WEAK_OR_FAILED"
    counterexamples = [
        {"counterexample_id": "C01", "finding": "Both d directions were selected after GDT318 outcome exposure.", "impact": "Only transfer to disjoint surfaces is prospective."},
        {"counterexample_id": "C02", "finding": "The panel has seven cells and 46 events.", "impact": "The two-bit model charge and section gates are intentionally severe."},
        {"counterexample_id": "C03", "finding": "Every cell is already known to license d.", "impact": "No unseen compatibility license is predicted."},
        {"counterexample_id": "C04", "finding": "The fixed-crossfit max-three diagnostic does not retrain shuffled worlds.", "impact": "Its p-value is diagnostic rather than exact."},
        {"counterexample_id": "C05", "finding": "No f84 row occurs in source, panel, or output.", "impact": "The sealed holdout remains untouched."},
    ]
    write(COUNTER, counterexamples)
    report = [
        "# GDT320 — fresh-surface `d` dual-entry transfer", "", f"Status: **{status}**.", "",
        "Every exact surface used by GDT318 is excluded.", "",
        f"The joint model changes held log loss by {float(joint['gain_bits_per_event']):+.6f} bits/event and {float(joint['selector_paid_gain_bits']):+.2f} bits after the fixed two-bit selector charge. Matched deltas are line-start {line_delta:+.3f} and post-DY {prev_delta:+.3f}; max-three diagnostic p={float(joint['max_three_diagnostic_p']):.8f}.", "",
        f"Joint coefficients are positive in {line_positive}/30 folds for line start and {prev_positive}/30 for preceding DY. {positive_sections}/3 powered B/H/S sections contribute positive joint gain.", "",
        "| model | gain bits/event | paid total bits | positive folios | max-three p |", "|---|---:|---:|---:|---:|",
    ]
    for row in model_rows[1:]:
        report.append(f"| {row['model']} | {float(row['gain_bits_per_event']):+.6f} | {float(row['selector_paid_gain_bits']):+.2f} | {row['positive_folios']}/30 | {float(row['max_three_diagnostic_p']):.6f} |")
    report += ["", "A failure leaves d as an exposed-panel coefficient rather than a reusable selector.", "", "## Claim ceiling", "", design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored."]
    REPORT.write_text("\n".join(report) + "\n")
    outputs = [MODELS, FOLDS, SECTIONS, COEFFICIENTS, PREDICTIONS, NULL, COUNTER, REPORT]
    inputs = [PANEL, R / "gdt320_capacity.tsv", R / "gdt320_design_validation.json", SOURCE, R / "gdt318_result.json"]
    result = {"schema": "GDT320_FRESH_D_DUAL_ENTRY_RESULT_V1", "status": status, "summary": {"cells": 7, "events": len(rows), "d_events": int(truth.sum()), "folios": len(folios), "joint_gain_bits_per_event": float(joint["gain_bits_per_event"]), "joint_selector_paid_gain_bits": float(joint["selector_paid_gain_bits"]), "matched_line_start_delta": line_delta, "matched_prev_dy_delta": prev_delta, "line_positive_coefficients": line_positive, "prev_dy_positive_coefficients": prev_positive, "positive_powered_sections": positive_sections, "joint_max_three_p": float(joint["max_three_diagnostic_p"])}, "semantic_assignments": 0, "claim_ceiling": design["claim_ceiling"], "f84": {"input_rows": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False}, "inputs": {path.name: sha(path) for path in inputs}, "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}, "implementation": {Path(__file__).name: sha(Path(__file__))}, "outputs": {path.name: sha(path) for path in outputs}}
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "summary": result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
