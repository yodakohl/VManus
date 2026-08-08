#!/usr/bin/env python3
"""IL011: test IL010's Currier direction against relaid Timm manuscripts.

This is a text-only mechanism control.  Each generated manuscript is poured
into the exact ZL prose geometry, parsed by the frozen structural parser, and
given the same Currier-excluded oriented-minus-unordered test as IL010.  The
conditional-null expectation is evaluated exactly rather than by Monte Carlo.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
sys.path.insert(0, str(HERE))

from run_il001_information_location import (  # noqa: E402
    Line,
    SOURCES,
    core,
    deep_canonical,
    load_lines,
    parse_rows,
    parse_token,
    sha256_path,
    split_name,
)
from run_il003_multiscale_boundaries import METADATA, map_signature, weight_maps  # noqa: E402
from run_il005_conditional_root_recency import (  # noqa: E402
    PageSequence,
    Position,
    build_pages,
    metadata_rows,
)
from run_il006_page_conditioned_root_adjacency import (  # noqa: E402
    Edge,
    MIN_EDGES,
    MIN_MOVABLE,
    adjacency_score,
    cell_indices,
    mobility,
)
from run_il010_cross_stratum_direction import (  # noqa: E402
    build_models,
    model_signatures,
)


PREREG = HERE / "hypotheses" / "IL011_TIMM_DIRECTION_CONTROL_PREREGISTRATION.md"
DEPENDENCIES = (
    HERE / "run_il001_information_location.py",
    HERE / "run_il003_multiscale_boundaries.py",
    HERE / "run_il005_conditional_root_recency.py",
    HERE / "run_il006_page_conditioned_root_adjacency.py",
    HERE / "run_il009_cross_stratum_adjacency.py",
    HERE / "run_il010_cross_stratum_direction.py",
)
IL010_RESULTS = HERE / "results" / "il010_cross_stratum_direction_results.json"
RESULTS = HERE / "results"
FROZEN = RESULTS / "il011_timm_direction_control_validation_frozen.json"
OUTPUT_JSON = RESULTS / "il011_timm_direction_control_results.json"
OUTPUT_REPORT = RESULTS / "il011_timm_direction_control_report.md"
VALIDATION_FAILURE = RESULTS / "il011_timm_direction_control_validation_failure.md"
TIMM_DIR = (
    BASE / "archive_pre_reset_2026-08-06" / "semantic_assumptions" /
    "cache" / "timm_generated_controls"
)
DEV_SEEDS = (19, 23, 41, 73, 97)
FINAL_SEEDS = tuple(range(101, 165))
MAX_WORKERS = 32
AXIS = "CURRIER"
EXACT_PARITY_TOLERANCE = 0.001
MIN_CONTROL_COVERAGE = 0.50
MIN_CONTROL_PAGES = 20
MIN_FINAL_CONTROLS = 60
EMPIRICAL_ALPHA = 0.05


def timm_path(seed: int) -> Path:
    return TIMM_DIR / f"generated_text_seed{seed}.txt"


def timm_tokens(path: Path) -> list[str]:
    output: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="strict").splitlines():
        stripped = raw.strip()
        if stripped and not stripped.startswith("#"):
            output.extend(stripped.split())
    return output


@lru_cache(maxsize=1)
def prose_template() -> tuple[Any, ...]:
    return tuple(
        row for row in parse_rows(SOURCES["ZL3b"])
        if row.kind == "P" and row.language in {"A", "B"} and row.words
    )


def relayout_lines(tokens: Sequence[str]) -> list[Line]:
    """Pour generated words into the raw ZL prose slots before parsing."""
    rows = prose_template()
    needed = sum(len(row.words) for row in rows)
    if len(tokens) < needed:
        raise ValueError(f"Timm text has {len(tokens)} words; need {needed}")
    output: list[Line] = []
    cursor = 0
    for row in rows:
        words = list(tokens[cursor:cursor + len(row.words)])
        cursor += len(row.words)
        preliminary = [
            word for word in words
            if (value := deep_canonical(word)) and core.segment(value)
        ]
        if len(preliminary) < 2:
            continue
        parsed = tuple(
            token for index, word in enumerate(preliminary)
            if (token := parse_token(word, index, len(preliminary))) is not None
        )
        if len(parsed) < 2:
            continue
        output.append(Line(
            page=row.page,
            locus=row.locus,
            language=row.language,
            section=row.section,
            hand=row.hand,
            paragraph_start=row.paragraph_start,
            tokens=parsed,
        ))
    return output


def edge_position_indices(
    page: PageSequence, labels: Sequence[tuple[str, ...]], d_set: frozenset,
) -> list[tuple[str, int, int]]:
    by_line: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for position_index, position in enumerate(page.positions):
        by_line[position.line_index].append((position.token_index, position_index))
    output: list[tuple[str, int, int]] = []
    for selected in by_line.values():
        selected.sort()
        for (left_token, left), (right_token, right) in zip(selected, selected[1:]):
            if right_token != left_token + 1:
                continue
            left_d = labels[left] in d_set
            right_d = labels[right] in d_set
            if left_d == right_d:
                continue
            if left_d:
                output.append(("DC", left, right))
            else:
                output.append(("CD", right, left))
    return output


def exact_null_score(page: PageSequence, model: Any) -> tuple[float, int, bool]:
    """Expected adjacency score under IL006's independent within-cell shuffles."""
    labels = [position.root for position in page.positions]
    cells = cell_indices(page, labels, model.d_set)
    distributions: dict[int, tuple[tuple[tuple[str, ...], float], ...]] = {}
    homogeneous = True
    for indices in cells:
        counts = Counter(labels[index] for index in indices)
        total = sum(counts.values())
        is_d = {root in model.d_set for root in counts}
        homogeneous &= len(is_d) == 1
        values = tuple((root, count / total) for root, count in sorted(counts.items()))
        for index in indices:
            distributions[index] = values
    edges = edge_position_indices(page, labels, model.d_set)
    expected_total = 0.0
    for orientation, d_index, c_index in edges:
        expected = 0.0
        for d_root, d_probability in distributions[d_index]:
            for c_root, c_probability in distributions[c_index]:
                expected += (
                    d_probability * c_probability *
                    model.edge_score(Edge(orientation, d_root, c_root))
                )
        expected_total += expected
    score = expected_total / len(edges) if edges else float("nan")
    return score, len(edges), bool(homogeneous and len(distributions) == len(labels))


def corpus_score(lines: Sequence[Line]) -> dict[str, Any]:
    d_weights, c_weights, form_weights = weight_maps()
    weights = {**d_weights, **c_weights}
    pages = build_pages(lines, weights, metadata_rows())
    source = [page for page in pages if split_name(page.page) == "train"]
    evaluate = [page for page in pages if split_name(page.page) == "test"]
    models, audit = build_models(source, pages, AXIS, d_weights, c_weights)
    rows: list[dict[str, Any]] = []
    possible = 0
    for page in evaluate:
        target_values = {position.stratum[0] for position in page.positions}
        if len(target_values) != 1:
            raise RuntimeError(f"multiple Currier values on {page.page}")
        target = next(iter(target_values))
        model = models[target]
        labels = [position.root for position in page.positions]
        observed, observed_edges = adjacency_score(page, labels, model)
        if observed_edges < MIN_EDGES:
            continue
        possible += 1
        cells = cell_indices(page, labels, model.d_set)
        movable_d, movable_c = mobility(labels, cells, model.d_set)
        if min(movable_d, movable_c) < MIN_MOVABLE:
            continue
        expected, expected_edges, integrity = exact_null_score(page, model)
        integrity &= observed_edges == expected_edges
        rows.append({
            "page": page.page,
            "edges": observed_edges,
            "movable_D": movable_d,
            "movable_C": movable_c,
            "observed": observed,
            "exact_null": expected,
            "residual": observed - expected,
            "integrity": integrity and math.isfinite(observed) and math.isfinite(expected),
        })
    if not rows:
        raise RuntimeError("no eligible IL011 pages")
    source_exclusion = all(
        target not in values["source_values"]
        for target, values in audit.items()
    )
    return {
        "possible_pages": possible,
        "evaluated_pages": len(rows),
        "coverage": len(rows) / possible if possible else 0.0,
        "mean_observed_score": float(np.mean([row["observed"] for row in rows])),
        "mean_exact_null_score": float(np.mean([row["exact_null"] for row in rows])),
        "mean_residual_bits_per_edge": float(np.mean([row["residual"] for row in rows])),
        "positive_page_fraction": sum(row["residual"] > 0 for row in rows) / len(rows),
        "all_integrity": all(row["integrity"] for row in rows),
        "source_exclusion": source_exclusion,
        "model_signatures": model_signatures({AXIS: models})[AXIS],
        "weight_signature": map_signature(d_weights, c_weights, form_weights),
        "page_rows": rows,
    }


def control_worker(seed: int) -> dict[str, Any]:
    path = timm_path(seed)
    score = corpus_score(relayout_lines(timm_tokens(path)))
    return {
        "seed": seed,
        "path": str(path.relative_to(BASE)),
        "sha256": sha256_path(path),
        **score,
    }


def evaluate_controls(seeds: Sequence[int]) -> list[dict[str, Any]]:
    workers = min(MAX_WORKERS, max(1, len(seeds)))
    if workers == 1:
        rows = [control_worker(seed) for seed in seeds]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            rows = list(executor.map(control_worker, seeds, chunksize=1))
    return sorted(rows, key=lambda row: row["seed"])


def control_manifest() -> dict[str, Any]:
    rows = []
    for seed in DEV_SEEDS + FINAL_SEEDS:
        path = timm_path(seed)
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append((seed, path.stat().st_size, sha256_path(path)))
    payload = "\n".join(f"{seed}\t{size}\t{digest}" for seed, size, digest in rows)
    return {
        "count": len(rows),
        "development_seeds": list(DEV_SEEDS),
        "final_seeds": list(FINAL_SEEDS),
        "sha256": hashlib.sha256(payload.encode("ascii")).hexdigest(),
    }


def provenance() -> dict[str, Any]:
    return {
        "runner_sha256": sha256_path(Path(__file__)),
        "preregistration_sha256": sha256_path(PREREG),
        "dependency_sha256": {path.name: sha256_path(path) for path in DEPENDENCIES},
        "zl_source_sha256": sha256_path(SOURCES["ZL3b"]),
        "metadata_sha256": sha256_path(METADATA),
        "il010_results_sha256": sha256_path(IL010_RESULTS),
        "control_manifest": control_manifest(),
    }


def exact_null_selftest() -> dict[str, Any]:
    class DummyModel:
        d_set = frozenset({("d0",), ("d1",)})

        @staticmethod
        def edge_score(edge: Edge) -> float:
            d_value = 0.0 if edge.d_root == ("d0",) else 2.0
            c_value = 0.0 if edge.c_root == ("c0",) else 1.0
            return d_value + c_value + (0.5 if edge.orientation == "CD" else 0.0)

    positions = (
        Position(0, 0, ("A", "H", "1"), ((0, "", "", "", ""),), 0, True, 0, ("d0",)),
        Position(0, 0, ("A", "H", "1"), ((0, "", "", "", ""),), 0, True, 1, ("c0",)),
        Position(1, 0, ("A", "H", "1"), ((0, "", "", "", ""),), 0, True, 0, ("d1",)),
        Position(1, 0, ("A", "H", "1"), ((0, "", "", "", ""),), 0, True, 1, ("c1",)),
    )
    page = PageSequence("synthetic", positions)
    model = DummyModel()
    exact, edges, integrity = exact_null_score(page, model)
    labels = [position.root for position in page.positions]
    enumerated = []
    for d_order in itertools.permutations((labels[0], labels[2])):
        for c_order in itertools.permutations((labels[1], labels[3])):
            assignment = [d_order[0], c_order[0], d_order[1], c_order[1]]
            score, count = adjacency_score(page, assignment, model)
            if count != edges:
                raise RuntimeError("IL011 selftest edge count changed")
            enumerated.append(score)
    brute = float(np.mean(enumerated))
    return {
        "passed": integrity and abs(exact - brute) < 1e-12,
        "exact": exact,
        "enumerated": brute,
        "edges": edges,
    }


def real_reference() -> tuple[dict[str, Any], dict[str, Any]]:
    score = corpus_score(load_lines(SOURCES["ZL3b"]))
    il010 = json.loads(IL010_RESULTS.read_text(encoding="utf-8"))
    published = il010["editions"]["ZL3b"][AXIS]
    comparison = {
        "published_random_null_residual": published["mean_residual_bits_per_edge"],
        "published_positive_page_fraction": published["positive_page_fraction"],
        "published_evaluated_pages": published["evaluated_pages"],
        "exact_minus_published_residual": (
            score["mean_residual_bits_per_edge"] - published["mean_residual_bits_per_edge"]
        ),
        "same_evaluated_pages": score["evaluated_pages"] == published["evaluated_pages"],
    }
    return score, comparison


def training_phase() -> None:
    started = time.perf_counter()
    real, comparison = real_reference()
    controls = evaluate_controls(DEV_SEEDS)
    print(json.dumps({
        "experiment": "IL011",
        "phase": "TRAINING_ONLY",
        "selftest": exact_null_selftest(),
        "real_exact": real,
        "il010_parity": comparison,
        "development_controls": controls,
        "elapsed_seconds": time.perf_counter() - started,
    }, indent=2, sort_keys=True))


def validation_phase() -> None:
    started = time.perf_counter()
    if OUTPUT_JSON.exists():
        raise RuntimeError("IL011 final result already exists")
    real_first, comparison_first = real_reference()
    dev_first = evaluate_controls(DEV_SEEDS)
    real_second, comparison_second = real_reference()
    dev_second = evaluate_controls(DEV_SEEDS)
    selftest = exact_null_selftest()
    deterministic = (
        real_first == real_second and comparison_first == comparison_second
        and dev_first == dev_second
    )
    gates = {
        "exact_null_selftest": selftest["passed"],
        "deterministic": deterministic,
        "real_integrity_and_source_exclusion": (
            real_first["all_integrity"] and real_first["source_exclusion"]
        ),
        "published_il010_parity": (
            comparison_first["same_evaluated_pages"]
            and abs(comparison_first["exact_minus_published_residual"]) <= EXACT_PARITY_TOLERANCE
        ),
        "development_control_count": len(dev_first) == len(DEV_SEEDS),
        "development_coverage": all(
            row["coverage"] >= MIN_CONTROL_COVERAGE
            and row["evaluated_pages"] >= MIN_CONTROL_PAGES
            for row in dev_first
        ),
        "development_integrity": all(
            row["all_integrity"] and row["source_exclusion"] for row in dev_first
        ),
        "held_control_inventory": control_manifest()["final_seeds"] == list(FINAL_SEEDS),
    }
    passed = all(gates.values())
    result = {
        "experiment": "IL011",
        "phase": "VALIDATION_FROZEN" if passed else "VALIDATION_FAILED",
        "created": "2026-08-06",
        **provenance(),
        "selftest": selftest,
        "real_exact": real_first,
        "il010_parity": comparison_first,
        "development_controls": dev_first,
        "thresholds": {
            "exact_parity_tolerance": EXACT_PARITY_TOLERANCE,
            "minimum_control_coverage": MIN_CONTROL_COVERAGE,
            "minimum_control_pages": MIN_CONTROL_PAGES,
            "minimum_final_controls": MIN_FINAL_CONTROLS,
            "empirical_alpha": EMPIRICAL_ALPHA,
        },
        "gates": gates,
        "elapsed_seconds": time.perf_counter() - started,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    FROZEN.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not passed:
        VALIDATION_FAILURE.write_text(
            "# IL011 — validation failure\n\n"
            "IL011 stopped before the 64 held Timm controls were scored.\n\n"
            f"```json\n{json.dumps(gates, indent=2, sort_keys=True)}\n```\n\n"
            "No system-class, language, or semantic inference is licensed.\n",
            encoding="utf-8",
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


def verify_frozen(frozen: dict[str, Any]) -> None:
    if frozen.get("phase") != "VALIDATION_FROZEN":
        raise RuntimeError("IL011 validation did not pass")
    current = provenance()
    for key, value in current.items():
        if frozen.get(key) != value:
            raise RuntimeError(f"IL011 frozen provenance changed: {key}")


def quantiles(values: Sequence[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "minimum": float(np.min(array)),
        "q025": float(np.quantile(array, 0.025)),
        "median": float(np.median(array)),
        "q975": float(np.quantile(array, 0.975)),
        "maximum": float(np.max(array)),
    }


def final_phase() -> None:
    started = time.perf_counter()
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    verify_frozen(frozen)
    controls = evaluate_controls(FINAL_SEEDS)
    if len(controls) != len(FINAL_SEEDS):
        raise RuntimeError("IL011 held control count changed")
    eligible = [row for row in controls if (
        row["coverage"] >= MIN_CONTROL_COVERAGE
        and row["evaluated_pages"] >= MIN_CONTROL_PAGES
        and row["all_integrity"] and row["source_exclusion"]
    )]
    if len(eligible) < MIN_FINAL_CONTROLS:
        raise RuntimeError(
            f"IL011 only {len(eligible)}/{len(controls)} held controls passed frozen eligibility"
        )
    real = frozen["real_exact"]
    real_residual = real["mean_residual_bits_per_edge"]
    real_positive = real["positive_page_fraction"]
    residual_exceed = sum(
        row["mean_residual_bits_per_edge"] >= real_residual - 1e-15
        for row in eligible
    )
    positive_exceed = sum(
        row["positive_page_fraction"] >= real_positive - 1e-15
        for row in eligible
    )
    union_exceed = sum(
        row["mean_residual_bits_per_edge"] >= real_residual - 1e-15
        or row["positive_page_fraction"] >= real_positive - 1e-15
        for row in eligible
    )
    denominator = len(eligible) + 1
    p_residual = (residual_exceed + 1) / denominator
    p_positive = (positive_exceed + 1) / denominator
    p_union = (union_exceed + 1) / denominator
    robust_excess = p_union <= EMPIRICAL_ALPHA
    status = (
        "IL010_EXCEEDS_TIMM_DIRECTION_CONTROL"
        if robust_excess else
        "IL010_COMPATIBLE_WITH_TIMM_DIRECTION_CONTROL"
    )
    result = {
        "experiment": "IL011",
        "status": status,
        "created": "2026-08-06",
        **provenance(),
        "validation_sha256": sha256_path(FROZEN),
        "decision_rule": (
            "plus-one empirical tail for any held control matching/exceeding "
            "the real residual OR positive-page fraction; alpha 0.05"
        ),
        "real_exact": real,
        "held_controls": controls,
        "control_distribution": {
            "submitted_controls": len(controls),
            "eligible_controls": len(eligible),
            "residual": quantiles([
                row["mean_residual_bits_per_edge"] for row in eligible
            ]),
            "positive_page_fraction": quantiles([
                row["positive_page_fraction"] for row in eligible
            ]),
            "residual_exceedances": residual_exceed,
            "positive_fraction_exceedances": positive_exceed,
            "union_exceedances": union_exceed,
            "residual_empirical_p": p_residual,
            "positive_fraction_empirical_p": p_positive,
            "conservative_union_empirical_p": p_union,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(report_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def report_markdown(result: dict[str, Any]) -> str:
    real = result["real_exact"]
    controls = result["control_distribution"]
    residual = controls["residual"]
    positive = controls["positive_page_fraction"]
    return "\n".join([
        "# IL011 — Timm control for cross-Currier direction",
        "",
        f"Status: **{result['status']}**",
        "",
        "| corpus | directional residual | positive pages | evaluated |",
        "|---|---:|---:|---:|",
        f"| ZL3b exact-null | {real['mean_residual_bits_per_edge']:+.5f} | "
        f"{100 * real['positive_page_fraction']:.1f}% | "
        f"{real['evaluated_pages']}/{real['possible_pages']} |",
        f"| {controls['eligible_controls']} eligible Timm controls median | {residual['median']:+.5f} | "
        f"{100 * positive['median']:.1f}% | — |",
        f"| Timm controls central 95% | {residual['q025']:+.5f}…{residual['q975']:+.5f} | "
        f"{100 * positive['q025']:.1f}%…{100 * positive['q975']:.1f}% | — |",
        "",
        f"Held controls matching/exceeding the real residual: "
        f"{controls['residual_exceedances']}/{controls['eligible_controls']} "
        f"(plus-one p={controls['residual_empirical_p']:.6g}).",
        f"Held controls matching/exceeding either the residual or positive-page fraction: "
        f"{controls['union_exceedances']}/{controls['eligible_controls']} "
        f"(conservative p={controls['conservative_union_empirical_p']:.6g}).",
        "",
        "Each generated text selected its own source-excluded Currier tables after being relaid into the exact ZL prose geometry. The IL006 conditional-null expectation was evaluated exactly.",
        "A real excess rejects this fixed local self-citation process as sufficient for IL010; compatibility would show that IL010 alone does not distinguish it.",
        "Neither outcome identifies ordinary language, notation, authorship, POS, sound, meaning, or plaintext.",
        "No OCR, image recognition, embedding, or automated visual input was used.",
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase", choices=("selftest", "train", "validate", "final"), required=True
    )
    args = parser.parse_args()
    if args.phase == "selftest":
        print(json.dumps(exact_null_selftest(), indent=2, sort_keys=True))
    elif args.phase == "train":
        training_phase()
    elif args.phase == "validate":
        validation_phase()
    else:
        final_phase()


if __name__ == "__main__":
    main()
