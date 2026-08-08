#!/usr/bin/env python3
"""IL006: page-conditioned cross-root adjacency inside physical lines."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_il001_information_location import (  # noqa: E402
    Root,
    SOURCES,
    bootstrap_ci,
    load_lines,
    sha256_path,
    sign_flip_p,
    split_name,
    stable_int,
)
from run_il003_multiscale_boundaries import METADATA, map_signature, weight_maps  # noqa: E402
from run_il005_conditional_root_recency import (  # noqa: E402
    PageSequence,
    Position,
    build_pages,
    marginal_signature,
    metadata_rows,
    random_assignment,
    root_free_signature,
)


PREREG = HERE / "hypotheses" / "IL006_PAGE_CONDITIONED_ROOT_ADJACENCY_PREREGISTRATION.md"
DEPENDENCIES = (
    HERE / "run_il001_information_location.py",
    HERE / "run_il002_matched_line_pairs.py",
    HERE / "run_il003_multiscale_boundaries.py",
    HERE / "run_il005_conditional_root_recency.py",
)
RESULTS = HERE / "results"
FROZEN = RESULTS / "il006_page_conditioned_root_adjacency_validation_frozen.json"
OUTPUT_JSON = RESULTS / "il006_page_conditioned_root_adjacency_results.json"
OUTPUT_REPORT = RESULTS / "il006_page_conditioned_root_adjacency_report.md"
VALIDATION_FAILURE = RESULTS / "il006_page_conditioned_root_adjacency_validation_failure.md"
ORIENTATIONS = ("DC", "CD")
TAU = 8.0
GLOBAL_MIXTURE = 0.5
NULL_REPEATS = 2_048
MIN_EDGES = 10
MIN_MOVABLE = 6
MAX_WORKERS = 32
SEED = 6_600_006


@dataclass(frozen=True)
class Edge:
    orientation: str
    d_root: Root
    c_root: Root


class EdgeModel:
    def __init__(
        self,
        train_pages: Sequence[PageSequence],
        d_weights: dict[Root, float],
        c_weights: dict[Root, float],
    ):
        self.d_roots = tuple(sorted(d_weights))
        self.c_roots = tuple(sorted(c_weights))
        self.d_set = frozenset(self.d_roots)
        self.c_set = frozenset(self.c_roots)
        self.d_index = {root: index for index, root in enumerate(self.d_roots)}
        self.c_index = {root: index for index, root in enumerate(self.c_roots)}
        self.orientation_index = {value: index for index, value in enumerate(ORIENTATIONS)}
        global_counts = np.zeros((len(ORIENTATIONS), len(self.c_roots)), dtype=np.float64)
        pair_counts = np.zeros(
            (len(ORIENTATIONS), len(self.d_roots), len(self.c_roots)),
            dtype=np.float64,
        )
        for page in train_pages:
            labels = [position.root for position in page.positions]
            for edge in extract_edges(page, labels, self.d_set):
                oi = self.orientation_index[edge.orientation]
                di = self.d_index[edge.d_root]
                ci = self.c_index[edge.c_root]
                global_counts[oi, ci] += 1.0
                pair_counts[oi, di, ci] += 1.0
        denominators = global_counts.sum(axis=1, keepdims=True) + 0.5 * len(self.c_roots)
        self.global_distribution = (global_counts + 0.5) / denominators
        row_totals = pair_counts.sum(axis=2, keepdims=True)
        self.conditional = (
            pair_counts + TAU * self.global_distribution[:, None, :]
        ) / (row_totals + TAU)

    def edge_score(self, edge: Edge) -> float:
        oi = self.orientation_index[edge.orientation]
        di = self.d_index[edge.d_root]
        ci = self.c_index[edge.c_root]
        conditional = self.conditional[oi, di, ci]
        global_value = self.global_distribution[oi, ci]
        query = GLOBAL_MIXTURE * global_value + (1.0 - GLOBAL_MIXTURE) * conditional
        return float(math.log2(query / global_value))

    def signature(self) -> str:
        payload = b"".join((
            np.asarray(self.global_distribution, dtype="<f8").tobytes(),
            np.asarray(self.conditional, dtype="<f8").tobytes(),
        ))
        return hashlib.sha256(payload).hexdigest()


def extract_edges(
    page: PageSequence, labels: Sequence[Root], d_set: frozenset[Root]
) -> list[Edge]:
    by_line: dict[int, list[tuple[int, Root]]] = defaultdict(list)
    for position, root in zip(page.positions, labels):
        by_line[position.line_index].append((position.token_index, root))
    output = []
    for selected in by_line.values():
        selected.sort()
        for (left_index, left), (right_index, right) in zip(selected, selected[1:]):
            if right_index != left_index + 1:
                continue
            left_d = left in d_set
            right_d = right in d_set
            if left_d == right_d:
                continue
            output.append(
                Edge("DC", left, right) if left_d else Edge("CD", right, left)
            )
    return output


def adjacency_score(
    page: PageSequence, labels: Sequence[Root], model: EdgeModel
) -> tuple[float, int]:
    edges = extract_edges(page, labels, model.d_set)
    if not edges:
        return float("nan"), 0
    return float(np.mean([model.edge_score(edge) for edge in edges])), len(edges)


def cell_indices(
    page: PageSequence, labels: Sequence[Root], d_set: frozenset[Root]
) -> tuple[tuple[int, ...], ...]:
    cells: dict[tuple[Any, ...], list[int]] = defaultdict(list)
    for index, (position, root) in enumerate(zip(page.positions, labels)):
        key = (
            "D" if root in d_set else "C",
            position.stratum,
            position.shell,
            position.position_bin,
            position.paragraph_opening,
        )
        cells[key].append(index)
    return tuple(tuple(value) for _key, value in sorted(cells.items(), key=lambda row: repr(row[0])))


def variable_cells(
    labels: Sequence[Root], cells: Sequence[Sequence[int]]
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(indices) for indices in cells
        if len(indices) >= 2 and len({labels[index] for index in indices}) >= 2
    )


def mobility(
    labels: Sequence[Root], cells: Sequence[Sequence[int]], d_set: frozenset[Root]
) -> tuple[int, int]:
    d_movable = 0
    c_movable = 0
    for indices in variable_cells(labels, cells):
        if labels[indices[0]] in d_set:
            d_movable += len(indices)
        else:
            c_movable += len(indices)
    return d_movable, c_movable


def normalization_gate(model: EdgeModel, pages: Sequence[PageSequence]) -> dict[str, Any]:
    global_sums = model.global_distribution.sum(axis=1)
    conditional_sums = model.conditional.sum(axis=2)
    finite = bool(
        np.all(np.isfinite(model.global_distribution))
        and np.all(np.isfinite(model.conditional))
    )
    maximum_error = float(max(
        np.max(np.abs(global_sums - 1.0)),
        np.max(np.abs(conditional_sums - 1.0)),
    ))
    scores = []
    for page in pages:
        labels = [position.root for position in page.positions]
        for edge in extract_edges(page, labels, model.d_set)[:20]:
            scores.append(model.edge_score(edge))
        if len(scores) >= 100:
            break
    finite &= bool(scores and np.all(np.isfinite(scores)))
    return {
        "passed": finite and maximum_error < 1e-10,
        "all_finite": finite,
        "maximum_probability_error": maximum_error,
        "global_rows_checked": len(ORIENTATIONS),
        "conditional_rows_checked": int(np.prod(conditional_sums.shape)),
        "edge_scores_checked": len(scores),
    }


def greedy_plant(
    page: PageSequence,
    original: Sequence[Root],
    cells: Sequence[Sequence[int]],
    model: EdgeModel,
) -> tuple[list[Root], int, int]:
    labels = list(original)
    selected = variable_cells(labels, cells)
    movable = sum(len(indices) for indices in selected)
    budget = math.ceil(0.10 * movable / 2)
    used = 0
    for _step in range(budget):
        baseline, _count = adjacency_score(page, labels, model)
        best_gain = 0.0
        best_pair: tuple[int, int] | None = None
        best_order: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None
        for indices in selected:
            for offset, left in enumerate(indices):
                for right in indices[offset + 1:]:
                    if labels[left] == labels[right]:
                        continue
                    labels[left], labels[right] = labels[right], labels[left]
                    candidate, _candidate_count = adjacency_score(page, labels, model)
                    labels[left], labels[right] = labels[right], labels[left]
                    gain = candidate - baseline
                    order = (page.positions[left].order_key, page.positions[right].order_key)
                    if (
                        gain > best_gain + 1e-15
                        or (
                            abs(gain - best_gain) <= 1e-15
                            and gain > 0
                            and (best_order is None or order < best_order)
                        )
                    ):
                        best_gain = gain
                        best_pair = (left, right)
                        best_order = order
        if best_pair is None or best_gain <= 1e-15:
            break
        left, right = best_pair
        labels[left], labels[right] = labels[right], labels[left]
        used += 1
    return labels, used, movable


def page_evaluation(
    job: tuple[PageSequence, EdgeModel, int, bool]
) -> dict[str, Any]:
    page, model, repeats, with_plant = job
    original = [position.root for position in page.positions]
    cells = cell_indices(page, original, model.d_set)
    d_movable, c_movable = mobility(original, cells, model.d_set)
    observed, edge_count = adjacency_score(page, original, model)
    if edge_count < MIN_EDGES or min(d_movable, c_movable) < MIN_MOVABLE:
        raise RuntimeError("ineligible page passed to IL006 worker")
    original_marginal = marginal_signature(original, cells)
    original_root_free = root_free_signature(page)
    rng = np.random.default_rng(stable_int(f"IL006|{page.page}|NULL"))
    negative_labels = random_assignment(original, cells, rng)
    negative, negative_edges = adjacency_score(page, negative_labels, model)
    integrity = bool(
        negative_edges == edge_count
        and marginal_signature(negative_labels, cells) == original_marginal
    )
    null_scores = []
    last_labels = negative_labels
    for _repeat in range(repeats):
        labels = random_assignment(original, cells, rng)
        score, count = adjacency_score(page, labels, model)
        integrity &= count == edge_count
        null_scores.append(score)
        last_labels = labels
    integrity &= marginal_signature(last_labels, cells) == original_marginal
    integrity &= root_free_signature(page) == original_root_free
    null_mean = float(np.mean(null_scores))
    planted: float | None = None
    plant_swaps = 0
    if with_plant:
        planted_labels, plant_swaps, plant_movable = greedy_plant(
            page, original, cells, model
        )
        if plant_movable != d_movable + c_movable:
            raise RuntimeError("IL006 plant mobility changed")
        integrity &= marginal_signature(planted_labels, cells) == original_marginal
        planted, planted_edges = adjacency_score(page, planted_labels, model)
        integrity &= planted_edges == edge_count
    return {
        "page": page.page,
        "eligible_edges": edge_count,
        "movable_D": d_movable,
        "movable_C": c_movable,
        "observed_score": observed,
        "negative_score": negative,
        "null_mean": null_mean,
        "residual": observed - null_mean,
        "negative_residual": negative - null_mean,
        "planted_score": planted,
        "plant_increment": planted - observed if planted is not None else None,
        "plant_swaps": plant_swaps,
        "integrity": integrity,
        "cell_marginal_sha256": original_marginal,
        "root_free_sha256": original_root_free,
        "null_scores": null_scores,
    }


def conditional_p(rows: Sequence[dict[str, Any]], field: str) -> float:
    observed = float(np.mean([row[field] for row in rows]))
    null = np.asarray([row["null_scores"] for row in rows], dtype=np.float64)
    centered = null - null.mean(axis=1, keepdims=True)
    replicate_means = centered.mean(axis=0)
    return float((np.count_nonzero(replicate_means >= observed - 1e-15) + 1) / (len(replicate_means) + 1))


def aggregate(rows: Sequence[dict[str, Any]], possible: int, with_plant: bool) -> dict[str, Any]:
    residuals = [row["residual"] for row in rows]
    negatives = [row["negative_residual"] for row in rows]
    sign_p = sign_flip_p(residuals, SEED + 10)
    randomization_p = conditional_p(rows, "residual") if rows else 1.0
    negative_sign_p = sign_flip_p(negatives, SEED + 11)
    negative_randomization_p = conditional_p(rows, "negative_residual") if rows else 1.0
    low, high = bootstrap_ci(residuals, SEED + 12)
    result = {
        "possible_pages": possible,
        "evaluated_pages": len(rows),
        "coverage": len(rows) / possible if possible else 0.0,
        "mean_observed_score": float(np.mean([row["observed_score"] for row in rows])) if rows else float("nan"),
        "mean_null_score": float(np.mean([row["null_mean"] for row in rows])) if rows else float("nan"),
        "mean_residual_bits_per_edge": float(np.mean(residuals)) if residuals else float("nan"),
        "positive_page_fraction": sum(value > 0 for value in residuals) / len(residuals) if residuals else 0.0,
        "sign_flip_p": sign_p,
        "conditional_randomization_p": randomization_p,
        "conservative_p": max(sign_p, randomization_p),
        "bootstrap_95_ci": [low, high],
        "negative": {
            "mean_residual_bits_per_edge": float(np.mean(negatives)) if negatives else float("nan"),
            "positive_page_fraction": sum(value > 0 for value in negatives) / len(negatives) if negatives else 0.0,
            "sign_flip_p": negative_sign_p,
            "conditional_randomization_p": negative_randomization_p,
            "conservative_p": max(negative_sign_p, negative_randomization_p),
        },
        "all_integrity": all(row["integrity"] for row in rows),
        "null_matrix_sha256": hashlib.sha256(
            np.asarray([row["null_scores"] for row in rows], dtype="<f8").tobytes()
        ).hexdigest(),
        "page_rows": [
            {key: value for key, value in row.items() if key != "null_scores"}
            for row in rows
        ],
    }
    if with_plant:
        increments = [row["plant_increment"] for row in rows]
        result["plant"] = {
            "mean_increment_bits_per_edge": float(np.mean(increments)) if increments else float("nan"),
            "positive_page_fraction": sum(value > 0 for value in increments) / len(increments) if increments else 0.0,
            "sign_flip_p": sign_flip_p(increments, SEED + 13),
            "total_swaps": sum(row["plant_swaps"] for row in rows),
        }
    return result


def evaluate_pages(
    pages: Sequence[PageSequence],
    model: EdgeModel,
    with_plant: bool,
    allowed_pages: set[str] | None = None,
) -> dict[str, Any]:
    base = []
    jobs = []
    for page in pages:
        if allowed_pages is not None and page.page not in allowed_pages:
            continue
        original = [position.root for position in page.positions]
        _score, edge_count = adjacency_score(page, original, model)
        if edge_count < MIN_EDGES:
            continue
        base.append(page)
        cells = cell_indices(page, original, model.d_set)
        d_movable, c_movable = mobility(original, cells, model.d_set)
        if min(d_movable, c_movable) >= MIN_MOVABLE:
            jobs.append((page, model, NULL_REPEATS, with_plant))
    workers = min(MAX_WORKERS, max(1, len(jobs)))
    if workers == 1:
        rows = [page_evaluation(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            rows = list(executor.map(page_evaluation, jobs, chunksize=1))
    rows.sort(key=lambda row: row["page"])
    return aggregate(rows, len(base), with_plant)


def material(result: dict[str, Any], p_threshold: float) -> bool:
    return bool(
        result["mean_residual_bits_per_edge"] >= 0.02
        and result["positive_page_fraction"] >= 0.60
        and result["conservative_p"] <= p_threshold
        and result["coverage"] >= 0.70
    )


def provenance() -> dict[str, Any]:
    return {
        "runner_sha256": sha256_path(Path(__file__)),
        "dependency_sha256": {path.name: sha256_path(path) for path in DEPENDENCIES},
        "preregistration_sha256": sha256_path(PREREG),
        "metadata_sha256": sha256_path(METADATA),
        "source_sha256": {name: sha256_path(path) for name, path in SOURCES.items()},
    }


def verify_provenance(frozen: dict[str, Any]) -> None:
    for key, value in provenance().items():
        if frozen.get(key) != value:
            raise RuntimeError(f"IL006 provenance changed after validation: {key}")


def validation_phase() -> None:
    started = time.perf_counter()
    d_weights, c_weights, form_weights = weight_maps()
    all_weights = {**d_weights, **c_weights}
    rows = metadata_rows()
    pages = build_pages(load_lines(SOURCES["ZL3b"]), all_weights, rows)
    train = [page for page in pages if split_name(page.page) == "train"]
    validation = [page for page in pages if split_name(page.page) == "validation"]
    model = EdgeModel(train, d_weights, c_weights)
    normalization = normalization_gate(model, validation)
    first = evaluate_pages(validation, model, with_plant=True)
    second = evaluate_pages(validation, model, with_plant=True)
    deterministic = first == second
    negative = first["negative"]
    gates = {
        "coverage_and_count": first["evaluated_pages"] >= 20 and first["coverage"] >= 0.70,
        "probability_normalization": normalization["passed"],
        "integrity": first["all_integrity"],
        "deterministic": deterministic,
        "planted_power": bool(
            first["plant"]["mean_increment_bits_per_edge"] >= 0.05
            and first["plant"]["positive_page_fraction"] >= 0.80
            and first["plant"]["sign_flip_p"] <= 0.01
        ),
        "reserved_null_negative": not bool(
            negative["mean_residual_bits_per_edge"] >= 0.02
            and negative["positive_page_fraction"] >= 0.60
            and negative["conservative_p"] <= 0.01
        ),
    }
    passed = all(gates.values())
    result = {
        "experiment": "IL006",
        "phase": "VALIDATION_FROZEN" if passed else "VALIDATION_FAILED",
        "created": "2026-08-06",
        **provenance(),
        "weight_signature": map_signature(d_weights, c_weights, form_weights),
        "model_signature": model.signature(),
        "root_partition_counts": {"D": len(d_weights), "C": len(c_weights)},
        "model": {"tau": TAU, "global_mixture": GLOBAL_MIXTURE},
        "normalization": normalization,
        "eligibility": {"minimum_edges": MIN_EDGES, "minimum_movable_each_partition": MIN_MOVABLE},
        "null_repeats": NULL_REPEATS,
        "gates": gates,
        "development_only": first,
        "elapsed_seconds": time.perf_counter() - started,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    FROZEN.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not passed:
        VALIDATION_FAILURE.write_text(validation_failure_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


def validation_failure_markdown(result: dict[str, Any]) -> str:
    return "\n".join([
        "# IL006 — validation failure",
        "",
        "IL006 stopped before bucket-0 adjacency scoring because a frozen gate failed.",
        "",
        "```json",
        json.dumps(result["gates"], indent=2, sort_keys=True),
        "```",
        "",
        "No line-assembly, language, or semantic inference is licensed.",
        "",
    ])


def final_phase() -> None:
    started = time.perf_counter()
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    if frozen.get("phase") != "VALIDATION_FROZEN":
        raise RuntimeError("IL006 validation did not pass")
    verify_provenance(frozen)
    d_weights, c_weights, form_weights = weight_maps()
    if map_signature(d_weights, c_weights, form_weights) != frozen["weight_signature"]:
        raise RuntimeError("IL006 root/form map changed")
    all_weights = {**d_weights, **c_weights}
    rows = metadata_rows()
    zl_pages = build_pages(load_lines(SOURCES["ZL3b"]), all_weights, rows)
    train = [page for page in zl_pages if split_name(page.page) == "train"]
    test = [page for page in zl_pages if split_name(page.page) == "test"]
    model = EdgeModel(train, d_weights, c_weights)
    if model.signature() != frozen["model_signature"]:
        raise RuntimeError("IL006 trained edge table changed")
    primary = evaluate_pages(test, model, with_plant=False)
    frozen_pages = {row["page"] for row in primary["page_rows"]}
    editions: dict[str, Any] = {"ZL3b": primary}
    for edition in ("IT2a", "RF1b"):
        alternate_pages = [
            page for page in build_pages(load_lines(SOURCES[edition]), all_weights, rows)
            if split_name(page.page) == "test"
        ]
        result = evaluate_pages(
            alternate_pages, model, with_plant=False, allowed_pages=frozen_pages
        )
        result["zl_page_reuse_fraction"] = (
            result["evaluated_pages"] / max(1, primary["evaluated_pages"])
        )
        editions[edition] = result
    alternate_ok = all(
        editions[edition]["mean_residual_bits_per_edge"] > 0
        and editions[edition]["zl_page_reuse_fraction"] >= 0.70
        for edition in ("IT2a", "RF1b")
    )
    passed = material(primary, 0.05) and alternate_ok
    status = "CONFIRMED_STRUCTURED_LINE_ROOT_ASSEMBLY" if passed else "FINAL_PAGE_PALETTE_NOT_REJECTED"
    interpretation = (
        "Adjacent root identities are non-exchangeable beyond page vocabulary, exact form, position, entry state, and stratum."
        if passed else
        "The frozen adjacency table did not reject page-palette exchangeability at this resolution."
    )
    result = {
        "experiment": "IL006",
        "status": status,
        "created": "2026-08-06",
        **provenance(),
        "validation_sha256": sha256_path(FROZEN),
        "weight_signature": frozen["weight_signature"],
        "model_signature": frozen["model_signature"],
        "editions": editions,
        "alternate_readings_same_positive_direction": alternate_ok,
        "material": passed,
        "interpretation": interpretation,
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(report_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def report_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# IL006 — page-conditioned cross-root adjacency",
        "",
        f"Status: **{result['status']}**",
        "",
        result["interpretation"],
        "",
        "| Reading | residual (bits/edge) | positive pages | conservative p | evaluated |",
        "|---|---:|---:|---:|---:|",
    ]
    for edition in SOURCES:
        row = result["editions"][edition]
        lines.append(
            f"| {edition} | {row['mean_residual_bits_per_edge']:+.5f} | "
            f"{100 * row['positive_page_fraction']:.1f}% | {row['conservative_p']:.6g} | "
            f"{row['evaluated_pages']}/{row['possible_pages']} |"
        )
    lines.extend([
        "",
        "ZL3b is primary; IT2a/RF1b are alternate readings, not replications.",
        "The null preserves page D/C inventories, exact root-free forms, positions, entry state, and edge locations.",
        "No natural-language identity, POS, syntax label, word meaning, cipher, pronunciation, or plaintext is inferred.",
        "No OCR, image recognition, embedding, or automated visual input was used.",
        "",
    ])
    return "\n".join(lines)


def synthetic_page(name: str, offset: int = 0) -> PageSequence:
    d_roots = [(f"d{index}",) for index in range(3)]
    c_roots = [(f"c{index}",) for index in range(3)]
    shell = ((0, "NONE", "NONE", "NONE", "NONE"),)
    positions = []
    for line in range(8):
        for token in range(6):
            pair = (token // 2 + line + offset) % 3
            root = d_roots[pair] if token % 2 == 0 else c_roots[pair]
            positions.append(Position(
                line_index=line,
                paragraph=0,
                stratum=("A", "H", "1"),
                shell=shell,
                position_bin=token % 3,
                paragraph_opening=line == 0,
                token_index=token,
                root=root,
            ))
    return PageSequence(name, tuple(positions))


def selftest() -> None:
    d_weights = {(f"d{index}",): 1.0 for index in range(3)}
    c_weights = {(f"c{index}",): 1.0 for index in range(3)}
    train = [synthetic_page(f"train{index}", index % 3) for index in range(9)]
    model = EdgeModel(train, d_weights, c_weights)
    gate = normalization_gate(model, train)
    assert gate["passed"], gate
    page = synthetic_page("held", 1)
    first = page_evaluation((page, model, 256, False))
    second = page_evaluation((page, model, 256, False))
    assert first == second
    assert first["integrity"]
    assert first["residual"] > 0.05, first
    original = [position.root for position in page.positions]
    cells = cell_indices(page, original, model.d_set)
    shuffled = random_assignment(original, cells, np.random.default_rng(123))
    planted, swaps, movable = greedy_plant(page, shuffled, cells, model)
    shuffled_score, _ = adjacency_score(page, shuffled, model)
    planted_score, _ = adjacency_score(page, planted, model)
    assert swaps > 0 and movable >= 2 * MIN_MOVABLE
    assert planted_score > shuffled_score
    assert marginal_signature(shuffled, cells) == marginal_signature(planted, cells)
    print(json.dumps({
        "status": "PASS",
        "synthetic_residual": first["residual"],
        "plant_increment": planted_score - shuffled_score,
        "normalization": gate,
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("selftest", "validate", "final"), required=True)
    args = parser.parse_args()
    if args.phase == "selftest":
        selftest()
    elif args.phase == "validate":
        validation_phase()
    else:
        final_phase()


if __name__ == "__main__":
    main()
