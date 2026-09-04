#!/usr/bin/env python3
"""Deterministic OUTER10 mirror diagnostics for GDT796.

The module consumes only the published GDT795 source-family atlas.  It keeps
the three outer A06--A15 bands separate from the inner five-member bands and
never imputes the absent A14 entries on f70v1 and f72r1.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

import numpy as np

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
ATLAS = (
    ROOT
    / "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts/"
    "GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv"
)

OUTER_MEMBERS = tuple(range(6, 16))
SELECTORS = ("f70v1", "f71v", "f72r1")
PHYSICAL_FOLIOS = ("f70", "f71", "f72")
PERIOD = 10
NULL_ITERATIONS = 4096
INCLUSIVE_NA_SEED = 79510
FIXED_MASK_SEED = 796013
EPSILON = 1e-12

RANKING_NAME = "GDT796_OUTER10_400_TRANSFORM_RANKINGS.tsv"
NULL_NAME = "GDT796_OUTER10_NULL_SUMMARIES.tsv"
SPLIT_NAME = "GDT796_OUTER10_SPLIT_HALF_RANKS.tsv"
CONTRIBUTION_NAME = "GDT796_OUTER10_BOUNDARY_POSITION_CONTRIBUTIONS.tsv"


@dataclass(frozen=True)
class Transform:
    """One member of D10 in the reported GDT796 convention."""

    name: str
    orientation: int
    shift: int
    indices: np.ndarray
    ordinal: int


@dataclass(frozen=True)
class ViewSpec:
    view_id: str
    field: str
    metric_id: str


VIEW_SPECS = (
    ViewSpec("ZL_MEMBER_NED", "zl_member_sequence", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ViewSpec("IT_MEMBER_NED", "it_member_sequence", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ViewSpec("RF_MEMBER_NED", "rf_member_sequence", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ViewSpec("BOUNDARY_NED", "canonical_boundary_family", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ViewSpec("COMPACT_NED", "canonical_compact_family", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ViewSpec("PREFIX_EXACT", "transferred_prefix", "CATEGORICAL_EXACT"),
    ViewSpec("PREFIX_NED", "transferred_prefix", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ViewSpec("RESIDUAL_NED", "strict_residual", "CHAR_NORMALIZED_LEVENSHTEIN"),
)


PAIR_INDICES = ((0, 1), (0, 2), (1, 2))
TRANSFORM_PARAMETERS = tuple(
    (orientation, shift) for orientation in (1, -1) for shift in range(PERIOD)
)
TRANSFORMS = tuple(
    Transform(
        name=("R" if orientation == 1 else "F") + str(shift),
        orientation=orientation,
        shift=shift,
        indices=np.asarray(
            [(orientation * coordinate + shift) % PERIOD for coordinate in range(PERIOD)],
            dtype=np.int64,
        ),
        ordinal=ordinal,
    )
    for ordinal, (orientation, shift) in enumerate(TRANSFORM_PARAMETERS)
)
TRANSFORM_INDEX = np.stack([transform.indices for transform in TRANSFORMS])
TRANSFORM_ORDINAL_BY_NAME = {transform.name: transform.ordinal for transform in TRANSFORMS}
IDENTITY_ORDINAL = 0
F9_ORDINAL = 19


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: Sequence[str] | None = None) -> None:
    materialized = list(rows)
    fieldnames = list(fields) if fields is not None else (list(materialized[0]) if materialized else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def f12(value: float) -> str:
    return f"{value:.12f}"


def levenshtein(left: Sequence[Any], right: Sequence[Any]) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for row_index, left_item in enumerate(left, start=1):
        current = [row_index]
        for column_index, right_item in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column_index] + 1,
                    previous[column_index - 1] + (left_item != right_item),
                )
            )
        previous = current
    return previous[-1]


def normalized_levenshtein(left: str | None, right: str | None) -> float:
    if left is None or right is None:
        return 0.0
    return 1.0 - levenshtein(left, right) / max(len(left), len(right), 1)


def categorical_exact(left: str | None, right: str | None) -> float:
    if left is None or right is None:
        return 0.0
    return float(left == right)


def transform_for(name: str) -> Transform:
    matches = [transform for transform in TRANSFORMS if transform.name == name]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicated transform: {name}")
    return matches[0]


def load_outer_panel(path: Path = ATLAS) -> list[list[dict[str, str] | None]]:
    """Load exactly f70v1/f71v/f72r1 A06--A15 from the GDT795 atlas."""

    if path.resolve() != ATLAS.resolve():
        raise ValueError("mirror analysis accepts only the canonical GDT795 atlas")
    rows = read_tsv(path)
    if len(rows) != 101:
        raise RuntimeError(f"GDT795 atlas row count changed: {len(rows)}")
    required = {
        "source_selector",
        "physical_folio",
        "template_id",
        "kluge_a_member",
        "locus",
        "complete_label_surface",
        *(spec.field for spec in VIEW_SPECS),
    }
    missing_columns = sorted(required - set(rows[0]))
    if missing_columns:
        raise RuntimeError("GDT795 atlas lacks fields: " + ", ".join(missing_columns))

    keyed: dict[tuple[str, int], dict[str, str]] = {}
    for row in rows:
        selector = row["source_selector"]
        member = int(row["kluge_a_member"])
        key = (selector, member)
        if key in keyed:
            raise RuntimeError(f"duplicate selector/member in GDT795 atlas: {key}")
        keyed[key] = row

    panel: list[list[dict[str, str] | None]] = []
    for selector, physical_folio in zip(SELECTORS, PHYSICAL_FOLIOS):
        sequence: list[dict[str, str] | None] = []
        for member in OUTER_MEMBERS:
            row = keyed.get((selector, member))
            if row is not None:
                if row["template_id"] != "T15" or row["physical_folio"] != physical_folio:
                    raise RuntimeError(f"unexpected outer-panel ownership at {selector} A{member:02d}")
            sequence.append(row)
        panel.append(sequence)

    missing_members = tuple(
        tuple(member for member, row in zip(OUTER_MEMBERS, sequence) if row is None)
        for sequence in panel
    )
    if missing_members != ((14,), (), (14,)):
        raise RuntimeError(f"OUTER10 missing-slot pattern changed: {missing_members}")
    if tuple(sum(row is not None for row in sequence) for sequence in panel) != (9, 10, 9):
        raise RuntimeError("OUTER10 observed-slot counts changed")
    return panel


def metric_for(spec: ViewSpec) -> Callable[[str | None, str | None], float]:
    if spec.metric_id == "CHAR_NORMALIZED_LEVENSHTEIN":
        return normalized_levenshtein
    if spec.metric_id == "CATEGORICAL_EXACT":
        return categorical_exact
    raise ValueError(f"unsupported metric: {spec.metric_id}")


def view_values(
    panel: Sequence[Sequence[dict[str, str] | None]], spec: ViewSpec
) -> list[list[str | None]]:
    return [[None if row is None else row[spec.field] for row in sequence] for sequence in panel]


def build_matrices(
    values: Sequence[Sequence[str | None]],
    metric: Callable[[str | None, str | None], float],
) -> tuple[dict[tuple[int, int], np.ndarray], dict[tuple[int, int], np.ndarray], dict[tuple[int, int], np.ndarray]]:
    similarity: dict[tuple[int, int], np.ndarray] = {}
    comparable: dict[tuple[int, int], np.ndarray] = {}
    exact: dict[tuple[int, int], np.ndarray] = {}
    for left_index, right_index in PAIR_INDICES:
        similarity[left_index, right_index] = np.asarray(
            [[metric(left, right) for right in values[right_index]] for left in values[left_index]],
            dtype=float,
        )
        comparable[left_index, right_index] = np.asarray(
            [
                [float(left is not None and right is not None) for right in values[right_index]]
                for left in values[left_index]
            ],
            dtype=float,
        )
        exact[left_index, right_index] = np.asarray(
            [
                [float(left is not None and right is not None and left == right) for right in values[right_index]]
                for left in values[left_index]
            ],
            dtype=float,
        )
    return similarity, comparable, exact


def score_grids(
    similarity: dict[tuple[int, int], np.ndarray],
    comparable: dict[tuple[int, int], np.ndarray],
    exact: dict[tuple[int, int], np.ndarray],
    subset: np.ndarray | None = None,
) -> dict[str, np.ndarray]:
    """Return 20x20 grids with f70 fixed to R0.

    Rows select the f71 transform and columns select the f72 transform.
    Comparable-normalized score is the sum of the three pair means, not a
    mean pooled over pairs.
    """

    coordinates = np.arange(PERIOD, dtype=np.int64)
    selected = coordinates if subset is None else np.asarray(subset, dtype=np.int64)
    reference = coordinates[selected]

    raw_01 = np.asarray(
        [similarity[0, 1][reference, indices[selected]].sum() for indices in TRANSFORM_INDEX]
    )
    raw_02 = np.asarray(
        [similarity[0, 2][reference, indices[selected]].sum() for indices in TRANSFORM_INDEX]
    )
    count_01 = np.asarray(
        [comparable[0, 1][reference, indices[selected]].sum() for indices in TRANSFORM_INDEX]
    )
    count_02 = np.asarray(
        [comparable[0, 2][reference, indices[selected]].sum() for indices in TRANSFORM_INDEX]
    )
    exact_01 = np.asarray(
        [exact[0, 1][reference, indices[selected]].sum() for indices in TRANSFORM_INDEX]
    )
    exact_02 = np.asarray(
        [exact[0, 2][reference, indices[selected]].sum() for indices in TRANSFORM_INDEX]
    )

    raw_12 = np.empty((20, 20), dtype=float)
    count_12 = np.empty((20, 20), dtype=float)
    exact_12 = np.empty((20, 20), dtype=float)
    for left_ordinal, left_indices in enumerate(TRANSFORM_INDEX):
        raw_12[left_ordinal] = np.asarray(
            [
                similarity[1, 2][left_indices[selected], right_indices[selected]].sum()
                for right_indices in TRANSFORM_INDEX
            ]
        )
        count_12[left_ordinal] = np.asarray(
            [
                comparable[1, 2][left_indices[selected], right_indices[selected]].sum()
                for right_indices in TRANSFORM_INDEX
            ]
        )
        exact_12[left_ordinal] = np.asarray(
            [
                exact[1, 2][left_indices[selected], right_indices[selected]].sum()
                for right_indices in TRANSFORM_INDEX
            ]
        )

    raw = raw_01[:, None] + raw_02[None, :] + raw_12
    pair_01 = np.divide(raw_01, count_01, out=np.zeros_like(raw_01), where=count_01 > 0)
    pair_02 = np.divide(raw_02, count_02, out=np.zeros_like(raw_02), where=count_02 > 0)
    pair_12 = np.divide(raw_12, count_12, out=np.zeros_like(raw_12), where=count_12 > 0)
    normalized = pair_01[:, None] + pair_02[None, :] + pair_12
    exact_hits = exact_01[:, None] + exact_02[None, :] + exact_12
    total_comparable = count_01[:, None] + count_02[None, :] + count_12
    return {
        "raw": raw,
        "normalized": normalized,
        "exact_hits": exact_hits,
        "total_comparable": total_comparable,
        "raw_01": np.broadcast_to(raw_01[:, None], (20, 20)),
        "raw_02": np.broadcast_to(raw_02[None, :], (20, 20)),
        "raw_12": raw_12,
        "count_01": np.broadcast_to(count_01[:, None], (20, 20)),
        "count_02": np.broadcast_to(count_02[None, :], (20, 20)),
        "count_12": count_12,
    }


def score_rank(grid: np.ndarray, row: int, column: int) -> tuple[int, int]:
    value = float(grid[row, column])
    rank = 1 + int(np.sum(grid > value + EPSILON))
    ties = int(np.sum(np.abs(grid - value) <= EPSILON))
    return rank, ties


def select_best(grid: np.ndarray) -> tuple[int, int]:
    """Use row-major np.argmax: R0..R9,F0..F9 for f71, then f72."""

    return tuple(int(value) for value in np.unravel_index(np.argmax(grid), grid.shape))


def transform_ranking_rows(
    panel: Sequence[Sequence[dict[str, str] | None]],
) -> tuple[list[dict[str, Any]], dict[str, tuple[dict[tuple[int, int], np.ndarray], dict[tuple[int, int], np.ndarray], dict[tuple[int, int], np.ndarray]]]]:
    rows: list[dict[str, Any]] = []
    matrices: dict[
        str,
        tuple[
            dict[tuple[int, int], np.ndarray],
            dict[tuple[int, int], np.ndarray],
            dict[tuple[int, int], np.ndarray],
        ],
    ] = {}
    for spec in VIEW_SPECS:
        values = view_values(panel, spec)
        matrix_set = build_matrices(values, metric_for(spec))
        matrices[spec.view_id] = matrix_set
        grids = score_grids(*matrix_set)
        local_rows: list[dict[str, Any]] = []
        for row_ordinal, transform_71 in enumerate(TRANSFORMS):
            for column_ordinal, transform_72 in enumerate(TRANSFORMS):
                raw_rank, raw_ties = score_rank(grids["raw"], row_ordinal, column_ordinal)
                normalized_rank, normalized_ties = score_rank(
                    grids["normalized"], row_ordinal, column_ordinal
                )
                local_rows.append(
                    {
                        "view_id": spec.view_id,
                        "source_field": spec.field,
                        "metric_id": spec.metric_id,
                        "transform_71": transform_71.name,
                        "transform_72": transform_72.name,
                        "transform_71_orientation": transform_71.orientation,
                        "transform_71_shift": transform_71.shift,
                        "transform_72_orientation": transform_72.orientation,
                        "transform_72_shift": transform_72.shift,
                        "raw_score": f12(float(grids["raw"][row_ordinal, column_ordinal])),
                        "raw_rank": raw_rank,
                        "raw_tie_count": raw_ties,
                        "comparable_normalized_score": f12(
                            float(grids["normalized"][row_ordinal, column_ordinal])
                        ),
                        "comparable_normalized_rank": normalized_rank,
                        "comparable_normalized_tie_count": normalized_ties,
                        "exact_value_hits": int(
                            grids["exact_hits"][row_ordinal, column_ordinal]
                        ),
                        "total_comparable_pairs": int(
                            grids["total_comparable"][row_ordinal, column_ordinal]
                        ),
                        "f70_f71_raw_score": f12(
                            float(grids["raw_01"][row_ordinal, column_ordinal])
                        ),
                        "f70_f72_raw_score": f12(
                            float(grids["raw_02"][row_ordinal, column_ordinal])
                        ),
                        "f71_f72_raw_score": f12(
                            float(grids["raw_12"][row_ordinal, column_ordinal])
                        ),
                        "f70_f71_comparable": int(
                            grids["count_01"][row_ordinal, column_ordinal]
                        ),
                        "f70_f72_comparable": int(
                            grids["count_02"][row_ordinal, column_ordinal]
                        ),
                        "f71_f72_comparable": int(
                            grids["count_12"][row_ordinal, column_ordinal]
                        ),
                        "is_reported_f9_r0": "YES"
                        if (row_ordinal, column_ordinal) == (F9_ORDINAL, IDENTITY_ORDINAL)
                        else "NO",
                        "is_identity": "YES"
                        if (row_ordinal, column_ordinal) == (IDENTITY_ORDINAL, IDENTITY_ORDINAL)
                        else "NO",
                    }
                )
        local_rows.sort(
            key=lambda row: (
                int(row["raw_rank"]),
                TRANSFORM_ORDINAL_BY_NAME[str(row["transform_71"])],
                TRANSFORM_ORDINAL_BY_NAME[str(row["transform_72"])],
            )
        )
        rows.extend(local_rows)
    return rows, matrices


def inclusive_na_permutations() -> np.ndarray:
    rng = np.random.default_rng(INCLUSIVE_NA_SEED)
    return np.stack(
        [
            [rng.permutation(PERIOD) for _ in range(len(SELECTORS))]
            for _ in range(NULL_ITERATIONS)
        ]
    )


def fixed_mask_permutations() -> np.ndarray:
    rng = np.random.default_rng(FIXED_MASK_SEED)
    permutations = np.empty((NULL_ITERATIONS, len(SELECTORS), PERIOD), dtype=np.int64)
    observed = (
        np.asarray((0, 1, 2, 3, 4, 5, 6, 7, 9), dtype=np.int64),
        np.arange(PERIOD, dtype=np.int64),
        np.asarray((0, 1, 2, 3, 4, 5, 6, 7, 9), dtype=np.int64),
    )
    for iteration in range(NULL_ITERATIONS):
        for diagram_index, allowed in enumerate(observed):
            permutation = np.arange(PERIOD, dtype=np.int64)
            permutation[allowed] = rng.permutation(allowed)
            permutations[iteration, diagram_index] = permutation
    return permutations


def null_maxima_raw(
    similarity: dict[tuple[int, int], np.ndarray], permutations: np.ndarray
) -> np.ndarray:
    p0, p1, p2 = permutations[:, 0], permutations[:, 1], permutations[:, 2]
    p1_transformed = np.take(p1, TRANSFORM_INDEX, axis=1)
    p2_transformed = np.take(p2, TRANSFORM_INDEX, axis=1)
    score_01 = similarity[0, 1][p0[:, None, :], p1_transformed].sum(axis=2)
    score_02 = similarity[0, 2][p0[:, None, :], p2_transformed].sum(axis=2)
    maxima = np.full(len(permutations), -np.inf, dtype=float)
    for ordinal, indices in enumerate(TRANSFORM_INDEX):
        p1_selected = np.take(p1, indices, axis=1)
        score_12 = similarity[1, 2][p1_selected[:, None, :], p2_transformed].sum(axis=2)
        maxima = np.maximum(
            maxima,
            (score_01[:, ordinal, None] + score_02 + score_12).max(axis=1),
        )
    return maxima


def null_maxima_normalized(
    similarity: dict[tuple[int, int], np.ndarray],
    comparable: dict[tuple[int, int], np.ndarray],
    permutations: np.ndarray,
) -> np.ndarray:
    p0, p1, p2 = permutations[:, 0], permutations[:, 1], permutations[:, 2]
    p1_transformed = np.take(p1, TRANSFORM_INDEX, axis=1)
    p2_transformed = np.take(p2, TRANSFORM_INDEX, axis=1)
    reference = np.arange(PERIOD, dtype=np.int64)

    count_01 = np.asarray(
        [comparable[0, 1][reference, indices].sum() for indices in TRANSFORM_INDEX]
    )
    count_02 = np.asarray(
        [comparable[0, 2][reference, indices].sum() for indices in TRANSFORM_INDEX]
    )
    count_12 = np.asarray(
        [
            [comparable[1, 2][left, right].sum() for right in TRANSFORM_INDEX]
            for left in TRANSFORM_INDEX
        ]
    )
    score_01 = np.divide(
        similarity[0, 1][p0[:, None, :], p1_transformed].sum(axis=2),
        count_01,
        out=np.zeros((len(permutations), len(TRANSFORMS))),
        where=count_01 > 0,
    )
    score_02 = np.divide(
        similarity[0, 2][p0[:, None, :], p2_transformed].sum(axis=2),
        count_02,
        out=np.zeros((len(permutations), len(TRANSFORMS))),
        where=count_02 > 0,
    )
    maxima = np.full(len(permutations), -np.inf, dtype=float)
    for ordinal, indices in enumerate(TRANSFORM_INDEX):
        p1_selected = np.take(p1, indices, axis=1)
        score_12 = np.divide(
            similarity[1, 2][p1_selected[:, None, :], p2_transformed].sum(axis=2),
            count_12[ordinal],
            out=np.zeros((len(permutations), len(TRANSFORMS))),
            where=count_12[ordinal] > 0,
        )
        maxima = np.maximum(
            maxima,
            (score_01[:, ordinal, None] + score_02 + score_12).max(axis=1),
        )
    return maxima


def null_summary_rows(
    matrices: dict[
        str,
        tuple[
            dict[tuple[int, int], np.ndarray],
            dict[tuple[int, int], np.ndarray],
            dict[tuple[int, int], np.ndarray],
        ],
    ]
) -> list[dict[str, Any]]:
    inclusive = inclusive_na_permutations()
    fixed = fixed_mask_permutations()
    rows: list[dict[str, Any]] = []
    for spec in VIEW_SPECS:
        similarity, comparable, exact = matrices[spec.view_id]
        grids = score_grids(similarity, comparable, exact)
        for null_id, seed, score_id, grid_key, maxima in (
            (
                "INCLUSIVE_NA_RAW_SUM",
                INCLUSIVE_NA_SEED,
                "RAW_SUM__NA_PAIR_ZERO",
                "raw",
                null_maxima_raw(similarity, inclusive),
            ),
            (
                "FIXED_MASK_COMPARABLE_NORMALIZED",
                FIXED_MASK_SEED,
                "SUM_OF_THREE_PAIR_MEANS",
                "normalized",
                null_maxima_normalized(similarity, comparable, fixed),
            ),
        ):
            grid = grids[grid_key]
            best_row, best_column = select_best(grid)
            observed = float(grid[best_row, best_column])
            exceedances = int(np.sum(maxima >= observed - EPSILON))
            rows.append(
                {
                    "view_id": spec.view_id,
                    "source_field": spec.field,
                    "metric_id": spec.metric_id,
                    "null_id": null_id,
                    "score_id": score_id,
                    "seed": seed,
                    "iterations": NULL_ITERATIONS,
                    "observed_best_transform_71": TRANSFORMS[best_row].name,
                    "observed_best_transform_72": TRANSFORMS[best_column].name,
                    "observed_best_score": f12(observed),
                    "observed_best_tie_count": int(
                        np.sum(np.abs(grid - observed) <= EPSILON)
                    ),
                    "null_mean_optimized_score": f12(float(np.mean(maxima))),
                    "null_population_sd": f12(float(np.std(maxima))),
                    "null_ge_observed": exceedances,
                    "add_one_p": f12(
                        (exceedances + 1) / (NULL_ITERATIONS + 1)
                    ),
                    "missing_slot_treatment": (
                        "NA_PERMUTED_AS_ONE_OF_TEN_VALUES__NA_PAIR_ZERO"
                        if null_id == "INCLUSIVE_NA_RAW_SUM"
                        else "A14_MASK_FIXED__ONLY_OBSERVED_VALUES_PERMUTED__PAIR_MEANS"
                    ),
                }
            )
    return rows


def split_half_rows(
    matrices: dict[
        str,
        tuple[
            dict[tuple[int, int], np.ndarray],
            dict[tuple[int, int], np.ndarray],
            dict[tuple[int, int], np.ndarray],
        ],
    ]
) -> list[dict[str, Any]]:
    halves = (
        (
            "TRAIN_A06_08_10_12_14__TEST_A07_09_11_13_15",
            np.asarray((0, 2, 4, 6, 8), dtype=np.int64),
            np.asarray((1, 3, 5, 7, 9), dtype=np.int64),
        ),
        (
            "TRAIN_A07_09_11_13_15__TEST_A06_08_10_12_14",
            np.asarray((1, 3, 5, 7, 9), dtype=np.int64),
            np.asarray((0, 2, 4, 6, 8), dtype=np.int64),
        ),
    )
    rows: list[dict[str, Any]] = []
    for spec in VIEW_SPECS:
        matrix_set = matrices[spec.view_id]
        for split_id, train_indices, test_indices in halves:
            train_grids = score_grids(*matrix_set, subset=train_indices)
            test_grids = score_grids(*matrix_set, subset=test_indices)
            row: dict[str, Any] = {
                "view_id": spec.view_id,
                "source_field": spec.field,
                "metric_id": spec.metric_id,
                "split_id": split_id,
                "train_a_members": "|".join(str(OUTER_MEMBERS[index]) for index in train_indices),
                "test_a_members": "|".join(str(OUTER_MEMBERS[index]) for index in test_indices),
            }
            for score_label, grid_key in (
                ("raw", "raw"),
                ("comparable_normalized", "normalized"),
            ):
                train_grid = train_grids[grid_key]
                test_grid = test_grids[grid_key]
                selected_row, selected_column = select_best(train_grid)
                test_rank, test_ties = score_rank(test_grid, selected_row, selected_column)
                row.update(
                    {
                        f"{score_label}_selected_transform_71": TRANSFORMS[selected_row].name,
                        f"{score_label}_selected_transform_72": TRANSFORMS[selected_column].name,
                        f"{score_label}_train_score": f12(
                            float(train_grid[selected_row, selected_column])
                        ),
                        f"{score_label}_train_best_tie_count": int(
                            np.sum(
                                np.abs(
                                    train_grid
                                    - train_grid[selected_row, selected_column]
                                )
                                <= EPSILON
                            )
                        ),
                        f"{score_label}_test_score": f12(
                            float(test_grid[selected_row, selected_column])
                        ),
                        f"{score_label}_test_rank": test_rank,
                        f"{score_label}_test_tie_count": test_ties,
                    }
                )
            rows.append(row)
    return rows


def boundary_position_contribution_rows(
    panel: Sequence[Sequence[dict[str, str] | None]],
) -> list[dict[str, Any]]:
    spec = next(spec for spec in VIEW_SPECS if spec.view_id == "BOUNDARY_NED")
    metric = metric_for(spec)
    f9 = TRANSFORMS[F9_ORDINAL].indices
    identity = TRANSFORMS[IDENTITY_ORDINAL].indices

    def field(row: dict[str, str] | None, name: str) -> str:
        return "NA" if row is None else row[name]

    rows: list[dict[str, Any]] = []
    for coordinate, member in enumerate(OUTER_MEMBERS):
        row_70 = panel[0][identity[coordinate]]
        row_71_f9 = panel[1][f9[coordinate]]
        row_71_identity = panel[1][identity[coordinate]]
        row_72 = panel[2][identity[coordinate]]

        family_70 = None if row_70 is None else row_70[spec.field]
        family_71_f9 = None if row_71_f9 is None else row_71_f9[spec.field]
        family_71_identity = None if row_71_identity is None else row_71_identity[spec.field]
        family_72 = None if row_72 is None else row_72[spec.field]

        f9_01 = metric(family_70, family_71_f9)
        f9_02 = metric(family_70, family_72)
        f9_12 = metric(family_71_f9, family_72)
        identity_01 = metric(family_70, family_71_identity)
        identity_02 = metric(family_70, family_72)
        identity_12 = metric(family_71_identity, family_72)
        f9_total = f9_01 + f9_02 + f9_12
        identity_total = identity_01 + identity_02 + identity_12

        rows.append(
            {
                "semantic_a_member": member,
                "local_coordinate": coordinate,
                "f70_native_a_member": member,
                "f70_locus": field(row_70, "locus"),
                "f70_surface": field(row_70, "complete_label_surface"),
                "f70_boundary_family": field(row_70, spec.field),
                "f71_f9_native_a_member": OUTER_MEMBERS[int(f9[coordinate])],
                "f71_f9_locus": field(row_71_f9, "locus"),
                "f71_f9_surface": field(row_71_f9, "complete_label_surface"),
                "f71_f9_boundary_family": field(row_71_f9, spec.field),
                "f72_native_a_member": member,
                "f72_locus": field(row_72, "locus"),
                "f72_surface": field(row_72, "complete_label_surface"),
                "f72_boundary_family": field(row_72, spec.field),
                "f9_f70_f71_similarity": f12(f9_01),
                "f9_f70_f72_similarity": f12(f9_02),
                "f9_f71_f72_similarity": f12(f9_12),
                "f9_total_contribution": f12(f9_total),
                "identity_f71_native_a_member": member,
                "identity_f71_locus": field(row_71_identity, "locus"),
                "identity_f71_surface": field(row_71_identity, "complete_label_surface"),
                "identity_f71_boundary_family": field(row_71_identity, spec.field),
                "identity_total_contribution": f12(identity_total),
                "f9_minus_identity": f12(f9_total - identity_total),
                "f9_exact_pair_hits": sum(
                    left is not None and right is not None and left == right
                    for left, right in (
                        (family_70, family_71_f9),
                        (family_70, family_72),
                        (family_71_f9, family_72),
                    )
                ),
                "missing_slot_in_reference_pair": "YES"
                if row_70 is None or row_72 is None
                else "NO",
            }
        )
    return rows


def run_analysis(output_dir: Path) -> dict[str, int]:
    panel = load_outer_panel()
    ranking_rows, matrices = transform_ranking_rows(panel)
    null_rows = null_summary_rows(matrices)
    split_rows = split_half_rows(matrices)
    contribution_rows = boundary_position_contribution_rows(panel)
    outputs = (
        (RANKING_NAME, ranking_rows),
        (NULL_NAME, null_rows),
        (SPLIT_NAME, split_rows),
        (CONTRIBUTION_NAME, contribution_rows),
    )
    for name, rows in outputs:
        write_tsv(output_dir / name, rows)
    return {name: len(rows) for name, rows in outputs}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reproduce the GDT796 OUTER10 f71 mirror diagnostics."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="directory for the four deterministic TSV outputs",
    )
    args = parser.parse_args()
    counts = run_analysis(args.output_dir.resolve())
    for name, count in counts.items():
        print(f"{name}\t{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
