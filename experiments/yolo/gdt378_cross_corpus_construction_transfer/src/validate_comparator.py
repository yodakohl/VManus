#!/usr/bin/env python3
"""Independent retained-output validation for the GDT378 comparator stage."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
ART = BASE / "artifacts"
OBS = ART / "gdt378_comparator_observation_layer.tsv.gz"
ORACLE = ART / "gdt378_hidden_oracle.tsv.gz"
RESULT = ART / "gdt378_comparator_result.json"
DESIGN = ART / "gdt378_comparator_design_freeze.json"
CONTRACT = ART / "gdt378_oracle_contract.json"
PRED = ART / "gdt378_head_held_predictions.tsv.gz"
FOLDS = ART / "gdt378_comparator_fold_scores.tsv"
SUMMARY = ART / "gdt378_signature_summary.tsv"
NULL = ART / "gdt378_comparator_null.tsv"
NULL_WORLDS = ART / "gdt378_comparator_null_worlds.tsv.gz"
FAMILY = ART / "gdt378_functional_family_calibration.tsv"
SIGNATURE = ART / "gdt378_transfer_signature_freeze.json"
SECONDARY_FREEZE = ART / "gdt378_secondary_transfer_signature_freeze.json"

REPS = [
    "ABSOLUTE_PROBABILITY", "WITHIN_RECORD_RANK",
    "STRUCTURE_MINUS_NUISANCE_DELTA", "DOMAIN_STANDARDIZED",
    "SCOPE_HORIZON", "NEIGHBOR_RECURRENCE", "FIXED_RANK_COMBINATION",
]
ENDPOINTS = [
    "HEAD_WITH_DEPENDENTS", "HIGH_VALENCY_HEAD", "REF_ANAPHORA",
    "CORRELATIVE_MEMBER", "NEXT_RESUME", "UNTIL_STATE_GATE", "COORDINATOR",
    "ALTERNATIVE_OR", "POLARITY_EXCLUSION", "COMPARISON", "FUNCTION_WORD",
    "STATE_TRANSITION", "CLOSER",
]


def rows(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rankdata(values):
    values = np.asarray(values, float)
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), float)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and values[order[j]] == values[order[i]]:
            j += 1
        ranks[order[i:j]] = (i + j + 1) / 2
        i = j
    return ranks


def auc(labels, scores):
    labels = np.asarray(labels, int)
    positive = int(labels.sum())
    negative = len(labels) - positive
    if not positive or not negative:
        return float("nan")
    return float((rankdata(scores)[labels == 1].sum() - positive * (positive + 1) / 2) / (positive * negative))


def average_precision(labels, scores):
    labels = np.asarray(labels, int)
    positive = int(labels.sum())
    if not positive:
        return float("nan")
    order = np.argsort(-np.asarray(scores, float), kind="stable")
    hits = 0
    total = 0.0
    for rank, index in enumerate(order, 1):
        if labels[index]:
            hits += 1
            total += hits / rank
    return total / positive


def bits(labels, probabilities):
    labels = np.asarray(labels, int)
    probabilities = np.clip(np.asarray(probabilities, float), 1e-9, 1 - 1e-9)
    return float(-np.sum(labels * np.log2(probabilities) + (1 - labels) * np.log2(1 - probabilities)))


def transfer_stat(endpoint, values, available):
    finite = {domain: values[domain] for domain in available if domain in values and math.isfinite(values[domain])}
    if endpoint == "HEAD_WITH_DEPENDENTS":
        procedural = [finite[d] for d in ("CURIOUS_CURES", "HARLEIAN_COOKERY", "QUINTE_ESSENCE") if d in finite]
        if "COREMA" not in finite or "PCEEC2" not in finite or not procedural:
            return float("nan")
        return min(finite["COREMA"], finite["PCEEC2"], max(procedural))
    if len(finite) < 3:
        return float("nan")
    return sorted(finite.values(), reverse=True)[2]


def main():
    result = json.loads(RESULT.read_text())
    design = json.loads(DESIGN.read_text())
    contract = json.loads(CONTRACT.read_text())
    signature = json.loads(SIGNATURE.read_text())
    secondary_freeze = json.loads(SECONDARY_FREEZE.read_text())
    obs = rows(OBS)
    oracle = rows(ORACLE)
    pred = rows(PRED)
    folds = rows(FOLDS)
    summary = rows(SUMMARY)
    null_summary = rows(NULL)
    null_worlds = rows(NULL_WORLDS)
    family = rows(FAMILY)
    checks = {}

    checks["layer_keys_exact"] = [r["element_key"] for r in obs] == [r["element_key"] for r in oracle] == [r["element_key"] for r in pred]
    checks["row_count"] = len(obs) == len(oracle) == len(pred) == design["rows"] == result["rows"] == 133183
    checks["record_count"] = len({(r["domain"], r["collection_id"], r["record_id"]) for r in obs}) == design["records"] == result["records"] == 3235
    checks["domain_counts"] = Counter(r["domain"] for r in obs) == Counter({"COREMA": 27349, "PCEEC2": 27518, "CURIOUS_CURES": 21817, "HARLEIAN_COOKERY": 40826, "QUINTE_ESSENCE": 15673})
    checks["observation_fields_form_blind"] = not (set(design["forbidden_observation_fields"]) & set(obs[0]))
    checks["oracle_fields_labels_only"] = set(oracle[0]) == {"element_key", "domain", "collection_id", "record_id", *ENDPOINTS}
    checks["fold_domains_independent"] = all(r["held_domain"] in contract["availability"][r["endpoint"]] for r in folds)
    checks["representations_exact"] = set(r["representation"] for r in folds) == set(REPS)
    checks["families_exact"] = set(r["endpoint"] for r in family) == set(ENDPOINTS)
    checks["null_world_shape"] = len(null_worlds) == 256 * len(ENDPOINTS) * len(REPS) and set(int(r["world"]) for r in null_worlds) == set(range(256))

    by_world = defaultdict(list)
    by_null = defaultdict(list)
    for row in null_worlds:
        by_world[int(row["world"])].append(float(row["world_max"]))
        if row["transfer_auc_floor"]:
            by_null[(row["endpoint"], row["representation"])].append(float(row["transfer_auc_floor"]))
    checks["world_max_constant"] = all(len(set(values)) == 1 for values in by_world.values())
    maxima = [by_world[world][0] for world in range(256)]

    fold_index = {(r["endpoint"], r["held_domain"], r["representation"]): r for r in folds}
    head_math = True
    for domain in contract["availability"]["HEAD_WITH_DEPENDENTS"]:
        ids = [i for i, row in enumerate(pred) if row["domain"] == domain]
        labels = [int(pred[i]["oracle_label"]) for i in ids]
        nuisance = [float(pred[i]["nuisance_probability"]) for i in ids]
        full = [float(pred[i]["full_probability"]) for i in ids]
        gain = bits(labels, nuisance) - bits(labels, full)
        rep = "SCOPE_HORIZON"
        row = fold_index[("HEAD_WITH_DEPENDENTS", domain, rep)]
        scores = [float(pred[i]["selected_representation_score"]) for i in ids]
        head_math &= all(pred[i]["selected_representation"] == rep for i in ids)
        head_math &= abs(auc(labels, scores) - float(row["auc"])) < 2e-8
        head_math &= abs(average_precision(labels, scores) - float(row["average_precision"])) < 2e-8
        head_math &= abs(gain - float(row["full_gain_vs_nuisance_bits"])) < 2e-5
    checks["head_fold_math"] = head_math

    summary_math = True
    for row in summary:
        if not row["transfer_auc_floor"]:
            continue
        key = (row["endpoint"], row["representation"])
        domain_aucs = json.loads(row["domain_aucs_json"])
        observed = transfer_stat(row["endpoint"], domain_aucs, contract["availability"][row["endpoint"]])
        local_p = (1 + sum(value >= observed for value in by_null[key])) / (1 + len(by_null[key]))
        max_p = (1 + sum(value >= observed for value in maxima)) / 257
        summary_math &= abs(observed - float(row["transfer_auc_floor"])) < 2e-9
        summary_math &= abs(local_p - float(row["local_p"])) < 2e-9
        summary_math &= abs(max_p - float(row["max_family_p"])) < 2e-9
    checks["summary_and_null_math"] = summary_math

    head_rows = sorted((r for r in summary if r["endpoint"] == "HEAD_WITH_DEPENDENTS" and r["transfer_auc_floor"]), key=lambda r: (-float(r["transfer_auc_floor"]), -float(r["mean_domain_auc"]), REPS.index(r["representation"])))
    best = head_rows[0]
    checks["best_head_exact"] = best["representation"] == result["best_head_representation"] == signature["representation"] == "SCOPE_HORIZON" and abs(float(best["transfer_auc_floor"]) - result["best_head_transfer_auc_floor"]) < 1e-12
    head_aucs = json.loads(best["domain_aucs_json"])
    head_gains = json.loads(best["domain_full_gains_json"])
    procedural = [d for d in ("CURIOUS_CURES", "HARLEIAN_COOKERY", "QUINTE_ESSENCE") if head_aucs.get(d, 0) >= .65 and head_gains.get(d, 0) > 0]
    gate = head_aucs.get("COREMA", 0) >= .65 and head_gains.get("COREMA", 0) > 0 and head_aucs.get("PCEEC2", 0) >= .65 and head_gains.get("PCEEC2", 0) > 0 and bool(procedural) and float(best["max_family_p"]) <= .05
    checks["head_gate_rebuilt"] = not gate and result["head_gate_pass"] is False and signature["head_gate_pass"] is False and signature["status"] == "NO_SIGNATURE_AUTHORIZED_FOR_VOYNICH"
    checks["head_domain_failures_explicit"] = head_aucs["COREMA"] < .65 and head_aucs["PCEEC2"] < .65 and head_gains["COREMA"] < 0 and head_gains["PCEEC2"] < 0
    checks["procedural_pass_only_quinte"] = procedural == ["QUINTE_ESSENCE"]
    checks["secondary_provisional_count"] = sum(r["status"] == "COMPARATOR_TRANSFER_PROVISIONAL" for r in family) == 7
    checks["secondary_not_voynich_authorized"] = all(r["voynich_eligible"] == "0" for r in family)
    checks["no_voynich"] = result["voynich_scored"] is False and result["voynich_rows_read"] == 0 and signature["voynich_scored"] is False
    checks["f84_flags"] = not any(result["f84"].values()) and signature["f84_accessed"] is False
    checks["result_status"] = result["status"] == "NO_CONSTRUCTION_HEAD_SIGNATURE_GENERALIZED"
    checks["result_input_hashes"] = all(sha(ROOT / path) == digest for path, digest in result["inputs"].items())
    checks["result_output_hashes"] = all(sha(ROOT / path) == digest for path, digest in result["outputs"].items())
    checks["implementation_hash"] = all(sha(ROOT / path) == digest for path, digest in result["implementation"].items())
    clone = dict(result)
    expected = clone.pop("content_hash")
    checks["result_content_hash"] = hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected
    sig_clone = dict(signature)
    sig_expected = sig_clone.pop("content_hash")
    checks["signature_content_hash"] = hashlib.sha256(json.dumps(sig_clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == sig_expected
    checks["null_summary_rows"] = len(null_summary) == sum(bool(r["transfer_auc_floor"]) for r in summary)
    frozen = secondary_freeze["signatures"]
    checks["secondary_freeze_exact"] = [(r["comparator_oracle_endpoint"], r["representation"]) for r in frozen] == [
        ("UNTIL_STATE_GATE", "WITHIN_RECORD_RANK"),
        ("ALTERNATIVE_OR", "NEIGHBOR_RECURRENCE"),
        ("POLARITY_EXCLUSION", "NEIGHBOR_RECURRENCE"),
        ("FUNCTION_WORD", "ABSOLUTE_PROBABILITY"),
    ]
    checks["secondary_freeze_gate"] = all(
        r["transfer_auc_floor"] >= .65 and r["max_family_p"] <= .05
        and len(r["strong_domains_auc_ge_0_65_and_positive_structure_gain"]) >= 3
        and bool(set(r["strong_domains_auc_ge_0_65_and_positive_structure_gain"]) & {"CURIOUS_CURES", "HARLEIAN_COOKERY", "QUINTE_ESSENCE"})
        and bool(set(r["strong_domains_auc_ge_0_65_and_positive_structure_gain"]) & {"COREMA", "PCEEC2"})
        for r in frozen
    )
    checks["secondary_model_shapes"] = all(
        len(r["coefficients"]) == len(r["feature_names"])
        and len(r["standardization_mean_excluding_intercept"]) == len(r["feature_names"]) - 1
        and len(r["standardization_scale_excluding_intercept"]) == len(r["feature_names"]) - 1
        and all(math.isfinite(float(value)) for key in ("coefficients", "standardization_mean_excluding_intercept", "standardization_scale_excluding_intercept") for value in r[key])
        for r in frozen
    )
    secondary_clone = dict(secondary_freeze)
    secondary_expected = secondary_clone.pop("content_hash")
    checks["secondary_freeze_content_hash"] = hashlib.sha256(json.dumps(secondary_clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == secondary_expected
    checks["secondary_freeze_hashes"] = all(sha(ROOT / path) == digest for part in ("inputs", "implementation") for path, digest in secondary_freeze[part].items())
    checks["secondary_freeze_seals"] = secondary_freeze["status"] == "FROZEN_BEFORE_ANY_VOYNICH_ACCESS" and not secondary_freeze["voynich_accessed"] and not secondary_freeze["voynich_scored"] and not any(secondary_freeze["f84"].values())

    validation = {
        "schema": "GDT378_COMPARATOR_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scope": "Independent retained-output keys, counts, HEAD fold metrics/gains, transfer statistic, stored-null p-values, gates, hashes, and seals; does not independently refit all 91 detectors.",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
    }
    (ART / "gdt378_comparator_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(validation["status"], f"{validation['checks_passed']}/{validation['checks_total']}")
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
