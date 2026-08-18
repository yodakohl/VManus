#!/usr/bin/env python3
"""Independently reconstruct GDT318 multiclass crossfit scores and diagnostics."""
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
MODELS = R / "gdt318_model_scores.tsv"
FOLDS = R / "gdt318_folio_scores.tsv"
SECTIONS = R / "gdt318_section_scores.tsv"
WRAPPERS = R / "gdt318_wrapper_scores.tsv"
COEFFICIENTS = R / "gdt318_coefficient_summary.tsv"
NULL = R / "gdt318_null.tsv"
RESULT = R / "gdt318_result.json"
OUT = R / "gdt318_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b):
    return abs(float(a) - float(b)) < 5e-12


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
    return (
        np.array([logged[cell_index[row["cell_id"]]] for row in train]),
        np.array([logged[cell_index[row["cell_id"]]] for row in test]),
    )


def feature_matrix(rows, features):
    return np.array([[float(row[name]) for name in features] for row in rows])


def fit(train_offsets, train_x, train_truth, test_offsets, test_x, class_count, ridge):
    if train_x.shape[1] == 0:
        return softmax(test_offsets), np.zeros((class_count, 0))
    beta = np.zeros((class_count, train_x.shape[1]))
    eye = np.eye(beta.size) * ridge
    for _ in range(60):
        probability = softmax(train_offsets + train_x @ beta.T)
        target = np.zeros_like(probability)
        target[np.arange(len(train_truth)), train_truth] = 1
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
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    design = json.loads(DESIGN.read_text())
    rows = read(PANEL)
    classes = design["classes"]
    class_index = {value: index for index, value in enumerate(classes)}
    source_truth = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: class_index[row["wrapper"]] for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"}
    check("source_join", all(row["event_id_sha256"] in source_truth for row in rows))
    truth = np.array([source_truth[row["event_id_sha256"]] for row in rows], int)
    model_names = list(design["models"])
    probabilities = {model: np.zeros((len(rows), len(classes))) for model in model_names}
    coefficient_values = defaultdict(list)
    exported_folds = {(row["physical_folio"], row["model"]): row for row in read(FOLDS)}
    folios = sorted({row["physical_folio"] for row in rows})
    for folio in folios:
        train_indices = [index for index, row in enumerate(rows) if row["physical_folio"] != folio]
        test_indices = [index for index, row in enumerate(rows) if row["physical_folio"] == folio]
        train = [rows[index] for index in train_indices]
        test = [rows[index] for index in test_indices]
        train_truth = truth[train_indices]
        train_offsets, test_offsets = offsets(train, test, train_truth, len(classes), design["alpha"])
        baseline = softmax(test_offsets)
        probabilities["CELL"][test_indices] = baseline
        baseline_bits = bits(baseline, truth[test_indices])
        for model in model_names[1:]:
            features = design["models"][model]
            predicted, beta = fit(train_offsets, feature_matrix(train, features), train_truth, test_offsets, feature_matrix(test, features), len(classes), design["ridge"])
            probabilities[model][test_indices] = predicted
            gain = float(np.sum(baseline_bits - bits(predicted, truth[test_indices])))
            exported = exported_folds[(folio, model)]
            check("fold", close(exported["gain_bits"], gain))
            for class_position, wrapper in enumerate(classes):
                for feature_position, feature in enumerate(features):
                    coefficient_values[(model, wrapper, feature)].append(float(beta[class_position, feature_position]))

    baseline_bits = bits(probabilities["CELL"], truth)
    gains = {model: baseline_bits - bits(probabilities[model], truth) for model in model_names[1:]}
    observed = {model: float(values.mean()) for model, values in gains.items()}
    exported_models = {row["model"]: row for row in read(MODELS)}
    check("baseline", close(exported_models["CELL"]["held_bits_per_event"], baseline_bits.mean()))
    for model in model_names[1:]:
        check("model_gain", close(exported_models[model]["gain_bits_per_event"], observed[model]))

    exported_sections = {(row["section"], row["model"]): row for row in read(SECTIONS)}
    for key, exported in exported_sections.items():
        indices = [index for index, row in enumerate(rows) if row["section"] == key[0]]
        check("section", close(exported["gain_bits"], gains[key[1]][indices].sum()))
    exported_wrappers = {(row["wrapper"], row["model"]): row for row in read(WRAPPERS)}
    for key, exported in exported_wrappers.items():
        indices = np.where(truth == class_index[key[0]])[0]
        check("wrapper", close(exported["gain_bits"], gains[key[1]][indices].sum()))
    exported_coefficients = {(row["model"], row["wrapper"], row["feature"]): row for row in read(COEFFICIENTS)}
    for key, values in coefficient_values.items():
        exported = exported_coefficients[key]
        check("coefficient", close(exported["mean_coefficient"], np.mean(values)) and int(exported["positive_folds"]) == sum(value > 0 for value in values))

    exported_null = read(NULL)
    check("null_rows", len(exported_null) == design["null"]["worlds"])
    null_by_model = {model: [] for model in model_names[1:]}
    max_values = []
    for world in range(design["null"]["worlds"]):
        permuted = permute(truth, rows, design["null"]["seed"], world)
        base = bits(probabilities["CELL"], permuted)
        values = {}
        for model in model_names[1:]:
            values[model] = float(np.mean(base - bits(probabilities[model], permuted)))
            null_by_model[model].append(values[model])
            check("null_value", close(exported_null[world][model], values[model]))
        max_values.append(max(values.values()))
        check("null_max", close(exported_null[world]["max_three_gain_bits_per_event"], max_values[-1]))
    for model in model_names[1:]:
        max_p = (1 + sum(value >= observed[model] - 1e-15 for value in max_values)) / (1 + len(max_values))
        check("max_p", close(exported_models[model]["max_three_diagnostic_p"], max_p))

    result = json.loads(RESULT.read_text())
    stored_content = result.pop("content_sha256")
    check("content", stored_content == canonical_hash(result))
    joint = exported_models["CELL_BOTH"]
    s_positive = int(exported_coefficients[("CELL_BOTH", "s", "line_first")]["positive_folds"])
    q_positive = int(exported_coefficients[("CELL_BOTH", "q", "prev_dy")]["positive_folds"])
    positive_sections = sum(float(row["gain_bits"]) > 0 for (section, model), row in exported_sections.items() if model == "CELL_BOTH" and section in ("B", "H", "S"))
    passed = float(joint["selector_paid_gain_bits"]) > 0 and positive_sections >= design["decision"]["positive_powered_sections_min"] and s_positive >= design["decision"]["s_line_positive_coefficients_min"] and q_positive >= design["decision"]["q_prev_dy_positive_coefficients_min"] and float(joint["max_three_diagnostic_p"]) <= design["decision"]["max_three_p_le"]
    status = "GLOBAL_WRAPPER_ENTRY_STATE_TRANSFERS" if passed else "GLOBAL_WRAPPER_ENTRY_STATE_WEAK_OR_FAILED"
    check("status", result["status"] == status)
    check("summary", result["summary"]["s_line_positive_coefficients"] == s_positive and result["summary"]["q_prev_dy_positive_coefficients"] == q_positive and close(result["summary"]["joint_gain_bits_per_event"], observed["CELL_BOTH"]))
    check("bindings", all(result["inputs"][name] == sha(R / name) for name in result["inputs"]) and all(result["outputs"][name] == sha(R / name) for name in result["outputs"]) and all(result["documents"][name] == sha(R / name) for name in result["documents"]) and all(result["implementation"][name] == sha(R / name) for name in result["implementation"]))
    check("f84", not any(result["f84"].values()) and not any(row["page"].startswith("f84") for row in rows))
    validation = {"schema": "GDT318_GLOBAL_WRAPPER_ENTRY_STATE_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "result_sha256": sha(RESULT), "f84_rows": 0, "scope": "INDEPENDENT_MULTICLASS_CROSSFIT_SCORE_NULL_DECISION_AND_BINDING_RECONSTRUCTION"}
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "reconstructed_status": status}, sort_keys=True))


if __name__ == "__main__":
    main()
