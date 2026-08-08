#!/usr/bin/env python3
"""IL009: transfer IL006 adjacency affinities across excluded strata."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_il001_information_location import (  # noqa: E402
    SOURCES,
    bootstrap_ci,
    load_lines,
    sha256_path,
    sign_flip_p,
    split_bucket,
    split_name,
)
from run_il003_multiscale_boundaries import METADATA, map_signature, weight_maps  # noqa: E402
from run_il005_conditional_root_recency import (  # noqa: E402
    PageSequence,
    build_pages,
    metadata_rows,
)
from run_il006_page_conditioned_root_adjacency import (  # noqa: E402
    EdgeModel,
    MIN_EDGES,
    MIN_MOVABLE,
    adjacency_score,
    cell_indices,
    mobility,
    normalization_gate,
    page_evaluation,
)


PREREG = HERE / "hypotheses" / "IL009_CROSS_STRATUM_ADJACENCY_PREREGISTRATION.md"
DEPENDENCIES = (
    HERE / "run_il001_information_location.py",
    HERE / "run_il003_multiscale_boundaries.py",
    HERE / "run_il005_conditional_root_recency.py",
    HERE / "run_il006_page_conditioned_root_adjacency.py",
)
RESULTS = HERE / "results"
FROZEN = RESULTS / "il009_cross_stratum_adjacency_validation_frozen.json"
OUTPUT_JSON = RESULTS / "il009_cross_stratum_adjacency_results.json"
OUTPUT_REPORT = RESULTS / "il009_cross_stratum_adjacency_report.md"
VALIDATION_FAILURE = RESULTS / "il009_cross_stratum_adjacency_validation_failure.md"

AXES = {"CURRIER": 0, "SECTION": 1, "HAND": 2}
NULL_REPEATS = 2_048
TRAIN_REPEATS = 256
SIGN_REPEATS = 199_999
MAX_WORKERS = 32
SEED = 6_900_009


def page_value(page: PageSequence, axis: str) -> str:
    index = AXES[axis]
    values = {position.stratum[index] for position in page.positions}
    if len(values) != 1:
        raise RuntimeError(f"IL009 page has multiple {axis} values: {page.page} {values}")
    return next(iter(values))


def target_values(pages: Sequence[PageSequence], axis: str) -> tuple[str, ...]:
    return tuple(sorted({page_value(page, axis) for page in pages}))


def build_models(
    source_pages: Sequence[PageSequence],
    all_pages: Sequence[PageSequence],
    axis: str,
    d_weights: dict,
    c_weights: dict,
) -> tuple[dict[str, EdgeModel], dict[str, Any]]:
    models: dict[str, EdgeModel] = {}
    audit: dict[str, Any] = {}
    for target in target_values(all_pages, axis):
        selected = [page for page in source_pages if page_value(page, axis) != target]
        if not selected:
            raise RuntimeError(f"IL009 no source pages for {axis} target {target}")
        if any(page_value(page, axis) == target for page in selected):
            raise RuntimeError("IL009 target value leaked into source model")
        model = EdgeModel(selected, d_weights, c_weights)
        models[target] = model
        audit[target] = {
            "source_pages": len(selected),
            "excluded_target": target,
            "source_values": sorted({page_value(page, axis) for page in selected}),
            "model_signature": model.signature(),
        }
    return models, audit


def axis_evaluation(
    pages: Sequence[PageSequence],
    models: dict[str, EdgeModel],
    axis: str,
    repeats: int,
    with_plant: bool,
    allowed_pages: set[str] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    base = []
    jobs = []
    for page in pages:
        if allowed_pages is not None and page.page not in allowed_pages:
            continue
        target = page_value(page, axis)
        model = models[target]
        labels = [position.root for position in page.positions]
        _score, edge_count = adjacency_score(page, labels, model)
        if edge_count < MIN_EDGES:
            continue
        base.append(page)
        cells = cell_indices(page, labels, model.d_set)
        d_movable, c_movable = mobility(labels, cells, model.d_set)
        if min(d_movable, c_movable) >= MIN_MOVABLE:
            jobs.append((page, model, repeats, with_plant))
    workers = min(MAX_WORKERS, max(1, len(jobs)))
    if workers == 1:
        rows = [page_evaluation(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            rows = list(executor.map(page_evaluation, jobs, chunksize=1))
    rows.sort(key=lambda row: row["page"])
    return rows, len(base)


def conditional_family_p(
    axis_rows: dict[str, list[dict[str, Any]]], field: str
) -> dict[str, float]:
    standardized: dict[str, np.ndarray] = {}
    observed_z: dict[str, float] = {}
    for axis, rows in axis_rows.items():
        matrix = np.asarray([row["null_scores"] for row in rows], dtype=np.float64)
        centered = matrix - matrix.mean(axis=1, keepdims=True)
        replicate_means = centered.mean(axis=0)
        scale = float(np.std(replicate_means, ddof=1))
        if not math.isfinite(scale) or scale <= 0:
            standardized[axis] = np.zeros(matrix.shape[1], dtype=np.float64)
            observed_z[axis] = 0.0
        else:
            standardized[axis] = replicate_means / scale
            observed_z[axis] = float(np.mean([row[field] for row in rows]) / scale)
    family_max = np.max(np.stack([standardized[axis] for axis in AXES]), axis=0)
    return {
        axis: float((np.count_nonzero(family_max >= observed_z[axis] - 1e-15) + 1) / (len(family_max) + 1))
        for axis in AXES
    }


def sign_family_p(
    axis_rows: dict[str, list[dict[str, Any]]], field: str, seed: int
) -> dict[str, float]:
    pages = sorted({row["page"] for rows in axis_rows.values() for row in rows})
    page_index = {page: index for index, page in enumerate(pages)}
    values: dict[str, np.ndarray] = {}
    indices: dict[str, np.ndarray] = {}
    denominators: dict[str, float] = {}
    observed_z: dict[str, float] = {}
    for axis, rows in axis_rows.items():
        array = np.asarray([row[field] for row in rows], dtype=np.float64)
        values[axis] = array
        indices[axis] = np.asarray([page_index[row["page"]] for row in rows], dtype=np.int64)
        denom = float(np.sqrt(np.sum(array * array)) / len(array)) if len(array) else 0.0
        denominators[axis] = denom
        observed_z[axis] = float(np.mean(array) / denom) if denom > 0 else 0.0
    exceed = {axis: 0 for axis in AXES}
    rng = np.random.default_rng(seed)
    done = 0
    batch = 10_000
    while done < SIGN_REPEATS:
        size = min(batch, SIGN_REPEATS - done)
        signs = rng.integers(0, 2, size=(size, len(pages)), dtype=np.int8) * 2 - 1
        z_columns = []
        for axis in AXES:
            denom = denominators[axis]
            if denom <= 0:
                z_columns.append(np.zeros(size, dtype=np.float64))
            else:
                means = (signs[:, indices[axis]] * values[axis]).mean(axis=1)
                z_columns.append(means / denom)
        maxima = np.max(np.stack(z_columns, axis=1), axis=1)
        for axis in AXES:
            exceed[axis] += int(np.count_nonzero(maxima >= observed_z[axis] - 1e-15))
        done += size
    return {axis: (exceed[axis] + 1) / (SIGN_REPEATS + 1) for axis in AXES}


def simple_axis_summary(
    rows: Sequence[dict[str, Any]], possible: int, seed: int, with_plant: bool
) -> dict[str, Any]:
    residuals = [row["residual"] for row in rows]
    negatives = [row["negative_residual"] for row in rows]
    low, high = bootstrap_ci(residuals, seed)
    output: dict[str, Any] = {
        "possible_pages": possible,
        "evaluated_pages": len(rows),
        "coverage": len(rows) / possible if possible else 0.0,
        "mean_observed_score": float(np.mean([row["observed_score"] for row in rows])),
        "mean_null_score": float(np.mean([row["null_mean"] for row in rows])),
        "mean_residual_bits_per_edge": float(np.mean(residuals)),
        "positive_page_fraction": sum(value > 0 for value in residuals) / len(residuals),
        "bootstrap_95_ci": [low, high],
        "all_integrity": all(row["integrity"] for row in rows),
        "negative": {
            "mean_residual_bits_per_edge": float(np.mean(negatives)),
            "positive_page_fraction": sum(value > 0 for value in negatives) / len(negatives),
        },
        "null_matrix_sha256": hashlib.sha256(
            np.asarray([row["null_scores"] for row in rows], dtype="<f8").tobytes()
        ).hexdigest(),
        "page_rows": [{key: value for key, value in row.items() if key != "null_scores"} for row in rows],
    }
    if with_plant:
        increments = [row["plant_increment"] for row in rows]
        output["plant"] = {
            "mean_increment_bits_per_edge": float(np.mean(increments)),
            "positive_page_fraction": sum(value > 0 for value in increments) / len(increments),
            "sign_flip_p": sign_flip_p(increments, seed + 1),
            "total_swaps": sum(row["plant_swaps"] for row in rows),
        }
    return output


def joint_summary(
    axis_rows: dict[str, list[dict[str, Any]]],
    possible: dict[str, int],
    with_plant: bool,
) -> dict[str, Any]:
    summaries = {
        axis: simple_axis_summary(axis_rows[axis], possible[axis], SEED + 10 + index, with_plant)
        for index, axis in enumerate(AXES)
    }
    conditional = conditional_family_p(axis_rows, "residual")
    signs = sign_family_p(axis_rows, "residual", SEED + 20)
    negative_conditional = conditional_family_p(axis_rows, "negative_residual")
    negative_signs = sign_family_p(axis_rows, "negative_residual", SEED + 21)
    for axis in AXES:
        summaries[axis]["family_conditional_p"] = conditional[axis]
        summaries[axis]["family_sign_flip_p"] = signs[axis]
        summaries[axis]["conservative_family_p"] = max(conditional[axis], signs[axis])
        summaries[axis]["negative"]["family_conditional_p"] = negative_conditional[axis]
        summaries[axis]["negative"]["family_sign_flip_p"] = negative_signs[axis]
        summaries[axis]["negative"]["conservative_family_p"] = max(
            negative_conditional[axis], negative_signs[axis]
        )
    if with_plant:
        plant_rows = {
            axis: [
                {"page": row["page"], "plant_increment": row["plant_increment"]}
                for row in rows
            ]
            for axis, rows in axis_rows.items()
        }
        plant_family = sign_family_p(plant_rows, "plant_increment", SEED + 22)
        for axis in AXES:
            summaries[axis]["plant"]["family_sign_flip_p"] = plant_family[axis]
    return summaries


def model_audit(
    models: dict[str, dict[str, EdgeModel]],
    source_audits: dict[str, dict[str, Any]],
    pages: Sequence[PageSequence],
) -> dict[str, Any]:
    normalization: dict[str, Any] = {}
    source_exclusion = True
    for axis in AXES:
        normalization[axis] = {}
        for target, model in models[axis].items():
            sample = [page for page in pages if page_value(page, axis) == target]
            normalization[axis][target] = normalization_gate(model, sample or pages)
            source_exclusion &= target not in source_audits[axis][target]["source_values"]
    return {
        "source_exclusion": source_exclusion,
        "all_normalized": all(
            row["passed"]
            for axis_rows in normalization.values()
            for row in axis_rows.values()
        ),
        "normalization": normalization,
        "sources": source_audits,
    }


def run_evaluation(
    all_pages: Sequence[PageSequence],
    source_pages: Sequence[PageSequence],
    eval_pages: Sequence[PageSequence],
    d_weights: dict,
    c_weights: dict,
    repeats: int,
    with_plant: bool,
    allowed_pages: dict[str, set[str]] | None = None,
) -> tuple[dict[str, Any], dict[str, dict[str, EdgeModel]], dict[str, Any]]:
    models: dict[str, dict[str, EdgeModel]] = {}
    sources: dict[str, dict[str, Any]] = {}
    axis_rows: dict[str, list[dict[str, Any]]] = {}
    possible: dict[str, int] = {}
    for axis in AXES:
        models[axis], sources[axis] = build_models(source_pages, all_pages, axis, d_weights, c_weights)
        allowed = allowed_pages[axis] if allowed_pages is not None else None
        axis_rows[axis], possible[axis] = axis_evaluation(
            eval_pages, models[axis], axis, repeats, with_plant, allowed
        )
    summaries = joint_summary(axis_rows, possible, with_plant)
    audit = model_audit(models, sources, all_pages)
    return summaries, models, audit


def model_signatures(models: dict[str, dict[str, EdgeModel]]) -> dict[str, dict[str, str]]:
    return {
        axis: {target: model.signature() for target, model in sorted(axis_models.items())}
        for axis, axis_models in models.items()
    }


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
            raise RuntimeError(f"IL009 provenance changed after validation: {key}")


def power_pass(row: dict[str, Any]) -> bool:
    return bool(
        row["plant"]["mean_increment_bits_per_edge"] >= 0.05
        and row["plant"]["positive_page_fraction"] >= 0.80
        and row["plant"]["family_sign_flip_p"] <= 0.01
    )


def negative_clean(row: dict[str, Any]) -> bool:
    negative = row["negative"]
    return not bool(
        negative["mean_residual_bits_per_edge"] >= 0.02
        and negative["positive_page_fraction"] >= 0.60
        and negative["conservative_family_p"] <= 0.01
    )


def material(row: dict[str, Any]) -> bool:
    return bool(
        row["mean_residual_bits_per_edge"] >= 0.02
        and row["positive_page_fraction"] >= 0.60
        and row["conservative_family_p"] <= 0.05
        and row["coverage"] >= 0.70
    )


def training_phase() -> None:
    started = time.perf_counter()
    d_weights, c_weights, form_weights = weight_maps()
    weights = {**d_weights, **c_weights}
    pages = build_pages(load_lines(SOURCES["ZL3b"]), weights, metadata_rows())
    source = [page for page in pages if split_bucket(page.page) in (3, 4)]
    evaluate = [page for page in pages if split_bucket(page.page) == 2]
    axes, models, audit = run_evaluation(
        pages, source, evaluate, d_weights, c_weights, TRAIN_REPEATS, True
    )
    print(json.dumps({
        "experiment": "IL009",
        "phase": "TRAINING_ONLY",
        "axes": axes,
        "model_audit": audit,
        "model_signatures": model_signatures(models),
        "weight_signature": map_signature(d_weights, c_weights, form_weights),
        "elapsed_seconds": time.perf_counter() - started,
    }, indent=2, sort_keys=True))


def validation_phase() -> None:
    started = time.perf_counter()
    d_weights, c_weights, form_weights = weight_maps()
    weights = {**d_weights, **c_weights}
    pages = build_pages(load_lines(SOURCES["ZL3b"]), weights, metadata_rows())
    source = [page for page in pages if split_name(page.page) == "train"]
    evaluate = [page for page in pages if split_name(page.page) == "validation"]
    first, models, audit = run_evaluation(
        pages, source, evaluate, d_weights, c_weights, NULL_REPEATS, True
    )
    second, second_models, second_audit = run_evaluation(
        pages, source, evaluate, d_weights, c_weights, NULL_REPEATS, True
    )
    deterministic = (
        first == second
        and model_signatures(models) == model_signatures(second_models)
        and audit == second_audit
    )
    gates = {
        "coverage_and_count": all(
            first[axis]["evaluated_pages"] >= 20 and first[axis]["coverage"] >= 0.70
            for axis in AXES
        ),
        "probability_normalization": audit["all_normalized"],
        "source_exclusion": audit["source_exclusion"],
        "integrity": all(first[axis]["all_integrity"] for axis in AXES),
        "deterministic": deterministic,
        "planted_power": all(power_pass(first[axis]) for axis in AXES),
        "reserved_null_negative": all(negative_clean(first[axis]) for axis in AXES),
    }
    passed = all(gates.values())
    result = {
        "experiment": "IL009",
        "phase": "VALIDATION_FROZEN" if passed else "VALIDATION_FAILED",
        "created": "2026-08-06",
        **provenance(),
        "weight_signature": map_signature(d_weights, c_weights, form_weights),
        "model_signatures": model_signatures(models),
        "axes": first,
        "model_audit": audit,
        "null_repeats": NULL_REPEATS,
        "gates": gates,
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
        "# IL009 — validation failure",
        "",
        "IL009 stopped before bucket-0 scoring because a frozen gate failed.",
        "",
        "```json",
        json.dumps(result["gates"], indent=2, sort_keys=True),
        "```",
        "",
        "No cross-stratum, system-class, language, or semantic inference is licensed.",
        "",
    ])


def final_phase() -> None:
    started = time.perf_counter()
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    if frozen.get("phase") != "VALIDATION_FROZEN":
        raise RuntimeError("IL009 validation did not pass")
    verify_provenance(frozen)
    d_weights, c_weights, form_weights = weight_maps()
    if map_signature(d_weights, c_weights, form_weights) != frozen["weight_signature"]:
        raise RuntimeError("IL009 root/form map changed")
    weights = {**d_weights, **c_weights}
    rows = metadata_rows()
    zl_pages = build_pages(load_lines(SOURCES["ZL3b"]), weights, rows)
    source = [page for page in zl_pages if split_name(page.page) == "train"]
    test = [page for page in zl_pages if split_name(page.page) == "test"]
    primary, models, audit = run_evaluation(
        zl_pages, source, test, d_weights, c_weights, NULL_REPEATS, False
    )
    if model_signatures(models) != frozen["model_signatures"]:
        raise RuntimeError("IL009 trained models changed")
    frozen_pages = {
        axis: {row["page"] for row in primary[axis]["page_rows"]}
        for axis in AXES
    }
    editions: dict[str, Any] = {"ZL3b": primary}
    for edition in ("IT2a", "RF1b"):
        alternate_all = build_pages(load_lines(SOURCES[edition]), weights, rows)
        alternate_test = [page for page in alternate_all if split_name(page.page) == "test"]
        axis_rows: dict[str, list[dict[str, Any]]] = {}
        possible: dict[str, int] = {}
        for axis in AXES:
            axis_rows[axis], possible[axis] = axis_evaluation(
                alternate_test,
                models[axis],
                axis,
                NULL_REPEATS,
                False,
                frozen_pages[axis],
            )
        alternate = joint_summary(axis_rows, possible, False)
        for axis in AXES:
            alternate[axis]["zl_page_reuse_fraction"] = (
                alternate[axis]["evaluated_pages"]
                / max(1, primary[axis]["evaluated_pages"])
            )
        editions[edition] = alternate
    confirmed = []
    for axis in AXES:
        alternate_ok = all(
            editions[edition][axis]["mean_residual_bits_per_edge"] > 0
            and editions[edition][axis]["zl_page_reuse_fraction"] >= 0.70
            for edition in ("IT2a", "RF1b")
        )
        if material(primary[axis]) and alternate_ok:
            confirmed.append(axis)
    status = (
        "CONFIRMED_CROSS_STRATUM_ADJACENCY_" + "_".join(confirmed)
        if confirmed else
        "NO_CROSS_STRATUM_ADJACENCY_TRANSFER_CONFIRMED"
    )
    result = {
        "experiment": "IL009",
        "status": status,
        "confirmed_axes": confirmed,
        "created": "2026-08-06",
        **provenance(),
        "validation_sha256": sha256_path(FROZEN),
        "weight_signature": frozen["weight_signature"],
        "model_signatures": frozen["model_signatures"],
        "model_audit": audit,
        "editions": editions,
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(report_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def report_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# IL009 — cross-stratum root-adjacency transfer",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Confirmed axes: {', '.join(result['confirmed_axes']) if result['confirmed_axes'] else 'none'}.",
        "",
        "| reading | excluded target axis | residual bits/edge | +pages | family p | evaluated |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for edition in SOURCES:
        for axis in AXES:
            row = result["editions"][edition][axis]
            lines.append(
                f"| {edition} | {axis} | {row['mean_residual_bits_per_edge']:+.5f} | "
                f"{100 * row['positive_page_fraction']:.1f}% | {row['conservative_family_p']:.6g} | "
                f"{row['evaluated_pages']}/{row['possible_pages']} |"
            )
    lines.extend([
        "",
        "Each scoring table excludes all source pages sharing the target page's value on the named axis.",
        "The within-page null still preserves page vocabulary, exact root-free forms, position, entry state, and edge locations.",
        "ZL3b is primary; IT2a/RF1b are alternate readings, not replications.",
        "Cross-stratum transfer is structural and does not establish language, POS, authorship, sound, meaning, or plaintext.",
        "No OCR, image recognition, embedding, or automated visual input was used.",
        "",
    ])
    return "\n".join(lines)


def selftest() -> None:
    from dataclasses import replace
    from run_il006_page_conditioned_root_adjacency import synthetic_page

    d_weights = {(f"d{index}",): 1.0 for index in range(3)}
    c_weights = {(f"c{index}",): 1.0 for index in range(3)}
    pages = []
    values = (("A", "H", "1"), ("B", "S", "2"), ("A", "P", "3"))
    for index in range(18):
        base = synthetic_page(f"p{index}", index % 3)
        stratum = values[index % len(values)]
        pages.append(PageSequence(base.page, tuple(replace(position, stratum=stratum) for position in base.positions)))
    source = pages[:12]
    evaluate = pages[12:]
    axes, _models, audit = run_evaluation(
        pages, source, evaluate, d_weights, c_weights, 256, False
    )
    assert audit["source_exclusion"] and audit["all_normalized"]
    assert all(axes[axis]["mean_residual_bits_per_edge"] > 0.05 for axis in AXES), axes
    assert all(axes[axis]["all_integrity"] for axis in AXES)
    print(json.dumps({
        "status": "PASS",
        "residuals": {axis: axes[axis]["mean_residual_bits_per_edge"] for axis in AXES},
        "source_exclusion": audit["source_exclusion"],
    }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("selftest", "train", "validate", "final"), required=True)
    args = parser.parse_args()
    if args.phase == "selftest":
        selftest()
    elif args.phase == "train":
        training_phase()
    elif args.phase == "validate":
        validation_phase()
    else:
        final_phase()


if __name__ == "__main__":
    main()
