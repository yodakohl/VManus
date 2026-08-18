#!/usr/bin/env python3
"""Score target-blind operation licenses from source-wrapper ecology."""
import csv
import hashlib
import json
import statistics
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
FEATURES = R / "gdt310_source_side_features.tsv"
DESIGN = R / "gdt310_design.json"
METHOD = R / "GDT310_SOURCE_SIDE_OPERATION_LICENSE_METHOD.md"
PRED = R / "gdt310_host_predictions.tsv"
SCORES = R / "gdt310_model_scores.tsv"
NULL = R / "gdt310_null_max.tsv"
COUNTER = R / "gdt310_counterexamples.tsv"
REPORT = R / "GDT310_SOURCE_SIDE_OPERATION_LICENSE_REPORT.md"
RESULT = R / "gdt310_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, rows[0].keys(), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def matrix(rows, names):
    values = np.array([[float(row[name]) for name in names] for row in rows])
    mean = values.mean(0)
    sd = values.std(0)
    sd[sd == 0] = 1
    return np.column_stack([np.ones(len(rows)), (values - mean) / sd])


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


def average_precision(prediction, labels):
    order = sorted(range(len(labels)), key=lambda index: (-prediction[index], index))
    hits = 0
    total = 0.0
    for rank, index in enumerate(order, 1):
        if labels[index] == 1:
            hits += 1
            total += hits / rank
    return total / hits


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


def main():
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    assert stored == canonical_hash(design)
    assert design["status"] == "FROZEN_BEFORE_TARGET_BLIND_LICENSE_SCORING"
    all_rows = read(FEATURES)
    model_names = list(design["models"])
    operation_data = {}
    observed = {}
    predictions = []
    scores = []
    null_values = {}

    for operation in design["operations"]:
        rows = [row for row in all_rows if row["operation"] == operation]
        labels = np.array([int(row["licensed"]) for row in rows], float)
        bins = quartiles(rows)
        matrices = {
            model: hat(matrix(rows, design["models"][model]), design["ridge"])
            for model in model_names
        }
        predicted = {
            model: loo(matrices[model], labels, design["prediction_clip"])
            for model in model_names
        }
        base = brier(predicted["FREQUENCY"], labels)
        operation_data[operation] = (rows, labels, bins, matrices)
        for model in model_names:
            gain = base - brier(predicted[model], labels)
            observed[(operation, model)] = gain
            scores.append(
                {
                    "operation": operation,
                    "model": model,
                    "hosts": len(rows),
                    "licensed_hosts": int(labels.sum()),
                    "brier": f"{brier(predicted[model], labels):.12f}",
                    "brier_gain_vs_frequency": f"{gain:.12f}",
                    "roc_auc": f"{auc(predicted[model], labels):.12f}",
                    "average_precision": f"{average_precision(predicted[model], labels):.12f}",
                    "null_mean_gain": "NA" if model == "FREQUENCY" else "",
                    "null_sd_gain": "NA" if model == "FREQUENCY" else "",
                    "standardized_gain": "NA" if model == "FREQUENCY" else "",
                    "local_p": "NA" if model == "FREQUENCY" else "",
                    "max12_p": "NA" if model == "FREQUENCY" else "",
                }
            )
            for index, row in enumerate(rows):
                predictions.append(
                    {
                        "operation": operation,
                        "host_id_sha256": row["host_id_sha256"],
                        "licensed": int(labels[index]),
                        "model": model,
                        "loo_probability": f"{predicted[model][index]:.12f}",
                        "source_event_count_quartile": int(bins[index]),
                    }
                )
            if model != "FREQUENCY":
                null_values[(operation, model)] = []

    for world in range(design["null_worlds"]):
        for operation, (_, labels, bins, matrices) in operation_data.items():
            shuffled = permute(labels, bins, design["null_seed"], world, operation)
            base = brier(loo(matrices["FREQUENCY"], shuffled, design["prediction_clip"]), shuffled)
            for model in model_names:
                if model != "FREQUENCY":
                    value = base - brier(
                        loo(matrices[model], shuffled, design["prediction_clip"]), shuffled
                    )
                    null_values[(operation, model)].append(value)

    means = {key: statistics.mean(values) for key, values in null_values.items()}
    sds = {key: statistics.pstdev(values) for key, values in null_values.items()}
    zscores = {
        key: (observed[key] - means[key]) / sds[key] if sds[key] else 0.0
        for key in null_values
    }
    max_z = [
        max(
            (null_values[key][world] - means[key]) / sds[key] if sds[key] else 0.0
            for key in null_values
        )
        for world in range(design["null_worlds"])
    ]
    score_map = {(row["operation"], row["model"]): row for row in scores}
    for key, values in null_values.items():
        local_p = (1 + sum(value >= observed[key] - 1e-15 for value in values)) / (
            1 + design["null_worlds"]
        )
        max_p = (1 + sum(value >= zscores[key] - 1e-15 for value in max_z)) / (
            1 + design["null_worlds"]
        )
        score_map[key].update(
            {
                "null_mean_gain": f"{means[key]:.12f}",
                "null_sd_gain": f"{sds[key]:.12f}",
                "standardized_gain": f"{zscores[key]:.12f}",
                "local_p": f"{local_p:.12f}",
                "max12_p": f"{max_p:.12f}",
            }
        )

    classes = {}
    for operation in design["operations"]:
        row = score_map[(operation, "FULL")]
        passes = (
            float(row["brier_gain_vs_frequency"]) > 0
            and float(row["roc_auc"]) >= design["decision"]["full_auc_minimum"]
            and float(row["max12_p"]) <= design["decision"]["full_max12_p_le"]
        )
        classes[operation] = (
            "TARGET_BLIND_LICENSE_PREDICTABLE"
            if passes
            else "TARGET_BLIND_LICENSE_OPAQUE_OR_UNRESOLVED"
        )
    status = (
        "SOURCE_SIDE_LICENSE_PARTLY_PREDICTABLE"
        if "TARGET_BLIND_LICENSE_PREDICTABLE" in classes.values()
        else "SOURCE_SIDE_LICENSE_NOT_PREDICTABLE"
    )

    counterexamples = [
        {
            "counterexample_id": "C01",
            "finding": "The source-side threshold leaves only 7 positive ch-to-s hosts and 8 positive d-to-s hosts.",
            "impact": "Rare-class AUC, AP and null tails remain high variance.",
        },
        {
            "counterexample_id": "C02",
            "finding": "GDT303 selected the three operation labels before this model family was frozen.",
            "impact": "This is target-blind feature construction, not independent operation discovery.",
        },
        {
            "counterexample_id": "C03",
            "finding": "Only source-wrapper occurrences contribute to predictors; target q/s occurrences contribute only the binary outcome.",
            "impact": "A positive result predicts license from pre-target ecology, unlike GDT309.",
        },
        {
            "counterexample_id": "C04",
            "finding": "Host identity, glyphs, substrings, exact surfaces and all wrapper-count columns are forbidden.",
            "impact": "A failure does not refute compatibility encoded only in those coordinates.",
        },
        {
            "counterexample_id": "C05",
            "finding": "The fixed model is linear ridge-10 with only 16 to 52 hosts per operation.",
            "impact": "Interaction-heavy licensing remains untested.",
        },
        {
            "counterexample_id": "C06",
            "finding": "No f84 row occurs in the source-side feature freeze.",
            "impact": "The sealed holdout remains untouched.",
        },
    ]
    write(PRED, predictions)
    write(SCORES, scores)
    write(NULL, [{"world_index": i, "max12_standardized_brier_gain": f"{v:.12f}"} for i, v in enumerate(max_z)])
    write(COUNTER, counterexamples)

    report = [
        "# GDT310 — source-side-only operation-license prediction",
        "",
        f"Status: **{status}**.",
        "",
        "Predictors are computed only from the source wrapper of each operation. Target q/s events supply the binary license label but no predictor values.",
        "",
        "| operation | hosts (+) | FULL gain | AUC | AP | max-12 p | class |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for operation in design["operations"]:
        row = score_map[(operation, "FULL")]
        report.append(
            f"| `{operation}` | {row['hosts']} ({row['licensed_hosts']}) | "
            f"{float(row['brier_gain_vs_frequency']):+.4f} | {float(row['roc_auc']):.3f} | "
            f"{float(row['average_precision']):.3f} | {row['max12_p']} | {classes[operation]} |"
        )
    report += [
        "",
        "## Fixed ablations",
        "",
        "| operation | layout gain | compiler gain | register gain | full gain |",
        "|---|---:|---:|---:|---:|",
    ]
    for operation in design["operations"]:
        values = [float(score_map[(operation, model)]["brier_gain_vs_frequency"]) for model in ("LAYOUT", "COMPILER", "REGISTER", "FULL")]
        report.append("| `{}` | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} |".format(operation, *values))
    report += [
        "",
        "## Interpretation",
        "",
    ]
    if status == "SOURCE_SIDE_LICENSE_PARTLY_PREDICTABLE":
        winners = [operation for operation, value in classes.items() if value == "TARGET_BLIND_LICENSE_PREDICTABLE"]
        report.append(
            "The frozen rule passes for " + ", ".join(f"`{value}`" for value in winners) + ". This is evidence that availability of those target alternants is partly predictable from the source form's independently observed layout/compiler/register ecology. It is not evidence for a linguistic affix or meaning."
        )
    else:
        report.append(
            "None of the operations passes the frozen target-blind rule. GDT309's observed-ecology classification therefore does not survive removal of target-wrapper events; the compatibility lists remain opaque under this low-capacity instrument."
        )
    report += [
        "",
        "## Claim ceiling",
        "",
        design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored.",
    ]
    REPORT.write_text("\n".join(report) + "\n")

    output_files = [PRED, SCORES, NULL, COUNTER, REPORT]
    input_files = [
        FEATURES,
        R / "gdt310_capacity.tsv",
        R / "gdt310_design_validation.json",
        R / "gdt303_result.json",
        R / "gdt307_result.json",
        R / "gdt308_result.json",
        R / "gdt309_result.json",
    ]
    result = {
        "schema": "GDT310_SOURCE_SIDE_OPERATION_LICENSE_RESULT_V1",
        "status": status,
        "classifications": classes,
        "summary": {
            "operation_host_rows": len(all_rows),
            "predictable_licenses": sum(value == "TARGET_BLIND_LICENSE_PREDICTABLE" for value in classes.values()),
        },
        "provenance": "POST_SELECTION_TARGET_BLIND_SOURCE_WRAPPER_ECOLOGY_TEST",
        "semantic_assignments": 0,
        "claim_ceiling": design["claim_ceiling"],
        "f84": {"input_files": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in input_files},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in output_files},
    }
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "classes": classes, "full": {operation: score_map[(operation, "FULL")] for operation in design["operations"]}}, sort_keys=True))


if __name__ == "__main__":
    main()
