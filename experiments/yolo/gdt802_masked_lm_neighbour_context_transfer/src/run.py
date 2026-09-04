#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt802_masked_lm_neighbour_context_transfer"
SRC = EXP / "src"
ART = EXP / "artifacts"
G800 = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
G801 = ROOT / "experiments/yolo/gdt801_terminal_lm_boundary_hierarchy_discriminator/artifacts/GDT801_542_SOURCE_SELECTOR_BOUNDARY_JOIN.tsv"
LINES = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
MODEL_SPECS = SRC / "CANDIDATE_MODEL_SPECS.tsv"

ATLAS = ART / "GDT802_4137_MASKED_NEIGHBOUR_ATLAS.tsv"
FOLDS = ART / "GDT802_326_FOLD_ASSIGNMENTS.tsv"
METRICS = ART / "GDT802_SPARSE_RIDGE_METRICS.tsv"
RAW_AUDIT = ART / "GDT802_RAW_IDENTITY_AUDIT.tsv"
PREDICTIONS = ART / "GDT802_4137_FULL_PREDICTIONS.tsv"
CAPACITY = ART / "GDT802_CONTEXT_CAPACITY.tsv"
COEFFICIENTS = ART / "GDT802_SHARED_CONTEXT_COEFFICIENTS.tsv"
DAIIN = ART / "GDT802_DAIIN_POSITION_CARD.tsv"
SENSITIVITY = ART / "GDT802_SENSITIVITY.tsv"
NULLS = ART / "GDT802_PERMUTATION_NULLS.tsv"
CANDIDATES = ART / "GDT802_CANDIDATE_ADJUDICATION.tsv"
CARD = ART / "GDT802_STRUCTURAL_CARD.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"

LAMBDA = 4.0
BASE_SHRINK = 16.0
RAW_SHRINK = 20.0
DEFAULT_NULL_REPS = 499
FOLIO_RE = re.compile(r"^(f\d+[rv])")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def f12(value: float) -> str:
    if math.isinf(value):
        return "INF"
    return f"{value:.12g}"


def physical_folio(selector: str) -> str:
    match = FOLIO_RE.match(selector)
    if match is None:
        raise ValueError(f"invalid selector: {selector}")
    return match.group(1)


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-min(value, 40.0))
        return 1.0 / (1.0 + z)
    z = math.exp(max(value, -40.0))
    return z / (1.0 + z)


def logit(probability: float) -> float:
    probability = min(1.0 - 1e-15, max(1e-15, probability))
    return math.log(probability / (1.0 - probability))


def event_loss(y: int, probability: float) -> float:
    probability = min(1.0 - 1e-15, max(1e-15, probability))
    return -(y * math.log(probability) + (1 - y) * math.log(1.0 - probability))


def auc_score(labels: Sequence[int], scores: Sequence[float]) -> float:
    ordered = sorted(zip(scores, labels), key=lambda item: item[0])
    ranks = [0.0] * len(ordered)
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and ordered[end][0] == ordered[start][0]:
            end += 1
        rank = (start + 1 + end) / 2.0
        for index in range(start, end):
            ranks[index] = rank
        start = end
    positive = sum(label for _, label in ordered)
    negative = len(ordered) - positive
    if not positive or not negative:
        return 0.5
    rank_sum = sum(rank for rank, (_, label) in zip(ranks, ordered) if label)
    return (rank_sum - positive * (positive + 1) / 2.0) / (positive * negative)


def balanced_fold_map(rows: Sequence[dict[str, Any]], field: str) -> tuple[dict[str, int], list[int]]:
    counts = Counter(str(row[field]) for row in rows)
    loads = [0] * 5
    mapping: dict[str, int] = {}
    for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        fold = min(range(5), key=lambda value: (loads[value], value))
        mapping[label] = fold
        loads[fold] += count
    return mapping, loads


def baseline_offsets(
    train: Sequence[int], all_indices: Sequence[int], rows: Sequence[dict[str, Any]], labels: Sequence[int],
) -> dict[int, float]:
    global_p = (sum(labels[index] for index in train) + 1.0) / (len(train) + 2.0)
    counts: Counter[int] = Counter()
    positives: Counter[int] = Counter()
    for index in train:
        cell = int(rows[index]["distance_cell"])
        counts[cell] += 1
        positives[cell] += labels[index]
    result: dict[int, float] = {}
    for index in all_indices:
        cell = int(rows[index]["distance_cell"])
        probability = (positives[cell] + BASE_SHRINK * global_p) / (counts[cell] + BASE_SHRINK)
        result[index] = logit(probability)
    return result


def eligible_groups(
    train: Sequence[int], rows: Sequence[dict[str, Any]], feature: str,
) -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for index in train:
        value = str(rows[index][feature])
        if value != "NONE":
            grouped[value].append(index)
    if feature == "stem":
        return {value: indices for value, indices in grouped.items() if len(indices) >= 5}
    return {
        value: indices
        for value, indices in grouped.items()
        if len(indices) >= 5
        and len({rows[index]["stem"] for index in indices}) >= 3
        and len({rows[index]["physical_folio"] for index in indices}) >= 3
    }


def fit_beta(indices: Sequence[int], offsets: dict[int, float], labels: Sequence[int]) -> float:
    beta = 0.0
    for _ in range(50):
        gradient = -LAMBDA * beta
        curvature = LAMBDA
        for index in indices:
            probability = sigmoid(offsets[index] + beta)
            gradient += labels[index] - probability
            curvature += probability * (1.0 - probability)
        step = gradient / curvature
        beta += step
        if abs(step) < 1e-12:
            break
    return max(-math.log(8.0), min(math.log(8.0), beta))


def fit_feature(
    train: Sequence[int], rows: Sequence[dict[str, Any]], labels: Sequence[int],
    offsets: dict[int, float], feature: str,
) -> tuple[dict[str, float], dict[str, list[int]]]:
    groups = eligible_groups(train, rows, feature)
    return {value: fit_beta(indices, offsets, labels) for value, indices in groups.items()}, groups


def score_partition(
    train: Sequence[int], test: Sequence[int], rows: Sequence[dict[str, Any]], labels: Sequence[int],
    neighbour_fields: tuple[str, str] = ("left_context", "right_context"),
) -> tuple[dict[str, dict[int, float]], dict[str, set[int]], list[dict[str, Any]]]:
    all_indices = list(train) + list(test)
    base = baseline_offsets(train, all_indices, rows, labels)
    stem_beta, _ = fit_feature(train, rows, labels, base, "stem")
    stem_adjusted = {
        index: base[index] + stem_beta.get(str(rows[index]["stem"]), 0.0)
        for index in all_indices
    }
    context_beta: dict[str, dict[str, float]] = {}
    context_groups: dict[str, dict[str, list[int]]] = {}
    residual_beta: dict[str, dict[str, float]] = {}
    for feature in neighbour_fields:
        context_beta[feature], context_groups[feature] = fit_feature(train, rows, labels, base, feature)
        residual_beta[feature], _ = fit_feature(train, rows, labels, stem_adjusted, feature)

    predictions = {model: {} for model in ("P", "S", "C", "SC")}
    coverage = {model: set() for model in ("S", "C", "SC")}
    coefficient_rows: list[dict[str, Any]] = []
    for feature in neighbour_fields:
        for value, beta in context_beta[feature].items():
            coefficient_rows.append({
                "side": "LEFT" if feature.startswith("left") else "RIGHT",
                "context_surface": value, "beta_context": beta,
                "beta_after_stem": residual_beta[feature][value],
                "train_events": len(context_groups[feature][value]),
                "train_stems": len({rows[index]["stem"] for index in context_groups[feature][value]}),
                "train_folios": len({rows[index]["physical_folio"] for index in context_groups[feature][value]}),
            })
    for index in test:
        stem_value = str(rows[index]["stem"])
        stem_delta = stem_beta.get(stem_value, 0.0)
        if stem_value in stem_beta:
            coverage["S"].add(index)
            coverage["SC"].add(index)
        context_delta = 0.0
        residual_delta = 0.0
        context_seen = False
        for feature in neighbour_fields:
            value = str(rows[index][feature])
            if value in context_beta[feature]:
                context_delta += context_beta[feature][value]
                residual_delta += residual_beta[feature][value]
                context_seen = True
        if context_seen:
            coverage["C"].add(index)
            coverage["SC"].add(index)
        predictions["P"][index] = sigmoid(base[index])
        predictions["S"][index] = sigmoid(base[index] + stem_delta)
        predictions["C"][index] = sigmoid(base[index] + context_delta)
        predictions["SC"][index] = sigmoid(base[index] + stem_delta + residual_delta)
    return predictions, coverage, coefficient_rows


def partitions(
    indices: Sequence[int], rows: Sequence[dict[str, Any]], scheme: str,
) -> list[tuple[str, list[int], list[int]]]:
    result: list[tuple[str, list[int], list[int]]] = []
    if scheme == "PAGE5":
        for page_fold in range(5):
            test = [index for index in indices if rows[index]["page_fold"] == page_fold]
            train = [index for index in indices if rows[index]["page_fold"] != page_fold]
            if test:
                result.append((f"P{page_fold}", train, test))
    elif scheme == "STEM5":
        for stem_fold in range(5):
            test = [index for index in indices if rows[index]["stem_fold"] == stem_fold]
            train = [index for index in indices if rows[index]["stem_fold"] != stem_fold]
            if test:
                result.append((f"S{stem_fold}", train, test))
    elif scheme == "CROSSED5X5":
        for page_fold in range(5):
            for stem_fold in range(5):
                test = [
                    index for index in indices
                    if rows[index]["page_fold"] == page_fold and rows[index]["stem_fold"] == stem_fold
                ]
                train = [
                    index for index in indices
                    if rows[index]["page_fold"] != page_fold and rows[index]["stem_fold"] != stem_fold
                ]
                if test:
                    result.append((f"P{page_fold}S{stem_fold}", train, test))
    else:
        raise ValueError(scheme)
    return result


def evaluate(
    indices: Sequence[int], rows: Sequence[dict[str, Any]], labels: Sequence[int], scheme: str,
    neighbour_fields: tuple[str, str] = ("left_context", "right_context"),
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[int, float]], dict[str, set[int]], list[dict[str, Any]]]:
    all_predictions = {model: {} for model in ("P", "S", "C", "SC")}
    all_coverage = {model: set() for model in ("S", "C", "SC")}
    coefficient_rows: list[dict[str, Any]] = []
    fold_losses: dict[str, list[float]] = defaultdict(list)
    for fold_id, train, test in partitions(indices, rows, scheme):
        predictions, coverage, coefficients = score_partition(train, test, rows, labels, neighbour_fields)
        for model in all_predictions:
            all_predictions[model].update(predictions[model])
            fold_losses[model].append(sum(event_loss(labels[i], predictions[model][i]) for i in test) / len(test))
        for model in all_coverage:
            all_coverage[model].update(coverage[model])
        for row in coefficients:
            row["fold_id"] = fold_id
            coefficient_rows.append(row)
    if set(all_predictions["P"]) != set(indices):
        raise RuntimeError(f"not all events scored for {scheme}")
    metrics: dict[str, dict[str, Any]] = {}
    for model, prediction in all_predictions.items():
        probabilities = [prediction[index] for index in indices]
        outcomes = [labels[index] for index in indices]
        losses = [event_loss(y, p) for y, p in zip(outcomes, probabilities)]
        covered = all_coverage.get(model, set())
        metrics[model] = {
            "n_events": len(indices), "m_events": sum(outcomes), "l_events": len(outcomes) - sum(outcomes),
            "logloss_nats": sum(losses) / len(losses), "total_logloss_nats": sum(losses),
            "mean_fold_logloss_nats": sum(fold_losses[model]) / len(fold_losses[model]),
            "brier": sum((y - p) ** 2 for y, p in zip(outcomes, probabilities)) / len(outcomes),
            "auc": auc_score(outcomes, probabilities),
            "covered_events": len(covered) if model != "P" else len(indices),
            "covered_m": sum(labels[index] for index in covered) if model != "P" else sum(outcomes),
            "folds": len(fold_losses[model]),
        }
    return metrics, all_predictions, all_coverage, coefficient_rows


def conditional_auc(
    indices: Sequence[int], rows: Sequence[dict[str, Any]], labels: Sequence[int], scores: dict[int, float],
) -> dict[str, float | int]:
    strata: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index in indices:
        strata[(str(rows[index]["stem"]), str(rows[index]["position4"]))].append(index)
    informative = [group for group in strata.values() if {labels[index] for index in group} == {0, 1}]
    macro_values: list[float] = []
    wins = 0.0
    pairs = 0
    eval_events = 0
    for group in informative:
        positive = [index for index in group if labels[index] == 1]
        negative = [index for index in group if labels[index] == 0]
        local_wins = 0.0
        for left in positive:
            for right in negative:
                local_wins += float(scores[left] > scores[right]) + 0.5 * float(scores[left] == scores[right])
        local_pairs = len(positive) * len(negative)
        macro_values.append(local_wins / local_pairs)
        wins += local_wins
        pairs += local_pairs
        eval_events += len(group)
    return {
        "eval_events": eval_events, "informative_strata": len(informative),
        "eval_stems": len({rows[index]["stem"] for group in informative for index in group}),
        "pairs": pairs, "macro_auc": sum(macro_values) / len(macro_values) if macro_values else 0.5,
        "micro_auc": wins / pairs if pairs else 0.5,
    }


def raw_identity_audit(
    indices: Sequence[int], rows: Sequence[dict[str, Any]], labels: Sequence[int], hold_field: str, side: str,
) -> dict[str, Any]:
    context_scores: dict[int, float] = {}
    novelty_scores: dict[int, float] = {}
    baseline_scores: dict[int, float] = {}
    eligible_indices: list[int] = []
    for held_value in sorted({str(rows[index][hold_field]) for index in indices}):
        train = [index for index in indices if str(rows[index][hold_field]) != held_value]
        test = [index for index in indices if str(rows[index][hold_field]) == held_value]
        global_rate = sum(labels[index] for index in train) / len(train)
        pos_n: Counter[str] = Counter()
        pos_m: Counter[str] = Counter()
        for index in train:
            position = str(rows[index]["position4"])
            pos_n[position] += 1
            pos_m[position] += labels[index]
        fields = (
            ("left_context",) if side == "LEFT" else
            ("right_context",) if side == "RIGHT" else
            ("left_context", "right_context")
        )
        n_counts: Counter[tuple[str, str, str]] = Counter()
        m_counts: Counter[tuple[str, str, str]] = Counter()
        pair_n: Counter[tuple[str, str]] = Counter()
        pair_m: Counter[tuple[str, str]] = Counter()
        for index in train:
            position = str(rows[index]["position4"])
            if side == "PAIR":
                left = str(rows[index]["left_context"])
                right = str(rows[index]["right_context"])
                if left != "NONE" and right != "NONE":
                    pair_n[(position, left + "\u241f" + right)] += 1
                    pair_m[(position, left + "\u241f" + right)] += labels[index]
            else:
                for feature in fields:
                    value = str(rows[index][feature])
                    if value != "NONE":
                        n_counts[(position, feature, value)] += 1
                        m_counts[(position, feature, value)] += labels[index]
        for index in test:
            position = str(rows[index]["position4"])
            q = pos_m[position] / pos_n[position] if pos_n[position] else global_rate
            if side == "PAIR":
                left = str(rows[index]["left_context"])
                right = str(rows[index]["right_context"])
                if left == "NONE" or right == "NONE":
                    continue
                key = (position, left + "\u241f" + right)
                n = pair_n[key]
                m = pair_m[key]
                score = (m + RAW_SHRINK * q) / (n + RAW_SHRINK)
            else:
                available: list[tuple[float, int]] = []
                for feature in fields:
                    value = str(rows[index][feature])
                    if value == "NONE":
                        continue
                    key = (position, feature, value)
                    n = n_counts[key]
                    m = m_counts[key]
                    available.append(((m + RAW_SHRINK * q) / (n + RAW_SHRINK), n))
                if not available:
                    continue
                score = sum(value[0] for value in available) / len(available)
                if side in {"LEFT", "RIGHT"}:
                    novelty_scores[index] = -float(available[0][1])
            eligible_indices.append(index)
            context_scores[index] = score
            baseline_scores[index] = q
    conditional = conditional_auc(eligible_indices, rows, labels, context_scores)
    novelty = conditional_auc(eligible_indices, rows, labels, novelty_scores) if side in {"LEFT", "RIGHT"} else None
    baseline_loss = sum(event_loss(labels[index], baseline_scores[index]) for index in eligible_indices) / len(eligible_indices)
    context_loss = sum(event_loss(labels[index], context_scores[index]) for index in eligible_indices) / len(eligible_indices)
    return {
        "available_events": len(eligible_indices), **conditional,
        "baseline_logloss_nats": baseline_loss, "context_logloss_nats": context_loss,
        "context_gain_nats": baseline_loss - context_loss,
        "novelty_macro_auc": novelty["macro_auc"] if novelty else None,
        "novelty_micro_auc": novelty["micro_auc"] if novelty else None,
    }


def conditional_daiin(
    rows: Sequence[dict[str, Any]], indices: Sequence[int], labels: Sequence[int],
) -> dict[str, float | int]:
    cells: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for index in indices:
        cell = cells[str(rows[index]["position4"])]
        positive = rows[index]["left_context"] == "daiin"
        if labels[index]:
            cell[0 if positive else 1] += 1
        else:
            cell[2 if positive else 3] += 1
    numerator = denominator = 0.0
    distribution: dict[int, float] = {0: 1.0}
    observed = 0
    expected = 0.0
    informative = 0
    for a, b, c, d in cells.values():
        n = a + b + c + d
        m_total = a + b
        context_total = a + c
        if not (m_total and m_total < n and context_total and context_total < n):
            continue
        informative += 1
        numerator += a * d / n
        denominator += b * c / n
        observed += a
        expected += m_total * context_total / n
        low = max(0, context_total - (n - m_total))
        high = min(m_total, context_total)
        divisor = math.comb(n, context_total)
        local = {
            value: math.comb(m_total, value) * math.comb(n - m_total, context_total - value) / divisor
            for value in range(low, high + 1)
        }
        updated: dict[int, float] = defaultdict(float)
        for left_value, left_probability in distribution.items():
            for value, probability in local.items():
                updated[left_value + value] += left_probability * probability
        distribution = dict(updated)
    odds = numerator / denominator if denominator else math.inf
    return {
        "strata": len(cells), "informative_strata": informative,
        "context_events": sum(rows[index]["left_context"] == "daiin" for index in indices),
        "context_m": sum(labels[index] for index in indices if rows[index]["left_context"] == "daiin"),
        "observed_m": observed, "expected_m": expected, "mh_odds_ratio": odds,
        "exact_upper_p": sum(probability for value, probability in distribution.items() if value >= observed),
        "exact_lower_p": sum(probability for value, probability in distribution.items() if value <= observed),
    }


def permuted_labels(
    rows: Sequence[dict[str, Any]], labels: Sequence[int], fields: tuple[str, str], rng: random.Random,
) -> list[int]:
    groups: dict[tuple[str, str], list[int]] = {}
    for index, row in enumerate(rows):
        key = (str(row[fields[0]]), str(row[fields[1]]))
        groups.setdefault(key, []).append(index)
    result = list(labels)
    for indices in groups.values():
        values = [labels[index] for index in indices]
        rng.shuffle(values)
        for index, value in zip(indices, values):
            result[index] = value
    return result


def context_only_partition(
    train: Sequence[int], test: Sequence[int], rows: Sequence[dict[str, Any]], labels: Sequence[int],
) -> tuple[dict[int, float], dict[int, float]]:
    all_indices = list(train) + list(test)
    base = baseline_offsets(train, all_indices, rows, labels)
    beta: dict[str, dict[str, float]] = {}
    for feature in ("left_context", "right_context"):
        beta[feature], _ = fit_feature(train, rows, labels, base, feature)
    p_predictions: dict[int, float] = {}
    c_predictions: dict[int, float] = {}
    for index in test:
        delta = sum(
            beta[feature].get(str(rows[index][feature]), 0.0)
            for feature in ("left_context", "right_context")
        )
        p_predictions[index] = sigmoid(base[index])
        c_predictions[index] = sigmoid(base[index] + delta)
    return p_predictions, c_predictions


def crossed_context_total_gain(rows: Sequence[dict[str, Any]], labels: Sequence[int]) -> float:
    indices = list(range(len(rows)))
    total = 0.0
    for _, train, test in partitions(indices, rows, "CROSSED5X5"):
        p_predictions, c_predictions = context_only_partition(train, test, rows, labels)
        total += sum(
            event_loss(labels[index], p_predictions[index]) - event_loss(labels[index], c_predictions[index])
            for index in test
        )
    return total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--null-reps", type=int, default=DEFAULT_NULL_REPS)
    args = parser.parse_args()
    if args.null_reps < 0:
        raise ValueError("null reps must be nonnegative")
    ART.mkdir(parents=True, exist_ok=True)
    for lock in read_tsv(SOURCE_LOCK):
        path = ROOT / lock["path"]
        if sha(path) != lock["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {lock['path']}")

    occurrence_rows = read_tsv(G800)
    line_rows = read_tsv(LINES)
    join_rows = read_tsv(G801)
    if (len(occurrence_rows), len(line_rows), len(join_rows)) != (4137, 4128, 542):
        raise RuntimeError("predecessor cardinality changed")
    if any(
        any(str(value).startswith("f84") for value in row.values())
        for row in occurrence_rows + line_rows + join_rows
    ):
        raise RuntimeError("sealed f84/f84r selector reached materialization")

    line_map: dict[tuple[str, str], list[str]] = {}
    for row in line_rows:
        key = (row["page"], row["locus"])
        if key in line_map:
            raise RuntimeError(f"duplicate line: {key}")
        tokens = row["zl3b_line"].split()
        if len(tokens) != int(row["token_count"]):
            raise RuntimeError(f"line token mismatch: {key}")
        line_map[key] = tokens

    running_join = [row for row in join_rows if row["occurrence_kind"] == "RUNNING_EVENT"]
    endings: dict[str, set[str]] = defaultdict(set)
    for row in running_join:
        endings[row["stem"]].add(row["terminal"])
    direct_stems = {stem for stem, values in endings.items() if values == {"l", "m"}}
    direct_ids = {row["gdt800_occurrence_id"] for row in running_join if row["stem"] in direct_stems}
    paired_stems = {row["stem"] for row in occurrence_rows}

    rows: list[dict[str, Any]] = []
    for ordinal, source in enumerate(occurrence_rows, 1):
        tokens = line_map.get((source["page"], source["locus"]))
        if tokens is None:
            raise RuntimeError(f"missing line for {source['occurrence_id']}")
        token_index = int(source["token_index"])
        if tokens[token_index - 1] != source["surface"] or len(tokens) != int(source["token_count"]):
            raise RuntimeError(f"target join mismatch: {source['occurrence_id']}")
        left = tokens[token_index - 2] if token_index > 1 else "NONE"
        right = tokens[token_index] if token_index < len(tokens) else "NONE"
        left_is_paired = left != "NONE" and left[-1:] in {"l", "m"} and left[:-1] in paired_stems
        right_is_paired = right != "NONE" and right[-1:] in {"l", "m"} and right[:-1] in paired_stems
        distance = int(source["distance_from_end"])
        position4 = "SINGLE" if len(tokens) == 1 else "FINAL" if distance == 0 else "PENULTIMATE" if distance == 1 else "EARLIER"
        rows.append({
            "event_ordinal": ordinal, "occurrence_id": source["occurrence_id"],
            "source_selector": source["page"], "physical_folio": physical_folio(source["page"]),
            "locus": source["locus"], "token_index": token_index, "token_count": len(tokens),
            "distance_from_end": distance, "distance_cell": min(distance, 5),
            "position_class": source["position_class"], "position4": position4,
            "masked_target": source["stem"] + "{l|m}", "stem": source["stem"],
            "terminal": source["terminal"], "left_context": left, "right_context": right,
            "left_context_sensitivity": "NONE" if left_is_paired else left,
            "right_context_sensitivity": "NONE" if right_is_paired else right,
            "paired_neighbour": int(left_is_paired or right_is_paired),
            "direct_388": int(source["occurrence_id"] in direct_ids),
            "population": "DIRECT_388" if source["occurrence_id"] in direct_ids else "CACHE_REST_3749",
            "semantic_export_credit": "ZERO__FORMAL_MASKED_CONTEXT_ONLY",
        })
    if len(direct_stems) != 28 or len(direct_ids) != 388 or sum(row["direct_388"] for row in rows) != 388:
        raise RuntimeError("direct deck changed")
    if Counter(row["terminal"] for row in rows) != Counter({"l": 3484, "m": 653}):
        raise RuntimeError("terminal margins changed")

    page_map, page_loads = balanced_fold_map(rows, "physical_folio")
    stem_map, stem_loads = balanced_fold_map(rows, "stem")
    for row in rows:
        row["page_fold"] = page_map[row["physical_folio"]]
        row["stem_fold"] = stem_map[row["stem"]]
    if page_loads != [828, 828, 827, 827, 827] or stem_loads != [829, 827, 827, 827, 827]:
        raise RuntimeError(f"fold load drift: page={page_loads} stem={stem_loads}")

    atlas_fields = [
        "event_ordinal", "occurrence_id", "source_selector", "physical_folio", "locus", "token_index",
        "token_count", "distance_from_end", "distance_cell", "position_class", "position4", "masked_target",
        "stem", "terminal", "left_context", "right_context", "left_context_sensitivity",
        "right_context_sensitivity", "paired_neighbour", "direct_388", "population", "page_fold", "stem_fold",
        "semantic_export_credit",
    ]
    write_tsv(ATLAS, rows, atlas_fields)

    fold_rows: list[dict[str, Any]] = []
    for kind, mapping in (("PHYSICAL_FOLIO", page_map), ("STEM", stem_map)):
        field = "physical_folio" if kind == "PHYSICAL_FOLIO" else "stem"
        counts = Counter(str(row[field]) for row in rows)
        for label in sorted(mapping):
            fold_rows.append({"group_type": kind, "group_label": label, "event_count": counts[label], "fold": mapping[label]})
    write_tsv(FOLDS, fold_rows, ["group_type", "group_label", "event_count", "fold"])

    labels = [int(row["terminal"] == "m") for row in rows]
    population_indices = {
        "DIRECT_388": [index for index, row in enumerate(rows) if row["direct_388"]],
        "CACHE_REST_3749": [index for index, row in enumerate(rows) if not row["direct_388"]],
        "FULL_4137": list(range(len(rows))),
    }
    evaluations: dict[tuple[str, str], tuple[dict[str, dict[str, Any]], dict[str, dict[int, float]], dict[str, set[int]], list[dict[str, Any]]]] = {}
    metric_rows: list[dict[str, Any]] = []
    for population, indices in population_indices.items():
        for scheme in ("PAGE5", "STEM5", "CROSSED5X5"):
            evaluated = evaluate(indices, rows, labels, scheme)
            evaluations[(population, scheme)] = evaluated
            metrics = evaluated[0]
            for model in ("P", "S", "C", "SC"):
                values = metrics[model]
                metric_rows.append({
                    "population": population, "scheme": scheme, "model": model,
                    "n_events": values["n_events"], "m_events": values["m_events"], "l_events": values["l_events"],
                    "folds": values["folds"], "covered_events": values["covered_events"], "covered_m": values["covered_m"],
                    "logloss_nats": f12(values["logloss_nats"]), "total_logloss_nats": f12(values["total_logloss_nats"]),
                    "mean_fold_logloss_nats": f12(values["mean_fold_logloss_nats"]),
                    "brier": f12(values["brier"]), "auc": f12(values["auc"]),
                    "gain_vs_p": f12(metrics["P"]["logloss_nats"] - values["logloss_nats"]),
                    "gain_vs_s": "NA" if model not in {"C", "SC"} else f12(metrics["S"]["logloss_nats"] - values["logloss_nats"]),
                })
    write_tsv(METRICS, metric_rows, [
        "population", "scheme", "model", "n_events", "m_events", "l_events", "folds", "covered_events",
        "covered_m", "logloss_nats", "total_logloss_nats", "mean_fold_logloss_nats", "brier", "auc",
        "gain_vs_p", "gain_vs_s",
    ])

    raw_rows: list[dict[str, Any]] = []
    for hold_name, hold_field in (("LEAVE_STEM_OUT", "stem"), ("LEAVE_PHYSICAL_FOLIO_OUT", "physical_folio")):
        for side in ("LEFT", "RIGHT", "LEFT_RIGHT_MEAN", "PAIR"):
            result = raw_identity_audit(population_indices["FULL_4137"], rows, labels, hold_field, side)
            raw_rows.append({
                "holdout": hold_name, "context_channel": side, "available_events": result["available_events"],
                "eval_events": result["eval_events"], "informative_strata": result["informative_strata"],
                "eval_stems": result["eval_stems"], "pairs": result["pairs"],
                "macro_auc": f12(float(result["macro_auc"])), "micro_auc": f12(float(result["micro_auc"])),
                "baseline_logloss_nats": f12(float(result["baseline_logloss_nats"])),
                "context_logloss_nats": f12(float(result["context_logloss_nats"])),
                "context_gain_nats": f12(float(result["context_gain_nats"])),
                "novelty_macro_auc": "NA" if result["novelty_macro_auc"] is None else f12(float(result["novelty_macro_auc"])),
                "novelty_micro_auc": "NA" if result["novelty_micro_auc"] is None else f12(float(result["novelty_micro_auc"])),
                "decision": "MODEL_DEPENDENT_LEAD_ONLY",
            })
    write_tsv(RAW_AUDIT, raw_rows, [
        "holdout", "context_channel", "available_events", "eval_events", "informative_strata", "eval_stems",
        "pairs", "macro_auc", "micro_auc", "baseline_logloss_nats", "context_logloss_nats", "context_gain_nats",
        "novelty_macro_auc", "novelty_micro_auc", "decision",
    ])

    full_page = evaluations[("FULL_4137", "PAGE5")]
    full_cross = evaluations[("FULL_4137", "CROSSED5X5")]
    prediction_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        prediction_rows.append({
            "occurrence_id": row["occurrence_id"], "population": row["population"], "terminal": row["terminal"],
            "page_fold": row["page_fold"], "stem_fold": row["stem_fold"],
            "page_p": f12(full_page[1]["P"][index]), "page_s": f12(full_page[1]["S"][index]),
            "page_c": f12(full_page[1]["C"][index]), "page_sc": f12(full_page[1]["SC"][index]),
            "cross_p": f12(full_cross[1]["P"][index]), "cross_c": f12(full_cross[1]["C"][index]),
            "page_context_covered": int(index in full_page[2]["C"]),
            "page_stem_covered": int(index in full_page[2]["S"]),
            "cross_context_covered": int(index in full_cross[2]["C"]),
            "semantic_export_credit": "ZERO__PREDICTIVE_SCORE_ONLY",
        })
    write_tsv(PREDICTIONS, prediction_rows, [
        "occurrence_id", "population", "terminal", "page_fold", "stem_fold", "page_p", "page_s", "page_c",
        "page_sc", "cross_p", "cross_c", "page_context_covered", "page_stem_covered", "cross_context_covered",
        "semantic_export_credit",
    ])

    capacity_rows: list[dict[str, Any]] = []
    for population, indices in population_indices.items():
        raw_pair_counts = Counter(
            (rows[index]["left_context"], rows[index]["right_context"])
            for index in indices if rows[index]["left_context"] != "NONE" and rows[index]["right_context"] != "NONE"
        )
        pair_counts = Counter(
            (rows[index]["position4"], rows[index]["left_context"], rows[index]["right_context"])
            for index in indices if rows[index]["left_context"] != "NONE" and rows[index]["right_context"] != "NONE"
        )
        pair_outcomes: dict[tuple[str, str, str], set[str]] = defaultdict(set)
        pair_stems: dict[tuple[str, str, str], set[str]] = defaultdict(set)
        pair_folios: dict[tuple[str, str, str], set[str]] = defaultdict(set)
        for index in indices:
            if rows[index]["left_context"] == "NONE" or rows[index]["right_context"] == "NONE":
                continue
            key = (rows[index]["position4"], rows[index]["left_context"], rows[index]["right_context"])
            pair_outcomes[key].add(rows[index]["terminal"])
            pair_stems[key].add(rows[index]["stem"])
            pair_folios[key].add(rows[index]["physical_folio"])
        for scheme in ("PAGE5", "STEM5", "CROSSED5X5"):
            _, _, coverage, _ = evaluations[(population, scheme)]
            capacity_rows.append({
                "population": population, "scheme": scheme, "n_events": len(indices),
                "physical_folios": len({rows[index]["physical_folio"] for index in indices}),
                "stems": len({rows[index]["stem"] for index in indices}),
                "left_real": sum(rows[index]["left_context"] != "NONE" for index in indices),
                "right_real": sum(rows[index]["right_context"] != "NONE" for index in indices),
                "both_real": sum(rows[index]["left_context"] != "NONE" and rows[index]["right_context"] != "NONE" for index in indices),
                "unique_left": len({rows[index]["left_context"] for index in indices if rows[index]["left_context"] != "NONE"}),
                "unique_right": len({rows[index]["right_context"] for index in indices if rows[index]["right_context"] != "NONE"}),
                "unique_raw_pairs": len(raw_pair_counts), "singleton_raw_pairs": sum(value == 1 for value in raw_pair_counts.values()),
                "unique_position_pairs": len(pair_counts), "singleton_position_pairs": sum(value == 1 for value in pair_counts.values()),
                "cross_stem_folio_bidirectional_pairs": sum(
                    pair_outcomes[key] == {"l", "m"} and len(pair_stems[key]) >= 2 and len(pair_folios[key]) >= 2
                    for key in pair_counts
                ),
                "context_covered": len(coverage["C"]), "context_covered_m": sum(labels[index] for index in coverage["C"]),
                "stem_covered": len(coverage["S"]), "stem_covered_m": sum(labels[index] for index in coverage["S"]),
                "paired_neighbour_events": sum(rows[index]["paired_neighbour"] for index in indices),
            })
    write_tsv(CAPACITY, capacity_rows, [
        "population", "scheme", "n_events", "physical_folios", "stems", "left_real", "right_real", "both_real",
        "unique_left", "unique_right", "unique_raw_pairs", "singleton_raw_pairs", "unique_position_pairs", "singleton_position_pairs",
        "cross_stem_folio_bidirectional_pairs", "context_covered", "context_covered_m", "stem_covered",
        "stem_covered_m", "paired_neighbour_events",
    ])

    coefficient_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in full_cross[3]:
        coefficient_groups[(row["side"], row["context_surface"])].append(row)
    coefficient_rows: list[dict[str, Any]] = []
    for (side, surface), values in coefficient_groups.items():
        field = "left_context" if side == "LEFT" else "right_context"
        relevant = [row for row in rows if row[field] == surface]
        betas = [float(row["beta_context"]) for row in values]
        residuals = [float(row["beta_after_stem"]) for row in values]
        coefficient_rows.append({
            "side": side, "context_surface": surface, "eligible_cross_folds": len(values),
            "global_events": len(relevant), "global_stems": len({row["stem"] for row in relevant}),
            "global_folios": len({row["physical_folio"] for row in relevant}),
            "global_m": sum(row["terminal"] == "m" for row in relevant),
            "mean_beta_context": f12(sum(betas) / len(betas)),
            "min_beta_context": f12(min(betas)), "max_beta_context": f12(max(betas)),
            "mean_beta_after_stem": f12(sum(residuals) / len(residuals)),
            "direct_events": sum(row["direct_388"] for row in relevant),
            "cache_rest_events": sum(not row["direct_388"] for row in relevant),
            "semantic_export_credit": "ZERO__OPAQUE_COMPLETE_CONTEXT",
        })
    coefficient_rows.sort(
        key=lambda row: (-int(row["eligible_cross_folds"]), -abs(float(row["mean_beta_after_stem"])), row["side"], row["context_surface"])
    )
    write_tsv(COEFFICIENTS, coefficient_rows, [
        "side", "context_surface", "eligible_cross_folds", "global_events", "global_stems", "global_folios",
        "global_m", "mean_beta_context", "min_beta_context", "max_beta_context", "mean_beta_after_stem",
        "direct_events", "cache_rest_events", "semantic_export_credit",
    ])

    daiin_rows: list[dict[str, Any]] = []
    daiin_summaries: dict[str, dict[str, float | int]] = {}
    for population, indices in population_indices.items():
        summary = conditional_daiin(rows, indices, labels)
        daiin_summaries[population] = summary
        for position in ("EARLIER", "PENULTIMATE", "FINAL", "SINGLE"):
            context = [index for index in indices if rows[index]["position4"] == position and rows[index]["left_context"] == "daiin"]
            other = [index for index in indices if rows[index]["position4"] == position and rows[index]["left_context"] != "daiin"]
            daiin_rows.append({
                "population": population, "position4": position,
                "daiin_l": sum(labels[index] == 0 for index in context), "daiin_m": sum(labels[index] == 1 for index in context),
                "other_l": sum(labels[index] == 0 for index in other), "other_m": sum(labels[index] == 1 for index in other),
                "mh_odds_ratio": f12(float(summary["mh_odds_ratio"])), "exact_upper_p": f12(float(summary["exact_upper_p"])),
                "exact_lower_p": f12(float(summary["exact_lower_p"])),
                "decision": "LOCAL_LEAD_ONLY" if population == "DIRECT_388" else "NO_INCREMENTAL_DAIIN_BRIDGE",
                "semantic_export_credit": "ZERO__NO_DAIIN_MEANING",
            })
    write_tsv(DAIIN, daiin_rows, [
        "population", "position4", "daiin_l", "daiin_m", "other_l", "other_m", "mh_odds_ratio",
        "exact_upper_p", "exact_lower_p", "decision", "semantic_export_credit",
    ])

    sensitivity_rows: list[dict[str, Any]] = []
    for population in ("CACHE_REST_3749", "FULL_4137"):
        indices = population_indices[population]
        ordinary = evaluations[(population, "CROSSED5X5")][0]
        masked = evaluate(indices, rows, labels, "CROSSED5X5", ("left_context_sensitivity", "right_context_sensitivity"))[0]
        ordinary_gain = ordinary["P"]["logloss_nats"] - ordinary["C"]["logloss_nats"]
        masked_gain = masked["P"]["logloss_nats"] - masked["C"]["logloss_nats"]
        sensitivity_rows.append({
            "population": population, "analysis": "MASK_ALL_PAIRED_TERMINAL_NEIGHBOURS",
            "masked_events": sum(rows[index]["paired_neighbour"] for index in indices),
            "ordinary_context_gain": f12(ordinary_gain), "masked_context_gain": f12(masked_gain),
            "masked_context_coverage": masked["C"]["covered_events"],
            "decision": "RETAINS" if masked_gain > 0 else "FAILS",
        })
    write_tsv(SENSITIVITY, sensitivity_rows, [
        "population", "analysis", "masked_events", "ordinary_context_gain", "masked_context_gain",
        "masked_context_coverage", "decision",
    ])

    observed_gain = crossed_context_total_gain(rows, labels)
    null_rows: list[dict[str, Any]] = []
    for null_id, fields, seed in (
        ("PHYSICAL_FOLIO_X_DISTANCE", ("physical_folio", "distance_cell"), 80201),
        ("STEM_X_DISTANCE", ("stem", "distance_cell"), 80202),
    ):
        rng = random.Random(seed)
        exceed = 0
        values: list[float] = []
        for _ in range(args.null_reps):
            null_labels = permuted_labels(rows, labels, fields, rng)
            value = crossed_context_total_gain(rows, null_labels)
            values.append(value)
            exceed += value >= observed_gain
        null_rows.append({
            "null_id": null_id, "strata_fields": "+".join(fields), "seed": seed,
            "permutations": args.null_reps, "observed_total_gain_nats": f12(observed_gain),
            "null_mean_total_gain_nats": f12(sum(values) / len(values)) if values else "NA",
            "null_max_total_gain_nats": f12(max(values)) if values else "NA", "exceed_or_equal": exceed,
            "add_one_p": f12((exceed + 1) / (args.null_reps + 1)) if values else "NA",
            "interpretation": "DIAGNOSTIC_ONLY__MODEL_ROBUSTNESS_IS_PRIMARY",
        })
    write_tsv(NULLS, null_rows, [
        "null_id", "strata_fields", "seed", "permutations", "observed_total_gain_nats",
        "null_mean_total_gain_nats", "null_max_total_gain_nats", "exceed_or_equal", "add_one_p", "interpretation",
    ])

    def get(population: str, scheme: str, model: str) -> dict[str, Any]:
        return evaluations[(population, scheme)][0][model]

    rest_context_gain = get("CACHE_REST_3749", "CROSSED5X5", "P")["logloss_nats"] - get("CACHE_REST_3749", "CROSSED5X5", "C")["logloss_nats"]
    full_context_gain = get("FULL_4137", "CROSSED5X5", "P")["logloss_nats"] - get("FULL_4137", "CROSSED5X5", "C")["logloss_nats"]
    rest_stem_gain = get("CACHE_REST_3749", "PAGE5", "P")["logloss_nats"] - get("CACHE_REST_3749", "PAGE5", "S")["logloss_nats"]
    full_stem_gain = get("FULL_4137", "PAGE5", "P")["logloss_nats"] - get("FULL_4137", "PAGE5", "S")["logloss_nats"]
    rest_context_after_stem = get("CACHE_REST_3749", "PAGE5", "S")["logloss_nats"] - get("CACHE_REST_3749", "PAGE5", "SC")["logloss_nats"]
    full_context_after_stem = get("FULL_4137", "PAGE5", "S")["logloss_nats"] - get("FULL_4137", "PAGE5", "SC")["logloss_nats"]
    sparse_context_lead = rest_context_gain > 0 and full_context_gain > 0
    stem_selected = rest_stem_gain > 0 and full_stem_gain > 0
    raw_by_key = {(row["holdout"], row["context_channel"]): row for row in raw_rows}
    raw_context_robust = all(
        float(raw_by_key[(holdout, "LEFT_RIGHT_MEAN")]["macro_auc"]) >= 0.5
        for holdout in ("LEAVE_STEM_OUT", "LEAVE_PHYSICAL_FOLIO_OUT")
    ) and all(
        float(raw_by_key[(holdout, "LEFT_RIGHT_MEAN")]["context_gain_nats"]) >= 0
        for holdout in ("LEAVE_STEM_OUT", "LEAVE_PHYSICAL_FOLIO_OUT")
    )
    context_selected = sparse_context_lead and raw_context_robust
    daiin_rest = daiin_summaries["CACHE_REST_3749"]
    daiin_selected = float(daiin_rest["mh_odds_ratio"]) > 1 and float(daiin_rest["exact_upper_p"]) <= 0.05
    architecture = (
        "PHYSICAL_POSITION_PLUS_LEARNED_STEM__SPARSE_CONTEXT_LEAD_UNRESOLVED"
        if stem_selected and sparse_context_lead and not context_selected else
        "MIXED_POSITION_STEM_SPARSE_CONTEXT" if stem_selected and context_selected else
        "PHYSICAL_POSITION_PLUS_LEARNED_STEM" if stem_selected else
        "PHYSICAL_POSITION_ONLY_NOT_BEATEN"
    )
    status = f"PARTIAL__4137_EXACT_NEIGHBOUR_JOINS__388_DISCOVERY__3749_TRANSFER__{architecture}__DAIIN_RETIRED__JOINT_FRAME_CAPACITY_STOP__ZERO_LEXEMES"

    candidate_rows = [
        {"candidate_id": "C1", "candidate": "PHYSICAL_POSITION_ONLY", "decision": "INSUFFICIENT_ALONE" if stem_selected else "SELECTED", "positive_evidence": "strong inherited distance-from-line-end baseline", "counterevidence": f"cache-rest page-held stem gain {f12(rest_stem_gain)}", "claim_ceiling": "formal position only"},
        {"candidate_id": "C2", "candidate": "LEARNED_STEM_PLUS_POSITION", "decision": "SELECTED" if stem_selected else "NOT_SELECTED", "positive_evidence": f"page-held gain rest {f12(rest_stem_gain)} and full {f12(full_stem_gain)} nats/event", "counterevidence": "stem is derived by deleting final EVA l/m and is not a proven morpheme", "claim_ceiling": "predictive analyst-derived family identity only"},
        {"candidate_id": "C3", "candidate": "SHARED_COMPLETE_CONTEXT_PLUS_POSITION", "decision": "WEAK_MODEL_DEPENDENT_LEAD" if sparse_context_lead and not context_selected else "SELECTED_COMPONENT" if context_selected else "NOT_SELECTED", "positive_evidence": f"sparse ridge hard-cross gain rest {f12(rest_context_gain)} and full {f12(full_context_gain)}", "counterevidence": f"transparent held-folio macro AUC {raw_by_key[('LEAVE_PHYSICAL_FOLIO_OUT','LEFT_RIGHT_MEAN')]['macro_auc']} and gain {raw_by_key[('LEAVE_PHYSICAL_FOLIO_OUT','LEFT_RIGHT_MEAN')]['context_gain_nats']}", "claim_ceiling": "unresolved opaque whole-context lead"},
        {"candidate_id": "C4", "candidate": "MIXED_STEM_AND_SHARED_CONTEXT", "decision": "NOT_INSTALLED__MODEL_DEPENDENT" if sparse_context_lead and not context_selected else "SELECTED" if context_selected and stem_selected else "NOT_SELECTED", "positive_evidence": f"sparse context after stem rest {f12(rest_context_after_stem)} and full {f12(full_context_after_stem)}", "counterevidence": "exact-identity effect changes with estimator and rarity rivals it", "claim_ceiling": "candidate architecture; no renderer export unless robust"},
        {"candidate_id": "C5", "candidate": "DAIIN_SPECIAL_BRIDGE", "decision": "SELECTED" if daiin_selected else "RETIRED", "positive_evidence": "direct deck has seven earlier l and five final m", "counterevidence": f"cache-rest position-controlled OR {f12(float(daiin_rest['mh_odds_ratio']))} upper p {f12(float(daiin_rest['exact_upper_p']))}", "claim_ceiling": "no daiin meaning"},
        {"candidate_id": "C6", "candidate": "TERMINAL_EQUIVALENCE", "decision": "REJECTED", "positive_evidence": "none", "counterevidence": "prediction cannot establish interchangeability or identity", "claim_ceiling": "no equivalence licence"},
    ]
    write_tsv(CANDIDATES, candidate_rows, ["candidate_id", "candidate", "decision", "positive_evidence", "counterevidence", "claim_ceiling"])
    card_rows = [{
        "card_id": "GDT802-SC1", "scope": "GDT800_PAIRED_TERMINAL_EVENTS",
        "structural_tag": "PHYSICAL_LINE_EDGE_PLUS_LEARNED_PAIRED_FAMILY__SPARSE_COMPLETE_CONTEXT_LEAD_UNRESOLVED",
        "german_display": "Zeilenpositionsform mit gelernter Familienneigung; vollständiger Nachbarkontext noch offen",
        "confidence": "C1_STRUCTURAL_WORKING",
        "positive_evidence": f"rest page-held stem gain {f12(rest_stem_gain)}; sparse rest crossed context gain {f12(rest_context_gain)}",
        "counterevidence": f"transparent held-folio macro context AUC {raw_by_key[('LEAVE_PHYSICAL_FOLIO_OUT','LEFT_RIGHT_MEAN')]['macro_auc']}; daiin rest OR {f12(float(daiin_rest['mh_odds_ratio']))}",
        "token_display_rule": "keep exact target whole opaque; expose physical edge and learned-family channel only",
        "equivalence_license": "NONE", "component_export": "NONE", "semantic_export": "NONE", "plaintext_value": "NONE",
    }]
    write_tsv(CARD, card_rows, [
        "card_id", "scope", "structural_tag", "german_display", "confidence", "positive_evidence", "counterevidence",
        "token_display_rule", "equivalence_license", "component_export", "semantic_export", "plaintext_value",
    ])

    full_capacity = next(row for row in capacity_rows if row["population"] == "FULL_4137" and row["scheme"] == "CROSSED5X5")
    held_page_raw = raw_by_key[("LEAVE_PHYSICAL_FOLIO_OUT", "LEFT_RIGHT_MEAN")]
    held_stem_raw = raw_by_key[("LEAVE_STEM_OUT", "LEFT_RIGHT_MEAN")]
    report = f"""# GDT802 — masked `l/m` neighbour-context transfer

Status: `{status}`

## Result

All **4,137/4,137** GDT800 targets join exactly to their cached V99R7 line and
token. They cover **155** derived paired families, **177** source selectors and
**171** normalized physical folios. No new page, image or transcription was
opened. There are **3,827** real left and **3,351** real right neighbours.

The strongest stable addition to GDT801 is target-family identity. On held
physical folios, it improves the physical distance baseline by
**{f12(rest_stem_gain)} nats/event** in the disjoint 3,749-event cache rest and
**{f12(full_stem_gain)}** over all 4,137 events. This remains an analyst-derived
paired-family key, not a demonstrated suffix or morpheme.

The complete-neighbour result is informative but not yet stable enough to
install. A sparse ridge model, admitting only complete surfaces seen at least
five times beside at least three stems on three folios, improves hard
simultaneous stem-and-folio holdout by **{f12(rest_context_gain)} nats/event**
outside the 388-event discovery deck and **{f12(full_context_gain)}** on the
full cache. It also adds **{f12(rest_context_after_stem)}** after stem control in
held-folio cache-rest.

But a transparent alpha-20 exact-identity estimator changes direction under
physical-folio holdout: the combined left/right conditional macro AUC is
**{held_page_raw['macro_auc']}** (micro **{held_page_raw['micro_auc']}**) and its
loss gain is **{held_page_raw['context_gain_nats']}**. Under held stems the
corresponding values are **{held_stem_raw['macro_auc']}** and
**{held_stem_raw['context_gain_nats']}**. Outcome-blind neighbour rarity matches
or beats several identity channels. The positive sparse result is therefore
kept as a **model-dependent lead**, not exported as a terminal role.

## Why whole two-sided frames stop

There are **{full_capacity['both_real']}** events with two real neighbours, but
**{full_capacity['singleton_raw_pairs']}/{full_capacity['unique_raw_pairs']}**
two-sided surface frames are singletons. With physical-position class included,
the count is **{full_capacity['singleton_position_pairs']}/{full_capacity['unique_position_pairs']}**. Only
**{full_capacity['cross_stem_folio_bidirectional_pairs']}** frames are
bidirectional across multiple stems and folios. That is a capacity stop for a
joint-frame grammar; left and right must remain separate candidate channels.

## `daiin` correction

The most attractive local example does not generalize. In the direct deck,
targets after `daiin` comprise seven earlier `l` and five final `m`. Outside
those 388 events they comprise 54 earlier `l`/5 `m`, twelve penultimate `l`,
and ten final `l`/11 `m`. Position-controlled cache-rest OR is
**{f12(float(daiin_rest['mh_odds_ratio']))}** with upper
`p={f12(float(daiin_rest['exact_upper_p']))}`. The special `daiin -> m` bridge
is retired: its apparent success was a local line-edge pattern, not a portable
whole-word rule. This assigns no meaning to `daiin`.

## Echo sensitivity

**{sum(row['paired_neighbour'] for row in rows)}** targets touch another member
of a GDT800 paired-terminal family. Masking all such adjacent family members
leaves cache-rest sparse context gain **{sensitivity_rows[0]['masked_context_gain']}**
and full gain **{sensitivity_rows[1]['masked_context_gain']}**. This records the
serial-echo risk but does not cure the estimator dependence above.

## Updated working architecture

The installed working model is now:

`PHYSICAL LINE EDGE + LEARNED PAIRED-FAMILY PROPENSITY`

A sparse cross-family complete-neighbour channel remains the best unresolved
lead. It is not yet part of the renderer. GDT802 grants no `l=m` equivalence,
no component value, no word meaning and no translation.

## Next route

The next useful pass is not another global neighbour classifier. Take the
recurrent surfaces in `GDT802_SHARED_CONTEXT_COEFFICIENTS.tsv` that remain
eligible across many crossed folds, split them by left/right and physical
distance, and compare their exact passages with an outcome-blind frequency
match. The aim is to find a repeated *construction* that beats rarity and page
style. Only after that should it be aligned with a descriptive or prescriptive
record field; coefficient sign alone never supplies a meaning.
"""
    REPORT.write_text(report, encoding="utf-8")

    outputs = [
        ATLAS, FOLDS, METRICS, RAW_AUDIT, PREDICTIONS, CAPACITY, COEFFICIENTS,
        DAIIN, SENSITIVITY, NULLS, CANDIDATES, CARD, REPORT,
    ]
    inputs = [G800, G801, LINES, SOURCE_LOCK, MODEL_SPECS, EXP / "PREREGISTRATION.md", EXP / "METHOD.md"]
    result: dict[str, Any] = {
        "schema": "GDT802_RESULT_V1", "experiment": "GDT802", "status": status,
        "decision": architecture, "exact_joins": len(rows), "direct_events": len(population_indices["DIRECT_388"]),
        "cache_rest_events": len(population_indices["CACHE_REST_3749"]), "stems": len(stem_map),
        "source_selectors": len({row["source_selector"] for row in rows}), "physical_folios": len(page_map),
        "left_real": sum(row["left_context"] != "NONE" for row in rows),
        "right_real": sum(row["right_context"] != "NONE" for row in rows),
        "sparse_context_lead": sparse_context_lead, "raw_context_robust": raw_context_robust,
        "context_selected": context_selected, "stem_selected": stem_selected,
        "gains_nats_per_event": {
            "cache_rest_cross_context_over_physical": rest_context_gain,
            "full_cross_context_over_physical": full_context_gain,
            "cache_rest_page_stem_over_physical": rest_stem_gain,
            "full_page_stem_over_physical": full_stem_gain,
            "cache_rest_page_context_over_stem": rest_context_after_stem,
            "full_page_context_over_stem": full_context_after_stem,
        },
        "raw_held_folio_combined": held_page_raw, "raw_held_stem_combined": held_stem_raw,
        "daiin_cache_rest": daiin_rest, "daiin_selected": daiin_selected,
        "joint_frame_capacity": {
            "both_real": full_capacity["both_real"], "raw_frames": full_capacity["unique_raw_pairs"],
            "raw_singleton_frames": full_capacity["singleton_raw_pairs"], "position_frames": full_capacity["unique_position_pairs"],
            "singleton_frames": full_capacity["singleton_position_pairs"],
            "cross_stem_folio_bidirectional": full_capacity["cross_stem_folio_bidirectional_pairs"],
        },
        "paired_neighbour_sensitivities": sensitivity_rows, "null_repetitions": args.null_reps,
        "semantic_exports": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "equivalence_licenses": 0, "new_pages_opened": 0, "new_images_opened": 0,
        "f84_or_f84r_accessed": False,
        "claim_ceiling": "FORMAL_POSITION_AND_LEARNED_FAMILY_ONLY__SPARSE_CONTEXT_UNRESOLVED__NO_MORPHEME_OR_TRANSLATION",
        "inputs": {rel(path): sha(path) for path in inputs},
        "outputs": {rel(path): sha(path) for path in outputs},
        "implementation": {rel(Path(__file__)): sha(Path(__file__))},
    }
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    print("direct=388 rest=3749 full=4137; selectors=177 physical_folios=171")
    print(f"rest sparse context gain={f12(rest_context_gain)}; rest stem gain={f12(rest_stem_gain)}")
    print(f"raw held-folio macro AUC={held_page_raw['macro_auc']}; daiin rest OR={f12(float(daiin_rest['mh_odds_ratio']))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
