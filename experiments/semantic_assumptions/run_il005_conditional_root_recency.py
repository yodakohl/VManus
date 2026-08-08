#!/usr/bin/env python3
"""IL005: form-conditioned exact-root recency inside pages and paragraphs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
sys.path.insert(0, str(HERE))

from run_il001_information_location import (  # noqa: E402
    Line,
    Root,
    SOURCES,
    bootstrap_ci,
    load_lines,
    page_groups,
    sha256_path,
    sign_flip_p,
    split_name,
    stable_int,
)
from run_il002_matched_line_pairs import holm_adjust  # noqa: E402
from run_il003_multiscale_boundaries import (  # noqa: E402
    METADATA,
    map_signature,
    weight_maps,
)


PREREG = HERE / "hypotheses" / "IL005_CONDITIONAL_ROOT_RECENCY_PREREGISTRATION.md"
DEPENDENCIES = (
    HERE / "run_il001_information_location.py",
    HERE / "run_il002_matched_line_pairs.py",
    HERE / "run_il003_multiscale_boundaries.py",
)
RESULTS = HERE / "results"
FROZEN = RESULTS / "il005_conditional_root_recency_validation_frozen.json"
OUTPUT_JSON = RESULTS / "il005_conditional_root_recency_results.json"
OUTPUT_REPORT = RESULTS / "il005_conditional_root_recency_report.md"
VALIDATION_FAILURE = RESULTS / "il005_conditional_root_recency_validation_failure.md"
SCOPES = ("PAGE", "PARAGRAPH")
NULL_REPEATS = 2_048
MIN_TOKENS = 20
MIN_MOVABLE = 6
MAX_WORKERS = 32
SEED = 5_500_005


@dataclass(frozen=True)
class Position:
    line_index: int
    paragraph: int
    stratum: tuple[str, str, str]
    shell: tuple[Any, ...]
    position_bin: int
    paragraph_opening: bool
    token_index: int
    root: Root

    @property
    def order_key(self) -> tuple[int, int, int]:
        return self.paragraph, self.line_index, self.token_index


@dataclass(frozen=True)
class PageSequence:
    page: str
    positions: tuple[Position, ...]


def metadata_rows() -> dict[str, dict[str, str]]:
    with METADATA.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        locus = row["locus"]
        if locus in output:
            raise RuntimeError(f"duplicate manual metadata locus: {locus}")
        output[locus] = row
    return output


def verify_manual_metadata(lines: Sequence[Line], rows: dict[str, dict[str, str]]) -> None:
    for line in lines:
        row = rows.get(line.locus)
        if row is None:
            raise RuntimeError(f"manual metadata missing locus: {line.locus}")
        expected = (row["language"], row["section"], row["hand"])
        if line.stratum != expected:
            raise RuntimeError(f"manual stratum mismatch at {line.locus}")


def build_pages(
    lines: Sequence[Line], weights: dict[Root, float], rows: dict[str, dict[str, str]]
) -> list[PageSequence]:
    verify_manual_metadata(lines, rows)
    output: list[PageSequence] = []
    for page, selected in page_groups(lines):
        selected = sorted(
            selected,
            key=lambda line: (int(rows[line.locus]["line_number"]), line.locus),
        )
        paragraph = -1
        positions: list[Position] = []
        for line_index, line in enumerate(selected):
            manual_opening = bool(int(rows[line.locus]["paragraph_start"]))
            if line_index == 0 or manual_opening:
                paragraph += 1
            for token_index, token in enumerate(line.tokens):
                if token.root not in weights:
                    continue
                positions.append(Position(
                    line_index=line_index,
                    paragraph=paragraph,
                    stratum=line.stratum,
                    shell=token.shell,
                    position_bin=token.position_bin,
                    paragraph_opening=(line_index == 0 or manual_opening),
                    token_index=token_index,
                    root=token.root,
                ))
        output.append(PageSequence(page, tuple(positions)))
    output.sort(key=lambda page: page.page)
    return output


def cell_indices(page: PageSequence, scope: str) -> tuple[tuple[int, ...], ...]:
    cells: dict[tuple[Any, ...], list[int]] = defaultdict(list)
    for index, position in enumerate(page.positions):
        key: tuple[Any, ...] = (
            position.stratum,
            position.shell,
            position.position_bin,
            position.paragraph_opening,
        )
        if scope == "PARAGRAPH":
            key += (position.paragraph,)
        cells[key].append(index)
    return tuple(tuple(indices) for _key, indices in sorted(cells.items(), key=lambda row: repr(row[0])))


def variable_cells(
    labels: Sequence[Root], cells: Sequence[Sequence[int]]
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(indices) for indices in cells
        if len(indices) >= 2 and len({labels[index] for index in indices}) >= 2
    )


def recency_score(
    page: PageSequence, labels: Sequence[Root], weights: dict[Root, float]
) -> float:
    previous: dict[Root, int] = {}
    pending: set[Root] = set()
    current: tuple[int, int] | None = None
    numerator = 0.0
    denominator = 0.0
    for position, root in zip(page.positions, labels):
        key = (position.paragraph, position.line_index)
        if key != current:
            if current is not None:
                for prior_root in pending:
                    previous[prior_root] = current[1]
                if key[0] != current[0]:
                    previous.clear()
            pending = set()
            current = key
        weight = weights[root]
        denominator += weight
        if root in previous:
            gap = position.line_index - previous[root]
            if gap <= 0:
                raise RuntimeError("nonpositive physical-line recurrence gap")
            numerator += weight / gap
        pending.add(root)
    return numerator / denominator if denominator > 0 else float("nan")


def marginal_signature(
    labels: Sequence[Root], cells: Sequence[Sequence[int]]
) -> str:
    rows = []
    for ordinal, indices in enumerate(cells):
        counter = Counter(labels[index] for index in indices)
        rows.append(f"{ordinal}\t{sorted(counter.items())!r}")
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def root_free_signature(page: PageSequence) -> str:
    rows = [
        repr((
            position.line_index,
            position.paragraph,
            position.stratum,
            position.shell,
            position.position_bin,
            position.paragraph_opening,
            position.token_index,
        ))
        for position in page.positions
    ]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def random_assignment(
    original: Sequence[Root], cells: Sequence[Sequence[int]], rng: np.random.Generator
) -> list[Root]:
    labels = list(original)
    for indices in cells:
        if len(indices) < 2:
            continue
        values = [original[index] for index in indices]
        order = rng.permutation(len(values))
        for target, source in zip(indices, order):
            labels[target] = values[int(source)]
    return labels


def greedy_plant(
    page: PageSequence,
    original: Sequence[Root],
    cells: Sequence[Sequence[int]],
    weights: dict[Root, float],
) -> tuple[list[Root], int, int]:
    labels = list(original)
    selected = variable_cells(labels, cells)
    movable = sum(len(indices) for indices in selected)
    budget = math.ceil(0.10 * movable / 2)
    used = 0
    for _step in range(budget):
        baseline = recency_score(page, labels, weights)
        best_gain = 0.0
        best_pair: tuple[int, int] | None = None
        best_order: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None
        for indices in selected:
            for offset, left in enumerate(indices):
                for right in indices[offset + 1:]:
                    if labels[left] == labels[right]:
                        continue
                    labels[left], labels[right] = labels[right], labels[left]
                    gain = recency_score(page, labels, weights) - baseline
                    labels[left], labels[right] = labels[right], labels[left]
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


def page_scope_evaluation(
    job: tuple[PageSequence, str, dict[Root, float], int, bool]
) -> dict[str, Any]:
    page, scope, weights, repeats, with_plant = job
    original = [position.root for position in page.positions]
    cells = cell_indices(page, scope)
    selected = variable_cells(original, cells)
    movable = sum(len(indices) for indices in selected)
    if len(original) < MIN_TOKENS or movable < MIN_MOVABLE:
        raise RuntimeError("ineligible page passed to recurrence worker")
    seed = stable_int(f"IL005|{page.page}|{scope}|NULL")
    rng = np.random.default_rng(seed)
    observed = recency_score(page, original, weights)
    original_marginal = marginal_signature(original, cells)
    negative_labels = random_assignment(original, cells, rng)
    negative = recency_score(page, negative_labels, weights)
    original_root_free = root_free_signature(page)
    integrity = marginal_signature(negative_labels, cells) == original_marginal
    null_scores = []
    last_labels = negative_labels
    for _repeat in range(repeats):
        labels = random_assignment(original, cells, rng)
        null_scores.append(recency_score(page, labels, weights))
        last_labels = labels
    integrity &= marginal_signature(last_labels, cells) == original_marginal
    integrity &= root_free_signature(page) == original_root_free
    null_mean = float(np.mean(null_scores))
    planted: float | None = None
    plant_swaps = 0
    if with_plant:
        planted_labels, plant_swaps, plant_movable = greedy_plant(
            page, original, cells, weights
        )
        if plant_movable != movable:
            raise RuntimeError("plant mobility changed")
        integrity &= marginal_signature(planted_labels, cells) == original_marginal
        planted = recency_score(page, planted_labels, weights)
    return {
        "page": page.page,
        "scope": scope,
        "tokens": len(original),
        "movable_positions": movable,
        "variable_cells": len(selected),
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
        "root_free_sha256": root_free_signature(page),
        "null_scores": null_scores,
    }


def conditional_p(rows: Sequence[dict[str, Any]], field: str) -> float:
    observed = float(np.mean([row[field] for row in rows]))
    null = np.asarray([row["null_scores"] for row in rows], dtype=np.float64)
    centered = null - null.mean(axis=1, keepdims=True)
    replicate_means = centered.mean(axis=0)
    return float((np.count_nonzero(replicate_means >= observed - 1e-15) + 1) / (len(replicate_means) + 1))


def aggregate_scope(
    rows: Sequence[dict[str, Any]], possible: int, with_plant: bool
) -> dict[str, Any]:
    residuals = [row["residual"] for row in rows]
    negatives = [row["negative_residual"] for row in rows]
    mean_residual = float(np.mean(residuals)) if residuals else float("nan")
    mean_null = float(np.mean([row["null_mean"] for row in rows])) if rows else float("nan")
    sign_p = sign_flip_p(residuals, SEED + 10)
    randomization_p = conditional_p(rows, "residual") if rows else 1.0
    negative_sign_p = sign_flip_p(negatives, SEED + 11)
    negative_randomization_p = conditional_p(rows, "negative_residual") if rows else 1.0
    low, high = bootstrap_ci(residuals, SEED + 12)
    clean_rows = []
    for row in rows:
        clean_rows.append({key: value for key, value in row.items() if key != "null_scores"})
    result = {
        "possible_pages": possible,
        "evaluated_pages": len(rows),
        "coverage": len(rows) / possible if possible else 0.0,
        "mean_observed_score": (
            float(np.mean([row["observed_score"] for row in rows])) if rows else float("nan")
        ),
        "mean_null_score": mean_null,
        "mean_residual": mean_residual,
        "relative_residual": mean_residual / mean_null if mean_null > 0 else float("nan"),
        "positive_page_fraction": (
            sum(value > 0 for value in residuals) / len(residuals) if residuals else 0.0
        ),
        "sign_flip_p": sign_p,
        "conditional_randomization_p": randomization_p,
        "conservative_p": max(sign_p, randomization_p),
        "bootstrap_95_ci": [low, high],
        "negative": {
            "mean_residual": float(np.mean(negatives)) if negatives else float("nan"),
            "relative_residual": (
                float(np.mean(negatives)) / mean_null if rows and mean_null > 0 else float("nan")
            ),
            "positive_page_fraction": (
                sum(value > 0 for value in negatives) / len(negatives) if negatives else 0.0
            ),
            "sign_flip_p": negative_sign_p,
            "conditional_randomization_p": negative_randomization_p,
            "conservative_p": max(negative_sign_p, negative_randomization_p),
        },
        "all_integrity": all(row["integrity"] for row in rows),
        "page_rows": clean_rows,
        "null_matrix_sha256": hashlib.sha256(
            np.asarray([row["null_scores"] for row in rows], dtype="<f8").tobytes()
        ).hexdigest(),
    }
    if with_plant:
        increments = [row["plant_increment"] for row in rows]
        result["plant"] = {
            "mean_increment": float(np.mean(increments)) if increments else float("nan"),
            "positive_page_fraction": (
                sum(value > 0 for value in increments) / len(increments) if increments else 0.0
            ),
            "sign_flip_p": sign_flip_p(increments, SEED + 13),
            "total_swaps": sum(row["plant_swaps"] for row in rows),
        }
    return result


def evaluate_partition(
    pages: Sequence[PageSequence],
    weights: dict[Root, float],
    with_plant: bool,
    allowed_pages: dict[str, set[str]] | None = None,
) -> dict[str, Any]:
    jobs = []
    possible: dict[str, int] = {}
    for scope in SCOPES:
        base = [page for page in pages if len(page.positions) >= MIN_TOKENS]
        if allowed_pages is not None:
            base = [page for page in base if page.page in allowed_pages[scope]]
        possible[scope] = len(base)
        for page in base:
            original = [position.root for position in page.positions]
            cells = cell_indices(page, scope)
            movable = sum(len(indices) for indices in variable_cells(original, cells))
            if movable >= MIN_MOVABLE:
                jobs.append((page, scope, weights, NULL_REPEATS, with_plant))
    workers = min(MAX_WORKERS, max(1, len(jobs)))
    if workers == 1:
        rows = [page_scope_evaluation(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            rows = list(executor.map(page_scope_evaluation, jobs, chunksize=1))
    rows.sort(key=lambda row: (row["scope"], row["page"]))
    return {
        scope: aggregate_scope(
            [row for row in rows if row["scope"] == scope],
            possible[scope],
            with_plant,
        )
        for scope in SCOPES
    }


def add_adjustment(scopes: dict[str, Any], negative: bool = False) -> None:
    raw = {
        scope: (
            scopes[scope]["negative"]["conservative_p"]
            if negative else scopes[scope]["conservative_p"]
        )
        for scope in SCOPES
    }
    adjusted = holm_adjust(raw)
    for scope in SCOPES:
        target = scopes[scope]["negative"] if negative else scopes[scope]
        target["holm_p"] = adjusted[scope]


def material(result: dict[str, Any], p_threshold: float) -> bool:
    return bool(
        result["mean_residual"] >= 0.005
        and result["relative_residual"] >= 0.02
        and result["positive_page_fraction"] >= 0.60
        and result["holm_p"] <= p_threshold
        and result.get("coverage", 1.0) >= 0.70
    )


def validation_gates(scopes: dict[str, Any], deterministic: bool) -> dict[str, Any]:
    gates: dict[str, Any] = {"deterministic": deterministic}
    for scope in SCOPES:
        result = scopes[scope]
        gates[f"{scope.lower()}_coverage_count"] = bool(
            result["evaluated_pages"] >= 20 and result["coverage"] >= 0.70
        )
        gates[f"{scope.lower()}_integrity"] = result["all_integrity"]
        gates[f"{scope.lower()}_plant"] = bool(
            result["plant"]["mean_increment"] >= 0.01
            and result["plant"]["positive_page_fraction"] >= 0.80
            and result["plant"]["sign_flip_p"] <= 0.01
        )
        negative = result["negative"]
        gates[f"{scope.lower()}_negative"] = not bool(
            negative["mean_residual"] >= 0.005
            and negative["relative_residual"] >= 0.02
            and negative["positive_page_fraction"] >= 0.60
            and negative["holm_p"] <= 0.01
        )
    return gates


def provenance() -> dict[str, Any]:
    return {
        "runner_sha256": sha256_path(Path(__file__)),
        "dependency_sha256": {path.name: sha256_path(path) for path in DEPENDENCIES},
        "preregistration_sha256": sha256_path(PREREG),
        "metadata_sha256": sha256_path(METADATA),
        "source_sha256": {name: sha256_path(path) for name, path in SOURCES.items()},
    }


def verify_provenance(frozen: dict[str, Any]) -> None:
    current = provenance()
    for key, value in current.items():
        if frozen.get(key) != value:
            raise RuntimeError(f"IL005 provenance changed after validation: {key}")


def validation_phase() -> None:
    started = time.perf_counter()
    d_weights, c_weights, form_weights = weight_maps()
    rows = metadata_rows()
    lines = load_lines(SOURCES["ZL3b"])
    pages = [
        page for page in build_pages(lines, d_weights, rows)
        if split_name(page.page) == "validation"
    ]
    first = evaluate_partition(pages, d_weights, with_plant=True)
    add_adjustment(first)
    add_adjustment(first, negative=True)
    second = evaluate_partition(pages, d_weights, with_plant=True)
    add_adjustment(second)
    add_adjustment(second, negative=True)
    deterministic = first == second
    gates = validation_gates(first, deterministic)
    passed = all(gates.values())
    result = {
        "experiment": "IL005",
        "phase": "VALIDATION_FROZEN" if passed else "VALIDATION_FAILED",
        "created": "2026-08-06",
        **provenance(),
        "weight_signature": map_signature(d_weights, c_weights, form_weights),
        "root_partition_counts": {"D": len(d_weights), "C": len(c_weights)},
        "null_repeats": NULL_REPEATS,
        "eligibility": {"minimum_tokens": MIN_TOKENS, "minimum_movable": MIN_MOVABLE},
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
        "# IL005 — validation failure",
        "",
        "IL005 stopped before bucket-0 or C-root scoring because at least one frozen gate failed.",
        "",
        "```json",
        json.dumps(result["gates"], indent=2, sort_keys=True),
        "```",
        "",
        "No manuscript-class or semantic inference is licensed.",
        "",
    ])


def final_phase() -> None:
    started = time.perf_counter()
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    if frozen.get("phase") != "VALIDATION_FROZEN":
        raise RuntimeError("IL005 validation did not pass")
    verify_provenance(frozen)
    d_weights, c_weights, form_weights = weight_maps()
    if map_signature(d_weights, c_weights, form_weights) != frozen["weight_signature"]:
        raise RuntimeError("IL005 root/form map changed")
    rows = metadata_rows()
    zl_pages = [
        page for page in build_pages(load_lines(SOURCES["ZL3b"]), c_weights, rows)
        if split_name(page.page) == "test"
    ]
    primary = evaluate_partition(zl_pages, c_weights, with_plant=False)
    add_adjustment(primary)
    frozen_pages = {
        scope: {row["page"] for row in primary[scope]["page_rows"]}
        for scope in SCOPES
    }
    editions: dict[str, Any] = {"ZL3b": primary}
    for edition in ("IT2a", "RF1b"):
        alternate_pages = [
            page for page in build_pages(load_lines(SOURCES[edition]), c_weights, rows)
            if split_name(page.page) == "test"
        ]
        result = evaluate_partition(
            alternate_pages, c_weights, with_plant=False, allowed_pages=frozen_pages
        )
        add_adjustment(result)
        for scope in SCOPES:
            denominator = max(1, primary[scope]["evaluated_pages"])
            result[scope]["zl_page_reuse_fraction"] = (
                result[scope]["evaluated_pages"] / denominator
            )
        editions[edition] = result
    decisions: dict[str, bool] = {}
    for scope in SCOPES:
        alternate_ok = all(
            editions[edition][scope]["mean_residual"] > 0
            and editions[edition][scope]["zl_page_reuse_fraction"] >= 0.70
            for edition in ("IT2a", "RF1b")
        )
        decisions[scope] = material(primary[scope], 0.05) and alternate_ok
    if decisions == {"PAGE": True, "PARAGRAPH": True}:
        status = "CONFIRMED_WITHIN_PARAGRAPH_ROOT_RECENCY"
        interpretation = (
            "Exact roots recur with physical-line recency even after paragraph inventory, "
            "exact form, position, entry state, and stratum are fixed."
        )
    elif decisions == {"PAGE": True, "PARAGRAPH": False}:
        status = "CONFIRMED_PARAGRAPH_ROOT_COMPARTMENTALIZATION"
        interpretation = (
            "Exact roots cluster by paragraph, but ordered recency within paragraphs is not established."
        )
    elif decisions == {"PAGE": False, "PARAGRAPH": False}:
        status = "FINAL_ORDER_FREE_PAGE_INVENTORY"
        interpretation = (
            "IL002's exact-root page coherence behaves as an order-free page inventory at this resolution."
        )
    else:
        status = "FINAL_INCONSISTENT_NESTED_OUTCOME"
        interpretation = (
            "The stricter paragraph result lacks its page-wide prerequisite; no physical scale is claimed."
        )
    result = {
        "experiment": "IL005",
        "status": status,
        "created": "2026-08-06",
        **provenance(),
        "validation_sha256": sha256_path(FROZEN),
        "weight_signature": frozen["weight_signature"],
        "editions": editions,
        "scope_material": decisions,
        "interpretation": interpretation,
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(report_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def report_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# IL005 — form-conditioned exact-root recency",
        "",
        f"Status: **{result['status']}**",
        "",
        result["interpretation"],
        "",
        "| Reading | scope | residual | relative | positive pages | Holm p | evaluated |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for edition in SOURCES:
        for scope in SCOPES:
            row = result["editions"][edition][scope]
            lines.append(
                f"| {edition} | {scope} | {row['mean_residual']:+.5f} | "
                f"{100 * row['relative_residual']:+.2f}% | "
                f"{100 * row['positive_page_fraction']:.1f}% | {row['holm_p']:.6g} | "
                f"{row['evaluated_pages']}/{row['possible_pages']} |"
            )
    lines.extend([
        "",
        "ZL3b is primary. IT2a/RF1b are alternate readings of the same manuscript, not replications.",
        "The conditional null preserves exact form shells, position bins, entry state, strata, and page inventory.",
        "No topic, language, generation mechanism, POS, word meaning, cipher, or plaintext is inferred.",
        "No OCR, image recognition, embedding, or automated visual input was used.",
        "",
    ])
    return "\n".join(lines)


def selftest() -> None:
    roots = [(f"r{index}",) for index in range(6)]
    weights = {root: 1.0 for root in roots}
    shell = ((0, "NONE", "NONE", "NONE", "NONE"),)
    positions = []
    for line in range(8):
        group = 0 if line < 4 else 3
        for token in range(6):
            positions.append(Position(
                line_index=line,
                paragraph=0,
                stratum=("A", "H", "1"),
                shell=shell,
                position_bin=token % 3,
                paragraph_opening=line == 0,
                token_index=token,
                root=roots[group + token % 3],
            ))
    page = PageSequence("synthetic", tuple(positions))
    first = page_scope_evaluation((page, "PAGE", weights, 256, False))
    second = page_scope_evaluation((page, "PAGE", weights, 256, False))
    assert first == second
    assert first["integrity"]
    assert first["residual"] > 0.05, first
    labels = random_assignment(
        [position.root for position in page.positions],
        cell_indices(page, "PAGE"),
        np.random.default_rng(123),
    )
    planted, swaps, movable = greedy_plant(
        page, labels, cell_indices(page, "PAGE"), weights
    )
    assert marginal_signature(labels, cell_indices(page, "PAGE")) == marginal_signature(
        planted, cell_indices(page, "PAGE")
    )
    assert swaps > 0 and movable >= MIN_MOVABLE
    assert recency_score(page, planted, weights) > recency_score(page, labels, weights)
    print(json.dumps({
        "status": "PASS",
        "synthetic_residual": first["residual"],
        "plant_increment": recency_score(page, planted, weights) - recency_score(page, labels, weights),
        "movable_positions": movable,
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
