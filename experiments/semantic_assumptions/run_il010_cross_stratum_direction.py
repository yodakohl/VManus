#!/usr/bin/env python3
"""IL010: direction-specific increment in cross-stratum root adjacency."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_il001_information_location import (  # noqa: E402
    Root,
    SOURCES,
    load_lines,
    sha256_path,
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
    Edge,
    EdgeModel,
    GLOBAL_MIXTURE,
    ORIENTATIONS,
    TAU,
    extract_edges,
    normalization_gate,
)
from run_il009_cross_stratum_adjacency import (  # noqa: E402
    AXES,
    NULL_REPEATS,
    TRAIN_REPEATS,
    axis_evaluation,
    joint_summary,
    page_value,
    target_values,
)


PREREG = HERE / "hypotheses" / "IL010_CROSS_STRATUM_DIRECTION_PREREGISTRATION.md"
DEPENDENCIES = (
    HERE / "run_il001_information_location.py",
    HERE / "run_il003_multiscale_boundaries.py",
    HERE / "run_il005_conditional_root_recency.py",
    HERE / "run_il006_page_conditioned_root_adjacency.py",
    HERE / "run_il009_cross_stratum_adjacency.py",
)
RESULTS = HERE / "results"
FROZEN = RESULTS / "il010_cross_stratum_direction_validation_frozen.json"
OUTPUT_JSON = RESULTS / "il010_cross_stratum_direction_results.json"
OUTPUT_REPORT = RESULTS / "il010_cross_stratum_direction_report.md"
VALIDATION_FAILURE = RESULTS / "il010_cross_stratum_direction_validation_failure.md"

PLANT_THRESHOLD = 0.02
MATERIAL_THRESHOLD = 0.005
MIN_POSITIVE_PAGES = 0.55


class CollapsedPairModel:
    """Pool D-C pair affinities across orientation but retain orientation marginals."""

    def __init__(
        self,
        train_pages: Sequence[PageSequence],
        d_weights: dict[Root, float],
        c_weights: dict[Root, float],
        oriented: EdgeModel,
    ):
        self.d_roots = tuple(sorted(d_weights))
        self.c_roots = tuple(sorted(c_weights))
        self.d_set = frozenset(self.d_roots)
        self.c_set = frozenset(self.c_roots)
        self.d_index = {root: index for index, root in enumerate(self.d_roots)}
        self.c_index = {root: index for index, root in enumerate(self.c_roots)}
        self.orientation_index = {value: index for index, value in enumerate(ORIENTATIONS)}
        pair_counts = np.zeros((len(self.d_roots), len(self.c_roots)), dtype=np.float64)
        global_counts = np.zeros(len(self.c_roots), dtype=np.float64)
        for page in train_pages:
            labels = [position.root for position in page.positions]
            for edge in extract_edges(page, labels, self.d_set):
                di = self.d_index[edge.d_root]
                ci = self.c_index[edge.c_root]
                pair_counts[di, ci] += 1.0
                global_counts[ci] += 1.0
        self.pooled_global = (global_counts + 0.5) / (
            global_counts.sum() + 0.5 * len(self.c_roots)
        )
        totals = pair_counts.sum(axis=1, keepdims=True)
        self.pooled_conditional = (
            pair_counts + TAU * self.pooled_global[None, :]
        ) / (totals + TAU)
        self.orientation_global = np.asarray(oriented.global_distribution, dtype=np.float64)

    def edge_score(self, edge: Edge) -> float:
        oi = self.orientation_index[edge.orientation]
        di = self.d_index[edge.d_root]
        ci = self.c_index[edge.c_root]
        global_value = self.orientation_global[oi, ci]
        pooled = self.pooled_conditional[di, ci]
        query = GLOBAL_MIXTURE * global_value + (1.0 - GLOBAL_MIXTURE) * pooled
        return float(math.log2(query / global_value))

    def signature(self) -> str:
        payload = b"".join((
            np.asarray(self.pooled_global, dtype="<f8").tobytes(),
            np.asarray(self.pooled_conditional, dtype="<f8").tobytes(),
            np.asarray(self.orientation_global, dtype="<f8").tobytes(),
        ))
        return hashlib.sha256(payload).hexdigest()

    def normalization(self) -> dict[str, Any]:
        errors = [
            float(abs(self.pooled_global.sum() - 1.0)),
            float(np.max(np.abs(self.pooled_conditional.sum(axis=1) - 1.0))),
            float(np.max(np.abs(self.orientation_global.sum(axis=1) - 1.0))),
        ]
        finite = bool(
            np.all(np.isfinite(self.pooled_global))
            and np.all(np.isfinite(self.pooled_conditional))
            and np.all(np.isfinite(self.orientation_global))
        )
        return {
            "passed": finite and max(errors) < 1e-10,
            "all_finite": finite,
            "maximum_probability_error": max(errors),
        }


class DirectionIncrementModel:
    def __init__(self, oriented: EdgeModel, collapsed: CollapsedPairModel):
        self.oriented = oriented
        self.collapsed = collapsed
        self.d_set = oriented.d_set

    def edge_score(self, edge: Edge) -> float:
        return self.oriented.edge_score(edge) - self.collapsed.edge_score(edge)

    def signature(self) -> str:
        return hashlib.sha256(
            (self.oriented.signature() + "|" + self.collapsed.signature()).encode("ascii")
        ).hexdigest()


def build_models(
    source_pages: Sequence[PageSequence],
    all_pages: Sequence[PageSequence],
    axis: str,
    d_weights: dict[Root, float],
    c_weights: dict[Root, float],
) -> tuple[dict[str, DirectionIncrementModel], dict[str, Any]]:
    models = {}
    audit = {}
    for target in target_values(all_pages, axis):
        selected = [page for page in source_pages if page_value(page, axis) != target]
        if not selected or any(page_value(page, axis) == target for page in selected):
            raise RuntimeError("IL010 source exclusion failure")
        oriented = EdgeModel(selected, d_weights, c_weights)
        collapsed = CollapsedPairModel(selected, d_weights, c_weights, oriented)
        model = DirectionIncrementModel(oriented, collapsed)
        models[target] = model
        audit[target] = {
            "excluded_target": target,
            "source_pages": len(selected),
            "source_values": sorted({page_value(page, axis) for page in selected}),
            "oriented_signature": oriented.signature(),
            "collapsed_signature": collapsed.signature(),
            "increment_signature": model.signature(),
            "oriented_normalization": normalization_gate(oriented, all_pages),
            "collapsed_normalization": collapsed.normalization(),
        }
    return models, audit


def model_signatures(models: dict[str, dict[str, DirectionIncrementModel]]) -> dict[str, dict[str, str]]:
    return {
        axis: {target: model.signature() for target, model in sorted(axis_models.items())}
        for axis, axis_models in models.items()
    }


def run_evaluation(
    all_pages: Sequence[PageSequence],
    source_pages: Sequence[PageSequence],
    eval_pages: Sequence[PageSequence],
    d_weights: dict[Root, float],
    c_weights: dict[Root, float],
    repeats: int,
    with_plant: bool,
    allowed_pages: dict[str, set[str]] | None = None,
) -> tuple[dict[str, Any], dict[str, dict[str, DirectionIncrementModel]], dict[str, Any]]:
    models = {}
    source_audit = {}
    rows = {}
    possible = {}
    for axis in AXES:
        models[axis], source_audit[axis] = build_models(
            source_pages, all_pages, axis, d_weights, c_weights
        )
        allowed = allowed_pages[axis] if allowed_pages is not None else None
        rows[axis], possible[axis] = axis_evaluation(
            eval_pages, models[axis], axis, repeats, with_plant, allowed
        )
    summaries = joint_summary(rows, possible, with_plant)
    source_exclusion = all(
        target not in values["source_values"]
        for axis_rows in source_audit.values()
        for target, values in axis_rows.items()
    )
    normalized = all(
        values["oriented_normalization"]["passed"]
        and values["collapsed_normalization"]["passed"]
        for axis_rows in source_audit.values()
        for values in axis_rows.values()
    )
    return summaries, models, {
        "source_exclusion": source_exclusion,
        "all_normalized": normalized,
        "sources": source_audit,
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
            raise RuntimeError(f"IL010 provenance changed after validation: {key}")


def power_pass(row: dict[str, Any]) -> bool:
    return bool(
        row["plant"]["mean_increment_bits_per_edge"] >= PLANT_THRESHOLD
        and row["plant"]["positive_page_fraction"] >= 0.80
        and row["plant"]["family_sign_flip_p"] <= 0.01
    )


def negative_clean(row: dict[str, Any]) -> bool:
    negative = row["negative"]
    return not bool(
        negative["mean_residual_bits_per_edge"] >= MATERIAL_THRESHOLD
        and negative["positive_page_fraction"] >= MIN_POSITIVE_PAGES
        and negative["conservative_family_p"] <= 0.01
    )


def material(row: dict[str, Any]) -> bool:
    return bool(
        row["mean_residual_bits_per_edge"] >= MATERIAL_THRESHOLD
        and row["positive_page_fraction"] >= MIN_POSITIVE_PAGES
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
        "experiment": "IL010",
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
        "experiment": "IL010",
        "phase": "VALIDATION_FROZEN" if passed else "VALIDATION_FAILED",
        "created": "2026-08-06",
        **provenance(),
        "weight_signature": map_signature(d_weights, c_weights, form_weights),
        "model_signatures": model_signatures(models),
        "thresholds": {
            "plant": PLANT_THRESHOLD,
            "material": MATERIAL_THRESHOLD,
            "positive_pages": MIN_POSITIVE_PAGES,
        },
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
        "# IL010 — validation failure",
        "",
        "IL010 stopped before bucket-0 scoring because a frozen gate failed.",
        "",
        "```json",
        json.dumps(result["gates"], indent=2, sort_keys=True),
        "```",
        "",
        "No cross-stratum direction, language, syntax-label, or semantic inference is licensed.",
        "",
    ])


def final_phase() -> None:
    started = time.perf_counter()
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    if frozen.get("phase") != "VALIDATION_FROZEN":
        raise RuntimeError("IL010 validation did not pass")
    verify_provenance(frozen)
    d_weights, c_weights, form_weights = weight_maps()
    if map_signature(d_weights, c_weights, form_weights) != frozen["weight_signature"]:
        raise RuntimeError("IL010 root/form map changed")
    weights = {**d_weights, **c_weights}
    rows = metadata_rows()
    zl_pages = build_pages(load_lines(SOURCES["ZL3b"]), weights, rows)
    source = [page for page in zl_pages if split_name(page.page) == "train"]
    test = [page for page in zl_pages if split_name(page.page) == "test"]
    primary, models, audit = run_evaluation(
        zl_pages, source, test, d_weights, c_weights, NULL_REPEATS, False
    )
    if model_signatures(models) != frozen["model_signatures"]:
        raise RuntimeError("IL010 trained models changed")
    frozen_pages = {
        axis: {row["page"] for row in primary[axis]["page_rows"]}
        for axis in AXES
    }
    editions: dict[str, Any] = {"ZL3b": primary}
    for edition in ("IT2a", "RF1b"):
        alternate_all = build_pages(load_lines(SOURCES[edition]), weights, rows)
        alternate_test = [page for page in alternate_all if split_name(page.page) == "test"]
        axis_rows = {}
        possible = {}
        for axis in AXES:
            axis_rows[axis], possible[axis] = axis_evaluation(
                alternate_test, models[axis], axis, NULL_REPEATS, False, frozen_pages[axis]
            )
        alternate = joint_summary(axis_rows, possible, False)
        for axis in AXES:
            alternate[axis]["zl_page_reuse_fraction"] = (
                alternate[axis]["evaluated_pages"] / max(1, primary[axis]["evaluated_pages"])
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
        "CONFIRMED_CROSS_STRATUM_DIRECTION_" + "_".join(confirmed)
        if confirmed else
        "NO_CROSS_STRATUM_DIRECTION_INCREMENT_CONFIRMED"
    )
    result = {
        "experiment": "IL010",
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
        "# IL010 — cross-stratum directional adjacency increment",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Confirmed axes: {', '.join(result['confirmed_axes']) if result['confirmed_axes'] else 'none'}.",
        "",
        "| reading | excluded target axis | directional increment | +pages | family p | evaluated |",
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
        "The score is orientation-aware affinity minus the same pair table pooled across DC/CD orientation.",
        "Each model excludes source pages sharing the target value; the exact IL006 within-page null is retained.",
        "ZL3b is primary; IT2a/RF1b are alternate readings, not replications.",
        "Direction-specific transfer does not identify reading direction, POS, syntax labels, language, sound, meaning, or plaintext.",
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
    strata = (("A", "H", "1"), ("B", "S", "2"), ("A", "P", "3"))
    for index in range(24):
        base = synthetic_page(f"p{index}", index % 3)
        # Reverse every CD edge's C label to make physical orientation informative.
        positions = list(base.positions)
        for pos_index, position in enumerate(positions):
            if position.token_index % 2 == 0 and (position.token_index // 2) % 2 == 1:
                root_index = (int(position.root[0][-1]) + 1) % 3
                positions[pos_index] = replace(position, root=(f"d{root_index}",))
        stratum = strata[index % len(strata)]
        pages.append(PageSequence(
            base.page,
            tuple(replace(position, stratum=stratum) for position in positions),
        ))
    axes, _models, audit = run_evaluation(
        pages, pages[:18], pages[18:], d_weights, c_weights, 256, False
    )
    assert audit["source_exclusion"] and audit["all_normalized"]
    assert all(axes[axis]["mean_residual_bits_per_edge"] > 0.01 for axis in AXES), axes
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
