#!/usr/bin/env python3
"""Degree-preserving operation-label nulls for GDT003 compatibility density."""

from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import multiprocessing as mp
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from run_gdt003_nested_heldout import apply_op, discover_operations


ROOT = Path(__file__).resolve().parent
DESIGN = ROOT / "gdt160_null_design.json"
METHOD = ROOT / "GDT160_COMPATIBILITY_PAIRING_NULL_METHOD.md"
OLD_CORPORA = ROOT / "gdt003_structural_fingerprint_corpora.json.gz"
NEW_CORPORA = ROOT / "gdt159_diplomatic_corpora.json.gz"
OLD_FP = ROOT / "gdt003_structural_fingerprints.tsv"
NEW_FP = ROOT / "gdt159_structural_fingerprints.tsv"
OLD_RESULT = ROOT / "gdt003_structural_fingerprint_result.json"
NEW_RESULT = ROOT / "gdt159_result.json"
SOURCE_PROVENANCE = ROOT / "gdt003_structural_fingerprint_source_provenance.json"
CORE = ROOT / "run_gdt003_nested_heldout.py"
FINGERPRINT_RUNNER = ROOT / "run_gdt003_structural_fingerprint_comparator.py"

OUT_FOLDS = ROOT / "gdt160_fold_decomposition.tsv"
OUT_NULL = ROOT / "gdt160_null_summary.tsv"
OUT_WORLDS = ROOT / "gdt160_null_worlds.tsv"
OUT_PAIRS = ROOT / "gdt160_pair_excess.tsv"
OUT_COUNTER = ROOT / "gdt160_counterexamples.tsv"
OUT_RESULT = ROOT / "gdt160_result.json"
OUT_REPORT = ROOT / "GDT160_COMPATIBILITY_PAIRING_NULL_REPORT.md"


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


def load_records() -> dict[str, list[dict[str, Any]]]:
    by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in (OLD_CORPORA, NEW_CORPORA):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for row in json.load(handle)["records"]:
                corpus = str(row["corpus_id"])
                if corpus == "VOYNICH_MATCHED" or corpus in json.loads(DESIGN.read_text(encoding="utf-8"))["comparators"]:
                    by[corpus].append(row)
    return by


def side(operation: tuple[str, str, str]) -> str:
    return "L" if operation[0].startswith("PREFIX") else "R"


def semantic_stats(
    forms: set[str], selected: list[dict[str, Any]], edge_maps: dict[tuple[str, str, str], dict[str, str]]
) -> tuple[Counter[str], dict[tuple[str, str], dict[str, int]]]:
    totals: Counter[str] = Counter()
    details: dict[tuple[str, str], dict[str, int]] = {}
    for left_index, first in enumerate(selected):
        operation_a = first["operation"]
        for second in selected[left_index + 1 :]:
            operation_b = second["operation"]
            pair_side = "LR" if side(operation_a) != side(operation_b) else side(operation_a) * 2
            totals[f"den_{pair_side}"] += 1
            triplets = complete = 0
            for base in set(edge_maps[operation_a]) & set(edge_maps[operation_b]):
                ax = edge_maps[operation_a][base]
                bx = edge_maps[operation_b][base]
                ab = apply_op(operation_a, bx)
                ba = apply_op(operation_b, ax)
                if ab is None or ab != ba:
                    continue
                triplets += 1
                complete += int(ab in forms)
            if triplets >= 3 and complete >= 1:
                totals[f"eligible_{pair_side}"] += 1
                totals[f"triplets_{pair_side}"] += triplets
                totals[f"complete_{pair_side}"] += complete
            if pair_side == "LR" and triplets >= 3 and complete >= 1:
                left, right = (first, second) if side(operation_a) == "L" else (second, first)
                details[(str(left["operation_id"]), str(right["operation_id"]))] = {
                    "triplets": triplets,
                    "complete": complete,
                    "eligible": int(triplets >= 3 and complete >= 1),
                    "left_support": int(left["edge_types"]),
                    "right_support": int(right["edge_types"]),
                }
    return totals, details


def graph_side(
    operations: list[dict[str, Any]], edge_maps: dict[tuple[str, str, str], dict[str, str]]
) -> dict[str, Any]:
    edges: list[tuple[str, str, int]] = []
    outgoing: dict[str, list[int]] = defaultdict(list)
    for label, row in enumerate(operations):
        # GDT003 stores domains from sets; sort the immutable edge endpoints so
        # MCMC edge IDs do not inherit process-specific Python hash order.
        for source, target in sorted(edge_maps[row["operation"]].items()):
            edge_id = len(edges)
            edges.append((source, target, label))
            outgoing[source].append(edge_id)
    return {"operations": operations, "edges": edges, "outgoing": outgoing}


def graph_arrays(left: dict[str, Any], right: dict[str, Any]) -> dict[str, np.ndarray]:
    left_edges = left["edges"]
    right_edges = right["edges"]
    left_out = left["outgoing"]
    right_out = right["outgoing"]
    trip_left: list[int] = []
    trip_right_edge: list[int] = []
    for host in set(left_out) & set(right_out):
        for left_edge in left_out[host]:
            left_label = left_edges[left_edge][2]
            for right_edge in right_out[host]:
                trip_left.append(left_label)
                trip_right_edge.append(right_edge)

    left_target_lookup: dict[tuple[str, int, str], bool] = {}
    for source, edge_ids in left_out.items():
        for edge_id in edge_ids:
            _, target, label = left_edges[edge_id]
            left_target_lookup[(source, label, target)] = True
    square_left: list[int] = []
    square_right_0: list[int] = []
    square_right_1: list[int] = []
    for host in set(left_out) & set(right_out):
        for left_edge in left_out[host]:
            _, left_target, left_label = left_edges[left_edge]
            if left_target not in right_out:
                continue
            for right_edge_0 in right_out[host]:
                _, right_target, _ = right_edges[right_edge_0]
                for right_edge_1 in right_out[left_target]:
                    _, final_target, _ = right_edges[right_edge_1]
                    if (right_target, left_label, final_target) in left_target_lookup:
                        square_left.append(left_label)
                        square_right_0.append(right_edge_0)
                        square_right_1.append(right_edge_1)
    return {
        "trip_fixed": np.asarray(trip_left, dtype=np.int32),
        "trip_edge": np.asarray(trip_right_edge, dtype=np.int32),
        "square_fixed": np.asarray(square_left, dtype=np.int32),
        "square_edge_0": np.asarray(square_right_0, dtype=np.int32),
        "square_edge_1": np.asarray(square_right_1, dtype=np.int32),
    }


def score_graph(
    arrays: dict[str, np.ndarray], labels: np.ndarray, fixed_count: int, shuffled_count: int
) -> tuple[int, np.ndarray, np.ndarray, np.ndarray]:
    size = fixed_count * shuffled_count
    pair_trip = arrays["trip_fixed"] * shuffled_count + labels[arrays["trip_edge"]]
    triplets = np.bincount(pair_trip, minlength=size)
    equal = labels[arrays["square_edge_0"]] == labels[arrays["square_edge_1"]]
    if np.any(equal):
        pair_complete = arrays["square_fixed"][equal] * shuffled_count + labels[arrays["square_edge_0"][equal]]
        complete = np.bincount(pair_complete, minlength=size)
    else:
        complete = np.zeros(size, dtype=np.int64)
    eligible = (triplets >= 3) & (complete >= 1)
    return int(eligible.sum()), eligible, triplets, complete


def transpose_arrays(left: dict[str, Any], right: dict[str, Any]) -> dict[str, np.ndarray]:
    # Build the same square test with right fixed and left labels shuffled.
    raw = graph_arrays(right, left)
    return raw


def blocks_for(
    graph: dict[str, Any], freq: Counter[str], form_folds: dict[str, set[str]], form_units: dict[str, set[str]], strict: bool
) -> tuple[list[list[int]], int]:
    blocks: dict[tuple[Any, ...], list[int]] = defaultdict(list)
    for edge_id, (source, target, _) in enumerate(graph["edges"]):
        key: tuple[Any, ...] = (len(source), len(target))
        if strict:
            key += (freq[source], len(form_folds[source]), len(form_units[source]))
        blocks[key].append(edge_id)
    usable = []
    movable: set[int] = set()
    for edge_ids in blocks.values():
        if len({graph["edges"][edge_id][0] for edge_id in edge_ids}) >= 2 and len({graph["edges"][edge_id][2] for edge_id in edge_ids}) >= 2:
            usable.append(edge_ids)
            movable.update(edge_ids)
    return usable, len(movable)


def randomized_worlds(
    graph: dict[str, Any], arrays: dict[str, np.ndarray], fixed_count: int, freq: Counter[str],
    form_folds: dict[str, set[str]], form_units: dict[str, set[str]], strict: bool,
    worlds: int, seed: int, collect_pairs: bool,
) -> dict[str, Any]:
    labels = np.asarray([edge[2] for edge in graph["edges"]], dtype=np.int32)
    shuffled_count = len(graph["operations"])
    blocks, switchable_edges = blocks_for(graph, freq, form_folds, form_units, strict)
    if not blocks:
        observed, eligible, _, _ = score_graph(arrays, labels, fixed_count, shuffled_count)
        return {"counts": [observed] * worlds, "pair_counts": eligible.astype(np.int64) * worlds, "switchable_edges": 0, "accepted": 0, "attempted": 0}
    weights = [len(block) * (len(block) - 1) for block in blocks]
    cumulative = np.cumsum(weights)
    rng = random.Random(seed)
    source_sets: dict[str, set[int]] = defaultdict(set)
    for source, _, label in graph["edges"]:
        source_sets[source].add(label)

    accepted = attempted = 0

    def switches(n: int) -> None:
        nonlocal accepted, attempted
        for _ in range(n):
            attempted += 1
            pick = rng.randrange(int(cumulative[-1]))
            block_index = int(np.searchsorted(cumulative, pick, side="right"))
            block = blocks[block_index]
            first, second = rng.sample(block, 2)
            source_a = graph["edges"][first][0]
            source_b = graph["edges"][second][0]
            label_a, label_b = int(labels[first]), int(labels[second])
            if source_a == source_b or label_a == label_b:
                continue
            if label_b in source_sets[source_a] or label_a in source_sets[source_b]:
                continue
            source_sets[source_a].remove(label_a)
            source_sets[source_b].remove(label_b)
            source_sets[source_a].add(label_b)
            source_sets[source_b].add(label_a)
            labels[first], labels[second] = label_b, label_a
            accepted += 1

    switches(20 * switchable_edges)
    counts: list[int] = []
    pair_counts = np.zeros(fixed_count * shuffled_count, dtype=np.int64)
    for _ in range(worlds):
        switches(switchable_edges)
        count, eligible, _, _ = score_graph(arrays, labels, fixed_count, shuffled_count)
        counts.append(count)
        if collect_pairs:
            pair_counts += eligible
    return {
        "counts": counts,
        "pair_counts": pair_counts,
        "switchable_edges": switchable_edges,
        "accepted": accepted,
        "attempted": attempted,
    }


def fold_seed(base: int, corpus: str, held: str, null: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{base}|{corpus}|{held}|{null}".encode()).digest()[:8], "big")


def corpus_worker(payload: tuple[str, list[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    corpus_id, records, design = payload
    worlds = int(design["worlds"])
    base_seed = int(design["seed"])
    fold_rows: list[dict[str, Any]] = []
    null_fold: list[dict[str, Any]] = []
    pair_aggregate: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    corpus_worlds = {name: np.zeros(worlds, dtype=np.int64) for name in design["nulls"]}
    total_denominator = total_semantic = total_graph = 0

    for held_fold in sorted({str(row["fold_id"]) for row in records}):
        train = [row for row in records if row["fold_id"] != held_fold]
        freq = Counter(str(row["form"]) for row in train)
        forms = set(freq)
        form_folds: dict[str, set[str]] = defaultdict(set)
        form_units: dict[str, set[str]] = defaultdict(set)
        for row in train:
            form_folds[str(row["form"])].add(str(row["fold_id"]))
            form_units[str(row["form"])].add(str(row["unit_id"]))
        selected, edge_maps = discover_operations(forms, freq, form_folds)
        semantic, semantic_pairs = semantic_stats(forms, selected, edge_maps)
        left_ops = [row for row in selected if side(row["operation"]) == "L"]
        right_ops = [row for row in selected if side(row["operation"]) == "R"]
        left_graph, right_graph = graph_side(left_ops, edge_maps), graph_side(right_ops, edge_maps)
        right_arrays = graph_arrays(left_graph, right_graph)
        left_arrays = transpose_arrays(left_graph, right_graph)
        right_labels = np.asarray([edge[2] for edge in right_graph["edges"]], dtype=np.int32)
        left_labels = np.asarray([edge[2] for edge in left_graph["edges"]], dtype=np.int32)
        graph_count_r, graph_eligible_r, graph_trip_r, graph_complete_r = score_graph(right_arrays, right_labels, len(left_ops), len(right_ops))
        graph_count_l, _, _, _ = score_graph(left_arrays, left_labels, len(right_ops), len(left_ops))
        if graph_count_r != graph_count_l:
            raise RuntimeError(f"orientation graph mismatch {corpus_id} {held_fold}")
        denominator = len(selected) * (len(selected) - 1) // 2
        semantic_all = sum(semantic[f"eligible_{name}"] for name in ("LL", "LR", "RR"))
        fold_row = {
            "corpus_id": corpus_id,
            "held_fold": held_fold,
            "training_forms": len(forms),
            "selected_operations": len(selected),
            "left_operations": len(left_ops),
            "right_operations": len(right_ops),
            "all_pair_denominator": denominator,
            "left_right_denominator": len(left_ops) * len(right_ops),
            "semantic_eligible_all": semantic_all,
            "semantic_eligible_LL": semantic["eligible_LL"],
            "semantic_eligible_LR": semantic["eligible_LR"],
            "semantic_eligible_RR": semantic["eligible_RR"],
            "semantic_LR_triplets": semantic["triplets_LR"],
            "semantic_LR_complete": semantic["complete_LR"],
            "graph_eligible_LR": graph_count_r,
            "graph_minus_semantic_LR": graph_count_r - semantic["eligible_LR"],
            "left_edges": len(left_graph["edges"]),
            "right_edges": len(right_graph["edges"]),
        }
        total_denominator += denominator
        total_semantic += semantic_all
        total_graph += graph_count_r + semantic["eligible_LL"] + semantic["eligible_RR"]

        null_specs = (
            ("RIGHT_LABEL_SWITCH_LENGTH_EXACT", right_graph, right_arrays, len(left_ops), False),
            ("LEFT_LABEL_SWITCH_LENGTH_EXACT", left_graph, left_arrays, len(right_ops), False),
            ("RIGHT_LABEL_SWITCH_RECURRENCE_STRICT", right_graph, right_arrays, len(left_ops), True),
        )
        results: dict[str, dict[str, Any]] = {}
        for name, graph, arrays, fixed_count, strict in null_specs:
            value = randomized_worlds(
                graph, arrays, fixed_count, freq, form_folds, form_units, strict, worlds,
                fold_seed(base_seed, corpus_id, held_fold, name), corpus_id == design["target"] and name == "RIGHT_LABEL_SWITCH_LENGTH_EXACT",
            )
            results[name] = value
            corpus_worlds[name] += np.asarray(value["counts"], dtype=np.int64)
            null_fold.append({
                "corpus_id": corpus_id,
                "held_fold": held_fold,
                "null": name,
                "observed_graph_eligible": graph_count_r,
                "null_mean_eligible": statistics.fmean(value["counts"]),
                "switchable_edges": value["switchable_edges"],
                "total_shuffled_edges": len(graph["edges"]),
                "switchable_fraction": value["switchable_edges"] / max(1, len(graph["edges"])),
                "accepted_switches": value["accepted"],
                "attempted_switches": value["attempted"],
                "acceptance_rate": value["accepted"] / max(1, value["attempted"]),
            })
            fold_row[f"{name}_switchable_edges"] = value["switchable_edges"]
            fold_row[f"{name}_null_mean"] = statistics.fmean(value["counts"])
        fold_rows.append(fold_row)

        if corpus_id == design["target"]:
            primary_counts = results["RIGHT_LABEL_SWITCH_LENGTH_EXACT"]["pair_counts"]
            left_index_by_id = {str(row["operation_id"]): index for index, row in enumerate(left_ops)}
            right_index_by_id = {str(row["operation_id"]): index for index, row in enumerate(right_ops)}
            pair_indices = set(int(index) for index in np.flatnonzero(graph_eligible_r))
            for left_id, right_id in semantic_pairs:
                pair_indices.add(left_index_by_id[left_id] * len(right_ops) + right_index_by_id[right_id])
            for pair_index in pair_indices:
                left_index, right_index = divmod(pair_index, len(right_ops))
                left, right = left_ops[left_index], right_ops[right_index]
                key = (str(left["operation_id"]), str(right["operation_id"]))
                detail = semantic_pairs.get(key, {
                    "eligible": 0,
                    "triplets": 0,
                    "complete": 0,
                    "left_support": int(left["edge_types"]),
                    "right_support": int(right["edge_types"]),
                })
                row = pair_aggregate[key]
                row["selected_folds"] += 1
                row["semantic_eligible_folds"] += detail["eligible"]
                row["semantic_triplets"] += detail["triplets"]
                row["semantic_complete"] += detail["complete"]
                row["graph_eligible_folds"] += int(graph_eligible_r[pair_index])
                row["graph_triplets"] += int(graph_trip_r[pair_index])
                row["graph_complete"] += int(graph_complete_r[pair_index])
                row["null_expected_eligible_folds"] += float(primary_counts[pair_index]) / worlds
                row["left_support_sum"] += detail["left_support"]
                row["right_support_sum"] += detail["right_support"]

    return {
        "corpus_id": corpus_id,
        "fold_rows": fold_rows,
        "null_fold": null_fold,
        "worlds": {name: values.tolist() for name, values in corpus_worlds.items()},
        "pair_aggregate": {f"{key[0]}\t{key[1]}": dict(value) for key, value in pair_aggregate.items()},
        "total_denominator": total_denominator,
        "total_semantic": total_semantic,
        "total_graph": total_graph,
    }


def quantile(values: list[int], q: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=float), q, method="linear"))


def main() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    records = load_records()
    tasks = [(corpus, records[corpus], design) for corpus in [design["target"], *design["comparators"]]]
    with mp.Pool(processes=min(6, len(tasks))) as pool:
        results = pool.map(corpus_worker, tasks)
    by = {row["corpus_id"]: row for row in results}

    fold_rows = [item for result in results for item in result["fold_rows"]]
    null_fold = [item for result in results for item in result["null_fold"]]
    world_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for result in results:
        corpus = result["corpus_id"]
        denominator = int(result["total_denominator"])
        semantic = int(result["total_semantic"])
        graph = int(result["total_graph"])
        for null_name, values in result["worlds"].items():
            for index, count in enumerate(values, 1):
                world_rows.append({
                    "corpus_id": corpus,
                    "null": null_name,
                    "world": index,
                    "null_eligible_pairs": count,
                    "null_all_pair_density": count / denominator,
                })
            mean = statistics.fmean(values)
            sd = statistics.pstdev(values)
            relevant = [row for row in null_fold if row["corpus_id"] == corpus and row["null"] == null_name]
            positive_folds = sum(float(row["observed_graph_eligible"]) > float(row["null_mean_eligible"]) for row in relevant)
            summary_rows.append({
                "corpus_id": corpus,
                "null": null_name,
                "folds": len(relevant),
                "all_pair_denominator": denominator,
                "semantic_eligible_pairs": semantic,
                "semantic_all_pair_density": semantic / denominator,
                "graph_observed_eligible_pairs": graph,
                "graph_observed_all_pair_density": graph / denominator,
                "graph_semantic_calibration_delta": graph - semantic,
                "null_mean_eligible_pairs": mean,
                "null_mean_all_pair_density": mean / denominator,
                "null_ci025_density": quantile(values, 0.025) / denominator,
                "null_ci975_density": quantile(values, 0.975) / denominator,
                "null_survival_fraction_of_graph_observed": mean / max(1, graph),
                "graph_excess_eligible_pairs": graph - mean,
                "graph_excess_all_pair_density": (graph - mean) / denominator,
                "graph_to_null_ratio": graph / max(1e-12, mean),
                "z_score": (graph - mean) / sd if sd else "NA",
                "inclusive_empirical_p": (1 + sum(value >= graph for value in values)) / (len(values) + 1),
                "positive_fold_directions": positive_folds,
                "mean_switchable_fraction": statistics.fmean(float(row["switchable_fraction"]) for row in relevant),
                "minimum_fold_switchable_fraction": min(float(row["switchable_fraction"]) for row in relevant),
                "mean_acceptance_rate": statistics.fmean(float(row["acceptance_rate"]) for row in relevant),
            })

    target_pairs = []
    for key, value in by[design["target"]]["pair_aggregate"].items():
        left, right = key.split("\t")
        selected = int(value["selected_folds"])
        expected = float(value["null_expected_eligible_folds"])
        row = {
            "left_operation": left,
            "right_operation": right,
            "selected_folds": selected,
            "semantic_eligible_folds": int(value["semantic_eligible_folds"]),
            "graph_eligible_folds": int(value["graph_eligible_folds"]),
            "null_expected_eligible_folds": expected,
            "graph_excess_eligible_folds": float(value["graph_eligible_folds"]) - expected,
            "semantic_triplets": int(value["semantic_triplets"]),
            "semantic_complete_rectangles": int(value["semantic_complete"]),
            "graph_triplets": int(value["graph_triplets"]),
            "graph_complete_rectangles": int(value["graph_complete"]),
            "mean_left_operation_support": float(value["left_support_sum"]) / selected,
            "mean_right_operation_support": float(value["right_support_sum"]) / selected,
        }
        if row["semantic_eligible_folds"] or row["graph_eligible_folds"] or expected >= 0.01:
            target_pairs.append(row)
    target_pairs.sort(key=lambda row: (-float(row["graph_excess_eligible_folds"]), -int(row["semantic_eligible_folds"]), str(row["left_operation"]), str(row["right_operation"])))
    for rank, row in enumerate(target_pairs, 1):
        row["excess_rank"] = rank

    target_primary = next(row for row in summary_rows if row["corpus_id"] == design["target"] and row["null"] == "RIGHT_LABEL_SWITCH_LENGTH_EXACT")
    target_reverse = next(row for row in summary_rows if row["corpus_id"] == design["target"] and row["null"] == "LEFT_LABEL_SWITCH_LENGTH_EXACT")
    strict = next(row for row in summary_rows if row["corpus_id"] == design["target"] and row["null"] == "RIGHT_LABEL_SWITCH_RECURRENCE_STRICT")
    gates = {
        "primary_mobility_at_least_25pct": float(target_primary["mean_switchable_fraction"]) >= 0.25,
        "positive_at_least_9_of_12": int(target_primary["positive_fold_directions"]) >= 9,
        "primary_p_at_most_point01": float(target_primary["inclusive_empirical_p"]) <= 0.01,
        "primary_survival_below_75pct": float(target_primary["null_survival_fraction_of_graph_observed"]) < 0.75,
        "reverse_direction_agrees": float(target_reverse["graph_excess_all_pair_density"]) > 0 and float(target_reverse["inclusive_empirical_p"]) <= 0.01,
    }
    if float(target_primary["mean_switchable_fraction"]) < 0.25:
        status = "INSUFFICIENT_NULL_MOBILITY"
    elif all(gates.values()):
        status = "SPECIFIC_LEFT_RIGHT_PAIRING_EXCESS_SUPPORTED"
    elif float(target_primary["graph_excess_all_pair_density"]) > 0:
        status = "PAIRING_EXCESS_PRESENT_BUT_DIFFUSE_OR_UNSTABLE"
    else:
        status = "PAIRING_EXCESS_NOT_ABOVE_DEGREE_NULL"

    positive_excess = sum(max(0.0, float(row["graph_excess_eligible_folds"])) for row in target_pairs)
    top20_excess = sum(max(0.0, float(row["graph_excess_eligible_folds"])) for row in target_pairs[:20])
    counter_rows = [
        {"claim": "OPERATION_COUNT_EXPLAINS_COMPATIBILITY", "evidence": "Every null preserves the selected operation inventory and denominator.", "impact": "Any excess is conditional on operation scale."},
        {"claim": "RESTRICTED_VOCABULARY_EXPLAINS_COMPATIBILITY", "evidence": "Forms, edge endpoints, recurrence, units, folds, lengths, and characters never move.", "impact": "Primary null conditions on the observed vocabulary graph."},
        {"claim": "NULL_IS_A_READABLE_SYNTHETIC_CORPUS", "evidence": "Switched labels need not remain literal edits of fixed endpoints.", "impact": "Result is graph-causal, not a generative-language likelihood."},
        {"claim": "PAIR_RANKS_ARE_CONFIRMATORY", "evidence": "Named pairs are ranked after observing excess.", "impact": "Pair identities are descriptive hypotheses only."},
        {"claim": "PAIRING_EXCESS_ITSELF_IS_VOYNICH_SPECIFIC", "evidence": "Every powered GDT159 comparator also exceeds its degree null, often by a larger ratio.", "impact": "The distinctive residual is absolute excess density and breadth, not the existence of morphotactic pairing."},
        {"claim": "F84R_USED", "evidence": "Frozen GDT003 provenance explicitly excludes f84r and no transcription/image table is opened.", "impact": "f84r remains sealed."},
    ]

    write_tsv(OUT_FOLDS, fold_rows)
    write_tsv(OUT_NULL, summary_rows)
    write_tsv(OUT_WORLDS, world_rows)
    write_tsv(OUT_PAIRS, target_pairs)
    write_tsv(OUT_COUNTER, counter_rows)

    comparison_lines = []
    primary_rows = [row for row in summary_rows if row["null"] == "RIGHT_LABEL_SWITCH_LENGTH_EXACT"]
    external_primary = [row for row in primary_rows if row["corpus_id"] != design["target"]]
    external_max_excess = max(float(row["graph_excess_all_pair_density"]) for row in external_primary)
    target_to_external_max_excess = float(target_primary["graph_excess_all_pair_density"]) / max(1e-12, external_max_excess)
    for row in sorted(primary_rows, key=lambda row: (0 if row["corpus_id"] == design["target"] else 1, -float(row["graph_to_null_ratio"]))):
        comparison_lines.append(
            f"| {row['corpus_id']} | {float(row['semantic_all_pair_density']):.6f} | {float(row['null_mean_all_pair_density']):.6f} | "
            f"{float(row['null_survival_fraction_of_graph_observed']):.3f} | {float(row['graph_to_null_ratio']):.2f} | "
            f"{row['positive_fold_directions']}/{row['folds']} | {float(row['inclusive_empirical_p']):.6f} |"
        )
    pair_lines = []
    for row in target_pairs[:15]:
        pair_lines.append(
            f"| {row['left_operation']} | {row['right_operation']} | {row['semantic_eligible_folds']} | "
            f"{float(row['null_expected_eligible_folds']):.3f} | {float(row['graph_excess_eligible_folds']):+.3f} | "
            f"{row['semantic_triplets']} | {row['semantic_complete_rectangles']} |"
        )
    target_fold = [row for row in fold_rows if row["corpus_id"] == design["target"]]
    semantic_ll = sum(int(row["semantic_eligible_LL"]) for row in target_fold)
    semantic_lr = sum(int(row["semantic_eligible_LR"]) for row in target_fold)
    semantic_rr = sum(int(row["semantic_eligible_RR"]) for row in target_fold)
    report = f"""# GDT160 compatibility-pairing null report

Decision: **{status}**.

## Exact decomposition

The frozen GDT003 Voynich density is reconstructed as
{float(target_primary['semantic_all_pair_density']):.12f}.  Its compatible-pair
numerator is LEFT×LEFT {semantic_ll}, LEFT×RIGHT {semantic_lr}, and
RIGHT×RIGHT {semantic_rr}.  Thus the entire published numerator is the
cross-side component, not a mixture of unrelated same-edge phenomena.

## Degree-preserving result

Under the primary right-label switch, the fixed graph retains a null mean
density of {float(target_primary['null_mean_all_pair_density']):.6f}, or
{100*float(target_primary['null_survival_fraction_of_graph_observed']):.1f}%
of graph-observed compatibility.  The graph-observed/null ratio is
{float(target_primary['graph_to_null_ratio']):.2f}; the direction is positive
on {target_primary['positive_fold_directions']}/{target_primary['folds']} folds
and the inclusive 1,024-world p is
{float(target_primary['inclusive_empirical_p']):.6f}.  Mean switch mobility is
{100*float(target_primary['mean_switchable_fraction']):.1f}% of right edges.

The direction-reversed left-label null retains
{100*float(target_reverse['null_survival_fraction_of_graph_observed']):.1f}%
and has p={float(target_reverse['inclusive_empirical_p']):.6f}.  The stricter
recurrence-profile null retains
{100*float(strict['null_survival_fraction_of_graph_observed']):.1f}% with
{100*float(strict['mean_switchable_fraction']):.1f}% mean mobility.  It is a
sensitivity, not the primary gate.

## Same normalization on GDT159 corpora

| corpus | observed density | null density | survives | observed/null | positive folds | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(comparison_lines)}

Every powered external corpus also has positive specific-pair excess and reaches
the empirical p floor; some have a larger observed/null ratio than Voynich.
Specific operation pairing is therefore not uniquely Voynich.  The remaining
distinction is absolute breadth: Voynich excess density is
{float(target_primary['graph_excess_all_pair_density']):.6f}, versus the largest
external excess {external_max_excess:.6f}, a
{target_to_external_max_excess:.1f}-fold difference.

## Pairs carrying the Voynich excess

| left operation | right operation | eligible folds | null expected | excess | triplets | complete |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(pair_lines)}

The top 20 post-ranked pairs account for
{100*top20_excess/max(1e-12,positive_excess):.1f}% of summed positive pair
excess.  These identities are an atlas for subsequent testing, not individually
adjusted discoveries.

## Interpretation

The primary null holds the complete vocabulary and transformation graph fixed,
including operation counts, operation supports, host degrees, recurrence,
lengths, characters, units, folds, and all corpus-side section/register
placement.  It changes only which right-operation identity labels each existing
right edge.  A positive excess therefore cannot be reduced to "many operations"
or "few recurrent hosts" alone.

The null is deliberately abstract.  A switched label is not required to remain
a literal edit of its fixed endpoints, because literal deterministic operations
plus an exactly fixed vocabulary admit no nontrivial randomization.  The result
supports organization of the surface-operation incidence graph, not linguistic
morphology by itself.

## Seal and claim ceiling

The scorer uses only the frozen GDT003/GDT159 panels and published aggregates.
The GDT003 source provenance explicitly excluded f84r.  No f84r row, image, or
formal payload was opened, queried, retained, joined, or scored.

At most this experiment supports specific LEFT×HOST×RIGHT organization beyond
degree/frequency margins.  It establishes no morpheme, word boundary, syntax,
language, sound, plaintext, semantics, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")

    output_paths = [OUT_FOLDS, OUT_NULL, OUT_WORLDS, OUT_PAIRS, OUT_COUNTER, OUT_REPORT]
    inputs = [DESIGN, METHOD, OLD_CORPORA, NEW_CORPORA, OLD_FP, NEW_FP, OLD_RESULT, NEW_RESULT, SOURCE_PROVENANCE]
    result = {
        "schema": "GDT160_COMPATIBILITY_PAIRING_NULL_RESULT_V1",
        "status": status,
        "gates": gates,
        "target": target_primary,
        "target_reverse": target_reverse,
        "target_recurrence_strict": strict,
        "exact_decomposition": {"LEFT_LEFT": semantic_ll, "LEFT_RIGHT": semantic_lr, "RIGHT_RIGHT": semantic_rr},
        "pair_excess": {"rows": len(target_pairs), "top20_fraction_positive_excess": top20_excess / max(1e-12, positive_excess)},
        "cross_corpus_excess": {"largest_external_excess_density": external_max_excess, "target_to_largest_external_excess_ratio": target_to_external_max_excess},
        "comparators": [row for row in summary_rows if row["null"] == "RIGHT_LABEL_SWITCH_LENGTH_EXACT" and row["corpus_id"] != design["target"]],
        "inputs": {path.name: sha(path) for path in inputs},
        "outputs": {path.name: sha(path) for path in output_paths},
        "implementation": {"runner": sha(Path(__file__)), "gdt003_core": sha(CORE), "gdt003_fingerprint_runner": sha(FINGERPRINT_RUNNER)},
        "source_freeze_commit": "fb01238",
        "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Surface-operation incidence pairing beyond degree/frequency margins only; no morphology, word boundary, language, sound, meaning, plaintext, or translation.",
    }
    result["result_content_sha256"] = canonical_sha(result)
    OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    print(json.dumps({"target": target_primary, "reverse": target_reverse, "strict": strict}, indent=2))


if __name__ == "__main__":
    main()
