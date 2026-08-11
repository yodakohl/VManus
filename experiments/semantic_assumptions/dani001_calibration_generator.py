#!/usr/bin/env python3
"""Deterministic, source-free synthetic generator for DANI001 calibration.

This module has no network API and no registered-source loader.  It constructs
only synthetic rows, projected synthetic lexicons, parser fixtures, mutation
digests, and their hash-only manifest.  Synthetic candidate maps may be
enumerated; the real released-map score is not represented by any API here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import struct
import tempfile
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from dani001_panel import (
    CORE_INPUTS,
    CORE_OUTPUTS,
    EDITION_ORDER,
    NIBBLE_CODE,
    NIBBLE_SYMBOLS,
    PANEL_ORDER,
    SEPARATOR_NAMES,
    compile_source_token,
)


MODULE_DIR = Path(__file__).resolve().parent
CALIBRATION_SPEC_PATH = MODULE_DIR / "DANI001_TARGET_BLIND_CALIBRATION_SPEC.md"
MANIFEST_PATH = MODULE_DIR / "DANI001_SYNTHETIC_MANIFEST.json"
CALIBRATION_SPEC_REL = (
    "experiments/semantic_assumptions/"
    "DANI001_TARGET_BLIND_CALIBRATION_SPEC.md"
)
SCIENCE_SPEC_REL = (
    "experiments/semantic_assumptions/"
    "DANI001_FIXED_MAPPING_DIAGNOSTIC_SPEC.md"
)
SCIENCE_COMMIT = "1faa87f"
SCIENCE_SPEC_SHA256 = (
    "cc73479b3c35eaa87a3f56184fc3472fe6232b67c13deb3bf30ef8555a6c8426"
)
CALIBRATION_SPEC_SHA256 = (
    "f38de851d96e5fbb3a9a8bbb7ecd9c925ee34e4cb1c181970b6f582fbdea9c32"
)

ROOT_DOMAIN = "DANI001-TARGET-BLIND-CALIBRATION-V1"
COUNTER_LABELS = (
    "plant-map-rank",
    "null-probe-rank",
    "null-key-tail",
    "adversary-candidate-rank",
    "adversary-decoy-tail",
    "toy-map-rank",
    "conjugacy-permutation",
)
MARKER_SPELLINGS = ("sh", "t", "p", "f")
MARKER_OUTPUTS = ("š", "ṭ", "p", "ṣ")
VOWEL_SPELLINGS = ("a", "o", "e", "i")
SYNTHETIC_DOMAINS = ("astro", "botanical", "general", "medical", "pharma")
ALLOWED_SEPARATORS = tuple(SEPARATOR_NAMES)
PAGE_RE = re.compile(r"^f([1-9][0-9]*)r$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

WORLD_IDS_ADVERSARY = (
    "FIXED_HEAVY_HIGH_COVERAGE",
    "ONE_TYPE_CONCENTRATION",
    "ONE_FOLIO_CONCENTRATION",
    "PREFIX_ONLY",
    "UNKNOWN_SKIP",
    "ONE_READING_WRONG",
)


def expected_world_signature(assertion_id: str) -> dict[str, object]:
    return {
        "assertion_count": 1,
        "assertions": [{
            "id": assertion_id,
            "operator": "WORLD_SIGNATURE",
            "value": True,
        }],
    }


class DANI001SyntheticError(RuntimeError):
    """The frozen synthetic construction or output contract was violated."""


def canonical_json_bytes(value: object) -> bytes:
    """Return the frozen UTF-8 canonical-JSON encoding with one LF."""

    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class CounterUse:
    """One bounded counter-hash result.

    The first integer in ``integer_fields`` is the modulus.  Remaining values
    are the call fields from the calibration specification.  Internal SHA
    rejection attempts are deterministically reconstructed and are not a new
    discretionary field.
    """

    label: str
    integer_fields: tuple[int, ...]
    result: int

    def to_manifest(self) -> list[object]:
        return [self.label, list(self.integer_fields), self.result]


def hash_counter(label: str, *fields: int) -> int:
    """Return H(label, fields...) as an unsigned little-endian integer."""

    if label not in COUNTER_LABELS:
        raise DANI001SyntheticError(f"counter label outside allowlist: {label}")
    if len(label.encode("ascii")) > 0xFFFF or len(fields) > 0xFFFF:
        raise DANI001SyntheticError("counter label/field count overflow")
    payload = bytearray(ROOT_DOMAIN.encode("ascii"))
    payload.append(0)
    encoded_label = label.encode("ascii")
    payload.extend(struct.pack("<H", len(encoded_label)))
    payload.extend(encoded_label)
    payload.extend(struct.pack("<H", len(fields)))
    for value in fields:
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < 2**64:
            raise DANI001SyntheticError("counter field outside uint64")
        payload.extend(struct.pack("<Q", value))
    return int.from_bytes(hashlib.sha256(payload).digest(), "little")


def bounded_draw(
    label: str,
    modulus: int,
    *fields: int,
    audit: list[CounterUse] | None = None,
) -> int:
    """Return the exact rejection-sampled B(label, modulus, fields...)."""

    if not isinstance(modulus, int) or isinstance(modulus, bool) or not 1 <= modulus <= 2**64:
        raise DANI001SyntheticError("bounded-draw modulus outside [1,2**64]")
    cutoff = (2**256 // modulus) * modulus
    attempt = 0
    while True:
        value = hash_counter(label, *fields, attempt)
        if value < cutoff:
            result = value % modulus
            if audit is not None:
                audit.append(CounterUse(label, (modulus, *fields), result))
            return result
        attempt += 1


def deterministic_permutation(
    label: str,
    variable_count: int,
    *fields: int,
    audit: list[CounterUse] | None = None,
) -> tuple[int, ...]:
    """Return PERM(label, variable_count, fields...) by Fisher--Yates."""

    if not 1 <= variable_count <= 10:
        raise DANI001SyntheticError("synthetic permutation size outside 1..10")
    values = list(range(variable_count))
    for completed, index in enumerate(range(variable_count - 1, 0, -1)):
        other = bounded_draw(
            label,
            index + 1,
            *fields,
            completed,
            audit=audit,
        )
        values[index], values[other] = values[other], values[index]
    return tuple(values)


def rank_lex(permutation: Sequence[int]) -> int:
    """Rank one permutation in Python's lexicographic tuple order."""

    values = tuple(permutation)
    size = len(values)
    if sorted(values) != list(range(size)):
        raise DANI001SyntheticError("cannot rank a nonpermutation")
    rank = 0
    remaining = list(range(size))
    for index, value in enumerate(values):
        ordinal = remaining.index(value)
        rank += ordinal * math.factorial(size - index - 1)
        remaining.pop(ordinal)
    return rank


def unrank_lex(variable_count: int, rank: int) -> tuple[int, ...]:
    """Invert :func:`rank_lex` exactly."""

    count = math.factorial(variable_count)
    if not 0 <= rank < count:
        raise DANI001SyntheticError("permutation rank outside orbit")
    remaining = list(range(variable_count))
    output: list[int] = []
    residual = rank
    for width in range(variable_count, 0, -1):
        factorial = math.factorial(width - 1)
        ordinal, residual = divmod(residual, factorial)
        output.append(remaining.pop(ordinal))
    return tuple(output)


def unique_nonidentity_ranks(
    label: str,
    count: int,
    variable_count: int = 10,
) -> tuple[tuple[int, tuple[CounterUse, ...]], ...]:
    """Freeze the first ``count`` unique nonidentity ranks and per-item draws."""

    orbit = math.factorial(variable_count)
    if count < 0 or count > orbit - 1:
        raise DANI001SyntheticError("impossible unique-rank request")
    used: set[int] = set()
    output: list[tuple[int, tuple[CounterUse, ...]]] = []
    for index in range(count):
        attempt = 0
        local_audit: list[CounterUse] = []
        while True:
            candidate = 1 + bounded_draw(
                label,
                orbit - 1,
                index,
                attempt,
                audit=local_audit,
            )
            if candidate not in used:
                used.add(candidate)
                output.append((candidate, tuple(local_audit)))
                break
            attempt += 1
    return tuple(output)


def first_nonidentity_permutation(
    label: str,
    variable_count: int,
    *fields: int,
) -> tuple[tuple[int, ...], tuple[CounterUse, ...]]:
    attempt = 0
    all_uses: list[CounterUse] = []
    identity = tuple(range(variable_count))
    while True:
        local: list[CounterUse] = []
        candidate = deterministic_permutation(
            label,
            variable_count,
            *fields,
            attempt,
            audit=local,
        )
        all_uses.extend(local)
        if candidate != identity:
            return candidate, tuple(all_uses)
        attempt += 1


def _tag_digits(width: int, index: int) -> tuple[int, ...]:
    if width < 1 or not 0 <= index < 4**width:
        raise DANI001SyntheticError("marker tag outside width")
    output = [0] * width
    residual = index
    for cursor in range(width - 1, -1, -1):
        output[cursor] = residual % 4
        residual //= 4
    return tuple(output)


def tag(width: int, index: int) -> str:
    return "".join(MARKER_SPELLINGS[value] for value in _tag_digits(width, index))


def keytag(width: int, index: int) -> str:
    return "".join(MARKER_OUTPUTS[value] for value in _tag_digits(width, index))


def vtag(width: int, index: int) -> str:
    """Return a normalized-type tag whose scanner emission is empty."""

    return "".join(VOWEL_SPELLINGS[value] for value in _tag_digits(width, index))


def ordinary_prefix(index: int) -> tuple[str, str]:
    """Raw/key prefixes for one of the ordinary 256 six-tail/toy types."""

    if not 0 <= index < 256:
        raise DANI001SyntheticError("ordinary synthetic type outside 0..255")
    marker = index // 16
    vowel = index % 16
    return vtag(2, vowel) + tag(2, marker), keytag(2, marker)


def five_tail_prefix(index: int) -> tuple[str, str]:
    """Parity-separated raw/key prefixes for a block-0/1 five-tail type."""

    if not 0 <= index < 512:
        raise DANI001SyntheticError("five-tail synthetic type outside 0..511")
    block, local = divmod(index, 256)
    marker = 32 * block + 2 * (local // 16) + local % 2
    vowel = (local % 16) // 2
    return vtag(2, vowel) + tag(3, marker), keytag(3, marker)


def one_type_prefix(index: int) -> tuple[str, str]:
    """Signal/decoy-disjoint prefix for ONE_TYPE_CONCENTRATION."""

    if not 0 <= index < 256:
        raise DANI001SyntheticError("one-type synthetic type outside 0..255")
    if index <= 8:
        return vtag(2, 0) + tag(3, index), keytag(3, index)
    local = index - 9
    marker = 9 + local // 16
    return vtag(2, local % 16) + tag(3, marker), keytag(3, marker)


def six_input_tail(index: int) -> tuple[int, ...]:
    return (0, 1, 2, 3, 4, 5) if index % 2 == 0 else (4, 5, 6, 7, 8, 9)


def five_input_tail(index: int) -> tuple[int, ...]:
    return (0, 1, 2, 3, 4) if index % 2 == 0 else (5, 6, 7, 8, 9)


def _render_input_tail(tail: Sequence[int]) -> str:
    return "".join(CORE_INPUTS[index] for index in tail)


def _render_output_tail(
    permutation: Sequence[int],
    tail: Sequence[int],
    variable_count: int = 10,
) -> str:
    outputs = CORE_OUTPUTS[:variable_count]
    return "".join(outputs[permutation[index]] for index in tail)


@dataclass(frozen=True, slots=True)
class SyntheticRow:
    edition: str
    page: str
    locus: str
    groups: tuple[str, ...] = field(repr=False)
    separators: tuple[str, ...] = field(repr=False)

    def __post_init__(self) -> None:
        if self.edition not in EDITION_ORDER:
            raise DANI001SyntheticError("synthetic row has unknown edition")
        match = PAGE_RE.fullmatch(self.page)
        if match is None:
            raise DANI001SyntheticError("synthetic row has nonnumeric page")
        folio = int(match.group(1))
        if self.locus != f"P.{folio}":
            raise DANI001SyntheticError("synthetic row page/locus folio drift")
        if not self.groups or any(not isinstance(group, str) for group in self.groups):
            raise DANI001SyntheticError("synthetic row has empty/invalid groups")
        if len(self.separators) != len(self.groups) - 1:
            raise DANI001SyntheticError("synthetic row topology mismatch")
        if any(value not in ALLOWED_SEPARATORS for value in self.separators):
            raise DANI001SyntheticError("synthetic row has unknown separator")

    @property
    def folio(self) -> int:
        match = PAGE_RE.fullmatch(self.page)
        assert match is not None
        return int(match.group(1))

    def to_object(self) -> dict[str, object]:
        return {
            "edition": self.edition,
            "page": self.page,
            "locus": self.locus,
            "groups": list(self.groups),
            "separators": list(self.separators),
        }


def canonicalize_rows(rows: Iterable[SyntheticRow]) -> tuple[SyntheticRow, ...]:
    output = tuple(sorted(
        rows,
        key=lambda row: (
            EDITION_ORDER.index(row.edition),
            row.folio,
            row.page.encode("utf-8"),
            row.locus.encode("utf-8"),
        ),
    ))
    seen: set[tuple[str, str, str]] = set()
    for row in output:
        key = (row.edition, row.page, row.locus)
        if key in seen:
            raise DANI001SyntheticError("duplicate synthetic row key")
        seen.add(key)
    if not output:
        raise DANI001SyntheticError("empty synthetic panel")
    return output


def _dot_only_groups(row: SyntheticRow) -> tuple[str, ...]:
    output: list[str] = []
    current = row.groups[0]
    for boundary, group in zip(row.separators, row.groups[1:], strict=True):
        if boundary == ".":
            output.append(current)
            current = group
        else:
            current += group
    output.append(current)
    return tuple(output)


def panel_projection(
    rows: Iterable[SyntheticRow],
    panel_name: str,
) -> tuple[dict[str, object], ...]:
    """Build the frozen target-free canonical synthetic panel projection."""

    if panel_name not in PANEL_ORDER:
        raise DANI001SyntheticError("unknown synthetic panel name")
    output: list[dict[str, object]] = []
    for row in canonicalize_rows(rows):
        raw_groups = row.groups if panel_name == "MANUAL_GROUP" else _dot_only_groups(row)
        for raw in raw_groups:
            compiled = compile_source_token(raw, row.folio)
            if compiled is None:
                continue
            token, strict = compiled
            output.append({
                "edition": row.edition,
                "page": row.page,
                "locus": row.locus,
                "folio": row.folio,
                "normalized_eva": token.normalized_eva,
                "emitted_template": list(token.emitted_template),
                "strict_literal_eligible": bool(strict),
            })
    return tuple(output)


def panel_projection_sha256(rows: Iterable[SyntheticRow], panel_name: str) -> str:
    return sha256_bytes(canonical_json_bytes(list(panel_projection(rows, panel_name))))


def _row_hashes(rows: Sequence[SyntheticRow]) -> tuple[tuple[str, ...], str]:
    digests = tuple(
        sha256_bytes(canonical_json_bytes(row.to_object()))
        for row in rows
    )
    joined = b"".join(bytes.fromhex(value) for value in digests)
    return digests, sha256_bytes(joined)


def _entries() -> list[dict[str, object]]:
    return [
        {"domain": domain, "source_present": True}
        for domain in SYNTHETIC_DOMAINS
    ]


def _base14_three(value: int) -> tuple[int, int, int]:
    if not 0 <= value < 14**3:
        raise DANI001SyntheticError("base-14 value outside three digits")
    return ((value // 196) % 14, (value // 14) % 14, value % 14)


def unreachable_key(index: int) -> str:
    digits = _base14_three(index)
    return "u" + "".join(NIBBLE_SYMBOLS[value] for value in digits)


def is_reachable_key(key: str) -> bool:
    return bool(key) and all(symbol in NIBBLE_CODE for symbol in key)


def build_lexicon(
    reachable_keys: Iterable[str],
    *,
    variable_count: int,
) -> tuple[dict[str, object], ...]:
    key_set = set(reachable_keys)
    if not key_set or any(not is_reachable_key(key) or len(key) > 8 for key in key_set):
        raise DANI001SyntheticError("synthetic reachable key invariant failed")
    if variable_count == 10:
        key_set.update(unreachable_key(index) for index in range(570))
    records = [
        {"key": key, "entries": _entries()}
        for key in sorted(key_set, key=lambda value: value.encode("utf-8"))
    ]
    return tuple(records)


def _uniform_rows(groups: tuple[str, ...]) -> tuple[SyntheticRow, ...]:
    separators = (".",) * (len(groups) - 1)
    return tuple(
        SyntheticRow(
            edition=edition,
            page=f"f{folio}r",
            locus=f"P.{folio}",
            groups=groups,
            separators=separators,
        )
        for edition in EDITION_ORDER
        for folio in range(1, 33)
    )


@lru_cache(maxsize=None)
def _base_groups(variable_count: int) -> tuple[str, ...]:
    if variable_count == 10:
        return tuple(
            ordinary_prefix(index)[0] + _render_input_tail(six_input_tail(index))
            for index in range(256)
        )
    if variable_count in (4, 6):
        tail = tuple(range(variable_count))
        return tuple(
            ordinary_prefix(index)[0] + _render_input_tail(tail)
            for index in range(256)
        )
    raise DANI001SyntheticError("unsupported base-world variable count")


@dataclass(frozen=True, slots=True)
class SyntheticWorld:
    world_id: str
    family: str
    trial_index: int
    variable_count: int
    candidate_rank: int
    secret_rank: int | None
    alternate_rank: int | None
    generator_fields: tuple[CounterUse, ...] = field(repr=False)
    rows: tuple[SyntheticRow, ...] = field(repr=False)
    lexicon: tuple[dict[str, object], ...] = field(repr=False)
    expected: dict[str, object] = field(repr=False)

    def __post_init__(self) -> None:
        orbit = math.factorial(self.variable_count)
        for value in (self.candidate_rank, self.secret_rank, self.alternate_rank):
            if value is not None and not 0 <= value < orbit:
                raise DANI001SyntheticError("synthetic map rank outside orbit")
        if self.candidate_rank == 0:
            raise DANI001SyntheticError("registered synthetic candidate must be nonidentity")
        canonicalize_rows(self.rows)
        if not self.lexicon:
            raise DANI001SyntheticError("synthetic world has empty lexicon")

    @property
    def permutation_count(self) -> int:
        return math.factorial(self.variable_count)

    def payload_object(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "variable_count": self.variable_count,
            "candidate_rank": self.candidate_rank,
            "secret_rank": self.secret_rank,
            "alternate_rank": self.alternate_rank,
            "rows": [row.to_object() for row in self.rows],
            "lexicon": list(self.lexicon),
        }

    def manifest_record(self) -> dict[str, object]:
        rows = canonicalize_rows(self.rows)
        row_digests, rows_digest = _row_hashes(rows)
        lexicon_bytes = canonical_json_bytes(list(self.lexicon))
        reachable_count = sum(
            is_reachable_key(record["key"])  # type: ignore[arg-type]
            for record in self.lexicon
        )
        return {
            "world_id": self.world_id,
            "family": self.family,
            "trial_index": self.trial_index,
            "variable_count": self.variable_count,
            "permutation_count": self.permutation_count,
            "candidate_rank": self.candidate_rank,
            "secret_rank": self.secret_rank,
            "alternate_rank": self.alternate_rank,
            "generator_fields": [value.to_manifest() for value in self.generator_fields],
            "row_count": len(rows),
            "row_sha256s": list(row_digests),
            "rows_sha256": rows_digest,
            "lexicon_record_count": len(self.lexicon),
            "reachable_key_count": reachable_count,
            "lexicon_sha256": sha256_bytes(lexicon_bytes),
            "dot_panel_sha256": panel_projection_sha256(rows, "DOT_ONLY_EMULATION"),
            "manual_panel_sha256": panel_projection_sha256(rows, "MANUAL_GROUP"),
            "world_sha256": sha256_bytes(canonical_json_bytes(self.payload_object())),
            "expected": self.expected,
        }


def _coherent_keys(
    permutation: Sequence[int],
    *,
    variable_count: int,
) -> tuple[str, ...]:
    if variable_count == 10:
        return tuple(
            ordinary_prefix(index)[1]
            + _render_output_tail(permutation, six_input_tail(index), variable_count)
            for index in range(256)
        )
    tail = tuple(range(variable_count))
    return tuple(
        ordinary_prefix(index)[1]
        + _render_output_tail(permutation, tail, variable_count)
        for index in range(256)
    )


def build_plant_world(
    trial_index: int,
    rank: int,
    rank_audit: Sequence[CounterUse],
) -> SyntheticWorld:
    permutation = unrank_lex(10, rank)
    rows = _uniform_rows(_base_groups(10))
    lexicon = build_lexicon(_coherent_keys(permutation, variable_count=10), variable_count=10)
    return SyntheticWorld(
        world_id=f"PLANT_{trial_index:03d}",
        family="PLANT",
        trial_index=trial_index,
        variable_count=10,
        candidate_rank=rank,
        secret_rank=rank,
        alternate_rank=None,
        generator_fields=tuple(rank_audit),
        rows=rows,
        lexicon=lexicon,
        expected=expected_world_signature(f"PLANT_{trial_index:03d}_SUCCESS"),
    )


def build_null_world(
    trial_index: int,
    probe_rank: int,
    rank_audit: Sequence[CounterUse],
) -> SyntheticWorld:
    audit = list(rank_audit)
    keys: list[str] = []
    for index in range(256):
        output_order = deterministic_permutation(
            "null-key-tail",
            10,
            trial_index,
            index,
            audit=audit,
        )
        keys.append(
            ordinary_prefix(index)[1]
            + "".join(CORE_OUTPUTS[value] for value in output_order[:6])
        )
    return SyntheticWorld(
        world_id=f"NULL_{trial_index:03d}",
        family="NULL",
        trial_index=trial_index,
        variable_count=10,
        candidate_rank=probe_rank,
        secret_rank=None,
        alternate_rank=None,
        generator_fields=tuple(audit),
        rows=_uniform_rows(_base_groups(10)),
        lexicon=build_lexicon(keys, variable_count=10),
        expected=expected_world_signature(
            f"NULL_{trial_index:03d}_PROBE_INDEPENDENCE"
        ),
    )


def build_toy_world(variable_count: int, *, plant: bool) -> SyntheticWorld:
    if variable_count not in (4, 6):
        raise DANI001SyntheticError("toy variable count must be 4 or 6")
    map_kind = 0 if plant else 1
    candidate, rank_audit = first_nonidentity_permutation(
        "toy-map-rank",
        variable_count,
        variable_count,
        map_kind,
    )
    candidate_rank = rank_lex(candidate)
    audit = list(rank_audit)
    if plant:
        keys = _coherent_keys(candidate, variable_count=variable_count)
    else:
        keys_list: list[str] = []
        for index in range(256):
            output_order = deterministic_permutation(
                "null-key-tail",
                variable_count,
                1000 + variable_count,
                index,
                audit=audit,
            )
            keys_list.append(
                ordinary_prefix(index)[1]
                + "".join(CORE_OUTPUTS[value] for value in output_order)
            )
        keys = tuple(keys_list)
    suffix = "PLANT" if plant else "NULL"
    return SyntheticWorld(
        world_id=f"TOY{variable_count}_{suffix}",
        family=f"TOY_{suffix}",
        trial_index=0,
        variable_count=variable_count,
        candidate_rank=candidate_rank,
        secret_rank=candidate_rank if plant else None,
        alternate_rank=None,
        generator_fields=tuple(audit),
        rows=_uniform_rows(_base_groups(variable_count)),
        lexicon=build_lexicon(keys, variable_count=variable_count),
        expected=expected_world_signature(
            f"TOY{variable_count}_{suffix}_COMPLETE_EQUALITY"
        ),
    )


def _rotated_alternate(permutation: Sequence[int]) -> tuple[int, ...]:
    return tuple((value + 1) % 10 for value in permutation)


def _decoy_tail(
    adversary_index: int,
    type_index: int,
    source_tail: Sequence[int],
    candidate: Sequence[int],
    audit: list[CounterUse],
    *,
    reject_both_parities: bool = False,
) -> tuple[int, ...]:
    forbidden = {tuple(candidate[value] for value in source_tail)}
    if reject_both_parities:
        forbidden = {
            tuple(candidate[value] for value in (0, 1, 2, 3, 4)),
            tuple(candidate[value] for value in (5, 6, 7, 8, 9)),
        }
    attempt = 0
    while True:
        output_order = deterministic_permutation(
            "adversary-decoy-tail",
            10,
            adversary_index,
            type_index,
            attempt,
            audit=audit,
        )
        output_tail = output_order[:5]
        if output_tail not in forbidden:
            return output_tail
        attempt += 1


def _world_from_parts(
    *,
    world_id: str,
    adversary_index: int,
    candidate_rank: int,
    candidate_audit: Sequence[CounterUse],
    rows: tuple[SyntheticRow, ...],
    keys: Iterable[str],
    expected: dict[str, object],
    secret_rank: int | None,
    alternate_rank: int | None,
    additional_audit: Sequence[CounterUse] = (),
) -> SyntheticWorld:
    return SyntheticWorld(
        world_id=world_id,
        family="ADVERSARY",
        trial_index=adversary_index,
        variable_count=10,
        candidate_rank=candidate_rank,
        secret_rank=secret_rank,
        alternate_rank=alternate_rank,
        generator_fields=tuple(candidate_audit) + tuple(additional_audit),
        rows=rows,
        lexicon=build_lexicon(keys, variable_count=10),
        expected=expected,
    )


def build_adversary_world(
    adversary_index: int,
    candidate_rank: int,
    candidate_audit: Sequence[CounterUse],
) -> SyntheticWorld:
    if not 0 <= adversary_index < len(WORLD_IDS_ADVERSARY):
        raise DANI001SyntheticError("unknown adversary index")
    world_id = WORLD_IDS_ADVERSARY[adversary_index]
    candidate = unrank_lex(10, candidate_rank)
    alternate = _rotated_alternate(candidate)
    alternate_rank = rank_lex(alternate)
    audit: list[CounterUse] = []

    if world_id == "FIXED_HEAVY_HIGH_COVERAGE":
        variable_groups = tuple(
            five_tail_prefix(index)[0] + _render_input_tail(five_input_tail(index))
            for index in range(256)
        )
        variable_keys = tuple(
            five_tail_prefix(index)[1]
            + _render_output_tail(alternate, five_input_tail(index))
            for index in range(256)
        )
        fixed_groups: list[str] = []
        fixed_keys: list[str] = []
        for index in range(64):
            digits = _tag_digits(3, index)
            fixed_groups.append(
                "cth"
                + MARKER_SPELLINGS[digits[0]] + "a"
                + MARKER_SPELLINGS[digits[1]] + "o"
                + MARKER_SPELLINGS[digits[2]] + "e"
            )
            fixed_keys.append("k" + keytag(3, index))
        groups = variable_groups + tuple(
            group for group in fixed_groups for _ in range(100)
        )
        return _world_from_parts(
            world_id=world_id,
            adversary_index=adversary_index,
            candidate_rank=candidate_rank,
            candidate_audit=candidate_audit,
            rows=_uniform_rows(groups),
            keys=variable_keys + tuple(fixed_keys),
            expected=expected_world_signature(
                "ADVERSARY_FIXED_HEAVY_HIGH_COVERAGE_SIGNATURE"
            ),
            secret_rank=alternate_rank,
            alternate_rank=alternate_rank,
        )

    if world_id == "ONE_TYPE_CONCENTRATION":
        groups: list[str] = []
        keys: list[str] = []
        for index in range(256):
            tail = five_input_tail(index)
            raw_prefix, key_prefix = one_type_prefix(index)
            raw = raw_prefix + _render_input_tail(tail)
            repetitions = 100 if index == 0 else 2 if index <= 8 else 1
            groups.extend([raw] * repetitions)
            if index <= 8:
                output_tail = tuple(candidate[value] for value in tail)
            else:
                output_tail = _decoy_tail(
                    adversary_index,
                    index,
                    tail,
                    candidate,
                    audit,
                    reject_both_parities=True,
                )
            keys.append(
                key_prefix
                + "".join(CORE_OUTPUTS[value] for value in output_tail)
            )
        return _world_from_parts(
            world_id=world_id,
            adversary_index=adversary_index,
            candidate_rank=candidate_rank,
            candidate_audit=candidate_audit,
            additional_audit=audit,
            rows=_uniform_rows(tuple(groups)),
            keys=keys,
            expected=expected_world_signature(
                "ADVERSARY_ONE_TYPE_CONCENTRATION_SIGNATURE"
            ),
            secret_rank=candidate_rank,
            alternate_rank=None,
        )

    if world_id == "ONE_FOLIO_CONCENTRATION":
        raw_types: list[str] = []
        keys: list[str] = []
        for index in range(512):
            tail = five_input_tail(index)
            raw_prefix, key_prefix = five_tail_prefix(index)
            raw_types.append(raw_prefix + _render_input_tail(tail))
            if index < 256:
                output_tail = tuple(candidate[value] for value in tail)
            else:
                output_tail = _decoy_tail(
                    adversary_index, index, tail, candidate, audit
                )
            keys.append(
                key_prefix
                + "".join(CORE_OUTPUTS[value] for value in output_tail)
            )
        rows = tuple(
            SyntheticRow(
                edition=edition,
                page=f"f{folio}r",
                locus=f"P.{folio}",
                groups=tuple(raw_types[:256] if folio == 1 else raw_types[256:]),
                separators=(".",) * 255,
            )
            for edition in EDITION_ORDER
            for folio in range(1, 33)
        )
        return _world_from_parts(
            world_id=world_id,
            adversary_index=adversary_index,
            candidate_rank=candidate_rank,
            candidate_audit=candidate_audit,
            additional_audit=audit,
            rows=rows,
            keys=keys,
            expected=expected_world_signature(
                "ADVERSARY_ONE_FOLIO_CONCENTRATION_SIGNATURE"
            ),
            secret_rank=candidate_rank,
            alternate_rank=None,
        )

    if world_id == "PREFIX_ONLY":
        groups = tuple(
            "t" + five_tail_prefix(index)[0]
            + _render_input_tail(five_input_tail(index))
            for index in range(256)
        )
        keys = tuple(
            five_tail_prefix(index)[1]
            + _render_output_tail(candidate, five_input_tail(index))
            for index in range(256)
        )
        return _world_from_parts(
            world_id=world_id,
            adversary_index=adversary_index,
            candidate_rank=candidate_rank,
            candidate_audit=candidate_audit,
            rows=_uniform_rows(groups),
            keys=keys,
            expected=expected_world_signature(
                "ADVERSARY_PREFIX_ONLY_SIGNATURE"
            ),
            secret_rank=candidate_rank,
            alternate_rank=None,
        )

    if world_id == "UNKNOWN_SKIP":
        groups = tuple(value + "b" for value in _base_groups(10))
        keys = _coherent_keys(candidate, variable_count=10)
        return _world_from_parts(
            world_id=world_id,
            adversary_index=adversary_index,
            candidate_rank=candidate_rank,
            candidate_audit=candidate_audit,
            rows=_uniform_rows(groups),
            keys=keys,
            expected=expected_world_signature(
                "ADVERSARY_UNKNOWN_SKIP_SIGNATURE"
            ),
            secret_rank=candidate_rank,
            alternate_rank=None,
        )

    if world_id == "ONE_READING_WRONG":
        raw_types = tuple(
            five_tail_prefix(index)[0]
            + _render_input_tail(five_input_tail(index))
            for index in range(512)
        )
        keys = tuple(
            five_tail_prefix(index)[1]
            + _render_output_tail(
                candidate if index < 256 else alternate,
                five_input_tail(index),
            )
            for index in range(512)
        )
        rows = tuple(
            SyntheticRow(
                edition=edition,
                page=f"f{folio}r",
                locus=f"P.{folio}",
                groups=raw_types[:256] if edition != "RF1b" else raw_types[256:],
                separators=(".",) * 255,
            )
            for edition in EDITION_ORDER
            for folio in range(1, 33)
        )
        return _world_from_parts(
            world_id=world_id,
            adversary_index=adversary_index,
            candidate_rank=candidate_rank,
            candidate_audit=candidate_audit,
            rows=rows,
            keys=keys,
            expected=expected_world_signature(
                "ADVERSARY_ONE_READING_WRONG_SIGNATURE"
            ),
            secret_rank=None,
            alternate_rank=alternate_rank,
        )

    raise AssertionError(world_id)


def build_parser_fixture() -> tuple[tuple[SyntheticRow, ...], dict[str, object]]:
    groups = ("k[dr:sy]", "l[ny]", "q{abc}y", "m<note>g", "kd")
    separators = (",", "<->", "<~>", ".")
    rows = tuple(
        SyntheticRow(edition, "f1r", "P.1", groups, separators)
        for edition in EDITION_ORDER
    )
    canonical_rows = canonicalize_rows(rows)
    row_digests, rows_digest = _row_hashes(canonical_rows)
    projections = {
        name: panel_projection(canonical_rows, name)
        for name in PANEL_ORDER
    }
    record = {
        "fixture_id": "PARSER_CANONICAL",
        "row_count": len(canonical_rows),
        "row_sha256s": list(row_digests),
        "rows_sha256": rows_digest,
        "dot_panel_sha256": sha256_bytes(
            canonical_json_bytes(list(projections["DOT_ONLY_EMULATION"]))
        ),
        "manual_panel_sha256": sha256_bytes(
            canonical_json_bytes(list(projections["MANUAL_GROUP"]))
        ),
        "strict_literal_counts": {
            name: sum(bool(item["strict_literal_eligible"]) for item in projection)
            for name, projection in projections.items()
        },
        "expected": {
            "assertion_count": 4,
            "assertions": [
                {"id": "PARSER_PRIMARY_SELECTION", "operator": "PARSER_FIXTURE", "value": True},
                {"id": "PARSER_SEPARATOR_STATES", "operator": "PARSER_FIXTURE", "value": True},
                {"id": "PARSER_PANEL_INDEPENDENCE", "operator": "PARSER_FIXTURE", "value": True},
                {"id": "PARSER_STRICT_PROPAGATION", "operator": "PARSER_FIXTURE", "value": True},
            ],
        },
    }
    return canonical_rows, record


def _mutation_record(
    mutation_id: str,
    base_world_id: str,
    payload: bytes,
    expected_status: str,
    expected_equalities: dict[str, object],
    *,
    payload_sha256s: dict[str, str] | None = None,
) -> dict[str, object]:
    if expected_status not in {
        "EXPECTED_HARD_STOP",
        "EXPECTED_BYTE_INVARIANCE",
        "EXPECTED_DECLARED_CHANGE",
    }:
        raise DANI001SyntheticError("unknown mutation expected status")
    mutated_digest = sha256_bytes(payload)
    digests = payload_sha256s or {"mutated": mutated_digest}
    if any(not HEX64_RE.fullmatch(value) for value in digests.values()):
        raise DANI001SyntheticError("invalid mutation component digest")
    return {
        "mutation_id": mutation_id,
        "assertion_id": f"MUTATION_{mutation_id}",
        "base_world_id": base_world_id,
        "operation": mutation_id,
        "mutated_input_sha256": mutated_digest,
        "payload_sha256s": digests,
        "expected_status": expected_status,
        "expected_equalities": expected_equalities,
    }


def _rows_bytes(rows: Sequence[SyntheticRow]) -> bytes:
    return canonical_json_bytes([row.to_object() for row in rows])


def build_mutation_records(
    plant_zero: SyntheticWorld,
    parser_rows: Sequence[SyntheticRow],
) -> tuple[dict[str, object], ...]:
    """Return the exact ordered hash-only mutation manifest records."""

    base_rows = canonicalize_rows(plant_zero.rows)
    output: list[dict[str, object]] = []
    output.append(_mutation_record(
        "EMPTY_PANEL", "PLANT_000", canonical_json_bytes([]),
        "EXPECTED_HARD_STOP", {"empty_panel_rejected": True},
    ))
    output.append(_mutation_record(
        "DUPLICATE_ROW", "PLANT_000", _rows_bytes(base_rows + (base_rows[0],)),
        "EXPECTED_HARD_STOP", {"duplicate_row_rejected": True},
    ))

    first_record = plant_zero.lexicon[0]
    encoded_key = json.dumps(first_record["key"], ensure_ascii=True)
    encoded_entries = json.dumps(
        first_record["entries"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    encoded_records = [
        (
            "{\"entries\":" + encoded_entries + ",\"key\":" + encoded_key
            + ",\"key\":" + encoded_key + "}"
        )
    ]
    encoded_records.extend(
        json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        for record in plant_zero.lexicon[1:]
    )
    duplicate_object = ("[" + ",".join(encoded_records) + "]\n").encode("utf-8")
    output.append(_mutation_record(
        "DUPLICATE_JSON_KEY", "PLANT_000", duplicate_object,
        "EXPECTED_HARD_STOP", {"duplicate_json_key_rejected": True},
    ))

    reversed_tokens = tuple(
        replace(row, groups=row.groups[::-1], separators=row.separators[::-1])
        for row in base_rows
    )
    output.append(_mutation_record(
        "TOKEN_REVERSE", "PLANT_000", _rows_bytes(reversed_tokens),
        "EXPECTED_BYTE_INVARIANCE",
        {"input_rows_equal": False, "score_vectors_equal": True},
    ))
    output.append(_mutation_record(
        "ROW_REVERSE", "PLANT_000", _rows_bytes(base_rows[::-1]),
        "EXPECTED_BYTE_INVARIANCE",
        {"input_rows_equal": False, "score_vectors_equal": True},
    ))
    reversed_lexicon = tuple(
        {"key": value["key"], "entries": list(reversed(value["entries"]))}
        for value in reversed(plant_zero.lexicon)
    )
    output.append(_mutation_record(
        "LEXICON_REVERSE", "PLANT_000", canonical_json_bytes(list(reversed_lexicon)),
        "EXPECTED_BYTE_INVARIANCE",
        {"projected_sets_equal": True, "score_vectors_equal": True},
    ))

    malformed = (
        ("UNMATCHED_SQUARE", "[k"),
        ("NESTED_SQUARE", "[[k]]"),
        ("UNMATCHED_BRACE", "{k"),
        ("NESTED_BRACE", "{{k}}"),
        ("UNMATCHED_ANGLE", "<k"),
        ("NESTED_ANGLE", "<<k>>"),
    )
    parser_base = tuple(parser_rows)
    for mutation_id, replacement_group in malformed:
        first = parser_base[0]
        changed_first = replace(
            first,
            groups=(replacement_group, *first.groups[1:]),
        )
        changed = (changed_first, *parser_base[1:])
        output.append(_mutation_record(
            mutation_id,
            "PARSER_CANONICAL",
            _rows_bytes(changed),
            "EXPECTED_HARD_STOP",
            {"panel_digest_created": False},
        ))

    overlength_record = {
        "key": "kkkkkkkkkkk",
        "entries": _entries(),
    }
    output.append(_mutation_record(
        "OVERLENGTH_PREIMAGE",
        "PLANT_000",
        canonical_json_bytes([*plant_zero.lexicon, overlength_record]),
        "EXPECTED_HARD_STOP",
        {"source_panel_opened": False},
    ))
    first = base_rows[0]
    overlength_first = replace(
        first,
        groups=(*first.groups, "kdrslnqymgk"),
        separators=(*first.separators, "."),
    )
    output.append(_mutation_record(
        "OVERLENGTH_TOKEN",
        "PLANT_000",
        _rows_bytes((overlength_first, *base_rows[1:])),
        "EXPECTED_DECLARED_CHANGE",
        {"always_unmatched": True, "denominator_delta": 1},
    ))
    unknown_rows = tuple(
        replace(row, groups=tuple(group + "b" for group in row.groups))
        for row in base_rows
    )
    output.append(_mutation_record(
        "UNKNOWN_INSERT", "PLANT_000", _rows_bytes(unknown_rows),
        "EXPECTED_DECLARED_CHANGE",
        {"default_vectors_equal": True, "strict_instances_removed": 24576},
    ))
    missing_edition = tuple(row for row in base_rows if row.edition != "RF1b")
    output.append(_mutation_record(
        "MISSING_EDITION", "PLANT_000", _rows_bytes(missing_edition),
        "EXPECTED_HARD_STOP", {"missing_rf_rejected": True},
    ))

    first_object = base_rows[0].to_object()
    first_object["page"] = "fRos"
    page_objects = [first_object, *(row.to_object() for row in base_rows[1:])]
    output.append(_mutation_record(
        "PAGE_DOMAIN", "PLANT_000", canonical_json_bytes(page_objects),
        "EXPECTED_HARD_STOP", {"nonnumeric_page_rejected": True},
    ))
    drift_object = base_rows[0].to_object()
    drift_object["page"] = "f2r"
    drift_objects = [drift_object, *(row.to_object() for row in base_rows[1:])]
    output.append(_mutation_record(
        "FOLIO_DRIFT", "PLANT_000", canonical_json_bytes(drift_objects),
        "EXPECTED_HARD_STOP", {"page_locus_disagreement_rejected": True},
    ))
    without_unreachable = tuple(
        value for value in plant_zero.lexicon
        if is_reachable_key(value["key"])  # type: ignore[arg-type]
    )
    full_bytes = canonical_json_bytes(list(plant_zero.lexicon))
    without_bytes = canonical_json_bytes(list(without_unreachable))
    removed = tuple(
        value for value in plant_zero.lexicon
        if not is_reachable_key(value["key"])  # type: ignore[arg-type]
    )
    removed_bytes = canonical_json_bytes(list(removed))
    if len(removed) != 570:
        raise DANI001SyntheticError("unreachable mutation inventory drift")
    output.append(_mutation_record(
        "UNREACHABLE_REMOVE",
        "PLANT_000",
        without_bytes,
        "EXPECTED_BYTE_INVARIANCE",
        {"raw_vectors_equal": True, "standardized_vectors_equal": True},
        payload_sha256s={
            "full": sha256_bytes(full_bytes),
            "removed_records": sha256_bytes(removed_bytes),
            "without": sha256_bytes(without_bytes),
        },
    ))
    restored = tuple(sorted(
        (*without_unreachable, *removed),
        key=lambda value: str(value["key"]).encode("utf-8"),
    ))
    restored_bytes = canonical_json_bytes(list(restored))
    if restored_bytes != full_bytes:
        raise DANI001SyntheticError("unreachable restore failed byte identity")
    output.append(_mutation_record(
        "UNREACHABLE_RESTORE_ADD_FROM_REMOVED",
        "PLANT_000_WITHOUT_UNREACHABLE",
        restored_bytes,
        "EXPECTED_BYTE_INVARIANCE",
        {
            "full_lexicon_bytes_equal": True,
            "raw_vectors_equal": True,
            "standardized_vectors_equal": True,
        },
        payload_sha256s={
            "removed_records": sha256_bytes(removed_bytes),
            "restored": sha256_bytes(restored_bytes),
            "without": sha256_bytes(without_bytes),
        },
    ))
    if len(output) != 20:
        raise DANI001SyntheticError("mutation inventory drift")
    return tuple(output)


def build_all_worlds() -> tuple[SyntheticWorld, ...]:
    """Construct all 238 scored synthetic worlds in memory, without scoring."""

    worlds: list[SyntheticWorld] = [
        build_toy_world(4, plant=True),
        build_toy_world(4, plant=False),
        build_toy_world(6, plant=True),
        build_toy_world(6, plant=False),
    ]
    plant_ranks = unique_nonidentity_ranks("plant-map-rank", 100)
    worlds.extend(
        build_plant_world(index, rank, audit)
        for index, (rank, audit) in enumerate(plant_ranks)
    )
    null_ranks = unique_nonidentity_ranks("null-probe-rank", 128)
    worlds.extend(
        build_null_world(index, rank, audit)
        for index, (rank, audit) in enumerate(null_ranks)
    )
    adversary_ranks = unique_nonidentity_ranks("adversary-candidate-rank", 6)
    worlds.extend(
        build_adversary_world(index, rank, audit)
        for index, (rank, audit) in enumerate(adversary_ranks)
    )
    if len(worlds) != 238 or len({world.world_id for world in worlds}) != 238:
        raise DANI001SyntheticError("scored synthetic world inventory drift")
    return tuple(worlds)


def iter_scored_worlds() -> Iterator[SyntheticWorld]:
    """Stable streaming API in the exact registered world order."""

    yield from build_all_worlds()


def verify_calibration_spec(
    expected_spec_sha256: str,
    spec_path: Path = CALIBRATION_SPEC_PATH,
) -> None:
    if not HEX64_RE.fullmatch(expected_spec_sha256):
        raise DANI001SyntheticError("expected calibration-spec SHA is malformed")
    if expected_spec_sha256 != CALIBRATION_SPEC_SHA256:
        raise DANI001SyntheticError("caller expected a different calibration spec")
    if sha256_path(spec_path) != CALIBRATION_SPEC_SHA256:
        raise DANI001SyntheticError("calibration specification hash drift")


def build_synthetic_manifest(expected_spec_sha256: str) -> dict[str, object]:
    """Build the complete hash-only registered manifest in memory."""

    verify_calibration_spec(expected_spec_sha256)
    worlds = build_all_worlds()
    parser_rows, parser_record = build_parser_fixture()
    plant_zero = next(world for world in worlds if world.world_id == "PLANT_000")
    mutations = build_mutation_records(plant_zero, parser_rows)
    protocol_projection = {"labels": list(COUNTER_LABELS), "root": ROOT_DOMAIN}
    _conjugacy, conjugacy_audit = first_nonidentity_permutation(
        "conjugacy-permutation", 10
    )
    control_order = (
        "toys",
        "plants",
        "nulls",
        "adversaries",
        "parser",
        "mutations",
        "conjugacy",
        "workers",
        "affix_equivalence",
        "unreachable_invariance",
    )
    assertion_ids: dict[str, list[str]] = {
        "toys": [
            "TOY4_PLANT_COMPLETE_EQUALITY",
            "TOY4_NULL_COMPLETE_EQUALITY",
            "TOY6_PLANT_COMPLETE_EQUALITY",
            "TOY6_NULL_COMPLETE_EQUALITY",
        ],
        "plants": [f"PLANT_{index:03d}_SUCCESS" for index in range(100)],
        "nulls": [
            *(f"NULL_{index:03d}_PROBE_INDEPENDENCE" for index in range(128)),
            "NULL_FALSE_PASS_COUNT_LE_1",
        ],
        "adversaries": [
            f"ADVERSARY_{world_id}_SIGNATURE"
            for world_id in WORLD_IDS_ADVERSARY
        ],
        "parser": [
            "PARSER_PRIMARY_SELECTION",
            "PARSER_SEPARATOR_STATES",
            "PARSER_PANEL_INDEPENDENCE",
            "PARSER_STRICT_PROPAGATION",
        ],
        "mutations": [str(value["assertion_id"]) for value in mutations],
        "conjugacy": ["CONJUGACY_VECTOR_EQUALITY"],
        "workers": ["WORKER_1_32_VECTOR_EQUALITY"],
        "affix_equivalence": [
            f"AFFIX_{world.world_id}_EQUIVALENCE" for world in worlds
        ],
        "unreachable_invariance": [
            f"UNREACHABLE_{world.world_id}_INVARIANCE"
            for world in worlds
            if world.variable_count == 10
        ],
    }
    totals = {name: len(assertion_ids[name]) for name in control_order}
    if totals != {
        "toys": 4,
        "plants": 100,
        "nulls": 129,
        "adversaries": 6,
        "parser": 4,
        "mutations": 20,
        "conjugacy": 1,
        "workers": 1,
        "affix_equivalence": 238,
        "unreachable_invariance": 234,
    } or sum(totals.values()) != 737:
        raise DANI001SyntheticError("atomic assertion inventory drift")
    return {
        "schema": "dani001-synthetic-manifest-v1",
        "science_spec": {
            "commit": SCIENCE_COMMIT,
            "path": SCIENCE_SPEC_REL,
            "sha256": SCIENCE_SPEC_SHA256,
        },
        "calibration_spec": {
            "path": CALIBRATION_SPEC_REL,
            "sha256": CALIBRATION_SPEC_SHA256,
        },
        "counter_protocol": {
            "root": ROOT_DOMAIN,
            "labels": list(COUNTER_LABELS),
            "sha256": sha256_bytes(canonical_json_bytes(protocol_projection)),
        },
        "worlds": [world.manifest_record() for world in worlds],
        "parser_fixture": parser_record,
        "mutations": list(mutations),
        "aggregate_expectations": {
            "control_order": list(control_order),
            "assertion_ids": assertion_ids,
            "totals": totals,
            "generator_fields": {
                "conjugacy": [value.to_manifest() for value in conjugacy_audit],
            },
            "plant_success_min": 95,
            "null_false_pass_max": 1,
            "world_count": 238,
            "atomic_assertion_count": 737,
        },
    }


def manifest_bytes(expected_spec_sha256: str) -> bytes:
    return canonical_json_bytes(build_synthetic_manifest(expected_spec_sha256))


def write_manifest_no_clobber(expected_spec_sha256: str) -> str:
    """Build and atomically install the one fixed manifest destination."""

    verify_calibration_spec(expected_spec_sha256)
    if MANIFEST_PATH.exists() or MANIFEST_PATH.is_symlink():
        raise DANI001SyntheticError("synthetic manifest destination already exists")
    data = manifest_bytes(expected_spec_sha256)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".dani001-synthetic-manifest-",
        dir=MANIFEST_PATH.parent,
    ) as directory:
        temporary = Path(directory) / "DANI001_SYNTHETIC_MANIFEST.json"
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb", closefd=True) as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        except BaseException:
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise
        try:
            os.link(temporary, MANIFEST_PATH)
        except FileExistsError as error:
            raise DANI001SyntheticError(
                "synthetic manifest no-clobber collision"
            ) from error
    return sha256_bytes(data)


def source_free_smoke() -> dict[str, object]:
    """Tiny deterministic fake smoke; it constructs no registered world."""

    draw_a = bounded_draw("toy-map-rank", 24, 4, 99)
    draw_b = bounded_draw("toy-map-rank", 24, 4, 99)
    if draw_a != draw_b:
        raise DANI001SyntheticError("counter smoke is nondeterministic")
    fake_ranks = (0, 1, 7, 23)
    for rank in fake_ranks:
        if rank_lex(unrank_lex(4, rank)) != rank:
            raise DANI001SyntheticError("rank/unrank smoke mismatch")
    prefixes = tuple(ordinary_prefix(index) for index in (0, 1, 15, 16, 255))
    for raw_prefix, key_prefix in prefixes:
        compiled = compile_source_token(raw_prefix + "kdrs", 1)
        if compiled is None or len(key_prefix) != 2:
            raise DANI001SyntheticError("deleted-vowel prefix smoke failed")
    return {
        "counter_draw": draw_a,
        "fake_rank_count": len(fake_ranks),
        "prefix_count": len(prefixes),
        "registered_worlds_constructed": 0,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the frozen source-free DANI001 synthetic manifest."
    )
    parser.add_argument(
        "--expected-spec-sha",
        required=True,
        help="Required exact SHA-256 of DANI001_TARGET_BLIND_CALIBRATION_SPEC.md",
    )
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="Required explicit authorization to write the one fixed manifest path",
    )
    args = parser.parse_args(argv)
    if not args.write_manifest:
        parser.error("--write-manifest is required; there is no implicit dry-run output")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    digest = write_manifest_no_clobber(args.expected_spec_sha)
    print(f"{MANIFEST_PATH.name} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
