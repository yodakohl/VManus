#!/usr/bin/env python3
"""Run the frozen GDT380 identity-free comparator calibration; no Voynich input."""
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
BASE = ROOT / "experiments/yolo/gdt380_identity_free_functional_transfer"
ART = BASE / "artifacts"
G378 = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"
OBS = G378 / "gdt378_comparator_observation_layer.tsv.gz"
ORACLE = G378 / "gdt378_hidden_oracle.tsv.gz"
CONTRACT = G378 / "gdt378_oracle_contract.json"
DESIGN = ART / "gdt380_comparator_behavior_freeze.json"

FAMILIES = [
    ("CMP_FUNCTION_01", "UNTIL_STATE_GATE", "GATE_TRANSITION"),
    ("CMP_FUNCTION_02", "ALTERNATIVE_OR", "BRANCH_RECONVERGENCE"),
    ("CMP_FUNCTION_03", "POLARITY_EXCLUSION", "MARKED_INVERSE_DELTA"),
    ("CMP_FUNCTION_04", "FUNCTION_WORD", "CLOSED_CLASS_BOTTLENECK"),
]
PROCEDURAL = {"CURIOUS_CURES", "HARLEIAN_COOKERY", "QUINTE_ESSENCE"}
HORIZONS = (1, 2, 4, 8)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict]) -> None:
    if path.suffix == ".gz":
        raw = path.open("wb")
        gz = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
        handle = io.TextIOWrapper(gz, encoding="utf-8", newline="")
    else:
        handle = path.open("w", encoding="utf-8", newline="")
    with handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, obj: dict) -> None:
    obj["content_hash"] = content(obj)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def entropy(values: list[str]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    n = len(values)
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / max(1, len(left | right))


def sigmoid(x: np.ndarray) -> np.ndarray:
    z = np.clip(x, -40, 40)
    return np.where(z >= 0, 1 / (1 + np.exp(-z)), np.exp(z) / (1 + np.exp(z)))


def fit(X: np.ndarray, y: np.ndarray, domains: list[str], l2: float = 4.0):
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    domain_counts = Counter(domains)
    weights = np.array([len(domains) / (len(domain_counts) * domain_counts[d]) for d in domains], float)
    mu = np.average(X[:, 1:], axis=0, weights=weights)
    sd = np.sqrt(np.average((X[:, 1:] - mu) ** 2, axis=0, weights=weights))
    sd[sd < 1e-8] = 1.0
    Z = X.copy()
    Z[:, 1:] = (Z[:, 1:] - mu) / sd
    beta = np.zeros(Z.shape[1])
    penalty = np.ones(len(beta)) * l2
    penalty[0] = 0.0
    for _ in range(35):
        prob = sigmoid(Z @ beta)
        work = np.maximum(prob * (1 - prob), 1e-6) * weights
        hessian = (Z.T * work) @ Z + np.diag(penalty)
        gradient = Z.T @ ((y - prob) * weights) - penalty * beta
        try:
            step = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(hessian, gradient, rcond=None)[0]
        beta += step
        if np.max(np.abs(step)) < 1e-7:
            break
    return beta, mu, sd


def predict(model, X: np.ndarray) -> np.ndarray:
    beta, mu, sd = model
    Z = np.asarray(X, float).copy()
    Z[:, 1:] = (Z[:, 1:] - mu) / sd
    return np.clip(sigmoid(Z @ beta), 1e-7, 1 - 1e-7)


def bits(y: np.ndarray, probability: np.ndarray) -> float:
    p = np.clip(np.asarray(probability), 1e-9, 1 - 1e-9)
    y = np.asarray(y)
    return float(-np.sum(y * np.log2(p) + (1 - y) * np.log2(1 - p)))


def rankdata(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values)
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


def auc(y: np.ndarray, score: np.ndarray) -> float:
    y = np.asarray(y, int)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if not n1 or not n0:
        return float("nan")
    ranks = rankdata(score)
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def average_precision(y: np.ndarray, score: np.ndarray) -> float:
    y = np.asarray(y, int)
    positives = int(y.sum())
    if not positives:
        return float("nan")
    order = np.argsort(-np.asarray(score), kind="stable")
    hit = 0
    total = 0.0
    for rank, idx in enumerate(order, 1):
        if y[idx]:
            hit += 1
            total += hit / rank
    return total / positives


def build_features(obs: list[dict]):
    n = len(obs)
    by_record: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    by_domain: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(obs):
        key = (row["domain"], row["collection_id"], row["record_id"])
        by_record[key].append(i)
        by_domain[row["domain"]].append(i)

    domain_forms = {}
    domain_edges = {}
    for domain in by_domain:
        form_stats = defaultdict(lambda: {"n": 0, "records": set(), "collections": set(), "prev": set(), "next": set(), "positions": []})
        edge_counts = Counter()
        for record, ids in by_record.items():
            if record[0] != domain:
                continue
            ids.sort(key=lambda i: int(obs[i]["element_ordinal"]))
            forms = [obs[i]["opaque_form_id"] for i in ids]
            for j, idx in enumerate(ids):
                form = forms[j]
                stat = form_stats[form]
                stat["n"] += 1
                stat["records"].add(record)
                stat["collections"].add(record[1])
                stat["positions"].append(float(obs[idx]["relative_position"]))
                if j:
                    stat["prev"].add(forms[j - 1])
                if j + 1 < len(forms):
                    stat["next"].add(forms[j + 1])
                    edge_counts[(forms[j], forms[j + 1])] += 1
        domain_forms[domain] = form_stats
        domain_edges[domain] = edge_counts

    nuisance_names = [
        "INTERCEPT", "LOG_RECORD_LENGTH", "RELATIVE_POSITION", "RELATIVE_POSITION_SQ",
        "LOG_SURFACE_LENGTH", "LOG_DIRECT_TOKEN_COUNT", "BOUNDARY_BEFORE", "BOUNDARY_AFTER",
        "LOG_WITHIN_RECORD_FREQUENCY", "IS_RECORD_START", "IS_RECORD_END",
    ]
    common_names = []
    for h in HORIZONS:
        common_names.extend([
            f"H{h}_LEFT_UNIQUE_RATE", f"H{h}_RIGHT_UNIQUE_RATE", f"H{h}_UNIQUE_DELTA",
            f"H{h}_LEFT_ENTROPY", f"H{h}_RIGHT_ENTROPY", f"H{h}_ENTROPY_DELTA",
            f"H{h}_BAG_JACCARD", f"H{h}_BAG_OVERLAP_MIN", f"H{h}_RIGHT_NOVELTY_RATE",
            f"H{h}_PIVOT_RETURN_LEFT", f"H{h}_PIVOT_RETURN_RIGHT",
            f"H{h}_LEFT_RIGHT_RECONVERGENCE", f"H{h}_RIGHT_TO_LEFT_RETURN",
        ])
    common_names.extend([
        "PREV_EQUALS_NEXT", "PIVOT_SELF_REPEAT_LEFT", "PIVOT_SELF_REPEAT_RIGHT",
        "LOG_FORWARD_RETURN_DISTANCE", "LOG_BACKWARD_RETURN_DISTANCE", "NO_FORWARD_RETURN",
        "DELETE_BRIDGE_LOG_FREQUENCY", "LOG_DOMAIN_FORM_FREQUENCY", "LOG_DOMAIN_RECORD_COVERAGE",
        "LOG_PREV_DIVERSITY", "LOG_NEXT_DIVERSITY", "POSITION_STD", "COLLECTION_COVERAGE",
        "NEIGHBOR_DIVERSITY_PER_OCCURRENCE", "RECORD_REMAINING_FRACTION",
    ])
    pivot_dependent = {
        "PIVOT_SELF_REPEAT_LEFT", "PIVOT_SELF_REPEAT_RIGHT", "LOG_FORWARD_RETURN_DISTANCE",
        "LOG_BACKWARD_RETURN_DISTANCE", "NO_FORWARD_RETURN", "LOG_DOMAIN_FORM_FREQUENCY",
        "LOG_DOMAIN_RECORD_COVERAGE", "LOG_PREV_DIVERSITY", "LOG_NEXT_DIVERSITY",
        "POSITION_STD", "COLLECTION_COVERAGE", "NEIGHBOR_DIVERSITY_PER_OCCURRENCE",
    }
    pivot_dependent.update({f"H{h}_PIVOT_RETURN_LEFT" for h in HORIZONS})
    pivot_dependent.update({f"H{h}_PIVOT_RETURN_RIGHT" for h in HORIZONS})

    nuisance = np.zeros((n, len(nuisance_names)), float)
    common = np.zeros((n, len(common_names)), float)
    record_keys = [None] * n

    for record, ids in by_record.items():
        ids.sort(key=lambda i: int(obs[i]["element_ordinal"]))
        forms = [obs[i]["opaque_form_id"] for i in ids]
        count = Counter(forms)
        positions = defaultdict(list)
        for j, form in enumerate(forms):
            positions[form].append(j)
        m = len(ids)
        for j, idx in enumerate(ids):
            row = obs[idx]
            form = forms[j]
            stat = domain_forms[record[0]][form]
            previous = [p for p in positions[form] if p < j]
            following = [p for p in positions[form] if p > j]
            nv = [
                1.0, math.log1p(m), float(row["relative_position"]), float(row["relative_position"]) ** 2,
                math.log1p(int(row["surface_length"])), math.log1p(int(row["direct_token_count"])),
                float(row["boundary_before"] not in {"", "NONE", "0"}),
                float(row["boundary_after"] not in {"", "NONE", "0"}), math.log1p(count[form]),
                float(j == 0), float(j == m - 1),
            ]
            cv = []
            for h in HORIZONS:
                left = forms[max(0, j - h):j]
                right = forms[j + 1:min(m, j + 1 + h)]
                ls, rs = set(left), set(right)
                lu = len(ls) / max(1, len(left))
                ru = len(rs) / max(1, len(right))
                le = entropy(left) / max(1.0, math.log2(max(2, len(left))))
                re = entropy(right) / max(1.0, math.log2(max(2, len(right))))
                overlap = len(ls & rs) / max(1, min(len(ls), len(rs)))
                cv.extend([
                    lu, ru, ru - lu, le, re, re - le, jaccard(ls, rs), overlap,
                    len([x for x in right if x not in ls]) / max(1, len(right)),
                    float(form in ls), float(form in rs),
                    float(bool(ls & rs) and j > 0 and j + 1 < m),
                    len([x for x in right if x in ls]) / max(1, len(right)),
                ])
            forward_distance = following[0] - j if following else m + 1
            backward_distance = j - previous[-1] if previous else m + 1
            prev_form = forms[j - 1] if j else ""
            next_form = forms[j + 1] if j + 1 < m else ""
            position_values = stat["positions"]
            cv.extend([
                float(j > 0 and j + 1 < m and prev_form == next_form),
                float(bool(previous)), float(bool(following)), math.log1p(forward_distance),
                math.log1p(backward_distance), float(not following),
                math.log1p(domain_edges[record[0]][(prev_form, next_form)]) if prev_form and next_form else 0.0,
                math.log1p(stat["n"]), math.log1p(len(stat["records"])), math.log1p(len(stat["prev"])),
                math.log1p(len(stat["next"])), float(np.std(position_values)),
                float(len(stat["collections"])),
                (len(stat["prev"]) + len(stat["next"])) / max(1, stat["n"]),
                (m - j - 1) / max(1, m),
            ])
            nuisance[idx] = nv
            common[idx] = cv
            record_keys[idx] = record

    name_to_idx = {name: i for i, name in enumerate(common_names)}
    blocks = {
        "GATE_TRANSITION": [],
        "BRANCH_RECONVERGENCE": [],
        "MARKED_INVERSE_DELTA": [],
        "CLOSED_CLASS_BOTTLENECK": [],
    }
    for h in HORIZONS:
        blocks["GATE_TRANSITION"].extend([
            f"H{h}_UNIQUE_DELTA", f"H{h}_ENTROPY_DELTA", f"H{h}_RIGHT_NOVELTY_RATE",
            f"H{h}_PIVOT_RETURN_RIGHT", f"H{h}_RIGHT_TO_LEFT_RETURN",
        ])
        blocks["BRANCH_RECONVERGENCE"].extend([
            f"H{h}_BAG_JACCARD", f"H{h}_BAG_OVERLAP_MIN", f"H{h}_LEFT_RIGHT_RECONVERGENCE",
            f"H{h}_RIGHT_TO_LEFT_RETURN", f"H{h}_RIGHT_NOVELTY_RATE",
        ])
        blocks["MARKED_INVERSE_DELTA"].extend([
            f"H{h}_UNIQUE_DELTA", f"H{h}_ENTROPY_DELTA", f"H{h}_PIVOT_RETURN_LEFT",
            f"H{h}_PIVOT_RETURN_RIGHT", f"H{h}_RIGHT_NOVELTY_RATE",
        ])
        blocks["CLOSED_CLASS_BOTTLENECK"].extend([
            f"H{h}_BAG_JACCARD", f"H{h}_PIVOT_RETURN_LEFT", f"H{h}_PIVOT_RETURN_RIGHT",
            f"H{h}_LEFT_RIGHT_RECONVERGENCE",
        ])
    blocks["GATE_TRANSITION"].extend(["LOG_FORWARD_RETURN_DISTANCE", "NO_FORWARD_RETURN", "DELETE_BRIDGE_LOG_FREQUENCY", "RECORD_REMAINING_FRACTION"])
    blocks["BRANCH_RECONVERGENCE"].extend(["PREV_EQUALS_NEXT", "DELETE_BRIDGE_LOG_FREQUENCY", "LOG_PREV_DIVERSITY", "LOG_NEXT_DIVERSITY"])
    blocks["MARKED_INVERSE_DELTA"].extend(["PREV_EQUALS_NEXT", "DELETE_BRIDGE_LOG_FREQUENCY", "LOG_FORWARD_RETURN_DISTANCE", "LOG_BACKWARD_RETURN_DISTANCE"])
    blocks["CLOSED_CLASS_BOTTLENECK"].extend([
        "LOG_DOMAIN_FORM_FREQUENCY", "LOG_DOMAIN_RECORD_COVERAGE", "LOG_PREV_DIVERSITY",
        "LOG_NEXT_DIVERSITY", "POSITION_STD", "COLLECTION_COVERAGE",
        "NEIGHBOR_DIVERSITY_PER_OCCURRENCE", "LOG_FORWARD_RETURN_DISTANCE", "NO_FORWARD_RETURN",
    ])
    block_indices = {name: [name_to_idx[x] for x in names] for name, names in blocks.items()}
    reduced_indices = {name: [i for i in ids if common_names[i] not in pivot_dependent] for name, ids in block_indices.items()}
    return nuisance, common, nuisance_names, common_names, blocks, block_indices, reduced_indices, record_keys


def transfer_floor(domain_rows: list[dict]) -> float:
    values = sorted((float(row["auc_full"]) for row in domain_rows), reverse=True)
    return values[2] if len(values) >= 3 else float("nan")


def main() -> None:
    design = json.loads(DESIGN.read_text())
    assert design["status"] == "FROZEN_BEFORE_COMPARATOR_BEHAVIOR_SCORING"
    assert design["voynich_target_rows_read"] == 0
    obs = read_tsv(OBS)
    oracle = read_tsv(ORACLE)
    assert [r["element_key"] for r in obs] == [r["element_key"] for r in oracle]
    contract = json.loads(CONTRACT.read_text())
    nuisance, common, nuisance_names, common_names, blocks, block_indices, reduced_indices, _ = build_features(obs)
    domains = np.array([row["domain"] for row in obs])
    fold_rows = []
    prediction_rows = []
    family_predictions = {}

    for family_id, endpoint, block in FAMILIES:
        available = contract["availability"][endpoint]
        y = np.array([int(row[endpoint]) for row in oracle], int)
        full_prediction = np.full(len(obs), np.nan)
        nuisance_prediction = np.full(len(obs), np.nan)
        reduced_prediction = np.full(len(obs), np.nan)
        for held in available:
            train_domains = [domain for domain in available if domain != held]
            train = np.where(np.isin(domains, train_domains))[0]
            test = np.where(domains == held)[0]
            Xn_train = nuisance[train]
            Xn_test = nuisance[test]
            Xf_train = np.column_stack([nuisance[train], common[train][:, block_indices[block]]])
            Xf_test = np.column_stack([nuisance[test], common[test][:, block_indices[block]]])
            Xr_train = np.column_stack([nuisance[train], common[train][:, reduced_indices[block]]])
            Xr_test = np.column_stack([nuisance[test], common[test][:, reduced_indices[block]]])
            train_domain_values = domains[train].tolist()
            pn = predict(fit(Xn_train, y[train], train_domain_values), Xn_test)
            pf = predict(fit(Xf_train, y[train], train_domain_values), Xf_test)
            pr = predict(fit(Xr_train, y[train], train_domain_values), Xr_test)
            nuisance_prediction[test] = pn
            full_prediction[test] = pf
            reduced_prediction[test] = pr
            yy = y[test]
            fold_rows.append({
                "anonymous_family": family_id,
                "held_domain": held,
                "n": len(test),
                "positives": int(yy.sum()),
                "auc_nuisance": f"{auc(yy, pn):.9f}",
                "auc_full": f"{auc(yy, pf):.9f}",
                "auc_without_pivot_recurrence": f"{auc(yy, pr):.9f}",
                "average_precision_full": f"{average_precision(yy, pf):.9f}",
                "prevalence": f"{yy.mean():.9f}",
                "gain_full_vs_nuisance_bits": f"{bits(yy, pn) - bits(yy, pf):.9f}",
                "gain_reduced_vs_nuisance_bits": f"{bits(yy, pn) - bits(yy, pr):.9f}",
                "training_domains": "|".join(train_domains),
            })
            for local, idx in enumerate(test):
                prediction_rows.append({
                    "element_key": obs[idx]["element_key"], "anonymous_family": family_id,
                    "held_domain": held, "oracle_label": int(yy[local]),
                    "nuisance_probability": f"{pn[local]:.9f}",
                    "full_behavior_probability": f"{pf[local]:.9f}",
                    "no_pivot_recurrence_probability": f"{pr[local]:.9f}",
                })
        family_predictions[family_id] = (y, nuisance_prediction, full_prediction, reduced_prediction, available)

    summary_rows = []
    for family_id, endpoint, block in FAMILIES:
        rows = [row for row in fold_rows if row["anonymous_family"] == family_id]
        gains = {row["held_domain"]: float(row["gain_full_vs_nuisance_bits"]) for row in rows}
        aucs = {row["held_domain"]: float(row["auc_full"]) for row in rows}
        reduced_gains = {row["held_domain"]: float(row["gain_reduced_vs_nuisance_bits"]) for row in rows}
        procedural_pass = [domain for domain in PROCEDURAL if aucs.get(domain, 0) >= 0.60 and gains.get(domain, 0) > 0]
        summary_rows.append({
            "anonymous_family": family_id, "behavior_block": block,
            "available_domains": len(rows), "transfer_auc_floor": f"{transfer_floor(rows):.9f}",
            "mean_domain_auc": f"{np.mean(list(aucs.values())):.9f}",
            "positive_gain_domains": sum(value > 0 for value in gains.values()),
            "positive_reduced_gain_domains": sum(value > 0 for value in reduced_gains.values()),
            "pceec2_auc": f"{aucs.get('PCEEC2', float('nan')):.9f}",
            "pceec2_gain_bits": f"{gains.get('PCEEC2', float('nan')):.9f}",
            "procedural_domains_passing": "|".join(sorted(procedural_pass)),
            "domain_aucs_json": json.dumps(aucs, sort_keys=True, separators=(",", ":")),
            "domain_gains_json": json.dumps(gains, sort_keys=True, separators=(",", ":")),
            "domain_reduced_gains_json": json.dumps(reduced_gains, sort_keys=True, separators=(",", ":")),
        })

    # Conditional held-score null: every held score is learned without that
    # domain. Labels are permuted only for evaluation, inside frozen strata.
    strata = defaultdict(list)
    for i, row in enumerate(obs):
        length = int(row["record_element_count"])
        length_bin = "1-8" if length <= 8 else "9-16" if length <= 16 else "17-32" if length <= 32 else "33+"
        position_bin = min(4, int(float(row["relative_position"]) * 5))
        boundary = f"{row['boundary_before']}|{row['boundary_after']}"
        recurrence = int(row["within_record_frequency"])
        recurrence_bin = "1" if recurrence <= 1 else "2" if recurrence == 2 else "3+"
        strata[(row["domain"], row["collection_id"], length_bin, position_bin, boundary, recurrence_bin)].append(i)

    observed_stats = {row["anonymous_family"]: float(row["transfer_auc_floor"]) for row in summary_rows}
    local_nulls = {family_id: [] for family_id, _, _ in FAMILIES}
    null_rows = []
    for world in range(design["null"]["worlds"]):
        rng = np.random.default_rng(design["null"]["seed"] + world)
        perm = np.arange(len(obs))
        for ids in strata.values():
            perm[ids] = rng.permutation(ids)
        world_values = {}
        for family_id, _, _ in FAMILIES:
            y, _, prediction, _, available = family_predictions[family_id]
            yp = y[perm]
            domain_aucs = []
            for held in available:
                ids = np.where(domains == held)[0]
                domain_aucs.append(auc(yp[ids], prediction[ids]))
            value = sorted(domain_aucs, reverse=True)[2]
            local_nulls[family_id].append(value)
            world_values[family_id] = value
        world_max = max(world_values.values())
        null_rows.append({
            "world": world,
            **{family_id: f"{world_values[family_id]:.9f}" for family_id, _, _ in FAMILIES},
            "world_max": f"{world_max:.9f}",
        })

    maxima = [float(row["world_max"]) for row in null_rows]
    eligible = []
    for row in summary_rows:
        family_id = row["anonymous_family"]
        observed = float(row["transfer_auc_floor"])
        local = (1 + sum(value >= observed for value in local_nulls[family_id])) / (1 + len(local_nulls[family_id]))
        maxp = (1 + sum(value >= observed for value in maxima)) / (1 + len(maxima))
        row["local_p"] = f"{local:.9f}"
        row["max_family_p"] = f"{maxp:.9f}"
        procedural_ok = bool(row["procedural_domains_passing"])
        passes = (
            observed >= design["comparator_gate"]["transfer_auc_floor_min"]
            and int(row["positive_gain_domains"]) >= design["comparator_gate"]["positive_gain_domains_min"]
            and float(row["pceec2_auc"]) >= design["comparator_gate"]["pceec2_auc_min"]
            and float(row["pceec2_gain_bits"]) > 0
            and procedural_ok
            and maxp <= design["comparator_gate"]["max_family_p_max"]
            and int(row["positive_reduced_gain_domains"]) >= 3
        )
        row["voynich_mapping_eligible"] = int(passes)
        row["status"] = "IDENTITY_FREE_COMPARATOR_TRANSFER_PASS" if passes else "NO_IDENTITY_FREE_COMPARATOR_TRANSFER"
        if passes:
            eligible.append(family_id)

    feature_rows = []
    for family_id, endpoint, block in FAMILIES:
        for order, feature in enumerate(blocks[block], 1):
            feature_rows.append({
                "anonymous_family": family_id, "behavior_block": block, "feature_ordinal": order,
                "feature": feature, "pivot_recurrence_dependent": int(common_names[block_indices[block][order - 1]] not in {common_names[i] for i in reduced_indices[block]}),
                "exact_identity_value_used": 0, "semantic_state": "UNASSIGNED",
            })

    write_tsv(ART / "gdt380_behavior_feature_manifest.tsv", feature_rows)
    write_tsv(ART / "gdt380_comparator_fold_scores.tsv", fold_rows)
    write_tsv(ART / "gdt380_comparator_predictions.tsv.gz", prediction_rows)
    write_tsv(ART / "gdt380_comparator_family_summary.tsv", summary_rows)
    write_tsv(ART / "gdt380_comparator_null.tsv.gz", null_rows)

    signature = {
        "schema": "GDT380_IDENTITY_FREE_SIGNATURE_FREEZE_V1",
        "status": "TARGET_MAPPING_AUTHORIZED" if eligible else "NO_TARGET_MAPPING_AUTHORIZED",
        "eligible_anonymous_families": eligible,
        "ineligible_anonymous_families": [family_id for family_id, _, _ in FAMILIES if family_id not in eligible],
        "behavior_blocks": {family_id: block for family_id, _, block in FAMILIES},
        "exact_identity_as_feature": False,
        "target_scored": False,
        "target_rows_read": 0,
        "semantic_state": "UNASSIGNED",
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "claim_ceiling": "COMPARATOR_IDENTITY_FREE_BEHAVIOR_TRANSFER_ONLY",
    }
    write_json(ART / "gdt380_identity_free_signature_freeze.json", signature)

    outputs = [
        ART / "gdt380_behavior_feature_manifest.tsv", ART / "gdt380_comparator_fold_scores.tsv",
        ART / "gdt380_comparator_predictions.tsv.gz", ART / "gdt380_comparator_family_summary.tsv",
        ART / "gdt380_comparator_null.tsv.gz", ART / "gdt380_identity_free_signature_freeze.json",
    ]
    result = {
        "schema": "GDT380_COMPARATOR_BEHAVIOR_RESULT_V1",
        "status": "IDENTITY_FREE_COMPARATOR_SIGNATURES_CALIBRATED" if eligible else "NO_IDENTITY_FREE_SIGNATURE_PASSED_COMPARATOR_GATE",
        "rows": len(obs),
        "records": len({(r["domain"], r["collection_id"], r["record_id"]) for r in obs}),
        "families_tested": 4,
        "eligible_anonymous_families": eligible,
        "voynich_target_scored": False,
        "voynich_target_rows_read": 0,
        "f1_used": False,
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [OBS, ORACLE, CONTRACT, DESIGN]},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs},
        "implementation": {str((BASE / "src/run_comparator.py").relative_to(ROOT)): sha(BASE / "src/run_comparator.py")},
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "semantic_state": "UNASSIGNED",
        "claim_ceiling": "COMPARATOR_IDENTITY_FREE_BEHAVIOR_TRANSFER_ONLY",
    }
    write_json(ART / "gdt380_comparator_result.json", result)
    print(json.dumps({"status": result["status"], "eligible": eligible, "rows": len(obs)}))


if __name__ == "__main__":
    main()
