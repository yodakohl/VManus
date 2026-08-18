#!/usr/bin/env python3
"""Independently rebuild GDT319 labels, crossfit scores, and diagnostic."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt319_frozen_panel.tsv"
DESIGN = R / "gdt319_design.json"
PREDICTIONS = R / "gdt319_predictions.tsv"
FOLDS = R / "gdt319_folio_scores.tsv"
SECTIONS = R / "gdt319_section_scores.tsv"
NULL = R / "gdt319_null.tsv"
RESULT = R / "gdt319_result.json"
OUT = R / "gdt319_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b):
    return abs(float(a) - float(b)) < 5e-12


def matrices(train, test, full):
    cells = sorted({row["cell_id"] for row in train})
    def encode(rows):
        return np.array([[1.0] + [float(row["cell_id"] == cell) for cell in cells] + ([float(row["line_first"])] if full else []) for row in rows])
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


def matched_delta(rows, truth):
    strata = defaultdict(lambda: [[], []])
    for index, row in enumerate(rows):
        strata[(row["cell_id"], row["register"])][int(row["line_first"])].append(int(truth[index]))
    numerator = denominator = 0.0
    for elsewhere, line_start in strata.values():
        if elsewhere and line_start:
            weight = len(elsewhere) * len(line_start) / (len(elsewhere) + len(line_start))
            numerator += weight * (sum(line_start) / len(line_start) - sum(elsewhere) / len(elsewhere))
            denominator += weight
    return numerator / denominator if denominator else 0.0


def main():
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    design = json.loads(DESIGN.read_text())
    rows = read(PANEL)
    truth_map = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: int(row["wrapper"] == "t") for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"}
    check("source_join", all(row["event_id_sha256"] in truth_map for row in rows))
    truth = np.array([truth_map[row["event_id_sha256"]] for row in rows], float)
    baseline = np.zeros(len(rows))
    candidate = np.zeros(len(rows))
    coefficients = {}
    exported_folds = {row["physical_folio"]: row for row in read(FOLDS)}
    for folio in sorted({row["physical_folio"] for row in rows}):
        train = [row for row in rows if row["physical_folio"] != folio]
        test = [row for row in rows if row["physical_folio"] == folio]
        train_truth = np.array([truth_map[row["event_id_sha256"]] for row in train], float)
        indices = [index for index, row in enumerate(rows) if row["physical_folio"] == folio]
        train_x, test_x = matrices(train, test, False)
        baseline[indices], _ = fit(train_x, train_truth, test_x, design["ridge"])
        train_x, test_x = matrices(train, test, True)
        candidate[indices], beta = fit(train_x, train_truth, test_x, design["ridge"])
        coefficients[folio] = beta[-1]
        gain = float(np.sum(event_bits(baseline[indices], truth[indices]) - event_bits(candidate[indices], truth[indices])))
        exported = exported_folds[folio]
        check("fold", close(exported["line_start_coefficient"], beta[-1]) and close(exported["gain_bits"], gain))
    gains = event_bits(baseline, truth) - event_bits(candidate, truth)
    gain = float(gains.mean())
    delta = matched_delta(rows, truth)
    predictions = {row["event_id_sha256"]: row for row in read(PREDICTIONS)}
    for index, row in enumerate(rows):
        exported = predictions[row["event_id_sha256"]]
        check("prediction", int(exported["observed_t"]) == int(truth[index]) and close(exported["cell_probability"], baseline[index]) and close(exported["cell_line_start_probability"], candidate[index]) and close(exported["gain_bits"], gains[index]))
    exported_sections = {row["section"]: row for row in read(SECTIONS)}
    for section, exported in exported_sections.items():
        indices = [index for index, row in enumerate(rows) if row["section"] == section]
        check("section", close(exported["gain_bits"], gains[indices].sum()))
    null_values = []
    for world in range(design["null"]["worlds"]):
        permuted = permute(truth, rows, design["null"]["seed"], world)
        null_values.append(float(np.mean(event_bits(baseline, permuted) - event_bits(candidate, permuted))))
    exported_null = read(NULL)
    check("null_rows", len(exported_null) == len(null_values))
    check("null_values", all(close(row["alignment_gain_bits_per_event"], value) for row, value in zip(exported_null, null_values)))
    diagnostic_p = (1 + sum(value >= gain - 1e-15 for value in null_values)) / (1 + len(null_values))
    positive_coefficients = int(sum(value > 0 for value in coefficients.values()))
    positive_folios = int(sum(float(row["gain_bits"]) > 0 for row in exported_folds.values()))
    positive_powered_sections = int(sum(float(exported_sections[section]["gain_bits"]) > 0 for section in ("B", "H", "S") if int(exported_sections[section]["powered"])))
    summary = {"cells": 7, "events": 50, "t_events": 20, "folios": 31, "gain_bits_per_event": gain, "matched_line_start_delta": delta, "positive_coefficients": positive_coefficients, "positive_folios": positive_folios, "positive_powered_sections": positive_powered_sections, "alignment_diagnostic_p": diagnostic_p}
    result = json.loads(RESULT.read_text())
    stored_content = result.pop("content_sha256")
    check("summary", all(close(result["summary"][key], value) if isinstance(value, float) else result["summary"][key] == value for key, value in summary.items()))
    check("content", stored_content == canonical_hash(result))
    check("status", result["status"] == "T_LINE_ENTRY_FRESH_SURFACE_TRANSFER_WEAK_OR_FAILED")
    check("bindings", all(result["inputs"][name] == sha(R / name) for name in result["inputs"]) and all(result["outputs"][name] == sha(R / name) for name in result["outputs"]) and all(result["documents"][name] == sha(R / name) for name in result["documents"]) and all(result["implementation"][name] == sha(R / name) for name in result["implementation"]))
    check("f84", not any(result["f84"].values()) and not any(row["page"].startswith("f84") for row in rows))
    validation = {"schema": "GDT319_FRESH_T_LINE_ENTRY_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "result_sha256": sha(RESULT), "f84_rows": 0, "scope": "INDEPENDENT_LABEL_CROSSFIT_SCORE_ALIGNMENT_AND_BINDING_RECONSTRUCTION"}
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
