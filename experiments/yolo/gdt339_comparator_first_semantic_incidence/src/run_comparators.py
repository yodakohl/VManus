#!/usr/bin/env python3
"""Select and freeze GDT339's opaque-ID semantic incidence invariant."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt339_comparator_first_semantic_incidence"
ART = EXP / "artifacts"
METHOD = EXP / "METHOD.md"
DESIGN = ART / "gdt339_comparator_design.json"
COREMA = ROOT / "gdt176_external_role_units.tsv"
COREMA_FREEZE = ROOT / "gdt176_source_freeze.json"
NUREMBERG = ROOT / "gdt155_unblinded_record_truth.tsv"
NUREMBERG_FREEZE = ROOT / "gdt155_unblind_export.json"
FOLDS = ART / "gdt339_comparator_folds.tsv"
MODELS = ART / "gdt339_comparator_models.tsv"
SUMMARY = ART / "gdt339_comparator_units_summary.tsv"
NULL = ART / "gdt339_comparator_null.tsv"
VARIANTS = ART / "gdt339_tried_variants.tsv"
FREEZE = ART / "gdt339_invariant_freeze.json"
RESULT = ART / "gdt339_comparator_result.json"
REPORT = EXP / "COMPARATOR_REPORT.md"
FEATURE_NAMES = (
    "log_occurrence_fraction",
    "record_frequency_fraction",
    "log_mean_within_record_multiplicity",
    "mean_record_degree_scaled",
    "repeated_record_fraction",
    "record_degree_cv",
    "partner_bin_occupancy",
    "partner_bin_entropy",
    "partner_bin_concentration",
    "mean_partner_record_frequency",
    "collection_dispersion",
)
MODEL_FEATURES = {
    "FREQUENCY_DEGREE": (0, 1, 2, 3),
    "TOPOLOGY_ONLY": (4, 5, 6, 7, 8, 9, 10),
    "FULL_INCIDENCE": tuple(range(len(FEATURE_NAMES))),
}
DATASET_CLASSES = {
    "COREMA": ("OPENER", "OPERATION", "INGREDIENT", "TOOL", "CLOSER"),
    "NUREMBERG": ("ADDRESSEE", "CONTENT", "OTHER"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def opaque_token(token: str) -> str:
    value = unicodedata.normalize("NFC", token.lower())
    return hashlib.sha256(("GDT339_OPAQUE_TOKEN_V1\0" + value).encode("utf-8")).hexdigest()[:20]


def tokens(text: str) -> list[str]:
    return re.findall(r"[^\W_]+", unicodedata.normalize("NFC", text.lower()), flags=re.UNICODE)


def load_units() -> dict[str, list[dict[str, str]]]:
    corema = [
        {
            "dataset": "COREMA",
            "collection": row["collection_id"],
            "record": row["recipe_id"],
            "identity": row["identity_hash"],
            "role": row["oracle_role"],
        }
        for row in read_tsv(COREMA)
    ]
    nuremberg: list[dict[str, str]] = []
    for row in read_tsv(NUREMBERG):
        if row["corpus"] != "NUREMBERG":
            continue
        sections = [
            ("ADDRESSEE", row["regularized_addressee"]),
            ("CONTENT", row["regularized_content"]),
        ]
        other_parts = []
        if row["regularized_other_sections"] != "NONE":
            for part in row["regularized_other_sections"].split(" || "):
                other_parts.append(part.split("=", 1)[1] if "=" in part else part)
        sections.append(("OTHER", " ".join(other_parts)))
        for role, text in sections:
            for token in tokens(text):
                nuremberg.append(
                    {
                        "dataset": "NUREMBERG",
                        "collection": row["book_or_ms"],
                        "record": row["record_id"],
                        "identity": opaque_token(token),
                        "role": role,
                    }
                )
    if {unit["role"] for unit in corema} != set(DATASET_CLASSES["COREMA"]):
        raise AssertionError("CoReMA class mismatch")
    if {unit["role"] for unit in nuremberg} != set(DATASET_CLASSES["NUREMBERG"]):
        raise AssertionError("Nuremberg class mismatch")
    return {"COREMA": corema, "NUREMBERG": nuremberg}


def stable_sample(units: list[dict[str, str]], cap: int) -> list[dict[str, str]]:
    buckets: dict[tuple[str, str], list[tuple[str, dict[str, str]]]] = defaultdict(list)
    occurrence = Counter()
    for unit in units:
        key = (unit["collection"], unit["role"], unit["record"], unit["identity"])
        occurrence[key] += 1
        digest = hashlib.sha256(
            "|".join((*key, str(occurrence[key]))).encode("utf-8")
        ).hexdigest()
        buckets[(unit["collection"], unit["role"])].append((digest, unit))
    selected = []
    for key in sorted(buckets):
        selected.extend(unit for _, unit in sorted(buckets[key])[:cap])
    return selected


def graph_features(
    reference: list[dict[str, str]], query: list[dict[str, str]], bins: int
) -> np.ndarray:
    records: dict[str, list[str]] = defaultdict(list)
    id_collections: dict[str, set[str]] = defaultdict(set)
    for unit in reference:
        records[unit["record"]].append(unit["identity"])
        id_collections[unit["identity"]].add(unit["collection"])
    counts = Counter(unit["identity"] for unit in reference)
    docs: dict[str, set[str]] = defaultdict(set)
    repeated_docs = Counter()
    degree_sum = Counter()
    degree_sq_sum = Counter()
    bin_counts: dict[str, Counter[int]] = defaultdict(Counter)
    record_counters = {record: Counter(values) for record, values in records.items()}
    for record, counter in record_counters.items():
        identities = sorted(counter)
        degree = len(identities)
        partner_bins = {
            ident: int(hashlib.sha256(("GDT339_PARTNER_BIN_V1\0" + ident).encode()).hexdigest()[:8], 16) % bins
            for ident in identities
        }
        for ident in identities:
            docs[ident].add(record)
            repeated_docs[ident] += int(counter[ident] > 1)
            degree_sum[ident] += degree
            degree_sq_sum[ident] += degree * degree
            for partner in identities:
                if partner != ident:
                    bin_counts[ident][partner_bins[partner]] += 1
    record_partner_df_sum = {
        record: sum(len(docs[partner]) for partner in counter)
        for record, counter in record_counters.items()
    }
    total = max(1, len(reference))
    n_records = max(1, len(records))
    n_collections = max(1, len({unit["collection"] for unit in reference}))
    max_degree = max((len(counter) for counter in record_counters.values()), default=1)
    vectors = []
    for unit in query:
        ident = unit["identity"]
        count = counts[ident]
        df = len(docs.get(ident, ()))
        mean_mult = count / max(1, df)
        mean_degree = degree_sum[ident] / max(1, df)
        variance = max(0.0, degree_sq_sum[ident] / max(1, df) - mean_degree * mean_degree)
        bc = bin_counts[ident]
        partner_total = sum(bc.values())
        entropy = 0.0
        if partner_total:
            for value in bc.values():
                p = value / partner_total
                entropy -= p * math.log2(p)
        partner_df_weight = sum(
            record_partner_df_sum[record] - df for record in docs.get(ident, ())
        )
        partner_weight = sum(
            max(0, len(record_counters[record]) - 1) for record in docs.get(ident, ())
        )
        vectors.append(
            [
                math.log1p(count) / math.log1p(total),
                df / n_records,
                math.log1p(mean_mult),
                math.log1p(mean_degree) / math.log1p(max_degree),
                repeated_docs[ident] / max(1, df),
                math.sqrt(variance) / max(1.0, mean_degree),
                len(bc) / bins,
                entropy / math.log2(bins),
                (max(bc.values()) / partner_total) if partner_total else 0.0,
                (partner_df_weight / max(1, partner_weight)) / n_records,
                len(id_collections.get(ident, ())) / n_collections,
            ]
        )
    return np.asarray(vectors, dtype=float)


def class_weights(y: np.ndarray, k: int) -> np.ndarray:
    counts = np.bincount(y, minlength=k).astype(float)
    weights = np.array([1.0 / max(1.0, counts[value]) for value in y])
    return weights / weights.mean()


def fit_model(
    X: np.ndarray, y: np.ndarray, indices: tuple[int, ...], classes: int, design: dict
) -> dict[str, object]:
    selected = X[:, indices]
    mean = selected.mean(axis=0)
    scale = selected.std(axis=0)
    scale[scale < 1e-9] = 1.0
    Z = np.column_stack([np.ones(len(selected)), np.clip((selected - mean) / scale, -6, 6)])
    weights = class_weights(y, classes)
    Y = np.eye(classes)[y]
    beta = np.zeros((Z.shape[1], classes))
    m = np.zeros_like(beta)
    v = np.zeros_like(beta)
    cfg = design["optimizer"]
    for step in range(1, int(cfg["steps"]) + 1):
        logits = Z @ beta
        logits -= logits.max(axis=1, keepdims=True)
        p = np.exp(logits)
        p /= p.sum(axis=1, keepdims=True)
        grad = Z.T @ ((p - Y) * weights[:, None]) / weights.sum()
        grad[1:] += float(cfg["ridge"]) * beta[1:]
        m = 0.9 * m + 0.1 * grad
        v = 0.999 * v + 0.001 * grad * grad
        beta -= float(cfg["learning_rate"]) * (m / (1 - 0.9**step)) / (np.sqrt(v / (1 - 0.999**step)) + 1e-8)
    return {"indices": indices, "mean": mean, "scale": scale, "beta": beta}


def predict(X: np.ndarray, model: dict[str, object]) -> np.ndarray:
    selected = X[:, model["indices"]]
    Z = np.column_stack(
        [np.ones(len(selected)), np.clip((selected - model["mean"]) / model["scale"], -6, 6)]
    )
    logits = Z @ model["beta"]
    logits -= logits.max(axis=1, keepdims=True)
    p = np.exp(logits)
    return p / p.sum(axis=1, keepdims=True)


def balanced_metrics(y: np.ndarray, p: np.ndarray, classes: int) -> dict[str, float]:
    per_class_bits = []
    recalls = []
    top = p.argmax(axis=1)
    for value in range(classes):
        mask = y == value
        if not np.any(mask):
            continue
        per_class_bits.append(float(-np.log2(np.maximum(p[mask, value], 1e-300)).mean()))
        recalls.append(float(np.mean(top[mask] == value)))
    return {
        "balanced_bits_per_unit": float(np.mean(per_class_bits)),
        "balanced_accuracy": float(np.mean(recalls)),
        "raw_accuracy": float(np.mean(top == y)),
    }


def identity_probabilities(
    train: list[dict[str, str]], test: list[dict[str, str]], class_names: tuple[str, ...], alpha: float
) -> np.ndarray:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for unit in train:
        counts[unit["identity"]][unit["role"]] += 1
    output = []
    for unit in test:
        counter = counts[unit["identity"]]
        total = sum(counter.values()) + alpha * len(class_names)
        output.append([(counter[name] + alpha) / total for name in class_names])
    return np.asarray(output)


def main() -> int:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    datasets = load_units()
    sampled = {
        name: stable_sample(units, int(design["sample_cap_per_collection_class"]))
        for name, units in datasets.items()
    }
    summary_rows = []
    for name, units in datasets.items():
        for collection in sorted({unit["collection"] for unit in units}):
            full = [unit for unit in units if unit["collection"] == collection]
            sample = [unit for unit in sampled[name] if unit["collection"] == collection]
            summary_rows.append(
                {
                    "dataset": name,
                    "collection": collection,
                    "records": len({unit["record"] for unit in full}),
                    "full_units": len(full),
                    "opaque_types": len({unit["identity"] for unit in full}),
                    "sampled_units": len(sample),
                    "role_counts_json": json.dumps(Counter(unit["role"] for unit in full), sort_keys=True),
                    "raw_forms_exported": "NO",
                }
            )
    write_tsv(SUMMARY, summary_rows)

    fold_rows: list[dict[str, object]] = []
    predictions: dict[tuple[str, str], tuple[np.ndarray, dict[str, np.ndarray]]] = {}
    aggregate: dict[tuple[str, str], list[tuple[int, dict[str, float]]]] = defaultdict(list)
    for dataset, units in datasets.items():
        class_names = DATASET_CLASSES[dataset]
        class_index = {name: index for index, name in enumerate(class_names)}
        collections = sorted({unit["collection"] for unit in units})
        for held in collections:
            train_full = [unit for unit in units if unit["collection"] != held]
            train = [unit for unit in sampled[dataset] if unit["collection"] != held]
            test = [unit for unit in sampled[dataset] if unit["collection"] == held]
            X_train = graph_features(train_full, train, int(design["partner_hash_bins"]))
            X_test = graph_features(train_full, test, int(design["partner_hash_bins"]))
            y_train = np.asarray([class_index[unit["role"]] for unit in train], dtype=int)
            y_test = np.asarray([class_index[unit["role"]] for unit in test], dtype=int)
            uniform = np.full((len(test), len(class_names)), 1 / len(class_names))
            model_probabilities = {"UNIFORM_PRIOR": uniform}
            for model_name, indices in MODEL_FEATURES.items():
                model_probabilities[model_name] = predict(
                    X_test, fit_model(X_train, y_train, indices, len(class_names), design)
                )
            model_probabilities["OPAQUE_ID_LOOKUP"] = identity_probabilities(
                train_full, test, class_names, float(design["dirichlet_alpha"])
            )
            for model_name, probabilities in model_probabilities.items():
                metrics = balanced_metrics(y_test, probabilities, len(class_names))
                fold_rows.append(
                    {
                        "dataset": dataset,
                        "held_collection": held,
                        "model": model_name,
                        "sampled_units": len(test),
                        **{key: f"{value:.12f}" for key, value in metrics.items()},
                        "gain_vs_uniform_bits": f"{(math.log2(len(class_names)) - metrics['balanced_bits_per_unit']) * len(test):.12f}",
                        "semantic_labels_used_for_training_only": "YES" if model_name != "UNIFORM_PRIOR" else "NO",
                    }
                )
                aggregate[(dataset, model_name)].append((len(test), metrics))
            predictions[(dataset, held)] = (
                y_test,
                {model: model_probabilities[model] for model in MODEL_FEATURES},
            )
    write_tsv(FOLDS, fold_rows)

    model_rows: list[dict[str, object]] = []
    for dataset in sorted(datasets):
        class_count = len(DATASET_CLASSES[dataset])
        for model_name in ("UNIFORM_PRIOR", *MODEL_FEATURES, "OPAQUE_ID_LOOKUP"):
            items = aggregate[(dataset, model_name)]
            total = sum(n for n, _ in items)
            bits = sum(n * values["balanced_bits_per_unit"] for n, values in items) / total
            model_rows.append(
                {
                    "dataset": dataset,
                    "model": model_name,
                    "folds": len(items),
                    "sampled_units": total,
                    "balanced_bits_per_unit": f"{bits:.12f}",
                    "gain_vs_uniform_bits": f"{(math.log2(class_count) - bits) * total:.12f}",
                    "positive_folds_vs_uniform": sum(
                        math.log2(class_count) > values["balanced_bits_per_unit"] for _, values in items
                    ),
                    "selection_eligible": "YES" if model_name in MODEL_FEATURES else "NO",
                }
            )
    write_tsv(MODELS, model_rows)
    model_index = {(row["dataset"], row["model"]): row for row in model_rows}
    selected = min(
        MODEL_FEATURES,
        key=lambda model: (
            sum(float(model_index[(dataset, model)]["balanced_bits_per_unit"]) for dataset in datasets),
            model,
        ),
    )

    observed_gain = sum(float(model_index[(dataset, selected)]["gain_vs_uniform_bits"]) for dataset in datasets)
    observed_by_model = {
        model: sum(float(model_index[(dataset, model)]["gain_vs_uniform_bits"]) for dataset in datasets)
        for model in MODEL_FEATURES
    }
    null_rows = []
    exceed = 0
    for world in range(int(design["null"]["worlds"])):
        rng = random.Random(int(design["null"]["seed"]) * 1_000_003 + world)
        gains = {model: 0.0 for model in MODEL_FEATURES}
        for (dataset, held), (truth, fold_probabilities) in predictions.items():
            shuffled = truth.copy()
            values = list(map(int, shuffled))
            rng.shuffle(values)
            shuffled[:] = values
            for model, probabilities in fold_probabilities.items():
                metrics = balanced_metrics(shuffled, probabilities, len(DATASET_CLASSES[dataset]))
                gains[model] += (
                    math.log2(len(DATASET_CLASSES[dataset])) - metrics["balanced_bits_per_unit"]
                ) * len(shuffled)
        max_gain = max(gains.values())
        exceed += int(max_gain >= observed_gain - 1e-12)
        null_rows.append(
            {
                "world": world,
                **{f"{model.lower()}_gain_bits": f"{gains[model]:.12f}" for model in MODEL_FEATURES},
                "max_three_gain_bits": f"{max_gain:.12f}",
            }
        )
    write_tsv(NULL, null_rows)
    p_value = (exceed + 1) / (len(null_rows) + 1)
    task_positive = {
        dataset: float(model_index[(dataset, selected)]["gain_vs_uniform_bits"]) > 0 for dataset in datasets
    }
    positive_folds = sum(
        float(row["gain_vs_uniform_bits"]) > 0
        for row in fold_rows
        if row["model"] == selected
    )
    freq_gain = {
        dataset: float(model_index[(dataset, selected)]["gain_vs_uniform_bits"])
        - float(model_index[(dataset, "FREQUENCY_DEGREE")]["gain_vs_uniform_bits"])
        for dataset in datasets
    }
    selector_paid_gain = observed_gain - float(design["selection_charge_bits"])
    supported = (
        all(task_positive.values())
        and (selected == "FREQUENCY_DEGREE" or all(value > 0 for value in freq_gain.values()))
        and positive_folds >= int(design["selection_gates"]["positive_folds_min"])
        and selector_paid_gain > 0
        and p_value <= float(design["selection_gates"]["max3_p_max"])
    )

    # Freeze the all-CoReMA coefficient matrix for anonymous C0..C4 projection.
    corema_full = datasets["COREMA"]
    corema_sample = sampled["COREMA"]
    X_corema = graph_features(corema_full, corema_sample, int(design["partner_hash_bins"]))
    y_corema = np.asarray(
        [DATASET_CLASSES["COREMA"].index(unit["role"]) for unit in corema_sample], dtype=int
    )
    fitted_models = {
        model_name: fit_model(X_corema, y_corema, indices, 5, design)
        for model_name, indices in MODEL_FEATURES.items()
    }
    fitted = fitted_models[selected]
    frozen_models = {
        model_name: {
            "feature_indices": list(model["indices"]),
            "feature_names": [FEATURE_NAMES[index] for index in model["indices"]],
            "mean": model["mean"].tolist(),
            "scale": model["scale"].tolist(),
            "beta": model["beta"].tolist(),
        }
        for model_name, model in fitted_models.items()
    }
    coefficient_payload = {
        "selected_model": selected,
        "selected_feature_indices": list(MODEL_FEATURES[selected]),
        "selected_feature_names": [FEATURE_NAMES[index] for index in MODEL_FEATURES[selected]],
        "anonymous_class_order": [f"C{index}" for index in range(5)],
        "comparator_role_order_sealed_for_audit": list(DATASET_CLASSES["COREMA"]),
        "mean": fitted["mean"].tolist(),
        "scale": fitted["scale"].tolist(),
        "beta": fitted["beta"].tolist(),
        "frozen_candidate_models": frozen_models,
    }
    variant_rows = [
        {
            "variant": model,
            "feature_indices": "|".join(map(str, MODEL_FEATURES[model])),
            "aggregate_gain_vs_uniform_bits": f"{observed_by_model[model]:.12f}",
            "selected": "YES" if model == selected else "NO",
            "post_voynich_tuning": "NO",
        }
        for model in MODEL_FEATURES
    ]
    variant_rows.append(
        {
            "variant": "OPAQUE_ID_LOOKUP",
            "feature_indices": "EXACT_ID",
            "aggregate_gain_vs_uniform_bits": f"{sum(float(model_index[(dataset, 'OPAQUE_ID_LOOKUP')]['gain_vs_uniform_bits']) for dataset in datasets):.12f}",
            "selected": "NO_INELIGIBLE_NAMESPACE_SPECIFIC",
            "post_voynich_tuning": "NO",
        }
    )
    write_tsv(VARIANTS, variant_rows)

    freeze = {
        "schema": "GDT339_INVARIANT_FREEZE_V1",
        "status": "COMPARATOR_INVARIANT_SUPPORTED_AND_FROZEN" if supported else "NO_TRANSFERABLE_COMPARATOR_INVARIANT",
        "selected": coefficient_payload,
        "comparator_evidence": {
            "aggregate_gain_vs_uniform_bits": observed_gain,
            "selector_paid_gain_bits": selector_paid_gain,
            "positive_folds": positive_folds,
            "folds": 10,
            "task_positive": task_positive,
            "gain_over_frequency_by_task": freq_gain,
            "max_three_diagnostic_p": p_value,
        },
        "voynich_outcomes_read_or_scored": False,
        "semantic_labels_exported_to_voynich": False,
        "inputs": {
            str(path.relative_to(ROOT)): sha256_file(path)
            for path in (METHOD, DESIGN, COREMA, COREMA_FREEZE, NUREMBERG, NUREMBERG_FREEZE)
        },
        "outputs": {
            str(path.relative_to(ROOT)): sha256_file(path)
            for path in (SUMMARY, FOLDS, MODELS, NULL, VARIANTS)
        },
        "implementation": {
            str(Path(__file__).resolve().relative_to(ROOT)): sha256_file(Path(__file__).resolve())
        },
        "f84": {"opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Comparator-selected opaque incidence instrument only; no Voynich class, role, meaning, or translation.",
    }
    freeze["content_sha256"] = hashlib.sha256(canonical_json_bytes(freeze)).hexdigest()
    FREEZE.write_bytes(canonical_json_bytes(freeze))
    result = {
        "schema": "GDT339_COMPARATOR_RESULT_V1",
        "status": freeze["status"],
        "selected_model": selected,
        "comparator_evidence": freeze["comparator_evidence"],
        "units": {name: len(units) for name, units in datasets.items()},
        "sampled_units": {name: len(units) for name, units in sampled.items()},
        "opaque_ids_only": True,
        "raw_position_shape_language_and_local_sequence_used": False,
        "voynich_outcomes_read_or_scored": False,
        "inputs": freeze["inputs"],
        "outputs": {**freeze["outputs"], str(FREEZE.relative_to(ROOT)): sha256_file(FREEZE)},
        "implementation": freeze["implementation"],
        "claim_ceiling": freeze["claim_ceiling"],
    }
    result["content_sha256"] = hashlib.sha256(canonical_json_bytes(result)).hexdigest()
    RESULT.write_bytes(canonical_json_bytes(result))
    report = f"""# GDT339 comparator-first incidence report

Status: **{freeze['status']}**.

The comparator stage used {len(datasets['COREMA']):,} CoReMA semantic units from six held collections and {len(datasets['NUREMBERG']):,} Nuremberg section-labelled token occurrences from four held books. All lexical forms were replaced by opaque IDs before feature construction; no position, word shape, language feature, or local sequence entered a model.

The selected transferable feature family is **{selected}**. It gains {observed_gain:+.3f} class-balanced held bits over uniform ({selector_paid_gain:+.3f} after the fixed three-model selector), is positive in {positive_folds}/10 held collections/books, and has fixed-prediction max-three diagnostic p={p_value:.6f}. Task gains over the frequency-degree model are {freq_gain['COREMA']:+.3f} bits for CoReMA and {freq_gain['NUREMBERG']:+.3f} bits for Nuremberg. Exact opaque-ID lookup is reported as a namespace-specific ceiling and was ineligible for selection.

The selected CoReMA coefficients and anonymous class order `C0..C4` are frozen in `artifacts/gdt339_invariant_freeze.json` before any Voynich outcome is scored. Comparator semantic names remain audit metadata and may not be exported as Voynich meanings.

## Claim ceiling

Comparator-calibrated opaque incidence only. No Voynich tuple, role, word, meaning, language, plaintext, translation, or f84 result follows from this stage.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": freeze["status"], "selected": selected, "evidence": freeze["comparator_evidence"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
