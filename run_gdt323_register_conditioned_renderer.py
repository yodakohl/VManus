#!/usr/bin/env python3
"""Score global, Currier-conditioned, and register-conditioned two-rule renderers."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt318_frozen_panel.tsv"
DESIGN = R / "gdt323_design.json"
METHOD = R / "GDT323_REGISTER_CONDITIONED_RENDERER_METHOD.md"
MODELS = R / "gdt323_model_scores.tsv"
FOLDS = R / "gdt323_folio_scores.tsv"
REGISTERS = R / "gdt323_register_scores.tsv"
SECTIONS = R / "gdt323_section_scores.tsv"
COEFFICIENTS = R / "gdt323_coefficient_summary.tsv"
NULL = R / "gdt323_null.tsv"
COUNTER = R / "gdt323_counterexamples.tsv"
REPORT = R / "GDT323_REGISTER_CONDITIONED_RENDERER_REPORT.md"
RESULT = R / "gdt323_result.json"


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
    value = np.exp(shifted)
    return value / value.sum(axis=1, keepdims=True)


def offsets(train, test, truth, class_count, alpha):
    cells = sorted({row["cell_id"] for row in train})
    index = {cell: i for i, cell in enumerate(cells)}
    counts = np.full((len(cells), class_count), alpha, float)
    for row, value in zip(train, truth):
        counts[index[row["cell_id"]], value] += 1
    logged = np.log(counts)
    return np.array([logged[index[row["cell_id"]]] for row in train]), np.array([logged[index[row["cell_id"]]] for row in test])


def group_value(row, model):
    if model == "GLOBAL_TWO_RULE":
        return "GLOBAL"
    if model == "CURRIER_TWO_RULE":
        return "A" if row["register"].endswith("_A") else "B"
    return row["register"]


def fit_grouped(train_offsets, train_rows, train_truth, test_offsets, test_rows, s_index, q_index, ridge, model):
    groups = sorted({group_value(row, model) for row in train_rows})
    group_index = {value: i for i, value in enumerate(groups)}
    beta = np.zeros((len(groups), 2))
    line = np.array([float(row["line_first"]) for row in train_rows])
    prev = np.array([float(row["prev_dy"]) for row in train_rows])
    train_group = np.array([group_index[group_value(row, model)] for row in train_rows])
    for _ in range(80):
        scores = train_offsets.copy()
        scores[:, s_index] += beta[train_group, 0] * line
        scores[:, q_index] += beta[train_group, 1] * prev
        probability = softmax(scores)
        step_max = 0.0
        for g in range(len(groups)):
            mask = train_group == g
            for feature_index, (class_position, feature) in enumerate(((s_index, line), (q_index, prev))):
                x = feature[mask]
                if not np.any(x):
                    continue
                target = (train_truth[mask] == class_position).astype(float)
                p = probability[mask, class_position]
                gradient = np.sum((p - target) * x) + ridge * beta[g, feature_index]
                hessian = np.sum(p * (1 - p) * x * x) + ridge
                step = gradient / hessian
                beta[g, feature_index] -= step
                step_max = max(step_max, abs(step))
        if step_max < 1e-9:
            break
    test_group = np.array([group_index[group_value(row, model)] for row in test_rows])
    scores = test_offsets.copy()
    scores[:, s_index] += beta[test_group, 0] * np.array([float(row["line_first"]) for row in test_rows])
    scores[:, q_index] += beta[test_group, 1] * np.array([float(row["prev_dy"]) for row in test_rows])
    return softmax(scores), dict(zip(groups, beta.tolist()))


def bits(probability, truth):
    return -np.log2(np.clip(probability[np.arange(len(truth)), truth], 1e-12, 1))


def permute(truth, rows, seed, world):
    out = truth.copy()
    strata = defaultdict(list)
    for index, row in enumerate(rows):
        strata[(row["cell_id"], row["register"])].append(index)
    for key, indices in sorted(strata.items()):
        value = truth[indices].copy()
        digest = hashlib.sha256(f"{seed}|{world}|{key[0]}|{key[1]}".encode()).hexdigest()
        rng = np.random.default_rng(int(digest[:16], 16))
        rng.shuffle(value)
        out[indices] = value
    return out


def main():
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    assert stored == canonical_hash(design)
    rows = read(PANEL)
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in rows)
    classes = design["classes"]
    class_index = {value: i for i, value in enumerate(classes)}
    truth_map = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: class_index[row["wrapper"]] for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE" and not row["page"].startswith("f84") and not row["locus"].startswith("f84")}
    truth = np.array([truth_map[row["event_id_sha256"]] for row in rows], int)
    candidates = design["models"][1:]
    probabilities = {model: np.zeros((len(rows), len(classes))) for model in design["models"]}
    coefficient_values = defaultdict(list)
    fold_rows = []
    folios = sorted({row["physical_folio"] for row in rows})
    for folio in folios:
        train_indices = [i for i, row in enumerate(rows) if row["physical_folio"] != folio]
        test_indices = [i for i, row in enumerate(rows) if row["physical_folio"] == folio]
        train = [rows[i] for i in train_indices]
        test = [rows[i] for i in test_indices]
        train_truth = truth[train_indices]
        train_offsets, test_offsets = offsets(train, test, train_truth, len(classes), design["alpha"])
        probabilities["CELL"][test_indices] = softmax(test_offsets)
        for model in candidates:
            predicted, beta = fit_grouped(train_offsets, train, train_truth, test_offsets, test, class_index["s"], class_index["q"], design["ridge"], model)
            probabilities[model][test_indices] = predicted
            for group, values in beta.items():
                coefficient_values[(model, group, "s_X_line_first")].append(values[0])
                coefficient_values[(model, group, "q_X_prev_dy")].append(values[1])
        base = bits(probabilities["CELL"][test_indices], truth[test_indices])
        for model in design["models"]:
            gain = 0.0 if model == "CELL" else float(np.sum(base - bits(probabilities[model][test_indices], truth[test_indices])))
            fold_rows.append({"physical_folio": folio, "model": model, "events": len(test_indices), "gain_bits": f"{gain:.12f}", "gain_bits_per_event": f"{gain / len(test_indices):.12f}"})
    baseline_bits = bits(probabilities["CELL"], truth)
    gains = {model: baseline_bits - bits(probabilities[model], truth) for model in candidates}
    observed = {model: float(value.mean()) for model, value in gains.items()}
    null_rows = []
    for world in range(design["null"]["worlds"]):
        shuffled = permute(truth, rows, design["null"]["seed"], world)
        base = bits(probabilities["CELL"], shuffled)
        values = {model: float(np.mean(base - bits(probabilities[model], shuffled))) for model in candidates}
        null_rows.append({"world_index": world, **{model: f"{values[model]:.12f}" for model in candidates}, "max_three_gain_bits_per_event": f"{max(values.values()):.12f}"})
    max_null = [float(row["max_three_gain_bits_per_event"]) for row in null_rows]
    model_rows = [{"model": "CELL", "parameters": 0, "held_bits_per_event": f"{baseline_bits.mean():.12f}", "gain_bits_per_event": "0.000000000000", "raw_gain_bits": "0.000000000000", "charge_bits": "0.000000000000", "charged_gain_bits": "0.000000000000", "charged_total_bits": f"{baseline_bits.sum():.12f}", "positive_folios": 0, "max_three_diagnostic_p": "1.000000000000"}]
    for model in candidates:
        charge = design["parameter_charges_bits"][model] + design["model_selector_bits"]
        p = (1 + sum(value >= observed[model] - 1e-15 for value in max_null)) / (1 + len(max_null))
        raw = observed[model] * len(rows)
        model_rows.append({"model": model, "parameters": design["parameter_counts"][model], "held_bits_per_event": f"{bits(probabilities[model], truth).mean():.12f}", "gain_bits_per_event": f"{observed[model]:.12f}", "raw_gain_bits": f"{raw:.12f}", "charge_bits": f"{charge:.12f}", "charged_gain_bits": f"{raw - charge:.12f}", "charged_total_bits": f"{bits(probabilities[model], truth).sum() + charge:.12f}", "positive_folios": sum(float(row["gain_bits"]) > 0 for row in fold_rows if row["model"] == model), "max_three_diagnostic_p": f"{p:.12f}"})
    coefficient_rows = []
    for key in sorted(coefficient_values):
        values = coefficient_values[key]
        coefficient_rows.append({"model": key[0], "group": key[1], "effect": key[2], "folds": len(values), "mean_coefficient": f"{np.mean(values):.12f}", "minimum_coefficient": f"{np.min(values):.12f}", "maximum_coefficient": f"{np.max(values):.12f}", "positive_folds": sum(value > 0 for value in values), "negative_folds": sum(value < 0 for value in values)})
    register_rows = []
    for register in design["registers"]:
        indices = [i for i, row in enumerate(rows) if row["register"] == register]
        for model in candidates:
            register_rows.append({"register": register, "model": model, "events": len(indices), "gain_bits": f"{gains[model][indices].sum():.12f}", "gain_bits_per_event": f"{gains[model][indices].mean():.12f}"})
    section_rows = []
    for section in sorted({row["section"] for row in rows}):
        indices = [i for i, row in enumerate(rows) if row["section"] == section]
        for model in candidates:
            section_rows.append({"section": section, "model": model, "events": len(indices), "gain_bits": f"{gains[model][indices].sum():.12f}", "gain_bits_per_event": f"{gains[model][indices].mean():.12f}"})
    write(MODELS, model_rows)
    write(FOLDS, fold_rows)
    write(REGISTERS, register_rows)
    write(SECTIONS, section_rows)
    write(COEFFICIENTS, coefficient_rows)
    write(NULL, null_rows)
    eligible = []
    for row in model_rows:
        model = row["model"]
        direction = True if model in ("CELL", "GLOBAL_TWO_RULE") else all(float(value["mean_coefficient"]) > 0 for value in coefficient_rows if value["model"] == model)
        if direction:
            eligible.append(row)
    selected = min(eligible, key=lambda row: float(row["charged_total_bits"]))
    selected_model = selected["model"]
    if selected_model == "REGISTER_TWO_RULE":
        status = "REGISTER_CONDITIONED_TWO_RULE_PREFERRED"
    elif selected_model == "CURRIER_TWO_RULE":
        status = "CURRIER_CONDITIONED_TWO_RULE_PREFERRED"
    elif selected_model == "GLOBAL_TWO_RULE":
        status = "GLOBAL_TWO_RULE_REMAINS_PREFERRED"
    else:
        status = "REGISTER_CONDITIONING_MIXED"
    counterexamples = [
        {"counterexample_id": "C01", "finding": "The register magnitude contrast was inspected before this decomposition was frozen.", "impact": "This is post-hoc model compression, not independent discovery."},
        {"counterexample_id": "C02", "finding": "The exact opaque cell remains an indispensable baseline key.", "impact": "Conditioning does not predict an unseen wrapper license."},
        {"counterexample_id": "C03", "finding": "The fixed-crossfit max-three null does not retrain coefficients.", "impact": "Its p-value is descriptive rather than an exact refitted-null probability."},
        {"counterexample_id": "C04", "finding": "Register labels combine section, Currier, and practical layout ecology.", "impact": "A register-conditioned magnitude is not a linguistic or semantic category."},
        {"counterexample_id": "C05", "finding": "No f84 row occurs in the frozen panel or scored outputs.", "impact": "The prohibited holdout remains untouched."},
    ]
    write(COUNTER, counterexamples)
    report = ["# GDT323 — register-conditioned renderer magnitude", "", f"Status: **{status}**.", "", "The same two renderer rules were fitted globally, by Currier stratum, and by the five fixed registers. No new wrapper rule or section-specific exception was searched.", "", "| model | parameters | gain bits/event | raw gain bits | charge | charged gain | positive folios | max-three p |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in model_rows[1:]:
        report.append(f"| {row['model']} | {row['parameters']} | {float(row['gain_bits_per_event']):+.6f} | {float(row['raw_gain_bits']):+.2f} | {float(row['charge_bits']):.2f} | {float(row['charged_gain_bits']):+.2f} | {row['positive_folios']}/91 | {float(row['max_three_diagnostic_p']):.8f} |")
    report += ["", f"Minimum charged held code: **{selected_model}**. The conditioning result concerns coefficient magnitude only; the rule inventory remains exactly `s × LINE_START` and `q × PREV_DY`.", "", "## Register contributions", "", "| register | events | global | Currier | register |", "|---|---:|---:|---:|---:|"]
    by_register = {(row["register"], row["model"]): row for row in register_rows}
    for register in design["registers"]:
        values = [by_register[(register, model)] for model in candidates]
        report.append(f"| {register} | {values[0]['events']} | {float(values[0]['gain_bits_per_event']):+.6f} | {float(values[1]['gain_bits_per_event']):+.6f} | {float(values[2]['gain_bits_per_event']):+.6f} |")
    report += ["", "## Claim ceiling", "", design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored."]
    REPORT.write_text("\n".join(report) + "\n")
    outputs = [MODELS, FOLDS, REGISTERS, SECTIONS, COEFFICIENTS, NULL, COUNTER, REPORT]
    inputs = [PANEL, SOURCE, R / "gdt323_design_validation.json", R / "gdt321_result.json", R / "gdt322_result.json"]
    summary = {"events": len(rows), "cells": len({row['cell_id'] for row in rows}), "folios": len(folios), "selected_model": selected_model, "selected_gain_bits_per_event": float(selected["gain_bits_per_event"]), "selected_charged_gain_bits": float(selected["charged_gain_bits"]), "global_charged_gain_bits": float(next(row for row in model_rows if row["model"] == "GLOBAL_TWO_RULE")["charged_gain_bits"]), "currier_charged_gain_bits": float(next(row for row in model_rows if row["model"] == "CURRIER_TWO_RULE")["charged_gain_bits"]), "register_charged_gain_bits": float(next(row for row in model_rows if row["model"] == "REGISTER_TWO_RULE")["charged_gain_bits"])}
    result = {"schema": "GDT323_REGISTER_CONDITIONED_RENDERER_RESULT_V1", "status": status, "summary": summary, "semantic_assignments": 0, "claim_ceiling": design["claim_ceiling"], "f84": {"input_rows": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False}, "inputs": {path.name: sha(path) for path in inputs}, "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}, "implementation": {Path(__file__).name: sha(Path(__file__))}, "outputs": {path.name: sha(path) for path in outputs}}
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "summary": summary}, sort_keys=True))


if __name__ == "__main__":
    main()
