#!/usr/bin/env python3
"""Small deterministic metrics used by GDT396 scoring."""

from __future__ import annotations

import math
from collections import Counter


def choose2(n: int) -> int:
    return n * (n - 1) // 2


def partition_metrics(truth: list[str], pred: list[str]) -> dict[str, float]:
    if len(truth) != len(pred) or not truth:
        raise ValueError("partition metric length/capacity")
    rows = Counter(zip(truth, pred)); a = Counter(truth); b = Counter(pred); n = len(truth)
    mutual = 0.0
    for (x, y), count in rows.items():
        mutual += count / n * math.log((count * n) / (a[x] * b[y]))
    ht = -sum(count / n * math.log(count / n) for count in a.values())
    hp = -sum(count / n * math.log(count / n) for count in b.values())
    nmi = 1.0 if ht == hp == 0 else (2 * mutual / (ht + hp) if ht + hp else 0.0)
    sum_rows = sum(choose2(count) for count in rows.values())
    sum_a = sum(choose2(count) for count in a.values()); sum_b = sum(choose2(count) for count in b.values())
    total = choose2(n); expected = sum_a * sum_b / total if total else 0.0
    maximum = 0.5 * (sum_a + sum_b)
    ari = (sum_rows - expected) / (maximum - expected) if maximum != expected else 1.0
    precision = sum_rows / sum_b if sum_b else (1.0 if sum_a == 0 else 0.0)
    recall = sum_rows / sum_a if sum_a else (1.0 if sum_b == 0 else 0.0)
    pair_f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    singleton_fraction = sum(count for count in b.values() if count == 1) / n
    largest_fraction = max(b.values()) / n
    pair_ratio = sum_b / sum_a if sum_a else (1.0 if sum_b == 0 else math.inf)
    return {
        "nmi": nmi, "ari": ari, "pair_f1": pair_f1,
        "singleton_fraction": singleton_fraction, "largest_cluster_fraction": largest_fraction,
        "nonsingleton_clusters": float(sum(count > 1 for count in b.values())),
        "cocluster_pair_ratio": pair_ratio,
    }


def binary_metrics(truth: list[bool], pred: list[bool]) -> dict[str, float]:
    if len(truth) != len(pred) or not truth:
        raise ValueError("binary metric length/capacity")
    tp = sum(t and p for t, p in zip(truth, pred)); tn = sum((not t) and (not p) for t, p in zip(truth, pred))
    fp = sum((not t) and p for t, p in zip(truth, pred)); fn = sum(t and (not p) for t, p in zip(truth, pred))
    tpr = tp / (tp + fn) if tp + fn else 0.0; tnr = tn / (tn + fp) if tn + fp else 0.0
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / denom if denom else 0.0
    fdr = fp / (tp + fp) if tp + fp else 0.0
    return {"balanced_accuracy": 0.5 * (tpr + tnr), "mcc": mcc, "fdr": fdr, "tp": float(tp), "tn": float(tn), "fp": float(fp), "fn": float(fn)}


def ranked_target_metrics(relevant: dict[str, set[str]], rankings: dict[str, list[str]], k: int = 5) -> dict[str, float]:
    if not relevant:
        raise ValueError("no target capacity")
    rr = []; hits = []; ndcg = []
    for source, truth in relevant.items():
        ranked = rankings.get(source, [])
        positions = [index + 1 for index, value in enumerate(ranked) if value in truth]
        rr.append(1.0 / min(positions) if positions else 0.0)
        hits.append(float(bool(positions and min(positions) == 1)))
        dcg = sum(1.0 / math.log2(index + 2) for index, value in enumerate(ranked[:k]) if value in truth)
        ideal = sum(1.0 / math.log2(index + 2) for index in range(min(k, len(truth))))
        ndcg.append(dcg / ideal if ideal else 0.0)
    return {"mrr": sum(rr) / len(rr), "hits1": sum(hits) / len(hits), "ndcg5": sum(ndcg) / len(ndcg)}


def interval_iou(a: tuple[int, int], b: tuple[int, int]) -> float:
    left = max(a[0], b[0]); right = min(a[1], b[1])
    intersection = max(0, right - left + 1)
    union = max(a[1], b[1]) - min(a[0], b[0]) + 1
    return intersection / union if union else 0.0
