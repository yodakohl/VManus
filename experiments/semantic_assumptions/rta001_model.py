#!/usr/bin/env python3
"""Transparent discrete-medoid model used by RTA001.

The CUDA path proposes assignments; all functions in this module are the
authoritative deterministic CPU implementation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

import numpy as np


REPRESENTATIONS = ("surface", "family", "member", "root", "construction")
READINGS = ("ZL3b", "IT2a", "RF1b")
K_GRID = (2, 4, 6, 8, 12, 16, 24, 32)
ABSTRACT_ORDER = ("construction", "root", "family", "member", "surface")
SCALE = 6


def universal(n: int) -> int:
    return 2 * int(math.floor(math.log2(n + 1))) + 1


def stable_seed(*parts: object) -> int:
    body = "|".join(map(str, parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(body).digest()[:8], "little")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def program_rows(results: Path, representation: str) -> list[dict[str, str]]:
    return read_tsv(results / f"rta001_edge_programs_{representation}.tsv")


@dataclass(frozen=True)
class EdgeMeta:
    edge_id: str
    panel_id: str
    physical_folio: str
    page: str
    relation_type: str
    relation_instance: str
    source_node: str
    target_node: str
    source_locus: str
    target_locus: str


@dataclass(frozen=True)
class FeatureData:
    representation: str
    vocabulary: tuple[str, ...]
    feature_names: tuple[str, ...]
    vectors: np.ndarray
    weights: np.ndarray
    raw_bits: np.ndarray
    edges: tuple[EdgeMeta, ...]
    medoid_programs: tuple[str, ...]


@dataclass(frozen=True)
class Model:
    representation: str
    k: int
    medoid_indices: tuple[int, ...]
    assignments: tuple[int, ...]
    assignment_costs_scaled: tuple[int, ...]
    library_bits_scaled: int
    residual_bits_scaled: int
    assignment_bits_scaled: int
    composition_bits_scaled: int
    cycle_bits_scaled: int
    rectangle_bits_scaled: int
    total_bits_scaled: int
    restart_seed: int
    proposal_backend: str


def _edge_groups(rows: list[dict[str, str]]) -> list[list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = {}
    order: list[str] = []
    for row in rows:
        if row["edge_id"] not in groups:
            groups[row["edge_id"]] = []
            order.append(row["edge_id"])
        groups[row["edge_id"]].append(row)
    return [groups[key] for key in order]


def build_feature_data(results: Path, representation: str) -> FeatureData:
    rows = program_rows(results, representation)
    groups = _edge_groups(rows)
    vocab = sorted(
        {
            token
            for row in rows
            if row["status"] == "EXACT_PROGRAM"
            for field in ("source_sequence_json", "target_sequence_json")
            for token in json.loads(row[field])
        }
    )
    atoms = sorted(
        {
            atom
            for row in rows
            if row["status"] == "EXACT_PROGRAM"
            for atom in json.loads(row["abstract_atom_counts_json"])
        }
    )
    feature_names = tuple([f"ATOM:{atom}" for atom in atoms] + [f"DELTA:{token}" for token in vocab] + [
        "SOURCE_LENGTH", "TARGET_LENGTH", "BOUNDARY_EDITS"
    ])
    atom_index = {value: index for index, value in enumerate(atoms)}
    vocab_index = {value: len(atoms) + index for index, value in enumerate(vocab)}
    vectors = []
    raw_bits = []
    edges = []
    programs = []
    for group in groups:
        exact = [row for row in group if row["status"] == "EXACT_PROGRAM"]
        if len(exact) not in {2, 3}:
            raise ValueError(f"edge has {len(exact)} readings: {group[0]['edge_id']}")
        per_reading: list[np.ndarray] = []
        bits = []
        canonical = []
        for row in exact:
            vector = np.zeros(len(feature_names), dtype=np.int32)
            for atom, count in json.loads(row["abstract_atom_counts_json"]).items():
                vector[atom_index[atom]] += int(count)
            source = json.loads(row["source_sequence_json"])
            target = json.loads(row["target_sequence_json"])
            for token in source:
                vector[vocab_index[token]] -= 1
            for token in target:
                vector[vocab_index[token]] += 1
            vector[-3] = len(source)
            vector[-2] = len(target)
            vector[-1] = sum(
                count for atom, count in json.loads(row["abstract_atom_counts_json"]).items() if "BOUNDARY" in atom
            )
            per_reading.append(vector)
            bits.append(int(row["description_length_bits"]))
            canonical.append(row["canonical_dsl_text"])
        total = np.sum(per_reading, axis=0, dtype=np.int32)
        scaled = total * (SCALE // len(per_reading))
        if np.any(scaled < np.iinfo(np.int16).min) or np.any(scaled > np.iinfo(np.int16).max):
            raise OverflowError("feature overflow")
        vectors.append(scaled.astype(np.int16))
        raw_bits.append(sum(bits) * SCALE // len(bits))
        programs.append(sorted(canonical)[0])
        first = group[0]
        edges.append(EdgeMeta(*(first[key] for key in [
            "edge_id", "panel_id", "physical_folio", "page", "relation_type", "relation_instance",
            "source_node", "target_node", "source_locus", "target_locus"
        ])))
    literal_weight = 1 + int(math.ceil(math.log2(len(vocab) + 1)))
    weights = np.array([2] * len(atoms) + [literal_weight] * len(vocab) + [2, 2, 2], dtype=np.int16)
    return FeatureData(
        representation,
        tuple(vocab),
        feature_names,
        np.stack(vectors),
        weights,
        np.array(raw_bits, dtype=np.int64),
        tuple(edges),
        tuple(programs),
    )


def weighted_distances(vectors: np.ndarray, medoids: np.ndarray, weights: np.ndarray) -> np.ndarray:
    diff = np.abs(vectors[:, None, :].astype(np.int32) - medoids[None, :, :].astype(np.int32))
    return np.sum(diff * weights[None, None, :].astype(np.int32), axis=2, dtype=np.int64)


def assign_cpu(vectors: np.ndarray, medoids: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    distances = weighted_distances(vectors, medoids, weights)
    assignments = np.argmin(distances, axis=1).astype(np.int32)
    return assignments, distances[np.arange(len(vectors)), assignments]


def initialize_medoids(vectors: np.ndarray, k: int, seed: int, weights: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(seed)
    first = int(rng.integers(0, len(vectors)))
    selected = [first]
    while len(selected) < k:
        distances = weighted_distances(vectors, vectors[selected], weights)
        nearest = np.min(distances, axis=1).astype(np.float64)
        nearest[selected] = 0
        if nearest.sum() == 0:
            candidate = next(i for i in range(len(vectors)) if i not in selected)
        else:
            candidate = int(rng.choice(len(vectors), p=nearest / nearest.sum()))
            if candidate in selected:
                candidate = next(i for i in range(len(vectors)) if i not in selected)
        selected.append(candidate)
    return np.array(selected, dtype=np.int32)


def hard_em(vectors: np.ndarray, weights: np.ndarray, initial: np.ndarray, iterations: int = 10) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    medoid_indices = np.array(initial, dtype=np.int32)
    for _ in range(iterations):
        assignments, costs = assign_cpu(vectors, vectors[medoid_indices], weights)
        updated = medoid_indices.copy()
        for cluster in range(len(medoid_indices)):
            members = np.flatnonzero(assignments == cluster)
            if len(members) == 0:
                order = np.argsort(-costs, kind="stable")
                updated[cluster] = int(next(i for i in order if i not in set(updated)))
                continue
            distances = weighted_distances(vectors[members], vectors[members], weights)
            totals = distances.sum(axis=0)
            updated[cluster] = int(members[int(np.argmin(totals))])
        if np.array_equal(updated, medoid_indices):
            break
        medoid_indices = updated
    assignments, costs = assign_cpu(vectors, vectors[medoid_indices], weights)
    return medoid_indices, assignments, costs


def random_proposals(vectors: np.ndarray, weights: np.ndarray, k: int, restarts: int, key: str) -> tuple[np.ndarray, np.ndarray]:
    all_medoids = []
    seeds = []
    for restart in range(restarts):
        seed = stable_seed("RTA001", key, k, restart)
        all_medoids.append(initialize_medoids(vectors, k, seed, weights))
        seeds.append(seed)
    return np.stack(all_medoids), np.array(seeds, dtype=np.uint64)


def improve_swaps(vectors: np.ndarray, weights: np.ndarray, medoids: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    current = np.array(medoids, dtype=np.int32)
    assignments, costs = assign_cpu(vectors, vectors[current], weights)
    total = int(costs.sum())
    while True:
        selected = set(map(int, current))
        found = None
        for slot in range(len(current)):
            for candidate in range(len(vectors)):
                if candidate in selected:
                    continue
                trial = current.copy()
                trial[slot] = candidate
                trial_assignments, trial_costs = assign_cpu(vectors, vectors[trial], weights)
                trial_total = int(trial_costs.sum())
                if trial_total < total:
                    found = (trial, trial_assignments, trial_costs, trial_total)
                    break
            if found is not None:
                break
        if found is None:
            return current, assignments, costs
        current, assignments, costs, total = found


def medoid_library_bits(data: FeatureData, medoids: Sequence[int]) -> int:
    total = universal(len(medoids)) * SCALE
    for index in medoids:
        nonzero = int(np.count_nonzero(data.vectors[index]))
        explicit = int(np.sum(np.abs(data.vectors[index].astype(np.int32)) * data.weights.astype(np.int32), dtype=np.int64))
        total += universal(nonzero) * SCALE + explicit
    return total


def categorical_model_costs(vectors: np.ndarray, assignments: np.ndarray, k: int) -> tuple[np.ndarray, int]:
    """Leave-one-out integer-bit codes and distribution-library bits."""
    costs = np.zeros(len(vectors), dtype=np.int64)
    library = 0
    for cluster in range(k):
        members = np.flatnonzero(assignments == cluster)
        if not len(members):
            continue
        base = vectors[members]
        for dimension in range(vectors.shape[1]):
            values, counts = np.unique(base[:, dimension], return_counts=True)
            count_map = {int(value): int(count) for value, count in zip(values, counts)}
            u = len(values) + 1  # one frozen unseen value
            library += universal(len(values)) * SCALE
            denominator = len(members) - 1 + u
            for index in members:
                numerator = count_map[int(vectors[index, dimension])]
                costs[index] += int(round(-math.log2(numerator / denominator) * SCALE))
    return costs, library


def categorical_test_costs(train_vectors: np.ndarray, train_assignments: np.ndarray, k: int,
                           test_vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scores = np.zeros((len(test_vectors), k), dtype=np.int64)
    for cluster in range(k):
        members = np.flatnonzero(train_assignments == cluster)
        if not len(members):
            scores[:, cluster] = np.iinfo(np.int32).max
            continue
        base = train_vectors[members]
        for dimension in range(train_vectors.shape[1]):
            values, counts = np.unique(base[:, dimension], return_counts=True)
            count_map = {int(value): int(count) for value, count in zip(values, counts)}
            u = len(values) + 1
            denominator = len(members) + u
            for row in range(len(test_vectors)):
                numerator = count_map.get(int(test_vectors[row, dimension]), 0) + 1
                scores[row, cluster] += int(round(-math.log2(numerator / denominator) * SCALE))
    assignments = np.argmin(scores, axis=1).astype(np.int32)
    return assignments, scores[np.arange(len(test_vectors)), assignments]


def algebra_bits(data: FeatureData, assignments: Sequence[int], medoids: Sequence[int]) -> tuple[int, int, int]:
    assignment_by_edge = {edge.edge_id: int(assignments[i]) for i, edge in enumerate(data.edges)}
    medoid_vectors = data.vectors[np.array(medoids)]
    composition = 0
    by_panel_record: dict[tuple[str, str], dict[tuple[str, str], str]] = {}
    for edge in data.edges:
        if edge.relation_type not in {"ROW_SUCCESSOR", "ROW_SKIP_ONE"}:
            continue
        record = edge.source_node.rsplit(":R", 1)[0]
        srow = edge.source_node.rsplit(":R", 1)[-1]
        trow = edge.target_node.rsplit(":R", 1)[-1]
        by_panel_record.setdefault((edge.panel_id, record), {})[(srow, trow)] = edge.edge_id
    delta_start = next(i for i, name in enumerate(data.feature_names) if name.startswith("DELTA:"))
    delta_end = len(data.feature_names) - 3
    literal_weight = data.weights[delta_start:delta_end].astype(np.int32)
    for relation in by_panel_record.values():
        if all(key in relation for key in [("1", "2"), ("2", "3"), ("1", "3")]):
            v12 = medoid_vectors[assignment_by_edge[relation[("1", "2")]], delta_start:delta_end].astype(np.int32)
            v23 = medoid_vectors[assignment_by_edge[relation[("2", "3")]], delta_start:delta_end].astype(np.int32)
            v13 = medoid_vectors[assignment_by_edge[relation[("1", "3")]], delta_start:delta_end].astype(np.int32)
            composition += int(np.sum(np.abs(v12 + v23 - v13) * literal_weight, dtype=np.int64))
    cycle = 0
    panels: dict[str, list[int]] = {}
    for i, edge in enumerate(data.edges):
        if edge.relation_type == "CYCLIC_SUCCESSOR":
            panels.setdefault(edge.panel_id, []).append(i)
    for indices in panels.values():
        combined = np.zeros(delta_end - delta_start, dtype=np.int32)
        for index in indices:
            # Closure is scored on the explicit edge transformation. The
            # library earns compression separately; a medoid may not erase a
            # planted closure violation from the algebra diagnostic.
            combined += data.vectors[index, delta_start:delta_end].astype(np.int32)
        cycle += int(np.sum(np.abs(combined) * literal_weight, dtype=np.int64))
    return composition, cycle, 0


def make_model(data: FeatureData, medoids: np.ndarray, assignments: np.ndarray, costs: np.ndarray, seed: int, backend: str) -> Model:
    k = len(medoids)
    categorical_costs, distribution_library = categorical_model_costs(data.vectors, assignments, k)
    library = medoid_library_bits(data, medoids) + distribution_library
    assignment_bits = len(data.edges) * int(math.ceil(math.log2(max(2, k)))) * SCALE
    residual = int(categorical_costs.sum())
    composition, cycle, rectangle = algebra_bits(data, assignments, medoids)
    total = library + assignment_bits + residual + 2 * composition + 2 * cycle + 2 * rectangle
    return Model(data.representation, k, tuple(map(int, medoids)), tuple(map(int, assignments)), tuple(map(int, costs)),
                 library, residual, assignment_bits, composition, cycle, rectangle, total, int(seed), backend)


def fit_model(
    data: FeatureData,
    k: int,
    key: str,
    restarts: int,
    gpu_assign: Callable[[np.ndarray, np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray]] | None = None,
) -> Model:
    proposals, seeds = random_proposals(data.vectors, data.weights, k, restarts, key)
    if gpu_assign is not None:
        gpu_assignments, gpu_costs = gpu_assign(data.vectors, data.vectors[proposals], data.weights)
        if gpu_assignments.shape != (restarts, len(data.edges)):
            raise ValueError("bad GPU proposal shape")
        order = np.argsort(gpu_costs.sum(axis=1), kind="stable")
        candidate_restarts = order[: min(8, len(order))]
        backend = "CUDA_PROPOSAL_CPU_EXACT"
    else:
        candidate_restarts = np.arange(restarts)
        backend = "CPU_PROPOSAL_CPU_EXACT"
    models = []
    for restart in candidate_restarts:
        medoids, assignments, costs = hard_em(data.vectors, data.weights, proposals[restart])
        models.append(make_model(data, medoids, assignments, costs, int(seeds[restart]), backend))
    return min(models, key=lambda model: (model.total_bits_scaled, model.medoid_indices, model.restart_seed))


def subset(data: FeatureData, indices: Sequence[int]) -> FeatureData:
    index = np.array(indices, dtype=np.int64)
    return FeatureData(data.representation, data.vocabulary, data.feature_names, data.vectors[index], data.weights,
                       data.raw_bits[index], tuple(data.edges[i] for i in index), tuple(data.medoid_programs[i] for i in index))


def training_projection(data: FeatureData, train_indices: Sequence[int], test_indices: Sequence[int]) -> tuple[FeatureData, FeatureData]:
    """Project one fold to its training-only literal vocabulary plus UNSEEN."""
    names = list(data.feature_names)
    delta_start = next(i for i, name in enumerate(names) if name.startswith("DELTA:"))
    delta_end = len(names) - 3
    train_rows = np.array(train_indices, dtype=np.int64)
    used_delta = [i for i in range(delta_start, delta_end) if np.any(data.vectors[train_rows, i] != 0)]
    unseen_delta = [i for i in range(delta_start, delta_end) if i not in set(used_delta)]
    fixed = list(range(delta_start))
    tail = list(range(delta_end, len(names)))

    def project(indices: Sequence[int]) -> FeatureData:
        rows = np.array(indices, dtype=np.int64)
        kept = data.vectors[np.ix_(rows, np.array(fixed + used_delta + tail, dtype=np.int64))].astype(np.int32)
        unseen = (data.vectors[np.ix_(rows, np.array(unseen_delta, dtype=np.int64))].sum(axis=1, dtype=np.int32)
                  if unseen_delta else np.zeros(len(rows), dtype=np.int32))
        insert_at = len(fixed) + len(used_delta)
        projected = np.insert(kept, insert_at, unseen, axis=1)
        if np.any(projected < np.iinfo(np.int16).min) or np.any(projected > np.iinfo(np.int16).max):
            raise OverflowError("fold projection overflow")
        feature_names = tuple([names[i] for i in fixed + used_delta] + ["DELTA:UNSEEN_LITERAL"] + [names[i] for i in tail])
        literal_weight = 1 + int(math.ceil(math.log2(len(used_delta) + 2)))
        weights = np.array([int(data.weights[i]) for i in fixed] + [literal_weight] * (len(used_delta) + 1) +
                           [int(data.weights[i]) for i in tail], dtype=np.int16)
        vocabulary = tuple(names[i].split(":", 1)[1] for i in used_delta) + ("UNSEEN_LITERAL",)
        return FeatureData(data.representation, vocabulary, feature_names, projected.astype(np.int16), weights,
                           data.raw_bits[rows], tuple(data.edges[i] for i in rows),
                           tuple(data.medoid_programs[i] for i in rows))

    return project(train_indices), project(test_indices)


def score_model(train: FeatureData, model: Model, test: FeatureData) -> tuple[np.ndarray, np.ndarray]:
    assignments, costs = categorical_test_costs(train.vectors, np.array(model.assignments), model.k, test.vectors)
    per_edge = costs + int(math.ceil(math.log2(max(2, model.k)))) * SCALE
    return assignments, per_edge


def baseline_scores(train: FeatureData, test: FeatureData) -> dict[str, np.ndarray]:
    one = np.array([int(np.argmin(weighted_distances(train.vectors, train.vectors, train.weights).sum(axis=0)))])
    _, edge_independent = assign_cpu(test.vectors, train.vectors[one], train.weights)
    relation = np.zeros(len(test.edges), dtype=np.int64)
    length = np.zeros(len(test.edges), dtype=np.int64)
    for i, edge in enumerate(test.edges):
        same_type = [j for j, candidate in enumerate(train.edges) if candidate.relation_type == edge.relation_type]
        candidates = same_type or list(range(len(train.edges)))
        distances = weighted_distances(test.vectors[i : i + 1], train.vectors[candidates], train.weights)[0]
        relation[i] = int(np.min(distances))
        src_len, dst_len = int(test.vectors[i, -3]), int(test.vectors[i, -2])
        exact = [j for j in candidates if int(train.vectors[j, -3]) == src_len and int(train.vectors[j, -2]) == dst_len]
        length[i] = int(np.min(weighted_distances(test.vectors[i : i + 1], train.vectors[exact], train.weights))) if exact else relation[i]
    return {"edge_independent": edge_independent, "relation_type_only": relation, "source_target_length_matched": length}


def baseline_training_and_test(train: FeatureData, test: FeatureData) -> dict[str, dict[str, object]]:
    full = weighted_distances(train.vectors, train.vectors, train.weights)
    one_index = int(np.argmin(full.sum(axis=0)))
    edge_assignments = np.zeros(len(train.edges), dtype=np.int32)
    edge_train, edge_distribution_library = categorical_model_costs(train.vectors, edge_assignments, 1)
    _, edge_test = categorical_test_costs(train.vectors, edge_assignments, 1, test.vectors)
    edge_library = medoid_library_bits(train, [one_index]) + edge_distribution_library

    type_indices: dict[str, int] = {}
    type_assignment = np.zeros(len(train.edges), dtype=np.int32)
    for cluster, relation_type in enumerate(sorted({edge.relation_type for edge in train.edges})):
        members = [i for i, edge in enumerate(train.edges) if edge.relation_type == relation_type]
        distances = weighted_distances(train.vectors[members], train.vectors[members], train.weights)
        medoid = members[int(np.argmin(distances.sum(axis=0)))]
        type_indices[relation_type] = medoid
        type_assignment[members] = cluster
    type_train, type_distribution_library = categorical_model_costs(train.vectors, type_assignment, len(type_indices))
    type_scores = np.zeros(len(test.edges), dtype=np.int64)
    for relation_type, medoid in type_indices.items():
        members = np.flatnonzero(type_assignment == sorted(type_indices).index(relation_type))
        test_members = [i for i, edge in enumerate(test.edges) if edge.relation_type == relation_type]
        if test_members:
            _, values = categorical_test_costs(train.vectors[members], np.zeros(len(members), dtype=np.int32), 1,
                                                test.vectors[np.array(test_members)])
            type_scores[test_members] = values
    missing_types = [i for i, edge in enumerate(test.edges) if edge.relation_type not in type_indices]
    if missing_types: type_scores[missing_types] = edge_test[missing_types]
    type_test = type_scores
    type_library = medoid_library_bits(train, sorted(set(type_indices.values()))) + type_distribution_library

    cell_indices: dict[tuple[str, int, int], int] = {}
    cell_assignment = np.zeros(len(train.edges), dtype=np.int32)
    cell_keys = sorted({(edge.relation_type, int(train.vectors[i, -3]), int(train.vectors[i, -2]))
                        for i, edge in enumerate(train.edges)})
    for cluster, key in enumerate(cell_keys):
        members = [i for i, edge in enumerate(train.edges)
                   if (edge.relation_type, int(train.vectors[i, -3]), int(train.vectors[i, -2])) == key]
        distances = weighted_distances(train.vectors[members], train.vectors[members], train.weights)
        medoid = members[int(np.argmin(distances.sum(axis=0)))]
        cell_indices[key] = medoid
        cell_assignment[members] = cluster
    cell_train, cell_distribution_library = categorical_model_costs(train.vectors, cell_assignment, len(cell_keys))
    cell_test = np.zeros(len(test.edges), dtype=np.int64)
    for i, edge in enumerate(test.edges):
        key = (edge.relation_type, int(test.vectors[i, -3]), int(test.vectors[i, -2]))
        if key in cell_indices:
            cluster = cell_keys.index(key)
            members = np.flatnonzero(cell_assignment == cluster)
            _, values = categorical_test_costs(train.vectors[members], np.zeros(len(members), dtype=np.int32), 1,
                                                test.vectors[i:i+1])
            cell_test[i] = values[0]
        else:
            cell_test[i] = type_test[i]
    cell_library = medoid_library_bits(train, sorted(set(cell_indices.values()))) + cell_distribution_library

    payload = {}
    for name, train_cost, test_cost, library in [
        ("edge_independent", edge_train, edge_test, edge_library),
        ("relation_type_only", type_train, type_test, type_library),
        ("source_target_length_matched", cell_train, cell_test, cell_library),
    ]:
        payload[name] = {
            "training_total_scaled": int(library + train_cost.sum()),
            "library_bits_scaled": int(library),
            "test_costs_scaled": test_cost,
        }
    return payload


def benchmark_backend(data: FeatureData, proposer: object | None) -> dict[str, object]:
    rows = min(512, len(data.edges))
    vectors = data.vectors[:rows]
    k = min(8, rows)
    benchmark_restarts = 1024
    proposals, _ = random_proposals(vectors, data.weights, k, benchmark_restarts, "BENCHMARK")
    medoids = vectors[proposals]
    start = time.perf_counter()
    cpu_assignments = np.empty((benchmark_restarts, rows), dtype="<i4")
    cpu_costs = np.empty((benchmark_restarts, rows), dtype="<u8")
    for restart in range(benchmark_restarts):
        assignments, costs = assign_cpu(vectors, medoids[restart], data.weights)
        cpu_assignments[restart] = assignments
        cpu_costs[restart] = costs
    cpu_seconds = time.perf_counter() - start
    cpu_digest = hashlib.sha256(cpu_assignments.tobytes() + cpu_costs.tobytes()).hexdigest()
    result: dict[str, object] = {"restarts": benchmark_restarts, "cpu_seconds": cpu_seconds, "cpu_sha256": cpu_digest}
    if proposer is None:
        result.update({"cuda_available": False, "selected_backend": "CPU", "reason": "CUDA proposer unavailable"})
        return result
    start = time.perf_counter()
    assignments, costs = proposer.assign_many(vectors, medoids, data.weights)
    cuda_seconds = time.perf_counter() - start
    cuda_digest = hashlib.sha256(assignments.astype("<i4").tobytes() + costs.astype("<u8").tobytes()).hexdigest()
    if cuda_digest != result["cpu_sha256"]:
        raise RuntimeError("CUDA proposal differs from exact CPU assignment")
    speedup = cpu_seconds / max(cuda_seconds, 1e-12)
    result.update({"cuda_available": True, "cuda_seconds": cuda_seconds, "cuda_sha256": cuda_digest,
                   "cuda_speedup": speedup, "selected_backend": "CUDA" if speedup >= 1.25 else "CPU",
                   "reason": "speed threshold met" if speedup >= 1.25 else "speed threshold not met"})
    return result
