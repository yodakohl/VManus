#!/usr/bin/env python3
"""Score held-folio source/target event choice for frozen operations."""
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PAIRS = R / "gdt303_pair_deltas.tsv"
PANEL = R / "gdt311_frozen_event_panel.tsv"
DESIGN = R / "gdt311_design.json"
METHOD = R / "GDT311_OPERATION_EVENT_CHOICE_METHOD.md"
PREDICTIONS = R / "gdt311_event_predictions.tsv"
SCORES = R / "gdt311_model_scores.tsv"
NULL = R / "gdt311_null_max.tsv"
COUNTER = R / "gdt311_counterexamples.tsv"
REPORT = R / "GDT311_OPERATION_EVENT_CHOICE_REPORT.md"
RESULT = R / "gdt311_result.json"


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


def pair_id(operation, source_hash, target_hash):
    text = f"{operation}|{source_hash}|{target_hash}"
    return hashlib.sha256(text.encode()).hexdigest()[:20]


def recover_labels(operations):
    lookup = {}
    for row in read(PAIRS):
        if row["operation"] not in operations:
            continue
        identifier = pair_id(row["operation"], row["source_surface_sha256"], row["target_surface_sha256"])
        lookup[(row["operation"], row["source_surface_sha256"])] = (identifier, 0)
        lookup[(row["operation"], row["target_surface_sha256"])] = (identifier, 1)
    labels = {}
    for event in read(SOURCE):
        if event["control_id"] != "VOYNICH_REFERENCE":
            continue
        assert not event["page"].startswith("f84") and not event["locus"].startswith("f84")
        for operation in operations:
            key = (operation, event["source_surface_sha256"])
            if key in lookup:
                identifier, role = lookup[key]
                anonymous = hashlib.sha256(f"{operation}|{event['observation_id']}".encode()).hexdigest()[:20]
                labels[anonymous] = (identifier, role)
    return labels


def design_matrix(training, test, pair_values, feature_names, categorical):
    pair_columns = sorted(pair_values)
    categories = {name: sorted({row[name] for row in training}) for name in feature_names if name in categorical}
    numeric = [name for name in feature_names if name not in categorical]
    mean = {name: statistics.mean(float(row[name]) for row in training) for name in numeric}
    sd = {
        name: statistics.pstdev(float(row[name]) for row in training) or 1.0
        for name in numeric
    }

    def encode(rows):
        result = []
        for row in rows:
            values = [1.0]
            values.extend(float(row["pair_id"] == value) for value in pair_columns)
            values.extend((float(row[name]) - mean[name]) / sd[name] for name in numeric)
            for name in feature_names:
                if name in categorical:
                    values.extend(float(row[name] == value) for value in categories[name])
            result.append(values)
        return np.array(result, float)

    return encode(training), encode(test)


def ridge_logistic(training_x, training_y, test_x, ridge, clip):
    beta = np.zeros(training_x.shape[1])
    penalty = np.eye(training_x.shape[1]) * ridge
    penalty[0, 0] = 0.0
    for _ in range(100):
        eta = np.clip(training_x @ beta, -30, 30)
        probability = 1.0 / (1.0 + np.exp(-eta))
        weights = np.maximum(probability * (1 - probability), 1e-8)
        gradient = training_x.T @ (training_y - probability) - penalty @ beta
        hessian = training_x.T @ (training_x * weights[:, None]) + penalty
        step = np.linalg.pinv(hessian) @ gradient
        beta += step
        if np.max(np.abs(step)) < 1e-10:
            break
    result = 1.0 / (1.0 + np.exp(-np.clip(test_x @ beta, -30, 30)))
    return np.clip(result, clip[0], clip[1])


def logloss_bits(prediction, labels):
    return float(-np.mean(labels * np.log2(prediction) + (1 - labels) * np.log2(1 - prediction)))


def brier(prediction, labels):
    return float(np.mean((prediction - labels) ** 2))


def auc(prediction, labels):
    positive = prediction[labels == 1]
    negative = prediction[labels == 0]
    return float(sum((a > b) + 0.5 * (a == b) for a in positive for b in negative) / (len(positive) * len(negative)))


def average_precision(prediction, labels):
    order = sorted(range(len(labels)), key=lambda index: (-prediction[index], index))
    hits = 0
    value = 0.0
    for rank, index in enumerate(order, 1):
        if labels[index] == 1:
            hits += 1
            value += hits / rank
    return value / hits


def permute(labels, strata, seed, world, suffix):
    result = labels.copy()
    grouped = defaultdict(list)
    for index, stratum in enumerate(strata):
        grouped[stratum].append(index)
    for stratum, indices in sorted(grouped.items()):
        values = labels[indices].copy()
        text = f"{seed}|{world}|{suffix}|{'|'.join(stratum)}"
        rng = np.random.default_rng(int(hashlib.sha256(text.encode()).hexdigest()[:16], 16))
        rng.shuffle(values)
        result[indices] = values
    return result


def main():
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    assert stored == canonical_hash(design)
    assert design["status"] == "FROZEN_BEFORE_HELD_EVENT_CHOICE_SCORING"
    panel = read(PANEL)
    recovered = recover_labels(design["operations"])
    for row in panel:
        assert row["anonymous_event_id"] in recovered
        assert recovered[row["anonymous_event_id"]][0] == row["pair_id"]

    operation_data = {}
    prediction_rows = []
    score_rows = []
    observed = {}
    null_primary = {}
    null_pair = {}
    for operation in design["operations"]:
        rows = [row for row in panel if row["operation"] == operation]
        training = [row for row in rows if row["split"] == "TRAIN"]
        test = [row for row in rows if row["split"] == "TEST"]
        training_y = np.array([recovered[row["anonymous_event_id"]][1] for row in training], float)
        test_y = np.array([recovered[row["anonymous_event_id"]][1] for row in test], float)
        pairs = {row["pair_id"] for row in rows}
        predicted = {}
        for model, features in design["models"].items():
            train_x, test_x = design_matrix(training, test, pairs, features, design["categorical_features"])
            predicted[model] = ridge_logistic(train_x, training_y, test_x, design["ridge"], design["probability_clip"])
        baseline_loss = logloss_bits(predicted["PAIR"], test_y)
        operation_data[operation] = (test, test_y, predicted)
        for model in design["models"]:
            gain = baseline_loss - logloss_bits(predicted[model], test_y)
            observed[(operation, model)] = gain
            score_rows.append(
                {
                    "operation": operation,
                    "model": model,
                    "test_events": len(test),
                    "target_events": int(test_y.sum()),
                    "held_bits_per_event": f"{logloss_bits(predicted[model], test_y):.12f}",
                    "gain_vs_pair_bits_per_event": f"{gain:.12f}",
                    "brier": f"{brier(predicted[model], test_y):.12f}",
                    "roc_auc": f"{auc(predicted[model], test_y):.12f}",
                    "average_precision": f"{average_precision(predicted[model], test_y):.12f}",
                    "null_mean_gain": "NA" if model == "PAIR" else "",
                    "null_centered_gain": "NA" if model == "PAIR" else "",
                    "standardized_gain": "NA" if model == "PAIR" else "",
                    "local_p": "NA" if model == "PAIR" else "",
                    "max12_p": "NA" if model == "PAIR" else "",
                    "pair_only_sensitivity_p": "NA" if model == "PAIR" else "",
                }
            )
            for index, row in enumerate(test):
                prediction_rows.append(
                    {
                        "anonymous_event_id": row["anonymous_event_id"],
                        "operation": operation,
                        "pair_id": row["pair_id"],
                        "physical_folio": row["physical_folio"],
                        "register": row["register"],
                        "observed_target_role": int(test_y[index]),
                        "model": model,
                        "held_probability": f"{predicted[model][index]:.12f}",
                    }
                )
            if model != "PAIR":
                null_primary[(operation, model)] = []
                null_pair[(operation, model)] = []

    worlds = design["null"]["worlds"]
    seed = design["null"]["seed"]
    for world in range(worlds):
        for operation, (test, test_y, predicted) in operation_data.items():
            strata_primary = [(row["pair_id"], row["register"]) for row in test]
            strata_pair = [(row["pair_id"],) for row in test]
            shuffled_primary = permute(test_y, strata_primary, seed, world, operation + "|PRIMARY")
            shuffled_pair = permute(test_y, strata_pair, seed, world, operation + "|PAIR")
            for labels, store in ((shuffled_primary, null_primary), (shuffled_pair, null_pair)):
                base = logloss_bits(predicted["PAIR"], labels)
                for model in design["models"]:
                    if model != "PAIR":
                        store[(operation, model)].append(base - logloss_bits(predicted[model], labels))

    means = {key: statistics.mean(values) for key, values in null_primary.items()}
    sds = {key: statistics.pstdev(values) for key, values in null_primary.items()}
    zscores = {key: (observed[key] - means[key]) / sds[key] if sds[key] else 0.0 for key in null_primary}
    max_z = [
        max((null_primary[key][world] - means[key]) / sds[key] if sds[key] else 0.0 for key in null_primary)
        for world in range(worlds)
    ]
    score_map = {(row["operation"], row["model"]): row for row in score_rows}
    for key, values in null_primary.items():
        local_p = (1 + sum(value >= observed[key] - 1e-15 for value in values)) / (1 + worlds)
        max_p = (1 + sum(value >= zscores[key] - 1e-15 for value in max_z)) / (1 + worlds)
        sensitivity_p = (1 + sum(value >= observed[key] - 1e-15 for value in null_pair[key])) / (1 + worlds)
        score_map[key].update(
            {
                "null_mean_gain": f"{means[key]:.12f}",
                "null_centered_gain": f"{observed[key] - means[key]:.12f}",
                "standardized_gain": f"{zscores[key]:.12f}",
                "local_p": f"{local_p:.12f}",
                "max12_p": f"{max_p:.12f}",
                "pair_only_sensitivity_p": f"{sensitivity_p:.12f}",
            }
        )

    classes = {}
    for operation in design["operations"]:
        row = score_map[(operation, "PAIR_FULL")]
        passes = (
            float(row["gain_vs_pair_bits_per_event"]) > 0
            and float(row["null_centered_gain"]) > 0
            and float(row["roc_auc"]) >= design["decision"]["auc_minimum"]
            and float(row["max12_p"]) <= design["decision"]["max12_p_le"]
        )
        classes[operation] = "HELD_EVENT_CHOICE_TRANSFER" if passes else "EVENT_CHOICE_WEAK_OR_UNRESOLVED"
    passed = sum(value == "HELD_EVENT_CHOICE_TRANSFER" for value in classes.values())
    if passed == len(classes):
        status = "OPERATION_EVENT_CHOICE_TRANSFERS_ON_LICENSED_PAIRS"
    elif passed:
        status = "OPERATION_EVENT_CHOICE_PARTLY_TRANSFERS"
    else:
        status = "OPERATION_EVENT_CHOICE_NOT_TRANSFERRED"

    counterexamples = [
        {"counterexample_id": "C01", "finding": "The three operations and their exact pairs were selected in GDT303 on the same manuscript.", "impact": "Held folios are deterministic and untouched by model fitting, but this is post-selection validation rather than independent discovery."},
        {"counterexample_id": "C02", "finding": "The primary null preserves pair-by-register target totals.", "impact": "Its tail tests position/boundary alignment after register mixture, not the register main effect itself."},
        {"counterexample_id": "C03", "finding": "DY-derived field first/last remains a parser-native coordinate.", "impact": "PAIR_BOUNDARY and physical line coordinates show whether a lead survives without that field coordinate."},
        {"counterexample_id": "C04", "finding": "An exact-pair intercept gives the candidate every known source/target compatibility relation.", "impact": "A positive result concerns occurrence choice only and cannot predict a new host license."},
        {"counterexample_id": "C05", "finding": "All same-group renderer coordinates and host glyph features are forbidden.", "impact": "Failure leaves same-group spelling constraints untested."},
        {"counterexample_id": "C06", "finding": "No f84 event occurs in the frozen source or panel.", "impact": "The sealed holdout remains untouched."},
    ]
    write(PREDICTIONS, prediction_rows)
    write(SCORES, score_rows)
    write(NULL, [{"world_index": index, "max12_standardized_gain": f"{value:.12f}"} for index, value in enumerate(max_z)])
    write(COUNTER, counterexamples)

    report = [
        "# GDT311 — held-folio operation event choice",
        "",
        f"Status: **{status}**.",
        "",
        "The exact pair license is supplied to every model. The score asks only whether training-folio external context improves source-versus-target choice on deterministic unseen folios.",
        "",
        "| operation | test events (+) | FULL gain bits/event | null-centered | AUC | max-12 p | class |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for operation in design["operations"]:
        row = score_map[(operation, "PAIR_FULL")]
        report.append(f"| `{operation}` | {row['test_events']} ({row['target_events']}) | {float(row['gain_vs_pair_bits_per_event']):+.5f} | {float(row['null_centered_gain']):+.5f} | {float(row['roc_auc']):.3f} | {row['max12_p']} | {classes[operation]} |")
    report += ["", "## Frozen component models", "", "| operation | position | prior-DY boundary | register | full |", "|---|---:|---:|---:|---:|"]
    for operation in design["operations"]:
        values = [float(score_map[(operation, model)]["gain_vs_pair_bits_per_event"]) for model in ("PAIR_POSITION", "PAIR_BOUNDARY", "PAIR_REGISTER", "PAIR_FULL")]
        report.append("| `{}` | {:+.5f} | {:+.5f} | {:+.5f} | {:+.5f} |".format(operation, *values))
    report += ["", "## Interpretation", ""]
    if passed:
        winners = [operation for operation, value in classes.items() if value == "HELD_EVENT_CHOICE_TRANSFER"]
        report.append("External context improves held source/target choice for " + ", ".join(f"`{value}`" for value in winners) + ". This supplies a low-capacity stochastic choice rule after an exact pair is licensed, not a productive unseen-host grammar.")
    else:
        report.append("No operation passes the held event-choice rule. The transferred positional deltas remain descriptive pair-level tendencies, but they do not provide enough calibrated probability gain over exact-pair rates on the deterministic unseen folios.")
    report += ["", "## Claim ceiling", "", design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored."]
    REPORT.write_text("\n".join(report) + "\n")

    outputs = [PREDICTIONS, SCORES, NULL, COUNTER, REPORT]
    inputs = [PANEL, R / "gdt311_capacity.tsv", R / "gdt311_design_validation.json", SOURCE, PAIRS, R / "gdt303_result.json", R / "gdt306_result.json", R / "gdt307_result.json", R / "gdt310_result.json"]
    result = {
        "schema": "GDT311_OPERATION_EVENT_CHOICE_RESULT_V1",
        "status": status,
        "classifications": classes,
        "summary": {"test_events": sum(int(score_map[(operation, "PAIR")]["test_events"]) for operation in design["operations"]), "transferred_operations": passed},
        "provenance": "POST_SELECTION_DETERMINISTIC_HELD_FOLIO_EVENT_CHOICE_TEST",
        "semantic_assignments": 0,
        "claim_ceiling": design["claim_ceiling"],
        "f84": {"input_rows": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in inputs},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in outputs},
    }
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "classes": classes, "full": {operation: score_map[(operation, "PAIR_FULL")] for operation in design["operations"]}}, sort_keys=True))


if __name__ == "__main__":
    main()
