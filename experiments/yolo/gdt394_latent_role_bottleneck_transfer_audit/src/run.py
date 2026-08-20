#!/usr/bin/env python3
"""Run frozen comparator-only GDT394 scalar-bottleneck audit."""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt394_latent_role_bottleneck_transfer_audit"
ART = BASE / "artifacts"
OBS = ROOT / "experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz"
C385 = ROOT / "experiments/yolo/gdt385_corema_parent_link_consequence/artifacts/gdt385_predictions.tsv.gz"
O387 = ROOT / "experiments/yolo/gdt387_cross_domain_parent_link_calibration/artifacts/gdt387_hidden_governor_oracle.tsv.gz"
P387 = ROOT / "experiments/yolo/gdt387_cross_domain_parent_link_calibration/artifacts/gdt387_predictions.tsv.gz"
FREEZE = ART / "gdt394_pre_score_freeze.json"

MODELS = [
    "ROLE_BOTTLENECK",
    "LINEAR_ROLE_1D",
    "SUPERVISED_RELATION_1D",
    "PCA_SOURCE_1D",
    "RANDOM_SOURCE_1D",
    "GRAMMAR_SUMMARY_1D",
    "EXACT_JOINT_ROLE_1D",
    "SHUFFLED_ROLE_1D",
]
HASH_BINS = 64
RIDGE = 10.0
QBINS = 8
ALPHA = 8.0
NULL_WORLDS = 512


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode()).digest()[:8], "big")


def logit(value: np.ndarray | float) -> np.ndarray:
    array = np.clip(np.asarray(value, float), 1e-7, 1 - 1e-7)
    return np.log(array / (1 - array))


def readgz(path: Path) -> list[dict[str, str]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    fields = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def writegz(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    fields = fields or list(rows[0])
    raw = path.open("wb")
    stream = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
    text = io.TextIOWrapper(stream, encoding="utf-8", newline="")
    with text:
        writer = csv.DictWriter(text, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def binint(value: str | int, cuts: tuple[int, ...]) -> int:
    number = int(value)
    for index, cut in enumerate(cuts):
        if number <= cut:
            return index
    return len(cuts)


def signed_hash(token: str) -> tuple[int, float]:
    digest = hashlib.sha256(token.encode()).digest()
    return int.from_bytes(digest[:4], "big") % HASH_BINS, 1.0 if digest[4] & 1 else -1.0


def source_matrices(rows: list[dict[str, str]]) -> tuple[np.ndarray, np.ndarray]:
    numeric = np.zeros((len(rows), 7), float)
    matrix = np.zeros((len(rows), HASH_BINS + numeric.shape[1]), float)
    summary = np.zeros((len(rows), 15), float)
    for i, row in enumerate(rows):
        categorical = [
            "H=" + row["host_id"],
            "G=" + row["rendered_group"],
            "W=" + row["wrapper_state"],
            "P=" + row["positional_state"],
            "B=" + row["boundary_state"],
            "R=" + row["record_state"],
            "V=" + row["renderer_variant"],
            "J=" + row["composite_joint_id"],
            "PREV=" + row["previous_host"],
            "EQ=" + row["source_token_equality"],
            "WP=" + row["wrapper_state"] + "|" + row["positional_state"],
            "PB=" + row["positional_state"] + "|" + row["boundary_state"],
            "WR=" + row["wrapper_state"] + "|" + row["renderer_variant"],
            "HB=" + row["host_id"] + "|" + row["boundary_state"],
        ]
        for token in categorical:
            index, sign = signed_hash(token)
            matrix[i, index] += sign
        numeric[i] = [
            float(row["relative_position"]),
            math.log1p(int(row["record_element_count"])),
            math.log1p(int(row["field_index"])),
            math.log1p(int(row["within_field_index"])),
            math.log1p(int(row["within_record_frequency"])),
            math.log1p(int(row["surface_length"])),
            1.0 if row["previous_host"] == "RECORD_START" else 0.0,
        ]
        matrix[i, HASH_BINS:] = numeric[i]
        summary[i, :7] = numeric[i]
        for token in (
            "P=" + row["positional_state"],
            "B=" + row["boundary_state"],
            "R=" + row["record_state"],
        ):
            index, sign = signed_hash("SUMMARY|" + token)
            summary[i, 7 + index % 8] += sign
    return matrix, summary


def standardize(train: np.ndarray, test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train.mean(axis=0)
    scale = train.std(axis=0)
    scale[scale < 1e-8] = 1.0
    return (train - mean) / scale, (test - mean) / scale


def ridge_direction(matrix: np.ndarray, target: np.ndarray) -> np.ndarray:
    centered = target - target.mean()
    return np.linalg.solve(matrix.T @ matrix + RIDGE * np.eye(matrix.shape[1]), matrix.T @ centered)


def first_pc(matrix: np.ndarray) -> np.ndarray:
    covariance = matrix.T @ matrix / max(1, len(matrix))
    values, vectors = np.linalg.eigh(covariance)
    vector = vectors[:, int(np.argmax(values))]
    nonzero = np.flatnonzero(np.abs(vector) > 1e-12)
    if len(nonzero) and vector[nonzero[0]] < 0:
        vector = -vector
    return vector


def opportunity(row: dict[str, str]) -> tuple[object, ...]:
    return (
        row["positional_state"],
        row["boundary_state"],
        binint(row["field_index"], (0, 1, 2, 4, 8)),
        binint(row["within_field_index"], (0, 1, 2, 4, 8)),
        binint(row["record_element_count"], (8, 16, 32, 64)),
        binint(row["within_record_frequency"], (1, 2, 4)),
    )


def crossfit_coordinates(
    domain: str,
    rows: list[dict[str, str]],
    role: np.ndarray,
    relation: np.ndarray,
    folds: np.ndarray,
    retained_role_probability: np.ndarray,
) -> dict[str, np.ndarray]:
    matrix, summary = source_matrices(rows)
    scores = {name: np.zeros(len(rows), float) for name in MODELS}
    scores["ROLE_BOTTLENECK"] = logit(retained_role_probability)
    random_generator = np.random.default_rng(seed("GDT394_FIXED_RANDOM_PROJECTION_V1"))
    random_vector = random_generator.normal(size=matrix.shape[1])
    random_vector /= np.linalg.norm(random_vector)

    for held in sorted(set(folds)):
        train = np.flatnonzero(folds != held)
        test = np.flatnonzero(folds == held)
        x_train, x_test = standardize(matrix[train], matrix[test])
        s_train, s_test = standardize(summary[train], summary[test])

        direction = ridge_direction(x_train, role[train])
        scores["LINEAR_ROLE_1D"][test] = x_test @ direction

        classes = int(relation.max()) + 1
        onehot = np.eye(classes)[relation[train]]
        onehot -= onehot.mean(axis=0)
        relation_axis = first_pc(onehot)
        relation_target = onehot @ relation_axis
        direction = ridge_direction(x_train, relation_target)
        scores["SUPERVISED_RELATION_1D"][test] = x_test @ direction

        scores["PCA_SOURCE_1D"][test] = x_test @ first_pc(x_train)
        scores["RANDOM_SOURCE_1D"][test] = x_test @ random_vector
        scores["GRAMMAR_SUMMARY_1D"][test] = s_test @ first_pc(s_train)

        counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for index in train:
            counts[rows[index]["composite_joint_id"]][int(role[index])] += 1
        probabilities = np.array(
            [
                (counts[rows[index]["composite_joint_id"]][1] + 1)
                / (sum(counts[rows[index]["composite_joint_id"]]) + 2)
                for index in test
            ]
        )
        scores["EXACT_JOINT_ROLE_1D"][test] = logit(probabilities)

        shuffled = role[train].copy()
        groups: dict[tuple[object, ...], list[int]] = defaultdict(list)
        for local, index in enumerate(train):
            groups[opportunity(rows[index])].append(local)
        generator = np.random.default_rng(seed(f"GDT394_SHUFFLED_ROLE|{domain}|{held}"))
        for members in groups.values():
            values = shuffled[members].copy()
            generator.shuffle(values)
            shuffled[members] = values
        direction = ridge_direction(x_train, shuffled)
        scores["SHUFFLED_ROLE_1D"][test] = x_test @ direction
    return scores


def quantile_edges(values: np.ndarray) -> np.ndarray:
    return np.unique(np.quantile(values, np.arange(1, QBINS) / QBINS))


def rank_metrics(probabilities: np.ndarray, truth: np.ndarray) -> tuple[int, float, np.ndarray]:
    true = probabilities[np.arange(len(truth)), truth]
    greater = (probabilities > true[:, None]).sum(axis=1)
    equal = (np.abs(probabilities - true[:, None]) <= 1e-15).sum(axis=1)
    ranks = 1.0 + greater + (equal - 1) / 2
    top1 = int(np.sum(np.argmax(probabilities, axis=1) == truth))
    return top1, float(np.mean(1.0 / ranks)), ranks


def evaluate(
    values: np.ndarray,
    relation: np.ndarray,
    folds: np.ndarray,
) -> dict[str, object]:
    classes = int(relation.max()) + 1
    baseline_true = np.zeros(len(relation), float)
    model_true = np.zeros(len(relation), float)
    model_probabilities = np.zeros((len(relation), classes), float)
    baseline_probabilities = np.zeros((len(relation), classes), float)
    fold_rows: list[dict[str, object]] = []
    for held in sorted(set(folds)):
        train = np.flatnonzero(folds != held)
        test = np.flatnonzero(folds == held)
        edges = quantile_edges(values[train])
        train_bin = np.digitize(values[train], edges)
        test_bin = np.digitize(values[test], edges)
        global_counts = np.bincount(relation[train], minlength=classes).astype(float)
        prior = (global_counts + 1) / (len(train) + classes)
        table = np.zeros((len(edges) + 1, classes), float)
        totals = np.zeros(len(edges) + 1, float)
        for bucket in range(len(edges) + 1):
            members = train[train_bin == bucket]
            counts = np.bincount(relation[members], minlength=classes).astype(float)
            table[bucket] = counts + ALPHA * prior
            totals[bucket] = len(members) + ALPHA
        probabilities = table[test_bin] / totals[test_bin, None]
        model_probabilities[test] = probabilities
        baseline_probabilities[test] = prior
        model_true[test] = probabilities[np.arange(len(test)), relation[test]]
        baseline_true[test] = prior[relation[test]]
        model_bits = float(-np.log2(np.clip(model_true[test], 1e-15, 1)).sum())
        baseline_bits = float(-np.log2(np.clip(baseline_true[test], 1e-15, 1)).sum())
        top1, mrr, _ = rank_metrics(probabilities, relation[test])
        base_top1, base_mrr, _ = rank_metrics(
            np.repeat(prior[None, :], len(test), axis=0), relation[test]
        )
        fold_rows.append(
            {
                "held_unit": held,
                "n": len(test),
                "baseline_bits": baseline_bits,
                "model_bits": model_bits,
                "gain_bits": baseline_bits - model_bits,
                "baseline_top1": base_top1,
                "model_top1": top1,
                "baseline_mrr": base_mrr,
                "model_mrr": mrr,
            }
        )
    baseline_bits = float(-np.log2(np.clip(baseline_true, 1e-15, 1)).sum())
    model_bits = float(-np.log2(np.clip(model_true, 1e-15, 1)).sum())
    top1, mrr, ranks = rank_metrics(model_probabilities, relation)
    baseline_top1, baseline_mrr, baseline_ranks = rank_metrics(
        baseline_probabilities, relation
    )
    return {
        "baseline_bits": baseline_bits,
        "model_bits": model_bits,
        "gain_bits": baseline_bits - model_bits,
        "positive_folds": sum(float(row["gain_bits"]) > 0 for row in fold_rows),
        "baseline_top1": baseline_top1,
        "model_top1": top1,
        "baseline_mrr": baseline_mrr,
        "model_mrr": mrr,
        "true_probability": model_true,
        "baseline_true_probability": baseline_true,
        "rank": ranks,
        "baseline_rank": baseline_ranks,
        "fold_rows": fold_rows,
    }


def load_domains() -> dict[str, dict[str, object]]:
    observations = [row for row in readgz(OBS) if row["domain"] in {"COREMA", "PCEEC2"}]
    observation_map = {row["element_key"]: row for row in observations}

    corema_predictions = [
        row for row in readgz(C385) if row["route_id"] == "CMP_PARENT_02"
    ]
    corema_rows = [dict(observation_map[row["element_key"]]) for row in corema_predictions]
    for row, prediction in zip(corema_rows, corema_predictions):
        row["role_y"] = prediction["role_y"]
        row["relation_class"] = prediction["relation_class"]
        row["retained_p_role"] = prediction["p_role"]
        row["target_key"] = prediction["target_element_key"]

    pceec_predictions = {row["element_key"]: row for row in readgz(P387)}
    oracle = readgz(O387)
    pceec_rows = [dict(observation_map[row["element_key"]]) for row in oracle]
    for row, hidden in zip(pceec_rows, oracle):
        prediction = pceec_predictions[hidden["element_key"]]
        row["role_y"] = hidden["anonymous_role_y"]
        row["relation_class"] = hidden["distance_class"]
        row["retained_p_role"] = prediction["p_role"]
        row["target_key"] = hidden["governor_key"]
        row["collection_id"] = hidden["source_file"]

    return {
        "COREMA": {"rows": corema_rows, "expected_n": 26169, "expected_folds": 6},
        "PCEEC2": {"rows": pceec_rows, "expected_n": 26493, "expected_folds": 84},
    }


def main() -> int:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert freeze["status"] == "FROZEN_BEFORE_SCORING"
    assert freeze["models"] == MODELS and freeze["null_worlds"] == NULL_WORLDS
    assert freeze["voynich_inputs"] == 0 and not any(freeze["f84"].values())

    domains = load_domains()
    score_rows: list[dict[str, object]] = []
    fold_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    null_summaries: list[dict[str, object]] = []
    counterexamples: list[dict[str, object]] = []
    retained_predictions: list[dict[str, object]] = []
    domain_results: dict[str, dict[str, object]] = {}

    for domain, specification in domains.items():
        rows: list[dict[str, str]] = specification["rows"]  # type: ignore[assignment]
        assert len(rows) == specification["expected_n"]
        folds = np.array([row["collection_id"] for row in rows], object)
        assert len(set(folds)) == specification["expected_folds"]
        role = np.array([int(row["role_y"]) for row in rows], int)
        class_names = sorted({row["relation_class"] for row in rows})
        class_index = {name: index for index, name in enumerate(class_names)}
        relation = np.array([class_index[row["relation_class"]] for row in rows], int)
        retained = np.array([float(row["retained_p_role"]) for row in rows], float)
        coordinates = crossfit_coordinates(domain, rows, role, relation, folds, retained)

        observed: dict[str, dict[str, object]] = {}
        for model in MODELS:
            result = evaluate(coordinates[model], relation, folds)
            observed[model] = result
            largest = max(result["fold_rows"], key=lambda row: int(row["n"]))  # type: ignore[arg-type]
            most_common = Counter(row["source_token_equality"] for row in rows).most_common(1)[0][0]
            keep = np.array([row["source_token_equality"] != most_common for row in rows])
            form_removed_gain = float(
                np.log2(
                    np.clip(result["true_probability"][keep], 1e-15, 1)  # type: ignore[index]
                    / np.clip(result["baseline_true_probability"][keep], 1e-15, 1)  # type: ignore[index]
                ).sum()
            )
            score_rows.append(
                {
                    "domain": domain,
                    "model": model,
                    "dimension": 1,
                    "n": len(rows),
                    "folds": len(set(folds)),
                    "role_rows": int(role.sum()),
                    "baseline_bits": result["baseline_bits"],
                    "model_bits": result["model_bits"],
                    "gain_bits": result["gain_bits"],
                    "positive_folds": result["positive_folds"],
                    "baseline_top1": result["baseline_top1"],
                    "model_top1": result["model_top1"],
                    "baseline_mrr": result["baseline_mrr"],
                    "model_mrr": result["model_mrr"],
                    "largest_fold": largest["held_unit"],
                    "gain_without_largest_fold": float(result["gain_bits"]) - float(largest["gain_bits"]),
                    "most_common_exact_form": most_common,
                    "gain_without_most_common_exact_form": form_removed_gain,
                }
            )
            for fold in result["fold_rows"]:  # type: ignore[union-attr]
                fold_rows.append({"domain": domain, "model": model, **fold})

        groups: dict[tuple[object, ...], list[int]] = defaultdict(list)
        for index, (fold, row) in enumerate(zip(folds, rows)):
            groups[(fold, *opportunity(row))].append(index)
        mobile = np.zeros(len(rows), bool)
        for members in groups.values():
            if len(members) > 1 and len({round(float(coordinates["ROLE_BOTTLENECK"][i]), 12) for i in members}) > 1:
                mobile[members] = True
        generator = np.random.default_rng(seed(f"GDT394_COUPLING_NULL_V1|{domain}"))
        null_gains = {model: [] for model in MODELS}
        for world in range(NULL_WORLDS):
            permutation = np.arange(len(rows))
            for members in groups.values():
                values = permutation[members].copy()
                generator.shuffle(values)
                permutation[members] = values
            gains = {}
            for model in MODELS:
                gain = float(evaluate(coordinates[model][permutation], relation, folds)["gain_bits"])
                null_gains[model].append(gain)
                gains[model] = gain
            null_rows.append(
                {
                    "domain": domain,
                    "world": world,
                    "max8_gain_bits": max(gains.values()),
                    "role_gain_bits": gains["ROLE_BOTTLENECK"],
                }
            )

        domain_score_rows = [row for row in score_rows if row["domain"] == domain]
        for row in domain_score_rows:
            values = np.array(null_gains[str(row["model"])])
            row["null_mean_gain_bits"] = float(values.mean())
            row["null_sd_gain_bits"] = float(values.std())
            row["null_centered_excess_bits"] = float(row["gain_bits"]) - float(values.mean())
            null_summaries.append(
                {
                    "domain": domain,
                    "model": row["model"],
                    "observed_gain_bits": row["gain_bits"],
                    "null_mean_gain_bits": row["null_mean_gain_bits"],
                    "null_sd_gain_bits": row["null_sd_gain_bits"],
                    "null_centered_excess_bits": row["null_centered_excess_bits"],
                }
            )
        role_row = next(row for row in domain_score_rows if row["model"] == "ROLE_BOTTLENECK")
        controls = [row for row in domain_score_rows if row["model"] != "ROLE_BOTTLENECK"]
        max_null = [row for row in null_rows if row["domain"] == domain]
        pvalue = (1 + sum(float(row["max8_gain_bits"]) >= float(role_row["gain_bits"]) for row in max_null)) / (NULL_WORLDS + 1)
        best_control_gain = max(float(row["gain_bits"]) for row in controls)
        best_control_excess = max(float(row["null_centered_excess_bits"]) for row in controls)
        best_control_mrr = max(float(row["model_mrr"]) for row in controls)
        best_control_top1 = max(int(row["model_top1"]) for row in controls)
        top1_margin = max(3, math.ceil(0.001 * len(rows)))
        gates = {
            "positive_gain": float(role_row["gain_bits"]) > 0,
            "beats_every_control_gain": float(role_row["gain_bits"]) > best_control_gain,
            "majority_positive_folds": int(role_row["positive_folds"]) >= (4 if domain == "COREMA" else 43),
            "positive_null_excess": float(role_row["null_centered_excess_bits"]) > 0,
            "beats_every_control_null_excess": float(role_row["null_centered_excess_bits"]) > best_control_excess,
            "max8_p": pvalue <= 0.05,
            "mrr_margin": float(role_row["model_mrr"]) >= best_control_mrr + 0.001,
            "top1_margin": int(role_row["model_top1"]) >= best_control_top1 + top1_margin,
            "not_one_fold": float(role_row["gain_without_largest_fold"]) > 0,
            "not_one_exact_form": float(role_row["gain_without_most_common_exact_form"]) > 0,
        }
        domain_pass = all(gates.values())
        role_result = observed["ROLE_BOTTLENECK"]
        best_control_model = max(controls, key=lambda row: float(row["gain_bits"]))["model"]
        best_result = observed[str(best_control_model)]
        differences = np.log2(
            np.clip(role_result["true_probability"], 1e-15, 1)  # type: ignore[arg-type]
            / np.clip(best_result["true_probability"], 1e-15, 1)  # type: ignore[arg-type]
        )
        for index in np.argsort(differences)[:20]:
            counterexamples.append(
                {
                    "domain": domain,
                    "element_key": rows[index]["element_key"],
                    "held_unit": folds[index],
                    "relation_class": rows[index]["relation_class"],
                    "role_y": int(role[index]),
                    "best_control": best_control_model,
                    "role_minus_control_log2_true_probability": float(differences[index]),
                    "role_rank": float(role_result["rank"][index]),  # type: ignore[index]
                    "control_rank": float(best_result["rank"][index]),  # type: ignore[index]
                }
            )
        for index, row in enumerate(rows):
            retained_predictions.append(
                {
                    "domain": domain,
                    "element_key": row["element_key"],
                    "held_unit": folds[index],
                    "relation_class": row["relation_class"],
                    "role_y": int(role[index]),
                    "best_control": best_control_model,
                    "baseline_true_probability": role_result["baseline_true_probability"][index],  # type: ignore[index]
                    "role_true_probability": role_result["true_probability"][index],  # type: ignore[index]
                    "best_control_true_probability": best_result["true_probability"][index],  # type: ignore[index]
                    "role_rank": role_result["rank"][index],  # type: ignore[index]
                    "best_control_rank": best_result["rank"][index],  # type: ignore[index]
                    "null_mobile": int(mobile[index]),
                }
            )
        domain_results[domain] = {
            "pass": domain_pass,
            "gates": gates,
            "max8_p": pvalue,
            "mobile_rows": int(mobile.sum()),
            "mobile_fraction": float(mobile.mean()),
            "role_gain_bits": role_row["gain_bits"],
            "role_null_centered_excess_bits": role_row["null_centered_excess_bits"],
            "best_control": best_control_model,
            "best_control_gain_bits": best_control_gain,
            "best_control_null_centered_excess_bits": best_control_excess,
            "role_mrr": role_row["model_mrr"],
            "best_control_mrr": best_control_mrr,
            "role_top1": role_row["model_top1"],
            "best_control_top1": best_control_top1,
        }

    overall_pass = all(result["pass"] for result in domain_results.values())
    status = (
        "ANONYMOUS_ROLE_BOTTLENECK_PORTABLE_ABOVE_MATCHED_CONTROLS"
        if overall_pass
        else "LATENT_ROLE_COMPRESSION_NOT_DISTINCT_FROM_MATCHED_SOURCE_BOTTLENECKS"
    )
    score_path = ART / "gdt394_bottleneck_scores.tsv"
    fold_path = ART / "gdt394_fold_scores.tsv"
    null_summary_path = ART / "gdt394_null_summary.tsv"
    null_path = ART / "gdt394_null_worlds.tsv"
    counter_path = ART / "gdt394_counterexamples.tsv"
    prediction_path = ART / "gdt394_predictions.tsv.gz"
    write(score_path, score_rows)
    write(fold_path, fold_rows)
    write(null_summary_path, null_summaries)
    write(null_path, null_rows)
    write(counter_path, counterexamples)
    writegz(prediction_path, retained_predictions)
    outputs = [score_path, fold_path, null_summary_path, null_path, counter_path, prediction_path]
    implementations = [BASE / "src/freeze.py", BASE / "src/validate_freeze.py", BASE / "src/run.py", BASE / "src/validate.py"]
    result = {
        "schema": "GDT394_RESULT_V1",
        "status": status,
        "interpretation_correction": "ROLE_SCORE_IS_DETERMINISTIC_SOURCE_COMPRESSION_NOT_CONDITIONAL_INFORMATION",
        "overall_pass": overall_pass,
        "domain_results": domain_results,
        "models": MODELS,
        "null_worlds": NULL_WORLDS,
        "voynich_rows_read": 0,
        "voynich_stage_authorized": False,
        "semantic_state": "UNASSIGNED",
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [OBS, C385, O387, P387, FREEZE]},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs},
        "implementation": {str(path.relative_to(ROOT)): sha(path) for path in implementations},
        "validation_scope": "RETAINED_FOLD_NULL_AND_PRIMARY_ARITHMETIC",
        "claim_ceiling": "COMPARATOR_ONLY_MATCHED_ONE_DIMENSIONAL_COMPRESSION_AUDIT",
    }
    content = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["content_sha256"] = hashlib.sha256(content).hexdigest()
    (ART / "gdt394_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": status, "domains": domain_results}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
