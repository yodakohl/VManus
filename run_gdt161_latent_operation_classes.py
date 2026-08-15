#!/usr/bin/env python3
"""Anonymous latent-class prediction on the frozen GDT160 operation graphs."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import multiprocessing as mp
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from run_gdt003_nested_heldout import discover_operations
from run_gdt160_compatibility_pairing_null import (
    blocks_for,
    fold_seed,
    graph_arrays,
    graph_side,
    score_graph,
    semantic_stats,
)


ROOT = Path(__file__).resolve().parent
DESIGN = ROOT / "gdt161_latent_class_design.json"
METHOD = ROOT / "GDT161_LATENT_OPERATION_CLASS_METHOD.md"
OLD_CORPORA = ROOT / "gdt003_structural_fingerprint_corpora.json.gz"
NEW_CORPORA = ROOT / "gdt159_diplomatic_corpora.json.gz"
GDT160_RESULT = ROOT / "gdt160_result.json"
GDT160_FOLDS = ROOT / "gdt160_fold_decomposition.tsv"
GDT160_PAIRS = ROOT / "gdt160_pair_excess.tsv"
GDT160_WORLDS = ROOT / "gdt160_null_worlds.tsv"
GDT160_DESIGN = ROOT / "gdt160_null_design.json"
CORE = ROOT / "run_gdt003_nested_heldout.py"
GDT160_RUNNER = ROOT / "run_gdt160_compatibility_pairing_null.py"

OUT_GRAPHS = ROOT / "gdt161_fold_graphs.tsv"
OUT_SCORES = ROOT / "gdt161_prediction_scores.tsv"
OUT_CLASSES = ROOT / "gdt161_operation_classes.tsv"
OUT_STABILITY = ROOT / "gdt161_class_stability.tsv"
OUT_SUMMARY = ROOT / "gdt161_comparator_summary.tsv"
OUT_TOP20 = ROOT / "gdt161_top20_concentration_null.tsv"
OUT_COUNTER = ROOT / "gdt161_counterexamples.tsv"
OUT_RESULT = ROOT / "gdt161_result.json"
OUT_REPORT = ROOT / "GDT161_LATENT_OPERATION_CLASS_REPORT.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = []
        for row in rows:
            for field in row:
                if field not in fields:
                    fields.append(field)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def opaque(side: str, operation_id: str) -> str:
    return side + hashlib.sha256(("GDT161|" + operation_id).encode()).hexdigest()[:16]


def bucket(value: str, salt: str, count: int) -> int:
    raw = hashlib.sha256((salt + "|" + value).encode()).digest()
    return int.from_bytes(raw[:8], "big") % count


def load_records(design: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    allowed = {design["target"], *design["comparators"]}
    by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in (OLD_CORPORA, NEW_CORPORA):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for row in json.load(handle)["records"]:
                corpus = str(row["corpus_id"])
                if corpus in allowed:
                    by[corpus].append(row)
    return by


def host_embedding(matrix: np.ndarray, dimensions: int = 32) -> np.ndarray:
    if matrix.size == 0:
        return np.zeros((matrix.shape[0], 1), dtype=float)
    norm = np.linalg.norm(matrix, axis=1, keepdims=True)
    normalized = matrix / np.maximum(norm, 1.0)
    gram = normalized @ normalized.T
    values, vectors = np.linalg.eigh(gram)
    keep = np.argsort(values)[::-1][: min(dimensions, len(values))]
    values = np.maximum(values[keep], 0.0)
    embedded = vectors[:, keep] * np.sqrt(values)[None, :]
    rownorm = np.linalg.norm(embedded, axis=1, keepdims=True)
    return embedded / np.maximum(rownorm, 1e-12)


def kmeans(values: np.ndarray, indices: np.ndarray, k: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    sub = values[indices]
    n = len(sub)
    k = min(k, n)
    if k <= 1:
        return np.zeros(n, dtype=np.int32), np.mean(sub, axis=0, keepdims=True)
    rng = random.Random(seed)
    first = rng.randrange(n)
    centers = [sub[first].copy()]
    distance = np.sum((sub - centers[0]) ** 2, axis=1)
    for _ in range(1, k):
        pick = int(np.argmax(distance + np.arange(n) * 1e-15))
        centers.append(sub[pick].copy())
        distance = np.minimum(distance, np.sum((sub - centers[-1]) ** 2, axis=1))
    centroids = np.asarray(centers)
    labels = np.zeros(n, dtype=np.int32)
    for _ in range(40):
        dist = np.sum((sub[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
        new = np.argmin(dist, axis=1).astype(np.int32)
        counts = np.bincount(new, minlength=k)
        for empty in np.flatnonzero(counts == 0):
            donor = int(np.argmax(np.min(dist, axis=1)))
            new[donor] = int(empty)
            dist[donor, :] = -1.0
        updated = np.vstack([sub[new == c].mean(axis=0) for c in range(k)])
        norm = np.linalg.norm(updated, axis=1, keepdims=True)
        updated = updated / np.maximum(norm, 1e-12)
        if np.array_equal(new, labels):
            labels, centroids = new, updated
            break
        labels, centroids = new, updated
    return labels, centroids


def assign(values: np.ndarray, indices: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    dist = np.sum((values[indices, None, :] - centroids[None, :, :]) ** 2, axis=2)
    return np.argmin(dist, axis=1).astype(np.int32)


def block_probabilities(
    y: np.ndarray, mask: np.ndarray, left: np.ndarray, right: np.ndarray,
    k_left: int, k_right: int, beta: float,
) -> np.ndarray:
    counts = np.zeros((k_left, k_right), dtype=float)
    positives = np.zeros((k_left, k_right), dtype=float)
    rows, cols = np.nonzero(mask)
    np.add.at(counts, (left[rows], right[cols]), 1.0)
    np.add.at(positives, (left[rows], right[cols]), y[rows, cols])
    return (positives + beta) / (counts + 2.0 * beta)


def block_predict(prob: np.ndarray, left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return prob[left[:, None], right[None, :]]


def mdl_bits(
    y: np.ndarray, mask: np.ndarray, prediction: np.ndarray,
    k_left: int, k_right: int, nleft: int, nright: int,
) -> float:
    yy = y[mask]
    pp = np.clip(prediction[mask], 1e-9, 1 - 1e-9)
    likelihood = float(np.sum(-(yy * np.log2(pp) + (1 - yy) * np.log2(1 - pp))))
    cells = max(2, int(mask.sum()))
    assignment = (0.0 if k_left == 1 else nleft * math.log2(k_left))
    assignment += (0.0 if k_right == 1 else nright * math.log2(k_right))
    return likelihood + 0.5 * k_left * k_right * math.log2(cells) + assignment


def ensure_nonempty(labels: np.ndarray, costs: np.ndarray, k: int) -> np.ndarray:
    labels = labels.copy()
    counts = np.bincount(labels, minlength=k)
    for empty in np.flatnonzero(counts == 0):
        candidates = np.argsort(np.min(costs, axis=1))[::-1]
        for candidate in candidates:
            old = int(labels[candidate])
            if counts[old] > 1:
                labels[candidate] = int(empty)
                counts[old] -= 1
                counts[empty] += 1
                break
    return labels


def compatibility_cocluster(
    y: np.ndarray, mask: np.ndarray, left_init: np.ndarray, right_init: np.ndarray,
    k_left: int, k_right: int, beta: float, iterations: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    left, right = left_init.copy(), right_init.copy()
    for _ in range(iterations):
        prob = block_probabilities(y, mask, left, right, k_left, k_right, beta)
        old_left, old_right = left.copy(), right.copy()
        right_onehot = np.eye(k_right)[right]
        left_counts = mask.astype(float) @ right_onehot
        left_positive = (y * mask).astype(float) @ right_onehot
        left_cost = -(left_positive @ np.log(np.clip(prob, 1e-9, 1 - 1e-9)).T
                      + (left_counts - left_positive) @ np.log(np.clip(1 - prob, 1e-9, 1 - 1e-9)).T)
        left = ensure_nonempty(np.argmin(left_cost, axis=1).astype(np.int32), left_cost, k_left)
        prob = block_probabilities(y, mask, left, right, k_left, k_right, beta)
        left_onehot = np.eye(k_left)[left]
        right_counts = mask.astype(float).T @ left_onehot
        right_positive = (y * mask).astype(float).T @ left_onehot
        right_cost = -(right_positive @ np.log(np.clip(prob, 1e-9, 1 - 1e-9))
                       + (right_counts - right_positive) @ np.log(np.clip(1 - prob, 1e-9, 1 - 1e-9)))
        right = ensure_nonempty(np.argmin(right_cost, axis=1).astype(np.int32), right_cost, k_right)
        if np.array_equal(left, old_left) and np.array_equal(right, old_right):
            break
    return left, right, block_probabilities(y, mask, left, right, k_left, k_right, beta)


def pair_features(left_inc: np.ndarray, right_inc: np.ndarray) -> np.ndarray:
    ls = left_inc.sum(axis=1)
    rs = right_inc.sum(axis=1)
    inter = left_inc @ right_inc.T
    union = ls[:, None] + rs[None, :] - inter
    jac = inter / np.maximum(union, 1.0)
    cosine = inter / np.sqrt(np.maximum(ls[:, None] * rs[None, :], 1.0))
    shape = inter.shape
    return np.column_stack([
        np.broadcast_to(np.log1p(ls)[:, None], shape).ravel(),
        np.broadcast_to(np.log1p(rs)[None, :], shape).ravel(),
        np.log1p(inter).ravel(), jac.ravel(), cosine.ravel(),
    ])


def logistic_fit(x: np.ndarray, y: np.ndarray, ridge: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale < 1e-12] = 1.0
    z = (x - mean) / scale
    z = np.column_stack([np.ones(len(z)), z])
    coef = np.zeros(z.shape[1], dtype=float)
    prevalence = (float(y.sum()) + 0.5) / (len(y) + 1.0)
    coef[0] = math.log(prevalence / (1 - prevalence))
    penalty = np.eye(z.shape[1]) * ridge
    penalty[0, 0] = 0.0
    for _ in range(40):
        eta = np.clip(z @ coef, -30, 30)
        p = 1.0 / (1.0 + np.exp(-eta))
        w = np.maximum(p * (1 - p), 1e-8)
        gradient = z.T @ (p - y) + penalty @ coef
        hessian = (z.T * w) @ z + penalty
        step = np.linalg.solve(hessian, gradient)
        coef -= step
        if float(np.max(np.abs(step))) < 1e-8:
            break
    return coef, mean, scale


def logistic_predict(model: tuple[np.ndarray, np.ndarray, np.ndarray], x: np.ndarray) -> np.ndarray:
    coef, mean, scale = model
    z = np.column_stack([np.ones(len(x)), (x - mean) / scale])
    return 1.0 / (1.0 + np.exp(-np.clip(z @ coef, -30, 30)))


def degree_predict(y: np.ndarray, train: np.ndarray) -> np.ndarray:
    global_p = (float(y[train].sum()) + 0.5) / (int(train.sum()) + 1.0)
    row_n = train.sum(axis=1)
    col_n = train.sum(axis=0)
    row_p = (np.sum(y * train, axis=1) + 0.5) / (row_n + 1.0)
    col_p = (np.sum(y * train, axis=0) + 0.5) / (col_n + 1.0)
    logit = lambda p: np.log(np.clip(p, 1e-8, 1 - 1e-8) / np.clip(1 - p, 1e-8, 1 - 1e-8))
    eta = logit(row_p)[:, None] + logit(col_p)[None, :] - logit(global_p)
    return 1.0 / (1.0 + np.exp(-np.clip(eta, -30, 30)))


def average_precision(y: np.ndarray, p: np.ndarray, keys: list[str]) -> float:
    positives = int(y.sum())
    if positives == 0:
        return float("nan")
    order = sorted(range(len(y)), key=lambda i: (-float(p[i]), keys[i]))
    hit = 0
    total = 0.0
    for rank, index in enumerate(order, 1):
        if y[index]:
            hit += 1
            total += hit / rank
    return total / positives


def metrics(y: np.ndarray, p: np.ndarray, keys: list[str]) -> dict[str, Any]:
    p = np.clip(p, 1e-9, 1 - 1e-9)
    loss = float(np.mean(-(y * np.log2(p) + (1 - y) * np.log2(1 - p))))
    positive = int(y.sum())
    order = sorted(range(len(y)), key=lambda i: (-float(p[i]), keys[i]))
    top = order[:positive] if positive else []
    return {
        "cells": len(y), "positives": positive, "prevalence": positive / max(1, len(y)),
        "average_precision": average_precision(y, p, keys), "log_loss_bits_per_cell": loss,
        "brier": float(np.mean((p - y) ** 2)),
        "top_prevalence_matched_precision": sum(int(y[i]) for i in top) / max(1, len(top)),
    }


def graph_for(records: list[dict[str, Any]], held_fold: str) -> dict[str, Any]:
    train = [row for row in records if str(row["fold_id"]) != held_fold]
    freq = Counter(str(row["form"]) for row in train)
    forms = set(freq)
    form_folds: dict[str, set[str]] = defaultdict(set)
    form_units: dict[str, set[str]] = defaultdict(set)
    for row in train:
        form_folds[str(row["form"])].add(str(row["fold_id"]))
        form_units[str(row["form"])].add(str(row["unit_id"]))
    selected, edge_maps = discover_operations(forms, freq, form_folds)
    left_ops = [row for row in selected if str(row["operation"] [0]).startswith("PREFIX")]
    right_ops = [row for row in selected if str(row["operation"] [0]).startswith("SUFFIX")]
    left_graph, right_graph = graph_side(left_ops, edge_maps), graph_side(right_ops, edge_maps)
    arrays = graph_arrays(left_graph, right_graph)
    labels = np.asarray([edge[2] for edge in right_graph["edges"]], dtype=np.int32)
    eligible_count, eligible, triplets, complete = score_graph(arrays, labels, len(left_ops), len(right_ops))
    y = eligible.reshape((len(left_ops), len(right_ops))).astype(np.int8)
    hosts = sorted({source for source, _, _ in left_graph["edges"]} | {source for source, _, _ in right_graph["edges"]})
    host_index = {host: index for index, host in enumerate(hosts)}
    left_inc = np.zeros((len(left_ops), len(hosts)), dtype=float)
    right_inc = np.zeros((len(right_ops), len(hosts)), dtype=float)
    for source, _, label in left_graph["edges"]:
        left_inc[int(label), host_index[source]] = 1.0
    for source, _, label in right_graph["edges"]:
        right_inc[int(label), host_index[source]] = 1.0
    left_ids = [opaque("L", str(row["operation_id"])) for row in left_ops]
    right_ids = [opaque("R", str(row["operation_id"])) for row in right_ops]
    return {
        "held_fold": held_fold, "freq": freq, "forms": forms, "form_folds": form_folds,
        "form_units": form_units, "left_ops": left_ops, "right_ops": right_ops,
        "left_graph": left_graph, "right_graph": right_graph, "arrays": arrays,
        "selected": selected, "edge_maps": edge_maps,
        "labels": labels, "y": y, "triplets": triplets.reshape(y.shape),
        "complete": complete.reshape(y.shape), "eligible_count": eligible_count,
        "left_inc": left_inc, "right_inc": right_inc, "left_ids": left_ids, "right_ids": right_ids,
    }


def select_host_block(
    y: np.ndarray, mask: np.ndarray, left_embedding: np.ndarray, right_embedding: np.ndarray,
    left_indices: np.ndarray, right_indices: np.ndarray, k_grid: list[int], beta: float, seed: int,
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    left_cache = {k: kmeans(left_embedding, left_indices, k, seed + 101 * k)
                  for k in k_grid if k <= len(left_indices)}
    right_cache = {k: kmeans(right_embedding, right_indices, k, seed + 211 * k)
                   for k in k_grid if k <= len(right_indices)}
    sub_y = y[np.ix_(left_indices, right_indices)]
    sub_mask = mask[np.ix_(left_indices, right_indices)]
    for k_left, (left_label, left_centroid) in left_cache.items():
        for k_right, (right_label, right_centroid) in right_cache.items():
            prob = block_probabilities(sub_y, sub_mask, left_label, right_label, k_left, k_right, beta)
            pred = block_predict(prob, left_label, right_label)
            mdl = mdl_bits(sub_y, sub_mask, pred, k_left, k_right, len(left_indices), len(right_indices))
            value = {"k_left": k_left, "k_right": k_right, "left_label": left_label, "right_label": right_label,
                     "left_centroid": left_centroid, "right_centroid": right_centroid,
                     "prob": prob, "mdl": mdl}
            if best is None or (mdl, k_left * k_right, k_left, k_right) < (
                best["mdl"], best["k_left"] * best["k_right"], best["k_left"], best["k_right"]
            ):
                best = value
    if best is None:
        raise RuntimeError("no host block capacity")
    return best


def evaluate_graph(corpus: str, graph: dict[str, Any], design: dict[str, Any]) -> dict[str, Any]:
    y = graph["y"]
    nleft, nright = y.shape
    beta = float(design["block_beta_prior"])
    k_grid = [int(k) for k in design["k_grid"]]
    seed = int.from_bytes(hashlib.sha256(f"{design['seed']}|{corpus}|{graph['held_fold']}".encode()).digest()[:8], "big")
    le, re = host_embedding(graph["left_inc"]), host_embedding(graph["right_inc"])
    features = pair_features(graph["left_inc"], graph["right_inc"])
    pair_keys = [f"{left}|{right}" for left in graph["left_ids"] for right in graph["right_ids"]]
    flat_y = y.ravel().astype(float)

    pair_predictions = {name: np.zeros(len(flat_y), dtype=float) for name in
                        ("GLOBAL", "HOST_PROFILE_LOGIT", "DEGREE_LOGIT", "HOST_BLOCK", "COMPAT_BLOCK")}
    selected_pair: dict[str, list[tuple[int, int]]] = {"HOST_BLOCK": [], "COMPAT_BLOCK": []}
    pair_partition = np.asarray([bucket(key, f"PAIR|{seed}", int(design["pair_cell_folds"])) for key in pair_keys])
    full_indices_l = np.arange(nleft)
    full_indices_r = np.arange(nright)
    left_cluster_cache: dict[int, np.ndarray] = {}
    right_cluster_cache: dict[int, np.ndarray] = {}
    for k in k_grid:
        if k <= nleft:
            left_cluster_cache[k] = kmeans(le, full_indices_l, k, seed + 101 * k)[0]
        if k <= nright:
            right_cluster_cache[k] = kmeans(re, full_indices_r, k, seed + 211 * k)[0]
    for outer in range(int(design["pair_cell_folds"])):
        test_flat = pair_partition == outer
        train_flat = ~test_flat
        train = train_flat.reshape(y.shape)
        test = test_flat.reshape(y.shape)
        global_p = (float(flat_y[train_flat].sum()) + beta) / (int(train_flat.sum()) + 2 * beta)
        pair_predictions["GLOBAL"][test_flat] = global_p
        logit = logistic_fit(features[train_flat], flat_y[train_flat], float(design["logistic_ridge"]))
        pair_predictions["HOST_PROFILE_LOGIT"][test_flat] = logistic_predict(logit, features[test_flat])
        pair_predictions["DEGREE_LOGIT"][test_flat] = degree_predict(y, train)[test]
        host_best = None
        compat_best = None
        for k_left, li in left_cluster_cache.items():
            for k_right, ri in right_cluster_cache.items():
                prob = block_probabilities(y, train, li, ri, k_left, k_right, beta)
                prediction = block_predict(prob, li, ri)
                mdl = mdl_bits(y, train, prediction, k_left, k_right, nleft, nright)
                key = (mdl, k_left * k_right, k_left, k_right)
                if host_best is None or key < host_best[:4]:
                    host_best = (mdl, k_left * k_right, k_left, k_right, prediction)
                cli, cri, cprob = compatibility_cocluster(
                    y, train, li, ri, k_left, k_right, beta, int(design["coclustering_iterations"])
                )
                cpred = block_predict(cprob, cli, cri)
                cmdl = mdl_bits(y, train, cpred, k_left, k_right, nleft, nright)
                ckey = (cmdl, k_left * k_right, k_left, k_right)
                if compat_best is None or ckey < compat_best[:4]:
                    compat_best = (cmdl, k_left * k_right, k_left, k_right, cpred)
        assert host_best is not None and compat_best is not None
        pair_predictions["HOST_BLOCK"][test_flat] = host_best[4].ravel()[test_flat]
        pair_predictions["COMPAT_BLOCK"][test_flat] = compat_best[4].ravel()[test_flat]
        selected_pair["HOST_BLOCK"].append((host_best[2], host_best[3]))
        selected_pair["COMPAT_BLOCK"].append((compat_best[2], compat_best[3]))

    node_predictions = {name: np.zeros(len(flat_y), dtype=float) for name in ("GLOBAL", "HOST_PROFILE_LOGIT", "HOST_BLOCK")}
    selected_node: list[tuple[int, int]] = []
    left_bucket = np.asarray([bucket(value, f"NODEL|{seed}", int(design["operation_folds_per_side"])) for value in graph["left_ids"]])
    right_bucket = np.asarray([bucket(value, f"NODER|{seed}", int(design["operation_folds_per_side"])) for value in graph["right_ids"]])
    for lb in range(int(design["operation_folds_per_side"])):
        held_l = np.flatnonzero(left_bucket == lb)
        train_l = np.flatnonzero(left_bucket != lb)
        for rb in range(int(design["operation_folds_per_side"])):
            held_r = np.flatnonzero(right_bucket == rb)
            train_r = np.flatnonzero(right_bucket != rb)
            if not len(held_l) or not len(held_r):
                continue
            train_y = y[np.ix_(train_l, train_r)]
            global_p = (float(train_y.sum()) + beta) / (train_y.size + 2 * beta)
            held_positions = (held_l[:, None] * nright + held_r[None, :]).ravel()
            node_predictions["GLOBAL"][held_positions] = global_p
            train_positions = (train_l[:, None] * nright + train_r[None, :]).ravel()
            model = logistic_fit(features[train_positions], flat_y[train_positions], float(design["logistic_ridge"]))
            node_predictions["HOST_PROFILE_LOGIT"][held_positions] = logistic_predict(model, features[held_positions])
            train_mask = np.ones(train_y.shape, dtype=bool)
            best = select_host_block(y, np.ones_like(y, dtype=bool), le, re, train_l, train_r, k_grid, beta, seed + lb * 1009 + rb * 9173)
            held_left_label = assign(le, held_l, best["left_centroid"])
            held_right_label = assign(re, held_r, best["right_centroid"])
            node_predictions["HOST_BLOCK"][held_positions] = best["prob"][held_left_label[:, None], held_right_label[None, :]].ravel()
            selected_node.append((int(best["k_left"]), int(best["k_right"])))

    score_rows: list[dict[str, Any]] = []
    for evaluation, predictions, selected in (
        ("MASKED_PAIR_CELL", pair_predictions, selected_pair),
        ("BOTH_OPERATIONS_UNSEEN", node_predictions, {"HOST_BLOCK": selected_node}),
    ):
        for model_name, prediction in predictions.items():
            m = metrics(flat_y, prediction, pair_keys)
            ks = selected.get(model_name, [])
            left_ks = [value[0] for value in ks]
            right_ks = [value[1] for value in ks]
            score_rows.append({
                "corpus_id": corpus, "held_fold": graph["held_fold"], "evaluation": evaluation,
                "model": model_name, **m,
                "selected_k_left_median": statistics.median(left_ks) if ks else "NA",
                "selected_k_left_min": min(left_ks) if ks else "NA", "selected_k_left_max": max(left_ks) if ks else "NA",
                "selected_k_right_median": statistics.median(right_ks) if ks else "NA",
                "selected_k_right_min": min(right_ks) if ks else "NA", "selected_k_right_max": max(right_ks) if ks else "NA",
            })

    full_mask = np.ones_like(y, dtype=bool)
    full_best = select_host_block(y, full_mask, le, re, full_indices_l, full_indices_r, k_grid, beta, seed)
    k_left, k_right = int(full_best["k_left"]), int(full_best["k_right"])
    left_labels, right_labels = full_best["left_label"], full_best["right_label"]
    full_prediction = block_predict(full_best["prob"], left_labels, right_labels)
    global_p = (float(y.sum()) + beta) / (y.size + 2 * beta)
    global_pred = np.full_like(y, global_p, dtype=float)
    graph_row = {
        "corpus_id": corpus, "held_fold": graph["held_fold"], "left_operations": nleft, "right_operations": nright,
        "pair_cells": y.size, "compatible_cells": int(y.sum()), "compatible_density": float(y.mean()),
        "selected_k_left_full_descriptive": k_left, "selected_k_right_full_descriptive": k_right,
        "left_min_class_size": int(np.bincount(left_labels, minlength=k_left).min()),
        "right_min_class_size": int(np.bincount(right_labels, minlength=k_right).min()),
        "block_mdl_bits": full_best["mdl"],
        "in_sample_block_gain_bits": mdl_bits(y, full_mask, global_pred, 1, 1, nleft, nright) - full_best["mdl"],
        "occupied_positive_blocks": int(sum(np.any(y[np.ix_(left_labels == a, right_labels == b)])
                                            for a in range(k_left) for b in range(k_right))),
        "blocks": k_left * k_right,
    }
    class_rows = []
    for side_name, ids, labels, inc in (
        ("LEFT", graph["left_ids"], left_labels, graph["left_inc"]),
        ("RIGHT", graph["right_ids"], right_labels, graph["right_inc"]),
    ):
        selected_k = k_left if side_name == "LEFT" else k_right
        sizes = np.bincount(labels, minlength=selected_k)
        for op_id, label, support in zip(ids, labels, inc.sum(axis=1), strict=True):
            class_rows.append({
                "corpus_id": corpus, "held_fold": graph["held_fold"], "side": side_name,
                "opaque_operation_id": op_id, "class_id": f"{side_name[0]}C{int(label)+1:02d}",
                "selected_k": selected_k, "class_size": int(sizes[int(label)]), "anonymous_host_support": int(support),
            })
    return {"scores": score_rows, "graph": graph_row, "classes": class_rows}


def coassignment_jaccard(first: dict[str, str], second: dict[str, str]) -> tuple[int, float]:
    common = sorted(set(first) & set(second))
    intersection = union = 0
    for i, left in enumerate(common):
        for right in common[i + 1:]:
            a = first[left] == first[right]
            b = second[left] == second[right]
            intersection += int(a and b)
            union += int(a or b)
    return len(common), intersection / union if union else 1.0


def corpus_worker(payload: tuple[str, list[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    corpus, records, design = payload
    graph_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    class_rows: list[dict[str, Any]] = []
    for held in sorted({str(row["fold_id"]) for row in records}):
        graph = graph_for(records, held)
        if len(graph["left_ops"]) < 4 or len(graph["right_ops"]) < 4:
            graph_rows.append({"corpus_id": corpus, "held_fold": held, "status": "INSUFFICIENT_CLASS_CAPACITY",
                               "left_operations": len(graph["left_ops"]), "right_operations": len(graph["right_ops"])})
            continue
        value = evaluate_graph(corpus, graph, design)
        graph_rows.append({"status": "SCORED", **value["graph"]})
        score_rows.extend(value["scores"])
        class_rows.extend(value["classes"])
    stability_rows: list[dict[str, Any]] = []
    for side_name in ("LEFT", "RIGHT"):
        maps: dict[str, dict[str, str]] = defaultdict(dict)
        for row in class_rows:
            if row["side"] == side_name:
                maps[str(row["held_fold"])][str(row["opaque_operation_id"])] = str(row["class_id"])
        for first, second in __import__("itertools").combinations(sorted(maps), 2):
            count, value = coassignment_jaccard(maps[first], maps[second])
            stability_rows.append({"corpus_id": corpus, "side": side_name, "fold_a": first, "fold_b": second,
                                   "common_operations": count, "coassignment_jaccard": value})
    return {"corpus": corpus, "graphs": graph_rows, "scores": score_rows, "classes": class_rows, "stability": stability_rows}


def aggregate_summaries(score_rows: list[dict[str, Any]], graph_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in score_rows:
        grouped[(str(row["corpus_id"]), str(row["evaluation"]), str(row["model"]))].append(row)
    summaries: list[dict[str, Any]] = []
    for (corpus, evaluation, model), rows in sorted(grouped.items()):
        total = sum(int(row["cells"]) for row in rows)
        weight = lambda field: sum(int(row["cells"]) * float(row[field]) for row in rows) / max(1, total)
        summaries.append({
            "corpus_id": corpus, "evaluation": evaluation, "model": model,
            "graph_folds": len(rows), "cells": total, "positives": sum(int(row["positives"]) for row in rows),
            "mean_average_precision": statistics.fmean(float(row["average_precision"]) for row in rows),
            "weighted_log_loss_bits_per_cell": weight("log_loss_bits_per_cell"),
            "weighted_brier": weight("brier"),
            "weighted_top_prevalence_precision": weight("top_prevalence_matched_precision"),
            "selected_k_left_median_across_graphs": statistics.median(
                float(row["selected_k_left_median"]) for row in rows if row["selected_k_left_median"] != "NA"
            ) if any(row["selected_k_left_median"] != "NA" for row in rows) else "NA",
            "selected_k_right_median_across_graphs": statistics.median(
                float(row["selected_k_right_median"]) for row in rows if row["selected_k_right_median"] != "NA"
            ) if any(row["selected_k_right_median"] != "NA" for row in rows) else "NA",
        })
    lookup = {(row["corpus_id"], row["evaluation"], row["model"]): row for row in summaries}
    for row in summaries:
        base_name = "HOST_PROFILE_LOGIT" if row["model"] in {"HOST_BLOCK", "COMPAT_BLOCK"} else "GLOBAL"
        base = lookup.get((row["corpus_id"], row["evaluation"], base_name))
        row["gain_bits_per_cell_over_named_baseline"] = (
            float(base["weighted_log_loss_bits_per_cell"]) - float(row["weighted_log_loss_bits_per_cell"])
            if base else "NA"
        )
        row["ap_gain_over_named_baseline"] = (
            float(row["mean_average_precision"]) - float(base["mean_average_precision"]) if base else "NA"
        )
        row["named_baseline"] = base_name if base else "NA"
        if row["model"] in {"HOST_BLOCK", "COMPAT_BLOCK"} and base:
            model_folds = {(r["corpus_id"], r["held_fold"], r["evaluation"]): r for r in score_rows if r["model"] == row["model"]}
            base_folds = {(r["corpus_id"], r["held_fold"], r["evaluation"]): r for r in score_rows if r["model"] == base_name}
            row["positive_graph_fold_directions"] = sum(
                float(value["log_loss_bits_per_cell"]) < float(base_folds[key]["log_loss_bits_per_cell"])
                for key, value in model_folds.items() if key in base_folds and key[0] == row["corpus_id"] and key[2] == row["evaluation"]
            )
        else:
            row["positive_graph_fold_directions"] = "NA"
    return summaries


def top20_null(records: list[dict[str, Any]], design: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    worlds = int(design["top20_null_worlds"])
    graphs = [graph_for(records, held) for held in sorted({str(row["fold_id"]) for row in records})]
    universe = sorted({(l, r) for graph in graphs for l in graph["left_ids"] for r in graph["right_ids"]})
    index = {key: i for i, key in enumerate(universe)}
    observed = np.zeros(len(universe), dtype=np.uint8)
    matrix = np.zeros((worlds, len(universe)), dtype=np.uint8)
    atlas_observed = np.zeros(len(universe), dtype=np.uint8)
    atlas_matrix = np.zeros((worlds, len(universe)), dtype=np.uint8)
    world_totals = np.zeros(worlds, dtype=np.int64)
    gdt160_design = json.loads(GDT160_DESIGN.read_text(encoding="utf-8"))

    for graph in graphs:
        labels = graph["labels"].copy()
        blocks, switchable = blocks_for(graph["right_graph"], graph["freq"], graph["form_folds"], graph["form_units"], False)
        weights = [len(block) * (len(block) - 1) for block in blocks]
        cumulative = np.cumsum(weights)
        rng = random.Random(fold_seed(int(gdt160_design["seed"]), design["target"], graph["held_fold"], design["top20_null"]))
        source_sets: dict[str, set[int]] = defaultdict(set)
        for source, _, label in graph["right_graph"]["edges"]:
            source_sets[source].add(label)

        def switches(number: int) -> None:
            for _ in range(number):
                pick = rng.randrange(int(cumulative[-1]))
                block = blocks[int(np.searchsorted(cumulative, pick, side="right"))]
                first, second = rng.sample(block, 2)
                source_a = graph["right_graph"]["edges"][first][0]
                source_b = graph["right_graph"]["edges"][second][0]
                label_a, label_b = int(labels[first]), int(labels[second])
                if source_a == source_b or label_a == label_b:
                    continue
                if label_b in source_sets[source_a] or label_a in source_sets[source_b]:
                    continue
                source_sets[source_a].remove(label_a); source_sets[source_b].remove(label_b)
                source_sets[source_a].add(label_b); source_sets[source_b].add(label_a)
                labels[first], labels[second] = label_b, label_a

        switches(20 * switchable)
        global_indices = np.asarray([index[(l, r)] for l in graph["left_ids"] for r in graph["right_ids"]], dtype=np.int32)
        initial_labels = np.asarray([edge[2] for edge in graph["right_graph"]["edges"]], dtype=np.int32)
        _, initial, _, _ = score_graph(graph["arrays"], initial_labels, len(graph["left_ops"]), len(graph["right_ops"]))
        observed[global_indices] += initial.astype(np.uint8)
        _, semantic_pairs = semantic_stats(graph["forms"], graph["selected"], graph["edge_maps"])
        atlas_local = initial.copy()
        for local_index, (left_id, right_id) in enumerate(
            (pair for pair in ((l, r) for l in graph["left_ids"] for r in graph["right_ids"]))
        ):
            # semantic_stats uses literal IDs; recover them by aligned operation order.
            li, ri = divmod(local_index, len(graph["right_ids"]))
            literal = (str(graph["left_ops"][li]["operation_id"]), str(graph["right_ops"][ri]["operation_id"]))
            if literal in semantic_pairs:
                atlas_local[local_index] = True
        atlas_selected_indices = global_indices[atlas_local]
        atlas_observed[atlas_selected_indices] += initial[atlas_local].astype(np.uint8)
        for world in range(worlds):
            switches(switchable)
            count, eligible, _, _ = score_graph(graph["arrays"], labels, len(graph["left_ops"]), len(graph["right_ops"]))
            matrix[world, global_indices] += eligible.astype(np.uint8)
            atlas_matrix[world, atlas_selected_indices] += eligible[atlas_local].astype(np.uint8)
            world_totals[world] += count

    published_worlds = []
    with GDT160_WORLDS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["corpus_id"] == design["target"] and row["null"] == design["top20_null"]:
                published_worlds.append(int(row["null_eligible_pairs"]))
    if world_totals.tolist() != published_worlds:
        raise RuntimeError("pair-level rerun does not reproduce GDT160 world totals")

    expected = matrix.mean(axis=0)
    atlas_pairs = set()
    with GDT160_PAIRS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            atlas_pairs.add((opaque("L", row["left_operation"]), opaque("R", row["right_operation"])))
    scopes = {
        "FULL_PAIR_UNIVERSE": (np.ones(len(universe), dtype=bool), observed, matrix),
        "FROZEN_GDT160_ATLAS_SCOPE": (
            np.asarray([key in atlas_pairs for key in universe], dtype=bool), atlas_observed, atlas_matrix
        ),
    }
    rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    for scope, (scope_mask, scope_observed, scope_matrix) in scopes.items():
        scope_expected = scope_matrix.mean(axis=0)
        total_world = scope_matrix.sum(axis=0).astype(float)
        obs_excess = np.maximum(scope_observed.astype(float) - scope_expected, 0.0)[scope_mask]
        observed_fraction = float(np.sort(obs_excess)[-20:].sum() / max(1e-12, obs_excess.sum()))
        values = []
        for world in range(worlds):
            loo = (total_world - scope_matrix[world]) / (worlds - 1)
            excess = np.maximum(scope_matrix[world].astype(float) - loo, 0.0)[scope_mask]
            fraction = float(np.sort(excess)[-20:].sum() / max(1e-12, excess.sum()))
            values.append(fraction)
            rows.append({
                "scope": scope, "world": world + 1,
                "null_eligible_pair_folds": int(scope_matrix[world].sum()),
                "positive_excess_sum": float(excess.sum()),
                "top20_positive_excess_fraction": fraction,
            })
        summary[scope] = {
            "pairs": int(scope_mask.sum()), "observed_top20_fraction": observed_fraction,
            "null_mean": statistics.fmean(values), "null_ci025": float(np.quantile(values, 0.025)),
            "null_ci975": float(np.quantile(values, 0.975)),
            "p_at_least_observed_concentration": (1 + sum(value >= observed_fraction for value in values)) / (worlds + 1),
            "p_at_most_observed_concentration": (1 + sum(value <= observed_fraction for value in values)) / (worlds + 1),
        }
    published = json.loads(GDT160_RESULT.read_text(encoding="utf-8"))["pair_excess"]["top20_fraction_positive_excess"]
    if abs(summary["FROZEN_GDT160_ATLAS_SCOPE"]["observed_top20_fraction"] - float(published)) > 1e-12:
        raise RuntimeError(
            "GDT160 atlas concentration not reproduced: "
            f"new={summary['FROZEN_GDT160_ATLAS_SCOPE']['observed_top20_fraction']!r} published={published!r}"
        )
    return rows, summary


def main() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    for name, expected in design["inputs"].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError(f"input hash mismatch: {name}")
    records = load_records(design)
    tasks = [(corpus, records[corpus], design) for corpus in [design["target"], *design["comparators"]]]
    with mp.Pool(processes=min(6, len(tasks))) as pool:
        results = pool.map(corpus_worker, tasks)
    graph_rows = [row for result in results for row in result["graphs"]]
    score_rows = [row for result in results for row in result["scores"]]
    class_rows = [row for result in results for row in result["classes"]]
    stability_rows = [row for result in results for row in result["stability"]]
    summary_rows = aggregate_summaries(score_rows, graph_rows)
    top20_rows, top20_summary = top20_null(records[design["target"]], design)

    lookup = {(row["corpus_id"], row["evaluation"], row["model"]): row for row in summary_rows}
    target_node = lookup[(design["target"], "BOTH_OPERATIONS_UNSEEN", "HOST_BLOCK")]
    target_node_base = lookup[(design["target"], "BOTH_OPERATIONS_UNSEEN", "HOST_PROFILE_LOGIT")]
    target_pair = lookup[(design["target"], "MASKED_PAIR_CELL", "COMPAT_BLOCK")]
    target_pair_base = lookup[(design["target"], "MASKED_PAIR_CELL", "HOST_PROFILE_LOGIT")]
    node_gain = float(target_node_base["weighted_log_loss_bits_per_cell"]) - float(target_node["weighted_log_loss_bits_per_cell"])
    pair_gain = float(target_pair_base["weighted_log_loss_bits_per_cell"]) - float(target_pair["weighted_log_loss_bits_per_cell"])
    node_ap_gain = float(target_node["mean_average_precision"]) - float(target_node_base["mean_average_precision"])
    median_k_left = float(target_node["selected_k_left_median_across_graphs"])
    median_k_right = float(target_node["selected_k_right_median_across_graphs"])
    positive = int(target_node["positive_graph_fold_directions"])
    survival = node_gain / pair_gain if pair_gain > 0 else None
    if max(median_k_left, median_k_right) <= 16 and node_gain > 0 and node_ap_gain > 0 and positive >= 9 and pair_gain > 0 and survival >= 0.5:
        status = "COMPACT_FACTORIAL_OPERATION_CLASSES_SUPPORTED"
    elif pair_gain > 0 and node_gain <= 0:
        status = "PAIR_COMPATIBILITY_COMPRESSIBLE_BUT_NOT_NEW_OPERATION_TRANSFERABLE"
    elif node_gain <= 0 and node_ap_gain <= 0:
        status = "LATENT_CLASSES_NOT_ABOVE_HOST_DEGREE_BASELINES"
    else:
        status = "LATENT_CLASSES_NOT_ABOVE_HOST_DEGREE_BASELINES"

    counter_rows = [
        {"claim": "GLYPH_IDENTITY_DRIVES_CLASSES", "evidence": "Model matrices contain only anonymous host incidence and masked compatibility; operation literals and family subtypes are forbidden.", "impact": "Any class effect is graph-distributional."},
        {"claim": "MASKED_CELL_GAIN_PROVES_TRANSFER", "evidence": "COMPAT_BLOCK sees each endpoint's other compatibility cells.", "impact": "Only BOTH_OPERATIONS_UNSEEN tests new-operation transfer."},
        {"claim": "HOST_BLOCK_BEATS_STRING_BASELINES", "evidence": "No characters enter this test; HOST_PROFILE_LOGIT is the matched support-profile baseline.", "impact": "The result concerns compatibility graph compression, not text likelihood."},
        {"claim": "LATIN_DIFFERENCE_IDENTIFIES_LANGUAGE", "evidence": "Comparator corpora differ in genre, capacity, and diplomatic practice.", "impact": "Cross-corpus values calibrate architecture only."},
        {"claim": "TOP20_NULL_IS_UNSELECTED", "evidence": "The atlas-scope null conditions on GDT160's observed-selected 4,309-row library; full-universe output is the selection-free sensitivity.", "impact": "Both scopes must be reported."},
        {"claim": "F84R_USED", "evidence": "Only frozen corpus bundles and GDT160 artifacts are inputs; frozen GDT003 provenance excludes f84r.", "impact": "f84r remains sealed."},
    ]

    target_stability = {}
    for side_name in ("LEFT", "RIGHT"):
        values = [float(row["coassignment_jaccard"]) for row in stability_rows
                  if row["corpus_id"] == design["target"] and row["side"] == side_name]
        target_stability[side_name] = {
            "comparisons": len(values), "mean_coassignment_jaccard": statistics.fmean(values),
            "median_coassignment_jaccard": statistics.median(values), "minimum": min(values), "maximum": max(values),
        }
    target_full_graphs = [row for row in graph_rows if row.get("corpus_id") == design["target"] and row.get("status") == "SCORED"]
    target_multiclass_graphs = sum(
        int(row["selected_k_left_full_descriptive"]) * int(row["selected_k_right_full_descriptive"]) > 1
        for row in target_full_graphs
    )
    external_full_graphs = [row for row in graph_rows if row.get("corpus_id") != design["target"] and row.get("status") == "SCORED"]
    external_multiclass_graphs = sum(
        int(row["selected_k_left_full_descriptive"]) * int(row["selected_k_right_full_descriptive"]) > 1
        for row in external_full_graphs
    )

    write_tsv(OUT_GRAPHS, graph_rows)
    write_tsv(OUT_SCORES, score_rows)
    write_tsv(OUT_CLASSES, class_rows)
    write_tsv(OUT_STABILITY, stability_rows)
    write_tsv(OUT_SUMMARY, summary_rows)
    write_tsv(OUT_TOP20, top20_rows)
    write_tsv(OUT_COUNTER, counter_rows)

    compare_lines = []
    for corpus in [design["target"], *design["comparators"]]:
        if (corpus, "BOTH_OPERATIONS_UNSEEN", "HOST_BLOCK") not in lookup:
            compare_lines.append(f"| {corpus} | INSUFFICIENT | | | | |")
            continue
        node = lookup[(corpus, "BOTH_OPERATIONS_UNSEEN", "HOST_BLOCK")]
        base = lookup[(corpus, "BOTH_OPERATIONS_UNSEEN", "HOST_PROFILE_LOGIT")]
        cell = lookup[(corpus, "MASKED_PAIR_CELL", "COMPAT_BLOCK")]
        cellbase = lookup[(corpus, "MASKED_PAIR_CELL", "HOST_PROFILE_LOGIT")]
        compare_lines.append(
            f"| {corpus} | {float(node['selected_k_left_median_across_graphs']):.1f}×{float(node['selected_k_right_median_across_graphs']):.1f} | "
            f"{float(base['weighted_log_loss_bits_per_cell'])-float(node['weighted_log_loss_bits_per_cell']):+.6f} | "
            f"{float(node['mean_average_precision'])-float(base['mean_average_precision']):+.6f} | "
            f"{node['positive_graph_fold_directions']}/{node['graph_folds']} | "
            f"{float(cellbase['weighted_log_loss_bits_per_cell'])-float(cell['weighted_log_loss_bits_per_cell']):+.6f} |"
        )

    survival_text = f"{survival:.3f}" if survival is not None else "not defined because masked-cell gain is nonpositive"
    report = f"""# GDT161 latent operation-class report

Decision: **{status}**.

## Predictive compression

| corpus | median LEFT×RIGHT K | both-unseen gain vs host baseline (bits/cell) | both-unseen AP gain | positive graph folds | masked-cell COMPAT gain |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(compare_lines)}

Voynich's anonymous HOST_BLOCK has both-operations-unseen gain
{node_gain:+.6f} bits/cell and AP gain {node_ap_gain:+.6f} over the matched
HOST_PROFILE_LOGIT baseline, with positive direction on {positive}/12
pre-existing GDT003 folds.  Its median selected class inventory is
{median_k_left:.1f}×{median_k_right:.1f}.  The
masked-cell compatibility-profile upper bound gains {pair_gain:+.6f}
bits/cell; the both-unseen fraction of that gain is
{survival_text}.

The full-graph descriptive MDL fits choose more than one class on
{target_multiclass_graphs}/12 Voynich folds and
{external_multiclass_graphs}/{len(external_full_graphs)} powered comparator
folds.  Where Voynich
does choose multiple descriptive classes, cross-fold coassignment is unstable:
median Jaccard is {target_stability['LEFT']['median_coassignment_jaccard']:.3f}
for LEFT and {target_stability['RIGHT']['median_coassignment_jaccard']:.3f} for
RIGHT.  Thus the large excess is well ranked by continuous anonymous host
overlap, but it does not collapse into a stable small categorical inventory
under this fixed class family.

The masked-cell result answers whether the already-observed compatibility
matrix is block-compressible.  The both-unseen result is the decisive test of
whether anonymous host-support profiles assign entirely new LEFT and RIGHT
operations to reusable classes.  Operation spellings, glyphs, edit strings,
and family subtype were not model features.

## Top-20 excess concentration

On the exact frozen GDT160 4,309-pair atlas, the observed top-20 share is
{top20_summary['FROZEN_GDT160_ATLAS_SCOPE']['observed_top20_fraction']:.6f}.
Its leave-one-world-out degree-null mean is
{top20_summary['FROZEN_GDT160_ATLAS_SCOPE']['null_mean']:.6f}
(95% interval {top20_summary['FROZEN_GDT160_ATLAS_SCOPE']['null_ci025']:.6f}–
{top20_summary['FROZEN_GDT160_ATLAS_SCOPE']['null_ci975']:.6f}); the inclusive
lower-tail/diffuseness p is
{top20_summary['FROZEN_GDT160_ATLAS_SCOPE']['p_at_most_observed_concentration']:.6f}.
The full pair-universe observed share is
{top20_summary['FULL_PAIR_UNIVERSE']['observed_top20_fraction']:.6f}, with null
mean {top20_summary['FULL_PAIR_UNIVERSE']['null_mean']:.6f} and lower-tail p
{top20_summary['FULL_PAIR_UNIVERSE']['p_at_most_observed_concentration']:.6f}.

The atlas-scope result conditions on the already selected GDT160 library; the
full-universe sensitivity removes that selection.  Neither gives individual
operation pairs confirmatory status.

## Interpretation

GDT160's 31.8× absolute excess is therefore evaluated here as a prediction
problem, not merely redescribed as a dense graph.  A compact factorial reading
requires the host-derived class model to transfer to pairs whose two operations
were absent from compatibility training.  A gain confined to COMPAT_BLOCK means
the exposed matrix has local communities but does not establish a reusable
operation algebra.

## Claim ceiling

This experiment concerns anonymous surface-operation incidence and predictive
graph compression only.  It establishes no morphology, word boundary,
language, sound, plaintext, meaning, semantic role, or translation.  f84r was
not opened, queried, retained, joined, or scored.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")

    inputs = [OLD_CORPORA, NEW_CORPORA, GDT160_RESULT, GDT160_FOLDS, GDT160_PAIRS,
              GDT160_WORLDS, GDT160_DESIGN, DESIGN, METHOD, CORE, GDT160_RUNNER]
    outputs = [OUT_GRAPHS, OUT_SCORES, OUT_CLASSES, OUT_STABILITY, OUT_SUMMARY,
               OUT_TOP20, OUT_COUNTER, OUT_REPORT]
    result = {
        "schema": "GDT161_LATENT_OPERATION_CLASS_RESULT_V1", "status": status,
        "target": design["target"], "target_both_unseen": target_node,
        "target_both_unseen_baseline": target_node_base,
        "target_masked_compat": target_pair, "target_masked_baseline": target_pair_base,
        "target_effects": {"both_unseen_gain_bits_per_cell": node_gain, "both_unseen_ap_gain": node_ap_gain,
                           "masked_cell_gain_bits_per_cell": pair_gain, "gain_survival_fraction": survival,
                           "positive_graph_folds": positive,
                           "median_k_left": median_k_left, "median_k_right": median_k_right},
        "top20_concentration": top20_summary, "target_class_stability": target_stability,
        "comparators": [row for row in summary_rows if row["corpus_id"] != design["target"]],
        "inputs": {path.name: sha(path) for path in inputs},
        "outputs": {path.name: sha(path) for path in outputs},
        "implementation": {"runner": sha(Path(__file__)), "gdt003_core": sha(CORE), "gdt160_runner": sha(GDT160_RUNNER)},
        "source_freeze_commit": "c5bddab",
        "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Anonymous surface-operation incidence and predictive graph compression only; no morphology, word boundary, language, sound, plaintext, meaning, semantic role, or translation.",
    }
    result["result_content_sha256"] = canonical_sha(result)
    OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(status)
    print(json.dumps(result["target_effects"], indent=2))
    print(json.dumps(top20_summary, indent=2))


if __name__ == "__main__":
    main()
