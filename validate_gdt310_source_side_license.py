#!/usr/bin/env python3
"""Independently rebuild GDT310 scores, null, decision, and bindings."""
import csv
import hashlib
import json
import statistics
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
FEATURES = R / "gdt310_source_side_features.tsv"
DESIGN = R / "gdt310_design.json"
SCORES = R / "gdt310_model_scores.tsv"
RESULT = R / "gdt310_result.json"
OUT = R / "gdt310_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def matrix(rows, names):
    values = np.array([[float(row[name]) for name in names] for row in rows])
    sd = values.std(0)
    sd[sd == 0] = 1
    return np.column_stack([np.ones(len(rows)), (values - values.mean(0)) / sd])


def hat(values, ridge):
    penalty = np.eye(values.shape[1]) * ridge
    penalty[0, 0] = 0
    return values @ np.linalg.pinv(values.T @ values + penalty) @ values.T


def loo(hat_matrix, labels, clip):
    fitted = hat_matrix @ labels
    diagonal = np.diag(hat_matrix)
    return np.clip((fitted - diagonal * labels) / (1 - diagonal), clip[0], clip[1])


def brier(prediction, labels):
    return float(np.mean((prediction - labels) ** 2))


def auc(prediction, labels):
    positive = prediction[labels == 1]
    negative = prediction[labels == 0]
    pairs = sum((a > b) + 0.5 * (a == b) for a in positive for b in negative)
    return float(pairs / (len(positive) * len(negative)))


def quartiles(rows):
    events = np.array([int(row["source_events"]) for row in rows])
    order = np.argsort(events, kind="stable")
    bins = np.empty(len(rows), int)
    for rank, index in enumerate(order):
        bins[index] = min(3, rank * 4 // len(rows))
    return bins


def permute(labels, bins, seed, world, operation):
    result = labels.copy()
    for bin_id in sorted(set(bins)):
        indices = np.where(bins == bin_id)[0]
        values = labels[indices].copy()
        key_text = f"{seed}|{world}|{operation}|{bin_id}"
        key = int(hashlib.sha256(key_text.encode()).hexdigest()[:16], 16)
        rng = np.random.default_rng(key)
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
    all_rows = read(FEATURES)
    scores = {(row["operation"], row["model"]): row for row in read(SCORES)}
    operation_data = {}
    observed = {}
    for operation in design["operations"]:
        rows = [row for row in all_rows if row["operation"] == operation]
        labels = np.array([int(row["licensed"]) for row in rows], float)
        bins = quartiles(rows)
        matrices = {
            model: hat(matrix(rows, names), design["ridge"])
            for model, names in design["models"].items()
        }
        prediction = {
            model: loo(value, labels, design["prediction_clip"])
            for model, value in matrices.items()
        }
        base = brier(prediction["FREQUENCY"], labels)
        operation_data[operation] = (labels, bins, matrices)
        for model, values in prediction.items():
            gain = base - brier(values, labels)
            observed[(operation, model)] = gain
            row = scores[(operation, model)]
            check(
                "observed_scores",
                close(row["brier"], brier(values, labels))
                and close(row["brier_gain_vs_frequency"], gain)
                and close(row["roc_auc"], auc(values, labels)),
            )

    tests = [
        (operation, model)
        for operation in design["operations"]
        for model in design["models"]
        if model != "FREQUENCY"
    ]
    null = {key: [] for key in tests}
    for world in range(design["null_worlds"]):
        for operation, (labels, bins, matrices) in operation_data.items():
            shuffled = permute(labels, bins, design["null_seed"], world, operation)
            base = brier(loo(matrices["FREQUENCY"], shuffled, design["prediction_clip"]), shuffled)
            for model in design["models"]:
                if model != "FREQUENCY":
                    value = base - brier(loo(matrices[model], shuffled, design["prediction_clip"]), shuffled)
                    null[(operation, model)].append(value)
    means = {key: statistics.mean(values) for key, values in null.items()}
    sds = {key: statistics.pstdev(values) for key, values in null.items()}
    zscores = {key: (observed[key] - means[key]) / sds[key] if sds[key] else 0.0 for key in tests}
    max_z = [
        max((null[key][world] - means[key]) / sds[key] if sds[key] else 0.0 for key in tests)
        for world in range(design["null_worlds"])
    ]
    for key in tests:
        local_p = (1 + sum(value >= observed[key] - 1e-15 for value in null[key])) / (1 + design["null_worlds"])
        max_p = (1 + sum(value >= zscores[key] - 1e-15 for value in max_z)) / (1 + design["null_worlds"])
        row = scores[key]
        check(
            "null_scores",
            close(row["null_mean_gain"], means[key])
            and close(row["null_sd_gain"], sds[key])
            and close(row["local_p"], local_p)
            and close(row["max12_p"], max_p),
        )

    classes = {}
    for operation in design["operations"]:
        row = scores[(operation, "FULL")]
        passes = (
            float(row["brier_gain_vs_frequency"]) > 0
            and float(row["roc_auc"]) >= design["decision"]["full_auc_minimum"]
            and float(row["max12_p"]) <= design["decision"]["full_max12_p_le"]
        )
        classes[operation] = "TARGET_BLIND_LICENSE_PREDICTABLE" if passes else "TARGET_BLIND_LICENSE_OPAQUE_OR_UNRESOLVED"
    status = "SOURCE_SIDE_LICENSE_PARTLY_PREDICTABLE" if "TARGET_BLIND_LICENSE_PREDICTABLE" in classes.values() else "SOURCE_SIDE_LICENSE_NOT_PREDICTABLE"
    result = json.loads(RESULT.read_text())
    stored = result.pop("content_sha256")
    check("content_hash", stored == canonical_hash(result))
    check("status_classes", result["status"] == status and result["classifications"] == classes)
    check("input_hashes", all(result["inputs"][name] == sha(R / name) for name in result["inputs"]))
    check("output_hashes", all(result["outputs"][name] == sha(R / name) for name in result["outputs"]))
    check("document_hashes", all(result["documents"][name] == sha(R / name) for name in result["documents"]))
    check("implementation_hash", all(result["implementation"][name] == sha(R / name) for name in result["implementation"]))
    check("f84_flags", not any(result["f84"].values()))
    validation = {
        "schema": "GDT310_SOURCE_SIDE_OPERATION_LICENSE_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks": checks,
        "result_sha256": sha(RESULT),
        "reconstructed_status": status,
        "f84_rows": 0,
        "scope": "INDEPENDENT_OBSERVED_SCORE_EXACT_NULL_DECISION_AND_BINDING_RECONSTRUCTION",
    }
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "reconstructed_status": status}, sort_keys=True))


if __name__ == "__main__":
    main()
