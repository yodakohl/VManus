#!/usr/bin/env python3
"""Freeze comparator-selected GDT378 signatures before any Voynich access."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
ART = BASE / "artifacts"
sys.path.insert(0, str(BASE / "src"))
import run_comparator as rc  # noqa: E402

PROCEDURAL = {"CURIOUS_CURES", "HARLEIAN_COOKERY", "QUINTE_ESSENCE"}
NON_RECIPE_GOLD = {"COREMA", "PCEEC2"}
QGRID = [.50, .65, .80, .90]

NUISANCE_NAMES = [
    "INTERCEPT", "LOG_RECORD_ELEMENTS", "RELATIVE_POSITION", "RELATIVE_POSITION_SQUARED",
    "LOG_SURFACE_LENGTH", "LOG_DIRECT_TOKEN_COUNT", "RECORD_START", "RECORD_END",
    "NORMALIZED_RECORD_ORDINAL", "LOG_PHYSICAL_LINE_COUNT",
]
SCOPE_NAMES = [
    "FORWARD_HORIZON", "BACKWARD_HORIZON", "PREVIOUS_RETURN_DISTANCE",
    "NEXT_RETURN_DISTANCE", "PREFIX_ID_DIVERSITY", "SUFFIX_ID_DIVERSITY",
    "HAS_PREVIOUS_SAME_ID", "HAS_NEXT_SAME_ID",
]
NEIGHBOR_NAMES = [
    "PREVIOUS_IS_SAME_ID", "NEXT_IS_SAME_ID", "LOG_WITHIN_RECORD_ID_COUNT",
    "WITHIN_RECORD_ID_DIVERSITY", "ID_IN_PREVIOUS_RECORD", "ID_IN_NEXT_RECORD",
    "PREVIOUS_RECORD_SET_JACCARD", "NEXT_RECORD_SET_JACCARD", "PREVIOUS_EQUALS_NEXT",
    "RETURN_DISTANCE_2_LEFT", "RETURN_DISTANCE_2_RIGHT", "LOG_DOMAIN_ID_COUNT",
    "LOG_DOMAIN_ID_RECORD_COUNT", "LOG_DOMAIN_PREDECESSOR_DIVERSITY",
    "LOG_DOMAIN_SUCCESSOR_DIVERSITY", "DOMAIN_ID_MEAN_POSITION", "DOMAIN_ID_POSITION_SD",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj):
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def table(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def matrix_for(rep, xn, scope, neighbor):
    if rep == "NEIGHBOR_RECURRENCE":
        return np.column_stack([xn, neighbor]), "NUISANCE_PLUS_NEIGHBOR", NUISANCE_NAMES + NEIGHBOR_NAMES
    if rep in {"ABSOLUTE_PROBABILITY", "WITHIN_RECORD_RANK"}:
        return np.column_stack([xn, scope, neighbor]), "NUISANCE_PLUS_SCOPE_PLUS_NEIGHBOR", NUISANCE_NAMES + SCOPE_NAMES + NEIGHBOR_NAMES
    raise ValueError(f"Unsupported selected representation: {rep}")


def held_scores(endpoint, rep, available, y, domain_arr, x, records):
    scores = np.full(len(y), np.nan)
    for held in available:
        train = np.where(np.isin(domain_arr, [domain for domain in available if domain != held]))[0]
        test = np.where(domain_arr == held)[0]
        model = rc.fit(x[train], y[train], domain_arr[train].tolist())
        base = rc.predict(model, x[test])
        scores[test] = rc.within_record_rank(base, test, records) if rep == "WITHIN_RECORD_RANK" else base
    return scores


def threshold_quantile(scores, y, domain_arr, available):
    candidates = []
    for quantile in QGRID:
        balanced = []
        for domain in available:
            ids = np.where(domain_arr == domain)[0]
            local = scores[ids]
            labels = y[ids]
            cut = float(np.quantile(local, quantile))
            predicted = local >= cut
            tpr = float(predicted[labels == 1].mean()) if labels.sum() else 0.0
            tnr = float((~predicted[labels == 0]).mean()) if (labels == 0).sum() else 0.0
            balanced.append((tpr + tnr) / 2)
        candidates.append((sum(balanced) / len(balanced), quantile))
    return max(candidates)


def main():
    result = json.loads((ART / "gdt378_comparator_result.json").read_text())
    design = json.loads((ART / "gdt378_comparator_design_freeze.json").read_text())
    contract = json.loads((ART / "gdt378_oracle_contract.json").read_text())
    assert result["voynich_rows_read"] == 0 and not result["voynich_scored"] and not any(result["f84"].values())
    obs = rc.read(ART / "gdt378_comparator_observation_layer.tsv.gz")
    oracle = rc.read(ART / "gdt378_hidden_oracle.tsv.gz")
    summary = table(ART / "gdt378_signature_summary.tsv")
    xn, scope, neighbor, records = rc.features(obs)
    domain_arr = np.array([row["domain"] for row in obs])
    selected = []

    for endpoint in rc.ENDPOINTS:
        if endpoint == "HEAD_WITH_DEPENDENTS":
            continue
        candidates = [row for row in summary if row["endpoint"] == endpoint and row["transfer_auc_floor"]]
        if not candidates:
            continue
        row = max(candidates, key=lambda item: (float(item["transfer_auc_floor"]), float(item["mean_domain_auc"]), -rc.REPS.index(item["representation"])))
        aucs = json.loads(row["domain_aucs_json"])
        gains = json.loads(row["domain_full_gains_json"])
        strong = sorted(domain for domain in aucs if aucs[domain] >= .65 and gains.get(domain, -math.inf) > 0)
        eligible = (
            float(row["transfer_auc_floor"]) >= .65
            and float(row["max_family_p"]) <= .05
            and len(strong) >= 3
            and bool(set(strong) & PROCEDURAL)
            and bool(set(strong) & NON_RECIPE_GOLD)
        )
        if not eligible:
            continue
        rep = row["representation"]
        x, model_kind, feature_names = matrix_for(rep, xn, scope, neighbor)
        available = contract["availability"][endpoint]
        y = np.array([int(item[endpoint]) for item in oracle], int)
        held = held_scores(endpoint, rep, available, y, domain_arr, x, records)
        valid = np.isfinite(held)
        macro_ba, quantile = threshold_quantile(held[valid], y[valid], domain_arr[valid], available)
        ids = np.where(np.isin(domain_arr, available))[0]
        model = rc.fit(x[ids], y[ids], domain_arr[ids].tolist())
        coefficient, mean, scale = model
        selected.append({
            "anonymous_signature_id": f"CMP_FUNCTION_{len(selected)+1:02d}",
            "comparator_oracle_endpoint": endpoint,
            "semantic_state_on_voynich": "UNASSIGNED",
            "representation": rep,
            "model_kind": model_kind,
            "application_postprocess": "WITHIN_RECORD_RANK" if rep == "WITHIN_RECORD_RANK" else "PROBABILITY",
            "feature_names": feature_names,
            "coefficients": coefficient.tolist(),
            "standardization_mean_excluding_intercept": mean.tolist(),
            "standardization_scale_excluding_intercept": scale.tolist(),
            "threshold_type": "WITHIN_RESOLUTION_SCORE_QUANTILE",
            "threshold_quantile": quantile,
            "held_comparator_macro_balanced_accuracy_at_quantile": macro_ba,
            "transfer_auc_floor": float(row["transfer_auc_floor"]),
            "max_family_p": float(row["max_family_p"]),
            "strong_domains_auc_ge_0_65_and_positive_structure_gain": strong,
            "available_domains": available,
            "training_rows": len(ids),
            "training_positives": int(y[ids].sum()),
        })

    freeze = {
        "schema": "GDT378_SECONDARY_TRANSFER_SIGNATURE_FREEZE_V1",
        "status": "FROZEN_BEFORE_ANY_VOYNICH_ACCESS",
        "chronology_note": "Comparator outcomes selected signatures; no Voynich table, row, identity, score, or candidate was accessed before this freeze.",
        "head_signature_status": "FAILED_OWN_PREDECLARED_GATE_NOT_TRANSFERRED",
        "secondary_selection_rule": {
            "minimum_transfer_auc_floor": .65,
            "maximum_max_family_p": .05,
            "minimum_domains_with_auc_ge_0_65_and_positive_structure_gain": 3,
            "require_at_least_one_procedural_domain": True,
            "require_at_least_one_non_recipe_gold_domain": True,
        },
        "signatures": selected,
        "signature_count": len(selected),
        "charged_application_family": {
            "resolutions": ["ATOMIC_JOINT_TUPLE", "SOURCE_GROUP", "FIELD_CONSTRUCTION_SPAN", "GRAMMAR_SLOT_POSITION"],
            "signatures": [row["anonymous_signature_id"] for row in selected],
            "thresholds": "FROZEN_PER_SIGNATURE_QUANTILE",
            "selection_and_null": "MAXT_ACROSS_ALL_SIGNATURES_RESOLUTIONS_SLOTS_AND_OPERATOR_FAMILIES",
        },
        "forbidden_application_inputs": ["raw_glyph_similarity", "PAGE_HOST_substrings", "semantic_gloss", "POS", "translation", "f84"],
        "voynich_accessed": False,
        "voynich_scored": False,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "inputs": {
            str(path.relative_to(ROOT)): sha(path)
            for path in [
                ART / "gdt378_comparator_result.json", ART / "gdt378_signature_summary.tsv",
                ART / "gdt378_comparator_observation_layer.tsv.gz", ART / "gdt378_hidden_oracle.tsv.gz",
                ART / "gdt378_oracle_contract.json", ART / "gdt378_comparator_design_freeze.json",
            ]
        },
        "implementation": {
            str((BASE / "src/freeze_transfer_signatures.py").relative_to(ROOT)): sha(BASE / "src/freeze_transfer_signatures.py"),
            str((BASE / "src/run_comparator.py").relative_to(ROOT)): sha(BASE / "src/run_comparator.py"),
        },
        "claim_ceiling": "ANONYMOUS_COMPARATOR_FUNCTION_SIGNATURES_ONLY_NO_VOYNICH_FUNCTION_OR_SEMANTICS",
    }
    freeze["content_hash"] = content(freeze)
    out = ART / "gdt378_secondary_transfer_signature_freeze.json"
    out.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": freeze["status"], "signatures": [(r["anonymous_signature_id"], r["comparator_oracle_endpoint"], r["representation"]) for r in selected]}))


if __name__ == "__main__":
    main()
