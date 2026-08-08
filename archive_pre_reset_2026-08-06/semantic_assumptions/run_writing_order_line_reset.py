#!/usr/bin/env python3
"""Determine whether the writing-order gradient resets at physical lines.

The frozen biological-label coordinate score already transfers to interior
prose order.  Here its cross-fitted length+root-free-form residual is measured
at the left and right interior of each line.  A line-local channel predicts a
positive within-line rise and a negative transition from the right interior of
one line to the left interior of the next.

Three fixed edge widths are corrected together by a shared whole-page max-t
sign-flip.  All biological source pages and literal line-edge words are
excluded. Five relaid Timm pseudo-texts are descriptive controls. No image is
opened.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import cupy as cp
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = {
    "ZL3b": ROOT / "transcription/sources/ZL3b-n.txt",
    "IT2a": ROOT / "transcription/sources/IT2a-n.txt",
    "RF1b": ROOT / "transcription/sources/RF1b-e.txt",
}
RESULTS = HERE / "results"
VIEWS = ("EDGE1", "EDGE2", "INTERIOR_THIRD")
PRIMARY = "EDGE1"
SEED = 19_750_423
TIMM_SEEDS = (19, 23, 41, 73, 97)

sys.path.insert(0, str(HERE))
from common import Row, parse_rows  # noqa: E402
from run_bidirectional_context_controls import (  # noqa: E402
    TIMM_DIR, relayout_rows, timm_tokens,
)
from run_label_prose_position_transfer import (  # noqa: E402
    make_events, nuisance_residual, page_parity, train_label_score,
)


def line_sides(length: int, view: str) -> tuple[list[int], list[int]]:
    interior = list(range(1, length - 1))
    if view == "EDGE1":
        return interior[:1], interior[-1:]
    if view == "EDGE2":
        width = min(2, max(1, len(interior) // 2))
        return interior[:width], interior[-width:]
    if view == "INTERIOR_THIRD":
        width = max(1, len(interior) // 3)
        return interior[:width], interior[-width:]
    raise ValueError(view)


def evaluate_rows(
    rows: list[Row], score: dict[str, float], excluded_pages: set[str],
) -> dict[str, dict[str, Any]]:
    events = make_events(rows, score, excluded_pages)
    residual = nuisance_residual(events, "LENGTH_FORM")
    residual_by_key = {
        (event["locus"], event["index"]): float(residual[index])
        for index, event in enumerate(events)
    }
    eligible = [
        row for row in rows
        if row.kind == "P" and row.page not in excluded_pages
        and len(row.words) >= 6
    ]
    output = {}
    for view in VIEWS:
        page_rises: defaultdict[str, list[float]] = defaultdict(list)
        page_resets: defaultdict[str, list[float]] = defaultdict(list)
        previous: Row | None = None
        side_cache: dict[str, tuple[float, float]] = {}
        for row in eligible:
            left_indices, right_indices = line_sides(len(row.words), view)
            left = float(np.mean([
                residual_by_key[row.locus, index] for index in left_indices
            ]))
            right = float(np.mean([
                residual_by_key[row.locus, index] for index in right_indices
            ]))
            side_cache[row.locus] = (left, right)
            page_rises[row.page].append(right - left)
            if previous is not None and previous.page == row.page:
                previous_right = side_cache[previous.locus][1]
                page_resets[row.page].append(left - previous_right)
            previous = row
        common_pages = sorted(set(page_rises) & set(page_resets))
        page_rows = {}
        for page in common_pages:
            rise = float(np.mean(page_rises[page]))
            reset = float(np.mean(page_resets[page]))
            page_rows[page] = {
                "within_line_rise": rise,
                "cross_line_reset": reset,
                "rise_minus_reset": rise - reset,
            }
        contrast = np.asarray([
            row["rise_minus_reset"] for row in page_rows.values()
        ])
        rises = np.asarray([
            row["within_line_rise"] for row in page_rows.values()
        ])
        resets = np.asarray([
            row["cross_line_reset"] for row in page_rows.values()
        ])
        output[view] = {
            "eligible_lines": len(eligible),
            "pages": len(page_rows),
            "mean_within_line_rise": float(rises.mean()),
            "positive_rise_pages": int(np.sum(rises > 0)),
            "mean_cross_line_reset": float(resets.mean()),
            "negative_reset_pages": int(np.sum(resets < 0)),
            "mean_rise_minus_reset": float(contrast.mean()),
            "positive_contrast_pages": int(np.sum(contrast > 0)),
            "parity_contrast_means": {
                str(parity): float(np.mean([
                    row["rise_minus_reset"]
                    for page, row in page_rows.items()
                    if page_parity(page) == parity
                ]))
                for parity in (0, 1)
            },
            "page_values": {
                page: row["rise_minus_reset"]
                for page, row in page_rows.items()
            },
        }
    return output


def family_sign_flip(
    results: dict[str, dict[str, Any]], permutations: int, seed: int,
) -> dict[str, Any]:
    pages = sorted(set().union(*(
        set(results[view]["page_values"]) for view in VIEWS
    )))
    matrix = np.full((len(VIEWS), len(pages)), np.nan, dtype=np.float64)
    for view_index, view in enumerate(VIEWS):
        by_page = results[view]["page_values"]
        for page_index, page in enumerate(pages):
            if page in by_page:
                matrix[view_index, page_index] = by_page[page]
    masks = [np.isfinite(row) for row in matrix]
    vectors = [matrix[index, mask] for index, mask in enumerate(masks)]
    observed_t = np.asarray([
        vector.mean() / (vector.std(ddof=1) / np.sqrt(len(vector)))
        for vector in vectors
    ])
    square_sums = [float(np.sum(vector * vector)) for vector in vectors]
    gpu_vectors = [cp.asarray(vector, dtype=cp.float64) for vector in vectors]
    gpu_observed = cp.asarray(observed_t, dtype=cp.float64)
    raw_exceed = np.zeros(len(VIEWS), dtype=np.int64)
    family_exceed = np.zeros(len(VIEWS), dtype=np.int64)
    rng = cp.random.RandomState(seed)
    batch = 20_000
    for start in range(0, permutations, batch):
        count = min(batch, permutations - start)
        signs = rng.randint(
            0, 2, size=(count, len(pages)), dtype=cp.int8,
        ) * 2 - 1
        null_columns = []
        for index, vector in enumerate(gpu_vectors):
            n = len(vector)
            means = signs[:, masks[index]] @ vector / n
            variance = cp.maximum(
                (square_sums[index] - n * means * means) / (n - 1), 0,
            )
            standard_error = cp.sqrt(variance / n)
            null_columns.append(cp.where(
                standard_error > 1e-12, means / standard_error, 0,
            ))
        null_t = cp.stack(null_columns, axis=1)
        raw_exceed += cp.asnumpy(cp.sum(
            null_t >= gpu_observed[None, :] - 1e-12, axis=0,
        ))
        null_max = cp.max(null_t, axis=1)
        family_exceed += cp.asnumpy(cp.sum(
            null_max[:, None] >= gpu_observed[None, :] - 1e-12, axis=0,
        ))
    return {
        "t": observed_t,
        "raw_p": (1 + raw_exceed) / (permutations + 1),
        "family_p": (1 + family_exceed) / (permutations + 1),
    }


def add_inference(
    results: dict[str, dict[str, Any]], permutations: int, seed: int,
) -> None:
    null = family_sign_flip(results, permutations, seed)
    for index, view in enumerate(VIEWS):
        results[view]["t"] = float(null["t"][index])
        results[view]["raw_one_sided_p"] = float(null["raw_p"][index])
        results[view]["max_t_family_p"] = float(null["family_p"][index])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--permutations", type=int, default=200_000)
    args = parser.parse_args()
    started = time.perf_counter()
    editions = {}
    models = {}
    for edition_index, (edition, path) in enumerate(SOURCES.items()):
        rows = parse_rows(path)
        words = sorted({
            word for row in rows if row.kind == "P" for word in row.words
        })
        score, source_pages, label_count = train_label_score(rows, words)
        result = evaluate_rows(rows, score, set(source_pages))
        add_inference(result, args.permutations, SEED + edition_index)
        editions[edition] = {
            "biological_label_training_items": label_count,
            "excluded_source_pages": source_pages,
            "views": result,
        }
        models[edition] = (rows, source_pages)

    zl_rows, zl_source_pages = models["ZL3b"]
    zl_prose_rows = [row for row in zl_rows if row.kind == "P"]
    timm_rows_by_seed = {}
    for seed in TIMM_SEEDS:
        path = TIMM_DIR / f"generated_text_seed{seed}.txt"
        if path.exists():
            timm_rows_by_seed[seed] = relayout_rows(
                zl_prose_rows, timm_tokens(path),
            )
    timm_words = sorted({
        word for rows in timm_rows_by_seed.values()
        for row in rows for word in row.words
    })
    timm_score = {}
    if timm_words:
        timm_score, _pages, _count = train_label_score(zl_rows, timm_words)
    timm = {
        f"Timm_{seed}": evaluate_rows(
            rows, timm_score, set(zl_source_pages),
        )
        for seed, rows in timm_rows_by_seed.items()
    }

    passed = all(
        row["views"][PRIMARY]["mean_within_line_rise"] > 0
        and row["views"][PRIMARY]["mean_cross_line_reset"] < 0
        and row["views"][PRIMARY]["max_t_family_p"] <= 0.05
        and all(
            value > 0 for value in
            row["views"][PRIMARY]["parity_contrast_means"].values()
        )
        for row in editions.values()
    )
    status = (
        "LINE_LOCAL_WRITING_ORDER_RESET_PASS"
        if passed else "LINE_LOCAL_WRITING_ORDER_RESET_FAIL"
    )
    payload = {
        "meta": {
            "elapsed_seconds": time.perf_counter() - started,
            "permutations": args.permutations,
            "gpu": cp.cuda.runtime.getDeviceProperties(0)["name"].decode(),
            "images_decoded": 0,
        },
        "protocol": {
            "score": "frozen biological-label GLYPH_COUNT/ridge-1 coordinate",
            "residual": "five-fold length plus exact root-free form",
            "source_pages_and_literal_line_edges_removed": True,
            "views": list(VIEWS),
            "primary": PRIMARY,
            "null": "shared whole-page sign flip with max-t correction",
        },
        "editions": editions,
        "timm_controls": timm,
        "decision": {"status": status, "passed": passed},
    }
    payload["meta"]["elapsed_seconds"] = time.perf_counter() - started
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "writing_order_line_reset_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    table = []
    for edition, row in editions.items():
        primary = row["views"][PRIMARY]
        table.append(
            f"| {edition} | {primary['eligible_lines']:,} | "
            f"{primary['mean_within_line_rise']:+.4f} | "
            f"{primary['mean_cross_line_reset']:+.4f} | "
            f"{primary['mean_rise_minus_reset']:+.4f} | "
            f"{primary['positive_contrast_pages']}/{primary['pages']} | "
            f"{primary['max_t_family_p']:.6f} |"
        )
    timm_values = [
        row[PRIMARY]["mean_rise_minus_reset"] for row in timm.values()
    ]
    report = [
        "# Line reset of the transferred writing-order gradient", "",
        "The frozen label-coordinate score is residualized for length and exact root-free form. Literal first/last words and all biological source pages are absent.",
        "",
        "| reading | lines | within-line rise | next-line reset | rise-reset contrast | positive pages | three-view family p |",
        "|---|---:|---:|---:|---:|---:|---:|", *table, "",
        f"**{status}**", "",
    ]
    if passed:
        report += [
            "The coordinate rises across each line and drops when writing returns to the next line's left interior. Safe tag: `[LINE-LOCAL POSITIONAL/PRODUCTION GRADIENT; RESET AT LINE BREAK]`. This rejects a manuscript-long counter and favors line-position-conditioned spelling, selection, or scribal production.",
            "",
        ]
    else:
        report += [
            "The transferred coordinate does not show a robust physical-line reset. Its sequence horizon remains unresolved.",
            "",
        ]
    if timm_values:
        report += [
            f"Five relaid Timm controls have primary rise-reset contrasts from {min(timm_values):+.4f} to {max(timm_values):+.4f} (mean {np.mean(timm_values):+.4f}).",
            "",
        ]
    report.append(
        f"Runtime: **{payload['meta']['elapsed_seconds']:.3f} seconds**; cached transcription/geometry only."
    )
    (RESULTS / "writing_order_line_reset_report.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8",
    )
    print(json.dumps({
        "status": status,
        "editions": {
            edition: {
                "rise": row["views"][PRIMARY]["mean_within_line_rise"],
                "reset": row["views"][PRIMARY]["mean_cross_line_reset"],
                "contrast": row["views"][PRIMARY]["mean_rise_minus_reset"],
                "family_p": row["views"][PRIMARY]["max_t_family_p"],
            }
            for edition, row in editions.items()
        },
        "timm_contrast_mean": float(np.mean(timm_values)) if timm_values else None,
        "elapsed_seconds": payload["meta"]["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
