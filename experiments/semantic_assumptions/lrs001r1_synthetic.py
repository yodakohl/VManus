#!/usr/bin/env python3
"""Pure synthetic fixtures for the LRS001-R1 calibration.

This module deliberately has no loader and performs no filesystem access.  A
caller must first load the frozen pseudonymous geometry and pass its rows to
``geometry_from_rows``.  Each input row is a mapping with these fields:

``anonymous_group_id``, ``anonymous_record_id``, ``split``, ``page``,
``physical_folio``, ``section``, ``currier``, ``hand``, ``code``, ``kind``,
``segment_group_count``, ``segment_group_index``, ``segment_count``,
``segment_index``, ``starts_after_drawing``, ``ends_before_drawing``,
``original_group_count``, ``symbol_count``, ``supported_class_target``,
``strict_test_movable``, ``strict_cell_id``, and
``strict_cell_record_count``.

Rows are canonicalized by UTF-8 record ID and physical ordinal.  The returned
``SyntheticGeometry`` and every ``SyntheticWorldData`` use that canonical row
order.  No real class identity, transcription surface, parser, or production
target API is accepted.  Synthetic class indices are local to the six opaque
length heads, while prototype indices address the 24 fixed prototypes for the
row's observed length.

The module registers worlds and constructs in-memory synthetic labels and
648-block prototype assignments.  It does not fit, score, execute, serialize,
or publish a registered world.
"""

from __future__ import annotations

import hashlib
import math
import os
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Mapping, Sequence


# The frozen method requires this before NumPy is imported.
for _thread_variable in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_thread_variable] = "1"

import numpy as np


PREFIX = "LRS001R1|"
MASTER = 20260810
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ"
ALPHABET_INDEX = {symbol: index for index, symbol in enumerate(ALPHABET)}
PROTOTYPE_COUNT = 24
PROTOTYPE_LENGTHS = tuple(range(1, 12))
CLASS_COUNT_BY_LENGTH = {1: 3, 2: 8, 3: 23, 4: 19, 5: 10, 6: 3}
SEPARATION_FAMILIES = frozenset(
    {"ONE_POSITION", "ONE_SURFACE", "RANDOM_DONOR", "REVERSED_MAPPING"}
)
ADVERSARIAL_FAMILIES = (
    "PAGE_TOPIC",
    "GLOBAL_FIXED_COLUMN",
    "LENGTH_BY_COLUMN",
    "CODE_DRAWING_STATE",
    "ORDERED_LENGTH_SHAPE",
    "UNORDERED_BAG_TOPIC",
    "PURE_FIRST_ORDER",
    "ONE_FOLIO",
    "ONE_CURRIER",
    "ONE_SECTION",
    "ONE_POSITION",
    "ONE_RECORD_LENGTH",
    "ONE_SURFACE",
    "EXACT_DUPLICATE_ONLY",
    "RANDOM_DONOR",
    "REVERSED_MAPPING",
)
WORLD_FAMILIES = ("NULL", "ORDER_FULL", "ORDER_REDUCED") + ADVERSARIAL_FAMILIES
_FULL_CONTEXT_FAMILIES = frozenset(
    {
        "ORDER_FULL",
        "ONE_POSITION",
        "ONE_SURFACE",
        "RANDOM_DONOR",
        "REVERSED_MAPPING",
    }
)


def _utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


def sha256_digest(key: str) -> bytes:
    """Return SHA-256 bytes, rejecting keys outside the frozen domain."""

    if not isinstance(key, str) or not key.startswith(PREFIX):
        raise ValueError("synthetic SHA key outside LRS001R1 domain")
    return hashlib.sha256(key.encode("utf-8")).digest()


def sha256_hex(key: str) -> str:
    return sha256_digest(key).hex()


def unit_uniform(key: str) -> float:
    """The registered deterministic U(s) primitive."""

    integer = int.from_bytes(sha256_digest(key)[:8], "little")
    value = (integer + 0.5) / 2**64
    if not math.isfinite(value) or not 0.0 < value < 1.0:
        raise ValueError("invalid deterministic uniform")
    return value


def unit_direction(key: str) -> np.ndarray:
    angle = 2.0 * math.pi * unit_uniform(key)
    value = np.asarray((math.cos(angle), math.sin(angle)), dtype=np.float64)
    if not np.isfinite(value).all():
        raise ValueError("nonfinite unit direction")
    return value


def class_direction(pool_size: int, class_index: int) -> np.ndarray:
    if pool_size < 2 or not 0 <= class_index < pool_size:
        raise ValueError("invalid class direction")
    angle = 2.0 * math.pi * class_index / pool_size
    return np.asarray((math.cos(angle), math.sin(angle)), dtype=np.float64)


def rotate_direction(direction: np.ndarray, record_length: int, ordinal: int) -> np.ndarray:
    if direction.shape != (2,) or not np.isfinite(direction).all():
        raise ValueError("invalid direction")
    if record_length < 1 or not 1 <= ordinal <= record_length:
        raise ValueError("invalid physical rotation")
    angle = 2.0 * math.pi * (ordinal - 1) / record_length
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.asarray(
        (
            cosine * direction[0] - sine * direction[1],
            sine * direction[0] + cosine * direction[1],
        ),
        dtype=np.float64,
    )


def stable_softmax(logits: np.ndarray) -> np.ndarray:
    values = np.asarray(logits, dtype=np.float64)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all():
        raise ValueError("invalid categorical logits")
    shifted = values - float(values.max())
    weights = np.exp(shifted, dtype=np.float64)
    total = float(weights.sum(dtype=np.float64))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("degenerate categorical weights")
    probabilities = weights / total
    if not np.isfinite(probabilities).all():
        raise ValueError("nonfinite categorical probabilities")
    return probabilities


def categorical_index(probabilities: np.ndarray, key: str) -> int:
    values = np.asarray(probabilities, dtype=np.float64)
    if (
        values.ndim != 1
        or len(values) < 2
        or not np.isfinite(values).all()
        or np.any(values < 0.0)
    ):
        raise ValueError("invalid categorical probabilities")
    total = float(values.sum(dtype=np.float64))
    if not math.isfinite(total) or abs(total - 1.0) > 1e-12:
        raise ValueError("categorical probabilities do not sum to one")
    threshold = unit_uniform(key)
    cumulative = 0.0
    for index, probability in enumerate(values):
        cumulative += float(probability)
        if cumulative >= threshold:  # Registered inclusive comparison.
            return index
    # Only a final floating-point rounding residual can reach here.
    if cumulative >= 1.0 - 1e-12:
        return len(values) - 1
    raise ValueError("categorical cumulative probability failure")


def directional_probabilities(pool_size: int, direction: np.ndarray, amplitude: float) -> np.ndarray:
    if pool_size < 2 or direction.shape != (2,) or not np.isfinite(direction).all():
        raise ValueError("invalid directional draw")
    if not math.isfinite(amplitude) or amplitude < 0.0:
        raise ValueError("invalid directional amplitude")
    logits = np.asarray(
        [amplitude * float(class_direction(pool_size, c) @ direction) for c in range(pool_size)],
        dtype=np.float64,
    )
    return stable_softmax(logits)


def directional_draw(pool_size: int, direction: np.ndarray, amplitude: float, key: str) -> int:
    return categorical_index(directional_probabilities(pool_size, direction, amplitude), key)


@dataclass(frozen=True, slots=True)
class PrototypeBank:
    sequences: tuple[tuple[str, ...], ...]
    blocks: tuple[np.ndarray, ...]

    def sequence(self, symbol_count: int, prototype_index: int) -> str:
        _validate_prototype_address(symbol_count, prototype_index)
        return self.sequences[symbol_count - 1][prototype_index]

    def block(self, symbol_count: int, prototype_index: int) -> np.ndarray:
        _validate_prototype_address(symbol_count, prototype_index)
        return self.blocks[symbol_count - 1][prototype_index]


def _validate_prototype_address(symbol_count: int, prototype_index: int) -> None:
    if symbol_count not in PROTOTYPE_LENGTHS or not 0 <= prototype_index < PROTOTYPE_COUNT:
        raise ValueError("invalid prototype address")


def sequence_block(sequence: str) -> np.ndarray:
    if not sequence or len(sequence) not in PROTOTYPE_LENGTHS:
        raise ValueError("invalid prototype sequence length")
    if any(symbol not in ALPHABET_INDEX for symbol in sequence):
        raise ValueError("unknown prototype symbol")
    values = [ALPHABET_INDEX[symbol] for symbol in sequence]
    block = np.zeros(648, dtype=np.float64)
    scale = 1.0 / len(values)
    for value in values:
        block[value] += scale
    block[24 + values[0]] = 1.0
    block[48 + values[-1]] = 1.0
    if len(values) > 1:
        pair_scale = 1.0 / (len(values) - 1)
        for left, right in zip(values, values[1:]):
            block[72 + 24 * left + right] += pair_scale
    wanted = np.asarray((1.0, 1.0, 1.0, 0.0 if len(values) == 1 else 1.0))
    observed = np.asarray(
        (block[:24].sum(), block[24:48].sum(), block[48:72].sum(), block[72:].sum())
    )
    if not np.isfinite(block).all() or float(np.max(np.abs(observed - wanted))) > 1e-12:
        raise ValueError("prototype block invariant failure")
    block.setflags(write=False)
    return block


@lru_cache(maxsize=1)
def prototype_bank() -> PrototypeBank:
    all_sequences: list[tuple[str, ...]] = []
    all_blocks: list[np.ndarray] = []
    for symbol_count in PROTOTYPE_LENGTHS:
        used: set[str] = set()
        sequences: list[str] = []
        blocks: list[np.ndarray] = []
        for prototype_index in range(PROTOTYPE_COUNT):
            for nonce in range(10_001):
                if nonce == 10_000:
                    raise ValueError("prototype collision limit exceeded")
                digest = sha256_digest(
                    f"{PREFIX}PROTO|{symbol_count}|{prototype_index}|{nonce}"
                )
                sequence = "".join(ALPHABET[value % 24] for value in digest[:symbol_count])
                if sequence in used:
                    continue
                used.add(sequence)
                sequences.append(sequence)
                blocks.append(sequence_block(sequence))
                break
        if len(sequences) != PROTOTYPE_COUNT or len(used) != PROTOTYPE_COUNT:
            raise ValueError("incomplete prototype bank")
        matrix = np.stack(blocks).astype(np.float64, copy=False)
        matrix.setflags(write=False)
        all_sequences.append(tuple(sequences))
        all_blocks.append(matrix)
    return PrototypeBank(tuple(all_sequences), tuple(all_blocks))


@dataclass(frozen=True, slots=True)
class WorldSpec:
    ordinal: int
    family: str
    index: int

    @property
    def identifier(self) -> str:
        return f"{self.family}:{self.index:02d}"

    @property
    def separates_target_and_group(self) -> bool:
        return self.family in SEPARATION_FAMILIES

    def key(self, purpose: str, *parts: object) -> str:
        if not purpose or "|" in purpose:
            raise ValueError("invalid synthetic key purpose")
        fields = [PREFIX[:-1], "WORLD", str(MASTER), self.family, str(self.index), purpose]
        fields.extend(str(part) for part in parts)
        return "|".join(fields)


@lru_cache(maxsize=1)
def world_registry() -> tuple[WorldSpec, ...]:
    worlds: list[WorldSpec] = []
    for index in range(64):
        worlds.append(WorldSpec(len(worlds), "NULL", index))
    for family in WORLD_FAMILIES[1:]:
        for index in range(8):
            worlds.append(WorldSpec(len(worlds), family, index))
    if len(worlds) != 208 or tuple(world.ordinal for world in worlds) != tuple(range(208)):
        raise ValueError("world registry cardinality/order failure")
    if {world.family for world in worlds} != set(WORLD_FAMILIES):
        raise ValueError("world registry family failure")
    return tuple(worlds)


@dataclass(frozen=True, slots=True)
class GeometryRow:
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
    segment_count: int
    segment_index: int
    starts_after_drawing: bool
    ends_before_drawing: bool
    original_group_count: int
    symbol_count: int
    supported_target: bool
    strict_test_movable: bool
    strict_cell_id: str
    strict_cell_record_count: int


@dataclass(frozen=True, slots=True)
class GeometryRecord:
    record_id: str
    row_indices: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class SyntheticGeometry:
    rows: tuple[GeometryRow, ...]
    records: tuple[GeometryRecord, ...]

    @property
    def row_ids(self) -> tuple[str, ...]:
        return tuple(row.group_id for row in self.rows)

    @property
    def record_ids(self) -> tuple[str, ...]:
        return tuple(record.record_id for record in self.records)


def _bool_field(value: object, field: str) -> bool:
    if value in (True, 1, "1"):
        return True
    if value in (False, 0, "0"):
        return False
    raise ValueError(f"invalid Boolean geometry field: {field}")


def _integer_field(value: object, field: str) -> int:
    try:
        result = int(str(value))
    except (TypeError, ValueError) as error:
        raise ValueError(f"invalid integer geometry field: {field}") from error
    return result


def geometry_from_rows(rows: Iterable[Mapping[str, object]]) -> SyntheticGeometry:
    """Validate and canonicalize an already loaded pseudonymous geometry."""

    converted: list[GeometryRow] = []
    for source in rows:
        converted.append(
            GeometryRow(
                group_id=str(source["anonymous_group_id"]),
                record_id=str(source["anonymous_record_id"]),
                split=str(source["split"]),
                page=str(source["page"]),
                folio=str(source["physical_folio"]),
                section=str(source["section"]),
                currier=str(source["currier"]),
                hand=str(source["hand"]),
                code=str(source["code"]),
                kind=str(source["kind"]),
                record_length=_integer_field(source["segment_group_count"], "segment_group_count"),
                ordinal=_integer_field(source["segment_group_index"], "segment_group_index"),
                segment_count=_integer_field(source["segment_count"], "segment_count"),
                segment_index=_integer_field(source["segment_index"], "segment_index"),
                starts_after_drawing=_bool_field(source["starts_after_drawing"], "starts_after_drawing"),
                ends_before_drawing=_bool_field(source["ends_before_drawing"], "ends_before_drawing"),
                original_group_count=_integer_field(source["original_group_count"], "original_group_count"),
                symbol_count=_integer_field(source["symbol_count"], "symbol_count"),
                supported_target=_bool_field(source["supported_class_target"], "supported_class_target"),
                strict_test_movable=_bool_field(source["strict_test_movable"], "strict_test_movable"),
                strict_cell_id=str(source["strict_cell_id"]),
                strict_cell_record_count=_integer_field(
                    source["strict_cell_record_count"], "strict_cell_record_count"
                ),
            )
        )
    if not converted:
        raise ValueError("empty synthetic geometry")
    converted.sort(key=lambda row: (_utf8_key(row.record_id), row.ordinal, _utf8_key(row.group_id)))
    if len({row.group_id for row in converted}) != len(converted):
        raise ValueError("duplicate pseudonymous group ID")

    grouped: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(converted):
        if row.split not in {"TRAIN", "CAL", "TEST"}:
            raise ValueError("unexpected geometry split")
        if row.symbol_count not in PROTOTYPE_LENGTHS:
            raise ValueError("geometry symbol count outside prototype bank")
        if row.supported_target and (
            row.symbol_count not in CLASS_COUNT_BY_LENGTH
            or row.ordinal in {1, row.record_length}
        ):
            raise ValueError("invalid supported target geometry")
        grouped[row.record_id].append(index)

    records: list[GeometryRecord] = []
    record_fields = (
        "split",
        "page",
        "folio",
        "section",
        "currier",
        "hand",
        "code",
        "kind",
        "record_length",
        "segment_count",
        "segment_index",
        "starts_after_drawing",
        "ends_before_drawing",
        "original_group_count",
        "strict_test_movable",
        "strict_cell_id",
        "strict_cell_record_count",
    )
    for record_id in sorted(grouped, key=_utf8_key):
        indices = tuple(grouped[record_id])
        group = [converted[index] for index in indices]
        length = group[0].record_length
        if not 5 <= length <= 12 or len(group) != length:
            raise ValueError("incomplete synthetic record geometry")
        if [row.ordinal for row in group] != list(range(1, length + 1)):
            raise ValueError("nonconsecutive synthetic record geometry")
        if any(len({getattr(row, field) for row in group}) != 1 for field in record_fields):
            raise ValueError("within-record geometry drift")
        if group[0].split == "TEST" and not group[0].strict_cell_id:
            raise ValueError("TEST record lacks strict cell")
        if group[0].strict_test_movable and (
            group[0].split != "TEST" or group[0].strict_cell_record_count < 2
        ):
            raise ValueError("invalid movable TEST record")
        records.append(GeometryRecord(record_id, indices))
    test_cells: dict[str, list[GeometryRecord]] = defaultdict(list)
    for record in records:
        row = converted[record.row_indices[0]]
        if row.split == "TEST":
            test_cells[row.strict_cell_id].append(record)
    for members in test_cells.values():
        actual = len(members)
        for record in members:
            row = converted[record.row_indices[0]]
            if row.strict_cell_record_count != actual:
                raise ValueError("strict TEST cell count drift")
            if row.strict_test_movable != (actual >= 2):
                raise ValueError("strict TEST mobility drift")
    return SyntheticGeometry(tuple(converted), tuple(records))


@dataclass(frozen=True, slots=True)
class SyntheticWorldData:
    world: WorldSpec
    row_ids: tuple[str, ...]
    prototype_indices: np.ndarray
    class_indices: np.ndarray
    target_separation: np.ndarray
    record_nonces: tuple[int, ...]
    copied_record_ids: tuple[str, ...]

    def group_blocks(self, geometry: SyntheticGeometry) -> np.ndarray:
        if self.row_ids != geometry.row_ids or len(self.prototype_indices) != len(geometry.rows):
            raise ValueError("world/geometry mismatch")
        bank = prototype_bank()
        output = np.empty((len(geometry.rows), 648), dtype=np.float64)
        for index, row in enumerate(geometry.rows):
            output[index] = bank.block(row.symbol_count, int(self.prototype_indices[index]))
        if not np.isfinite(output).all():
            raise ValueError("nonfinite synthetic group blocks")
        return output

    def class_ids(self, geometry: SyntheticGeometry) -> tuple[str | None, ...]:
        if self.row_ids != geometry.row_ids:
            raise ValueError("world/geometry mismatch")
        output: list[str | None] = []
        for row, class_index in zip(geometry.rows, self.class_indices, strict=True):
            value = int(class_index)
            if not row.supported_target:
                if value != -1:
                    raise ValueError("class assigned to unsupported row")
                output.append(None)
                continue
            count = CLASS_COUNT_BY_LENGTH[row.symbol_count]
            if not 0 <= value < count:
                raise ValueError("synthetic class outside opaque head")
            output.append(f"T{row.symbol_count}_{value}")
        return tuple(output)


def _full_direction(world: WorldSpec, record: GeometryRecord, row: GeometryRow) -> np.ndarray:
    base = unit_direction(world.key("RECORD_DIRECTION", record.record_id))
    return rotate_direction(base, row.record_length, row.ordinal)


def _null_direction(world: WorldSpec, row: GeometryRow, purpose: str = "NULL_DIRECTION") -> np.ndarray:
    return unit_direction(world.key(purpose, row.group_id))


def _position_band(row: GeometryRow) -> int:
    return min(2, math.floor(3 * (row.ordinal - 1) / (row.record_length - 1)))


def _length_shape_direction(record_rows: Sequence[GeometryRow]) -> np.ndarray:
    odd = sum(math.log1p(row.symbol_count) for row in record_rows if row.ordinal % 2 == 1)
    even = sum(math.log1p(row.symbol_count) for row in record_rows if row.ordinal % 2 == 0)
    value = np.asarray((odd, even), dtype=np.float64)
    norm = float(np.linalg.norm(value))
    if not math.isfinite(norm) or norm <= 1e-12:
        raise ValueError("degenerate ordered-length direction")
    return value / norm


def _context_direction(
    geometry: SyntheticGeometry,
    world: WorldSpec,
    record: GeometryRecord,
    row: GeometryRow,
) -> tuple[np.ndarray, float]:
    family = world.family
    if family == "NULL":
        return _null_direction(world, row), 1.0
    if family == "ORDER_REDUCED":
        return _full_direction(world, record, row), 2.0
    if family in _FULL_CONTEXT_FAMILIES:
        return _full_direction(world, record, row), 3.0
    if family == "PAGE_TOPIC":
        return unit_direction(world.key("PAGE_DIRECTION", row.page)), 3.0
    if family == "GLOBAL_FIXED_COLUMN":
        return unit_direction(world.key("COLUMN_DIRECTION", row.record_length, row.ordinal)), 3.0
    if family == "LENGTH_BY_COLUMN":
        return unit_direction(
            world.key("LENGTH_COLUMN_DIRECTION", row.record_length, row.ordinal, row.symbol_count)
        ), 3.0
    if family == "CODE_DRAWING_STATE":
        return unit_direction(
            world.key(
                "CODE_DRAWING_DIRECTION",
                row.code,
                row.segment_count,
                row.segment_index,
                int(row.starts_after_drawing),
                int(row.ends_before_drawing),
                row.original_group_count,
            )
        ), 3.0
    if family == "ORDERED_LENGTH_SHAPE":
        return unit_direction(world.key("LENGTH_SHAPE_CONTEXT", row.ordinal, row.symbol_count)), 3.0
    if family == "UNORDERED_BAG_TOPIC":
        return unit_direction(world.key("BAG_DIRECTION", record.record_id)), 3.0
    if family == "ONE_FOLIO":
        folios = sorted(
            {
                candidate.folio
                for candidate in geometry.rows
                if candidate.split == "TEST"
                and candidate.strict_test_movable
                and candidate.supported_target
            },
            key=_utf8_key,
        )
        if not folios:
            raise ValueError("ONE_FOLIO has no movable TEST target folio")
        if row.split in {"TRAIN", "CAL"} or row.folio == folios[world.index % len(folios)]:
            return _full_direction(world, record, row), 3.0
        return _null_direction(world, row), 1.0
    if family == "ONE_CURRIER":
        selected = "A" if world.index % 2 == 0 else "B"
        if row.currier == selected:
            return _full_direction(world, record, row), 3.0
        return _null_direction(world, row), 1.0
    if family == "ONE_SECTION":
        selected = ("B", "H", "S")[world.index % 3]
        if row.section == selected:
            return _full_direction(world, record, row), 3.0
        return _null_direction(world, row), 1.0
    if family == "ONE_RECORD_LENGTH":
        selected = 0 if world.index % 2 == 0 else 1
        band = 0 if row.record_length <= 8 else 1
        if band == selected:
            return _full_direction(world, record, row), 3.0
        return _null_direction(world, row), 1.0
    if family == "ORDER_FULL":
        return _full_direction(world, record, row), 3.0
    if family in {"RANDOM_DONOR", "REVERSED_MAPPING"}:
        return _full_direction(world, record, row), 3.0
    raise ValueError(f"context direction requires specialized generator: {family}")


def _draw_key(world: WorldSpec, purpose: str, row: GeometryRow, nonce: int) -> str:
    return world.key(purpose, row.group_id, nonce)


def _draw_group(
    world: WorldSpec,
    row: GeometryRow,
    pool_size: int,
    direction: np.ndarray,
    amplitude: float,
    nonce: int,
    purpose: str = "GROUP_DRAW",
) -> int:
    return directional_draw(pool_size, direction, amplitude, _draw_key(world, purpose, row, nonce))


def _record_lookup(geometry: SyntheticGeometry) -> dict[str, GeometryRecord]:
    return {record.record_id: record for record in geometry.records}


def _random_donor_successors(geometry: SyntheticGeometry) -> dict[str, str]:
    cells: dict[str, list[str]] = defaultdict(list)
    for record in geometry.records:
        row = geometry.rows[record.row_indices[0]]
        if row.split == "TEST" and row.strict_test_movable:
            cells[row.strict_cell_id].append(record.record_id)
    successors: dict[str, str] = {}
    for cell_id in sorted(cells, key=_utf8_key):
        members = sorted(cells[cell_id], key=_utf8_key)
        if len(members) < 2:
            raise ValueError("RANDOM_DONOR movable cell has fewer than two records")
        for index, record_id in enumerate(members):
            successors[record_id] = members[(index + 1) % len(members)]
    return successors


def _separated_target_draw(
    geometry: SyntheticGeometry,
    world: WorldSpec,
    record: GeometryRecord,
    row: GeometryRow,
    nonce: int,
    records_by_id: Mapping[str, GeometryRecord],
    successors: Mapping[str, str],
) -> int:
    pool_size = CLASS_COUNT_BY_LENGTH[row.symbol_count]
    family = world.family
    if family == "ONE_POSITION":
        if _position_band(row) == world.index % 3:
            direction, amplitude = _full_direction(world, record, row), 3.0
        else:
            direction, amplitude = _null_direction(world, row, "TARGET_NULL_DIRECTION"), 1.0
        return _draw_group(world, row, pool_size, direction, amplitude, nonce, "TARGET_DRAW")
    if family == "ONE_SURFACE":
        ordered_classes = [
            (symbol_count, class_index)
            for symbol_count in sorted(CLASS_COUNT_BY_LENGTH)
            for class_index in range(CLASS_COUNT_BY_LENGTH[symbol_count])
        ]
        selected = ordered_classes[world.index % len(ordered_classes)]
        full = _full_direction(world, record, row)
        null = _null_direction(world, row, "TARGET_NULL_DIRECTION")
        logits = np.empty(pool_size, dtype=np.float64)
        for class_index in range(pool_size):
            coordinate = class_direction(pool_size, class_index)
            logits[class_index] = float(coordinate @ null)
            if (row.symbol_count, class_index) == selected:
                logits[class_index] += 3.0 * float(coordinate @ full)
        return categorical_index(
            stable_softmax(logits), _draw_key(world, "TARGET_DRAW", row, nonce)
        )
    if family == "RANDOM_DONOR":
        target_record = record
        if row.split == "TEST" and row.strict_test_movable:
            donor_id = successors.get(record.record_id)
            if donor_id is None:
                raise ValueError("missing RANDOM_DONOR successor")
            target_record = records_by_id[donor_id]
        base = unit_direction(world.key("RECORD_DIRECTION", target_record.record_id))
        direction = rotate_direction(base, row.record_length, row.ordinal)
        return _draw_group(world, row, pool_size, direction, 3.0, nonce, "TARGET_DRAW")
    if family == "REVERSED_MAPPING":
        if row.split == "TEST":
            base = unit_direction(world.key("RECORD_DIRECTION", record.record_id))
            direction = rotate_direction(
                base, row.record_length, row.record_length + 1 - row.ordinal
            )
        else:
            direction = _full_direction(world, record, row)
        return _draw_group(world, row, pool_size, direction, 3.0, nonce, "TARGET_DRAW")
    raise ValueError("unregistered target/group separation")


def _generate_pure_first_order_record(
    geometry: SyntheticGeometry,
    world: WorldSpec,
    record: GeometryRecord,
    nonce: int,
) -> tuple[list[int], list[int]]:
    prototypes: list[int] = []
    classes: list[int] = []
    previous = -1
    for local_index, row_index in enumerate(record.row_indices):
        row = geometry.rows[row_index]
        pool_size = CLASS_COUNT_BY_LENGTH[row.symbol_count] if row.supported_target else 24
        if local_index == 0:
            direction = _null_direction(world, row, "FIRST_ORDER_INITIAL_DIRECTION")
            amplitude = 1.0
        else:
            follows = unit_uniform(world.key("FIRST_ORDER_TRANSITION", row.group_id)) < 0.8
            if follows:
                direction = class_direction(24, previous)
                amplitude = 3.0
            else:
                direction = _null_direction(world, row, "FIRST_ORDER_INDEPENDENT_DIRECTION")
                amplitude = 1.0
        prototype = _draw_group(
            world, row, pool_size, direction, amplitude, nonce, "FIRST_ORDER_DRAW"
        )
        prototypes.append(prototype)
        classes.append(prototype if row.supported_target else -1)
        previous = prototype
    return prototypes, classes


def _generate_regular_record(
    geometry: SyntheticGeometry,
    world: WorldSpec,
    record: GeometryRecord,
    nonce: int,
    records_by_id: Mapping[str, GeometryRecord],
    successors: Mapping[str, str],
) -> tuple[list[int], list[int], list[bool]]:
    if world.family == "PURE_FIRST_ORDER":
        prototypes, classes = _generate_pure_first_order_record(geometry, world, record, nonce)
        return prototypes, classes, [False] * len(prototypes)
    record_rows = [geometry.rows[index] for index in record.row_indices]
    length_shape = (
        _length_shape_direction(record_rows)
        if world.family == "ORDERED_LENGTH_SHAPE"
        else None
    )
    prototypes: list[int] = []
    classes: list[int] = []
    separation: list[bool] = []
    for row in record_rows:
        direction, amplitude = _context_direction(geometry, world, record, row)
        if length_shape is not None and row.supported_target:
            direction = length_shape
        if world.separates_target_and_group:
            prototype = _draw_group(world, row, 24, direction, amplitude, nonce)
            if not row.supported_target:
                target_class = -1
                separated = False
            else:
                target_class = _separated_target_draw(
                    geometry,
                    world,
                    record,
                    row,
                    nonce,
                    records_by_id,
                    successors,
                )
                separated = True
        else:
            pool_size = CLASS_COUNT_BY_LENGTH[row.symbol_count] if row.supported_target else 24
            prototype = _draw_group(world, row, pool_size, direction, amplitude, nonce)
            target_class = prototype if row.supported_target else -1
            separated = False
        prototypes.append(prototype)
        classes.append(target_class)
        separation.append(separated)
    return prototypes, classes, separation


def _duplicate_pairs(
    geometry: SyntheticGeometry,
) -> tuple[list[tuple[GeometryRecord, GeometryRecord]], list[GeometryRecord]]:
    strata: dict[tuple[str, tuple[int, ...], tuple[int, ...]], list[GeometryRecord]] = defaultdict(list)
    for record in geometry.records:
        rows = [geometry.rows[index] for index in record.row_indices]
        key = (
            rows[0].split,
            tuple(row.symbol_count for row in rows),
            tuple(int(row.supported_target) for row in rows),
        )
        strata[key].append(record)
    pairs: list[tuple[GeometryRecord, GeometryRecord]] = []
    unpaired: list[GeometryRecord] = []
    for key in sorted(strata, key=lambda value: (_utf8_key(value[0]), value[1], value[2])):
        records = sorted(strata[key], key=lambda record: _utf8_key(record.record_id))
        for index in range(0, len(records) - 1, 2):
            pairs.append((records[index], records[index + 1]))
        if len(records) % 2:
            unpaired.append(records[-1])
    pairs.sort(
        key=lambda pair: (
            _utf8_key(geometry.rows[pair[0].row_indices[0]].split),
            _utf8_key(pair[0].record_id),
        )
    )
    unpaired.sort(
        key=lambda record: (
            _utf8_key(geometry.rows[record.row_indices[0]].split),
            _utf8_key(record.record_id),
        )
    )
    return pairs, unpaired


def _generate_exact_duplicate_world(
    geometry: SyntheticGeometry,
    world: WorldSpec,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, tuple[str, ...], tuple[int, ...]]:
    prototypes = np.full(len(geometry.rows), -1, dtype=np.int16)
    classes = np.full(len(geometry.rows), -1, dtype=np.int16)
    separation = np.zeros(len(geometry.rows), dtype=np.bool_)
    copied: list[str] = []
    nonces_by_record: dict[str, int] = {}
    signatures: dict[str, set[tuple[tuple[int, int], ...]]] = defaultdict(set)
    pairs, unpaired = _duplicate_pairs(geometry)
    for first, second in pairs:
        first_rows = [geometry.rows[index] for index in first.row_indices]
        second_rows = [geometry.rows[index] for index in second.row_indices]
        if (
            [row.symbol_count for row in first_rows]
            != [row.symbol_count for row in second_rows]
            or [row.supported_target for row in first_rows]
            != [row.supported_target for row in second_rows]
        ):
            raise ValueError("incompatible exact-duplicate pair")
        split = first_rows[0].split
        for nonce in range(10_001):
            if nonce == 10_000:
                raise ValueError("exact-duplicate pair collision limit exceeded")
            proposed = [
                _draw_group(
                    world,
                    row,
                    CLASS_COUNT_BY_LENGTH[row.symbol_count]
                    if row.supported_target
                    else 24,
                    _full_direction(world, first, row),
                    3.0,
                    nonce,
                    "DUPLICATE_FULL_DRAW",
                )
                for row in first_rows
            ]
            signature = tuple(
                (row.symbol_count, prototype)
                for row, prototype in zip(first_rows, proposed, strict=True)
            )
            if signature in signatures[split]:
                continue
            signatures[split].add(signature)
            for first_index, second_index, first_row, prototype in zip(
                first.row_indices,
                second.row_indices,
                first_rows,
                proposed,
                strict=True,
            ):
                prototypes[first_index] = prototypes[second_index] = prototype
                if first_row.supported_target:
                    classes[first_index] = classes[second_index] = prototype
            nonces_by_record[first.record_id] = nonce
            nonces_by_record[second.record_id] = nonce
            break
        copied.append(second.record_id)
    for record in unpaired:
        rows = [geometry.rows[index] for index in record.row_indices]
        split = rows[0].split
        for nonce in range(10_001):
            if nonce == 10_000:
                raise ValueError("exact-duplicate unpaired collision limit exceeded")
            proposed = [
                _draw_group(
                    world,
                    row,
                    CLASS_COUNT_BY_LENGTH[row.symbol_count] if row.supported_target else 24,
                    _null_direction(world, row),
                    1.0,
                    nonce,
                )
                for row in rows
            ]
            signature = tuple(
                (row.symbol_count, prototype)
                for row, prototype in zip(rows, proposed, strict=True)
            )
            if signature in signatures[split]:
                continue
            signatures[split].add(signature)
            for row_index, row, prototype in zip(
                record.row_indices, rows, proposed, strict=True
            ):
                prototypes[row_index] = prototype
                if row.supported_target:
                    classes[row_index] = prototype
            nonces_by_record[record.record_id] = nonce
            break
    if np.any(prototypes < 0):
        raise ValueError("incomplete exact-duplicate world")
    nonces = tuple(nonces_by_record[record.record_id] for record in geometry.records)
    return prototypes, classes, separation, tuple(sorted(copied, key=_utf8_key)), nonces


def generate_world(geometry: SyntheticGeometry, world: WorldSpec) -> SyntheticWorldData:
    """Generate one in-memory registered fixture without fitting or scoring it."""

    registered = world_registry()
    if not 0 <= world.ordinal < len(registered) or registered[world.ordinal] != world:
        raise ValueError("world is not in the frozen registry")
    prototype_bank()  # Force and validate the complete fixed bank first.
    if world.family == "EXACT_DUPLICATE_ONLY":
        prototypes, classes, separation, copied, nonces = _generate_exact_duplicate_world(
            geometry, world
        )
    else:
        prototypes = np.full(len(geometry.rows), -1, dtype=np.int16)
        classes = np.full(len(geometry.rows), -1, dtype=np.int16)
        separation = np.zeros(len(geometry.rows), dtype=np.bool_)
        records_by_id = _record_lookup(geometry)
        successors = _random_donor_successors(geometry) if world.family == "RANDOM_DONOR" else {}
        signatures: dict[str, set[tuple[tuple[int, int], ...]]] = defaultdict(set)
        record_nonces: list[int] = []
        for record in geometry.records:
            split = geometry.rows[record.row_indices[0]].split
            accepted = False
            for nonce in range(10_001):
                if nonce == 10_000:
                    raise ValueError("record-signature collision limit exceeded")
                record_prototypes, record_classes, record_separation = _generate_regular_record(
                    geometry,
                    world,
                    record,
                    nonce,
                    records_by_id,
                    successors,
                )
                signature = tuple(
                    (geometry.rows[row_index].symbol_count, record_prototypes[local])
                    for local, row_index in enumerate(record.row_indices)
                )
                if signature in signatures[split]:
                    continue
                signatures[split].add(signature)
                for local, row_index in enumerate(record.row_indices):
                    prototypes[row_index] = record_prototypes[local]
                    classes[row_index] = record_classes[local]
                    separation[row_index] = record_separation[local]
                record_nonces.append(nonce)
                accepted = True
                break
            if not accepted:
                raise ValueError("failed to construct unique record signature")
        nonces = tuple(record_nonces)
        copied = ()

    if np.any(prototypes < 0):
        raise ValueError("incomplete synthetic prototype assignment")
    for index, row in enumerate(geometry.rows):
        prototype = int(prototypes[index])
        if not 0 <= prototype < 24:
            raise ValueError("prototype index outside fixed bank")
        target_class = int(classes[index])
        if row.supported_target:
            if not 0 <= target_class < CLASS_COUNT_BY_LENGTH[row.symbol_count]:
                raise ValueError("synthetic target class outside head")
            if not separation[index] and target_class != prototype:
                raise ValueError("unregistered target/group separation")
        elif target_class != -1 or separation[index]:
            raise ValueError("unsupported row received target state")
    if world.separates_target_and_group != bool(np.any(separation)):
        raise ValueError("target-separation family flag mismatch")
    if world.family not in SEPARATION_FAMILIES and np.any(separation):
        raise ValueError("target/group separation outside registered falsifiers")
    prototypes.setflags(write=False)
    classes.setflags(write=False)
    separation.setflags(write=False)
    return SyntheticWorldData(
        world=world,
        row_ids=geometry.row_ids,
        prototype_indices=prototypes,
        class_indices=classes,
        target_separation=separation,
        record_nonces=nonces,
        copied_record_ids=copied,
    )


__all__ = [
    "ADVERSARIAL_FAMILIES",
    "ALPHABET",
    "CLASS_COUNT_BY_LENGTH",
    "GeometryRecord",
    "GeometryRow",
    "MASTER",
    "PROTOTYPE_COUNT",
    "PROTOTYPE_LENGTHS",
    "PrototypeBank",
    "SEPARATION_FAMILIES",
    "SyntheticGeometry",
    "SyntheticWorldData",
    "WORLD_FAMILIES",
    "WorldSpec",
    "categorical_index",
    "class_direction",
    "directional_draw",
    "directional_probabilities",
    "generate_world",
    "geometry_from_rows",
    "prototype_bank",
    "rotate_direction",
    "sequence_block",
    "sha256_digest",
    "sha256_hex",
    "stable_softmax",
    "unit_direction",
    "unit_uniform",
    "world_registry",
]
