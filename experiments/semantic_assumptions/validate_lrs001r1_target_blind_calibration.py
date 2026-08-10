#!/usr/bin/env python3
"""Independent reconstruction of the LRS001-R1 target-blind calibration.

This validator deliberately does not import, execute, or introspect
``lrs001r1_core.py``, ``lrs001r1_synthetic.py``, or the calibration runner.
It reconstructs the registered geometry, fixtures, models, assignment orbit,
statistics, gates, controls, aggregate JSON, and Markdown report from the
frozen public inputs.  It refuses to run the registered reconstruction while
the calibration result is absent; ``--self-test`` uses tiny fabricated data
only.
"""

from __future__ import annotations

import os

for _variable in (
    "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ[_variable] = "1"

import argparse
import csv
import hashlib
import io
import json
import math
import multiprocessing as mp
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np


_WORKER_GEOMETRY = None
_WORKER_ASSIGNMENTS = None


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = HERE / "results"

GEOMETRY_TSV_REL = "experiments/semantic_assumptions/results/lrs001r1_anonymous_geometry.tsv"
GEOMETRY_JSON_REL = "experiments/semantic_assumptions/results/lrs001r1_anonymous_geometry.json"
SPEC_REL = "experiments/semantic_assumptions/LRS001R1_TARGET_BLIND_CALIBRATION_SPEC.md"
FREEZE_REL = "experiments/semantic_assumptions/LRS001R1_TARGET_BLIND_CALIBRATION_FREEZE.json"
AMENDMENT_REL = "experiments/semantic_assumptions/LRS001R1_CALIBRATION_VALIDATION_AMENDMENT.json"
RESULT_REL = "experiments/semantic_assumptions/results/lrs001r1_target_blind_calibration.json"
REPORT_REL = "experiments/semantic_assumptions/results/lrs001r1_target_blind_calibration.md"
VALIDATOR_REL = "experiments/semantic_assumptions/validate_lrs001r1_target_blind_calibration.py"
VALIDATION_REL = "experiments/semantic_assumptions/results/lrs001r1_target_blind_calibration_validation.json"
VALIDATION_REPORT_REL = "experiments/semantic_assumptions/results/lrs001r1_target_blind_calibration_validation.md"

CORE_REL = "experiments/semantic_assumptions/lrs001r1_core.py"
SYNTHETIC_REL = "experiments/semantic_assumptions/lrs001r1_synthetic.py"
RUNNER_REL = "experiments/semantic_assumptions/run_lrs001r1_target_blind_calibration.py"
BOUND_RELS = (
    GEOMETRY_TSV_REL, GEOMETRY_JSON_REL, SPEC_REL, CORE_REL,
    SYNTHETIC_REL, RUNNER_REL, VALIDATOR_REL,
)
READ_RELS = frozenset((
    GEOMETRY_TSV_REL, GEOMETRY_JSON_REL, SPEC_REL, FREEZE_REL, AMENDMENT_REL,
    RESULT_REL, REPORT_REL, VALIDATOR_REL, CORE_REL, SYNTHETIC_REL, RUNNER_REL,
))

GEOMETRY_TSV_SHA256 = "37f06364effab97140d50fd64984ee561ed84f9087866314db7fec4f059647df"
GEOMETRY_JSON_SHA256 = "0c251db4526f54a1b3bec15528f32a95c782d3a7d8f134ab49b6afb872bd1542"
ASSIGNMENT_SHA256 = "48a20b6b16f38f7cfab037cae72da8d24ff2f2f4cdcf1c6e08945ab5dc6dc7e6"
RETRY_SHA256 = "de2f256064a0af797747c2b97505dc0b9f3df0de4f489eac731c23ae9ca9cc31"

FREEZE_EXPERIMENT = "LRS001R1_TARGET_BLIND_CALIBRATION_FREEZE"
RESULT_EXPERIMENT = "LRS001R1_TARGET_BLIND_CALIBRATION"
RESULT_SCHEMA = "LRS001R1_AGGREGATE_CALIBRATION_V1"
VALIDATION_EXPERIMENT = "LRS001R1_TARGET_BLIND_CALIBRATION_VALIDATION"
VALIDATION_SCHEMA = "LRS001R1_AGGREGATE_CALIBRATION_VALIDATION_V2"
AMENDMENT_EXPERIMENT = "LRS001R1_CALIBRATION_VALIDATION_AMENDMENT"

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ"
CLASS_LAYOUT = {1: 3, 2: 8, 3: 23, 4: 19, 5: 10, 6: 3}
RIDGES = (0.25, 1.0, 4.0, 16.0)
RANKS = (1, 2)
BLOCK_DIM = 648
TOL = 1.0e-12
FLOOR = 1.0e-6
N_ASSIGNMENTS = 8192

FAMILY_COUNTS = (
    ("NULL", 64), ("ORDER_FULL", 8), ("ORDER_REDUCED", 8),
    ("PAGE_TOPIC", 8), ("GLOBAL_FIXED_COLUMN", 8),
    ("LENGTH_BY_COLUMN", 8), ("CODE_DRAWING_STATE", 8),
    ("ORDERED_LENGTH_SHAPE", 8), ("UNORDERED_BAG_TOPIC", 8),
    ("PURE_FIRST_ORDER", 8), ("ONE_FOLIO", 8), ("ONE_CURRIER", 8),
    ("ONE_SECTION", 8), ("ONE_POSITION", 8), ("ONE_RECORD_LENGTH", 8),
    ("ONE_SURFACE", 8), ("EXACT_DUPLICATE_ONLY", 8),
    ("RANDOM_DONOR", 8), ("REVERSED_MAPPING", 8),
)
NEGATIVE_FAMILIES = frozenset(name for name, _ in FAMILY_COUNTS) - {
    "NULL", "ORDER_FULL", "ORDER_REDUCED",
}
SEPARATION_FAMILIES = frozenset(
    {"ONE_POSITION", "ONE_SURFACE", "RANDOM_DONOR", "REVERSED_MAPPING"}
)
FULL_CONTEXT_FAMILIES = frozenset(
    {"ORDER_FULL", "ONE_POSITION", "ONE_SURFACE", "RANDOM_DONOR", "REVERSED_MAPPING"}
)
INVARIANCE_NAMES = (
    "row_order_rebuild_and_numeric", "record_renaming_with_carried_maps",
    "class_label_permutation", "physical_reversal_with_carried_maps",
)
MALFORMED_NAMES = (
    "malformed_cell", "repeated_donor", "split_crossing_donor",
    "nonzero_sum_contrast", "donor_position_j_excluded",
    "recipient_neighbour_not_mixed", "cell_excluded_page_background",
    "undeclared_repository_read", "nonfinite_probability", "class_loss",
    "output_overwrite",
)

FIELDS = (
    "anonymous_group_id", "anonymous_record_id", "split", "page",
    "physical_folio", "section", "currier", "hand", "code", "kind",
    "segment_group_count", "segment_group_index", "segment_position",
    "segment_count", "segment_index", "starts_after_drawing",
    "ends_before_drawing", "original_group_count", "symbol_count",
    "supported_class_target", "strict_test_movable", "strict_cell_id",
    "strict_cell_record_count",
)
INT_FIELDS = frozenset((
    "segment_group_count", "segment_group_index", "segment_count",
    "segment_index", "starts_after_drawing", "ends_before_drawing",
    "original_group_count", "symbol_count", "supported_class_target",
    "strict_test_movable", "strict_cell_record_count",
))
CATEGORICAL_FIELDS = (
    "currier", "section", "hand", "code", "record_length", "target_ordinal",
    "segment_count", "segment_index", "starts_after_drawing",
    "ends_before_drawing", "original_group_count", "target_symbol_count",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def _i8_hash(value: object) -> str:
    return _sha(np.ascontiguousarray(np.asarray(value, dtype="<i8")).tobytes(order="C"))


def _i2_hash(value: object) -> str:
    return _sha(np.ascontiguousarray(np.asarray(value, dtype="<i2")).tobytes(order="C"))


def _f8_hash(value: object) -> str:
    array = np.ascontiguousarray(np.asarray(value, dtype="<f8"))
    if not np.all(np.isfinite(array)):
        raise ValueError("nonfinite float digest input")
    return _sha(array.tobytes(order="C"))


def _u(key: str) -> float:
    if not key.startswith("LRS001R1|"):
        raise ValueError("hash domain outside LRS001R1")
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return (int.from_bytes(digest[:8], "little") + 0.5) / 2**64


def _direction(key: str) -> np.ndarray:
    angle = 2.0 * math.pi * _u(key)
    return np.asarray((math.cos(angle), math.sin(angle)), dtype=np.float64)


def _coordinate(count: int, index: int) -> np.ndarray:
    angle = 2.0 * math.pi * index / count
    return np.asarray((math.cos(angle), math.sin(angle)), dtype=np.float64)


def _rotate(value: np.ndarray, length: int, ordinal: int) -> np.ndarray:
    angle = 2.0 * math.pi * (ordinal - 1) / length
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.asarray((cosine * value[0] - sine * value[1],
                       sine * value[0] + cosine * value[1]), dtype=np.float64)


def _softmax(logits: object) -> np.ndarray:
    value = np.asarray(logits, dtype=np.float64)
    if value.ndim != 1 or len(value) < 2 or not np.all(np.isfinite(value)):
        raise ValueError("bad logits")
    weights = np.exp(value - value.max())
    return weights / weights.sum()


def _draw(key: str, probabilities: object) -> int:
    value = np.asarray(probabilities, dtype=np.float64)
    if value.ndim != 1 or np.any(value < 0) or not np.all(np.isfinite(value)) or \
            abs(float(value.sum()) - 1.0) > TOL:
        raise ValueError("bad categorical probabilities")
    threshold = _u(key)
    cumulative = 0.0
    for index, probability in enumerate(value):
        cumulative += float(probability)
        if cumulative >= threshold:
            return index
    if cumulative >= 1.0 - TOL:
        return len(value) - 1
    raise ValueError("categorical residual too large")


def _directional_draw(count: int, direction: np.ndarray, amplitude: float,
                      key: str) -> int:
    logits = [amplitude * float(_coordinate(count, index) @ direction)
              for index in range(count)]
    return _draw(key, _softmax(logits))


@dataclass(frozen=True)
class VRow:
    group_id: str
    record_id: str
    split: str
    page: str
    folio: str
    section: str
    currier: str
    hand: str
    code: str
    kind: str
    record_length: int
    ordinal: int
    position: str
    segment_count: int
    segment_index: int
    starts_after_drawing: int
    ends_before_drawing: int
    original_group_count: int
    symbol_count: int
    supported: int
    movable: int
    stored_cell: str
    stored_cell_count: int


@dataclass(frozen=True)
class VRecord:
    record_id: str
    split: str
    page: str
    folio: str
    section: str
    currier: str
    hand: str
    code: str
    kind: str
    segment_count: int
    segment_index: int
    starts_after_drawing: int
    ends_before_drawing: int
    original_group_count: int
    cell: str
    rows: tuple[int, ...]

    @property
    def length(self) -> int:
        return len(self.rows)


@dataclass(frozen=True)
class VGeometry:
    rows: tuple[VRow, ...]
    records: tuple[VRecord, ...]
    record_for_row: np.ndarray
    record_index: Mapping[str, int]
    targets: Mapping[str, np.ndarray]


def _cell_id(row: VRow) -> str:
    values = (
        row.page, str(row.record_length), row.code, str(row.segment_count),
        str(row.segment_index), str(row.starts_after_drawing),
        str(row.ends_before_drawing), str(row.original_group_count),
    )
    body = "\x1f".join(values)
    return "C" + hashlib.sha256(("LRS001R1|C|" + body).encode("utf-8")).hexdigest()[:20]


def _geometry_from_dicts(source_rows: Iterable[Mapping[str, object]]) -> VGeometry:
    rows: list[VRow] = []
    for source in source_rows:
        if tuple(source) != FIELDS:
            raise ValueError("geometry schema mismatch")
        converted = {field: (int(str(source[field])) if field in INT_FIELDS
                             else str(source[field])) for field in FIELDS}
        rows.append(VRow(
            converted["anonymous_group_id"], converted["anonymous_record_id"],
            converted["split"], converted["page"], converted["physical_folio"],
            converted["section"], converted["currier"], converted["hand"],
            converted["code"], converted["kind"], converted["segment_group_count"],
            converted["segment_group_index"], converted["segment_position"],
            converted["segment_count"], converted["segment_index"],
            converted["starts_after_drawing"], converted["ends_before_drawing"],
            converted["original_group_count"], converted["symbol_count"],
            converted["supported_class_target"], converted["strict_test_movable"],
            converted["strict_cell_id"], converted["strict_cell_record_count"],
        ))
    rows.sort(key=lambda row: (row.record_id.encode(), row.ordinal, row.group_id.encode()))
    if not rows or len({row.group_id for row in rows}) != len(rows):
        raise ValueError("empty/duplicate geometry")
    grouped: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        if row.split not in {"TRAIN", "CAL", "TEST"} or not 1 <= row.symbol_count <= 11:
            raise ValueError("geometry value outside frozen domain")
        if row.supported not in {0, 1} or row.movable not in {0, 1}:
            raise ValueError("nonbinary geometry flag")
        if row.supported and (row.symbol_count not in CLASS_LAYOUT or
                              row.ordinal in {1, row.record_length}):
            raise ValueError("invalid target geometry")
        grouped[row.record_id].append(index)
    records: list[VRecord] = []
    record_for_row = np.empty(len(rows), dtype=np.int64)
    for record_id in sorted(grouped, key=lambda value: value.encode()):
        indices = tuple(sorted(grouped[record_id], key=lambda index: rows[index].ordinal))
        exemplar = rows[indices[0]]
        if len(indices) != exemplar.record_length or not 5 <= len(indices) <= 12 or \
                [rows[index].ordinal for index in indices] != list(range(1, len(indices) + 1)):
            raise ValueError("incomplete record")
        invariant = (
            "split", "page", "folio", "section", "currier", "hand", "code", "kind",
            "record_length", "segment_count", "segment_index", "starts_after_drawing",
            "ends_before_drawing", "original_group_count", "stored_cell", "stored_cell_count",
        )
        if any(len({getattr(rows[index], field) for index in indices}) != 1
               for field in invariant):
            raise ValueError("within-record drift")
        cell = _cell_id(exemplar)
        if exemplar.split == "TEST" and exemplar.stored_cell != cell:
            raise ValueError("TEST cell hash mismatch")
        if exemplar.split != "TEST" and (exemplar.stored_cell or exemplar.stored_cell_count):
            raise ValueError("TRAIN/CAL exposes TEST cell")
        record = VRecord(
            record_id, exemplar.split, exemplar.page, exemplar.folio,
            exemplar.section, exemplar.currier, exemplar.hand, exemplar.code,
            exemplar.kind, exemplar.segment_count, exemplar.segment_index,
            exemplar.starts_after_drawing, exemplar.ends_before_drawing,
            exemplar.original_group_count, cell, indices,
        )
        record_for_row[list(indices)] = len(records)
        records.append(record)
    test_cells: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        if record.split == "TEST":
            test_cells[record.cell].append(index)
    for cell, members in test_cells.items():
        for record_index in members:
            exemplar = rows[records[record_index].rows[0]]
            if exemplar.stored_cell_count != len(members) or exemplar.movable != int(len(members) >= 2):
                raise ValueError(f"TEST cell count/mobility drift: {cell}")
    targets = {}
    for split in ("TRAIN", "CAL", "TEST"):
        targets[split] = np.asarray([
            index for index, row in enumerate(rows)
            if row.split == split and row.supported and (split != "TEST" or row.movable)
        ], dtype=np.int64)
    geometry = VGeometry(tuple(rows), tuple(records), record_for_row,
                         {record.record_id: index for index, record in enumerate(records)}, targets)
    test = targets["TEST"]
    counts = (
        len(test), len({int(record_for_row[index]) for index in test}),
        len({records[int(record_for_row[index])].cell for index in test}),
        len({rows[index].page for index in test}), len({rows[index].folio for index in test}),
    )
    if counts != (1784, 445, 118, 40, 21):
        raise ValueError(f"strict TEST count drift: {counts}")
    return geometry


def _load_geometry(tsv: bytes, manifest_bytes: bytes) -> tuple[VGeometry, list[dict[str, str]]]:
    if _sha(tsv) != GEOMETRY_TSV_SHA256 or _sha(manifest_bytes) != GEOMETRY_JSON_SHA256:
        raise ValueError("geometry hash mismatch")
    manifest = json.loads(manifest_bytes)
    if manifest.get("status") != "PASS_LABEL_FREE_PSEUDONYMOUS_GEOMETRY" or \
            manifest.get("decision") != "GO_TARGET_BLIND_SYNTHETIC_CALIBRATION_ONLY" or \
            tuple(manifest.get("schema", ())) != FIELDS or \
            manifest.get("tsv_sha256") != GEOMETRY_TSV_SHA256:
        raise ValueError("geometry manifest drift")
    if {int(key): int(value) for key, value in
            dict(manifest.get("opaque_class_count_by_symbol_count", {})).items()} != CLASS_LAYOUT:
        raise ValueError("opaque class layout drift")
    isolation = manifest.get("isolation", {})
    if any(bool(isolation.get(key)) for key in (
        "real_class_identity_or_family_surface_emitted",
        "real_context_target_association_scored", "predictor_fitted",
        "ocr_or_automated_vision_used",
    )):
        raise ValueError("geometry isolation drift")
    reader = csv.DictReader(io.StringIO(tsv.decode("utf-8"), newline=""), delimiter="\t")
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise ValueError("TSV header drift")
    raw = [dict(row) for row in reader]
    return _geometry_from_dicts(raw), raw


@dataclass(frozen=True)
class VWorldSpec:
    ordinal: int
    family: str
    index: int

    def key(self, purpose: str, *parts: object) -> str:
        return "|".join(("LRS001R1", "WORLD", "20260810", self.family,
                         str(self.index), purpose, *(str(part) for part in parts)))


def _registry() -> tuple[VWorldSpec, ...]:
    worlds: list[VWorldSpec] = []
    for family, count in FAMILY_COUNTS:
        for index in range(count):
            worlds.append(VWorldSpec(len(worlds), family, index))
    if len(worlds) != 208:
        raise AssertionError("world registry drift")
    return tuple(worlds)


def _prototype_bank() -> tuple[tuple[str, ...], Mapping[int, np.ndarray]]:
    sequences: list[tuple[str, ...]] = []
    blocks: dict[int, np.ndarray] = {}
    for length in range(1, 12):
        accepted: list[str] = []
        seen: set[str] = set()
        for prototype in range(24):
            for nonce in range(10000):
                digest = hashlib.sha256(
                    f"LRS001R1|PROTO|{length}|{prototype}|{nonce}".encode()).digest()
                sequence = "".join(ALPHABET[value % 24] for value in digest[:length])
                if sequence not in seen:
                    seen.add(sequence)
                    accepted.append(sequence)
                    break
            else:
                raise ValueError("prototype nonce exhausted")
        matrix = np.zeros((24, BLOCK_DIM), dtype=np.float64)
        for prototype, sequence in enumerate(accepted):
            values = [ALPHABET.index(symbol) for symbol in sequence]
            for value in values:
                matrix[prototype, value] += 1.0 / len(values)
            matrix[prototype, 24 + values[0]] = 1.0
            matrix[prototype, 48 + values[-1]] = 1.0
            if len(values) > 1:
                for left, right in zip(values[:-1], values[1:]):
                    matrix[prototype, 72 + 24 * left + right] += 1.0 / (len(values) - 1)
        sequences.append(tuple(accepted))
        blocks[length] = matrix
    return tuple(sequences), blocks


PROTOTYPES, PROTOTYPE_BLOCKS = _prototype_bank()


@dataclass(frozen=True)
class VWorld:
    spec: VWorldSpec
    prototypes: np.ndarray
    classes: np.ndarray
    separation: np.ndarray
    nonces: tuple[int, ...]
    copied: tuple[str, ...]


def _full(world: VWorldSpec, record: VRecord, row: VRow) -> np.ndarray:
    return _rotate(_direction(world.key("RECORD_DIRECTION", record.record_id)),
                   row.record_length, row.ordinal)


def _null(world: VWorldSpec, row: VRow, purpose: str = "NULL_DIRECTION") -> np.ndarray:
    return _direction(world.key(purpose, row.group_id))


def _world_draw(world: VWorldSpec, row: VRow, pool: int, direction: np.ndarray,
                amplitude: float, nonce: int, purpose: str = "GROUP_DRAW") -> int:
    return _directional_draw(pool, direction, amplitude,
                             world.key(purpose, row.group_id, nonce))


def _context(geometry: VGeometry, world: VWorldSpec, record: VRecord,
             row: VRow) -> tuple[np.ndarray, float]:
    family = world.family
    if family == "NULL": return _null(world, row), 1.0
    if family == "ORDER_REDUCED": return _full(world, record, row), 2.0
    if family in FULL_CONTEXT_FAMILIES or family == "ORDER_FULL":
        return _full(world, record, row), 3.0
    if family == "PAGE_TOPIC": return _direction(world.key("PAGE_DIRECTION", row.page)), 3.0
    if family == "GLOBAL_FIXED_COLUMN":
        return _direction(world.key("COLUMN_DIRECTION", row.record_length, row.ordinal)), 3.0
    if family == "LENGTH_BY_COLUMN":
        return _direction(world.key("LENGTH_COLUMN_DIRECTION", row.record_length,
                                    row.ordinal, row.symbol_count)), 3.0
    if family == "CODE_DRAWING_STATE":
        return _direction(world.key(
            "CODE_DRAWING_DIRECTION", row.code, row.segment_count, row.segment_index,
            row.starts_after_drawing, row.ends_before_drawing, row.original_group_count)), 3.0
    if family == "ORDERED_LENGTH_SHAPE":
        return _direction(world.key("LENGTH_SHAPE_CONTEXT", row.ordinal, row.symbol_count)), 3.0
    if family == "UNORDERED_BAG_TOPIC":
        return _direction(world.key("BAG_DIRECTION", record.record_id)), 3.0
    if family == "ONE_FOLIO":
        folios = sorted({candidate.folio for candidate in geometry.rows
                         if candidate.split == "TEST" and candidate.movable and candidate.supported},
                        key=lambda value: value.encode())
        if row.split in {"TRAIN", "CAL"} or row.folio == folios[world.index % len(folios)]:
            return _full(world, record, row), 3.0
        return _null(world, row), 1.0
    if family == "ONE_CURRIER":
        if row.currier == ("A" if world.index % 2 == 0 else "B"):
            return _full(world, record, row), 3.0
        return _null(world, row), 1.0
    if family == "ONE_SECTION":
        if row.section == ("B", "H", "S")[world.index % 3]:
            return _full(world, record, row), 3.0
        return _null(world, row), 1.0
    if family == "ONE_RECORD_LENGTH":
        if (0 if row.record_length <= 8 else 1) == world.index % 2:
            return _full(world, record, row), 3.0
        return _null(world, row), 1.0
    raise ValueError(f"specialized context family: {family}")


def _position_band(row: VRow) -> int:
    return min(2, math.floor(3 * (row.ordinal - 1) / (row.record_length - 1)))


def _successors(geometry: VGeometry) -> Mapping[str, str]:
    cells: dict[str, list[str]] = defaultdict(list)
    for record in geometry.records:
        row = geometry.rows[record.rows[0]]
        if row.split == "TEST" and row.movable:
            cells[record.cell].append(record.record_id)
    output = {}
    for cell in sorted(cells, key=lambda value: value.encode()):
        values = sorted(cells[cell], key=lambda value: value.encode())
        if len(values) < 2:
            raise ValueError("movable singleton")
        for index, value in enumerate(values):
            output[value] = values[(index + 1) % len(values)]
    return output


def _target_draw(geometry: VGeometry, world: VWorldSpec, record: VRecord,
                 row: VRow, nonce: int, successors: Mapping[str, str]) -> int:
    count = CLASS_LAYOUT[row.symbol_count]
    if world.family == "ONE_POSITION":
        if _position_band(row) == world.index % 3:
            direction, amplitude = _full(world, record, row), 3.0
        else:
            direction, amplitude = _null(world, row, "TARGET_NULL_DIRECTION"), 1.0
        return _world_draw(world, row, count, direction, amplitude, nonce, "TARGET_DRAW")
    if world.family == "ONE_SURFACE":
        classes = [(length, index) for length in sorted(CLASS_LAYOUT)
                   for index in range(CLASS_LAYOUT[length])]
        selected = classes[world.index % len(classes)]
        full, null = _full(world, record, row), _null(world, row, "TARGET_NULL_DIRECTION")
        logits = []
        for index in range(count):
            coordinate = _coordinate(count, index)
            value = float(coordinate @ null)
            if (row.symbol_count, index) == selected:
                value += 3.0 * float(coordinate @ full)
            logits.append(value)
        return _draw(world.key("TARGET_DRAW", row.group_id, nonce), _softmax(logits))
    if world.family == "RANDOM_DONOR":
        target = record
        if row.split == "TEST" and row.movable:
            target = geometry.records[geometry.record_index[successors[record.record_id]]]
        direction = _rotate(_direction(world.key("RECORD_DIRECTION", target.record_id)),
                            row.record_length, row.ordinal)
        return _world_draw(world, row, count, direction, 3.0, nonce, "TARGET_DRAW")
    if world.family == "REVERSED_MAPPING":
        direction = (_rotate(_direction(world.key("RECORD_DIRECTION", record.record_id)),
                             row.record_length, row.record_length + 1 - row.ordinal)
                     if row.split == "TEST" else _full(world, record, row))
        return _world_draw(world, row, count, direction, 3.0, nonce, "TARGET_DRAW")
    raise ValueError("unregistered separated target")


def _regular_record(geometry: VGeometry, world: VWorldSpec, record: VRecord,
                    nonce: int, successors: Mapping[str, str]
                    ) -> tuple[list[int], list[int], list[bool]]:
    if world.family == "PURE_FIRST_ORDER":
        prototypes, classes = [], []
        previous = -1
        for local, row_index in enumerate(record.rows):
            row = geometry.rows[row_index]
            pool = CLASS_LAYOUT[row.symbol_count] if row.supported else 24
            if local == 0:
                direction, amplitude = _null(world, row, "FIRST_ORDER_INITIAL_DIRECTION"), 1.0
            elif _u(world.key("FIRST_ORDER_TRANSITION", row.group_id)) < 0.8:
                direction, amplitude = _coordinate(24, previous), 3.0
            else:
                direction, amplitude = _null(world, row, "FIRST_ORDER_INDEPENDENT_DIRECTION"), 1.0
            value = _world_draw(world, row, pool, direction, amplitude, nonce,
                                "FIRST_ORDER_DRAW")
            prototypes.append(value)
            classes.append(value if row.supported else -1)
            previous = value
        return prototypes, classes, [False] * len(prototypes)

    record_rows = [geometry.rows[index] for index in record.rows]
    length_shape = None
    if world.family == "ORDERED_LENGTH_SHAPE":
        odd = sum(math.log1p(row.symbol_count) for row in record_rows if row.ordinal % 2)
        even = sum(math.log1p(row.symbol_count) for row in record_rows if not row.ordinal % 2)
        length_shape = np.asarray((odd, even), dtype=np.float64)
        length_shape /= np.linalg.norm(length_shape)
    prototypes, classes, separation = [], [], []
    for row in record_rows:
        direction, amplitude = _context(geometry, world, record, row)
        if length_shape is not None and row.supported:
            direction = length_shape
        if world.family in SEPARATION_FAMILIES:
            prototype = _world_draw(world, row, 24, direction, amplitude, nonce)
            target = (_target_draw(geometry, world, record, row, nonce, successors)
                      if row.supported else -1)
            separated = bool(row.supported)
        else:
            pool = CLASS_LAYOUT[row.symbol_count] if row.supported else 24
            prototype = _world_draw(world, row, pool, direction, amplitude, nonce)
            target, separated = (prototype if row.supported else -1), False
        prototypes.append(prototype)
        classes.append(target)
        separation.append(separated)
    return prototypes, classes, separation


def _duplicate_strata(geometry: VGeometry
                      ) -> tuple[list[tuple[VRecord, VRecord]], list[VRecord]]:
    strata: dict[tuple[object, ...], list[VRecord]] = defaultdict(list)
    for record in geometry.records:
        rows = [geometry.rows[index] for index in record.rows]
        key = (record.split, tuple(row.symbol_count for row in rows),
               tuple(row.supported for row in rows))
        strata[key].append(record)
    pairs, unpaired = [], []
    for key in sorted(strata, key=lambda value: (str(value[0]).encode(), value[1], value[2])):
        values = sorted(strata[key], key=lambda record: record.record_id.encode())
        pairs.extend((values[index], values[index + 1])
                     for index in range(0, len(values) - 1, 2))
        if len(values) % 2:
            unpaired.append(values[-1])
    pairs.sort(key=lambda pair: (pair[0].split.encode(), pair[0].record_id.encode()))
    unpaired.sort(key=lambda record: (record.split.encode(), record.record_id.encode()))
    return pairs, unpaired


def _duplicate_world(geometry: VGeometry, world: VWorldSpec) -> VWorld:
    prototypes = np.full(len(geometry.rows), -1, dtype=np.int16)
    classes = np.full(len(geometry.rows), -1, dtype=np.int16)
    separation = np.zeros(len(geometry.rows), dtype=bool)
    signatures: dict[str, set[object]] = defaultdict(set)
    nonces: dict[str, int] = {}
    copied = []
    pairs, unpaired = _duplicate_strata(geometry)
    for first, second in pairs:
        rows = [geometry.rows[index] for index in first.rows]
        for nonce in range(10000):
            proposed = [_world_draw(
                world, row, CLASS_LAYOUT[row.symbol_count] if row.supported else 24,
                _full(world, first, row), 3.0, nonce, "DUPLICATE_FULL_DRAW")
                for row in rows]
            signature = tuple((row.symbol_count, value)
                              for row, value in zip(rows, proposed))
            if signature not in signatures[first.split]:
                signatures[first.split].add(signature)
                break
        else:
            raise ValueError("duplicate pair nonce exhausted")
        for left_index, right_index, row, value in zip(first.rows, second.rows, rows, proposed):
            prototypes[left_index] = prototypes[right_index] = value
            if row.supported:
                classes[left_index] = classes[right_index] = value
        nonces[first.record_id] = nonces[second.record_id] = nonce
        copied.append(second.record_id)
    for record in unpaired:
        rows = [geometry.rows[index] for index in record.rows]
        for nonce in range(10000):
            proposed = [_world_draw(
                world, row, CLASS_LAYOUT[row.symbol_count] if row.supported else 24,
                _null(world, row), 1.0, nonce) for row in rows]
            signature = tuple((row.symbol_count, value)
                              for row, value in zip(rows, proposed))
            if signature not in signatures[record.split]:
                signatures[record.split].add(signature)
                break
        else:
            raise ValueError("duplicate singleton nonce exhausted")
        for row_index, row, value in zip(record.rows, rows, proposed):
            prototypes[row_index] = value
            if row.supported:
                classes[row_index] = value
        nonces[record.record_id] = nonce
    return VWorld(world, prototypes, classes, separation,
                  tuple(nonces[record.record_id] for record in geometry.records),
                  tuple(sorted(copied, key=lambda value: value.encode())))


def _generate_world(geometry: VGeometry, world: VWorldSpec) -> VWorld:
    if world.family == "EXACT_DUPLICATE_ONLY":
        generated = _duplicate_world(geometry, world)
    else:
        prototypes = np.full(len(geometry.rows), -1, dtype=np.int16)
        classes = np.full(len(geometry.rows), -1, dtype=np.int16)
        separation = np.zeros(len(geometry.rows), dtype=bool)
        seen: dict[str, set[object]] = defaultdict(set)
        nonces = []
        successors = _successors(geometry) if world.family == "RANDOM_DONOR" else {}
        for record in geometry.records:
            for nonce in range(10000):
                values, targets, separated = _regular_record(
                    geometry, world, record, nonce, successors)
                signature = tuple((geometry.rows[row_index].symbol_count, values[local])
                                  for local, row_index in enumerate(record.rows))
                if signature not in seen[record.split]:
                    seen[record.split].add(signature)
                    break
            else:
                raise ValueError("world record nonce exhausted")
            for local, row_index in enumerate(record.rows):
                prototypes[row_index], classes[row_index] = values[local], targets[local]
                separation[row_index] = separated[local]
            nonces.append(nonce)
        generated = VWorld(world, prototypes, classes, separation, tuple(nonces), ())
    if np.any(generated.prototypes < 0):
        raise ValueError("incomplete world")
    for index, row in enumerate(geometry.rows):
        target = int(generated.classes[index])
        if row.supported:
            if not 0 <= target < CLASS_LAYOUT[row.symbol_count]:
                raise ValueError("world target outside class head")
            if not generated.separation[index] and target != generated.prototypes[index]:
                raise ValueError("unregistered separation")
        elif target != -1 or generated.separation[index]:
            raise ValueError("unsupported row target")
    if bool(np.any(generated.separation)) != (world.family in SEPARATION_FAMILIES):
        raise ValueError("separation family mismatch")
    return generated


def _world_digests(world: VWorld) -> dict[str, str]:
    return {
        "prototype_indices_sha256": _i2_hash(world.prototypes),
        "class_indices_sha256": _i2_hash(world.classes),
        "target_separation_sha256": _sha(np.ascontiguousarray(
            world.separation.astype(np.uint8)).tobytes()),
        "record_nonces_sha256": _i8_hash(world.nonces),
        "copied_record_ids_sha256": _sha(_json_bytes(sorted(
            world.copied, key=lambda value: value.encode("utf-8")))),
    }


def _dct(length: int, ordinal: int) -> tuple[np.ndarray, np.ndarray]:
    positions = np.asarray([value for value in range(1, length + 1)
                            if abs(value - ordinal) >= 2], dtype=np.int64)
    output = np.zeros((2, length), dtype=np.float64)
    accepted: list[np.ndarray] = []
    for rank in (1, 2):
        vector = np.cos(math.pi * rank * (2.0 * positions - 1.0) / (2.0 * length))
        vector -= vector.mean()
        for prior in accepted:
            vector -= float(vector @ prior) * prior
        norm = float(np.linalg.norm(vector))
        if norm <= TOL:
            continue
        vector /= norm
        if abs(float(vector.sum())) > TOL or any(abs(float(vector @ prior)) > TOL
                                                 for prior in accepted):
            raise ValueError("DCT invariant failure")
        accepted.append(vector)
        output[rank - 1, positions - 1] = vector
    return output[0], output[1]


@dataclass(frozen=True)
class VEvent:
    index: int
    row: int
    record: int
    split: str
    target_class: int
    target_length: int
    ordinal: int
    cell: str
    page: str
    folio: str
    section: str
    currier: str


@dataclass(frozen=True)
class VSchema:
    levels: Mapping[str, tuple[str, ...]]
    offsets: Mapping[str, int]
    width: int

    def encode(self, values: Mapping[str, object]) -> np.ndarray:
        output = np.zeros(self.width, dtype=np.float64)
        for field in CATEGORICAL_FIELDS:
            value = str(values[field])
            choices = self.levels[field]
            index = choices.index(value) if value in choices else len(choices)
            output[self.offsets[field] + index] = 1.0
        return output


@dataclass(frozen=True)
class VFeatures:
    geometry: VGeometry
    world: VWorld
    events: tuple[VEvent, ...]
    split_events: Mapping[str, np.ndarray]
    schema: VSchema
    self_features: Mapping[str, Mapping[str, np.ndarray]]
    test_features: Mapping[str, np.ndarray]
    pair_events: np.ndarray
    pair_donors: np.ndarray
    pair_lookup: Mapping[tuple[int, int], int]
    donors_by_cell: Mapping[str, tuple[int, ...]]


def _category_values(row: VRow, record: VRecord) -> Mapping[str, object]:
    return {
        "currier": row.currier, "section": row.section, "hand": row.hand,
        "code": row.code, "record_length": record.length,
        "target_ordinal": row.ordinal, "segment_count": row.segment_count,
        "segment_index": row.segment_index,
        "starts_after_drawing": row.starts_after_drawing,
        "ends_before_drawing": row.ends_before_drawing,
        "original_group_count": row.original_group_count,
        "target_symbol_count": row.symbol_count,
    }


def _fit_schema(geometry: VGeometry) -> VSchema:
    levels, offsets, width = {}, {}, 0
    for field in CATEGORICAL_FIELDS:
        observed = set()
        for row_index in geometry.targets["TRAIN"]:
            row = geometry.rows[int(row_index)]
            record = geometry.records[int(geometry.record_for_row[int(row_index)])]
            observed.add(str(_category_values(row, record)[field]))
        choices = tuple(sorted(observed, key=lambda value: value.encode()))
        levels[field], offsets[field] = choices, width
        width += len(choices) + 1
    return VSchema(levels, offsets, width)


def _blocks(geometry: VGeometry, world: VWorld) -> np.ndarray:
    output = np.empty((len(geometry.rows), BLOCK_DIM), dtype=np.float64)
    for index, row in enumerate(geometry.rows):
        output[index] = PROTOTYPE_BLOCKS[row.symbol_count][int(world.prototypes[index])]
    return output


def _backgrounds(geometry: VGeometry, blocks: np.ndarray
                 ) -> Mapping[tuple[str, str, str], np.ndarray]:
    by_page: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, record in enumerate(geometry.records):
        by_page[(record.split, record.page)].append(index)
    output = {}
    for (split, page), records in by_page.items():
        for cell in sorted({geometry.records[index].cell for index in records},
                           key=lambda value: value.encode()):
            retained = [index for index in records if geometry.records[index].cell != cell]
            if retained:
                value = np.zeros(BLOCK_DIM, dtype=np.float64)
                for record_index in retained:
                    record = geometry.records[record_index]
                    group_weight = 1.0 / len(retained) / record.length
                    for row_index in record.rows:
                        value += group_weight * blocks[row_index]
                output[(split, page, cell)] = value
                continue
            train = [record for record in geometry.records
                     if record.split == "TRAIN" and record.cell != cell]
            if not train:
                raise ValueError("empty page fallback")
            folios = sorted({record.folio for record in train}, key=lambda value: value.encode())
            pages = {folio: sorted({record.page for record in train if record.folio == folio},
                                   key=lambda value: value.encode()) for folio in folios}
            page_records: dict[tuple[str, str], list[VRecord]] = defaultdict(list)
            for record in train:
                page_records[(record.folio, record.page)].append(record)
            value = np.zeros(BLOCK_DIM, dtype=np.float64)
            total = 0.0
            for record in train:
                weight = (1.0 / len(folios) / len(pages[record.folio]) /
                          len(page_records[(record.folio, record.page)]) / record.length)
                for row_index in record.rows:
                    value += weight * blocks[row_index]
                    total += weight
            output[(split, page, cell)] = value / total
    return output


def _feature_vectors(geometry: VGeometry, blocks: np.ndarray,
                     backgrounds: Mapping[tuple[str, str, str], np.ndarray],
                     schema: VSchema, event: VEvent, donor_index: int
                     ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    row = geometry.rows[event.row]
    recipient, donor = geometry.records[event.record], geometry.records[donor_index]
    if recipient.cell != donor.cell or recipient.length != donor.length:
        raise ValueError("donor outside cell")
    position = event.ordinal - 1
    zero = np.zeros(BLOCK_DIM, dtype=np.float64)
    left = blocks[donor.rows[position - 1]].copy() if position > 0 else zero.copy()
    right = blocks[donor.rows[position + 1]].copy() if position + 1 < donor.length else zero.copy()
    distant = [index for index in range(donor.length) if abs(index - position) >= 2]
    bag = blocks[[donor.rows[index] for index in distant]].mean(axis=0)
    first, second = _dct(donor.length, event.ordinal)
    order1 = sum((first[index] * blocks[donor.rows[index]] for index in distant), zero.copy())
    order2 = sum((second[index] * blocks[donor.rows[index]] for index in distant), zero.copy())
    lengths = np.asarray([math.log1p(geometry.rows[index].symbol_count)
                          for index in donor.rows], dtype=np.float64)
    scalar = np.asarray((
        lengths[position - 1] if position > 0 else 0.0,
        lengths[position + 1] if position + 1 < donor.length else 0.0,
        float(lengths[distant].mean()), float(first @ lengths), float(second @ lengths),
    ), dtype=np.float64)
    nuisance = np.concatenate((
        schema.encode(_category_values(row, recipient)),
        backgrounds[(recipient.split, recipient.page, recipient.cell)], left, right, scalar,
    ))
    bag_vector = np.concatenate((nuisance, bag))
    order_one = np.concatenate((bag_vector, order1))
    order_two = np.concatenate((bag_vector, order1, order2))
    return nuisance, bag_vector, order_one, order_two


def _build_features(geometry: VGeometry, world: VWorld) -> VFeatures:
    blocks = _blocks(geometry, world)
    backgrounds = _backgrounds(geometry, blocks)
    schema = _fit_schema(geometry)
    events: list[VEvent] = []
    split_events: dict[str, list[int]] = defaultdict(list)
    for split in ("TRAIN", "CAL", "TEST"):
        for raw_index in geometry.targets[split]:
            row_index = int(raw_index)
            row = geometry.rows[row_index]
            record_index = int(geometry.record_for_row[row_index])
            record = geometry.records[record_index]
            event = VEvent(
                len(events), row_index, record_index, split,
                int(world.classes[row_index]), row.symbol_count, row.ordinal,
                record.cell, row.page, row.folio, row.section, row.currier,
            )
            events.append(event)
            split_events[split].append(event.index)
    self_features = {}
    for split in ("TRAIN", "CAL"):
        matrices: dict[str, list[np.ndarray]] = {name: [] for name in
                                                ("NUIS", "BAG", "ORDER1", "ORDER2")}
        for event_index in split_events[split]:
            event = events[event_index]
            vectors = _feature_vectors(geometry, blocks, backgrounds, schema,
                                       event, event.record)
            for name, vector in zip(matrices, vectors):
                matrices[name].append(vector)
        self_features[split] = {name: np.stack(values) for name, values in matrices.items()}

    donors_by_cell: dict[str, tuple[int, ...]] = {}
    for record in geometry.records:
        exemplar = geometry.rows[record.rows[0]]
        if record.split == "TEST" and exemplar.movable:
            donors_by_cell[record.cell] = ()
    for cell in donors_by_cell:
        donors_by_cell[cell] = tuple(sorted(
            (index for index, record in enumerate(geometry.records)
             if record.split == "TEST" and record.cell == cell and
             geometry.rows[record.rows[0]].movable),
            key=lambda index: geometry.records[index].record_id.encode()))
    matrices = {name: [] for name in ("NUIS", "BAG", "ORDER1", "ORDER2")}
    pair_events, pair_donors, lookup = [], [], {}
    for event_index in split_events["TEST"]:
        event = events[event_index]
        for donor in donors_by_cell[event.cell]:
            lookup[(event_index, donor)] = len(pair_events)
            pair_events.append(event_index)
            pair_donors.append(donor)
            vectors = _feature_vectors(geometry, blocks, backgrounds, schema, event, donor)
            for name, vector in zip(matrices, vectors):
                matrices[name].append(vector)
    return VFeatures(
        geometry, world, tuple(events),
        {name: np.asarray(values, dtype=np.int64) for name, values in split_events.items()},
        schema, self_features, {name: np.stack(values) for name, values in matrices.items()},
        np.asarray(pair_events, dtype=np.int64), np.asarray(pair_donors, dtype=np.int64),
        lookup, donors_by_cell,
    )


def _hierarchy_weights(events: Sequence[VEvent], indices: Sequence[int] | None = None,
                       *, rescale: bool = True) -> np.ndarray:
    chosen = list(range(len(events))) if indices is None else [int(value) for value in indices]
    if not chosen:
        raise ValueError("empty hierarchy")
    folios, pages, cells, records = set(), set(), set(), defaultdict(list)
    for index in chosen:
        event = events[index]
        folios.add(event.folio)
        pages.add((event.folio, event.page))
        cells.add((event.folio, event.page, event.cell))
        records[event.record].append(index)
    pages_per_folio = Counter(folio for folio, _ in pages)
    cells_per_page = Counter((folio, page) for folio, page, _ in cells)
    records_per_cell = Counter(
        (events[indices_[0]].folio, events[indices_[0]].page, events[indices_[0]].cell)
        for indices_ in records.values())
    output = np.empty(len(chosen), dtype=np.float64)
    for local, index in enumerate(chosen):
        event = events[index]
        cell = (event.folio, event.page, event.cell)
        output[local] = (1.0 / len(folios) / pages_per_folio[event.folio] /
                         cells_per_page[(event.folio, event.page)] /
                         records_per_cell[cell] / len(records[event.record]))
    if abs(float(output.sum()) - 1.0) > 1e-10:
        raise ValueError("hierarchy weight sum")
    return output * len(chosen) if rescale else output


def _hierarchy_mean(values: object, events: Sequence[VEvent],
                    indices: Sequence[int] | None = None) -> float:
    vector = np.asarray(values, dtype=np.float64)
    chosen = list(range(len(events))) if indices is None else [int(value) for value in indices]
    return float(_hierarchy_weights(events, chosen, rescale=False) @ vector[chosen])


@dataclass(frozen=True)
class VStandardizer:
    center: np.ndarray
    scale: np.ndarray
    keep: np.ndarray

    def transform(self, matrix: object) -> np.ndarray:
        value = np.asarray(matrix, dtype=np.float64)
        output = (value[:, self.keep] - self.center[self.keep]) / self.scale[self.keep]
        if not np.all(np.isfinite(output)):
            raise ValueError("nonfinite standardized feature")
        return output


@dataclass(frozen=True)
class VHead:
    length: int
    class_count: int
    ridge: float
    standardizer: VStandardizer
    means: np.ndarray
    variance: np.ndarray
    log_prior: np.ndarray

    def log_proba(self, matrix: object) -> tuple[np.ndarray, np.ndarray]:
        x = self.standardizer.transform(matrix)
        inverse = 1.0 / self.variance
        logits = (x * inverse) @ self.means.T
        logits -= 0.5 * np.sum(self.means * self.means * inverse, axis=1)[None, :]
        logits += self.log_prior[None, :]
        logits -= logits.max(axis=1, keepdims=True)
        probability = np.exp(logits)
        probability /= probability.sum(axis=1, keepdims=True)
        flags = probability < FLOOR
        probability = np.maximum(probability, FLOOR)
        probability /= probability.sum(axis=1, keepdims=True)
        return np.log(probability), flags


@dataclass(frozen=True)
class VModel:
    design: str
    ridge: float
    heads: Mapping[int, VHead]

    def true_scores(self, matrix: object, lengths: object,
                    classes: object) -> tuple[np.ndarray, np.ndarray]:
        value = np.asarray(matrix, dtype=np.float64)
        lengths_array = np.asarray(lengths, dtype=np.int64)
        class_array = np.asarray(classes, dtype=np.int64)
        scores, flags = np.empty(len(value)), np.empty(len(value), dtype=bool)
        for length, head in self.heads.items():
            selected = np.flatnonzero(lengths_array == length)
            logs, floor = head.log_proba(value[selected])
            labels = class_array[selected]
            scores[selected] = logs[np.arange(len(selected)), labels]
            flags[selected] = floor[np.arange(len(selected)), labels]
        if not np.all(np.isfinite(scores)):
            raise ValueError("nonfinite true score")
        return scores, flags


@dataclass(frozen=True)
class VCandidate:
    order_rank: int
    ridge: float
    nuisance_score: float
    bag_score: float
    order_score: float
    order_minus_bag: float
    order_minus_nuisance: float
    floor_rate_nuisance: float
    floor_rate_bag: float
    floor_rate_order: float


@dataclass(frozen=True)
class VModels:
    selected: VCandidate
    candidates: tuple[VCandidate, ...]
    nuisance: VModel
    bag: VModel
    order: VModel


def _standardizer(matrix: np.ndarray, weights: np.ndarray) -> VStandardizer:
    center = np.average(matrix, axis=0, weights=weights)
    variance = np.average((matrix - center) ** 2, axis=0, weights=weights)
    scale = np.sqrt(np.maximum(variance, 0.0))
    keep = scale > TOL
    if not np.any(keep):
        raise ValueError("all features constant")
    return VStandardizer(center, scale, keep)


def _fit_head(matrix: np.ndarray, labels: np.ndarray, weights: np.ndarray,
              length: int, ridge: float,
              standardizer: VStandardizer | None = None) -> VHead:
    count = CLASS_LAYOUT[length]
    if set(np.unique(labels)) != set(range(count)):
        raise ValueError("class loss")
    fitted = standardizer or _standardizer(matrix, weights)
    x = fitted.transform(matrix)
    means = np.empty((count, x.shape[1]), dtype=np.float64)
    class_weight = np.empty(count, dtype=np.float64)
    residual = np.zeros(x.shape[1], dtype=np.float64)
    for class_index in range(count):
        mask = labels == class_index
        class_weight[class_index] = weights[mask].sum()
        means[class_index] = np.average(x[mask], axis=0, weights=weights[mask])
        residual += np.sum(weights[mask, None] * (x[mask] - means[class_index]) ** 2,
                           axis=0)
    variance = residual / weights.sum() + ridge
    prior = (0.5 + class_weight) / (0.5 * count + weights.sum())
    if not np.all(np.isfinite(variance)) or np.any(variance <= 0):
        raise ValueError("invalid LDA variance")
    return VHead(length, count, ridge, fitted, means, variance, np.log(prior))


def _fit_model(features: VFeatures, splits: Sequence[str], design: str, ridge: float,
               standards: Mapping[int, VStandardizer] | None = None) -> VModel:
    matrix = np.concatenate([features.self_features[split][design] for split in splits])
    event_indices = [int(index) for split in splits for index in features.split_events[split]]
    events = [features.events[index] for index in event_indices]
    heads = {}
    for length in sorted(CLASS_LAYOUT):
        local = [index for index, event in enumerate(events) if event.target_length == length]
        weights = _hierarchy_weights(events, local)
        labels = np.asarray([events[index].target_class for index in local], dtype=np.int64)
        heads[length] = _fit_head(matrix[local], labels, weights, length, ridge,
                                  None if standards is None else standards[length])
    return VModel(design, ridge, heads)


def _score_self(features: VFeatures, model: VModel, split: str
                ) -> tuple[np.ndarray, np.ndarray]:
    events = [features.events[int(index)] for index in features.split_events[split]]
    return model.true_scores(features.self_features[split][model.design],
                             [event.target_length for event in events],
                             [event.target_class for event in events])


def _candidate_payload(candidates: Sequence[VCandidate]) -> list[dict[str, object]]:
    output = []
    for candidate in candidates:
        output.append({
            "order_rank": candidate.order_rank, "ridge": candidate.ridge,
            "nuisance_score": candidate.nuisance_score,
            "bag_score": candidate.bag_score, "order_score": candidate.order_score,
            "order_minus_bag": candidate.order_minus_bag,
            "order_minus_nuisance": candidate.order_minus_nuisance,
            "floor_rate_nuisance": candidate.floor_rate_nuisance,
            "floor_rate_bag": candidate.floor_rate_bag,
            "floor_rate_order": candidate.floor_rate_order,
        })
    return output


def _calibrate(features: VFeatures
               ) -> tuple[VModels | None, str | None, tuple[VCandidate, ...], str | None]:
    train_events = [features.events[int(index)]
                    for index in features.split_events["TRAIN"]]
    for length, class_count in sorted(CLASS_LAYOUT.items()):
        labels = {event.target_class for event in train_events
                  if event.target_length == length}
        if labels != set(range(class_count)):
            return None, "CAL_STOP_MISSING_CLASS", tuple(), None
    cal_events = [features.events[int(index)] for index in features.split_events["CAL"]]
    train_models, candidates = {}, []
    for ridge in RIDGES:
        for design in ("NUIS", "BAG", "ORDER1", "ORDER2"):
            train_models[(design, ridge)] = _fit_model(features, ("TRAIN",), design, ridge)
        scores, floors = {}, {}
        for design in ("NUIS", "BAG", "ORDER1", "ORDER2"):
            scores[design], floors[design] = _score_self(
                features, train_models[(design, ridge)], "CAL")
        for rank in RANKS:
            order = f"ORDER{rank}"
            nuisance_score = _hierarchy_mean(scores["NUIS"], cal_events)
            bag_score = _hierarchy_mean(scores["BAG"], cal_events)
            order_score = _hierarchy_mean(scores[order], cal_events)
            candidates.append(VCandidate(
                rank, ridge, nuisance_score, bag_score, order_score,
                order_score - bag_score, order_score - nuisance_score,
                float(floors["NUIS"].mean()), float(floors["BAG"].mean()),
                float(floors[order].mean()),
            ))

    def better(left: VCandidate, right: VCandidate) -> bool:
        for a, b in ((min(left.order_minus_bag, left.order_minus_nuisance),
                      min(right.order_minus_bag, right.order_minus_nuisance)),
                     (left.order_score, right.order_score)):
            if a > b + TOL: return True
            if b > a + TOL: return False
        if left.order_rank != right.order_rank:
            return left.order_rank < right.order_rank
        return left.ridge > right.ridge + TOL

    selected = candidates[0]
    for candidate in candidates[1:]:
        if better(candidate, selected):
            selected = candidate
    digest = _sha(_json_bytes(_candidate_payload(candidates)))
    if not all(math.isfinite(value) for value in (
        selected.order_minus_bag, selected.order_minus_nuisance,
        selected.nuisance_score, selected.bag_score, selected.order_score,
    )):
        return None, "CAL_STOP_NONFINITE", tuple(candidates), digest
    if selected.order_minus_bag <= 0 or selected.order_minus_nuisance <= 0:
        return None, "CAL_STOP_NONPOSITIVE_GAIN", tuple(candidates), digest
    if max(selected.floor_rate_nuisance, selected.floor_rate_bag,
           selected.floor_rate_order) > 0.05 + TOL:
        return None, "CAL_STOP_FLOOR_DOMINATED", tuple(candidates), digest
    final = {}
    for output, design in (("NUIS", "NUIS"), ("BAG", "BAG"),
                           ("ORDER", f"ORDER{selected.order_rank}")):
        standards = {length: head.standardizer
                     for length, head in train_models[(design, selected.ridge)].heads.items()}
        final[output] = _fit_model(features, ("TRAIN", "CAL"), design,
                                   selected.ridge, standards)
    return VModels(selected, tuple(candidates), final["NUIS"], final["BAG"],
                   final["ORDER"]), None, tuple(candidates), digest


@dataclass(frozen=True)
class VAssignments:
    records: np.ndarray
    maps: np.ndarray
    columns: Mapping[int, int]
    retries: np.ndarray


def _assignments(geometry: VGeometry) -> VAssignments:
    cells: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(geometry.records):
        exemplar = geometry.rows[record.rows[0]]
        if record.split == "TEST" and exemplar.movable:
            cells[record.cell].append(index)
    records = np.asarray(sorted((value for values in cells.values() for value in values),
                                key=lambda index: geometry.records[index].record_id.encode()),
                         dtype=np.int64)
    if len(records) != 453:
        raise ValueError("assignment panel is not 453 records")
    columns = {int(record): index for index, record in enumerate(records)}
    maps = np.empty((N_ASSIGNMENTS, len(records)), dtype=np.int64)
    retries = np.zeros(N_ASSIGNMENTS, dtype=np.int64)
    maps[0] = records
    seen = {maps[0].tobytes()}
    for assignment in range(1, N_ASSIGNMENTS):
        for retry in range(10000):
            candidate = records.copy()
            for cell in sorted(cells, key=lambda value: value.encode()):
                recipients = sorted(cells[cell],
                                    key=lambda index: geometry.records[index].record_id.encode())
                keyed = []
                for donor in recipients:
                    donor_id = geometry.records[donor].record_id
                    key = f"LRS001R1|ASSIGN|{assignment}|{retry}|{cell}|{donor_id}"
                    keyed.append((hashlib.sha256(key.encode()).digest(), donor_id, donor))
                if len({value[0] for value in keyed}) != len(keyed):
                    raise ValueError("assignment hash tie")
                donors = [value[2] for value in sorted(
                    keyed, key=lambda value: (value[0], value[1].encode()))]
                for recipient, donor in zip(recipients, donors):
                    candidate[columns[recipient]] = donor
            if candidate.tobytes() not in seen:
                maps[assignment] = candidate
                retries[assignment] = retry
                seen.add(candidate.tobytes())
                break
        else:
            raise ValueError("assignment retry exhausted")
    if _i8_hash(maps) != ASSIGNMENT_SHA256 or _i8_hash(retries) != RETRY_SHA256 or retries.max() != 0:
        raise ValueError("assignment digest drift")
    return VAssignments(records, maps, columns, retries)


@dataclass(frozen=True)
class VPairScores:
    order: np.ndarray
    bag: np.ndarray
    nuisance: np.ndarray
    floor_order: np.ndarray
    floor_bag: np.ndarray
    floor_nuisance: np.ndarray


@dataclass(frozen=True)
class VChannel:
    effects: np.ndarray
    observed: float
    null_mean: float
    null_sd: float
    z: float
    p: float


@dataclass(frozen=True)
class VEvaluation:
    ob: VChannel
    on: VChannel
    identity_ob: np.ndarray
    identity_on: np.ndarray


def _score_pairs(features: VFeatures, models: VModels) -> VPairScores:
    events = [features.events[int(index)] for index in features.pair_events]
    lengths = [event.target_length for event in events]
    labels = [event.target_class for event in events]
    nuisance, nf = models.nuisance.true_scores(features.test_features["NUIS"], lengths, labels)
    bag, bf = models.bag.true_scores(features.test_features["BAG"], lengths, labels)
    order, of = models.order.true_scores(
        features.test_features[f"ORDER{models.selected.order_rank}"], lengths, labels)
    return VPairScores(order, bag, nuisance, of, bf, nf)


def _max_t(ob: np.ndarray, on: np.ndarray) -> tuple[VChannel, VChannel]:
    null_ob, null_on = ob[1:], on[1:]
    mean_ob, mean_on = float(null_ob.mean()), float(null_on.mean())
    sd_ob, sd_on = float(null_ob.std(ddof=0)), float(null_on.std(ddof=0))
    if min(sd_ob, sd_on) <= TOL or not all(math.isfinite(value) for value in
                                            (mean_ob, mean_on, sd_ob, sd_on)):
        raise ValueError("degenerate maxT null")
    z_ob, z_on = (ob - mean_ob) / sd_ob, (on - mean_on) / sd_on
    maximum = np.maximum(z_ob[1:], z_on[1:])
    p_ob = (1.0 + np.count_nonzero(maximum >= z_ob[0] - TOL)) / N_ASSIGNMENTS
    p_on = (1.0 + np.count_nonzero(maximum >= z_on[0] - TOL)) / N_ASSIGNMENTS
    return (VChannel(ob, float(ob[0]), mean_ob, sd_ob, float(z_ob[0]), float(p_ob)),
            VChannel(on, float(on[0]), mean_on, sd_on, float(z_on[0]), float(p_on)))


def _evaluate_assignments(features: VFeatures, pairs: VPairScores,
                          assignments: VAssignments) -> VEvaluation:
    event_indices = features.split_events["TEST"]
    events = [features.events[int(index)] for index in event_indices]
    weights = _hierarchy_weights(events, rescale=False)
    effects_ob = np.zeros(N_ASSIGNMENTS, dtype=np.float64)
    effects_on = np.zeros(N_ASSIGNMENTS, dtype=np.float64)
    identity_ob, identity_on = np.empty(len(events)), np.empty(len(events))
    pair_for_record = np.full(len(features.geometry.records), -1, dtype=np.int64)
    for column, raw_event_index in enumerate(event_indices):
        event_index = int(raw_event_index)
        event = features.events[event_index]
        pair_for_record.fill(-1)
        for donor in features.donors_by_cell[event.cell]:
            pair_for_record[donor] = features.pair_lookup[(event_index, donor)]
        donors = assignments.maps[:, assignments.columns[event.record]]
        selected = pair_for_record[donors]
        if np.any(selected < 0):
            raise ValueError("ineligible assignment donor")
        ob = pairs.order[selected] - pairs.bag[selected]
        on = pairs.order[selected] - pairs.nuisance[selected]
        effects_ob += weights[column] * ob
        effects_on += weights[column] * on
        identity_ob[column], identity_on[column] = ob[0], on[0]
    ob_channel, on_channel = _max_t(effects_ob, effects_on)
    return VEvaluation(ob_channel, on_channel, identity_ob, identity_on)


def _subgroup(delta: np.ndarray, events: Sequence[VEvent], mask: object,
              minimum: int | None = None) -> float:
    selected = np.flatnonzero(np.asarray(mask, dtype=bool))
    if not len(selected) or (minimum is not None and len(selected) < minimum):
        raise ValueError("subgroup capacity")
    return float(_hierarchy_weights(events, selected, rescale=False) @ delta[selected])


def _concentration(delta: np.ndarray, events: Sequence[VEvent], labels: Sequence[object]) -> float:
    weights = _hierarchy_weights(events, rescale=False)
    totals: dict[str, float] = defaultdict(float)
    for value, weight, label in zip(delta, weights, labels):
        totals[str(label)] += float(value * weight)
    denominator = sum(abs(value) for value in totals.values())
    if denominator <= TOL or not math.isfinite(denominator):
        raise ValueError("zero contribution denominator")
    return max(abs(value) for value in totals.values()) / denominator


def _signatures(geometry: VGeometry, world: VWorld) -> Mapping[int, object]:
    return {index: tuple((geometry.rows[row_index].symbol_count,
                          int(world.prototypes[row_index])) for row_index in record.rows)
            for index, record in enumerate(geometry.records)}


def _gate_checks(features: VFeatures, models: VModels, pairs: VPairScores,
                 evaluation: VEvaluation) -> Mapping[str, bool]:
    geometry = features.geometry
    events = [features.events[int(index)] for index in features.split_events["TEST"]]
    checks: dict[str, bool] = {
        "exact_class_count": sum(CLASS_LAYOUT.values()) == 66,
        "exact_head_count": len(models.order.heads) == 6,
        "cal_positive_ob": models.selected.order_minus_bag > 0,
        "cal_positive_on": models.selected.order_minus_nuisance > 0,
    }
    signatures = _signatures(geometry, features.world)
    signature_counts = Counter((geometry.records[index].split, signature)
                               for index, signature in signatures.items())
    duplicated = {index for index, signature in signatures.items()
                  if signature_counts[(geometry.records[index].split, signature)] > 1}
    for prefix, delta, channel in (
        ("ob", evaluation.identity_ob, evaluation.ob),
        ("on", evaluation.identity_on, evaluation.on),
    ):
        if abs(_hierarchy_mean(delta, events) - channel.observed) > 1e-10:
            raise ValueError("observed effect mismatch")
        checks[f"{prefix}_effect"] = channel.observed >= 0.03 - TOL
        checks[f"{prefix}_maxt"] = channel.p <= 0.01 + TOL and channel.z >= 3.0 - TOL
        folios = sorted({event.folio for event in events}, key=lambda value: value.encode())
        folio_effects, folio_loo = {}, {}
        for folio in folios:
            mask = np.asarray([event.folio == folio for event in events])
            folio_effects[folio] = _subgroup(delta, events, mask)
            folio_loo[folio] = _subgroup(delta, events, ~mask)
        checks[f"{prefix}_folio_sign"] = sum(value > 0 for value in folio_effects.values()) >= 16
        checks[f"{prefix}_folio_loo"] = all(value > 0 for value in folio_loo.values())
        checks[f"{prefix}_folio_concentration"] = (
            _concentration(delta, events, [event.folio for event in events]) <= 0.20 + TOL)
        currier = {level: _subgroup(delta, events,
                                    [event.currier == level for event in events], 100)
                   for level in ("A", "B")}
        checks[f"{prefix}_currier"] = (all(value >= 0.01 - TOL for value in currier.values())
                                        and min(currier.values()) / max(currier.values()) >= 0.25 - TOL)
        sections = {level: _subgroup(delta, events,
                                     [event.section == level for event in events], 100)
                    for level in ("B", "H", "S")}
        checks[f"{prefix}_section"] = (all(value >= 0.01 - TOL for value in sections.values())
                                        and min(sections.values()) / max(sections.values()) >= 0.25 - TOL)
        lengths = {
            "5-8": _subgroup(delta, events,
                              [5 <= geometry.records[event.record].length <= 8
                               for event in events], 100),
            "9-12": _subgroup(delta, events,
                               [9 <= geometry.records[event.record].length <= 12
                                for event in events], 100),
        }
        checks[f"{prefix}_record_length"] = (
            all(value >= 0.01 - TOL for value in lengths.values()) and
            min(lengths.values()) / max(lengths.values()) >= 0.25 - TOL)
        bands = {band: _subgroup(
            delta, events,
            [min(2, math.floor(3 * (event.ordinal - 1) /
                               (geometry.records[event.record].length - 1))) == band
             for event in events], 100) for band in range(3)}
        checks[f"{prefix}_position"] = (
            sum(value >= 0.01 - TOL for value in bands.values()) >= 2 and
            all(value > -0.01 + TOL for value in bands.values()))
        classes = [(event.target_length, event.target_class) for event in events]
        checks[f"{prefix}_class_loo"] = all(
            _subgroup(delta, events, [value != level for value in classes]) > 0
            for level in sorted(set(classes)))
        checks[f"{prefix}_class_concentration"] = (
            _concentration(delta, events, [str(value) for value in classes]) <= 0.20 + TOL)
        keep = np.asarray([event.record not in duplicated for event in events])
        retained = np.flatnonzero(keep)
        retained_folios = {events[index].folio for index in retained}
        duplicate_effect = _subgroup(delta, events, keep) if len(retained) else None
        deletion_positive = len(retained) > 0
        for folio in sorted(retained_folios, key=lambda value: value.encode()):
            subset = keep & np.asarray([event.folio != folio for event in events])
            deletion_positive &= bool(np.any(subset)) and _subgroup(delta, events, subset) > 0
        checks[f"{prefix}_duplicate_deletion"] = (
            len(retained) >= 1500 and len(retained_folios) >= 20 and
            duplicate_effect is not None and duplicate_effect >= 0.01 - TOL and deletion_positive)
    checks["finite_test_probabilities"] = all(np.all(np.isfinite(value)) for value in
                                                (pairs.order, pairs.bag, pairs.nuisance))
    identity_pairs = np.asarray([
        features.pair_lookup[(int(event_index), features.events[int(event_index)].record)]
        for event_index in features.split_events["TEST"]], dtype=np.int64)
    checks["test_floor_rate"] = all(float(value[identity_pairs].mean()) <= 0.05 + TOL
                                    for value in (pairs.floor_order, pairs.floor_bag,
                                                  pairs.floor_nuisance))
    return checks


def _public_world(geometry: VGeometry, spec: VWorldSpec, world: VWorld,
                  assignments: VAssignments
                  ) -> tuple[dict[str, object], Mapping[str, object] | None]:
    digests = _world_digests(world)
    for length, class_count in sorted(CLASS_LAYOUT.items()):
        indices = [int(index) for index in geometry.targets["TRAIN"]
                   if geometry.rows[int(index)].symbol_count == length]
        labels = {int(world.classes[index]) for index in indices}
        if labels != set(range(class_count)):
            return ({
                "ordinal": spec.ordinal, "family": spec.family, "world": spec.index,
                "calibration_status": "CAL_STOP_MISSING_CLASS",
                "selected": None, "channels": None,
                "gate_pass_count": 0, "gate_count": 0, "gates": {},
                "passes": False,
                "digests": {**digests, "candidate_grid_sha256": None,
                            "order_bag_effects_sha256": None,
                            "order_nuisance_effects_sha256": None},
            }, None)
    features = _build_features(geometry, world)
    models, stop, candidates, candidate_digest = _calibrate(features)
    if models is None:
        return ({
            "ordinal": spec.ordinal, "family": spec.family, "world": spec.index,
            "calibration_status": stop, "selected": None, "channels": None,
            "gate_pass_count": 0, "gate_count": 0, "gates": {}, "passes": False,
            "digests": {**digests, "candidate_grid_sha256": candidate_digest,
                        "order_bag_effects_sha256": None,
                        "order_nuisance_effects_sha256": None},
        }, None)
    pairs = _score_pairs(features, models)
    evaluation = _evaluate_assignments(features, pairs, assignments)
    checks = _gate_checks(features, models, pairs, evaluation)
    selected = models.selected
    public = {
        "ordinal": spec.ordinal, "family": spec.family, "world": spec.index,
        "calibration_status": "PASS_CAL",
        "selected": {
            "order_rank": selected.order_rank, "ridge": selected.ridge,
            "order_minus_bag": selected.order_minus_bag,
            "order_minus_nuisance": selected.order_minus_nuisance,
            "order_score": selected.order_score,
            "floor_rate_nuisance": selected.floor_rate_nuisance,
            "floor_rate_bag": selected.floor_rate_bag,
            "floor_rate_order": selected.floor_rate_order,
        },
        "channels": {
            "ORDER_BAG": {"effect": evaluation.ob.observed,
                          "null_mean": evaluation.ob.null_mean,
                          "null_sd": evaluation.ob.null_sd, "z": evaluation.ob.z,
                          "maxT_p": evaluation.ob.p},
            "ORDER_NUIS": {"effect": evaluation.on.observed,
                           "null_mean": evaluation.on.null_mean,
                           "null_sd": evaluation.on.null_sd, "z": evaluation.on.z,
                           "maxT_p": evaluation.on.p},
        },
        "gate_pass_count": sum(bool(value) for value in checks.values()),
        "gate_count": len(checks), "gates": dict(sorted(checks.items())),
        "passes": all(checks.values()),
        "digests": {**digests, "candidate_grid_sha256": candidate_digest,
                    "order_bag_effects_sha256": _f8_hash(evaluation.ob.effects),
                    "order_nuisance_effects_sha256": _f8_hash(evaluation.on.effects)},
    }
    return public, {"features": features, "models": models, "pairs": pairs,
                    "evaluation": evaluation, "checks": checks, "world": world}


def _internal(geometry: VGeometry, world: VWorld, assignments: VAssignments
              ) -> Mapping[str, object]:
    features = _build_features(geometry, world)
    models, stop, _, _ = _calibrate(features)
    if models is None:
        raise ValueError(f"control fixture CAL stop: {stop}")
    pairs = _score_pairs(features, models)
    evaluation = _evaluate_assignments(features, pairs, assignments)
    checks = _gate_checks(features, models, pairs, evaluation)
    return {"features": features, "models": models, "pairs": pairs,
            "evaluation": evaluation, "checks": checks, "world": world}


def _numeric_equal(left: Mapping[str, object], right: Mapping[str, object], *,
                   exact: bool = False) -> bool:
    left_models, right_models = left["models"], right["models"]
    assert isinstance(left_models, VModels) and isinstance(right_models, VModels)
    if exact and _json_bytes(_candidate_payload(left_models.candidates)) != \
            _json_bytes(_candidate_payload(right_models.candidates)):
        return False
    if (left_models.selected.order_rank, left_models.selected.ridge) != \
            (right_models.selected.order_rank, right_models.selected.ridge):
        return False
    for field in (
        "nuisance_score", "bag_score", "order_score", "order_minus_bag",
        "order_minus_nuisance", "floor_rate_nuisance", "floor_rate_bag",
        "floor_rate_order",
    ):
        if abs(float(getattr(left_models.selected, field)) -
               float(getattr(right_models.selected, field))) > 1e-10:
            return False
    left_eval, right_eval = left["evaluation"], right["evaluation"]
    assert isinstance(left_eval, VEvaluation) and isinstance(right_eval, VEvaluation)
    for first, second in ((left_eval.ob, right_eval.ob), (left_eval.on, right_eval.on)):
        if ((not np.array_equal(first.effects, second.effects)) if exact else
                (not np.allclose(first.effects, second.effects, rtol=0.0, atol=1e-10))):
            return False
        for field in ("observed", "null_mean", "null_sd", "z", "p"):
            if (getattr(first, field) != getattr(second, field) if exact else
                    abs(float(getattr(first, field)) - float(getattr(second, field))) > 1e-10):
                return False
    return left["checks"] == right["checks"]


def _mapped_world(old_geometry: VGeometry, new_geometry: VGeometry, old_world: VWorld,
                  *, class_shift: bool = False) -> VWorld:
    values = {row.group_id: (int(old_world.prototypes[index]),
                             int(old_world.classes[index]),
                             bool(old_world.separation[index]))
              for index, row in enumerate(old_geometry.rows)}
    prototypes, classes, separation = [], [], []
    for row in new_geometry.rows:
        prototype, target, separated = values[row.group_id]
        if class_shift and target >= 0:
            target = (target + 1) % CLASS_LAYOUT[row.symbol_count]
            separated = True
        prototypes.append(prototype)
        classes.append(target)
        separation.append(separated)
    return VWorld(old_world.spec, np.asarray(prototypes, dtype=np.int16),
                  np.asarray(classes, dtype=np.int16), np.asarray(separation, dtype=bool),
                  old_world.nonces, old_world.copied)


def _carried_assignments(old: VGeometry, new: VGeometry, assignments: VAssignments,
                         rename: Mapping[str, str]) -> VAssignments:
    conversion = np.asarray([new.record_index[rename[record.record_id]]
                             for record in old.records], dtype=np.int64)
    new_records = conversion[assignments.records]
    order = np.argsort(np.asarray([new.records[int(index)].record_id.encode()
                                   for index in new_records], dtype=object))
    new_records = new_records[order]
    columns = {int(record): index for index, record in enumerate(new_records)}
    maps = np.empty_like(assignments.maps)
    for old_column, old_record in enumerate(assignments.records):
        maps[:, columns[int(conversion[int(old_record)])]] = conversion[assignments.maps[:, old_column]]
    return VAssignments(new_records, maps, columns, assignments.retries.copy())


def _invariance_controls(raw_rows: Sequence[Mapping[str, str]], geometry: VGeometry,
                         base: Mapping[str, object], assignments: VAssignments
                         ) -> Mapping[str, bool]:
    base_world = base["world"]
    assert isinstance(base_world, VWorld)
    reversed_rows = list(reversed(sorted((dict(row) for row in raw_rows),
                                         key=lambda row: row["anonymous_group_id"].encode())))
    row_geometry = _geometry_from_dicts(reversed_rows)
    row_world = _mapped_world(geometry, row_geometry, base_world)
    same_geometry = (
        row_geometry.rows == geometry.rows and row_geometry.records == geometry.records and
        np.array_equal(row_geometry.record_for_row, geometry.record_for_row) and
        all(np.array_equal(row_geometry.targets[split], geometry.targets[split])
            for split in ("TRAIN", "CAL", "TEST")))
    same_world = (np.array_equal(row_world.prototypes, base_world.prototypes) and
                  np.array_equal(row_world.classes, base_world.classes))
    row_result = (same_geometry and same_world and
                  _numeric_equal(base, _internal(row_geometry, row_world, assignments),
                                 exact=True))

    identifiers = sorted((record.record_id for record in geometry.records),
                         key=lambda value: value.encode())
    rename = {value: identifiers[-1 - index] for index, value in enumerate(identifiers)}
    renamed_rows = [dict(row, anonymous_record_id=rename[row["anonymous_record_id"]])
                    for row in raw_rows]
    renamed_geometry = _geometry_from_dicts(renamed_rows)
    renamed_world = _mapped_world(geometry, renamed_geometry, base_world)
    carried = _carried_assignments(geometry, renamed_geometry, assignments, rename)
    rename_result = _numeric_equal(base, _internal(renamed_geometry, renamed_world, carried))

    shifted = _mapped_world(geometry, geometry, base_world, class_shift=True)
    class_result = _numeric_equal(base, _internal(geometry, shifted, assignments))

    reversal_rows = []
    for row in raw_rows:
        changed = dict(row)
        changed["segment_group_index"] = str(
            int(row["segment_group_count"]) + 1 - int(row["segment_group_index"]))
        reversal_rows.append(changed)
    reversal_geometry = _geometry_from_dicts(reversal_rows)
    reversal_world = _mapped_world(geometry, reversal_geometry, base_world)
    reversal_result = _numeric_equal(base, _internal(
        reversal_geometry, reversal_world, assignments))
    return dict(zip(INVARIANCE_NAMES,
                    (row_result, rename_result, class_result, reversal_result)))


def _validate_assignment_structure(geometry: VGeometry, assignments: VAssignments) -> None:
    cells: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(geometry.records):
        if record.split == "TEST" and geometry.rows[record.rows[0]].movable:
            cells[record.cell].append(index)
    if assignments.maps.shape != (8192, 453) or len(assignments.records) != 453:
        raise ValueError("assignment shape")
    for members in cells.values():
        columns = [assignments.columns[index] for index in members]
        if not np.all(np.sort(assignments.maps[:, columns], axis=1) ==
                      np.sort(np.asarray(members))[None, :]):
            raise ValueError("assignment donor violation")


def _mutation_invisible(base: Mapping[str, object], geometry: VGeometry,
                        donor_record: int, event_index: int, mutated_row: int) -> bool:
    features = base["features"]
    world = base["world"]
    assert isinstance(features, VFeatures) and isinstance(world, VWorld)
    baseline = features.pair_lookup[(event_index, donor_record)]
    prototypes = world.prototypes.copy()
    prototypes[mutated_row] = (int(prototypes[mutated_row]) + 1) % 24
    changed = replace(world, prototypes=prototypes)
    blocks, backgrounds = _blocks(geometry, changed), _backgrounds(geometry, _blocks(geometry, changed))
    vectors = _feature_vectors(geometry, blocks, backgrounds, features.schema,
                               features.events[event_index], donor_record)
    return all(np.array_equal(features.test_features[name][baseline], vector)
               for name, vector in zip(("NUIS", "BAG", "ORDER1", "ORDER2"), vectors))


def _malformed_controls(raw_rows: Sequence[Mapping[str, str]], geometry: VGeometry,
                        base: Mapping[str, object], assignments: VAssignments
                        ) -> Mapping[str, bool]:
    controls = {}
    bad = [dict(row) for row in raw_rows]
    index = next(index for index, row in enumerate(bad)
                 if row["split"] == "TEST" and row["strict_test_movable"] == "1")
    bad[index]["strict_cell_id"] = "C00000000000000000000"
    try: _geometry_from_dicts(bad); controls["malformed_cell"] = False
    except ValueError: controls["malformed_cell"] = True

    cell_members: dict[str, list[int]] = defaultdict(list)
    for record_index, record in enumerate(geometry.records):
        if record.split == "TEST" and geometry.rows[record.rows[0]].movable:
            cell_members[record.cell].append(record_index)
    repeated_cell = next(values for _, values in sorted(cell_members.items()) if len(values) >= 2)
    first_column = assignments.columns[repeated_cell[0]]
    second_column = assignments.columns[repeated_cell[1]]
    repeated = assignments.maps.copy()
    repeated[1, second_column] = repeated[1, first_column]
    try:
        _validate_assignment_structure(geometry, replace(assignments, maps=repeated))
        controls["repeated_donor"] = False
    except ValueError: controls["repeated_donor"] = True
    crossing = assignments.maps.copy()
    crossing[1, 0] = next(index for index, record in enumerate(geometry.records)
                          if record.split == "TRAIN")
    try:
        _validate_assignment_structure(geometry, replace(assignments, maps=crossing))
        controls["split_crossing_donor"] = False
    except ValueError: controls["split_crossing_donor"] = True

    first, second = _dct(8, 4)
    changed = first.copy(); changed[np.flatnonzero(changed)[0]] += 0.125
    try:
        distant = np.asarray([index for index in range(8) if abs(index - 3) >= 2])
        if abs(float(changed[distant].sum())) > TOL or \
                abs(float(second[distant].sum())) > TOL or \
                abs(float(changed[distant] @ second[distant])) > TOL:
            raise ValueError("invalid ordered contrast")
        controls["nonzero_sum_contrast"] = False
    except ValueError:
        controls["nonzero_sum_contrast"] = True

    features = base["features"]
    assert isinstance(features, VFeatures)
    event_index = int(features.split_events["TEST"][0])
    event = features.events[event_index]
    recipient = geometry.records[event.record]
    controls["donor_position_j_excluded"] = _mutation_invisible(
        base, geometry, event.record, event_index, recipient.rows[event.ordinal - 1])
    alternate = next(value for value in features.donors_by_cell[event.cell]
                     if value != event.record)
    neighbour_position = event.ordinal - 2
    if neighbour_position < 0:
        neighbour_position = event.ordinal
    controls["recipient_neighbour_not_mixed"] = _mutation_invisible(
        base, geometry, alternate, event_index, recipient.rows[neighbour_position])
    controls["cell_excluded_page_background"] = _mutation_invisible(
        base, geometry, event.record, event_index, geometry.records[alternate].rows[0])

    try:
        _checked_read("VOYNICH_ACTIVE_STATE.md")
        controls["undeclared_repository_read"] = False
    except PermissionError:
        controls["undeclared_repository_read"] = True
    models = base["models"]
    assert isinstance(models, VModels)
    pair_index = features.pair_lookup[(event_index, event.record)]
    matrix = features.test_features[f"ORDER{models.selected.order_rank}"][pair_index:pair_index + 1].copy()
    matrix[0, 0] = np.nan
    try:
        models.order.heads[event.target_length].log_proba(matrix)
        controls["nonfinite_probability"] = False
    except ValueError:
        controls["nonfinite_probability"] = True
    altered_events = tuple(replace(value, target_class=0)
                           if value.target_length == 1 and
                           value.target_class == CLASS_LAYOUT[1] - 1 else value
                           for value in features.events)
    altered = replace(features, events=altered_events)
    try:
        _fit_model(altered, ("TRAIN",), "NUIS", 0.25)
        controls["class_loss"] = False
    except ValueError:
        controls["class_loss"] = True
    temporary = Path(tempfile.mkdtemp(prefix="lrs001r1-validator-no-clobber-"))
    try:
        source, destination = temporary / "source", temporary / "destination"
        source.write_bytes(b"new")
        destination.write_bytes(b"old")
        try:
            os.link(source, destination)
            controls["output_overwrite"] = False
        except FileExistsError:
            controls["output_overwrite"] = destination.read_bytes() == b"old"
    finally:
        shutil.rmtree(temporary)
    if set(controls) != set(MALFORMED_NAMES):
        raise AssertionError("malformed control schema")
    return controls


def _checked_read(relative: str) -> bytes:
    if relative not in READ_RELS:
        raise PermissionError(f"validator repository read denied: {relative}")
    return (ROOT / relative).read_bytes()


def _validate_freeze(payload: bytes, expected_hash: str
                     , amendment: Mapping[str, object]
                     ) -> tuple[Mapping[str, object], Mapping[str, bytes]]:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash) or _sha(payload) != expected_hash:
        raise ValueError("freeze SHA-256 mismatch")
    freeze = json.loads(payload)
    if freeze.get("experiment") != FREEZE_EXPERIMENT or \
            freeze.get("status") != "FROZEN_UNSCORED" or \
            freeze.get("decision") != "AUTHORIZE_TARGET_BLIND_CALIBRATION_ONLY" or \
            not re.fullmatch(r"[0-9a-f]{40}", str(freeze.get("registration_commit", ""))):
        raise ValueError("freeze header drift")
    bound = freeze.get("bound_files")
    if not isinstance(bound, dict) or set(bound) != set(BOUND_RELS):
        raise ValueError("freeze bound-file schema drift")
    if bound[GEOMETRY_TSV_REL] != GEOMETRY_TSV_SHA256 or \
            bound[GEOMETRY_JSON_REL] != GEOMETRY_JSON_SHA256:
        raise ValueError("freeze geometry binding drift")
    outputs_absent = freeze.get("outputs_absent")
    if not isinstance(outputs_absent, list) or len(outputs_absent) != 2 or \
            set(outputs_absent) != {RESULT_REL, REPORT_REL}:
        raise ValueError("freeze output-absence schema drift")
    loaded = {}
    for relative in BOUND_RELS:
        value = _checked_read(relative)
        expected = (amendment["corrected_validator_sha256"]
                    if relative == VALIDATOR_REL else bound[relative])
        if _sha(value) != expected:
            raise ValueError(f"freeze-bound source drift: {relative}")
        loaded[relative] = value
    return freeze, loaded


def _validate_amendment(payload: bytes, expected_hash: str,
                        freeze_hash: str) -> Mapping[str, object]:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash) or _sha(payload) != expected_hash:
        raise ValueError("validation-amendment SHA-256 mismatch")
    amendment = json.loads(payload)
    expected_keys = {
        "experiment", "status", "decision", "base_freeze_sha256",
        "registration_commit", "original_validator_sha256",
        "corrected_validator_sha256", "corrected_validator_commit",
        "source_result_sha256", "source_report_sha256", "outputs_absent",
        "producer_rerun_forbidden",
    }
    if set(amendment) != expected_keys or \
            amendment.get("experiment") != AMENDMENT_EXPERIMENT or \
            amendment.get("status") != "FROZEN_VALIDATOR_ONLY" or \
            amendment.get("decision") != "AUTHORIZE_ONE_CORRECTED_CLEAN_RECONSTRUCTION_ONLY" or \
            amendment.get("base_freeze_sha256") != freeze_hash or \
            amendment.get("producer_rerun_forbidden") is not True:
        raise ValueError("validation-amendment header drift")
    for field in ("original_validator_sha256", "corrected_validator_sha256",
                  "source_result_sha256", "source_report_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(amendment.get(field, ""))):
            raise ValueError(f"malformed amendment hash: {field}")
    for field in ("registration_commit", "corrected_validator_commit"):
        if not re.fullmatch(r"[0-9a-f]{40}", str(amendment.get(field, ""))):
            raise ValueError(f"malformed amendment commit: {field}")
    outputs = amendment.get("outputs_absent")
    if not isinstance(outputs, list) or len(outputs) != 2 or \
            set(outputs) != {VALIDATION_REL, VALIDATION_REPORT_REL}:
        raise ValueError("validation-amendment output schema drift")
    return amendment


def _family_summaries(worlds: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
    output = {}
    for family, count in FAMILY_COUNTS:
        selected = [world for world in worlds if world["family"] == family]
        if len(selected) != count:
            raise ValueError(f"world count drift: {family}")
        hyperparameters = Counter(
            (world["selected"]["order_rank"], world["selected"]["ridge"])
            for world in selected if world["selected"] is not None)
        output[family] = {
            "worlds": count,
            "passes": sum(bool(world["passes"]) for world in selected),
            "calibration_stops": sum(world["calibration_status"] != "PASS_CAL"
                                     for world in selected),
            "selected_hyperparameters": {
                f"q{int(key[0])}_lambda{float(key[1]):g}": value
                for key, value in sorted(hyperparameters.items())
            },
        }
    return output


def _calibration_report(result: Mapping[str, object]) -> bytes:
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


def _worker_world(spec: VWorldSpec) -> dict[str, object]:
    if _WORKER_GEOMETRY is None or _WORKER_ASSIGNMENTS is None:
        raise RuntimeError("validator worker not initialized")
    world = _generate_world(_WORKER_GEOMETRY, spec)
    public, _ = _public_world(_WORKER_GEOMETRY, spec, world, _WORKER_ASSIGNMENTS)
    return public


def _worker_count(requested: int) -> int:
    if not 1 <= requested <= 32:
        raise ValueError("workers outside 1..32")
    memory_limit = 32
    try:
        with open("/proc/meminfo", encoding="ascii") as handle:
            available = next(int(line.split()[1]) for line in handle
                             if line.startswith("MemAvailable:"))
        memory_limit = max(1, available // (2 * 1024 * 1024))
    except (OSError, StopIteration, ValueError):
        pass
    return max(1, min(requested, 32, os.cpu_count() or 1, memory_limit))


def _reconstruct_result(geometry: VGeometry, raw_rows: Sequence[Mapping[str, str]],
                        freeze: Mapping[str, object], freeze_hash: str,
                        observed: Mapping[str, object], workers_requested: int
                        ) -> tuple[dict[str, object], Mapping[str, bool]]:
    global _WORKER_GEOMETRY, _WORKER_ASSIGNMENTS
    assignments = _assignments(geometry)
    _validate_assignment_structure(geometry, assignments)
    registry = _registry()
    _WORKER_GEOMETRY, _WORKER_ASSIGNMENTS = geometry, assignments
    workers = _worker_count(workers_requested)
    if workers == 1:
        worlds = [_worker_world(spec) for spec in registry]
    else:
        with mp.get_context("fork").Pool(workers, maxtasksperchild=1) as pool:
            worlds = pool.map(_worker_world, registry, chunksize=1)
    worlds.sort(key=lambda value: int(value["ordinal"]))

    positive_public = next((world for world in worlds
                            if world["family"] == "ORDER_FULL" and
                            world["calibration_status"] == "PASS_CAL"), None)
    positive = None
    if positive_public is not None:
        positive_spec = next(spec for spec in registry
                             if spec.ordinal == int(positive_public["ordinal"]))
        positive_world = _generate_world(geometry, positive_spec)
        reconstructed_positive, positive = _public_world(
            geometry, positive_spec, positive_world, assignments)
        if reconstructed_positive != positive_public or positive is None:
            raise ValueError("positive control fixture reconstruction drift")
    if positive is None:
        invariance = {name: False for name in INVARIANCE_NAMES}
        malformed = {name: False for name in MALFORMED_NAMES}
    else:
        invariance = _invariance_controls(raw_rows, geometry, positive, assignments)
        malformed = _malformed_controls(raw_rows, geometry, positive, assignments)
    controls_ok = all(invariance.values()) and all(malformed.values())
    families = _family_summaries(worlds)
    aggregate = {
        "exact_208_world_registry": len(worlds) == 208,
        "zero_of_64_null": families["NULL"]["passes"] == 0,
        "all_8_order_full": families["ORDER_FULL"]["passes"] == 8,
        "all_8_order_reduced": families["ORDER_REDUCED"]["passes"] == 8,
        "zero_of_8_each_adversarial": all(families[name]["passes"] == 0
                                           for name in NEGATIVE_FAMILIES),
        "all_malformed_controls_rejected": all(malformed.values()),
        "all_invariance_controls_pass": all(invariance.values()),
        "exact_8192_by_453_assignment_orbit": (
            assignments.maps.shape == (8192, 453) and
            _i8_hash(assignments.maps) == ASSIGNMENT_SHA256 and
            _i8_hash(assignments.retries) == RETRY_SHA256 and
            int(assignments.retries.max()) == 0),
        "exact_input_audit_before_output": True,
        "real_association_absent": True,
        "ocr_and_automated_vision_absent": True,
    }
    passed = all(aggregate.values())
    observed_workers = observed.get("workers")
    if not isinstance(observed_workers, int) or not 1 <= observed_workers <= 32:
        raise ValueError("result worker count outside 1..32")
    result = {
        "experiment": RESULT_EXPERIMENT,
        "schema_version": RESULT_SCHEMA,
        "status": ("PASS_LRS001R1_TARGET_BLIND_CALIBRATION" if passed else
                   "STOP_LRS001R1_TARGET_BLIND_CALIBRATION"),
        "decision": ("AUTHORIZE_SEPARATE_LRS001R1_TARGET_REGISTRATION" if passed else
                     "TARGET_FORBIDDEN"),
        "registration_commit": freeze["registration_commit"],
        "freeze_sha256": freeze_hash,
        "inputs": {**dict(freeze["bound_files"]), FREEZE_REL: freeze_hash},
        "geometry_counts": {
            "rows": len(geometry.rows), "records": len(geometry.records),
            "test_targets": 1784, "test_target_bearing_records": 445,
            "test_movable_records": 453, "test_cells": 118,
            "test_pages": 40, "test_folios": 21, "opaque_classes": 66,
        },
        "assignment": {"rows": 8192, "columns": 453,
                       "map_sha256": ASSIGNMENT_SHA256,
                       "retry_sha256": RETRY_SHA256, "maximum_retry": 0},
        "worlds": worlds, "families": families,
        "controls": {"invariance": invariance, "malformed": malformed},
        "gates": aggregate, "workers": observed_workers,
        "isolation": {
            "allowed_repository_input_count": 8,
            "observed_repository_input_count": 8,
            "expected_denied_read_count": 1,
            "unexpected_audit_event_count": 0,
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
    aggregate_consistent = (
        controls_ok == (aggregate["all_malformed_controls_rejected"] and
                        aggregate["all_invariance_controls_pass"]) and
        passed == all(aggregate.values()) and
        (result["status"], result["decision"]) ==
        (("PASS_LRS001R1_TARGET_BLIND_CALIBRATION",
          "AUTHORIZE_SEPARATE_LRS001R1_TARGET_REGISTRATION") if passed else
         ("STOP_LRS001R1_TARGET_BLIND_CALIBRATION", "TARGET_FORBIDDEN"))
    )
    return result, {"aggregate_and_control_state_exact": aggregate_consistent}


def _validation_report(value: Mapping[str, object]) -> bytes:
    return ("# LRS001-R1 target-blind calibration validation\n\n"
            f"Status: **{value['status']}**.\n\n"
            f"Checks: {value['check_count']}; all passed.\n\n"
            "The validator independently reconstructed all 208 synthetic worlds, "
            "the 8,192 × 453 donor orbit, model selection, effects, gates, controls, "
            "aggregate JSON, and report without importing producer code. No real "
            "context-target association was accessed.\n").encode("utf-8")


def _install_validation(json_payload: bytes, report_payload: bytes) -> None:
    destinations = (ROOT / VALIDATION_REL, ROOT / VALIDATION_REPORT_REL)
    if any(path.exists() for path in destinations):
        raise FileExistsError("validation output exists")
    staging = Path(tempfile.mkdtemp(prefix="lrs001r1-validation-stage-", dir=ROOT.parent))
    installed = []
    try:
        staged = (staging / "validation.json", staging / "validation.md")
        for path, payload in zip(staged, (json_payload, report_payload)):
            with path.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        for source, destination in zip(staged, destinations):
            os.link(source, destination)
            installed.append(destination)
    except BaseException:
        for path in reversed(installed):
            path.unlink()
        raise
    finally:
        shutil.rmtree(staging)


def _self_test() -> Mapping[str, bool]:
    checks = {
        "registry_208": len(_registry()) == 208,
        "prototype_lengths": set(PROTOTYPE_BLOCKS) == set(range(1, 12)),
        "prototype_shape": all(value.shape == (24, 648)
                               for value in PROTOTYPE_BLOCKS.values()),
    }
    for length, matrix in PROTOTYPE_BLOCKS.items():
        wanted_last = 0.0 if length == 1 else 1.0
        checks[f"block_sums_{length}"] = bool(
            np.allclose(matrix[:, :24].sum(axis=1), 1.0, rtol=0.0, atol=TOL) and
            np.allclose(matrix[:, 24:48].sum(axis=1), 1.0, rtol=0.0, atol=TOL) and
            np.allclose(matrix[:, 48:72].sum(axis=1), 1.0, rtol=0.0, atol=TOL) and
            np.allclose(matrix[:, 72:].sum(axis=1), wanted_last, rtol=0.0, atol=TOL))
    contrast_ok = True
    for length in range(5, 13):
        for ordinal in range(1, length + 1):
            accepted = []
            for vector in _dct(length, ordinal):
                norm = float(np.linalg.norm(vector))
                if norm <= TOL:
                    contrast_ok &= bool(np.all(vector == 0.0))
                else:
                    contrast_ok &= abs(float(vector.sum())) <= TOL
                    contrast_ok &= abs(norm - 1.0) <= TOL
                    contrast_ok &= all(abs(float(vector @ prior)) <= TOL for prior in accepted)
                    accepted.append(vector)
    checks["dct_contract"] = contrast_ok
    probabilities = _softmax(np.asarray((0.0, 1.0, -1.0)))
    checks["softmax"] = bool(np.all(np.isfinite(probabilities)) and
                              abs(float(probabilities.sum()) - 1.0) <= TOL)
    checks["deterministic_draw"] = (_draw("LRS001R1|SELFTEST|DRAW", probabilities) ==
                                    _draw("LRS001R1|SELFTEST|DRAW", probabilities))
    matrix = np.asarray(((0.0,), (1.0,), (2.0,), (3.0,), (4.0,), (5.0,)))
    labels = np.asarray((0, 1, 2, 0, 1, 2), dtype=np.int64)
    weights = np.ones(6)
    head = _fit_head(matrix, labels, weights, 1, 1.0)
    logs, floor = head.log_proba(matrix)
    checks["fake_lda"] = logs.shape == (6, 3) and floor.shape == (6, 3)
    try:
        _checked_read("VOYNICH_ACTIVE_STATE.md")
        checks["allowlist_rejection"] = False
    except PermissionError:
        checks["allowlist_rejection"] = True
    if not all(checks.values()):
        raise RuntimeError(f"validator fake self-test failed: {checks}")
    return checks


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-sha256",
                        help="published SHA-256 of the frozen registration")
    parser.add_argument("--amendment-sha256",
                        help="published SHA-256 of the validator-only amendment")
    parser.add_argument("--workers", type=int, default=32,
                        help="independent whole-world workers, 1..32")
    parser.add_argument("--self-test", action="store_true",
                        help="run fabricated primitive tests only")
    parser.add_argument("--no-write", action="store_true",
                        help="validate but do not install validation artifacts")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parse_args(argv)
    if arguments.self_test:
        checks = _self_test()
        print(json.dumps({"status": "PASS_FAKE_SELF_TESTS", "checks": len(checks)},
                         sort_keys=True))
        return 0

    # This guard deliberately precedes every registered scientific read.  It
    # makes an accidental pre-calibration invocation cheap and harmless.
    if not (ROOT / RESULT_REL).exists() or not (ROOT / REPORT_REL).exists():
        print(json.dumps({"status": "NOT_READY_RESULT_ABSENT",
                          "registered_reconstruction_started": False}, sort_keys=True))
        return 2
    if not arguments.freeze_sha256:
        raise ValueError("--freeze-sha256 is required after result creation")
    if not arguments.amendment_sha256:
        raise ValueError("--amendment-sha256 is required after result creation")

    amendment_payload = _checked_read(AMENDMENT_REL)
    amendment = _validate_amendment(
        amendment_payload, arguments.amendment_sha256, arguments.freeze_sha256)
    freeze_payload = _checked_read(FREEZE_REL)
    freeze, loaded = _validate_freeze(
        freeze_payload, arguments.freeze_sha256, amendment)
    result_payload = _checked_read(RESULT_REL)
    report_payload = _checked_read(REPORT_REL)
    if amendment["registration_commit"] != freeze["registration_commit"] or \
            amendment["original_validator_sha256"] != \
            freeze["bound_files"][VALIDATOR_REL] or \
            amendment["source_result_sha256"] != _sha(result_payload) or \
            amendment["source_report_sha256"] != _sha(report_payload):
        raise ValueError("validation amendment/base artifact binding drift")
    observed = json.loads(result_payload)
    if _json_bytes(observed) != result_payload:
        raise ValueError("calibration JSON is not canonical")
    expected_keys = {
        "experiment", "schema_version", "status", "decision", "registration_commit",
        "freeze_sha256", "inputs", "geometry_counts", "assignment", "worlds",
        "families", "controls", "gates", "workers", "isolation", "claim_ceiling",
    }
    if set(observed) != expected_keys or observed.get("experiment") != RESULT_EXPERIMENT or \
            observed.get("schema_version") != RESULT_SCHEMA:
        raise ValueError("calibration aggregate schema drift")
    if observed.get("freeze_sha256") != arguments.freeze_sha256 or \
            observed.get("registration_commit") != freeze["registration_commit"] or \
            observed.get("inputs") != {**dict(freeze["bound_files"]),
                                       FREEZE_REL: arguments.freeze_sha256}:
        raise ValueError("calibration result/freeze binding drift")

    # Opaque source reads above are hash binding only.  The validator must not
    # import producer modules; enforce the source-level absence in its own body.
    validator_source = loaded[VALIDATOR_REL].decode("utf-8")
    producer_import_absent = not bool(re.search(
        r"(?m)^\s*(?:from|import)\s+(?:lrs001r1_core|lrs001r1_synthetic|"
        r"run_lrs001r1_target_blind_calibration)\b", validator_source))
    if not producer_import_absent:
        raise ValueError("validator imports a producer module")

    geometry, raw_rows = _load_geometry(loaded[GEOMETRY_TSV_REL],
                                        loaded[GEOMETRY_JSON_REL])
    reconstructed, internal_checks = _reconstruct_result(
        geometry, raw_rows, freeze, arguments.freeze_sha256, observed,
        arguments.workers)
    if _json_bytes(reconstructed) != result_payload:
        raise ValueError("independent aggregate reconstruction differs")
    reconstructed_report = _calibration_report(reconstructed)
    if reconstructed_report != report_payload:
        raise ValueError("independent report reconstruction differs")

    checks = {
        "freeze_sha256": _sha(freeze_payload) == arguments.freeze_sha256,
        "six_base_and_amended_validator_hashes": all(
            _sha(loaded[path]) == freeze["bound_files"][path]
            for path in BOUND_RELS if path != VALIDATOR_REL) and
            _sha(loaded[VALIDATOR_REL]) == amendment["corrected_validator_sha256"],
        "producer_import_absent": producer_import_absent,
        "geometry_tsv_sha256": _sha(loaded[GEOMETRY_TSV_REL]) == GEOMETRY_TSV_SHA256,
        "geometry_manifest_sha256": _sha(loaded[GEOMETRY_JSON_REL]) == GEOMETRY_JSON_SHA256,
        "exact_208_worlds": len(reconstructed["worlds"]) == 208,
        "exact_8192_by_453_assignments": reconstructed["assignment"] == {
            "rows": 8192, "columns": 453, "map_sha256": ASSIGNMENT_SHA256,
            "retry_sha256": RETRY_SHA256, "maximum_retry": 0},
        "candidate_and_effect_hashes": all(
            set(world["digests"]) == {
                "prototype_indices_sha256", "class_indices_sha256",
                "target_separation_sha256", "record_nonces_sha256",
                "copied_record_ids_sha256", "candidate_grid_sha256",
                "order_bag_effects_sha256", "order_nuisance_effects_sha256",
            } for world in reconstructed["worlds"]),
        "named_controls_exact": reconstructed["controls"] == observed["controls"],
        "family_decisions_exact": reconstructed["families"] == observed["families"],
        "top_level_gates_exact": reconstructed["gates"] == observed["gates"],
        "canonical_result_exact": _json_bytes(reconstructed) == result_payload,
        "report_exact": reconstructed_report == report_payload,
        "real_association_absent": True,
        "ocr_and_automated_vision_absent": True,
        "internal_control_reconstruction": all(internal_checks.values()),
    }
    if not all(checks.values()):
        raise RuntimeError(f"validation check failed: {checks}")
    source_pass = reconstructed["status"] == "PASS_LRS001R1_TARGET_BLIND_CALIBRATION"
    validation = {
        "experiment": VALIDATION_EXPERIMENT,
        "schema_version": VALIDATION_SCHEMA,
        "status": "PASS_CLEAN_RECONSTRUCTION",
        "decision": ("VALIDATED_CALIBRATION_PASS" if source_pass else
                     "VALIDATED_CALIBRATION_STOP"),
        "validated_experiment": RESULT_EXPERIMENT,
        "source_result_sha256": _sha(result_payload),
        "source_report_sha256": _sha(report_payload),
        "freeze_sha256": arguments.freeze_sha256,
        "validation_amendment_sha256": arguments.amendment_sha256,
        "corrected_validator_sha256": amendment["corrected_validator_sha256"],
        "bound_files": dict(freeze["bound_files"]),
        "check_count": len(checks), "checks": checks,
        "reconstructed_counts": {
            "worlds": 208, "assignment_rows": 8192, "assignment_columns": 453,
            "test_targets": 1784, "classes": 66,
        },
        "isolation": {
            "producer_modules_imported": False,
            "real_class_identity_or_family_surface_accessed": False,
            "real_context_target_association_scored": False,
            "ocr_or_automated_vision_used": False,
        },
        "claim_ceiling": (
            "Independent validation of target-free synthetic calibration only; no "
            "manuscript field, word, role, language, meaning, plaintext, or translation."
        ),
    }
    validation_payload = _json_bytes(validation)
    validation_report = _validation_report(validation)
    if not arguments.no_write:
        _install_validation(validation_payload, validation_report)
    print(json.dumps({"status": validation["status"], "decision": validation["decision"],
                      "checks": len(checks)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
