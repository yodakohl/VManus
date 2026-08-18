#!/usr/bin/env python3
"""Independently rebuild GDT311 held scores, null tails, and bindings."""
import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PAIRS = R / "gdt303_pair_deltas.tsv"
PANEL = R / "gdt311_frozen_event_panel.tsv"
DESIGN = R / "gdt311_design.json"
SCORES = R / "gdt311_model_scores.tsv"
RESULT = R / "gdt311_result.json"
OUT = R / "gdt311_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def make_pair_id(operation, source_hash, target_hash):
    return hashlib.sha256(f"{operation}|{source_hash}|{target_hash}".encode()).hexdigest()[:20]


def labels_for(operations):
    surface = {}
    for row in read(PAIRS):
        if row["operation"] in operations:
            identifier = make_pair_id(row["operation"], row["source_surface_sha256"], row["target_surface_sha256"])
            surface[(row["operation"], row["source_surface_sha256"])] = (identifier, 0)
            surface[(row["operation"], row["target_surface_sha256"])] = (identifier, 1)
    labels = {}
    f84 = 0
    for event in read(SOURCE):
        if event["control_id"] != "VOYNICH_REFERENCE":
            continue
        f84 += int(event["page"].startswith("f84") or event["locus"].startswith("f84"))
        for operation in operations:
            key = (operation, event["source_surface_sha256"])
            if key in surface:
                anonymous = hashlib.sha256(f"{operation}|{event['observation_id']}".encode()).hexdigest()[:20]
                labels[anonymous] = surface[key]
    assert f84 == 0
    return labels


def matrices(training, test, pairs, names, categorical):
    pair_columns = sorted(pairs)
    categories = {name: sorted({row[name] for row in training}) for name in names if name in categorical}
    numeric = [name for name in names if name not in categorical]
    means = {name: statistics.mean(float(row[name]) for row in training) for name in numeric}
    sds = {name: statistics.pstdev(float(row[name]) for row in training) or 1.0 for name in numeric}

    def build(rows):
        matrix = []
        for row in rows:
            values = [1.0] + [float(row["pair_id"] == value) for value in pair_columns]
            values += [(float(row[name]) - means[name]) / sds[name] for name in numeric]
            for name in names:
                if name in categorical:
                    values += [float(row[name] == value) for value in categories[name]]
            matrix.append(values)
        return np.array(matrix, float)

    return build(training), build(test)


def fit_predict(train_x, train_y, test_x, ridge, clip):
    beta = np.zeros(train_x.shape[1])
    penalty = np.eye(train_x.shape[1]) * ridge
    penalty[0, 0] = 0.0
    for _ in range(100):
        probability = 1 / (1 + np.exp(-np.clip(train_x @ beta, -30, 30)))
        weights = np.maximum(probability * (1 - probability), 1e-8)
        gradient = train_x.T @ (train_y - probability) - penalty @ beta
        hessian = train_x.T @ (train_x * weights[:, None]) + penalty
        step = np.linalg.pinv(hessian) @ gradient
        beta += step
        if np.max(np.abs(step)) < 1e-10:
            break
    prediction = 1 / (1 + np.exp(-np.clip(test_x @ beta, -30, 30)))
    return np.clip(prediction, clip[0], clip[1])


def bits(prediction, labels):
    return float(-np.mean(labels * np.log2(prediction) + (1 - labels) * np.log2(1 - prediction)))


def brier(prediction, labels):
    return float(np.mean((prediction - labels) ** 2))


def auc(prediction, labels):
    positive = prediction[labels == 1]
    negative = prediction[labels == 0]
    return float(sum((a > b) + 0.5 * (a == b) for a in positive for b in negative) / (len(positive) * len(negative)))


def shuffle(labels, strata, seed, world, suffix):
    result = labels.copy()
    groups = defaultdict(list)
    for index, stratum in enumerate(strata):
        groups[stratum].append(index)
    for stratum, indices in sorted(groups.items()):
        values = labels[indices].copy()
        text = f"{seed}|{world}|{suffix}|{'|'.join(stratum)}"
        rng = np.random.default_rng(int(hashlib.sha256(text.encode()).hexdigest()[:16], 16))
        rng.shuffle(values)
        result[indices] = values
    return result


def close(left, right):
    return abs(float(left) - float(right)) < 5e-12


def main():
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    design = json.loads(DESIGN.read_text())
    panel = read(PANEL)
    labels = labels_for(design["operations"])
    scores = {(row["operation"], row["model"]): row for row in read(SCORES)}
    observed = {}
    operation_data = {}
    for operation in design["operations"]:
        rows = [row for row in panel if row["operation"] == operation]
        training = [row for row in rows if row["split"] == "TRAIN"]
        test = [row for row in rows if row["split"] == "TEST"]
        train_y = np.array([labels[row["anonymous_event_id"]][1] for row in training], float)
        test_y = np.array([labels[row["anonymous_event_id"]][1] for row in test], float)
        predicted = {}
        for model, names in design["models"].items():
            train_x, test_x = matrices(training, test, {row["pair_id"] for row in rows}, names, design["categorical_features"])
            predicted[model] = fit_predict(train_x, train_y, test_x, design["ridge"], design["probability_clip"])
        base = bits(predicted["PAIR"], test_y)
        operation_data[operation] = (test, test_y, predicted)
        for model, probability in predicted.items():
            gain = base - bits(probability, test_y)
            observed[(operation, model)] = gain
            row = scores[(operation, model)]
            check("observed_score", close(row["held_bits_per_event"], bits(probability, test_y)) and close(row["gain_vs_pair_bits_per_event"], gain) and close(row["brier"], brier(probability, test_y)) and close(row["roc_auc"], auc(probability, test_y)))

    tests = [(operation, model) for operation in design["operations"] for model in design["models"] if model != "PAIR"]
    primary = {key: [] for key in tests}
    pair_only = {key: [] for key in tests}
    worlds = design["null"]["worlds"]
    seed = design["null"]["seed"]
    for world in range(worlds):
        for operation, (test, test_y, predicted) in operation_data.items():
            first = shuffle(test_y, [(row["pair_id"], row["register"]) for row in test], seed, world, operation + "|PRIMARY")
            second = shuffle(test_y, [(row["pair_id"],) for row in test], seed, world, operation + "|PAIR")
            for shuffled, store in ((first, primary), (second, pair_only)):
                base = bits(predicted["PAIR"], shuffled)
                for model in design["models"]:
                    if model != "PAIR":
                        store[(operation, model)].append(base - bits(predicted[model], shuffled))
    means = {key: statistics.mean(values) for key, values in primary.items()}
    sds = {key: statistics.pstdev(values) for key, values in primary.items()}
    zscores = {key: (observed[key] - means[key]) / sds[key] if sds[key] else 0.0 for key in tests}
    max_z = [max((primary[key][world] - means[key]) / sds[key] if sds[key] else 0.0 for key in tests) for world in range(worlds)]
    for key in tests:
        local = (1 + sum(value >= observed[key] - 1e-15 for value in primary[key])) / (1 + worlds)
        maximum = (1 + sum(value >= zscores[key] - 1e-15 for value in max_z)) / (1 + worlds)
        sensitivity = (1 + sum(value >= observed[key] - 1e-15 for value in pair_only[key])) / (1 + worlds)
        row = scores[key]
        check("null_score", close(row["null_mean_gain"], means[key]) and close(row["null_centered_gain"], observed[key] - means[key]) and close(row["local_p"], local) and close(row["max12_p"], maximum) and close(row["pair_only_sensitivity_p"], sensitivity))

    classes = {}
    for operation in design["operations"]:
        row = scores[(operation, "PAIR_FULL")]
        passes = float(row["gain_vs_pair_bits_per_event"]) > 0 and float(row["null_centered_gain"]) > 0 and float(row["roc_auc"]) >= design["decision"]["auc_minimum"] and float(row["max12_p"]) <= design["decision"]["max12_p_le"]
        classes[operation] = "HELD_EVENT_CHOICE_TRANSFER" if passes else "EVENT_CHOICE_WEAK_OR_UNRESOLVED"
    passed = sum(value == "HELD_EVENT_CHOICE_TRANSFER" for value in classes.values())
    if passed == len(classes):
        status = "OPERATION_EVENT_CHOICE_TRANSFERS_ON_LICENSED_PAIRS"
    elif passed:
        status = "OPERATION_EVENT_CHOICE_PARTLY_TRANSFERS"
    else:
        status = "OPERATION_EVENT_CHOICE_NOT_TRANSFERRED"
    result = json.loads(RESULT.read_text())
    stored = result.pop("content_sha256")
    check("content_hash", stored == canonical_hash(result))
    check("status_classes", result["status"] == status and result["classifications"] == classes)
    check("input_hashes", all(result["inputs"][name] == sha(R / name) for name in result["inputs"]))
    check("output_hashes", all(result["outputs"][name] == sha(R / name) for name in result["outputs"]))
    check("document_hashes", all(result["documents"][name] == sha(R / name) for name in result["documents"]))
    check("implementation_hash", all(result["implementation"][name] == sha(R / name) for name in result["implementation"]))
    check("f84_flags", not any(result["f84"].values()))
    validation = {"schema": "GDT311_OPERATION_EVENT_CHOICE_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "result_sha256": sha(RESULT), "reconstructed_status": status, "f84_rows": 0, "scope": "INDEPENDENT_SPLIT_LABEL_FIT_SCORE_EXACT_NULL_DECISION_AND_BINDING_RECONSTRUCTION"}
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "reconstructed_status": status}, sort_keys=True))


if __name__ == "__main__":
    main()
