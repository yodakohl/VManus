#!/usr/bin/env python3
"""Target-blind LRS001-R1 calibration primitives.

This module deliberately knows only the pseudonymous geometry contract and
synthetic prototype/class data supplied by a runner.  It must never import a
transcription, family surface, source-native class map, or capacity artifact.

The public API is intentionally functional: load/validate geometry, construct
the frozen synthetic representation, build predictor matrices, calibrate and
refit the six diagonal-LDA heads, enumerate whole-record assignments, score the
TEST panel, and evaluate the preregistered maxT/gate battery.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

# Keep numerical kernels deterministic and prevent nested BLAS oversubscription.
for _name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

import numpy as np


ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ"
ALPHABET_SIZE = len(ALPHABET)
BLOCK_DIM = 24 + 24 + 24 + 24 * 24
CLASS_LAYOUT = {1: 3, 2: 8, 3: 23, 4: 19, 5: 10, 6: 3}
CONTEXT_LENGTHS = tuple(range(1, 12))
RIDGES = (0.25, 1.0, 4.0, 16.0)
ORDER_RANKS = (1, 2)
PROBABILITY_FLOOR = 1.0e-6
TOL = 1.0e-12
N_ASSIGNMENTS = 8192
SEPARATION_FAMILIES = frozenset(
    {"ONE_SURFACE", "ONE_POSITION", "RANDOM_DONOR", "REVERSED_MAPPING"}
)

GEOMETRY_FIELDS = (
    "anonymous_group_id", "anonymous_record_id", "split", "page",
    "physical_folio", "section", "currier", "hand", "code", "kind",
    "segment_group_count", "segment_group_index", "segment_position",
    "segment_count", "segment_index", "starts_after_drawing",
    "ends_before_drawing", "original_group_count", "symbol_count",
    "supported_class_target", "strict_test_movable", "strict_cell_id",
    "strict_cell_record_count",
)

CATEGORICAL_FIELDS = (
    "currier", "section", "hand", "code", "record_length", "target_ordinal",
    "segment_count", "segment_index", "starts_after_drawing",
    "ends_before_drawing", "original_group_count", "target_symbol_count",
)

EXPECTED_GEOMETRY_COUNTS = {
    "targets": 1784,
    "records": 445,
    "cells": 118,
    "pages": 40,
    "folios": 21,
}
EXPECTED_GEOMETRY_TSV_SHA256 = "37f06364effab97140d50fd64984ee561ed84f9087866314db7fec4f059647df"
EXPECTED_GEOMETRY_MANIFEST_SHA256 = "0c251db4526f54a1b3bec15528f32a95c782d3a7d8f134ab49b6afb872bd1542"

_INT_FIELDS = {
    "segment_group_count", "segment_group_index", "segment_count",
    "segment_index", "starts_after_drawing", "ends_before_drawing",
    "original_group_count", "symbol_count", "supported_class_target",
    "strict_test_movable", "strict_cell_record_count",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


def uniform01(key: str) -> float:
    """Frozen SHA-256 U(key), with little-endian first eight digest bytes."""
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return (int.from_bytes(digest[:8], "little") + 0.5) / 2**64


def categorical_sample(key: str, probabilities: Sequence[float]) -> int:
    values = np.asarray(probabilities, dtype=np.float64)
    if values.ndim != 1 or len(values) == 0 or not np.all(np.isfinite(values)):
        raise ValueError("invalid categorical probabilities")
    if np.any(values < 0.0) or abs(float(values.sum()) - 1.0) > TOL:
        raise ValueError("categorical probabilities must be nonnegative and sum to one")
    u = uniform01(key)
    cumulative = 0.0
    for index, probability in enumerate(values):
        cumulative += float(probability)
        if cumulative >= u:
            return index
    return len(values) - 1


def unit_direction(size: int, class_index: int) -> np.ndarray:
    if size <= 0 or not 0 <= class_index < size:
        raise ValueError("invalid direction class")
    angle = 2.0 * math.pi * class_index / size
    return np.array((math.cos(angle), math.sin(angle)), dtype=np.float64)


def keyed_direction(key: str) -> np.ndarray:
    angle = 2.0 * math.pi * uniform01(key)
    return np.array((math.cos(angle), math.sin(angle)), dtype=np.float64)


def rotate_direction(vector: Sequence[float], length: int, ordinal: int) -> np.ndarray:
    if length < 1 or not 1 <= ordinal <= length:
        raise ValueError("invalid rotation ordinal")
    source = np.asarray(vector, dtype=np.float64)
    if source.shape != (2,) or not np.all(np.isfinite(source)):
        raise ValueError("rotation expects a finite two-vector")
    angle = 2.0 * math.pi * (ordinal - 1) / length
    rotation = np.array(((math.cos(angle), -math.sin(angle)),
                         (math.sin(angle), math.cos(angle))), dtype=np.float64)
    return rotation @ source


@dataclass(frozen=True)
class GeometryRow:
    anonymous_group_id: str
    anonymous_record_id: str
    split: str
    page: str
    physical_folio: str
    section: str
    currier: str
    hand: str
    code: str
    kind: str
    segment_group_count: int
    segment_group_index: int
    segment_position: str
    segment_count: int
    segment_index: int
    starts_after_drawing: int
    ends_before_drawing: int
    original_group_count: int
    symbol_count: int
    supported_class_target: int
    strict_test_movable: int
    strict_cell_id: str
    strict_cell_record_count: int


@dataclass(frozen=True)
class Record:
    record_id: str
    split: str
    page: str
    physical_folio: str
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
    cell_id: str
    row_indices: tuple[int, ...]

    @property
    def length(self) -> int:
        return len(self.row_indices)


@dataclass(frozen=True)
class Geometry:
    rows: tuple[GeometryRow, ...]
    records: tuple[Record, ...]
    row_index: Mapping[str, int]
    record_index: Mapping[str, int]
    record_for_row: np.ndarray
    target_rows: Mapping[str, np.ndarray]


def _derived_cell_id(row: GeometryRow, record_length: int) -> str:
    """Internal cell identity for TRAIN/CAL; never used as a predictor."""
    parts = (
        row.page, str(row.segment_group_count), row.code,
        str(row.segment_count), str(row.segment_index),
        str(row.starts_after_drawing), str(row.ends_before_drawing),
        str(row.original_group_count),
    )
    raw = "\x1f".join(parts)
    return "C" + hashlib.sha256(("LRS001R1|C|" + raw).encode("utf-8")).hexdigest()[:20]


def geometry_from_rows(rows: Iterable[Mapping[str, object]], *,
                       strict_registered_counts: bool = False) -> Geometry:
    """Validate in-memory pseudonymous rows and build immutable indices."""
    parsed: list[GeometryRow] = []
    for line_number, raw in enumerate(rows, 2):
        if tuple(raw.keys()) != GEOMETRY_FIELDS:
            missing = set(GEOMETRY_FIELDS) - set(raw)
            extra = set(raw) - set(GEOMETRY_FIELDS)
            raise ValueError(f"geometry schema mismatch at line {line_number}: "
                             f"missing={sorted(missing)} extra={sorted(extra)}")
        converted: dict[str, object] = {}
        for field in GEOMETRY_FIELDS:
            value = raw[field]
            if field in _INT_FIELDS:
                try:
                    converted[field] = int(str(value))
                except ValueError as exc:
                    raise ValueError(f"non-integer {field} at line {line_number}") from exc
            else:
                converted[field] = str(value)
        parsed.append(GeometryRow(**converted))
    if not parsed:
        raise ValueError("empty geometry")

    # Scientific order never depends on the physical TSV row order.
    parsed.sort(key=lambda row: (utf8_key(row.anonymous_record_id),
                                 row.segment_group_index,
                                 utf8_key(row.anonymous_group_id)))

    group_ids = [row.anonymous_group_id for row in parsed]
    if len(set(group_ids)) != len(group_ids) or any(not value for value in group_ids):
        raise ValueError("anonymous group IDs must be nonempty and unique")
    for row in parsed:
        if row.split not in {"TRAIN", "CAL", "TEST"}:
            raise ValueError(f"invalid split {row.split!r}")
        if row.symbol_count not in CONTEXT_LENGTHS:
            raise ValueError("symbol_count outside frozen 1..11 support")
        if row.supported_class_target not in {0, 1} or row.strict_test_movable not in {0, 1}:
            raise ValueError("binary geometry field outside {0,1}")
        if row.starts_after_drawing not in {0, 1} or row.ends_before_drawing not in {0, 1}:
            raise ValueError("drawing flags outside {0,1}")
        if min(row.segment_group_count, row.segment_group_index, row.segment_count,
               row.segment_index, row.original_group_count) < 1:
            raise ValueError("nonpositive geometry count/index")
        if row.segment_group_index > row.segment_group_count:
            raise ValueError("segment group index exceeds count")
        if row.segment_index > row.segment_count:
            raise ValueError("segment index exceeds count")
        if row.strict_test_movable and row.split != "TEST":
            raise ValueError("strict movable bit outside TEST")
        if row.strict_test_movable and (not row.strict_cell_id or row.strict_cell_record_count < 2):
            raise ValueError("movable TEST row lacks a valid strict cell")
        if row.split != "TEST" and (row.strict_cell_id or row.strict_cell_record_count):
            raise ValueError("TRAIN/CAL row exposes TEST cell data")

    grouped: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(parsed):
        grouped[row.anonymous_record_id].append(index)
    records: list[Record] = []
    record_for_row = np.empty(len(parsed), dtype=np.int64)
    for record_id in sorted(grouped, key=utf8_key):
        indices = sorted(grouped[record_id], key=lambda i: parsed[i].segment_group_index)
        exemplar = parsed[indices[0]]
        expected_positions = list(range(1, len(indices) + 1))
        positions = [parsed[i].segment_group_index for i in indices]
        if positions != expected_positions:
            raise ValueError(f"record {record_id} has noncontiguous group positions")
        if any(parsed[i].segment_group_count != len(indices) for i in indices):
            raise ValueError(f"record {record_id} has inconsistent group count")
        invariant = (
            "split", "page", "physical_folio", "section", "currier", "hand",
            "code", "kind", "segment_count", "segment_index",
            "starts_after_drawing", "ends_before_drawing", "original_group_count",
            "strict_cell_id", "strict_cell_record_count",
        )
        for field in invariant:
            if len({getattr(parsed[i], field) for i in indices}) != 1:
                raise ValueError(f"record {record_id} varies in {field}")
        reconstructed_cell = _derived_cell_id(exemplar, len(indices))
        if exemplar.split == "TEST" and exemplar.strict_cell_id != reconstructed_cell:
            raise ValueError(f"strict cell ID mismatch for record {record_id}")
        internal_cell = reconstructed_cell
        record = Record(
            record_id=record_id, split=exemplar.split, page=exemplar.page,
            physical_folio=exemplar.physical_folio, section=exemplar.section,
            currier=exemplar.currier, hand=exemplar.hand, code=exemplar.code,
            kind=exemplar.kind, segment_count=exemplar.segment_count,
            segment_index=exemplar.segment_index,
            starts_after_drawing=exemplar.starts_after_drawing,
            ends_before_drawing=exemplar.ends_before_drawing,
            original_group_count=exemplar.original_group_count,
            cell_id=internal_cell, row_indices=tuple(indices),
        )
        record_number = len(records)
        records.append(record)
        record_for_row[indices] = record_number

    # A TEST strict cell must be metadata-homogeneous and its advertised count exact.
    test_cells: dict[str, list[int]] = defaultdict(list)
    for i, record in enumerate(records):
        if record.split == "TEST" and record.cell_id:
            test_cells[record.cell_id].append(i)
    for cell_id, record_indices in test_cells.items():
        advertised = {parsed[records[i].row_indices[0]].strict_cell_record_count
                      for i in record_indices}
        if advertised != {len(record_indices)}:
            raise ValueError(f"strict cell {cell_id} record count mismatch")
        signatures = {
            (records[i].page, records[i].length, records[i].code,
             records[i].segment_count, records[i].segment_index,
             records[i].starts_after_drawing, records[i].ends_before_drawing,
             records[i].original_group_count)
            for i in record_indices
        }
        if len(signatures) != 1:
            raise ValueError(f"strict cell {cell_id} is not homogeneous")

    target_rows = {}
    for split in ("TRAIN", "CAL", "TEST"):
        values = [i for i, row in enumerate(parsed)
                  if row.split == split and row.supported_class_target and
                  (split != "TEST" or row.strict_test_movable)]
        target_rows[split] = np.asarray(values, dtype=np.int64)

    geometry = Geometry(
        rows=tuple(parsed), records=tuple(records),
        row_index={row.anonymous_group_id: i for i, row in enumerate(parsed)},
        record_index={record.record_id: i for i, record in enumerate(records)},
        record_for_row=record_for_row,
        target_rows=target_rows,
    )
    if strict_registered_counts:
        _guard_registered_counts(geometry)
    return geometry


def load_geometry(tsv_path: str | Path, *, manifest_path: str | Path | None = None,
                  expected_tsv_sha256: str | None = EXPECTED_GEOMETRY_TSV_SHA256,
                  expected_manifest_sha256: str | None = EXPECTED_GEOMETRY_MANIFEST_SHA256,
                  strict_registered_counts: bool = True) -> Geometry:
    """Load only the frozen pseudonymous geometry and optional guard manifests."""
    path = Path(tsv_path)
    payload = path.read_bytes()
    actual_hash = sha256_bytes(payload)
    if expected_tsv_sha256 is not None and actual_hash != expected_tsv_sha256:
        raise ValueError("anonymous geometry TSV SHA-256 mismatch")
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != GEOMETRY_FIELDS:
            raise ValueError("anonymous geometry TSV schema mismatch")
        geometry = geometry_from_rows(reader, strict_registered_counts=strict_registered_counts)

    if strict_registered_counts and manifest_path is None:
        raise ValueError("registered geometry load requires its frozen manifest")
    if manifest_path is not None:
        manifest_payload = Path(manifest_path).read_bytes()
        if expected_manifest_sha256 is not None and \
                sha256_bytes(manifest_payload) != expected_manifest_sha256:
            raise ValueError("anonymous geometry manifest SHA-256 mismatch")
        manifest = json.loads(manifest_payload)
        if manifest.get("status") != "PASS_LABEL_FREE_PSEUDONYMOUS_GEOMETRY":
            raise ValueError("anonymous geometry manifest did not pass")
        if manifest.get("decision") != "GO_TARGET_BLIND_SYNTHETIC_CALIBRATION_ONLY":
            raise ValueError("anonymous geometry manifest has wrong decision")
        if tuple(manifest.get("schema", ())) != GEOMETRY_FIELDS:
            raise ValueError("anonymous geometry manifest schema mismatch")
        if manifest.get("tsv_sha256") != actual_hash:
            raise ValueError("manifest/TSV SHA-256 mismatch")
        layout = {int(k): int(v) for k, v in
                  dict(manifest.get("opaque_class_count_by_symbol_count", {})).items()}
        if layout != CLASS_LAYOUT:
            raise ValueError("manifest opaque class layout mismatch")
        isolation = manifest.get("isolation", {})
        forbidden_true = ("real_class_identity_or_family_surface_emitted",
                          "real_context_target_association_scored", "predictor_fitted",
                          "ocr_or_automated_vision_used")
        if any(bool(isolation.get(key)) for key in forbidden_true):
            raise ValueError("manifest isolation guard failed")
    return geometry


def _guard_registered_counts(geometry: Geometry) -> None:
    test = geometry.target_rows["TEST"]
    values = {
        "targets": len(test),
        "records": len({int(geometry.record_for_row[i]) for i in test}),
        "cells": len({geometry.records[int(geometry.record_for_row[i])].cell_id for i in test}),
        "pages": len({geometry.rows[i].page for i in test}),
        "folios": len({geometry.rows[i].physical_folio for i in test}),
    }
    if values != EXPECTED_GEOMETRY_COUNTS:
        raise ValueError(f"registered TEST geometry count mismatch: {values}")


def build_prototypes() -> Mapping[int, tuple[str, ...]]:
    """Construct the frozen 24 unique prototype sequences for each length."""
    result: dict[int, tuple[str, ...]] = {}
    for length in CONTEXT_LENGTHS:
        accepted: list[str] = []
        seen: set[str] = set()
        for class_index in range(24):
            for nonce in range(10000):
                key = f"LRS001R1|PROTO|{length}|{class_index}|{nonce}"
                digest = hashlib.sha256(key.encode("utf-8")).digest()
                sequence = "".join(ALPHABET[byte % ALPHABET_SIZE]
                                   for byte in digest[:length])
                if sequence not in seen:
                    accepted.append(sequence)
                    seen.add(sequence)
                    break
            else:
                raise RuntimeError(f"prototype collision loop exceeded at length {length}")
        if len(accepted) != 24:
            raise AssertionError("prototype construction failed")
        result[length] = tuple(accepted)
    return result


PROTOTYPES = build_prototypes()


def prototype_block(sequence: str) -> np.ndarray:
    """Return the exact 648-dimensional count/edge/adjacency block."""
    if len(sequence) not in CONTEXT_LENGTHS or any(symbol not in ALPHABET for symbol in sequence):
        raise ValueError("prototype sequence outside frozen alphabet/length")
    indices = [ALPHABET.index(symbol) for symbol in sequence]
    counts = np.zeros(24, dtype=np.float64)
    first = np.zeros(24, dtype=np.float64)
    last = np.zeros(24, dtype=np.float64)
    adjacent = np.zeros((24, 24), dtype=np.float64)
    for index in indices:
        counts[index] += 1.0 / len(indices)
    first[indices[0]] = 1.0
    last[indices[-1]] = 1.0
    if len(indices) > 1:
        for left, right in zip(indices[:-1], indices[1:]):
            adjacent[left, right] += 1.0 / (len(indices) - 1)
    block = np.concatenate((counts, first, last, adjacent.ravel()))
    expected = (1.0, 1.0, 1.0, 0.0 if len(indices) == 1 else 1.0)
    observed = (float(counts.sum()), float(first.sum()), float(last.sum()),
                float(adjacent.sum()))
    if block.shape != (BLOCK_DIM,) or any(abs(a - b) > TOL
                                          for a, b in zip(observed, expected)):
        raise AssertionError("invalid 648 prototype block")
    return block


PROTOTYPE_BLOCKS = {
    length: np.stack([prototype_block(value) for value in sequences])
    for length, sequences in PROTOTYPES.items()
}


@dataclass(frozen=True)
class SyntheticWorld:
    """Synthetic assignments aligned to geometry rows.

    ``prototype_index`` is 0..23 for every geometry group.  ``target_class``
    is -1 outside supported targets and an opaque 0-based class inside them.
    The optional family label is used only by reporting/gate code.
    """
    prototype_index: np.ndarray
    target_class: np.ndarray
    family: str = ""


def make_world(geometry: Geometry, prototype_index: Sequence[int],
               target_class: Sequence[int], *, family: str = "",
               allow_target_prototype_separation: bool = False) -> SyntheticWorld:
    prototypes = np.asarray(prototype_index, dtype=np.int64)
    targets = np.asarray(target_class, dtype=np.int64)
    if prototypes.shape != (len(geometry.rows),) or targets.shape != prototypes.shape:
        raise ValueError("world arrays must align one-to-one with geometry rows")
    if np.any((prototypes < 0) | (prototypes >= 24)):
        raise ValueError("prototype index outside 0..23")
    supported = np.array([row.supported_class_target for row in geometry.rows], dtype=bool)
    for i, row in enumerate(geometry.rows):
        if supported[i]:
            if row.symbol_count not in CLASS_LAYOUT:
                raise ValueError("supported target outside opaque 1..6 class layout")
            classes = CLASS_LAYOUT[row.symbol_count]
            if not 0 <= int(targets[i]) < classes:
                raise ValueError("supported target class outside opaque class layout")
            if not allow_target_prototype_separation and int(prototypes[i]) != int(targets[i]):
                raise ValueError("target class/prototype split outside allowed falsifier")
        elif targets[i] != -1:
            raise ValueError("non-target carries a synthetic target class")
    return SyntheticWorld(prototypes.copy(), targets.copy(), family)


def make_world_from_synthetic(geometry: Geometry, synthetic: object) -> SyntheticWorld:
    """Checked duck-typed adapter for the frozen no-I/O synthetic module."""
    try:
        row_ids = tuple(getattr(synthetic, "row_ids"))
        prototypes = getattr(synthetic, "prototype_indices")
        classes = getattr(synthetic, "class_indices")
        separation = np.asarray(getattr(synthetic, "target_separation"), dtype=bool)
        family = str(getattr(getattr(synthetic, "world"), "family"))
    except (AttributeError, TypeError) as exc:
        raise ValueError("invalid synthetic-world object") from exc
    expected_ids = tuple(row.anonymous_group_id for row in geometry.rows)
    if row_ids != expected_ids or separation.shape != (len(geometry.rows),):
        raise ValueError("synthetic-world/geometry row mismatch")
    if np.any(separation) and family not in SEPARATION_FAMILIES:
        raise ValueError("undeclared target/context separation family")
    return make_world(
        geometry, prototypes, classes, family=family,
        allow_target_prototype_separation=family in SEPARATION_FAMILIES,
    )


def synthetic_record_signatures(
    geometry: Geometry, world: SyntheticWorld
) -> Mapping[int, tuple[tuple[int, int], ...]]:
    """Ordered whole-record prototype signatures, indexed by record number."""
    return {
        record_index: tuple(
            (
                geometry.rows[row_index].symbol_count,
                int(world.prototype_index[row_index]),
            )
            for row_index in record.row_indices
        )
        for record_index, record in enumerate(geometry.records)
    }


def dct_contrasts(record_length: int, target_ordinal: int) -> tuple[np.ndarray, np.ndarray]:
    """Return two frozen centered/orthonormal distant-position contrasts."""
    if record_length < 1 or not 1 <= target_ordinal <= record_length:
        raise ValueError("invalid record length/target ordinal")
    positions = np.asarray([k for k in range(1, record_length + 1)
                            if abs(k - target_ordinal) >= 2], dtype=np.int64)
    output = np.zeros((2, record_length), dtype=np.float64)
    accepted: list[np.ndarray] = []
    for rank in (1, 2):
        if len(positions) == 0:
            continue
        vector = np.cos(math.pi * rank * (2.0 * positions - 1.0) /
                        (2.0 * record_length))
        vector -= vector.mean()
        for prior in accepted:
            vector -= float(vector @ prior) * prior
        norm = float(np.linalg.norm(vector))
        if norm <= TOL:
            continue
        vector /= norm
        accepted.append(vector)
        output[rank - 1, positions - 1] = vector
        if abs(float(vector.sum())) > TOL:
            raise AssertionError("DCT contrast did not center")
    return output[0], output[1]


@dataclass(frozen=True)
class Event:
    event_index: int
    row_index: int
    record_index: int
    split: str
    target_class: int
    target_length: int
    target_ordinal: int
    cell_id: str
    page: str
    folio: str
    section: str
    currier: str


@dataclass(frozen=True)
class CategoricalSchema:
    levels: Mapping[str, tuple[str, ...]]
    offsets: Mapping[str, int]
    width: int

    def encode(self, values: Mapping[str, object]) -> np.ndarray:
        vector = np.zeros(self.width, dtype=np.float64)
        for field in CATEGORICAL_FIELDS:
            level = str(values[field])
            choices = self.levels[field]
            try:
                index = choices.index(level)
            except ValueError:
                index = len(choices)  # frozen OTHER column
            vector[self.offsets[field] + index] = 1.0
        return vector


@dataclass(frozen=True)
class FeatureData:
    geometry: Geometry
    world: SyntheticWorld
    events: tuple[Event, ...]
    event_indices_by_split: Mapping[str, np.ndarray]
    schema: CategoricalSchema
    # Self-donor TRAIN/CAL features; dict design -> matrix aligned to events subset.
    self_features: Mapping[str, Mapping[str, np.ndarray]]
    # TEST candidate feature matrices and lookup: design -> rows, plus pair arrays.
    test_features: Mapping[str, np.ndarray]
    test_pair_event: np.ndarray
    test_pair_donor_record: np.ndarray
    test_pair_lookup: Mapping[tuple[int, int], int]
    donor_records_by_cell: Mapping[str, tuple[int, ...]]


def _categorical_values(row: GeometryRow, record: Record) -> dict[str, object]:
    return {
        "currier": row.currier,
        "section": row.section,
        "hand": row.hand,
        "code": row.code,
        "record_length": record.length,
        "target_ordinal": row.segment_group_index,
        "segment_count": row.segment_count,
        "segment_index": row.segment_index,
        "starts_after_drawing": row.starts_after_drawing,
        "ends_before_drawing": row.ends_before_drawing,
        "original_group_count": row.original_group_count,
        "target_symbol_count": row.symbol_count,
    }


def _fit_categorical_schema(geometry: Geometry, train_rows: Sequence[int]) -> CategoricalSchema:
    levels: dict[str, tuple[str, ...]] = {}
    offsets: dict[str, int] = {}
    width = 0
    for field in CATEGORICAL_FIELDS:
        observed = set()
        for row_index in train_rows:
            row = geometry.rows[int(row_index)]
            record = geometry.records[int(geometry.record_for_row[int(row_index)])]
            observed.add(str(_categorical_values(row, record)[field]))
        choices = tuple(sorted(observed, key=utf8_key))
        if not choices:
            raise ValueError(f"no TRAIN levels for {field}")
        levels[field] = choices
        offsets[field] = width
        width += len(choices) + 1  # explicit OTHER
    return CategoricalSchema(levels, offsets, width)


def _world_blocks(geometry: Geometry, world: SyntheticWorld) -> np.ndarray:
    blocks = np.empty((len(geometry.rows), BLOCK_DIM), dtype=np.float64)
    for i, row in enumerate(geometry.rows):
        blocks[i] = PROTOTYPE_BLOCKS[row.symbol_count][int(world.prototype_index[i])]
    return blocks


def _page_backgrounds(geometry: Geometry, blocks: np.ndarray) -> Mapping[tuple[str, str, str], np.ndarray]:
    records_by_page: dict[tuple[str, str], list[int]] = defaultdict(list)
    for record_index, record in enumerate(geometry.records):
        records_by_page[(record.split, record.page)].append(record_index)
    result: dict[tuple[str, str, str], np.ndarray] = {}
    for (split, page), record_indices in records_by_page.items():
        cells = sorted({geometry.records[i].cell_id for i in record_indices}, key=utf8_key)
        for cell_id in cells:
            eligible_rows = [row_index for i in record_indices
                             if geometry.records[i].cell_id != cell_id
                             for row_index in geometry.records[i].row_indices]
            if eligible_rows:
                retained = [i for i in record_indices
                            if geometry.records[i].cell_id != cell_id]
                weighted = np.zeros(BLOCK_DIM, dtype=np.float64)
                for record_index in retained:
                    record = geometry.records[record_index]
                    group_weight = 1.0 / len(retained) / record.length
                    for row_index in record.row_indices:
                        weighted += group_weight * blocks[row_index]
                result[(split, page, cell_id)] = weighted
                continue

            # Exact leave-current-cell-out equal-folio TRAIN fallback.  Each
            # retained group has weight 1/(F*P_f*R_p*G_r), then weights are
            # renormalized.  The current cell is reconstructed identically in
            # every split, so no recipient cell can leak through this path.
            retained_records = [record for record in geometry.records
                                if record.split == "TRAIN" and record.cell_id != cell_id]
            if not retained_records:
                raise ValueError("page-background fallback retained no TRAIN record")
            folios = sorted({record.physical_folio for record in retained_records}, key=utf8_key)
            pages_by_folio = {
                folio: sorted({record.page for record in retained_records
                               if record.physical_folio == folio}, key=utf8_key)
                for folio in folios
            }
            records_by_folio_page: dict[tuple[str, str], list[Record]] = defaultdict(list)
            for record in retained_records:
                records_by_folio_page[(record.physical_folio, record.page)].append(record)
            weighted = np.zeros(BLOCK_DIM, dtype=np.float64)
            total_weight = 0.0
            for record in retained_records:
                record_weight = (1.0 / len(folios) /
                                 len(pages_by_folio[record.physical_folio]) /
                                 len(records_by_folio_page[(record.physical_folio, record.page)]))
                group_weight = record_weight / record.length
                for row_index in record.row_indices:
                    weighted += group_weight * blocks[row_index]
                    total_weight += group_weight
            if total_weight <= 0.0:
                raise ValueError("page-background fallback has zero total weight")
            result[(split, page, cell_id)] = weighted / total_weight
    return result


def _record_bundle(record: Record, donor: Record, blocks: np.ndarray,
                   target_ordinal: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Whole donor predictor bundle for a recipient ordinal.

    The recipient contributes only its ordinal/length. Every content and length
    value below is taken from the same donor record.
    """
    if record.length != donor.length or not 1 <= target_ordinal <= record.length:
        raise ValueError("donor/recipient length mismatch")
    position = target_ordinal - 1
    donor_rows = donor.row_indices
    zero = np.zeros(BLOCK_DIM, dtype=np.float64)
    left = blocks[donor_rows[position - 1]].copy() if position > 0 else zero.copy()
    right = blocks[donor_rows[position + 1]].copy() if position + 1 < donor.length else zero.copy()
    distant_positions = [k for k in range(donor.length) if abs(k - position) >= 2]
    if distant_positions:
        bag = blocks[[donor_rows[k] for k in distant_positions]].mean(axis=0)
    else:
        bag = zero.copy()
    c1, c2 = dct_contrasts(record.length, target_ordinal)
    order1 = sum((c1[k] * blocks[donor_rows[k]] for k in distant_positions), zero.copy())
    order2 = sum((c2[k] * blocks[donor_rows[k]] for k in distant_positions), zero.copy())
    return left, right, bag, order1, order2


def _compose_features(geometry: Geometry, blocks: np.ndarray,
                      backgrounds: Mapping[tuple[str, str, str], np.ndarray],
                      schema: CategoricalSchema, event: Event,
                      donor_record_index: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    row = geometry.rows[event.row_index]
    recipient = geometry.records[event.record_index]
    donor = geometry.records[donor_record_index]
    if recipient.cell_id != donor.cell_id:
        raise ValueError("donor outside recipient strict cell")
    left, right, bag, order1, order2 = _record_bundle(
        recipient, donor, blocks, event.target_ordinal)
    position = event.target_ordinal - 1
    donor_rows = donor.row_indices
    left_length = math.log1p(geometry.rows[donor_rows[position - 1]].symbol_count) if position > 0 else 0.0
    right_length = (math.log1p(geometry.rows[donor_rows[position + 1]].symbol_count)
                    if position + 1 < donor.length else 0.0)
    distant_positions = [k for k in range(donor.length) if abs(k - position) >= 2]
    distant_lengths = np.asarray(
        [math.log1p(geometry.rows[donor_rows[k]].symbol_count) for k in range(donor.length)],
        dtype=np.float64,
    )
    distant_mean_length = (float(distant_lengths[distant_positions].mean())
                            if distant_positions else 0.0)
    c1, c2 = dct_contrasts(recipient.length, event.target_ordinal)
    length_c1 = float(c1 @ distant_lengths)
    length_c2 = float(c2 @ distant_lengths)
    nuisance = np.concatenate((
        schema.encode(_categorical_values(row, recipient)),
        backgrounds[(recipient.split, recipient.page, recipient.cell_id)],
        left, right,
        np.asarray((left_length, right_length, distant_mean_length,
                    length_c1, length_c2), dtype=np.float64),
    ))
    bag_features = np.concatenate((nuisance, bag))
    order_one = np.concatenate((bag_features, order1))
    order_two = np.concatenate((bag_features, order1, order2))
    return nuisance, bag_features, order_one, order_two


def build_feature_data(geometry: Geometry, world: SyntheticWorld) -> FeatureData:
    """Build frozen self-donor TRAIN/CAL and all eligible TEST donor features."""
    blocks = _world_blocks(geometry, world)
    backgrounds = _page_backgrounds(geometry, blocks)
    schema = _fit_categorical_schema(geometry, geometry.target_rows["TRAIN"])

    events: list[Event] = []
    event_indices_by_split: dict[str, list[int]] = defaultdict(list)
    for split in ("TRAIN", "CAL", "TEST"):
        for row_index in geometry.target_rows[split]:
            i = int(row_index)
            row = geometry.rows[i]
            record_index = int(geometry.record_for_row[i])
            record = geometry.records[record_index]
            event = Event(
                event_index=len(events), row_index=i, record_index=record_index,
                split=split, target_class=int(world.target_class[i]),
                target_length=row.symbol_count,
                target_ordinal=row.segment_group_index, cell_id=record.cell_id,
                page=row.page, folio=row.physical_folio, section=row.section,
                currier=row.currier,
            )
            events.append(event)
            event_indices_by_split[split].append(event.event_index)

    self_features: dict[str, dict[str, np.ndarray]] = {}
    for split in ("TRAIN", "CAL"):
        matrices = {name: [] for name in ("NUIS", "BAG", "ORDER1", "ORDER2")}
        for event_index in event_indices_by_split[split]:
            event = events[event_index]
            values = _compose_features(geometry, blocks, backgrounds, schema,
                                       event, event.record_index)
            for name, vector in zip(matrices, values):
                matrices[name].append(vector)
        self_features[split] = {
            name: np.stack(vectors) if vectors else np.empty((0, 0), dtype=np.float64)
            for name, vectors in matrices.items()
        }

    donors_by_cell: dict[str, tuple[int, ...]] = {}
    for record_index, record in enumerate(geometry.records):
        if record.split == "TEST" and record.cell_id:
            donors_by_cell.setdefault(record.cell_id, ())
    for cell_id in list(donors_by_cell):
        donors = [i for i, record in enumerate(geometry.records)
                  if record.split == "TEST" and record.cell_id == cell_id]
        donors_by_cell[cell_id] = tuple(sorted(donors,
                                               key=lambda i: utf8_key(geometry.records[i].record_id)))

    test_matrices = {name: [] for name in ("NUIS", "BAG", "ORDER1", "ORDER2")}
    pair_event: list[int] = []
    pair_donor: list[int] = []
    pair_lookup: dict[tuple[int, int], int] = {}
    for event_index in event_indices_by_split["TEST"]:
        event = events[event_index]
        donors = donors_by_cell[event.cell_id]
        if len(donors) < 2:
            raise ValueError("TEST target has fewer than two eligible record donors")
        for donor_record_index in donors:
            pair_index = len(pair_event)
            pair_lookup[(event_index, donor_record_index)] = pair_index
            pair_event.append(event_index)
            pair_donor.append(donor_record_index)
            values = _compose_features(geometry, blocks, backgrounds, schema,
                                       event, donor_record_index)
            for name, vector in zip(test_matrices, values):
                test_matrices[name].append(vector)
    test_features = {name: np.stack(vectors) for name, vectors in test_matrices.items()}
    return FeatureData(
        geometry=geometry, world=world, events=tuple(events),
        event_indices_by_split={key: np.asarray(value, dtype=np.int64)
                                for key, value in event_indices_by_split.items()},
        schema=schema, self_features=self_features, test_features=test_features,
        test_pair_event=np.asarray(pair_event, dtype=np.int64),
        test_pair_donor_record=np.asarray(pair_donor, dtype=np.int64),
        test_pair_lookup=pair_lookup, donor_records_by_cell=donors_by_cell,
    )


def hierarchy_weights(events: Sequence[Event], indices: Sequence[int] | None = None,
                      *, rescale_to_count: bool = True) -> np.ndarray:
    """Equal target -> record -> cell -> page -> folio hierarchy weights."""
    chosen = list(range(len(events))) if indices is None else [int(i) for i in indices]
    if not chosen:
        raise ValueError("empty hierarchy panel")
    by_folio: dict[str, list[int]] = defaultdict(list)
    by_page: dict[tuple[str, str], list[int]] = defaultdict(list)
    by_cell: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    by_record: dict[int, list[int]] = defaultdict(list)
    for index in chosen:
        event = events[index]
        by_folio[event.folio].append(index)
        by_page[(event.folio, event.page)].append(index)
        by_cell[(event.folio, event.page, event.cell_id)].append(index)
        by_record[event.record_index].append(index)
    page_counts = Counter((event.folio, event.page) for event in (events[i] for i in chosen))
    del page_counts  # counts of targets are not hierarchy denominators
    pages_per_folio = Counter(page_key[0] for page_key in by_page)
    cells_per_page = Counter((cell_key[0], cell_key[1]) for cell_key in by_cell)
    records_per_cell = Counter(
        (events[record_events[0]].folio, events[record_events[0]].page,
         events[record_events[0]].cell_id)
        for record_events in by_record.values()
    )
    n_folios = len(by_folio)
    weights = np.zeros(len(chosen), dtype=np.float64)
    for local_index, event_index in enumerate(chosen):
        event = events[event_index]
        cell_key = (event.folio, event.page, event.cell_id)
        weights[local_index] = (
            1.0 / n_folios /
            pages_per_folio[event.folio] /
            cells_per_page[(event.folio, event.page)] /
            records_per_cell[cell_key] /
            len(by_record[event.record_index])
        )
    if abs(float(weights.sum()) - 1.0) > 1e-10:
        raise AssertionError("hierarchy weights do not sum to one")
    if rescale_to_count:
        weights *= len(chosen)
    return weights


@dataclass(frozen=True)
class Standardizer:
    center: np.ndarray
    scale: np.ndarray
    keep: np.ndarray

    def transform(self, matrix: np.ndarray) -> np.ndarray:
        values = np.asarray(matrix, dtype=np.float64)
        if values.ndim != 2 or values.shape[1] != len(self.center):
            raise ValueError("matrix width differs from frozen standardizer")
        transformed = (values[:, self.keep] - self.center[self.keep]) / self.scale[self.keep]
        if not np.all(np.isfinite(transformed)):
            raise ValueError("nonfinite standardized feature")
        return transformed


def fit_standardizer(matrix: np.ndarray, weights: np.ndarray) -> Standardizer:
    values = np.asarray(matrix, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    if values.ndim != 2 or w.shape != (len(values),) or np.any(w < 0) or \
            not np.all(np.isfinite(values)) or not np.all(np.isfinite(w)) or w.sum() <= 0:
        raise ValueError("invalid standardizer input")
    center = np.average(values, axis=0, weights=w)
    variance = np.average((values - center) ** 2, axis=0, weights=w)
    scale = np.sqrt(np.maximum(variance, 0.0))
    keep = scale > TOL
    if not np.any(keep):
        raise ValueError("standardizer dropped all features")
    return Standardizer(center, scale, keep)


@dataclass(frozen=True)
class DiagonalLDAHead:
    target_length: int
    class_count: int
    ridge: float
    standardizer: Standardizer
    means: np.ndarray
    variance: np.ndarray
    log_prior: np.ndarray

    def predict_log_proba(self, matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        x = self.standardizer.transform(matrix)
        inverse = 1.0 / self.variance
        logits = (x * inverse) @ self.means.T
        logits -= 0.5 * np.sum(self.means * self.means * inverse, axis=1)[None, :]
        logits += self.log_prior[None, :]
        if not np.all(np.isfinite(logits)):
            raise ValueError("nonfinite diagonal-LDA logits")
        logits -= logits.max(axis=1, keepdims=True)
        probabilities = np.exp(logits)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        floor_flags = probabilities < PROBABILITY_FLOOR
        probabilities = np.maximum(probabilities, PROBABILITY_FLOOR)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        return np.log(probabilities), floor_flags


@dataclass(frozen=True)
class LDAModel:
    design: str
    ridge: float
    heads: Mapping[int, DiagonalLDAHead]

    def score_true(self, matrix: np.ndarray, lengths: Sequence[int],
                   classes: Sequence[int]) -> tuple[np.ndarray, np.ndarray]:
        lengths_array = np.asarray(lengths, dtype=np.int64)
        classes_array = np.asarray(classes, dtype=np.int64)
        if len(matrix) != len(lengths_array) or classes_array.shape != lengths_array.shape:
            raise ValueError("score arrays differ in length")
        scores = np.empty(len(matrix), dtype=np.float64)
        floor = np.empty(len(matrix), dtype=bool)
        for length in sorted(self.heads):
            mask = np.flatnonzero(lengths_array == length)
            if len(mask) == 0:
                continue
            logs, flags = self.heads[length].predict_log_proba(matrix[mask])
            y = classes_array[mask]
            if np.any((y < 0) | (y >= logs.shape[1])):
                raise ValueError("true class outside fitted head")
            scores[mask] = logs[np.arange(len(mask)), y]
            floor[mask] = flags[np.arange(len(mask)), y]
        if not np.all(np.isfinite(scores)):
            raise ValueError("unscored/nonfinite true probability")
        return scores, floor


def _fit_head(matrix: np.ndarray, labels: np.ndarray, weights: np.ndarray,
              target_length: int, ridge: float,
              *, standardizer: Standardizer | None = None) -> DiagonalLDAHead:
    class_count = CLASS_LAYOUT[target_length]
    if len(matrix) < 2 or len(np.unique(labels)) < 2:
        raise ValueError("head has fewer than two candidates")
    if set(np.unique(labels)) != set(range(class_count)):
        raise ValueError(f"head {target_length} is missing a class")
    fitted_standardizer = standardizer or fit_standardizer(matrix, weights)
    x = fitted_standardizer.transform(matrix)
    means = np.empty((class_count, x.shape[1]), dtype=np.float64)
    class_weight = np.empty(class_count, dtype=np.float64)
    residual_sum = np.zeros(x.shape[1], dtype=np.float64)
    for class_index in range(class_count):
        mask = labels == class_index
        class_weight[class_index] = weights[mask].sum()
        if class_weight[class_index] <= 0:
            raise ValueError("class has zero fitted weight")
        means[class_index] = np.average(x[mask], axis=0, weights=weights[mask])
        residual_sum += np.sum(weights[mask, None] * (x[mask] - means[class_index]) ** 2,
                               axis=0)
    variance = residual_sum / weights.sum()
    if np.any(~np.isfinite(variance)) or np.any(variance < 0):
        raise ValueError("invalid pooled variance")
    variance = variance + ridge
    prior = (0.5 + class_weight) / (0.5 * class_count + weights.sum())
    return DiagonalLDAHead(target_length, class_count, ridge, fitted_standardizer,
                           means, variance, np.log(prior))


def fit_lda_model(feature_data: FeatureData, split_names: Sequence[str], design: str,
                  ridge: float, *, frozen_standardizers: Mapping[int, Standardizer] | None = None) -> LDAModel:
    if design not in {"NUIS", "BAG", "ORDER1", "ORDER2"} or ridge not in RIDGES:
        raise ValueError("unknown design/ridge")
    matrices = []
    event_indices = []
    for split in split_names:
        if split not in {"TRAIN", "CAL"}:
            raise ValueError("only self-donor TRAIN/CAL may fit a model")
        matrices.append(feature_data.self_features[split][design])
        event_indices.extend(feature_data.event_indices_by_split[split].tolist())
    matrix = np.concatenate(matrices, axis=0)
    events = [feature_data.events[i] for i in event_indices]
    heads: dict[int, DiagonalLDAHead] = {}
    for length in sorted(CLASS_LAYOUT):
        local = [i for i, event in enumerate(events) if event.target_length == length]
        if not local:
            raise ValueError(f"missing target-length head {length}")
        hierarchy = hierarchy_weights(events, local)
        labels = np.asarray([events[i].target_class for i in local], dtype=np.int64)
        standardizer = None if frozen_standardizers is None else frozen_standardizers[length]
        heads[length] = _fit_head(matrix[local], labels, hierarchy, length, ridge,
                                  standardizer=standardizer)
    return LDAModel(design, ridge, heads)


def _score_self(feature_data: FeatureData, model: LDAModel, split: str) -> tuple[np.ndarray, np.ndarray]:
    event_indices = feature_data.event_indices_by_split[split]
    events = [feature_data.events[int(i)] for i in event_indices]
    return model.score_true(
        feature_data.self_features[split][model.design],
        [event.target_length for event in events],
        [event.target_class for event in events],
    )


def hierarchy_mean(values: Sequence[float], events: Sequence[Event],
                   indices: Sequence[int] | None = None) -> float:
    vector = np.asarray(values, dtype=np.float64)
    chosen = list(range(len(events))) if indices is None else [int(i) for i in indices]
    if vector.shape != (len(events),):
        raise ValueError("hierarchy values/events mismatch")
    weights = hierarchy_weights(events, chosen, rescale_to_count=False)
    return float(weights @ vector[chosen])


@dataclass(frozen=True)
class CalibrationCandidate:
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
class CalibratedModels:
    selected: CalibrationCandidate
    candidates: tuple[CalibrationCandidate, ...]
    nuisance: LDAModel
    bag: LDAModel
    order: LDAModel


def calibrate_and_refit(feature_data: FeatureData) -> CalibratedModels:
    """Select q/lambda on CAL, enforce CAL stop, and refit TRAIN+CAL once."""
    train_events = [feature_data.events[int(i)]
                    for i in feature_data.event_indices_by_split["TRAIN"]]
    for length, class_count in sorted(CLASS_LAYOUT.items()):
        labels = {event.target_class for event in train_events
                  if event.target_length == length}
        if labels != set(range(class_count)):
            raise RuntimeError("CAL_STOP_MISSING_CLASS")
    cal_indices = feature_data.event_indices_by_split["CAL"]
    cal_events = [feature_data.events[int(i)] for i in cal_indices]
    candidates: list[CalibrationCandidate] = []
    train_models: dict[tuple[str, float], LDAModel] = {}
    for ridge in RIDGES:
        for design in ("NUIS", "BAG", "ORDER1", "ORDER2"):
            train_models[(design, ridge)] = fit_lda_model(feature_data, ("TRAIN",),
                                                          design, ridge)
        scores: dict[str, np.ndarray] = {}
        floors: dict[str, np.ndarray] = {}
        for design in ("NUIS", "BAG", "ORDER1", "ORDER2"):
            scores[design], floors[design] = _score_self(
                feature_data, train_models[(design, ridge)], "CAL")
        for rank in ORDER_RANKS:
            order_name = f"ORDER{rank}"
            n_score = hierarchy_mean(scores["NUIS"], cal_events)
            b_score = hierarchy_mean(scores["BAG"], cal_events)
            o_score = hierarchy_mean(scores[order_name], cal_events)
            candidates.append(CalibrationCandidate(
                order_rank=rank, ridge=ridge, nuisance_score=n_score,
                bag_score=b_score, order_score=o_score,
                order_minus_bag=o_score - b_score,
                order_minus_nuisance=o_score - n_score,
                floor_rate_nuisance=float(floors["NUIS"].mean()),
                floor_rate_bag=float(floors["BAG"].mean()),
                floor_rate_order=float(floors[order_name].mean()),
            ))

    def better(left: CalibrationCandidate, right: CalibrationCandidate) -> bool:
        # Lexicographic selection with 1e-12 ties: max min gain, max ORDER,
        # smaller q, then larger lambda.
        left_values = (min(left.order_minus_bag, left.order_minus_nuisance),
                       left.order_score)
        right_values = (min(right.order_minus_bag, right.order_minus_nuisance),
                        right.order_score)
        for a, b in zip(left_values, right_values):
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
    if selected.order_minus_bag <= 0 or selected.order_minus_nuisance <= 0:
        raise RuntimeError("CAL_STOP_NONPOSITIVE_GAIN")
    if not all(math.isfinite(value) for value in
               (selected.order_minus_bag, selected.order_minus_nuisance,
                selected.nuisance_score, selected.bag_score, selected.order_score)):
        raise RuntimeError("CAL_STOP_NONFINITE")
    if max(selected.floor_rate_nuisance, selected.floor_rate_bag,
           selected.floor_rate_order) > 0.05 + TOL:
        raise RuntimeError("CAL_STOP_FLOOR_DOMINATED")

    rank = selected.order_rank
    ridge = selected.ridge
    final: dict[str, LDAModel] = {}
    for output_name, design in (("NUIS", "NUIS"), ("BAG", "BAG"),
                                ("ORDER", f"ORDER{rank}")):
        train_model = train_models[(design, ridge)]
        standards = {length: head.standardizer for length, head in train_model.heads.items()}
        final[output_name] = fit_lda_model(feature_data, ("TRAIN", "CAL"), design,
                                           ridge, frozen_standardizers=standards)
    return CalibratedModels(selected, tuple(candidates), final["NUIS"],
                            final["BAG"], final["ORDER"])


@dataclass(frozen=True)
class AssignmentMaps:
    record_indices: np.ndarray
    maps: np.ndarray
    record_column: Mapping[int, int]
    retries: np.ndarray

    def donor_for(self, assignment: int, recipient_record: int) -> int:
        return int(self.maps[assignment, self.record_column[recipient_record]])


def generate_assignment_maps(geometry: Geometry, *, count: int = N_ASSIGNMENTS,
                             require_unique: bool = True) -> AssignmentMaps:
    """Generate identity plus deterministic whole-record within-cell maps."""
    if count < 1 or count > N_ASSIGNMENTS:
        raise ValueError("assignment count outside 1..8192")
    cells: dict[str, list[int]] = defaultdict(list)
    for record_index, record in enumerate(geometry.records):
        if record.split == "TEST" and record.cell_id and record.length >= 1:
            # Every record in a qualifying strict cell moves as part of the
            # global bijection, including records without a target event.
            if geometry.rows[record.row_indices[0]].strict_test_movable:
                cells[record.cell_id].append(record_index)
    if not cells or any(len(records) < 2 for records in cells.values()):
        raise ValueError("assignment panel contains missing/singleton cell")
    record_indices = np.asarray(sorted((i for records in cells.values() for i in records),
                                       key=lambda i: utf8_key(geometry.records[i].record_id)),
                                dtype=np.int64)
    record_column = {int(record): i for i, record in enumerate(record_indices)}
    maps = np.empty((count, len(record_indices)), dtype=np.int64)
    retries = np.zeros(count, dtype=np.int64)
    maps[0] = record_indices
    seen = {maps[0].tobytes()}
    for assignment in range(1, count):
        for retry in range(10000):
            candidate = record_indices.copy()
            for cell_id in sorted(cells, key=utf8_key):
                recipients = sorted(cells[cell_id],
                                    key=lambda i: utf8_key(geometry.records[i].record_id))
                keyed = []
                for donor in recipients:
                    donor_id = geometry.records[donor].record_id
                    key = (f"LRS001R1|ASSIGN|{assignment}|{retry}|"
                           f"{cell_id}|{donor_id}")
                    keyed.append((hashlib.sha256(key.encode("utf-8")).digest(),
                                  donor_id, donor))
                if len({item[0] for item in keyed}) != len(keyed):
                    raise RuntimeError("assignment hash tie")
                donors = [item[2] for item in sorted(
                    keyed, key=lambda item: (item[0], utf8_key(item[1])))]
                if len(set(donors)) != len(recipients):
                    raise AssertionError("assignment is not a bijection")
                for recipient, donor in zip(recipients, donors):
                    candidate[record_column[recipient]] = donor
            packed = candidate.tobytes()
            if packed not in seen:
                maps[assignment] = candidate
                retries[assignment] = retry
                seen.add(packed)
                break
        else:
            raise RuntimeError("assignment retry exceeded 10,000")
    if require_unique:
        packed = {row.tobytes() for row in maps}
        if len(packed) != count:
            raise RuntimeError("global whole-record assignment map collision")
    return AssignmentMaps(record_indices, maps, record_column, retries)


@dataclass(frozen=True)
class PairScores:
    order: np.ndarray
    bag: np.ndarray
    nuisance: np.ndarray
    floor_order: np.ndarray
    floor_bag: np.ndarray
    floor_nuisance: np.ndarray


def score_test_pairs(feature_data: FeatureData, models: CalibratedModels) -> PairScores:
    pair_events = [feature_data.events[int(i)] for i in feature_data.test_pair_event]
    lengths = [event.target_length for event in pair_events]
    classes = [event.target_class for event in pair_events]
    nuisance, nf = models.nuisance.score_true(feature_data.test_features["NUIS"],
                                              lengths, classes)
    bag, bf = models.bag.score_true(feature_data.test_features["BAG"], lengths, classes)
    order_name = f"ORDER{models.selected.order_rank}"
    order, of = models.order.score_true(feature_data.test_features[order_name],
                                        lengths, classes)
    return PairScores(order, bag, nuisance, of, bf, nf)


def assignment_score_matrices(feature_data: FeatureData, pairs: PairScores,
                              assignments: AssignmentMaps) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Lookup precomputed pair scores for every assignment and TEST target."""
    test_events = feature_data.event_indices_by_split["TEST"]
    shape = (len(assignments.maps), len(test_events))
    order = np.empty(shape, dtype=np.float64)
    bag = np.empty(shape, dtype=np.float64)
    nuisance = np.empty(shape, dtype=np.float64)
    pair_by_record = np.full(len(feature_data.geometry.records), -1, dtype=np.int64)
    for event_column, event_index_value in enumerate(test_events):
        event_index = int(event_index_value)
        recipient = feature_data.events[event_index].record_index
        pair_by_record.fill(-1)
        for donor in feature_data.donor_records_by_cell[feature_data.events[event_index].cell_id]:
            pair_by_record[donor] = feature_data.test_pair_lookup[(event_index, donor)]
        donor_vector = assignments.maps[:, assignments.record_column[recipient]]
        pair_indices = pair_by_record[donor_vector]
        if np.any(pair_indices < 0):
            raise ValueError("assignment selected an ineligible donor")
        order[:, event_column] = pairs.order[pair_indices]
        bag[:, event_column] = pairs.bag[pair_indices]
        nuisance[:, event_column] = pairs.nuisance[pair_indices]
    return order, bag, nuisance


@dataclass(frozen=True)
class ChannelResult:
    name: str
    effects: np.ndarray
    observed: float
    null_mean: float
    null_sd: float
    z: float
    max_t_p: float


@dataclass(frozen=True)
class MaxTResult:
    order_minus_bag: ChannelResult
    order_minus_nuisance: ChannelResult
    null_maximum: np.ndarray


@dataclass(frozen=True)
class AssignmentEvaluation:
    max_t: MaxTResult
    identity_order_minus_bag: np.ndarray
    identity_order_minus_nuisance: np.ndarray


def _max_t_from_effects(effects_ob: np.ndarray, effects_on: np.ndarray) -> MaxTResult:
    if effects_ob.shape != (N_ASSIGNMENTS,) or effects_on.shape != (N_ASSIGNMENTS,):
        raise ValueError("registered maxT requires exactly 8192 effects per channel")
    null_ob = effects_ob[1:]
    null_on = effects_on[1:]
    mean_ob, mean_on = float(null_ob.mean()), float(null_on.mean())
    sd_ob, sd_on = float(null_ob.std(ddof=0)), float(null_on.std(ddof=0))
    if (
        not np.all(np.isfinite(effects_ob))
        or not np.all(np.isfinite(effects_on))
        or not math.isfinite(sd_ob)
        or not math.isfinite(sd_on)
        or sd_ob <= TOL
        or sd_on <= TOL
    ):
        raise ValueError("degenerate assignment null")
    z_ob = (effects_ob - mean_ob) / sd_ob
    z_on = (effects_on - mean_on) / sd_on
    maximum = np.maximum(z_ob[1:], z_on[1:])

    def channel(name: str, effects: np.ndarray, mean: float, sd: float,
                z: np.ndarray) -> ChannelResult:
        threshold = float(z[0]) - TOL
        p = (1.0 + float(np.count_nonzero(maximum >= threshold))) / N_ASSIGNMENTS
        return ChannelResult(name, effects, float(effects[0]), mean, sd,
                             float(z[0]), p)
    return MaxTResult(channel("ORDER-BAG", effects_ob, mean_ob, sd_ob, z_ob),
                      channel("ORDER-NUIS", effects_on, mean_on, sd_on, z_on),
                      maximum)


def evaluate_maxT(feature_data: FeatureData, order_scores: np.ndarray,
                  bag_scores: np.ndarray, nuisance_scores: np.ndarray) -> MaxTResult:
    """Aggregate exact hierarchy effects and calculate synchronous maxT p-values."""
    if order_scores.shape != bag_scores.shape or order_scores.shape != nuisance_scores.shape:
        raise ValueError("assignment score shapes differ")
    if order_scores.shape[0] != N_ASSIGNMENTS:
        raise ValueError("registered maxT requires exactly 8192 maps")
    test_events = [feature_data.events[int(i)]
                   for i in feature_data.event_indices_by_split["TEST"]]
    weights = hierarchy_weights(test_events, rescale_to_count=False)
    delta_ob = order_scores - bag_scores
    delta_on = order_scores - nuisance_scores
    effects_ob = delta_ob @ weights
    effects_on = delta_on @ weights
    return _max_t_from_effects(effects_ob, effects_on)


def evaluate_assignments(feature_data: FeatureData, pairs: PairScores,
                         assignments: AssignmentMaps) -> AssignmentEvaluation:
    """Memory-bounded indexed lookup plus exact hierarchy/maxT aggregation."""
    if assignments.maps.shape[0] != N_ASSIGNMENTS:
        raise ValueError("registered evaluation requires exactly 8192 maps")
    test_event_indices = feature_data.event_indices_by_split["TEST"]
    test_events = [feature_data.events[int(i)] for i in test_event_indices]
    weights = hierarchy_weights(test_events, rescale_to_count=False)
    effects_ob = np.zeros(N_ASSIGNMENTS, dtype=np.float64)
    effects_on = np.zeros(N_ASSIGNMENTS, dtype=np.float64)
    identity_ob = np.empty(len(test_events), dtype=np.float64)
    identity_on = np.empty(len(test_events), dtype=np.float64)
    pair_by_record = np.full(len(feature_data.geometry.records), -1, dtype=np.int64)
    for event_column, event_index_value in enumerate(test_event_indices):
        event_index = int(event_index_value)
        event = feature_data.events[event_index]
        pair_by_record.fill(-1)
        for donor in feature_data.donor_records_by_cell[event.cell_id]:
            pair_by_record[donor] = feature_data.test_pair_lookup[(event_index, donor)]
        donor_vector = assignments.maps[:, assignments.record_column[event.record_index]]
        pair_indices = pair_by_record[donor_vector]
        if np.any(pair_indices < 0):
            raise ValueError("assignment selected an ineligible donor")
        delta_ob = pairs.order[pair_indices] - pairs.bag[pair_indices]
        delta_on = pairs.order[pair_indices] - pairs.nuisance[pair_indices]
        effects_ob += weights[event_column] * delta_ob
        effects_on += weights[event_column] * delta_on
        identity_ob[event_column] = delta_ob[0]
        identity_on[event_column] = delta_on[0]
    return AssignmentEvaluation(_max_t_from_effects(effects_ob, effects_on),
                                identity_ob, identity_on)


def subgroup_effect(delta: np.ndarray, events: Sequence[Event], mask: Sequence[bool],
                    *, minimum_capacity: int | None = None) -> float:
    mask_array = np.asarray(mask, dtype=bool)
    if mask_array.shape != (len(events),):
        raise ValueError("subgroup mask/events mismatch")
    chosen = np.flatnonzero(mask_array)
    if minimum_capacity is not None and len(chosen) < minimum_capacity:
        raise ValueError(f"subgroup capacity below {minimum_capacity} targets")
    if len(chosen) == 0:
        raise ValueError("empty subgroup")
    weights = hierarchy_weights(events, chosen, rescale_to_count=False)
    return float(weights @ np.asarray(delta, dtype=np.float64)[chosen])


def normalized_contributions(delta: np.ndarray, events: Sequence[Event],
                             labels: Sequence[object]) -> Mapping[str, float]:
    """Fractions of absolute full-panel weighted contribution by label."""
    if len(labels) != len(events):
        raise ValueError("contribution labels/events mismatch")
    weights = hierarchy_weights(events, rescale_to_count=False)
    totals: dict[str, float] = defaultdict(float)
    for value, weight, label in zip(np.asarray(delta), weights, labels):
        totals[str(label)] += float(value * weight)
    denominator = sum(abs(value) for value in totals.values())
    if not math.isfinite(denominator) or denominator <= TOL:
        raise ValueError("zero contribution denominator")
    return {key: abs(value) / denominator for key, value in totals.items()}


@dataclass(frozen=True)
class GateResult:
    passed: bool
    checks: Mapping[str, bool]
    metrics: Mapping[str, object]


def _position_band(event: Event, geometry: Geometry) -> int:
    length = geometry.records[event.record_index].length
    if length <= 1:
        return 0
    return min(2, math.floor(3 * (event.target_ordinal - 1) / (length - 1)))


def evaluate_passes(feature_data: FeatureData, models: CalibratedModels,
                    max_t: MaxTResult, order_scores: np.ndarray,
                    bag_scores: np.ndarray, nuisance_scores: np.ndarray,
                    pairs: PairScores, *, duplicate_record_signatures: Mapping[int, object]) -> GateResult:
    """Evaluate the full preregistered gate battery for both channels.

    ``duplicate_record_signatures`` must be runner-generated from synthetic
    records only; no source/native value is accepted or needed.
    """
    geometry = feature_data.geometry
    _guard_registered_counts(geometry)
    test_events = [feature_data.events[int(i)]
                   for i in feature_data.event_indices_by_split["TEST"]]
    delta_channels = {
        "OB": order_scores[0] - bag_scores[0],
        "ON": order_scores[0] - nuisance_scores[0],
    }
    channel_results = {"OB": max_t.order_minus_bag, "ON": max_t.order_minus_nuisance}
    checks: dict[str, bool] = {
        "exact_class_count": sum(CLASS_LAYOUT.values()) == 66,
        "exact_head_count": len(models.order.heads) == 6,
        "cal_positive_ob": models.selected.order_minus_bag > 0,
        "cal_positive_on": models.selected.order_minus_nuisance > 0,
    }
    metrics: dict[str, object] = {}
    for channel, delta in delta_channels.items():
        result = channel_results[channel]
        prefix = channel.lower()
        recomputed_observed = hierarchy_mean(delta, test_events)
        if abs(recomputed_observed - result.observed) > 1e-10:
            raise ValueError(f"{channel} maxT result/score mismatch")
        checks[f"{prefix}_effect"] = result.observed >= 0.03 - TOL
        checks[f"{prefix}_maxt"] = result.max_t_p <= 0.01 + TOL and result.z >= 3.0 - TOL

        folios = sorted({event.folio for event in test_events}, key=utf8_key)
        folio_effect = {}
        loo_folio = {}
        for folio in folios:
            mask = np.asarray([event.folio == folio for event in test_events])
            folio_effect[folio] = subgroup_effect(delta, test_events, mask)
            loo_folio[folio] = subgroup_effect(delta, test_events, ~mask)
        checks[f"{prefix}_folio_sign"] = sum(value > 0 for value in folio_effect.values()) >= 16
        checks[f"{prefix}_folio_loo"] = all(value > 0 for value in loo_folio.values())
        folio_contribution = normalized_contributions(delta, test_events,
                                                      [event.folio for event in test_events])
        checks[f"{prefix}_folio_concentration"] = max(folio_contribution.values()) <= 0.20 + TOL

        currier = {level: subgroup_effect(delta, test_events,
                                          [event.currier == level for event in test_events],
                                          minimum_capacity=100)
                   for level in ("A", "B")}
        checks[f"{prefix}_currier"] = (all(value >= 0.01 - TOL for value in currier.values()) and
                                       min(currier.values()) / max(currier.values()) >= 0.25 - TOL)
        sections = {level: subgroup_effect(delta, test_events,
                                           [event.section == level for event in test_events],
                                           minimum_capacity=100)
                    for level in ("B", "H", "S")}
        checks[f"{prefix}_section"] = (all(value >= 0.01 - TOL for value in sections.values()) and
                                       min(sections.values()) / max(sections.values()) >= 0.25 - TOL)
        length_groups = {
            "5-8": subgroup_effect(delta, test_events,
                                   [5 <= geometry.records[event.record_index].length <= 8
                                    for event in test_events], minimum_capacity=100),
            "9-12": subgroup_effect(delta, test_events,
                                    [9 <= geometry.records[event.record_index].length <= 12
                                     for event in test_events], minimum_capacity=100),
        }
        checks[f"{prefix}_record_length"] = (
            all(value >= 0.01 - TOL for value in length_groups.values()) and
            min(length_groups.values()) / max(length_groups.values()) >= 0.25 - TOL)
        bands = {band: subgroup_effect(delta, test_events,
                                       [_position_band(event, geometry) == band
                                        for event in test_events], minimum_capacity=100)
                 for band in range(3)}
        checks[f"{prefix}_position"] = (sum(value >= 0.01 - TOL for value in bands.values()) >= 2 and
                                        all(value > -0.01 + TOL for value in bands.values()))

        classes = [(event.target_length, event.target_class) for event in test_events]
        class_levels = sorted(set(classes))
        class_loo = {}
        for level in class_levels:
            mask = [value != level for value in classes]
            class_loo[str(level)] = subgroup_effect(delta, test_events, mask)
        class_contribution = normalized_contributions(delta, test_events,
                                                      [str(value) for value in classes])
        checks[f"{prefix}_class_loo"] = all(value > 0 for value in class_loo.values())
        checks[f"{prefix}_class_concentration"] = max(class_contribution.values()) <= 0.20 + TOL

        # Remove every record whose synthetic signature occurs more than once
        # anywhere in the supplied split/world signature table.
        missing_signatures = set(range(len(geometry.records))) - set(duplicate_record_signatures)
        if missing_signatures:
            raise ValueError("synthetic duplicate signatures do not cover every record")
        counts = Counter((geometry.records[index].split, value)
                         for index, value in duplicate_record_signatures.items())
        duplicate_records = {record_index for record_index, signature in
                             duplicate_record_signatures.items()
                             if counts[(geometry.records[record_index].split,
                                        signature)] > 1}
        keep = np.asarray([event.record_index not in duplicate_records for event in test_events])
        kept = np.flatnonzero(keep)
        kept_folios = {test_events[i].folio for i in kept}
        duplicate_effect: float | None = None
        deletion_folio_positive = False
        if len(kept) > 0:
            duplicate_effect = subgroup_effect(delta, test_events, keep)
            deletion_folio_positive = True
            for folio in sorted(kept_folios, key=utf8_key):
                subset = keep & np.asarray([event.folio != folio for event in test_events])
                if not np.any(subset):
                    deletion_folio_positive = False
                    break
                deletion_folio_positive &= subgroup_effect(delta, test_events, subset) > 0
        checks[f"{prefix}_duplicate_deletion"] = (
            len(kept) >= 1500 and len(kept_folios) >= 20 and
            duplicate_effect is not None and
            duplicate_effect >= 0.01 - TOL and deletion_folio_positive)
        metrics[prefix] = {
            "folio_effect": folio_effect, "folio_loo": loo_folio,
            "currier": currier, "section": sections, "record_length": length_groups,
            "position": bands, "class_loo": class_loo,
            "duplicate_deletion_effect": duplicate_effect,
            "duplicate_deletion_targets": len(kept),
            "duplicate_deletion_folios": len(kept_folios),
        }

    if not (np.all(np.isfinite(order_scores)) and np.all(np.isfinite(bag_scores)) and
            np.all(np.isfinite(nuisance_scores))):
        checks["finite_test_probabilities"] = False
    else:
        checks["finite_test_probabilities"] = True
    identity_pair_indices = []
    for event_index in feature_data.event_indices_by_split["TEST"]:
        event = feature_data.events[int(event_index)]
        identity_pair_indices.append(feature_data.test_pair_lookup[(int(event_index), event.record_index)])
    identity_pair_indices = np.asarray(identity_pair_indices, dtype=np.int64)
    checks["test_floor_rate"] = all(
        float(flags[identity_pair_indices].mean()) <= 0.05 + TOL
        for flags in (pairs.floor_order, pairs.floor_bag, pairs.floor_nuisance)
    )
    return GateResult(all(checks.values()), checks, metrics)


def evaluate_passes_from_assignment(feature_data: FeatureData,
                                    models: CalibratedModels,
                                    evaluation: AssignmentEvaluation,
                                    pairs: PairScores, *,
                                    duplicate_record_signatures: Mapping[int, object]) -> GateResult:
    """Gate wrapper for the memory-bounded assignment evaluator."""
    delta_ob = np.asarray(evaluation.identity_order_minus_bag, dtype=np.float64)
    delta_on = np.asarray(evaluation.identity_order_minus_nuisance, dtype=np.float64)
    if delta_ob.shape != delta_on.shape:
        raise ValueError("identity channel shape mismatch")
    zero = np.zeros((1, len(delta_ob)), dtype=np.float64)
    order = delta_ob[None, :]
    nuisance = (delta_ob - delta_on)[None, :]
    return evaluate_passes(
        feature_data, models, evaluation.max_t, order, zero, nuisance, pairs,
        duplicate_record_signatures=duplicate_record_signatures,
    )


__all__ = [
    "ALPHABET", "BLOCK_DIM", "CLASS_LAYOUT", "CONTEXT_LENGTHS", "RIDGES", "ORDER_RANKS",
    "PROBABILITY_FLOOR", "N_ASSIGNMENTS", "GEOMETRY_FIELDS", "PROTOTYPES",
    "PROTOTYPE_BLOCKS", "GeometryRow", "Record", "Geometry", "SyntheticWorld",
    "Event", "CategoricalSchema", "FeatureData", "Standardizer",
    "DiagonalLDAHead", "LDAModel", "CalibrationCandidate", "CalibratedModels",
    "AssignmentMaps", "PairScores", "ChannelResult", "MaxTResult",
    "AssignmentEvaluation", "GateResult",
    "uniform01", "categorical_sample", "unit_direction", "keyed_direction",
    "rotate_direction", "geometry_from_rows", "load_geometry", "build_prototypes",
    "prototype_block", "make_world", "make_world_from_synthetic",
    "synthetic_record_signatures", "dct_contrasts", "build_feature_data",
    "hierarchy_weights", "fit_standardizer", "fit_lda_model", "hierarchy_mean",
    "calibrate_and_refit", "generate_assignment_maps", "score_test_pairs",
    "assignment_score_matrices", "evaluate_maxT", "subgroup_effect",
    "evaluate_assignments", "normalized_contributions", "evaluate_passes",
    "evaluate_passes_from_assignment",
]
