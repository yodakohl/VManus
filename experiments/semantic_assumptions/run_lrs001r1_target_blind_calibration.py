#!/usr/bin/env python3
"""Run the frozen LRS001-R1 target-blind synthetic calibration.

The process imports only the standard library and NumPy before installing its
repository audit hook.  The two frozen repository modules are then compiled
from already hash-checked bytes.  No manuscript class/content artifact is an
accepted input, and worker processes inherit all scientific data through
``fork`` without opening repository files.
"""

from __future__ import annotations

import os

# The specification requires single-threaded numerical kernels inside each
# whole-world worker.  Assignment, rather than setdefault, defeats inherited
# interactive settings.
for _thread_name in (
    "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ[_thread_name] = "1"

import argparse
import csv
import dataclasses
import gc
import hashlib
import io
import json
import math
import multiprocessing as mp
import re
import shutil
import sys
import tempfile
import types
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = HERE / "results"

GEOMETRY_TSV_REL = "experiments/semantic_assumptions/results/lrs001r1_anonymous_geometry.tsv"
GEOMETRY_JSON_REL = "experiments/semantic_assumptions/results/lrs001r1_anonymous_geometry.json"
SPEC_REL = "experiments/semantic_assumptions/LRS001R1_TARGET_BLIND_CALIBRATION_SPEC.md"
CORE_REL = "experiments/semantic_assumptions/lrs001r1_core.py"
SYNTHETIC_REL = "experiments/semantic_assumptions/lrs001r1_synthetic.py"
RUNNER_REL = "experiments/semantic_assumptions/run_lrs001r1_target_blind_calibration.py"
VALIDATOR_REL = "experiments/semantic_assumptions/validate_lrs001r1_target_blind_calibration.py"
FREEZE_REL = "experiments/semantic_assumptions/LRS001R1_TARGET_BLIND_CALIBRATION_FREEZE.json"
OUT_JSON_REL = "experiments/semantic_assumptions/results/lrs001r1_target_blind_calibration.json"
OUT_REPORT_REL = "experiments/semantic_assumptions/results/lrs001r1_target_blind_calibration.md"

BOUND_RELS = (
    GEOMETRY_TSV_REL, GEOMETRY_JSON_REL, SPEC_REL, CORE_REL,
    SYNTHETIC_REL, RUNNER_REL, VALIDATOR_REL,
)
ALLOWED_INPUT_RELS = frozenset((*BOUND_RELS, FREEZE_REL))
OUTPUT_RELS = (OUT_JSON_REL, OUT_REPORT_REL)

GEOMETRY_TSV_SHA256 = "37f06364effab97140d50fd64984ee561ed84f9087866314db7fec4f059647df"
GEOMETRY_JSON_SHA256 = "0c251db4526f54a1b3bec15528f32a95c782d3a7d8f134ab49b6afb872bd1542"
ASSIGNMENT_SHA256 = "48a20b6b16f38f7cfab037cae72da8d24ff2f2f4cdcf1c6e08945ab5dc6dc7e6"
RETRY_SHA256 = "de2f256064a0af797747c2b97505dc0b9f3df0de4f489eac731c23ae9ca9cc31"
TOL = 1.0e-12

FREEZE_EXPERIMENT = "LRS001R1_TARGET_BLIND_CALIBRATION_FREEZE"
FREEZE_STATUS = "FROZEN_UNSCORED"
FREEZE_DECISION = "AUTHORIZE_TARGET_BLIND_CALIBRATION_ONLY"
RESULT_EXPERIMENT = "LRS001R1_TARGET_BLIND_CALIBRATION"
SCHEMA_VERSION = "LRS001R1_AGGREGATE_CALIBRATION_V1"

FAMILY_COUNTS = (
    ("NULL", 64),
    ("ORDER_FULL", 8),
    ("ORDER_REDUCED", 8),
    ("PAGE_TOPIC", 8),
    ("GLOBAL_FIXED_COLUMN", 8),
    ("LENGTH_BY_COLUMN", 8),
    ("CODE_DRAWING_STATE", 8),
    ("ORDERED_LENGTH_SHAPE", 8),
    ("UNORDERED_BAG_TOPIC", 8),
    ("PURE_FIRST_ORDER", 8),
    ("ONE_FOLIO", 8),
    ("ONE_CURRIER", 8),
    ("ONE_SECTION", 8),
    ("ONE_POSITION", 8),
    ("ONE_RECORD_LENGTH", 8),
    ("ONE_SURFACE", 8),
    ("EXACT_DUPLICATE_ONLY", 8),
    ("RANDOM_DONOR", 8),
    ("REVERSED_MAPPING", 8),
)
NEGATIVE_FAMILIES = frozenset(name for name, _ in FAMILY_COUNTS) - {
    "NULL", "ORDER_FULL", "ORDER_REDUCED",
}
INVARIANCE_CONTROL_NAMES = (
    "row_order_rebuild_and_numeric",
    "record_renaming_with_carried_maps",
    "class_label_permutation",
    "physical_reversal_with_carried_maps",
)
MALFORMED_CONTROL_NAMES = (
    "malformed_cell", "repeated_donor", "split_crossing_donor",
    "nonzero_sum_contrast", "donor_position_j_excluded",
    "recipient_neighbour_not_mixed", "cell_excluded_page_background",
    "undeclared_repository_read", "nonfinite_probability", "class_loss",
    "output_overwrite",
)

# Audit state exists before hook installation and is inherited read-only by
# fork workers.  Only repository paths are scientific-input constrained;
# standard-library, NumPy, IPC, and dynamic-loader paths outside ROOT remain
# available.
_AUDIT_INSTALLED = False
_AUDIT_READS: list[str] = []
_AUDIT_CREATES: list[str] = []
_AUDIT_REMOVES: list[str] = []
_AUDIT_EXPECTED_DENIALS: list[str] = []
_AUDIT_UNEXPECTED: list[str] = []
_EXPECT_DENIAL = False

_CORE = None
_SYNTHETIC = None
_GEOMETRY = None
_SYNTHETIC_GEOMETRY = None
_ASSIGNMENTS = None
_WORKER_REPOSITORY_READS_FORBIDDEN = False


def _relative_repository_path(value: object) -> str | None:
    if isinstance(value, int):
        return None
    try:
        path = Path(os.fsdecode(value))
    except (TypeError, ValueError):
        return None
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        return path.resolve(strict=False).relative_to(ROOT).as_posix()
    except ValueError:
        return None


def _open_is_write(mode: object, flags: object) -> bool:
    if isinstance(mode, str) and any(marker in mode for marker in "wax+"):
        return True
    if isinstance(flags, int):
        return bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
    return False


def _audit_hook(event: str, args: tuple[object, ...]) -> None:
    global _EXPECT_DENIAL
    if event == "open" and args:
        relative = _relative_repository_path(args[0])
        if relative is None:
            return
        if _WORKER_REPOSITORY_READS_FORBIDDEN:
            raise PermissionError(f"worker repository open denied: {relative}")
        write = _open_is_write(args[1] if len(args) > 1 else None,
                               args[2] if len(args) > 2 else None)
        if not write and relative in ALLOWED_INPUT_RELS:
            _AUDIT_READS.append(relative)
            return
        message = f"repository open denied: {relative}"
        if _EXPECT_DENIAL:
            _AUDIT_EXPECTED_DENIALS.append(relative)
        else:
            _AUDIT_UNEXPECTED.append(message)
        raise PermissionError(message)
    if event == "os.link" and len(args) >= 2:
        destination = _relative_repository_path(args[1])
        source = _relative_repository_path(args[0])
        if destination in OUTPUT_RELS and source is None:
            _AUDIT_CREATES.append(str(destination))
            return
        if destination is not None or source is not None:
            message = f"repository hard-link denied: {source}->{destination}"
            _AUDIT_UNEXPECTED.append(message)
            raise PermissionError(message)
    if event in {"os.remove", "os.unlink"} and args:
        relative = _relative_repository_path(args[0])
        if relative is None:
            return
        if relative in OUTPUT_RELS and relative in _AUDIT_CREATES:
            _AUDIT_REMOVES.append(relative)
            return
        message = f"repository removal denied: {relative}"
        _AUDIT_UNEXPECTED.append(message)
        raise PermissionError(message)
    if event in {"os.rename", "os.replace"} and len(args) >= 2:
        source = _relative_repository_path(args[0])
        destination = _relative_repository_path(args[1])
        if source is not None or destination is not None:
            message = f"repository rename denied: {source}->{destination}"
            _AUDIT_UNEXPECTED.append(message)
            raise PermissionError(message)


def _install_audit_hook() -> None:
    global _AUDIT_INSTALLED
    if _AUDIT_INSTALLED:
        raise RuntimeError("audit hook already installed")
    sys.addaudithook(_audit_hook)
    _AUDIT_INSTALLED = True


def _worker_initializer() -> None:
    global _WORKER_REPOSITORY_READS_FORBIDDEN
    _WORKER_REPOSITORY_READS_FORBIDDEN = True


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def _read_bound(relative: str) -> bytes:
    if relative not in ALLOWED_INPUT_RELS:
        raise ValueError(f"path outside frozen allowlist: {relative}")
    return (ROOT / relative).read_bytes()


def _load_repository_module(name: str, relative: str, payload: bytes) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    module.__package__ = ""
    module.__spec__ = None
    sys.modules[name] = module
    try:
        code = compile(payload, str(ROOT / relative), "exec", dont_inherit=True)
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def _validate_freeze(payload: bytes, expected_sha256: str) -> tuple[dict[str, object], dict[str, bytes]]:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("--freeze-sha256 must be 64 lowercase hexadecimal characters")
    if _sha256(payload) != expected_sha256:
        raise RuntimeError("freeze SHA-256 mismatch before parse")
    freeze = json.loads(payload)
    if freeze.get("experiment") != FREEZE_EXPERIMENT:
        raise RuntimeError("freeze experiment mismatch")
    if freeze.get("status") != FREEZE_STATUS:
        raise RuntimeError("freeze status mismatch")
    if freeze.get("decision") != FREEZE_DECISION:
        raise RuntimeError("freeze decision mismatch")
    if not re.fullmatch(r"[0-9a-f]{40}", str(freeze.get("registration_commit", ""))):
        raise RuntimeError("freeze registration_commit is not a full lowercase commit hash")
    bound = freeze.get("bound_files")
    if not isinstance(bound, dict) or set(bound) != set(BOUND_RELS) or len(bound) != 7:
        raise RuntimeError("freeze bound_files must contain exactly seven registered paths")
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
           for value in bound.values()):
        raise RuntimeError("freeze contains a malformed bound SHA-256")
    outputs = freeze.get("outputs_absent")
    if not isinstance(outputs, list) or len(outputs) != 2 or set(outputs) != set(OUTPUT_RELS):
        raise RuntimeError("freeze outputs_absent mismatch")
    if bound[GEOMETRY_TSV_REL] != GEOMETRY_TSV_SHA256 or \
            bound[GEOMETRY_JSON_REL] != GEOMETRY_JSON_SHA256:
        raise RuntimeError("freeze geometry hash drift")

    loaded: dict[str, bytes] = {}
    for relative in BOUND_RELS:
        payload_for_file = _read_bound(relative)
        if _sha256(payload_for_file) != bound[relative]:
            raise RuntimeError(f"bound file SHA-256 mismatch: {relative}")
        loaded[relative] = payload_for_file
    return freeze, loaded


def _outputs_absent() -> bool:
    return all(not (ROOT / relative).exists() for relative in OUTPUT_RELS)


def _load_geometry(core: types.ModuleType, synthetic: types.ModuleType,
                   loaded: Mapping[str, bytes]):
    manifest = json.loads(loaded[GEOMETRY_JSON_REL])
    if manifest.get("status") != "PASS_LABEL_FREE_PSEUDONYMOUS_GEOMETRY" or \
            manifest.get("decision") != "GO_TARGET_BLIND_SYNTHETIC_CALIBRATION_ONLY":
        raise RuntimeError("geometry manifest authorization drift")
    if tuple(manifest.get("schema", ())) != core.GEOMETRY_FIELDS:
        raise RuntimeError("geometry manifest schema drift")
    if manifest.get("tsv_sha256") != GEOMETRY_TSV_SHA256:
        raise RuntimeError("geometry manifest TSV binding drift")
    layout = {int(key): int(value) for key, value in
              dict(manifest.get("opaque_class_count_by_symbol_count", {})).items()}
    if layout != core.CLASS_LAYOUT:
        raise RuntimeError("geometry opaque class layout drift")
    isolation = manifest.get("isolation", {})
    if any(bool(isolation.get(key)) for key in (
        "real_class_identity_or_family_surface_emitted",
        "real_context_target_association_scored", "predictor_fitted",
        "ocr_or_automated_vision_used",
    )):
        raise RuntimeError("geometry isolation drift")
    text = loaded[GEOMETRY_TSV_REL].decode("utf-8")
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter="\t")
    if tuple(reader.fieldnames or ()) != core.GEOMETRY_FIELDS:
        raise RuntimeError("geometry TSV schema drift")
    rows = [dict(row) for row in reader]
    geometry = core.geometry_from_rows(rows, strict_registered_counts=True)
    synthetic_geometry = synthetic.geometry_from_rows(rows)
    if tuple(row.anonymous_group_id for row in geometry.rows) != synthetic_geometry.row_ids:
        raise RuntimeError("core/synthetic geometry canonicalization mismatch")
    return rows, geometry, synthetic_geometry


def _little_i8_digest(array: np.ndarray) -> str:
    value = np.ascontiguousarray(np.asarray(array, dtype="<i8"))
    return _sha256(value.tobytes(order="C"))


def _little_i2_digest(array: np.ndarray) -> str:
    value = np.ascontiguousarray(np.asarray(array, dtype="<i2"))
    return _sha256(value.tobytes(order="C"))


def _little_f8_digest(array: np.ndarray) -> str:
    value = np.ascontiguousarray(np.asarray(array, dtype="<f8"))
    if not np.all(np.isfinite(value)):
        raise ValueError("refusing to hash a nonfinite aggregate array")
    return _sha256(value.tobytes(order="C"))


def _synthetic_digests(synthetic_data) -> dict[str, str]:
    return {
        "prototype_indices_sha256": _little_i2_digest(synthetic_data.prototype_indices),
        "class_indices_sha256": _little_i2_digest(synthetic_data.class_indices),
        "target_separation_sha256": _sha256(
            np.ascontiguousarray(np.asarray(synthetic_data.target_separation,
                                            dtype=np.uint8)).tobytes(order="C")),
        "record_nonces_sha256": _little_i8_digest(np.asarray(synthetic_data.record_nonces)),
        "copied_record_ids_sha256": _sha256(_canonical_json(
            sorted(synthetic_data.copied_record_ids,
                   key=lambda value: value.encode("utf-8")))),
    }


def _assignment_panel(geometry) -> dict[str, tuple[int, ...]]:
    cells: dict[str, list[int]] = defaultdict(list)
    for record_index, record in enumerate(geometry.records):
        exemplar = geometry.rows[record.row_indices[0]]
        if record.split == "TEST" and exemplar.strict_test_movable:
            cells[record.cell_id].append(record_index)
    return {cell: tuple(sorted(values, key=lambda index:
                               geometry.records[index].record_id.encode("utf-8")))
            for cell, values in cells.items()}


def _validate_assignments(core, geometry, assignments, *, frozen_digest: bool) -> None:
    cells = _assignment_panel(geometry)
    expected_records = sorted((index for values in cells.values() for index in values),
                              key=lambda index: geometry.records[index].record_id.encode("utf-8"))
    if len(expected_records) != 453:
        raise ValueError("whole-donor panel is not exactly 453 records")
    if assignments.record_indices.shape != (453,) or \
            assignments.maps.shape != (core.N_ASSIGNMENTS, 453) or \
            assignments.retries.shape != (core.N_ASSIGNMENTS,):
        raise ValueError("assignment array shape mismatch")
    if assignments.record_indices.tolist() != expected_records:
        raise ValueError("assignment record panel mismatch")
    if not np.array_equal(assignments.maps[0], assignments.record_indices):
        raise ValueError("assignment identity row mismatch")
    if assignments.retries[0] != 0 or np.any(assignments.retries < 0) or \
            np.any(assignments.retries >= 10000):
        raise ValueError("assignment retry vector mismatch")
    for cell, recipients in cells.items():
        del cell
        columns = np.asarray([assignments.record_column[index] for index in recipients],
                             dtype=np.int64)
        observed = np.sort(assignments.maps[:, columns], axis=1)
        expected = np.sort(np.asarray(recipients, dtype=np.int64))
        if not np.all(observed == expected[None, :]):
            raise ValueError("assignment contains repeated or split/cell-crossing donor")
    if len({row.tobytes() for row in np.ascontiguousarray(assignments.maps)}) != core.N_ASSIGNMENTS:
        raise ValueError("assignment global map repetition")
    if frozen_digest:
        if _little_i8_digest(assignments.maps) != ASSIGNMENT_SHA256:
            raise ValueError("assignment map frozen digest mismatch")
        if _little_i8_digest(assignments.retries) != RETRY_SHA256 or \
                int(assignments.retries.max()) != 0:
            raise ValueError("assignment retry frozen digest mismatch")


def _finite(value: float) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("nonfinite aggregate output")
    return result


def _candidate_grid_payload(candidates: Sequence[object]) -> list[dict[str, object]]:
    fields = (
        "order_rank", "ridge", "nuisance_score", "bag_score", "order_score",
        "order_minus_bag", "order_minus_nuisance", "floor_rate_nuisance",
        "floor_rate_bag", "floor_rate_order",
    )
    output = []
    for candidate in candidates:
        row = {}
        for field in fields:
            value = getattr(candidate, field)
            row[field] = int(value) if field == "order_rank" else _finite(value)
        output.append(row)
    return output


def _calibrate_with_trace(core, feature_data):
    """Core-equivalent CAL selection that retains the eight-row trace digest."""
    cal_indices = feature_data.event_indices_by_split["CAL"]
    cal_events = [feature_data.events[int(index)] for index in cal_indices]
    candidates = []
    train_models = {}
    for ridge in core.RIDGES:
        for design in ("NUIS", "BAG", "ORDER1", "ORDER2"):
            train_models[(design, ridge)] = core.fit_lda_model(
                feature_data, ("TRAIN",), design, ridge)
        scores = {}
        floors = {}
        for design in ("NUIS", "BAG", "ORDER1", "ORDER2"):
            scores[design], floors[design] = core._score_self(
                feature_data, train_models[(design, ridge)], "CAL")
        for rank in core.ORDER_RANKS:
            order_name = f"ORDER{rank}"
            nuisance_score = core.hierarchy_mean(scores["NUIS"], cal_events)
            bag_score = core.hierarchy_mean(scores["BAG"], cal_events)
            order_score = core.hierarchy_mean(scores[order_name], cal_events)
            candidates.append(core.CalibrationCandidate(
                order_rank=rank, ridge=ridge, nuisance_score=nuisance_score,
                bag_score=bag_score, order_score=order_score,
                order_minus_bag=order_score - bag_score,
                order_minus_nuisance=order_score - nuisance_score,
                floor_rate_nuisance=float(floors["NUIS"].mean()),
                floor_rate_bag=float(floors["BAG"].mean()),
                floor_rate_order=float(floors[order_name].mean()),
            ))

    def better(left, right) -> bool:
        for a, b in (
            (min(left.order_minus_bag, left.order_minus_nuisance),
             min(right.order_minus_bag, right.order_minus_nuisance)),
            (left.order_score, right.order_score),
        ):
            if a > b + TOL:
                return True
            if b > a + TOL:
                return False
        if left.order_rank != right.order_rank:
            return left.order_rank < right.order_rank
        return left.ridge > right.ridge + TOL

    selected = candidates[0]
    for candidate in candidates[1:]:
        if better(candidate, selected):
            selected = candidate
    grid_digest = _sha256(_canonical_json(_candidate_grid_payload(candidates)))
    values = (
        selected.order_minus_bag, selected.order_minus_nuisance,
        selected.nuisance_score, selected.bag_score, selected.order_score,
    )
    if not all(math.isfinite(value) for value in values):
        return None, "CAL_STOP_NONFINITE", tuple(candidates), grid_digest
    if selected.order_minus_bag <= 0 or selected.order_minus_nuisance <= 0:
        return None, "CAL_STOP_NONPOSITIVE_GAIN", tuple(candidates), grid_digest
    if max(selected.floor_rate_nuisance, selected.floor_rate_bag,
           selected.floor_rate_order) > 0.05 + TOL:
        return None, "CAL_STOP_FLOOR_DOMINATED", tuple(candidates), grid_digest
    final = {}
    for output_name, design in (
        ("NUIS", "NUIS"), ("BAG", "BAG"),
        ("ORDER", f"ORDER{selected.order_rank}"),
    ):
        train_model = train_models[(design, selected.ridge)]
        standardizers = {length: head.standardizer
                         for length, head in train_model.heads.items()}
        final[output_name] = core.fit_lda_model(
            feature_data, ("TRAIN", "CAL"), design, selected.ridge,
            frozen_standardizers=standardizers)
    models = core.CalibratedModels(selected, tuple(candidates), final["NUIS"],
                                   final["BAG"], final["ORDER"])
    return models, None, tuple(candidates), grid_digest


def _public_world_stop(world_spec, reason: str, synthetic_digests: Mapping[str, str],
                       candidate_grid_sha256: str) -> dict[str, object]:
    return {
        "ordinal": int(world_spec.ordinal), "family": world_spec.family,
        "world": int(world_spec.index), "calibration_status": reason,
        "selected": None, "channels": None, "gate_pass_count": 0,
        "gate_count": 0, "gates": {}, "passes": False,
        "digests": {**dict(synthetic_digests),
                    "candidate_grid_sha256": candidate_grid_sha256,
                    "order_bag_effects_sha256": None,
                    "order_nuisance_effects_sha256": None},
    }


def _evaluate_core_world(core, geometry, world, assignments):
    features = core.build_feature_data(geometry, world)
    models, stop, candidates, grid_digest = _calibrate_with_trace(core, features)
    if models is None:
        return None, stop, grid_digest
    pairs = core.score_test_pairs(features, models)
    evaluation = core.evaluate_assignments(features, pairs, assignments)
    signatures = core.synthetic_record_signatures(geometry, world)
    gates = core.evaluate_passes_from_assignment(
        features, models, evaluation, pairs,
        duplicate_record_signatures=signatures,
    )
    return {
        "features": features, "models": models, "pairs": pairs,
        "evaluation": evaluation, "gates": gates, "signatures": signatures,
        "candidate_grid": candidates, "candidate_grid_sha256": grid_digest,
    }, None, grid_digest


def _public_world(world_spec, internal, stop: str | None,
                  synthetic_digests: Mapping[str, str],
                  candidate_grid_sha256: str) -> dict[str, object]:
    if internal is None:
        return _public_world_stop(world_spec, str(stop), synthetic_digests,
                                  candidate_grid_sha256)
    selected = internal["models"].selected
    maximum = internal["evaluation"].max_t
    channels = {}
    for key, value in (
        ("ORDER_BAG", maximum.order_minus_bag),
        ("ORDER_NUIS", maximum.order_minus_nuisance),
    ):
        channels[key] = {
            "effect": _finite(value.observed), "null_mean": _finite(value.null_mean),
            "null_sd": _finite(value.null_sd), "z": _finite(value.z),
            "maxT_p": _finite(value.max_t_p),
        }
    checks = internal["gates"].checks
    return {
        "ordinal": int(world_spec.ordinal), "family": world_spec.family,
        "world": int(world_spec.index), "calibration_status": "PASS_CAL",
        "selected": {
            "order_rank": int(selected.order_rank), "ridge": _finite(selected.ridge),
            "order_minus_bag": _finite(selected.order_minus_bag),
            "order_minus_nuisance": _finite(selected.order_minus_nuisance),
            "order_score": _finite(selected.order_score),
            "floor_rate_nuisance": _finite(selected.floor_rate_nuisance),
            "floor_rate_bag": _finite(selected.floor_rate_bag),
            "floor_rate_order": _finite(selected.floor_rate_order),
        },
        "channels": channels,
        "gate_pass_count": int(sum(bool(value) for value in checks.values())),
        "gate_count": int(len(checks)),
        "gates": {key: bool(value) for key, value in sorted(checks.items())},
        "passes": bool(internal["gates"].passed),
        "digests": {
            **dict(synthetic_digests),
            "candidate_grid_sha256": candidate_grid_sha256,
            "order_bag_effects_sha256": _little_f8_digest(
                maximum.order_minus_bag.effects),
            "order_nuisance_effects_sha256": _little_f8_digest(
                maximum.order_minus_nuisance.effects),
        },
    }


def _run_world(world_spec):
    synthetic_data = _SYNTHETIC.generate_world(_SYNTHETIC_GEOMETRY, world_spec)
    digests = _synthetic_digests(synthetic_data)
    world = _CORE.make_world_from_synthetic(_GEOMETRY, synthetic_data)
    internal, stop, candidate_digest = _evaluate_core_world(
        _CORE, _GEOMETRY, world, _ASSIGNMENTS)
    return _public_world(world_spec, internal, stop, digests, candidate_digest)


def _run_world_with_internal(world_spec):
    synthetic_data = _SYNTHETIC.generate_world(_SYNTHETIC_GEOMETRY, world_spec)
    digests = _synthetic_digests(synthetic_data)
    world = _CORE.make_world_from_synthetic(_GEOMETRY, synthetic_data)
    internal, stop, candidate_digest = _evaluate_core_world(
        _CORE, _GEOMETRY, world, _ASSIGNMENTS)
    return (_public_world(world_spec, internal, stop, digests, candidate_digest),
            internal, world)


def _worker_count(requested: int) -> int:
    if not 1 <= requested <= 32:
        raise ValueError("workers must be in 1..32")
    # Each world materializes several high-dimensional float64 designs.  Keep
    # enough headroom to avoid swapping while still exploiting up to 32 cores.
    memory_limit = 32
    try:
        with open("/proc/meminfo", encoding="ascii") as handle:
            available_kib = next(int(line.split()[1]) for line in handle
                                 if line.startswith("MemAvailable:"))
        memory_limit = max(1, available_kib // (2 * 1024 * 1024))
    except (OSError, StopIteration, ValueError):
        pass
    return max(1, min(requested, 32, os.cpu_count() or 1, memory_limit))


def _conjugated_world(base_geometry, new_geometry, base_world, *, class_shift: bool = False):
    by_group = {
        row.anonymous_group_id: (int(base_world.prototype_index[index]),
                                 int(base_world.target_class[index]))
        for index, row in enumerate(base_geometry.rows)
    }
    prototypes = []
    classes = []
    for row in new_geometry.rows:
        prototype, target = by_group[row.anonymous_group_id]
        if class_shift and target >= 0:
            target = (target + 1) % _CORE.CLASS_LAYOUT[row.symbol_count]
        prototypes.append(prototype)
        classes.append(target)
    return _CORE.make_world(
        new_geometry, prototypes, classes, family=base_world.family,
        allow_target_prototype_separation=class_shift or
        base_world.family in _CORE.SEPARATION_FAMILIES,
    )


def _carried_assignments(base_geometry, new_geometry, assignments,
                         record_name_map: Mapping[str, str]):
    conversion = np.full(len(base_geometry.records), -1, dtype=np.int64)
    for old_index, record in enumerate(base_geometry.records):
        conversion[old_index] = new_geometry.record_index[record_name_map[record.record_id]]
    new_records = conversion[assignments.record_indices]
    order = np.argsort([new_geometry.records[int(index)].record_id.encode("utf-8")
                        for index in new_records])
    new_records = new_records[order]
    record_column = {int(record): column for column, record in enumerate(new_records)}
    maps = np.empty_like(assignments.maps)
    for old_column, old_recipient in enumerate(assignments.record_indices):
        new_recipient = int(conversion[int(old_recipient)])
        new_column = record_column[new_recipient]
        maps[:, new_column] = conversion[assignments.maps[:, old_column]]
    carried = _CORE.AssignmentMaps(new_records, maps, record_column,
                                    assignments.retries.copy())
    _validate_assignments(_CORE, new_geometry, carried, frozen_digest=False)
    return carried


def _numeric_invariance(base, transformed) -> bool:
    left_model = base["models"].selected
    right_model = transformed["models"].selected
    if left_model.order_rank != right_model.order_rank or \
            abs(left_model.ridge - right_model.ridge) > TOL:
        return False
    for field in (
        "nuisance_score", "bag_score", "order_score", "order_minus_bag",
        "order_minus_nuisance", "floor_rate_nuisance", "floor_rate_bag",
        "floor_rate_order",
    ):
        if abs(float(getattr(left_model, field)) - float(getattr(right_model, field))) > 1e-10:
            return False
    for name in ("order_minus_bag", "order_minus_nuisance"):
        left = getattr(base["evaluation"].max_t, name)
        right = getattr(transformed["evaluation"].max_t, name)
        if not np.allclose(left.effects, right.effects, rtol=0.0, atol=1e-10):
            return False
        for field in ("observed", "null_mean", "null_sd", "z", "max_t_p"):
            if abs(float(getattr(left, field)) - float(getattr(right, field))) > 1e-10:
                return False
    return (base["gates"].passed == transformed["gates"].passed and
            dict(base["gates"].checks) == dict(transformed["gates"].checks))


def _byte_exact_numeric_invariance(base, transformed) -> bool:
    left_selected = base["models"].selected
    right_selected = transformed["models"].selected
    if _canonical_json(_candidate_grid_payload(base["candidate_grid"])) != \
            _canonical_json(_candidate_grid_payload(transformed["candidate_grid"])):
        return False
    if left_selected != right_selected:
        return False
    for name in ("order_minus_bag", "order_minus_nuisance"):
        left = getattr(base["evaluation"].max_t, name)
        right = getattr(transformed["evaluation"].max_t, name)
        if not np.array_equal(left.effects, right.effects):
            return False
        if any(getattr(left, field) != getattr(right, field) for field in
               ("observed", "null_mean", "null_sd", "z", "max_t_p")):
            return False
    return (
        base["gates"].passed == transformed["gates"].passed
        and dict(base["gates"].checks) == dict(transformed["gates"].checks)
    )


def _row_order_control(rows, base_geometry, base_synthetic_geometry,
                       base_world, base_internal) -> bool:
    reversed_rows = list(reversed(sorted(
        (dict(row) for row in rows),
        key=lambda row: row["anonymous_group_id"].encode("utf-8"),
    )))
    geometry = _CORE.geometry_from_rows(reversed_rows, strict_registered_counts=True)
    synthetic_geometry = _SYNTHETIC.geometry_from_rows(reversed_rows)
    if geometry.rows != base_geometry.rows or geometry.records != base_geometry.records or \
            synthetic_geometry.rows != base_synthetic_geometry.rows or \
            synthetic_geometry.records != base_synthetic_geometry.records:
        return False
    world = _conjugated_world(base_geometry, geometry, base_world)
    if not np.array_equal(world.prototype_index, base_world.prototype_index) or \
            not np.array_equal(world.target_class, base_world.target_class):
        return False
    transformed, stop, _ = _evaluate_core_world(_CORE, geometry, world, _ASSIGNMENTS)
    if transformed is None:
        raise RuntimeError(f"row-order control stopped: {stop}")
    result = _byte_exact_numeric_invariance(base_internal, transformed)
    del transformed
    gc.collect()
    return result


def _record_renaming_control(rows, base_geometry, base_world, base_internal):
    identifiers = sorted((record.record_id for record in base_geometry.records),
                         key=lambda value: value.encode("utf-8"))
    rename = {value: identifiers[-1 - index] for index, value in enumerate(identifiers)}
    changed = [dict(row, anonymous_record_id=rename[row["anonymous_record_id"]])
               for row in rows]
    geometry = _CORE.geometry_from_rows(changed, strict_registered_counts=True)
    world = _conjugated_world(base_geometry, geometry, base_world)
    assignments = _carried_assignments(base_geometry, geometry, _ASSIGNMENTS, rename)
    transformed, stop, _ = _evaluate_core_world(_CORE, geometry, world, assignments)
    if transformed is None:
        raise RuntimeError(f"record-renaming control stopped: {stop}")
    result = _numeric_invariance(base_internal, transformed)
    del transformed
    gc.collect()
    return result


def _class_permutation_control(base_geometry, base_world, base_internal):
    world = _conjugated_world(base_geometry, base_geometry, base_world, class_shift=True)
    transformed, stop, _ = _evaluate_core_world(_CORE, base_geometry, world, _ASSIGNMENTS)
    if transformed is None:
        raise RuntimeError(f"class-permutation control stopped: {stop}")
    result = _numeric_invariance(base_internal, transformed)
    del transformed
    gc.collect()
    return result


def _physical_reversal_control(rows, base_geometry, base_world, base_internal):
    changed = []
    for row in rows:
        replacement = dict(row)
        replacement["segment_group_index"] = str(
            int(row["segment_group_count"]) + 1 - int(row["segment_group_index"])
        )
        changed.append(replacement)
    geometry = _CORE.geometry_from_rows(changed, strict_registered_counts=True)
    if tuple(record.record_id for record in geometry.records) != \
            tuple(record.record_id for record in base_geometry.records):
        raise RuntimeError("physical reversal changed record identity")
    world = _conjugated_world(base_geometry, geometry, base_world)
    transformed, stop, _ = _evaluate_core_world(_CORE, geometry, world, _ASSIGNMENTS)
    if transformed is None:
        raise RuntimeError(f"physical-reversal control stopped: {stop}")
    result = _numeric_invariance(base_internal, transformed)
    del transformed
    gc.collect()
    return result


def _expect_rejection(callable_value) -> bool:
    try:
        callable_value()
    except (ValueError, RuntimeError, FloatingPointError, PermissionError,
            FileExistsError):
        return True
    return False


def _validate_contrast_pair(first: np.ndarray, second: np.ndarray) -> None:
    accepted: list[np.ndarray] = []
    for value in (first, second):
        vector = np.asarray(value, dtype=np.float64)
        if vector.ndim != 1 or not np.all(np.isfinite(vector)):
            raise ValueError("malformed DCT contrast")
        norm = float(np.linalg.norm(vector))
        if norm <= TOL:
            if np.any(vector != 0.0):
                raise ValueError("unavailable DCT contrast is not exactly zero")
            continue
        if abs(float(vector.sum())) > TOL or abs(norm - 1.0) > TOL:
            raise ValueError("DCT contrast centering/norm failure")
        if any(abs(float(vector @ prior)) > TOL for prior in accepted):
            raise ValueError("DCT contrast orthogonality failure")
        accepted.append(vector)


def _validate_all_contrasts() -> None:
    for length in range(5, 13):
        for ordinal in range(1, length + 1):
            _validate_contrast_pair(*_CORE.dct_contrasts(length, ordinal))


def _mutated_block_control(base_internal, base_world, event_index: int,
                           donor_record: int, mutated_row: int) -> bool:
    features = base_internal["features"]
    event = features.events[event_index]
    baseline_pair = features.test_pair_lookup[(event_index, donor_record)]
    prototypes = base_world.prototype_index.copy()
    prototypes[mutated_row] = (int(prototypes[mutated_row]) + 1) % 24
    changed_world = _CORE.make_world(
        _GEOMETRY, prototypes, base_world.target_class, family="ONE_POSITION",
        allow_target_prototype_separation=True,
    )
    blocks = _CORE._world_blocks(_GEOMETRY, changed_world)
    backgrounds = _CORE._page_backgrounds(_GEOMETRY, blocks)
    changed = _CORE._compose_features(
        _GEOMETRY, blocks, backgrounds, features.schema, event, donor_record,
    )
    names = ("NUIS", "BAG", "ORDER1", "ORDER2")
    return all(np.array_equal(features.test_features[name][baseline_pair], vector)
               for name, vector in zip(names, changed))


def _undeclared_read_denied() -> bool:
    global _EXPECT_DENIAL
    _EXPECT_DENIAL = True
    try:
        return _expect_rejection(lambda: (ROOT / "VOYNICH_ACTIVE_STATE.md").read_bytes())
    finally:
        _EXPECT_DENIAL = False


def _malformed_controls(rows, base_world, base_internal) -> dict[str, bool]:
    controls: dict[str, bool] = {}

    bad_rows = [dict(row) for row in rows]
    bad_index = next(index for index, row in enumerate(bad_rows)
                     if row["split"] == "TEST" and row["strict_test_movable"] == "1")
    bad_rows[bad_index]["strict_cell_id"] = "C00000000000000000000"
    controls["malformed_cell"] = _expect_rejection(
        lambda: _CORE.geometry_from_rows(bad_rows, strict_registered_counts=True))

    repeated_maps = _ASSIGNMENTS.maps.copy()
    repeated_cell = next(
        members for _, members in sorted(_assignment_panel(_GEOMETRY).items())
        if len(members) >= 2
    )
    first_column = _ASSIGNMENTS.record_column[repeated_cell[0]]
    second_column = _ASSIGNMENTS.record_column[repeated_cell[1]]
    repeated_maps[1, second_column] = repeated_maps[1, first_column]
    repeated = _CORE.AssignmentMaps(_ASSIGNMENTS.record_indices.copy(), repeated_maps,
                                    dict(_ASSIGNMENTS.record_column),
                                    _ASSIGNMENTS.retries.copy())
    controls["repeated_donor"] = _expect_rejection(
        lambda: _validate_assignments(_CORE, _GEOMETRY, repeated, frozen_digest=False))

    crossing_maps = _ASSIGNMENTS.maps.copy()
    train_record = next(index for index, record in enumerate(_GEOMETRY.records)
                        if record.split == "TRAIN")
    crossing_maps[1, 0] = train_record
    crossing = _CORE.AssignmentMaps(_ASSIGNMENTS.record_indices.copy(), crossing_maps,
                                    dict(_ASSIGNMENTS.record_column),
                                    _ASSIGNMENTS.retries.copy())
    controls["split_crossing_donor"] = _expect_rejection(
        lambda: _validate_assignments(_CORE, _GEOMETRY, crossing, frozen_digest=False))

    def bad_contrast() -> None:
        first, second = _CORE.dct_contrasts(8, 4)
        distant = np.flatnonzero(first != 0.0)
        if len(distant) == 0:
            raise RuntimeError("control fixture lacks a contrast")
        changed = first.copy()
        changed[distant[0]] += 0.125
        _validate_contrast_pair(changed, second)

    controls["nonzero_sum_contrast"] = _expect_rejection(bad_contrast)

    features = base_internal["features"]
    event_index = int(features.event_indices_by_split["TEST"][0])
    event = features.events[event_index]
    recipient = _GEOMETRY.records[event.record_index]
    controls["donor_position_j_excluded"] = _mutated_block_control(
        base_internal, base_world, event_index, event.record_index,
        recipient.row_indices[event.target_ordinal - 1],
    )

    alternate = next(value for value in features.donor_records_by_cell[event.cell_id]
                     if value != event.record_index)
    neighbour_position = event.target_ordinal - 2
    if neighbour_position < 0:
        neighbour_position = event.target_ordinal
    controls["recipient_neighbour_not_mixed"] = _mutated_block_control(
        base_internal, base_world, event_index, alternate,
        recipient.row_indices[neighbour_position],
    )
    other_record = _GEOMETRY.records[alternate]
    controls["cell_excluded_page_background"] = _mutated_block_control(
        base_internal, base_world, event_index, event.record_index,
        other_record.row_indices[0],
    )

    controls["undeclared_repository_read"] = _undeclared_read_denied()

    models = base_internal["models"]
    pair_index = features.test_pair_lookup[(event_index, event.record_index)]
    order_name = f"ORDER{models.selected.order_rank}"
    bad_matrix = features.test_features[order_name][pair_index:pair_index + 1].copy()
    bad_matrix[0, 0] = np.nan
    controls["nonfinite_probability"] = _expect_rejection(
        lambda: models.order.heads[event.target_length].predict_log_proba(bad_matrix))

    changed_events = []
    missing_length = 1
    missing_class = _CORE.CLASS_LAYOUT[missing_length] - 1
    for value in features.events:
        target_class = value.target_class
        if value.target_length == missing_length and target_class == missing_class:
            target_class = 0
        changed_events.append(dataclasses.replace(value, target_class=target_class))
    class_loss_features = dataclasses.replace(features, events=tuple(changed_events))
    controls["class_loss"] = _expect_rejection(
        lambda: _CORE.fit_lda_model(class_loss_features, ("TRAIN",), "NUIS", 0.25))

    test_directory = Path(tempfile.mkdtemp(prefix="lrs001r1-no-clobber-"))
    try:
        source = test_directory / "source"
        destination = test_directory / "destination"
        source.write_bytes(b"new")
        destination.write_bytes(b"old")
        controls["output_overwrite"] = _expect_rejection(
            lambda: os.link(source, destination))
    finally:
        shutil.rmtree(test_directory)
    return controls


def _family_summaries(records: Sequence[Mapping[str, object]]) -> dict[str, object]:
    output = {}
    for family, count in FAMILY_COUNTS:
        selected = [row for row in records if row["family"] == family]
        if len(selected) != count:
            raise RuntimeError(f"world count drift for {family}")
        hyperparameters = Counter(
            (row["selected"]["order_rank"], row["selected"]["ridge"])
            for row in selected if row["selected"] is not None
        )
        output[family] = {
            "worlds": count,
            "passes": sum(bool(row["passes"]) for row in selected),
            "calibration_stops": sum(row["calibration_status"] != "PASS_CAL"
                                     for row in selected),
            "selected_hyperparameters": {
                f"q{int(key[0])}_lambda{float(key[1]):g}": value
                for key, value in sorted(hyperparameters.items())
            },
        }
    return output


def _report(result: Mapping[str, object]) -> bytes:
    lines = [
        "# LRS001-R1 target-blind calibration", "",
        f"Status: **{result['status']}**.", "",
        "| family | passes | worlds | CAL stops |", "|---|---:|---:|---:|",
    ]
    for family, _ in FAMILY_COUNTS:
        summary = result["families"][family]
        lines.append(f"| {family} | {summary['passes']} | {summary['worlds']} | "
                     f"{summary['calibration_stops']} |")
    lines.extend([
        "", f"Decision: **{result['decision']}**.", "",
        "This is target-free synthetic instrument calibration. No real class identity, "
        "context-target association, word, language, meaning, plaintext, or translation "
        "was accessed or inferred.", "",
    ])
    return "\n".join(lines).encode("utf-8")


def _audit_ready_for_install() -> bool:
    return (
        not _AUDIT_UNEXPECTED and
        set(_AUDIT_READS) == ALLOWED_INPUT_RELS and
        set(_AUDIT_CREATES) == set() and
        set(_AUDIT_REMOVES) == set() and
        _AUDIT_EXPECTED_DENIALS == ["VOYNICH_ACTIVE_STATE.md"] and
        _outputs_absent()
    )


def _install_outputs(json_payload: bytes, report_payload: bytes) -> None:
    if not _audit_ready_for_install():
        raise RuntimeError("audit/output-absence guard failed before installation")
    staging = Path(tempfile.mkdtemp(prefix="lrs001r1-stage-", dir=ROOT.parent))
    installed: list[Path] = []
    try:
        staged_json = staging / "calibration.json"
        staged_report = staging / "calibration.md"
        for path, payload in ((staged_json, json_payload), (staged_report, report_payload)):
            with path.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        if not _audit_ready_for_install():
            raise RuntimeError("audit/output-absence drift after staging")
        for staged, relative in ((staged_json, OUT_JSON_REL),
                                 (staged_report, OUT_REPORT_REL)):
            destination = ROOT / relative
            os.link(staged, destination)
            installed.append(destination)
        if _AUDIT_CREATES != list(OUTPUT_RELS) or _AUDIT_REMOVES:
            raise RuntimeError("repository create audit mismatch after installation")
    except BaseException:
        for path in reversed(installed):
            path.unlink()
        raise
    finally:
        shutil.rmtree(staging)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-sha256", required=True,
                        help="published SHA-256 of the frozen registration JSON")
    parser.add_argument("--workers", type=int, default=32,
                        help="whole-world fork workers, 1..32 (memory-clamped)")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    global _CORE, _SYNTHETIC, _GEOMETRY, _SYNTHETIC_GEOMETRY, _ASSIGNMENTS
    arguments = _parse_args(argv)
    if not _outputs_absent():
        raise RuntimeError("calibration output already exists")

    _install_audit_hook()
    freeze_payload = _read_bound(FREEZE_REL)
    freeze, loaded = _validate_freeze(freeze_payload, arguments.freeze_sha256)
    if not _outputs_absent():
        raise RuntimeError("calibration output appeared during freeze validation")

    _CORE = _load_repository_module("lrs001r1_core", CORE_REL, loaded[CORE_REL])
    _SYNTHETIC = _load_repository_module(
        "lrs001r1_synthetic", SYNTHETIC_REL, loaded[SYNTHETIC_REL])
    rows, _GEOMETRY, _SYNTHETIC_GEOMETRY = _load_geometry(_CORE, _SYNTHETIC, loaded)

    registry = _SYNTHETIC.world_registry()
    observed_registry = Counter(world.family for world in registry)
    if len(registry) != 208 or observed_registry != Counter(dict(FAMILY_COUNTS)) or \
            tuple(world.ordinal for world in registry) != tuple(range(208)):
        raise RuntimeError("synthetic world registry drift")

    _ASSIGNMENTS = _CORE.generate_assignment_maps(_GEOMETRY)
    _validate_assignments(_CORE, _GEOMETRY, _ASSIGNMENTS, frozen_digest=True)
    _validate_all_contrasts()

    positive_fixtures = [world for world in registry if world.family == "ORDER_FULL"]
    remaining = [world for world in registry if world.family != "ORDER_FULL"]
    workers = _worker_count(arguments.workers)
    if workers == 1:
        records = [_run_world(world) for world in remaining]
    else:
        context = mp.get_context("fork")
        with context.Pool(
            processes=workers,
            initializer=_worker_initializer,
            maxtasksperchild=1,
        ) as pool:
            records = pool.map(_run_world, remaining, chunksize=1)

    positive_internal = None
    positive_world = None
    for positive_fixture in positive_fixtures:
        positive_public, candidate_internal, candidate_world = \
            _run_world_with_internal(positive_fixture)
        records.append(positive_public)
        if positive_internal is None and candidate_internal is not None:
            positive_internal = candidate_internal
            positive_world = candidate_world
        else:
            del candidate_internal
            gc.collect()
    records.sort(key=lambda row: int(row["ordinal"]))

    if positive_internal is None:
        invariance = {name: False for name in INVARIANCE_CONTROL_NAMES}
        malformed = {name: False for name in MALFORMED_CONTROL_NAMES}
        # The output must still be able to report a clean STOP. Exercise the
        # audit denial even though the scientific malformed-control suite has
        # no fitted positive fixture and therefore remains false.
        if not _undeclared_read_denied():
            raise RuntimeError("undeclared-read audit probe did not reject")
    else:
        invariance = {
            "row_order_rebuild_and_numeric": _row_order_control(
                rows, _GEOMETRY, _SYNTHETIC_GEOMETRY,
                positive_world, positive_internal),
            "record_renaming_with_carried_maps": _record_renaming_control(
                rows, _GEOMETRY, positive_world, positive_internal),
            "class_label_permutation": _class_permutation_control(
                _GEOMETRY, positive_world, positive_internal),
            "physical_reversal_with_carried_maps": _physical_reversal_control(
                rows, _GEOMETRY, positive_world, positive_internal),
        }
        malformed = _malformed_controls(rows, positive_world, positive_internal)
        del positive_internal
    gc.collect()

    families = _family_summaries(records)
    aggregate_gates = {
        "exact_208_world_registry": len(records) == 208,
        "zero_of_64_null": families["NULL"]["passes"] == 0,
        "all_8_order_full": families["ORDER_FULL"]["passes"] == 8,
        "all_8_order_reduced": families["ORDER_REDUCED"]["passes"] == 8,
        "zero_of_8_each_adversarial": all(families[name]["passes"] == 0
                                           for name in NEGATIVE_FAMILIES),
        "all_malformed_controls_rejected": all(malformed.values()),
        "all_invariance_controls_pass": all(invariance.values()),
        "exact_8192_by_453_assignment_orbit": (
            _ASSIGNMENTS.maps.shape == (8192, 453) and
            _little_i8_digest(_ASSIGNMENTS.maps) == ASSIGNMENT_SHA256 and
            _little_i8_digest(_ASSIGNMENTS.retries) == RETRY_SHA256 and
            int(_ASSIGNMENTS.retries.max()) == 0
        ),
        "exact_input_audit_before_output": _audit_ready_for_install(),
        "real_association_absent": True,
        "ocr_and_automated_vision_absent": True,
    }
    passed = all(aggregate_gates.values())
    status = ("PASS_LRS001R1_TARGET_BLIND_CALIBRATION" if passed else
              "STOP_LRS001R1_TARGET_BLIND_CALIBRATION")
    decision = ("AUTHORIZE_SEPARATE_LRS001R1_TARGET_REGISTRATION" if passed else
                "TARGET_FORBIDDEN")
    result = {
        "experiment": RESULT_EXPERIMENT,
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "decision": decision,
        "registration_commit": freeze["registration_commit"],
        "freeze_sha256": arguments.freeze_sha256,
        "inputs": {**dict(freeze["bound_files"]), FREEZE_REL: arguments.freeze_sha256},
        "geometry_counts": {
            "rows": len(_GEOMETRY.rows), "records": len(_GEOMETRY.records),
            "test_targets": 1784, "test_target_bearing_records": 445,
            "test_movable_records": 453, "test_cells": 118,
            "test_pages": 40, "test_folios": 21, "opaque_classes": 66,
        },
        "assignment": {
            "rows": 8192, "columns": 453,
            "map_sha256": ASSIGNMENT_SHA256, "retry_sha256": RETRY_SHA256,
            "maximum_retry": 0,
        },
        "worlds": records,
        "families": families,
        "controls": {"invariance": invariance, "malformed": malformed},
        "gates": aggregate_gates,
        "workers": workers,
        "isolation": {
            "allowed_repository_input_count": 8,
            "observed_repository_input_count": len(set(_AUDIT_READS)),
            "expected_denied_read_count": len(_AUDIT_EXPECTED_DENIALS),
            "unexpected_audit_event_count": len(_AUDIT_UNEXPECTED),
            "repository_temporary_paths_created": 0,
            "calibration_outputs_absent_immediately_before_install": True,
            "real_class_identity_or_family_surface_accessed": False,
            "real_context_target_association_scored": False,
            "ocr_or_automated_vision_used": False,
        },
        "claim_ceiling": (
            "Target-blind synthetic instrument calibration only; no manuscript field, "
            "word, role, language, meaning, plaintext, or translation."
        ),
    }
    json_payload = _canonical_json(result)
    report_payload = _report(result)
    _install_outputs(json_payload, report_payload)
    print(json.dumps({"status": status, "decision": decision,
                      "family_passes": {name: families[name]["passes"]
                                        for name, _ in FAMILY_COUNTS}},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
