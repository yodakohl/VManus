#!/usr/bin/env python3
"""Independently rebuild GDT320 dual-entry scores, null, and decision."""
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
MODELS = R / "gdt320_model_scores.tsv"
FOLDS = R / "gdt320_folio_scores.tsv"
SECTIONS = R / "gdt320_section_scores.tsv"
COEFFICIENTS = R / "gdt320_coefficient_summary.tsv"
NULL = R / "gdt320_null.tsv"
RESULT = R / "gdt320_result.json"
OUT = R / "gdt320_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b):
    return abs(float(a) - float(b)) < 5e-12


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
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    design = json.loads(DESIGN.read_text())
    rows = read(PANEL)
    truth_map = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: int(row["wrapper"] == "d") for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"}
    check("source_join", all(row["event_id_sha256"] in truth_map for row in rows))
    truth = np.array([truth_map[row["event_id_sha256"]] for row in rows], float)
    model_names = list(design["models"])
    probabilities = {model: np.zeros(len(rows)) for model in model_names}
    coefficients = defaultdict(list)
    exported_folds = {(row["physical_folio"], row["model"]): row for row in read(FOLDS)}
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
            gain = 0.0 if model == "CELL" else float(np.sum(event_bits(probabilities["CELL"][indices], truth[indices]) - event_bits(probabilities[model][indices], truth[indices])))
            check("fold", close(exported_folds[(folio, model)]["gain_bits"], gain))
            for offset, feature in enumerate(features, 1):
                coefficients[(model, feature)].append(float(beta[-len(features) - 1 + offset]))
    baseline_bits = event_bits(probabilities["CELL"], truth)
    gains = {model: baseline_bits - event_bits(probabilities[model], truth) for model in model_names[1:]}
    observed = {model: float(value.mean()) for model, value in gains.items()}
    exported_models = {row["model"]: row for row in read(MODELS)}
    for model in model_names[1:]:
        check("model_gain", close(exported_models[model]["gain_bits_per_event"], observed[model]))
    exported_coefficients = {(row["model"], row["feature"]): row for row in read(COEFFICIENTS)}
    for key, values in coefficients.items():
        check("coefficient", close(exported_coefficients[key]["mean_coefficient"], np.mean(values)) and int(exported_coefficients[key]["positive_folds"]) == sum(value > 0 for value in values))
    exported_sections = {(row["section"], row["model"]): row for row in read(SECTIONS)}
    for key, exported in exported_sections.items():
        indices = [index for index, row in enumerate(rows) if row["section"] == key[0]]
        check("section", close(exported["gain_bits"], gains[key[1]][indices].sum()))
    exported_null = read(NULL)
    check("null_rows", len(exported_null) == design["null"]["worlds"])
    max_values = []
    for world in range(design["null"]["worlds"]):
        permuted = permute(truth, rows, design["null"]["seed"], world)
        base = event_bits(probabilities["CELL"], permuted)
        values = {model: float(np.mean(base - event_bits(probabilities[model], permuted))) for model in model_names[1:]}
        for model, value in values.items():
            check("null_value", close(exported_null[world][model], value))
        max_values.append(max(values.values()))
        check("null_max", close(exported_null[world]["max_three_gain_bits_per_event"], max_values[-1]))
    for model in model_names[1:]:
        max_p = (1 + sum(value >= observed[model] - 1e-15 for value in max_values)) / (1 + len(max_values))
        check("max_p", close(exported_models[model]["max_three_diagnostic_p"], max_p))
    line_delta = matched_delta(rows, truth, "line_first")
    prev_delta = matched_delta(rows, truth, "prev_dy")
    line_positive = int(exported_coefficients[("CELL_BOTH", "line_first")]["positive_folds"])
    prev_positive = int(exported_coefficients[("CELL_BOTH", "prev_dy")]["positive_folds"])
    positive_sections = int(sum(float(row["gain_bits"]) > 0 for (section, model), row in exported_sections.items() if model == "CELL_BOTH" and section in ("B", "H", "S") and int(row["powered"])))
    joint = exported_models["CELL_BOTH"]
    passed = float(joint["selector_paid_gain_bits"]) > 0 and line_delta > 0 and prev_delta > 0 and line_positive >= design["decision"]["positive_coefficients_min_each"] and prev_positive >= design["decision"]["positive_coefficients_min_each"] and positive_sections >= design["decision"]["positive_powered_sections_min"] and float(joint["max_three_diagnostic_p"]) <= design["decision"]["max_three_p_le"]
    status = "D_DUAL_ENTRY_EXTENDS_TO_FRESH_SURFACES" if passed else "D_DUAL_ENTRY_FRESH_TRANSFER_WEAK_OR_FAILED"
    result = json.loads(RESULT.read_text())
    stored_content = result.pop("content_sha256")
    check("content", stored_content == canonical_hash(result))
    check("status", result["status"] == status)
    check("summary", close(result["summary"]["joint_gain_bits_per_event"], observed["CELL_BOTH"]) and close(result["summary"]["matched_line_start_delta"], line_delta) and close(result["summary"]["matched_prev_dy_delta"], prev_delta))
    check("bindings", all(result["inputs"][name] == sha(R / name) for name in result["inputs"]) and all(result["outputs"][name] == sha(R / name) for name in result["outputs"]) and all(result["documents"][name] == sha(R / name) for name in result["documents"]) and all(result["implementation"][name] == sha(R / name) for name in result["implementation"]))
    check("f84", not any(result["f84"].values()) and not any(row["page"].startswith("f84") for row in rows))
    validation = {"schema": "GDT320_FRESH_D_DUAL_ENTRY_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "result_sha256": sha(RESULT), "f84_rows": 0, "scope": "INDEPENDENT_CROSSFIT_MAX_THREE_DECISION_AND_BINDING_RECONSTRUCTION"}
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "reconstructed_status": status}, sort_keys=True))


if __name__ == "__main__":
    main()
