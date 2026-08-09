#!/usr/bin/env python3
"""Run the frozen, target-free SME003 synthetic calibration.

This executable refuses to import the numeric implementation until it has
verified the separately created implementation-freeze manifest, every frozen
file named by that manifest, and the absence of every target and result
artifact.  It never accepts a morphology or target path.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[3]
RELATIVE_DIR = "experiments/semantic_assumptions/star_morphology_entry"
RESULT_RELATIVE = f"{RELATIVE_DIR}/sme003_synthetic_calibration_result.json"
REPORT_RELATIVE = "experiments/semantic_assumptions/results/sme003_synthetic_calibration_report.md"
FREEZE_RELATIVE = f"{RELATIVE_DIR}/SME003_CALIBRATION_IMPLEMENTATION_FREEZE.json"
MATRIX_RELATIVE = f"{RELATIVE_DIR}/anonymous_paragraph_matrix.tsv"
INVENTORY_RELATIVE = f"{RELATIVE_DIR}/anonymous_feature_inventory.json"
PREFLIGHT_RELATIVE = f"{RELATIVE_DIR}/sme003_cross_folio_preflight.json"
PREFLIGHT_VALIDATION_RELATIVE = f"{RELATIVE_DIR}/sme003_cross_folio_preflight_validation.json"
AUTHORIZED_COMMAND = (
    "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ./vpy "
    f"{RELATIVE_DIR}/run_sme003_synthetic_calibration.py"
)
CLAIM_CEILING = (
    "anonymous target-free synthetic calibration only; no morphology association, "
    "feature interpretation, meaning, lexeme, plaintext, language, or translation"
)
STRENGTHS = (0.25, 0.50, 0.75, 1.00)
WHOLE_ROW_KINDS = (
    "ONE_FOLIO",
    "ONE_READING",
    "REVERSAL",
    "FOLIO_RANDOM",
    "OPPOSITE_CLUSTER",
)
INVARIANCE_KINDS = (
    "ABS_CUBIC",
    "REL_CUBIC",
    "PARITY",
    "EARLY",
    "QUARTER_1",
    "QUARTER_2",
    "QUARTER_3",
    "LENGTH_LINEAR",
    "LENGTH_CUBIC",
    "PAGE_CONSTANT",
)
MUTATION_KINDS = (
    "duplicate",
    "missing",
    "extra",
    "page_split",
    "folio_drift",
    "ordinal_gap",
    "locus_drift",
    "edition_drift",
    "reordered_feature",
    "negative_word_count",
    "nonfinite",
    "zero_scale",
    "nonpositive_shrunk_covariance",
    "rotation_bias",
    "target_artifact",
)
REQUIRED_FROZEN_FILES = frozenset(
    {
        MATRIX_RELATIVE,
        INVENTORY_RELATIVE,
        f"{RELATIVE_DIR}/SME003_CROSS_FOLIO_PREFLIGHT_SPEC.md",
        f"{RELATIVE_DIR}/build_sme003_cross_folio_preflight.py",
        PREFLIGHT_RELATIVE,
        f"{RELATIVE_DIR}/validate_sme003_cross_folio_preflight.py",
        PREFLIGHT_VALIDATION_RELATIVE,
        "experiments/semantic_assumptions/results/sme003_cross_folio_preflight.md",
        f"{RELATIVE_DIR}/SME003_SYNTHETIC_CALIBRATION_SPEC.md",
        f"{RELATIVE_DIR}/sme003_core.py",
        f"{RELATIVE_DIR}/sme003_fixture.py",
        f"{RELATIVE_DIR}/run_sme003_synthetic_calibration.py",
        f"{RELATIVE_DIR}/validate_sme003_synthetic_calibration.py",
    }
)
REQUIRED_TARGET_PATHS = frozenset(
    {
        "experiments/semantic_assumptions/results/sme001_star_morphology_paragraph_result.md",
        "experiments/semantic_assumptions/results/sme003_cross_folio_result.md",
        f"{RELATIVE_DIR}/SME001_TARGET_RESULT.json",
        f"{RELATIVE_DIR}/SME003_TARGET_RESULT.json",
        f"{RELATIVE_DIR}/TARGET_RESULT.json",
        f"{RELATIVE_DIR}/sme001_target_result.tsv",
        f"{RELATIVE_DIR}/sme003_target_result.tsv",
    }
)


class CalibrationError(RuntimeError):
    """A frozen target-free calibration contract failed closed."""


np: Any = None
core: Any = None
fixture: Any = None
PANEL: Any = None
UNITS: Any = None
LABEL_PANEL: Any = None
ROTATION_FIXTURES: Any = None
ROTATIONS: Any = None
BASELINE_TRANSFORMS: Any = None
BASELINE_PROJECTION: Any = None
FIXTURE_TO_CORE: Any = None
CORE_TO_FIXTURE: Any = None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _repo_path(relative: str) -> Path:
    candidate = (REPO_ROOT / relative).resolve()
    try:
        candidate.relative_to(REPO_ROOT.resolve())
    except ValueError as error:
        raise CalibrationError(f"path escapes repository: {relative!r}") from error
    return candidate


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _require_true_mapping(value: Any, name: str) -> dict[str, bool]:
    if not isinstance(value, dict) or not value:
        raise CalibrationError(f"{name} must be a nonempty object")
    answer: dict[str, bool] = {}
    for key, item in value.items():
        if not isinstance(key, str) or item is not True:
            raise CalibrationError(f"{name} must map paths to literal true")
        _repo_path(key)
        answer[key] = True
    return answer


def _check_absence(paths: Mapping[str, bool], name: str) -> dict[str, bool]:
    checked = _require_true_mapping(paths, name)
    present = [relative for relative in checked if _repo_path(relative).exists()]
    if present:
        raise CalibrationError(f"{name} artifact present: {present}")
    return {relative: True for relative in sorted(checked)}


def _verify_freeze_manifest(path: Path) -> tuple[dict[str, Any], dict[str, bool], dict[str, bool]]:
    manifest = _load_json(path)
    if not isinstance(manifest, dict):
        raise CalibrationError("freeze manifest must be a JSON object")
    if manifest.get("experiment") != "SME003":
        raise CalibrationError("freeze manifest experiment mismatch")
    if manifest.get("status") != "FROZEN_TARGET_FREE_CALIBRATION_UNRUN":
        raise CalibrationError("freeze manifest status is not the frozen-unrun status")
    for key in ("target_rows_accessed", "morphology_fields_accessed", "target_join_performed"):
        if manifest.get(key) is not False:
            raise CalibrationError(f"freeze manifest {key} must be literal false")
    if manifest.get("authorized_command") != AUTHORIZED_COMMAND:
        raise CalibrationError("freeze manifest authorized command mismatch")
    if not isinstance(manifest.get("claim_ceiling"), str) or not manifest["claim_ceiling"].strip():
        raise CalibrationError("freeze manifest claim ceiling is absent")

    frozen = manifest.get("frozen_files")
    if not isinstance(frozen, dict) or set(frozen) != set(REQUIRED_FROZEN_FILES):
        missing = sorted(REQUIRED_FROZEN_FILES - set(frozen or {}))
        extra = sorted(set(frozen or {}) - REQUIRED_FROZEN_FILES)
        raise CalibrationError(
            f"freeze manifest target-free file set mismatch; missing={missing}, extra={extra}"
        )
    for relative, expected in sorted(frozen.items()):
        if not isinstance(relative, str) or not isinstance(expected, str) or len(expected) != 64:
            raise CalibrationError("invalid frozen_files entry")
        actual = _sha256_file(_repo_path(relative))
        if actual != expected:
            raise CalibrationError(f"frozen file hash mismatch: {relative}")

    target_absence = _check_absence(
        manifest.get("target_artifact_absence"), "target_artifact_absence"
    )
    if not REQUIRED_TARGET_PATHS.issubset(target_absence):
        raise CalibrationError(
            "freeze manifest omits one or more required SME001/SME003 target artifacts"
        )
    result_declared = _require_true_mapping(
        manifest.get("result_artifact_absence"), "result_artifact_absence"
    )
    required_results = {RESULT_RELATIVE, REPORT_RELATIVE}
    if not required_results.issubset(result_declared):
        raise CalibrationError("freeze manifest lacks both frozen result-absence paths")
    result_absence = _check_absence(result_declared, "result_artifact_absence")
    return manifest, target_absence, result_absence


def _load_runtime_modules() -> None:
    global np, core, fixture
    if np is not None:
        return
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    np = importlib.import_module("numpy")
    core = importlib.import_module("sme003_core")
    fixture = importlib.import_module("sme003_fixture")


def _initialize_runtime(matrix_path: str, inventory_path: str) -> None:
    global PANEL, UNITS, LABEL_PANEL, ROTATION_FIXTURES, ROTATIONS
    global BASELINE_TRANSFORMS, BASELINE_PROJECTION, FIXTURE_TO_CORE, CORE_TO_FIXTURE
    _load_runtime_modules()
    PANEL = core.load_anonymous(matrix_path, inventory_path, require_frozen_hashes=True)
    core_order_units = tuple(
        fixture.Unit(str(page), int(ordinal), unit_id, str(folio))
        for unit_id, page, ordinal, folio in zip(
            PANEL.unit_ids, PANEL.pages, PANEL.ordinals, PANEL.folios, strict=True
        )
    )
    LABEL_PANEL = fixture.generate_label_panel(core_order_units)
    UNITS = LABEL_PANEL.units
    core_index = {unit_id: index for index, unit_id in enumerate(PANEL.unit_ids)}
    FIXTURE_TO_CORE = np.asarray(
        [core_index[unit.unit_id] for unit in UNITS], dtype=np.int64
    )
    CORE_TO_FIXTURE = np.empty(len(UNITS), dtype=np.int64)
    CORE_TO_FIXTURE[FIXTURE_TO_CORE] = np.arange(len(UNITS), dtype=np.int64)
    if (
        sorted(FIXTURE_TO_CORE.tolist()) != list(range(len(UNITS)))
        or not np.array_equal(
            FIXTURE_TO_CORE[CORE_TO_FIXTURE], np.arange(len(UNITS), dtype=np.int64)
        )
        or tuple(PANEL.unit_ids[index] for index in FIXTURE_TO_CORE)
        != tuple(unit.unit_id for unit in UNITS)
    ):
        raise CalibrationError("core/fixture unit-order permutation contract failed")
    ROTATION_FIXTURES = fixture.build_calibration_rotations()
    ROTATIONS = {
        ensemble: ROTATION_FIXTURES[ensemble].shifts for ensemble in fixture.ENSEMBLES
    }
    BASELINE_TRANSFORMS = core.transform(PANEL)
    BASELINE_PROJECTION = fixture.target_blind_projection_matrix(
        {
            edition: BASELINE_TRANSFORMS.all_folio.standardized[index]
            for index, edition in enumerate(fixture.EDITIONS)
        }
    )
    round_trip = _matrix_from_editions(_values_by_edition(PANEL.values))
    if not np.array_equal(round_trip, PANEL.values):
        raise CalibrationError("core/fixture matrix-order round trip failed")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def _canonical_json_digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _matrix_digest(matrix: Any) -> str:
    array = np.asarray(matrix, dtype=np.float64)
    if array.shape != (156, 3, 84) or not np.isfinite(array).all():
        raise CalibrationError("matrix checkpoint requires finite 156x3x84 values")
    return core.array_sha256(np.transpose(array, (1, 0, 2)), "<f8")


def _values_by_edition(matrix: Any) -> dict[str, Any]:
    array = np.asarray(matrix, dtype=np.float64)
    return {
        edition: np.asarray(
            array[FIXTURE_TO_CORE, index, :], dtype=np.float64, order="C"
        )
        for index, edition in enumerate(fixture.EDITIONS)
    }


def _matrix_from_editions(values: Mapping[str, Any]) -> Any:
    if set(values) != set(fixture.EDITIONS):
        raise CalibrationError("edition matrix key mismatch")
    fixture_order = np.stack(
        [values[edition] for edition in fixture.EDITIONS], axis=1
    )
    core_order = np.empty_like(fixture_order)
    core_order[FIXTURE_TO_CORE] = fixture_order
    return core_order


def _fixture_labels_to_core(labels: Sequence[str]) -> tuple[str, ...]:
    if len(labels) != len(UNITS):
        raise CalibrationError("fixture label length mismatch")
    answer = [""] * len(labels)
    for fixture_index, core_index in enumerate(FIXTURE_TO_CORE.tolist()):
        answer[core_index] = str(labels[fixture_index])
    if any(not state for state in answer):
        raise CalibrationError("fixture/core label remap left an empty state")
    return tuple(answer)


def _paired_labels(world_id: int, *, complement: bool = False) -> Any:
    world = LABEL_PANEL.world(world_id)
    targets: dict[str, tuple[str, ...]] = {}
    for target in fixture.TARGETS:
        labels = world.labels(target)
        if complement:
            labels = tuple(
                fixture.HIGH if state == fixture.LOW else
                fixture.LOW if state == fixture.HIGH else fixture.IGNORED
                for state in labels
            )
        targets[target] = _fixture_labels_to_core(labels)
    return core.PairedLabels(tuple(PANEL.unit_ids), targets)


def _label_checkpoint(world_id: int) -> dict[str, Any]:
    world = LABEL_PANEL.world(world_id)
    target_records: dict[str, Any] = {}
    for target in fixture.TARGETS:
        labels = world.labels(target)
        lines = [
            f"{world_id},{target},{unit.page},{unit.ordinal},{state}\n"
            for unit, state in zip(UNITS, labels, strict=True)
        ]
        pages = fixture.informative_pages(UNITS, labels)
        target_records[target] = {
            "sha256": hashlib.sha256("".join(lines).encode("ascii")).hexdigest(),
            "counts": {state: labels.count(state) for state in fixture.STATES},
            "informative_pages": list(pages),
            "informative_folios": sorted({page[:-1] for page in pages}),
        }
    return {
        "world": world_id,
        "paired_sha256": world.paired_sha256,
        "targets": target_records,
    }


def _transform_checkpoint(bundle: Any) -> dict[str, Any]:
    folds: dict[str, Any] = {}
    for folio in PANEL.folio_names:
        fold = bundle.folds[folio]
        for edition_index, edition in enumerate(PANEL.editions):
            folds[f"{folio}__{edition}"] = {
                "residual_sha256": core.array_sha256(
                    fold.residuals[:, edition_index, :], "<f8"
                ),
                "standardized_sha256": core.array_sha256(
                    fold.standardized[edition_index], "<f8"
                ),
                "weight_sha256": core.array_sha256(fold.weights[edition_index], "<f8"),
                "scales_sha256": core.array_sha256(
                    fold.scales[edition_index, bundle.eligible_mask], "<f8"
                ),
                "rho": float(fold.diagnostics[edition_index]["rho"]),
            }
    return {
        "eligible_features": list(bundle.eligible_features),
        "eligible_sha256": core.string_list_sha256(bundle.eligible_features),
        "folds": folds,
        "all_folio_standardized": {
            edition: core.array_sha256(
                bundle.all_folio.standardized[edition_index], "<f8"
            )
            for edition_index, edition in enumerate(PANEL.editions)
        },
    }


def _score_checkpoint(matrix: Any, labels: Any, *, validate_counts: bool = True) -> tuple[dict[str, Any], Any, Any]:
    transforms = core.transform(PANEL, matrix)
    dual = core.score_world(
        transforms,
        labels,
        ROTATIONS,
        expected_assignments=fixture.CALIBRATION_ASSIGNMENTS,
        validate_directed_counts=validate_counts,
    )
    first = dual.ensembles[fixture.ENSEMBLES[0]]
    orientation = {
        target: {
            "vector_sha256": {
                edition: first.digests["orientation_vectors"][f"{target}__{edition}"]
                for edition in PANEL.editions
            },
            "cosines": dict(first.orientation_cosines[target]),
        }
        for target in fixture.TARGETS
    }
    ensemble_records: dict[str, Any] = {}
    folio_index = {folio: index for index, folio in enumerate(PANEL.folio_names)}
    for ensemble in fixture.ENSEMBLES:
        score = dual.ensembles[ensemble]
        if any(score.orientation_cosines[t] != first.orientation_cosines[t] for t in fixture.TARGETS):
            raise CalibrationError("orientation changed between rotation ensembles")
        targets_record: dict[str, Any] = {}
        for target_index, target in enumerate(fixture.TARGETS):
            support = score.supports[target]
            identity_t = {
                edition: float(score.T[target_index, edition_index, 0])
                for edition_index, edition in enumerate(PANEL.editions)
            }
            identity_z = {
                edition: float(score.z[target_index, edition_index, 0])
                for edition_index, edition in enumerate(PANEL.editions)
            }
            gates = {
                "family_p": bool(score.gates[target]["family_p_at_most_0_05"]),
                "all_t_positive": bool(score.gates[target]["every_reading_raw_T_positive"]),
                "material": bool(score.gates[target]["weakest_reading_material_at_least_0_05"]),
                "orientation": bool(score.gates[target]["all_orientation_cosines_at_least_0_10"]),
                "common_support": bool(score.gates[target]["common_positive_folio_support"]),
                "deletion": bool(score.gates[target]["every_conditional_deletion_positive"]),
            }
            targets_record[target] = {
                "T_sha256": {
                    edition: core.array_sha256(score.T[target_index, edition_index], "<f8")
                    for edition_index, edition in enumerate(PANEL.editions)
                },
                "z_sha256": {
                    edition: core.array_sha256(score.z[target_index, edition_index], "<f8")
                    for edition_index, edition in enumerate(PANEL.editions)
                },
                "R_sha256": core.array_sha256(score.robust_R[target_index], "<f8"),
                "identity_T": identity_t,
                "identity_z": identity_z,
                "identity_R": float(score.robust_R[target_index, 0]),
                "p": float(score.family_p[target]),
                "A": {
                    edition: float(score.raw_A[target_index, edition_index])
                    for edition_index, edition in enumerate(PANEL.editions)
                },
                "identity_contributions": {
                    edition: {
                        folio: float(
                            score.contributions[
                                target_index, edition_index, 0, folio_index[folio]
                            ]
                        )
                        for folio in support.informative_folios
                    }
                    for edition_index, edition in enumerate(PANEL.editions)
                },
                "common_positive_folios": list(score.common_positive_folios[target]),
                "deletion_T": {
                    edition: {
                        folio: float(
                            score.deletion_T[
                                target_index, edition_index, 0, folio_index[folio]
                            ]
                        )
                        for folio in support.informative_folios
                    }
                    for edition_index, edition in enumerate(PANEL.editions)
                },
                "gates": gates,
                "ensemble_pass": bool(score.target_pass[target]),
            }
        ensemble_records[ensemble] = {
            "M_sha256": core.array_sha256(score.family_M, "<f8"),
            "targets": targets_record,
        }
    checkpoint = {
        "matrix_sha256": _matrix_digest(matrix),
        "transforms": _transform_checkpoint(transforms),
        "orientation": orientation,
        "ensembles": ensemble_records,
        "complete_dual_ensemble_pass": {
            target: bool(dual.target_pass[target]) for target in fixture.TARGETS
        },
    }
    return checkpoint, transforms, dual


def _driver(world: int, target: str, driver_name: str, *, folio_random: str | None = None) -> Any:
    base = fixture.build_driver_fixture(
        world,
        target,
        driver_name,
        BASELINE_TRANSFORMS.eligible_features,
        PANEL.formal_features,
        tuple(PANEL.features[len(PANEL.formal_features):]),
    )
    if folio_random is None:
        return base
    signs = tuple(
        -1 if fixture.rank_digest(
            world, f"CONTROL_FOLIO_DIRECTION|{target}|{folio_random}", feature
        )[-1] & 1 == 0 else 1
        for feature in base.features
    )
    return replace(base, signs=signs)


def _projection_for_matrix(matrix: Any, driver_info: Any) -> tuple[Any, Any]:
    transforms = core.transform(PANEL, matrix)
    projection_matrix = fixture.target_blind_projection_matrix(
        {
            edition: transforms.all_folio.standardized[index]
            for index, edition in enumerate(PANEL.editions)
        }
    )
    core_projection = fixture.project_units(
        projection_matrix, transforms.eligible_features, driver_info
    )
    return core_projection[FIXTURE_TO_CORE], transforms


def _plan_mapping(plan: Any, allowed_pages: set[str] | None = None) -> dict[str, list[list[Any]]]:
    answer: dict[str, list[list[Any]]] = {}
    core_index = {unit_id: index for index, unit_id in enumerate(PANEL.unit_ids)}
    for page_plan in plan.pages:
        if allowed_pages is not None and page_plan.page not in allowed_pages:
            answer[page_plan.page] = []
        else:
            answer[page_plan.page] = [
                [
                    core_index[swap.low_unit_id],
                    core_index[swap.high_unit_id],
                    float(swap.gain),
                ]
                for swap in page_plan.complete_swaps
            ]
    return answer


def _plan_stats(plan: Any, mapping: Mapping[str, Sequence[Sequence[Any]]]) -> dict[str, Any]:
    applied: dict[str, int] = {}
    totals: dict[str, int] = {}
    for page_plan in plan.pages:
        total = len(mapping[page_plan.page])
        totals[page_plan.page] = total
        applied[page_plan.page] = min(page_plan.applied_count, total)
    total_trace = sum(totals.values())
    total_applied = sum(applied.values())
    return {
        "trace_lengths": totals,
        "applied_swaps": applied,
        "total_trace": total_trace,
        "total_applied": total_applied,
        "realized_trace_fraction": (
            0.0 if total_trace == 0 else float(total_applied / total_trace)
        ),
    }


def _ordinary_plant(
    matrix: Any,
    world: int,
    target: str,
    driver_name: str,
    strength: float,
    *,
    only_folios: set[str] | None = None,
    reverse_folios: set[str] | None = None,
    editions: Sequence[str] = fixture.EDITIONS if fixture is not None else ("ZL3b", "IT2a", "RF1b"),
) -> tuple[Any, dict[str, Any]]:
    driver_info = _driver(world, target, driver_name)
    projection, _ = _projection_for_matrix(matrix, driver_info)
    if reverse_folios:
        signs = {
            folio: (-1 if folio in reverse_folios else 1)
            for folio in fixture.FOLIO_ORDER
        }
        projection = fixture.folio_signed_projection(UNITS, projection, signs)
    labels = LABEL_PANEL.world(world).labels(target)
    plan = fixture.build_beneficial_swap_plan(UNITS, labels, projection, target, strength)
    allowed_pages = None
    effective = plan
    if only_folios is not None:
        allowed_pages = {page for page in fixture.PAGE_ORDER if page[:-1] in only_folios}
        effective = fixture.restrict_swap_plan(plan, folios=sorted(only_folios))
    planted_editions = fixture.apply_whole_row_plan(
        _values_by_edition(matrix),
        effective,
        unit_ids=tuple(unit.unit_id for unit in UNITS),
        editions_to_apply=editions,
    )
    planted = _matrix_from_editions(planted_editions)
    mapping = _plan_mapping(plan, allowed_pages)
    stats = _plan_stats(effective, mapping)
    stats.update(
        {
            "driver_features": list(driver_info.features),
            "driver_feature_sha256": core.string_list_sha256(driver_info.features),
            "driver_sign_sha256": core.array_sha256(
                np.asarray(driver_info.signs, dtype=np.float64), "<f8"
            ),
            "mapping_sha256": _canonical_json_digest(mapping),
        }
    )
    return planted, stats


def _run_null(task: Mapping[str, Any]) -> dict[str, Any]:
    world = int(task["world"])
    labels = _paired_labels(world)
    evaluation, _, _ = _score_checkpoint(PANEL.values, labels)
    return {
        "world": world,
        "label_sha256": LABEL_PANEL.world(world).paired_sha256,
        "evaluation": evaluation,
        "union_pass": bool(any(evaluation["complete_dual_ensemble_pass"].values())),
    }


def _run_power(task: Mapping[str, Any]) -> dict[str, Any]:
    world = int(task["world"])
    target = str(task["target"])
    driver_name = str(task["driver"])
    strength = float(task["strength"])
    planted, stats = _ordinary_plant(
        PANEL.values, world, target, driver_name, strength
    )
    labels = _paired_labels(world)
    evaluation, transforms, _ = _score_checkpoint(planted, labels)
    selected = tuple(stats["driver_features"])
    driver_map = {
        item: (
            selected if item == target else tuple(transforms.eligible_features)
        )
        for item in fixture.TARGETS
    }
    rms = core.realized_driver_rms(transforms, labels, driver_map)[target]
    return {
        "world": world,
        "target": target,
        "driver": driver_name,
        "strength": strength,
        "label_sha256": LABEL_PANEL.world(world).paired_sha256,
        "plant": stats,
        "realized_D_rms": rms,
        "evaluation": evaluation,
        "target_complete_pass": bool(
            evaluation["complete_dual_ensemble_pass"][target]
        ),
    }


def _reversal_plant(world: int, target: str, driver_name: str) -> tuple[Any, dict[str, Any]]:
    driver_info = _driver(world, target, driver_name)
    projection, _ = _projection_for_matrix(PANEL.values, driver_info)
    labels = LABEL_PANEL.world(world).labels(target)
    forward = fixture.build_beneficial_swap_plan(
        UNITS, labels, projection, target, 1.0
    )
    reverse = fixture.build_beneficial_swap_plan(
        UNITS, labels, -projection, target, 1.0
    )
    planted = fixture.apply_edition_plans(
        _values_by_edition(PANEL.values),
        {
            "ZL3b": forward,
            "IT2a": forward,
            "RF1b": reverse,
        },
        unit_ids=tuple(unit.unit_id for unit in UNITS),
    )
    forward_mapping = _plan_mapping(forward)
    reverse_mapping = _plan_mapping(reverse)
    stats = {
        "driver_features": list(driver_info.features),
        "driver_feature_sha256": core.string_list_sha256(driver_info.features),
        "driver_sign_sha256": core.array_sha256(
            np.asarray(driver_info.signs, dtype=np.float64), "<f8"
        ),
        "forward_mapping_sha256": _canonical_json_digest(forward_mapping),
        "reverse_mapping_sha256": _canonical_json_digest(reverse_mapping),
        "forward": _plan_stats(forward, forward_mapping),
        "reverse": _plan_stats(reverse, reverse_mapping),
    }
    return _matrix_from_editions(planted), stats


def _folio_random_plant(world: int, target: str, driver_name: str) -> tuple[Any, dict[str, Any]]:
    labels = LABEL_PANEL.world(world).labels(target)
    informative_folios = sorted(
        {page[:-1] for page in fixture.informative_pages(UNITS, labels)}
    )
    selected = _driver(world, target, driver_name).features
    planted = _values_by_edition(PANEL.values)
    mapping_digests: dict[str, str] = {}
    folio_stats: dict[str, Any] = {}
    for folio in informative_folios:
        driver_info = _driver(world, target, driver_name, folio_random=folio)
        projection_core = fixture.project_units(
            BASELINE_PROJECTION, BASELINE_TRANSFORMS.eligible_features, driver_info
        )
        projection = projection_core[FIXTURE_TO_CORE]
        full_plan = fixture.build_beneficial_swap_plan(
            UNITS, labels, projection, target, 1.0
        )
        plan = fixture.restrict_swap_plan(full_plan, folios=(folio,))
        allowed = {page for page in fixture.PAGE_ORDER if page[:-1] == folio}
        mapping = _plan_mapping(full_plan, allowed)
        planted = fixture.apply_whole_row_plan(
            planted, plan, unit_ids=tuple(unit.unit_id for unit in UNITS)
        )
        mapping_digests[folio] = _canonical_json_digest(mapping)
        folio_stats[folio] = _plan_stats(plan, mapping)
    return _matrix_from_editions(planted), {
        "driver_features": list(selected),
        "folio_mapping_sha256": mapping_digests,
        "folio_stats": folio_stats,
    }


def _run_whole_row(task: Mapping[str, Any]) -> dict[str, Any]:
    kind = str(task["kind"])
    world = int(task["world"])
    target = str(task["target"])
    driver_name = str(task["driver"])
    labels = LABEL_PANEL.world(world).labels(target)
    informative_folios = sorted(
        {page[:-1] for page in fixture.informative_pages(UNITS, labels)}
    )
    if kind == "ONE_FOLIO":
        chosen = min(
            informative_folios,
            key=lambda folio: fixture.rank_key(
                world, f"CONTROL_ONE_FOLIO|{target}", folio
            ),
        )
        planted, stats = _ordinary_plant(
            PANEL.values,
            world,
            target,
            driver_name,
            1.0,
            only_folios={chosen},
        )
        stats["selected_folio"] = chosen
    elif kind == "ONE_READING":
        planted, stats = _ordinary_plant(
            PANEL.values,
            world,
            target,
            driver_name,
            1.0,
            editions=("ZL3b",),
        )
    elif kind == "REVERSAL":
        planted, stats = _reversal_plant(world, target, driver_name)
    elif kind == "FOLIO_RANDOM":
        planted, stats = _folio_random_plant(world, target, driver_name)
    elif kind == "OPPOSITE_CLUSTER":
        ordered = sorted(
            informative_folios,
            key=lambda folio: fixture.rank_key(
                world, f"CONTROL_CLUSTER|{target}", folio
            ),
        )
        forward_count = 4 if target == fixture.RAY_LIKE else 3
        reverse = set(ordered[forward_count:])
        planted, stats = _ordinary_plant(
            PANEL.values,
            world,
            target,
            driver_name,
            1.0,
            reverse_folios=reverse,
        )
        stats["ordered_folios"] = ordered
        stats["reverse_folios"] = sorted(reverse)
    else:
        raise CalibrationError(f"unknown whole-row control: {kind}")
    evaluation, _, _ = _score_checkpoint(planted, _paired_labels(world))
    rejected = not bool(evaluation["complete_dual_ensemble_pass"][target])
    if kind == "ONE_FOLIO":
        required_rejection = all(
            (
                not evaluation["ensembles"][ensemble]["targets"][target]["gates"]["common_support"]
            )
            or (
                not evaluation["ensembles"][ensemble]["targets"][target]["gates"]["deletion"]
            )
            for ensemble in fixture.ENSEMBLES
        )
    elif kind in ("ONE_READING", "REVERSAL"):
        required_rejection = all(
            any(
                not evaluation["ensembles"][ensemble]["targets"][target]["gates"][gate]
                for gate in ("all_t_positive", "material", "orientation")
            )
            for ensemble in fixture.ENSEMBLES
        )
    else:
        required_rejection = rejected
    return {
        "kind": kind,
        "target": target,
        "driver": driver_name,
        "world": world,
        "label_sha256": LABEL_PANEL.world(world).paired_sha256,
        "plant": stats,
        "evaluation": evaluation,
        "target_rejected": rejected,
        "required_rejection_gate_failed": required_rejection,
    }


def _page_center(values: Any) -> Any:
    array = np.asarray(values, dtype=np.float64)
    answer = np.empty_like(array, dtype=np.float64)
    for page in PANEL.page_names:
        mask = PANEL.pages == page
        answer[mask] = array[mask] - np.mean(
            array[mask], axis=0, keepdims=True
        )
    return answer


def _response_rms(matrix: Any, edition_index: int, feature_index: int) -> float:
    centered = _page_center(np.asarray(matrix)[:, edition_index, feature_index])
    rms = math.sqrt(float(np.mean(centered * centered)))
    if not math.isfinite(rms) or rms <= core.NUM_TOL:
        raise CalibrationError("zero/nonfinite response population RMS")
    return rms


def _signed_component(
    matrix: Any,
    basis: Any,
    fraction: float,
    domain: str,
    feature_names: Sequence[str],
) -> Any:
    answer = np.asarray(matrix, dtype=np.float64).copy()
    centered = _page_center(np.asarray(basis, dtype=np.float64))
    basis_rms = math.sqrt(float(np.mean(centered * centered)))
    if not math.isfinite(basis_rms) or basis_rms <= core.NUM_TOL:
        raise CalibrationError("zero/nonfinite control basis population RMS")
    normalized = centered / basis_rms
    feature_index = {name: index for index, name in enumerate(PANEL.features)}
    for feature in feature_names:
        index = feature_index[feature]
        sign = 1.0 if fixture.rank_digest(0, domain, feature)[-1] & 1 else -1.0
        for edition_index in range(3):
            amplitude = fraction * _response_rms(matrix, edition_index, index)
            answer[:, edition_index, index] += sign * amplitude * normalized
    return answer


def _invariance_matrix(kind: str) -> tuple[Any, float]:
    ordinals = PANEL.ordinals.astype(np.float64)
    sizes = np.asarray(
        [fixture.PAGE_SIZES[str(page)] for page in PANEL.pages], dtype=np.float64
    )
    relative = (ordinals - 0.5) / sizes
    absolute = (ordinals - 0.5) / 16.0
    quarter = np.minimum((relative * 4.0).astype(np.int64), 3)
    eligible_without_word_count = tuple(
        feature for feature in BASELINE_TRANSFORMS.eligible_features
        if feature != "PARA_WORD_COUNT"
    )
    positional = {
        "ABS_CUBIC": absolute ** 3,
        "REL_CUBIC": relative ** 3,
        "PARITY": (PANEL.ordinals % 2 == 1).astype(np.float64),
        "EARLY": (ordinals <= sizes / 2.0).astype(np.float64),
        "QUARTER_1": (quarter == 1).astype(np.float64),
        "QUARTER_2": (quarter == 2).astype(np.float64),
        "QUARTER_3": (quarter == 3).astype(np.float64),
    }
    if kind in positional:
        return _signed_component(
            PANEL.values,
            positional[kind],
            0.5,
            f"CONTROL_NUISANCE|{kind}",
            eligible_without_word_count,
        ), 1e-10
    if kind in ("LENGTH_LINEAR", "LENGTH_CUBIC"):
        power = 1 if kind == "LENGTH_LINEAR" else 3
        answer = np.asarray(PANEL.values, dtype=np.float64).copy()
        wc_index = PANEL.features.index("PARA_WORD_COUNT")
        root_features = tuple(PANEL.features[len(PANEL.formal_features):])
        feature_index = {name: index for index, name in enumerate(PANEL.features)}
        for edition_index in range(3):
            raw = np.log1p(PANEL.values[:, edition_index, wc_index]) ** power
            basis = _page_center(raw)
            basis_rms = math.sqrt(float(np.mean(basis * basis)))
            if not math.isfinite(basis_rms) or basis_rms <= core.NUM_TOL:
                raise CalibrationError("zero/nonfinite word-count control RMS")
            for feature in root_features:
                index = feature_index[feature]
                sign = 1.0 if fixture.rank_digest(
                    0, f"CONTROL_LENGTH|{kind}", feature
                )[-1] & 1 else -1.0
                amplitude = 0.5 * _response_rms(PANEL.values, edition_index, index)
                answer[:, edition_index, index] += sign * amplitude * basis / basis_rms
        return answer, 1e-10
    if kind == "PAGE_CONSTANT":
        answer = np.asarray(PANEL.values, dtype=np.float64).copy()
        feature_index = {name: index for index, name in enumerate(PANEL.features)}
        for edition_index in range(3):
            for page, positions in zip(PANEL.page_names, PANEL.page_positions, strict=True):
                for feature in eligible_without_word_count:
                    index = feature_index[feature]
                    sign = 1.0 if fixture.rank_digest(
                        0, f"CONTROL_PAGE_CONSTANT|{page}", feature
                    )[-1] & 1 else -1.0
                    answer[positions, edition_index, index] += (
                        0.10 * sign * _response_rms(PANEL.values, edition_index, index)
                    )
        return answer, 1e-12
    raise CalibrationError(f"unknown invariance control: {kind}")


def _orientation_vectors(transforms: Any, labels: Any, validate_counts: bool) -> Any:
    encoded, supports = core._encode_targets(
        PANEL,
        labels.targets,
        labels.unit_ids,
        validate_directed_counts=validate_counts,
    )
    contrasts = core._page_contrast_tables(PANEL, encoded)
    directions = core._identity_directions(transforms, contrasts, supports)
    return {
        target: {
            edition: directions[target][edition_index]
            for edition_index, edition in enumerate(PANEL.editions)
        }
        for target in fixture.TARGETS
    }


def _invariance_comparison(
    baseline_transforms: Any,
    baseline_score: Any,
    baseline_directions: Mapping[str, Mapping[str, Any]],
    transforms: Any,
    score: Any,
    directions: Mapping[str, Mapping[str, Any]],
    tolerance: float,
    *,
    compare_orientation_vectors: bool = True,
) -> dict[str, Any]:
    residual_max = max(
        float(np.max(np.abs(
            baseline_transforms.folds[folio].residuals
            - transforms.folds[folio].residuals
        )))
        for folio in PANEL.folio_names
    )
    residual_max = max(
        residual_max,
        float(np.max(np.abs(
            baseline_transforms.all_folio.residuals
            - transforms.all_folio.residuals
        ))),
    )
    score_differences: list[float] = []
    if compare_orientation_vectors:
        score_differences.extend(
            float(np.max(np.abs(
                baseline_directions[target][edition]
                - directions[target][edition]
            )))
            for target in fixture.TARGETS
            for edition in PANEL.editions
        )
    score_differences.extend(
        abs(
            float(baseline_score.ensembles[ensemble].orientation_cosines[target][pair])
            - float(score.ensembles[ensemble].orientation_cosines[target][pair])
        )
        for ensemble in fixture.ENSEMBLES
        for target in fixture.TARGETS
        for pair in baseline_score.ensembles[ensemble].orientation_cosines[target]
    )
    for ensemble in fixture.ENSEMBLES:
        left = baseline_score.ensembles[ensemble]
        right = score.ensembles[ensemble]
        for left_array, right_array in (
            (left.T, right.T),
            (left.z, right.z),
            (left.robust_R, right.robust_R),
            (left.family_M, right.family_M),
            (left.contributions, right.contributions),
            (left.deletion_T, right.deletion_T),
        ):
            if left_array.shape != right_array.shape or not np.array_equal(
                np.isnan(left_array), np.isnan(right_array)
            ):
                raise CalibrationError("invariance score defined-mask drift")
            finite = np.isfinite(left_array) & np.isfinite(right_array)
            score_differences.append(
                float(np.max(np.abs(left_array[finite] - right_array[finite])))
                if np.any(finite) else 0.0
            )
    score_max = max(score_differences, default=0.0)
    gates_identical = (
        baseline_score.target_pass == score.target_pass
        and all(
            baseline_score.ensembles[ensemble].gates
            == score.ensembles[ensemble].gates
            for ensemble in fixture.ENSEMBLES
        )
    )
    passes = (
        residual_max <= tolerance
        and score_max <= tolerance
        and gates_identical
    )
    return {
        "residual_max_abs": residual_max,
        "score_max_abs": score_max,
        "tolerance": tolerance,
        "gates_identical": gates_identical,
        "passes": passes,
    }


def _run_invariance(task: Mapping[str, Any]) -> dict[str, Any]:
    kind = str(task["kind"])
    modified, tolerance = _invariance_matrix(kind)
    labels = _paired_labels(0)
    baseline_evaluation, baseline_transforms, baseline_score = _score_checkpoint(
        PANEL.values, labels
    )
    evaluation, transforms, score = _score_checkpoint(modified, labels)
    comparison = _invariance_comparison(
        baseline_transforms,
        baseline_score,
        _orientation_vectors(baseline_transforms, labels, True),
        transforms,
        score,
        _orientation_vectors(transforms, labels, True),
        tolerance,
    )
    if (
        comparison["gates_identical"]
        != (
            evaluation["complete_dual_ensemble_pass"]
            == baseline_evaluation["complete_dual_ensemble_pass"]
        )
    ):
        raise CalibrationError("invariance gate comparison is internally inconsistent")
    return {
        "kind": kind,
        "world": 0,
        "matrix_sha256": _matrix_digest(modified),
        "evaluation": evaluation,
        "invariance": comparison,
    }


def _run_complement(_: Mapping[str, Any]) -> dict[str, Any]:
    labels = _paired_labels(0)
    complemented_labels = _paired_labels(0, complement=True)
    baseline, baseline_transforms, baseline_score = _score_checkpoint(PANEL.values, labels)
    complemented, transforms, score = _score_checkpoint(
        PANEL.values, complemented_labels, validate_counts=False
    )
    baseline_directions = _orientation_vectors(baseline_transforms, labels, True)
    complemented_directions = _orientation_vectors(
        transforms, complemented_labels, False
    )
    comparison = _invariance_comparison(
        baseline_transforms,
        baseline_score,
        baseline_directions,
        transforms,
        score,
        complemented_directions,
        1e-12,
        compare_orientation_vectors=False,
    )
    reversal_max = max(
        float(np.max(np.abs(
            baseline_directions[target][edition]
            + complemented_directions[target][edition]
        )))
        for target in fixture.TARGETS
        for edition in PANEL.editions
    )
    invariant = comparison["passes"] and reversal_max <= 1e-12
    return {
        "world": 0,
        "baseline": baseline,
        "complemented": complemented,
        "score_invariance": comparison,
        "orientation_reversal_max_abs": reversal_max,
        "decision_invariant": invariant,
    }


def _identity_training_direction(bundle: Any, labels: Sequence[str], held: str) -> Any | None:
    labels_array = np.asarray(labels)
    if labels_array.shape != (len(PANEL.unit_ids),):
        raise CalibrationError("training-direction label length mismatch")
    pages = tuple(
        page
        for page, positions in zip(PANEL.page_names, PANEL.page_positions, strict=True)
        if np.any(labels_array[positions] == fixture.LOW)
        and np.any(labels_array[positions] == fixture.HIGH)
    )
    folios = sorted({page[:-1] for page in pages})
    if held not in folios:
        return None
    fold = bundle.folds[held]
    answer = np.empty((3, len(bundle.eligible_features)), dtype=np.float64)
    for edition_index in range(3):
        vectors = []
        for folio in folios:
            if folio == held:
                continue
            page_vectors = []
            for page, positions in zip(PANEL.page_names, PANEL.page_positions, strict=True):
                if page[:-1] != folio or page not in pages:
                    continue
                states = labels_array[positions]
                standardized = fold.standardized[edition_index, positions]
                page_vectors.append(
                    np.mean(standardized[states == fixture.HIGH], axis=0)
                    - np.mean(standardized[states == fixture.LOW], axis=0)
                )
            vectors.append(np.mean(np.stack(page_vectors), axis=0))
        answer[edition_index] = np.mean(np.stack(vectors), axis=0)
    return answer


def _run_leakage(task: Mapping[str, Any]) -> dict[str, Any]:
    held = str(task["held_folio"])
    mutated = np.asarray(PANEL.values, dtype=np.float64).copy()
    for page, positions in zip(PANEL.page_names, PANEL.page_positions, strict=True):
        if page[:-1] != held:
            continue
        source = sorted(
            positions.tolist(),
            key=lambda index: fixture.rank_key(
                0, f"CONTROL_HELD_MUTATION|{held}", PANEL.unit_ids[index]
            ),
        )
        mutated[positions, :, :] = PANEL.values[np.asarray(source), :, :]
    changed = core.transform(PANEL, mutated)
    labels_pair = _paired_labels(0)
    pre: dict[str, Any] = {}
    post: dict[str, Any] = {}
    train = PANEL.folios != held
    for edition_index, edition in enumerate(PANEL.editions):
        before = BASELINE_TRANSFORMS.folds[held]
        after = changed.folds[held]
        before_directions: dict[str, str | None] = {}
        after_directions: dict[str, str | None] = {}
        for target in fixture.TARGETS:
            left = _identity_training_direction(
                BASELINE_TRANSFORMS, labels_pair.targets[target], held
            )
            right = _identity_training_direction(
                changed, labels_pair.targets[target], held
            )
            before_directions[target] = (
                None if left is None else core.array_sha256(left[edition_index], "<f8")
            )
            after_directions[target] = (
                None if right is None else core.array_sha256(right[edition_index], "<f8")
            )
        pre[edition] = {
            "weight": core.array_sha256(before.weights[edition_index], "<f8"),
            "training_rows": core.array_sha256(
                before.standardized[edition_index, train], "<f8"
            ),
            "training_directions": before_directions,
        }
        post[edition] = {
            "weight": core.array_sha256(after.weights[edition_index], "<f8"),
            "training_rows": core.array_sha256(
                after.standardized[edition_index, train], "<f8"
            ),
            "training_directions": after_directions,
        }
    return {"held_folio": held, "pre": pre, "post": post, "unchanged": pre == post}


def _independent_baseline(world: int) -> tuple[Any, dict[str, str]]:
    baseline = np.asarray(PANEL.values, dtype=np.float64).copy()
    digests: dict[str, str] = {}
    for edition_index, edition in enumerate(PANEL.editions):
        for page, positions in zip(PANEL.page_names, PANEL.page_positions, strict=True):
            destinations = sorted(
                positions.tolist(),
                key=lambda index: (
                    fixture.rank_key(
                        world,
                        f"CONTROL_INDEPENDENT_BASELINE|{edition}|{page}",
                        PANEL.unit_ids[index],
                    ),
                    int(PANEL.ordinals[index]),
                    PANEL.unit_ids[index],
                ),
            )
            destination_array = np.asarray(destinations, dtype=np.int64)
            baseline[destination_array, edition_index, :] = PANEL.values[
                positions, edition_index, :
            ]
            lines = "".join(
                f"{PANEL.unit_ids[source]},{PANEL.unit_ids[destination]}\n"
                for source, destination in zip(
                    positions.tolist(), destinations, strict=True
                )
            )
            digests[f"{edition}__{page}"] = hashlib.sha256(
                lines.encode("ascii")
            ).hexdigest()
    return baseline, digests


def _run_dependence(task: Mapping[str, Any]) -> dict[str, Any]:
    world = int(task["world"])
    target = str(task["target"])
    driver_name = str(task["driver"])
    baseline, permutation_digests = _independent_baseline(world)
    planted, stats = _ordinary_plant(
        baseline, world, target, driver_name, 1.0
    )
    evaluation, _, _ = _score_checkpoint(planted, _paired_labels(world))
    return {
        "target": target,
        "driver": driver_name,
        "world": world,
        "label_sha256": LABEL_PANEL.world(world).paired_sha256,
        "baseline_matrix_sha256": _matrix_digest(baseline),
        "reading_page_permutation_sha256": permutation_digests,
        "planted_matrix_sha256": _matrix_digest(planted),
        "plant": stats,
        "evaluation": evaluation,
        "diagnostic_only": True,
    }


def _run_task(task: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    category = str(task["category"])
    handlers = {
        "null": _run_null,
        "power": _run_power,
        "whole_row": _run_whole_row,
        "invariance": _run_invariance,
        "complement": _run_complement,
        "leakage": _run_leakage,
        "dependence": _run_dependence,
    }
    if category not in handlers:
        raise CalibrationError(f"unknown worker category: {category}")
    return category, handlers[category](task)


def _assert_panel_binding(panel: Any) -> None:
    if (
        len(panel.unit_ids) != 156
        or len(set(panel.unit_ids)) != 156
        or tuple(panel.page_names) != fixture.PAGE_ORDER
        or tuple(panel.folio_names) != fixture.FOLIO_ORDER
        or tuple(panel.editions) != fixture.EDITIONS
        or len(panel.features) != 84
        or tuple(panel.features[:len(panel.formal_features)]) != tuple(panel.formal_features)
        or tuple(panel.features[len(panel.formal_features):])
        != tuple(
            "ROOT_ATOM_RATE__" + name for name in panel.root_atom_features
        ) + tuple("ROOT_WORD_RATE__" + name for name in panel.root_word_features)
    ):
        raise CalibrationError("anonymous panel binding contract failed")
    for page, positions in zip(panel.page_names, panel.page_positions, strict=True):
        if (
            len(positions) != fixture.PAGE_SIZES[page]
            or panel.ordinals[positions].tolist()
            != list(range(1, fixture.PAGE_SIZES[page] + 1))
            or set(panel.pages[positions].tolist()) != {page}
            or set(panel.folios[positions].tolist()) != {page[:-1]}
        ):
            raise CalibrationError(f"page metadata binding failed: {page}")
    if len(panel.loci) != 156 or len(set(panel.loci)) != 156:
        raise CalibrationError("locus binding contract failed")


def _must_reject(name: str, function: Any) -> dict[str, Any]:
    try:
        function()
    except Exception as error:  # Mutation probes require any fail-closed exception.
        message = f"{type(error).__name__}: {error}"
        if not message.strip():
            raise CalibrationError(f"{name} mutation produced an empty error")
        return {"mutation": name, "rejected": True, "error": message}
    raise CalibrationError(f"mutation was not rejected: {name}")


def _mutation_records() -> list[dict[str, Any]]:
    units = list(UNITS)
    probes: dict[str, Any] = {
        "duplicate": lambda: fixture.generate_label_panel(units[:-1] + [units[0]]),
        "missing": lambda: fixture.generate_label_panel(units[:-1]),
        "extra": lambda: fixture.generate_label_panel(units + [units[-1]]),
        "page_split": lambda: fixture.generate_label_panel(
            [replace(units[0], page="f104v")] + units[1:]
        ),
        "folio_drift": lambda: fixture.generate_label_panel(
            [replace(units[0], physical_folio="f105")] + units[1:]
        ),
        "ordinal_gap": lambda: fixture.generate_label_panel(
            [replace(units[0], ordinal=2)] + units[1:]
        ),
        "locus_drift": lambda: _assert_panel_binding(
            replace(PANEL, loci=PANEL.loci[:-1] + (PANEL.loci[-2],))
        ),
        "edition_drift": lambda: _assert_panel_binding(
            replace(PANEL, editions=("ZL3b", "IT2a", "DRIFT"))
        ),
        "reordered_feature": lambda: _assert_panel_binding(
            replace(PANEL, features=tuple(reversed(PANEL.features)))
        ),
        "negative_word_count": lambda: core.transform(
            PANEL,
            _numeric_mutation("negative_word_count"),
        ),
        "nonfinite": lambda: core.transform(PANEL, _numeric_mutation("nonfinite")),
        "zero_scale": lambda: core.transform(PANEL, _numeric_mutation("zero_scale")),
        "nonpositive_shrunk_covariance": lambda: core.analytic_oas(
            np.zeros((10, 83), dtype=np.float64)
        ),
        "rotation_bias": lambda: core.validate_rotations(
            PANEL,
            _biased_rotation(),
            ensemble=fixture.INDEPENDENT_PAGE,
            expected_assignments=fixture.CALIBRATION_ASSIGNMENTS,
        ),
        "target_artifact": lambda: _check_absence(
            {f"{RELATIVE_DIR}/run_sme003_synthetic_calibration.py": True},
            "synthetic_target_artifact_mutation",
        ),
    }
    return [_must_reject(name, probes[name]) for name in MUTATION_KINDS]


def _numeric_mutation(name: str) -> Any:
    answer = np.asarray(PANEL.values, dtype=np.float64).copy()
    if name == "negative_word_count":
        answer[0, 0, PANEL.features.index("PARA_WORD_COUNT")] = -1.0
    elif name == "nonfinite":
        answer[0, 0, 0] = np.nan
    elif name == "zero_scale":
        answer[:, :, 0] = 0.0
    else:
        raise CalibrationError(f"unknown numeric mutation: {name}")
    return answer


def _biased_rotation() -> Any:
    answer = np.asarray(
        ROTATION_FIXTURES[fixture.INDEPENDENT_PAGE].shifts, dtype="<u2"
    ).copy(order="C")
    answer[1] = answer[0]
    return answer


def _validate_preflight(preflight: Mapping[str, Any], validation: Mapping[str, Any]) -> None:
    if (
        preflight.get("experiment") != "SME003"
        or preflight.get("status") != "PASS_TARGET_BLIND_CROSS_FOLIO_PREFLIGHT"
        or preflight.get("decision") != "GO_TO_TARGET_FREE_SYNTHETIC_DESIGN"
        or preflight.get("target_rows_accessed") is not False
        or preflight.get("morphology_fields_accessed") is not False
        or preflight.get("target_join_performed") is not False
        or not all(preflight.get("gates", {}).values())
    ):
        raise CalibrationError("preflight artifact is not an intact target-blind pass")
    if (
        validation.get("experiment") != "SME003"
        or validation.get("status")
        != "PASS_INDEPENDENT_NONIMPORTING_PREFLIGHT_VALIDATION"
        or validation.get("decision") != "GO_TO_TARGET_FREE_SYNTHETIC_DESIGN_ONLY"
    ):
        raise CalibrationError("preflight validator result is not an intact pass")
    checkpoint = _transform_checkpoint(BASELINE_TRANSFORMS)
    if checkpoint["eligible_features"] != list(
        preflight["formal_eligible"] + preflight["root_eligible"]
    ):
        raise CalibrationError("preflight eligible-feature reconstruction mismatch")
    for key, record in preflight["transforms"].items():
        observed = checkpoint["folds"].get(key)
        if observed is None:
            raise CalibrationError(f"preflight transform absent from reconstruction: {key}")
        if (
            observed["standardized_sha256"]
            != record["standardized_matrix_sha256"]
            or observed["weight_sha256"] != record["weight_matrix_sha256"]
            or abs(observed["rho"] - float(record["rho"])) > 5e-12
        ):
            raise CalibrationError(f"preflight transform reconstruction mismatch: {key}")


def _rotation_checkpoint() -> dict[str, Any]:
    return {
        ensemble: {
            "N": fixture.CALIBRATION_ASSIGNMENTS,
            "shape": list(ROTATION_FIXTURES[ensemble].shifts.shape),
            "dtype": "<u2",
            "order": "C",
            "sha256": ROTATION_FIXTURES[ensemble].sha256,
            "unique_rows": int(
                np.unique(ROTATION_FIXTURES[ensemble].shifts, axis=0).shape[0]
            ),
            "row_attempts": list(ROTATION_FIXTURES[ensemble].row_attempts),
            "row_attempts_sha256": core.array_sha256(
                np.asarray(
                    ROTATION_FIXTURES[ensemble].row_attempts, dtype="<u2"
                ),
                "<u2",
            ),
            "maximum_row_attempt": ROTATION_FIXTURES[ensemble].max_row_attempt,
        }
        for ensemble in fixture.ENSEMBLES
    }


def _task_grid() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = [
        {"category": "null", "world": world} for world in fixture.WORLD_IDS
    ]
    tasks.extend(
        {
            "category": "power",
            "target": target,
            "driver": driver,
            "strength": strength,
            "world": world,
        }
        for target in fixture.TARGETS
        for driver in fixture.DRIVERS
        for strength in STRENGTHS
        for world in fixture.POWER_WORLD_IDS
    )
    tasks.extend(
        {
            "category": "whole_row",
            "kind": kind,
            "target": target,
            "driver": driver,
            "world": world,
        }
        for kind in WHOLE_ROW_KINDS
        for target in fixture.TARGETS
        for driver in fixture.DRIVERS
        for world in fixture.POWER_WORLD_IDS
    )
    tasks.extend(
        {"category": "invariance", "kind": kind}
        for kind in INVARIANCE_KINDS
    )
    tasks.append({"category": "complement"})
    tasks.extend(
        {"category": "leakage", "held_folio": folio}
        for folio in fixture.FOLIO_ORDER
    )
    tasks.extend(
        {
            "category": "dependence",
            "target": target,
            "driver": driver,
            "world": world,
        }
        for target in fixture.TARGETS
        for driver in fixture.DRIVERS
        for world in fixture.POWER_WORLD_IDS
    )
    if len(tasks) != 402:
        raise CalibrationError(f"task-grid size mismatch: {len(tasks)}")
    return tasks


def _summarize_gates(
    records: Mapping[str, list[dict[str, Any]]],
    mutations: Sequence[Mapping[str, Any]],
    deterministic: bool,
) -> tuple[dict[str, Any], list[str], bool]:
    null_count = sum(int(record["union_pass"]) for record in records["null"])
    power_counts: dict[tuple[str, str, float], int] = {}
    for target in fixture.TARGETS:
        for driver in fixture.DRIVERS:
            for strength in STRENGTHS:
                power_counts[(target, driver, strength)] = sum(
                    int(record["target_complete_pass"])
                    for record in records["power"]
                    if record["target"] == target
                    and record["driver"] == driver
                    and record["strength"] == strength
                )
    gates: dict[str, Any] = {
        "null_union_pass_count": null_count,
        "null_ceiling": null_count <= 4,
        "power_pass_counts": {
            target: {
                driver: {
                    f"{strength:.2f}": power_counts[(target, driver, strength)]
                    for strength in STRENGTHS
                }
                for driver in fixture.DRIVERS
            }
            for target in fixture.TARGETS
        },
    }
    for target in fixture.TARGETS:
        threshold = 7 if target == fixture.RAY_LIKE else 6
        gates[f"power_{target}_at_075"] = all(
            power_counts[(target, driver, 0.75)] >= threshold
            for driver in fixture.DRIVERS
        )
        gates[f"power_{target}_at_100"] = all(
            power_counts[(target, driver, 1.00)] >= threshold
            for driver in fixture.DRIVERS
        )
        gates[f"monotone_{target}"] = all(
            power_counts[(target, driver, stronger)]
            >= power_counts[(target, driver, weaker)] - 1
            for driver in fixture.DRIVERS
            for weaker, stronger in zip(STRENGTHS[:-1], STRENGTHS[1:], strict=True)
        )
    gates.update(
        {
            "whole_row_controls_rejected": all(
                record["target_rejected"]
                and record["required_rejection_gate_failed"]
                for record in records["whole_row"]
            ),
            "invariance_controls_pass": all(
                record["invariance"]["passes"]
                for record in records["invariance"]
            ),
            "complement_control_pass": records["complement"][0]["decision_invariant"],
            "leakage_controls_pass": all(
                record["unchanged"] for record in records["leakage"]
            ),
            "mutation_controls_pass": (
                len(mutations) == len(MUTATION_KINDS)
                and all(record["rejected"] for record in mutations)
            ),
            "reading_dependence_reported": len(records["dependence"]) == 32,
            "deterministic_fixture_reconstruction": deterministic,
            "full_two_target_family_every_evaluation": all(
                set(record["evaluation"]["complete_dual_ensemble_pass"])
                == set(fixture.TARGETS)
                for category in ("null", "power", "whole_row", "invariance", "dependence")
                for record in records[category]
            ),
        }
    )
    boolean_gate_names = [
        key for key, value in gates.items() if isinstance(value, bool)
    ]
    failures = sorted(key for key in boolean_gate_names if not gates[key])
    return gates, failures, not failures


def _report(result: Mapping[str, Any]) -> str:
    passed = result["decision"] == "PASS_TARGET_FREE_SYNTHETIC_CALIBRATION"
    if passed:
        outcome = (
            "All frozen target-free calibration and control gates passed. "
            "This authorizes only the separately frozen next step described by the claim ceiling."
        )
    else:
        outcome = (
            "The frozen target-free calibration failed. SME003 is closed before target access. "
            f"Failed gates: {', '.join(result['failures'])}."
        )
    return (
        "# SME003 target-free synthetic calibration\n\n"
        f"Decision: **{result['decision']}**\n\n"
        f"{outcome}\n\n"
        f"Null union passes: {result['gates']['null_union_pass_count']} / 64.\n\n"
        "The run used 64 paired null worlds, 128 primary power cases, all frozen "
        "controls and sensitivities, two 8,192-assignment ensembles, and 32 workers "
        "with BLAS thread counts fixed to one.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}.\n"
    )


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    if temporary.exists():
        raise CalibrationError(f"stale temporary output exists: {temporary}")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as error:
            raise CalibrationError(f"output appeared during run: {path}") from error
        temporary.unlink()
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write_pair(outputs: Sequence[tuple[Path, bytes]]) -> None:
    """Install a small output bundle without overwriting either destination."""
    temporaries: list[tuple[Path, Path]] = []
    created: list[Path] = []
    try:
        for path, data in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
            if temporary.exists() or path.exists():
                raise CalibrationError(f"output path is not absent: {path}")
            with temporary.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            temporaries.append((path, temporary))
        if any(path.exists() for path, _temporary in temporaries):
            raise CalibrationError("an output appeared while staging the result bundle")
        for path, temporary in temporaries:
            try:
                os.link(temporary, path)
            except FileExistsError as error:
                raise CalibrationError(f"output appeared during bundle install: {path}") from error
            created.append(path)
    except Exception:
        temporary_by_path = dict(temporaries)
        for path in created:
            temporary = temporary_by_path[path]
            if path.exists() and temporary.exists() and os.path.samefile(path, temporary):
                path.unlink()
        raise
    finally:
        for _path, temporary in temporaries:
            if temporary.exists():
                temporary.unlink()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--freeze",
        type=Path,
        default=_repo_path(FREEZE_RELATIVE),
        help="separately created SME003 calibration implementation freeze",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if os.environ.get("OPENBLAS_NUM_THREADS") != "1" or os.environ.get("OMP_NUM_THREADS") != "1":
        raise CalibrationError("authorized execution requires OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1")
    freeze_path = args.freeze.resolve()
    if freeze_path != _repo_path(FREEZE_RELATIVE):
        raise CalibrationError("only the frozen repository manifest path is accepted")
    manifest, target_absence_before, result_absence_before = _verify_freeze_manifest(
        freeze_path
    )

    matrix_path = _repo_path(MATRIX_RELATIVE)
    inventory_path = _repo_path(INVENTORY_RELATIVE)
    _initialize_runtime(str(matrix_path), str(inventory_path))
    _assert_panel_binding(PANEL)
    preflight = _load_json(_repo_path(PREFLIGHT_RELATIVE))
    preflight_validation = _load_json(_repo_path(PREFLIGHT_VALIDATION_RELATIVE))
    _validate_preflight(preflight, preflight_validation)

    repeated_labels = fixture.generate_label_panel(UNITS)
    repeated_rotations = fixture.build_calibration_rotations()
    deterministic = (
        tuple(item.paired_sha256 for item in repeated_labels.worlds)
        == tuple(item.paired_sha256 for item in LABEL_PANEL.worlds)
        and all(
            repeated_rotations[ensemble].sha256
            == ROTATION_FIXTURES[ensemble].sha256
            and repeated_rotations[ensemble].row_attempts
            == ROTATION_FIXTURES[ensemble].row_attempts
            for ensemble in fixture.ENSEMBLES
        )
    )

    tasks = _task_grid()
    records: dict[str, list[dict[str, Any]]] = {
        category: []
        for category in (
            "null",
            "power",
            "whole_row",
            "invariance",
            "complement",
            "leakage",
            "dependence",
        )
    }
    with ProcessPoolExecutor(
        max_workers=32,
        initializer=_initialize_runtime,
        initargs=(str(matrix_path), str(inventory_path)),
    ) as executor:
        for category, record in executor.map(_run_task, tasks, chunksize=1):
            records[category].append(record)

    mutations = _mutation_records()
    gates, failures, passed = _summarize_gates(records, mutations, deterministic)
    target_absence_after = _check_absence(
        manifest["target_artifact_absence"], "target_artifact_absence_after"
    )
    if target_absence_after != target_absence_before:
        raise CalibrationError("target artifact absence map changed during calibration")

    frozen_files = dict(manifest["frozen_files"])
    input_hashes = {
        Path(relative).name: frozen_files[relative]
        for relative in (MATRIX_RELATIVE, INVENTORY_RELATIVE, PREFLIGHT_RELATIVE)
    }
    source_relatives = (
        f"{RELATIVE_DIR}/SME003_SYNTHETIC_CALIBRATION_SPEC.md",
        f"{RELATIVE_DIR}/SME003_CROSS_FOLIO_PREFLIGHT_SPEC.md",
        f"{RELATIVE_DIR}/sme003_core.py",
        f"{RELATIVE_DIR}/sme003_fixture.py",
        f"{RELATIVE_DIR}/run_sme003_synthetic_calibration.py",
        f"{RELATIVE_DIR}/validate_sme003_synthetic_calibration.py",
    )
    source_hashes = {
        Path(relative).name: frozen_files[relative] for relative in source_relatives
    }
    decision = (
        "PASS_TARGET_FREE_SYNTHETIC_CALIBRATION"
        if passed else "FAIL_CLOSE_SME003_BEFORE_TARGET"
    )
    result: dict[str, Any] = {
        "experiment": "SME003",
        "status": decision,
        "input_hashes": input_hashes,
        "source_hashes": source_hashes,
        "frozen_files": frozen_files,
        "freeze_status": manifest["status"],
        "authorized_command": AUTHORIZED_COMMAND,
        "workers": 32,
        "blas_threads": 1,
        "target_absence_before": target_absence_before,
        "target_absence_after": target_absence_after,
        "target_rows_accessed": False,
        "morphology_fields_accessed": False,
        "target_join_performed": False,
        "preflight_validation_status": preflight_validation["status"],
        "preflight_reconstruction": _transform_checkpoint(BASELINE_TRANSFORMS),
        "rotation_ensembles": _rotation_checkpoint(),
        "label_worlds": [_label_checkpoint(world) for world in fixture.WORLD_IDS],
        "null_worlds": records["null"],
        "power_worlds": records["power"],
        "controls": {
            "whole_row": records["whole_row"],
            "invariance": records["invariance"],
            "complement": records["complement"][0],
            "leakage": records["leakage"],
            "mutations": mutations,
            "reading_dependence": records["dependence"],
        },
        "gates": gates,
        "failures": failures,
        "decision": decision,
        "claim_ceiling": CLAIM_CEILING,
    }
    result_bytes = json.dumps(
        result, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False
    ).encode("ascii") + b"\n"
    report_bytes = _report(result).encode("utf-8")
    _check_absence(manifest["target_artifact_absence"], "target_artifact_absence_final")
    result_absence_final = _check_absence(
        manifest["result_artifact_absence"], "result_artifact_absence_final"
    )
    if result_absence_final != result_absence_before:
        raise CalibrationError("result artifact absence map changed during calibration")
    _atomic_write_pair(
        (
            (_repo_path(RESULT_RELATIVE), result_bytes),
            (_repo_path(REPORT_RELATIVE), report_bytes),
        )
    )
    print(decision)
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CalibrationError as error:
        print(f"SME003_CALIBRATION_BLOCKED: {error}", file=sys.stderr)
        raise SystemExit(2)
