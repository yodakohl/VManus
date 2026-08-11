#!/usr/bin/env python3
"""Clean-room validator for the DANI001 target-blind calibration.

This file deliberately does not import the producer, panel builder, synthetic
generator, or integer core.  Its registered execution path reconstructs the
synthetic manifest and all numerical decisions from the two prose contracts,
then conditionally reconstructs nonidentity-only actual capacity.  ``--self-test``
uses fabricated four-variable objects only and performs no repository data or
network access.
"""

from __future__ import annotations

import argparse
import builtins
import ctypes
import csv
import gc
import hashlib
import importlib.metadata
import io
import itertools
import json
import locale
import math
import multiprocessing
import os
import platform
import re
import socket
import ssl
import stat
import struct
import sys
import tempfile
import time
import urllib.error
import urllib.request
from array import array
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "experiments" / "semantic_assumptions"
RESULTS = MOD / "results"

SCIENCE_REL = "experiments/semantic_assumptions/DANI001_FIXED_MAPPING_DIAGNOSTIC_SPEC.md"
CALIBRATION_REL = "experiments/semantic_assumptions/DANI001_TARGET_BLIND_CALIBRATION_SPEC.md"
MANIFEST_REL = "experiments/semantic_assumptions/DANI001_SYNTHETIC_MANIFEST.json"
FREEZE_REL = "experiments/semantic_assumptions/DANI001_CALIBRATION_FREEZE.json"
PRODUCER_RESULT_REL = "experiments/semantic_assumptions/results/dani001_target_blind_calibration.json"
PRODUCER_REPORT_REL = "experiments/semantic_assumptions/results/dani001_target_blind_calibration.md"
VALIDATION_RESULT_REL = "experiments/semantic_assumptions/results/dani001_target_blind_calibration_validation.json"
VALIDATION_REPORT_REL = "experiments/semantic_assumptions/results/dani001_target_blind_calibration_validation.md"

SCIENCE_COMMIT = "1faa87f"
SCIENCE_SHA = "cc73479b3c35eaa87a3f56184fc3472fe6232b67c13deb3bf30ef8555a6c8426"
CALIBRATION_SHA = "f38de851d96e5fbb3a9a8bbb7ecd9c925ee34e4cb1c181970b6f582fbdea9c32"
MANIFEST_SHA = "0931be3e683d2badcdaa08bf125de5f4a4b6dbe292305197c663f6cdf3075f80"

SCHEMA_MANIFEST = "dani001-synthetic-manifest-v1"
SCHEMA_RESULT = "dani001-target-blind-calibration-result-v1"
SCHEMA_VALIDATION = "dani001-target-blind-calibration-validation-v1"
CLAIM_CEILING = "Target-blind engineering calibration only; no language, lexeme, plaintext, or translation."
WIDTH10_WORLD_WORKERS = 1
MAX_LIVE_VECTOR_STATES = 2
WIDTH10_PROCESS_MEMORY_BOUND = 1536 * 1024 * 1024

ROOT_DOMAIN = "DANI001-TARGET-BLIND-CALIBRATION-V1"
COUNTER_LABELS = (
    "plant-map-rank", "null-probe-rank", "null-key-tail",
    "adversary-candidate-rank", "adversary-decoy-tail",
    "toy-map-rank", "conjugacy-permutation",
)
EDITIONS = ("ZL3b", "IT2a", "RF1b")
PANELS = ("DOT_ONLY_EMULATION", "MANUAL_GROUP")
CORE_IN = ("k", "d", "r", "s", "l", "n", "q", "y", "m", "g")
CORE_OUT = ("k", "d", "r", "s", "l", "n", "w", "y", "m", "g")
MARKER_RAW = ("sh", "t", "p", "f")
MARKER_OUT = ("š", "ṭ", "p", "ṣ")
VOWELS = ("a", "o", "e", "i")
NIBBLES = ("k", "d", "r", "s", "l", "n", "w", "y", "m", "g", "š", "ṭ", "p", "ṣ")
NIBBLE = {value: index for index, value in enumerate(NIBBLES, 1)}
CORE_OUTPUT_INDEX = {NIBBLE[value]: index for index, value in enumerate(CORE_OUT)}
SYNTH_DOMAINS = ("astro", "botanical", "general", "medical", "pharma")
ALL_DOMAINS = ("astro", "botanical", "function", "general", "medical", "pharma")
ADVERSARIES = (
    "FIXED_HEAVY_HIGH_COVERAGE", "ONE_TYPE_CONCENTRATION",
    "ONE_FOLIO_CONCENTRATION", "PREFIX_ONLY", "UNKNOWN_SKIP",
    "ONE_READING_WRONG",
)
SCORING_VIEWS = (
    "FULL_DEPOSITED_AFFIX", "DIRECT_ONLY", "STRICT_NO_FUNCTION",
    "STRICT_LITERAL", "TOP20_DELETED", "SOURCE_PRESENT",
    "LEAVE_ASTRO_OUT", "LEAVE_BOTANICAL_OUT", "LEAVE_FUNCTION_OUT",
    "LEAVE_GENERAL_OUT", "LEAVE_MEDICAL_OUT", "LEAVE_PHARMA_OUT",
)
CONTROL_ORDER = (
    "toys", "plants", "nulls", "adversaries", "parser", "mutations",
    "conjugacy", "workers", "affix_equivalence", "unreachable_invariance",
)
SEPARATORS = (".", ",", "<->", "<~>")
SEPARATOR_NAME = {
    ".": "CONFIDENT_APPARENT_SPACE",
    ",": "UNCERTAIN_SMALL_SPACE",
    "<->": "DRAWING_INTERRUPTION",
    "<~>": "UNALIGNED_DRAWING_INTERRUPTION",
}
PAGE_SYNTH = re.compile(r"^f([1-9][0-9]*)r$")
PAGE_REAL = re.compile(r"^f([0-9]+)[rv][0-9]*$")
PAGE_HEADER = re.compile(r"^<([^>.]+)>\s+<!(.*)>")
SOURCE_ROW = re.compile(r"^<([^,]+),([^>]*)>\s*(?:<!([^>]*)>)?\s*(.*)$")
METADATA = re.compile(r"\$([A-Z])=([^\s>]+)")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SSL_CONTEXT = ssl.create_default_context()
try:
    LIVE_NUMPY_VERSION = importlib.metadata.version("numpy")
except importlib.metadata.PackageNotFoundError:
    LIVE_NUMPY_VERSION = "MISSING"

ATOM: dict[str, tuple[int, ...]] = {
    "cth": (NIBBLE["ṭ"], NIBBLE["k"]),
    "ckh": (NIBBLE["k"], NIBBLE["k"]),
    "cph": (NIBBLE["p"], NIBBLE["k"]),
    "cfh": (NIBBLE["p"], NIBBLE["k"]),
    "sh": (NIBBLE["š"],), "ch": (NIBBLE["k"],),
    **{value: (-(index + 1),) for index, value in enumerate(CORE_IN)},
    "t": (NIBBLE["ṭ"],), "p": (NIBBLE["p"],), "f": (NIBBLE["ṣ"],),
    "a": (), "o": (), "e": (), "i": (), "x": (), "h": (),
}

EXTERNAL_URLS = (
    "https://zenodo.org/api/records/19583305",
    "https://zenodo.org/api/records/19609475/files/pipeline_v31_1.py/content",
    "https://zenodo.org/api/records/19609475/files/lexicon_v31_session31_final.json/content",
)
ATLAS_COLUMNS = (
    "source_group_id", "edition", "locus", "page", "section", "currier", "hand",
    "code", "kind", "grammar_scope", "source_row_index", "source_group_index",
    "source_group_count", "paragraph_start", "paragraph_end", "left_separator",
    "right_separator", "ivtff_group_raw", "clean_ascii_fragments",
    "clean_ascii_fragment_count", "legacy_surface_positions_1based",
    "legacy_interlinear_row_present", "legacy_mapping_status",
)
ATLAS_SEPARATOR = {
    ".": "DEFINITE_SPACE", ",": "UNCERTAIN_SMALL_SPACE",
    "<->": "DRAWING_INTERRUPTION", "<~>": "DRAWING_INTERRUPTION_UNALIGNED",
}
SOURCE_REL = {
    "ZL3b": "transcription/sources/ZL3b-n.txt",
    "IT2a": "transcription/sources/IT2a-n.txt",
    "RF1b": "transcription/sources/RF1b-e.txt",
}
LOCAL_SHA = {
    "transcription/sources/ZL3b-n.txt": "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "transcription/sources/IT2a-n.txt": "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    "transcription/sources/RF1b-e.txt": "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
    "experiments/semantic_assumptions/results/source_separator_transcription.tsv": "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    "experiments/semantic_assumptions/results/source_separator_transcription_validation.json": "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
}
ATLAS_REL = "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ATLAS_VALIDATION_REL = "experiments/semantic_assumptions/results/source_separator_transcription_validation.json"


class ValidationStop(RuntimeError):
    """A contract failure that installs no validation output."""


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
            size += len(block)
    return h.hexdigest(), size


def strict_json(data: bytes) -> Any:
    def unique(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise ValidationStop("duplicate JSON member")
            out[key] = value
        return out
    try:
        return json.loads(
            data.decode("utf-8", "strict"), object_pairs_hook=unique,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValidationStop(f"nonfinite JSON constant: {value}")))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValidationStop("invalid canonical JSON") from error


def exact_keys(value: Mapping[str, Any], names: Sequence[str], label: str) -> None:
    if set(value) != set(names):
        raise ValidationStop(f"{label} member drift")


def exact_json_equal(actual: object, expected: object, label: str) -> None:
    """JSON equality with no Python bool/int or subclass coercions."""
    if type(actual) is not type(expected):
        raise ValidationStop(f"{label} JSON type drift")
    if isinstance(expected, dict):
        if list(actual.keys()) != list(expected.keys()):
            # Member order is not semantic, but exact membership is.
            if set(actual) != set(expected):
                raise ValidationStop(f"{label} JSON member drift")
        for key in expected:
            exact_json_equal(actual[key], expected[key], f"{label}.{key}")
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            raise ValidationStop(f"{label} JSON array length drift")
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            exact_json_equal(left, right, f"{label}[{index}]")
    elif actual != expected:
        raise ValidationStop(f"{label} JSON value drift")
    if isinstance(expected, (dict, list)) and canonical(actual) != canonical(expected):
        raise ValidationStop(f"{label} canonical subtree bytes drift")


def json_int(value: object, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValidationStop(f"{label} integer drift")
    return value


def json_bool(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise ValidationStop(f"{label} boolean drift")
    return value


@dataclass(frozen=True, slots=True)
class Draw:
    label: str
    fields: tuple[int, ...]
    result: int

    def object(self) -> list[object]:
        return [self.label, list(self.fields), self.result]


def counter_hash(label: str, *fields: int) -> int:
    if label not in COUNTER_LABELS or any(type(v) is not int or not 0 <= v < 2**64 for v in fields):
        raise ValidationStop("counter domain violation")
    encoded = label.encode("ascii")
    body = bytearray(ROOT_DOMAIN.encode("ascii") + b"\0")
    body.extend(struct.pack("<H", len(encoded)))
    body.extend(encoded)
    body.extend(struct.pack("<H", len(fields)))
    for value in fields:
        body.extend(struct.pack("<Q", value))
    return int.from_bytes(hashlib.sha256(body).digest(), "little")


def draw(label: str, modulus: int, *fields: int, log: list[Draw] | None = None) -> int:
    if type(modulus) is not int or not 1 <= modulus <= 2**64:
        raise ValidationStop("invalid bounded-draw modulus")
    limit = (2**256 // modulus) * modulus
    attempt = 0
    while True:
        value = counter_hash(label, *fields, attempt)
        if value < limit:
            result = value % modulus
            if log is not None:
                log.append(Draw(label, (modulus, *fields), result))
            return result
        attempt += 1


def counter_perm(label: str, width: int, *fields: int,
                 log: list[Draw] | None = None) -> tuple[int, ...]:
    if width not in range(1, 11):
        raise ValidationStop("permutation width violation")
    values = list(range(width))
    for completed, index in enumerate(range(width - 1, 0, -1)):
        other = draw(label, index + 1, *fields, completed, log=log)
        values[index], values[other] = values[other], values[index]
    return tuple(values)


def rank_perm(values: Sequence[int]) -> int:
    values = tuple(values)
    if sorted(values) != list(range(len(values))):
        raise ValidationStop("nonpermutation")
    remaining = list(range(len(values)))
    rank = 0
    for index, value in enumerate(values):
        ordinal = remaining.index(value)
        rank += ordinal * math.factorial(len(values) - index - 1)
        remaining.pop(ordinal)
    return rank


def unrank_perm(width: int, rank: int) -> tuple[int, ...]:
    if width not in range(1, 11) or not 0 <= rank < math.factorial(width):
        raise ValidationStop("rank outside permutation orbit")
    remaining = list(range(width))
    output: list[int] = []
    for n in range(width, 0, -1):
        place, rank = divmod(rank, math.factorial(n - 1))
        output.append(remaining.pop(place))
    return tuple(output)


def unique_ranks(label: str, count: int, width: int = 10) -> tuple[tuple[int, tuple[Draw, ...]], ...]:
    used: set[int] = set()
    output: list[tuple[int, tuple[Draw, ...]]] = []
    modulus = math.factorial(width) - 1
    for sequence in range(count):
        collision = 0
        log: list[Draw] = []
        while True:
            candidate = 1 + draw(label, modulus, sequence, collision, log=log)
            if candidate not in used:
                used.add(candidate)
                output.append((candidate, tuple(log)))
                break
            collision += 1
    return tuple(output)


def first_nonidentity(label: str, width: int, *fields: int) -> tuple[tuple[int, ...], tuple[Draw, ...]]:
    attempt = 0
    log: list[Draw] = []
    while True:
        candidate = counter_perm(label, width, *fields, attempt, log=log)
        if candidate != tuple(range(width)):
            return candidate, tuple(log)
        attempt += 1


def base4(width: int, value: int) -> tuple[int, ...]:
    if not 0 <= value < 4**width:
        raise ValidationStop("tag outside width")
    result = [0] * width
    for position in range(width - 1, -1, -1):
        result[position], value = value % 4, value // 4
    return tuple(result)


def tag(width: int, value: int) -> str:
    return "".join(MARKER_RAW[index] for index in base4(width, value))


def keytag(width: int, value: int) -> str:
    return "".join(MARKER_OUT[index] for index in base4(width, value))


def vtag(width: int, value: int) -> str:
    return "".join(VOWELS[index] for index in base4(width, value))


def ordinary_prefix(index: int) -> tuple[str, str]:
    return vtag(2, index % 16) + tag(2, index // 16), keytag(2, index // 16)


def five_prefix(index: int) -> tuple[str, str]:
    block, local = divmod(index, 256)
    marker = 32 * block + 2 * (local // 16) + local % 2
    vowel = (local % 16) // 2
    return vtag(2, vowel) + tag(3, marker), keytag(3, marker)


def concentration_prefix(index: int) -> tuple[str, str]:
    if index <= 8:
        return vtag(2, 0) + tag(3, index), keytag(3, index)
    local = index - 9
    return vtag(2, local % 16) + tag(3, 9 + local // 16), keytag(3, 9 + local // 16)


def six_tail(index: int) -> tuple[int, ...]:
    return (0, 1, 2, 3, 4, 5) if index % 2 == 0 else (4, 5, 6, 7, 8, 9)


def five_tail(index: int) -> tuple[int, ...]:
    return (0, 1, 2, 3, 4) if index % 2 == 0 else (5, 6, 7, 8, 9)


def input_tail(values: Sequence[int]) -> str:
    return "".join(CORE_IN[index] for index in values)


def output_tail(permutation: Sequence[int], values: Sequence[int], width: int = 10) -> str:
    return "".join(CORE_OUT[:width][permutation[index]] for index in values)


def normalize(raw: str) -> tuple[str, bool]:
    output: list[str] = []
    ambiguous = False
    cursor = 0
    delimiters = "[]{}<>"
    while cursor < len(raw):
        value = raw[cursor]
        if value in "[{<":
            close = {"[": "]", "{": "}", "<": ">"}[value]
            end = raw.find(close, cursor + 1)
            if end < 0:
                raise ValidationStop("unmatched annotation")
            body = raw[cursor + 1:end]
            if any(item in delimiters for item in body):
                raise ValidationStop("nested annotation")
            if value == "[":
                output.append(body.split(":", 1)[0])
                ambiguous = True
            elif value == "{":
                ambiguous = True
            elif raw[cursor:end + 1] in {"<->", "<~>"}:
                raise ValidationStop("separator entered token normalizer")
            cursor = end + 1
            continue
        if value in "]}>":
            raise ValidationStop("unmatched closing annotation")
        output.append(value)
        cursor += 1
    lowered = "".join(output).lower()
    return "".join(value for value in lowered if "a" <= value <= "z"), ambiguous


def scan(normalized: str) -> tuple[tuple[int, ...], bool]:
    emitted: list[int] = []
    complete = True
    cursor = 0
    while cursor < len(normalized):
        atom = next((normalized[cursor:cursor + width] for width in (3, 2, 1)
                     if normalized[cursor:cursor + width] in ATOM), None)
        if atom is None:
            complete = False
            cursor += 1
        else:
            emitted.extend(ATOM[atom])
            cursor += len(atom)
    return tuple(emitted), complete


def compile_token(raw: str, folio: int) -> tuple["Token", bool] | None:
    normalized, ambiguity = normalize(raw)
    template, complete = scan(normalized)
    if len(normalized) < 2 or not template:
        return None
    return Token(folio, normalized, template), complete and not ambiguity


@dataclass(frozen=True, slots=True)
class Token:
    folio: int
    normalized: str = field(repr=False)
    template: tuple[int, ...] = field(repr=False)


@dataclass(frozen=True, slots=True)
class Row:
    edition: str
    page: str
    locus: str
    groups: tuple[str, ...] = field(repr=False)
    separators: tuple[str, ...] = field(repr=False)

    def __post_init__(self) -> None:
        match = PAGE_SYNTH.fullmatch(self.page)
        if self.edition not in EDITIONS or match is None:
            raise ValidationStop("invalid synthetic row identity")
        if self.locus != f"P.{int(match.group(1))}" or not self.groups:
            raise ValidationStop("synthetic page/locus drift or empty row")
        if len(self.separators) != len(self.groups) - 1 or any(v not in SEPARATORS for v in self.separators):
            raise ValidationStop("invalid synthetic row topology")

    @property
    def folio(self) -> int:
        match = PAGE_SYNTH.fullmatch(self.page)
        assert match
        return int(match.group(1))

    def obj(self) -> dict[str, object]:
        return {"edition": self.edition, "page": self.page, "locus": self.locus,
                "groups": list(self.groups), "separators": list(self.separators)}


def ordered_rows(rows: Iterable[Row], *, require_all_editions: bool = True) -> tuple[Row, ...]:
    rows = tuple(sorted(rows, key=lambda value: (
        EDITIONS.index(value.edition), value.folio,
        value.page.encode(), value.locus.encode())))
    if not rows or len({(r.edition, r.page, r.locus) for r in rows}) != len(rows):
        raise ValidationStop("empty or duplicate synthetic rows")
    if require_all_editions and {row.edition for row in rows} != set(EDITIONS):
        raise ValidationStop("synthetic panel must contain all three editions")
    return rows


def joined_dot_groups(row: Row) -> tuple[str, ...]:
    output: list[str] = []
    current = row.groups[0]
    for separator, group in zip(row.separators, row.groups[1:], strict=True):
        if separator == ".":
            output.append(current)
            current = group
        else:
            current += group
    output.append(current)
    return tuple(output)


def panel_projection(rows: Iterable[Row], panel: str) -> tuple[dict[str, object], ...]:
    output: list[dict[str, object]] = []
    for row in ordered_rows(rows):
        groups = row.groups if panel == "MANUAL_GROUP" else joined_dot_groups(row)
        for raw in groups:
            compiled = compile_token(raw, row.folio)
            if compiled is None:
                continue
            token, strict = compiled
            output.append({"edition": row.edition, "page": row.page,
                           "locus": row.locus, "folio": row.folio,
                           "normalized_eva": token.normalized,
                           "emitted_template": list(token.template),
                           "strict_literal_eligible": strict})
    return tuple(output)


def uniform_rows(groups: tuple[str, ...]) -> tuple[Row, ...]:
    return tuple(Row(edition, f"f{folio}r", f"P.{folio}", groups,
                     (".",) * (len(groups) - 1))
                 for edition in EDITIONS for folio in range(1, 33))


def base_groups(width: int) -> tuple[str, ...]:
    if width == 10:
        return tuple(ordinary_prefix(i)[0] + input_tail(six_tail(i)) for i in range(256))
    if width in (4, 6):
        return tuple(ordinary_prefix(i)[0] + input_tail(tuple(range(width))) for i in range(256))
    raise ValidationStop("unsupported synthetic width")


def entries() -> list[dict[str, object]]:
    return [{"domain": value, "source_present": True} for value in SYNTH_DOMAINS]


def unreachable(index: int) -> str:
    digits = ((index // 196) % 14, (index // 14) % 14, index % 14)
    return "u" + "".join(NIBBLES[value] for value in digits)


def reachable(key: str) -> bool:
    return bool(key) and all(value in NIBBLE for value in key)


def lexicon(keys: Iterable[str], width: int) -> tuple[dict[str, object], ...]:
    values = set(keys)
    if not values or any(not reachable(key) or len(key) > 8 for key in values):
        raise ValidationStop("synthetic reachable-key invariant")
    if width == 10:
        values.update(unreachable(index) for index in range(570))
    return tuple({"key": key, "entries": entries()}
                 for key in sorted(values, key=lambda item: item.encode()))


def world_assertion(value: str) -> dict[str, object]:
    return {"assertion_count": 1, "assertions": [
        {"id": value, "operator": "WORLD_SIGNATURE", "value": True}]}


@dataclass(frozen=True, slots=True)
class World:
    world_id: str
    family: str
    trial: int
    width: int
    candidate: int
    secret: int | None
    alternate: int | None
    draws: tuple[Draw, ...] = field(repr=False)
    rows: tuple[Row, ...] = field(repr=False)
    lexicon: tuple[dict[str, object], ...] = field(repr=False)
    expected: dict[str, object] = field(repr=False)

    def payload(self) -> dict[str, object]:
        return {"world_id": self.world_id, "variable_count": self.width,
                "candidate_rank": self.candidate, "secret_rank": self.secret,
                "alternate_rank": self.alternate,
                "rows": [row.obj() for row in self.rows], "lexicon": list(self.lexicon)}

    def manifest(self) -> dict[str, object]:
        rows = ordered_rows(self.rows)
        row_hashes = [digest(canonical(row.obj())) for row in rows]
        projected = {panel: panel_projection(rows, panel) for panel in PANELS}
        return {
            "world_id": self.world_id, "family": self.family,
            "trial_index": self.trial, "variable_count": self.width,
            "permutation_count": math.factorial(self.width),
            "candidate_rank": self.candidate, "secret_rank": self.secret,
            "alternate_rank": self.alternate,
            "generator_fields": [value.object() for value in self.draws],
            "row_count": len(rows), "row_sha256s": row_hashes,
            "rows_sha256": digest(b"".join(bytes.fromhex(v) for v in row_hashes)),
            "lexicon_record_count": len(self.lexicon),
            "reachable_key_count": sum(reachable(str(v["key"])) for v in self.lexicon),
            "lexicon_sha256": digest(canonical(list(self.lexicon))),
            "dot_panel_sha256": digest(canonical(list(projected["DOT_ONLY_EMULATION"]))),
            "manual_panel_sha256": digest(canonical(list(projected["MANUAL_GROUP"]))),
            "world_sha256": digest(canonical(self.payload())), "expected": self.expected,
        }


def coherent_keys(permutation: Sequence[int], width: int) -> tuple[str, ...]:
    tail = tuple(range(width))
    return tuple(ordinary_prefix(i)[1] + output_tail(
        permutation, six_tail(i) if width == 10 else tail, width)
        for i in range(256))


def plant_world(index: int, rank: int, draws: Sequence[Draw]) -> World:
    permutation = unrank_perm(10, rank)
    return World(f"PLANT_{index:03d}", "PLANT", index, 10, rank, rank, None,
                 tuple(draws), uniform_rows(base_groups(10)),
                 lexicon(coherent_keys(permutation, 10), 10),
                 world_assertion(f"PLANT_{index:03d}_SUCCESS"))


def null_world(index: int, rank: int, rank_draws: Sequence[Draw]) -> World:
    log = list(rank_draws)
    keys = []
    for item in range(256):
        permutation = counter_perm("null-key-tail", 10, index, item, log=log)
        keys.append(ordinary_prefix(item)[1] + "".join(CORE_OUT[v] for v in permutation[:6]))
    return World(f"NULL_{index:03d}", "NULL", index, 10, rank, None, None,
                 tuple(log), uniform_rows(base_groups(10)), lexicon(keys, 10),
                 world_assertion(f"NULL_{index:03d}_PROBE_INDEPENDENCE"))


def toy_world(width: int, planted: bool) -> World:
    permutation, selection = first_nonidentity("toy-map-rank", width, width, 0 if planted else 1)
    log = list(selection)
    if planted:
        keys = coherent_keys(permutation, width)
    else:
        keys = []
        for item in range(256):
            tail = counter_perm("null-key-tail", width, 1000 + width, item, log=log)
            keys.append(ordinary_prefix(item)[1] + "".join(CORE_OUT[v] for v in tail))
    suffix = "PLANT" if planted else "NULL"
    return World(f"TOY{width}_{suffix}", f"TOY_{suffix}", 0, width,
                 rank_perm(permutation), rank_perm(permutation) if planted else None,
                 None, tuple(log), uniform_rows(base_groups(width)), lexicon(keys, width),
                 world_assertion(f"TOY{width}_{suffix}_COMPLETE_EQUALITY"))


def decoy(adversary: int, item: int, tail: Sequence[int], candidate: Sequence[int],
          log: list[Draw], both: bool = False) -> tuple[int, ...]:
    forbidden = {tuple(candidate[v] for v in tail)}
    if both:
        forbidden = {tuple(candidate[v] for v in (0, 1, 2, 3, 4)),
                     tuple(candidate[v] for v in (5, 6, 7, 8, 9))}
    attempt = 0
    while True:
        value = counter_perm("adversary-decoy-tail", 10, adversary, item, attempt, log=log)[:5]
        if value not in forbidden:
            return value
        attempt += 1


def adversary_world(index: int, rank: int, rank_draws: Sequence[Draw]) -> World:
    name = ADVERSARIES[index]
    candidate = unrank_perm(10, rank)
    alternate = tuple((value + 1) % 10 for value in candidate)
    alternate_rank = rank_perm(alternate)
    log: list[Draw] = []
    rows: tuple[Row, ...]
    keys: list[str] | tuple[str, ...]
    secret: int | None = rank
    alt: int | None = None
    if name == "FIXED_HEAVY_HIGH_COVERAGE":
        variables = tuple(five_prefix(i)[0] + input_tail(five_tail(i)) for i in range(256))
        keys = [five_prefix(i)[1] + output_tail(alternate, five_tail(i)) for i in range(256)]
        fixed_raw, fixed_keys = [], []
        for item in range(64):
            d = base4(3, item)
            fixed_raw.append("cth" + MARKER_RAW[d[0]] + "a" + MARKER_RAW[d[1]] + "o" + MARKER_RAW[d[2]] + "e")
            fixed_keys.append("k" + keytag(3, item))
        rows = uniform_rows(variables + tuple(v for v in fixed_raw for _ in range(100)))
        keys.extend(fixed_keys)
        secret = alternate_rank
        alt = alternate_rank
    elif name == "ONE_TYPE_CONCENTRATION":
        groups, keys = [], []
        for item in range(256):
            tail = five_tail(item)
            raw_prefix, key_prefix = concentration_prefix(item)
            groups.extend([raw_prefix + input_tail(tail)] * (100 if item == 0 else 2 if item <= 8 else 1))
            out = tuple(candidate[v] for v in tail) if item <= 8 else decoy(index, item, tail, candidate, log, True)
            keys.append(key_prefix + "".join(CORE_OUT[v] for v in out))
        rows = uniform_rows(tuple(groups))
    elif name == "ONE_FOLIO_CONCENTRATION":
        groups, keys = [], []
        for item in range(512):
            tail = five_tail(item)
            raw_prefix, key_prefix = five_prefix(item)
            groups.append(raw_prefix + input_tail(tail))
            out = tuple(candidate[v] for v in tail) if item < 256 else decoy(index, item, tail, candidate, log)
            keys.append(key_prefix + "".join(CORE_OUT[v] for v in out))
        rows = tuple(Row(e, f"f{f}r", f"P.{f}", tuple(groups[:256] if f == 1 else groups[256:]), (".",) * 255)
                     for e in EDITIONS for f in range(1, 33))
    elif name == "PREFIX_ONLY":
        groups = tuple("t" + five_prefix(i)[0] + input_tail(five_tail(i)) for i in range(256))
        keys = tuple(five_prefix(i)[1] + output_tail(candidate, five_tail(i)) for i in range(256))
        rows = uniform_rows(groups)
    elif name == "UNKNOWN_SKIP":
        rows = uniform_rows(tuple(value + "b" for value in base_groups(10)))
        keys = coherent_keys(candidate, 10)
    else:
        groups = tuple(five_prefix(i)[0] + input_tail(five_tail(i)) for i in range(512))
        keys = tuple(five_prefix(i)[1] + output_tail(candidate if i < 256 else alternate, five_tail(i)) for i in range(512))
        rows = tuple(Row(e, f"f{f}r", f"P.{f}", groups[:256] if e != "RF1b" else groups[256:], (".",) * 255)
                     for e in EDITIONS for f in range(1, 33))
        secret = None
        alt = alternate_rank
    return World(name, "ADVERSARY", index, 10, rank, secret, alt,
                 tuple(rank_draws) + tuple(log), rows, lexicon(keys, 10),
                 world_assertion(f"ADVERSARY_{name}_SIGNATURE"))


def all_worlds() -> tuple[World, ...]:
    worlds = [toy_world(4, True), toy_world(4, False), toy_world(6, True), toy_world(6, False)]
    worlds.extend(plant_world(i, rank, uses) for i, (rank, uses) in enumerate(unique_ranks("plant-map-rank", 100)))
    worlds.extend(null_world(i, rank, uses) for i, (rank, uses) in enumerate(unique_ranks("null-probe-rank", 128)))
    worlds.extend(adversary_world(i, rank, uses) for i, (rank, uses) in enumerate(unique_ranks("adversary-candidate-rank", 6)))
    if len(worlds) != 238 or len({world.world_id for world in worlds}) != 238:
        raise ValidationStop("world registry drift")
    return tuple(worlds)


def parser_fixture() -> tuple[tuple[Row, ...], dict[str, object]]:
    rows = ordered_rows(Row(edition, "f1r", "P.1",
                            ("k[dr:sy]", "l[ny]", "q{abc}y", "m<note>g", "kd"),
                            (",", "<->", "<~>", ".")) for edition in EDITIONS)
    hashes = [digest(canonical(row.obj())) for row in rows]
    projections = {panel: panel_projection(rows, panel) for panel in PANELS}
    record = {
        "fixture_id": "PARSER_CANONICAL", "row_count": 3,
        "row_sha256s": hashes,
        "rows_sha256": digest(b"".join(bytes.fromhex(v) for v in hashes)),
        "dot_panel_sha256": digest(canonical(list(projections[PANELS[0]]))),
        "manual_panel_sha256": digest(canonical(list(projections[PANELS[1]]))),
        "strict_literal_counts": {panel: sum(bool(v["strict_literal_eligible"])
                                                     for v in projections[panel])
                                  for panel in PANELS},
        "expected": {"assertion_count": 4, "assertions": [
            {"id": value, "operator": "PARSER_FIXTURE", "value": True}
            for value in ("PARSER_PRIMARY_SELECTION", "PARSER_SEPARATOR_STATES",
                          "PARSER_PANEL_INDEPENDENCE", "PARSER_STRICT_PROPAGATION")
        ]},
    }
    return rows, record


def mutation_record(name: str, base: str, payload: bytes, status_value: str,
                    equalities: dict[str, object],
                    parts: dict[str, str] | None = None) -> dict[str, object]:
    payload_digest = digest(payload)
    return {"mutation_id": name, "assertion_id": f"MUTATION_{name}",
            "base_world_id": base, "operation": name,
            "mutated_input_sha256": payload_digest,
            "payload_sha256s": parts if parts is not None else {"mutated": payload_digest},
            "expected_status": status_value, "expected_equalities": equalities}


def row_bytes(rows: Sequence[Row]) -> bytes:
    return canonical([row.obj() for row in rows])


def mutations(plant: World, parser_rows: Sequence[Row]) -> tuple[dict[str, object], ...]:
    base = ordered_rows(plant.rows)
    out: list[dict[str, object]] = [
        mutation_record("EMPTY_PANEL", "PLANT_000", canonical([]), "EXPECTED_HARD_STOP",
                        {"empty_panel_rejected": True}),
        mutation_record("DUPLICATE_ROW", "PLANT_000", row_bytes(base + (base[0],)),
                        "EXPECTED_HARD_STOP", {"duplicate_row_rejected": True}),
    ]
    first = plant.lexicon[0]
    encoded_entries = json.dumps(first["entries"], sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=True, allow_nan=False)
    encoded_key = json.dumps(first["key"], ensure_ascii=True, allow_nan=False)
    encoded_records = [f'{{"entries":{encoded_entries},"key":{encoded_key},"key":{encoded_key}}}']
    encoded_records.extend(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=True, allow_nan=False)
                           for value in plant.lexicon[1:])
    duplicate = ("[" + ",".join(encoded_records) + "]\n").encode()
    out.append(mutation_record("DUPLICATE_JSON_KEY", "PLANT_000", duplicate,
                               "EXPECTED_HARD_STOP", {"duplicate_json_key_rejected": True}))
    token_reverse = tuple(replace(row, groups=row.groups[::-1], separators=row.separators[::-1])
                          for row in base)
    out.extend((
        mutation_record("TOKEN_REVERSE", "PLANT_000", row_bytes(token_reverse),
                        "EXPECTED_BYTE_INVARIANCE",
                        {"input_rows_equal": False, "score_vectors_equal": True}),
        mutation_record("ROW_REVERSE", "PLANT_000", row_bytes(base[::-1]),
                        "EXPECTED_BYTE_INVARIANCE",
                        {"input_rows_equal": False, "score_vectors_equal": True}),
    ))
    lexicon_reverse = [{"key": value["key"], "entries": list(reversed(value["entries"]))}
                       for value in reversed(plant.lexicon)]
    out.append(mutation_record("LEXICON_REVERSE", "PLANT_000", canonical(lexicon_reverse),
                               "EXPECTED_BYTE_INVARIANCE",
                               {"projected_sets_equal": True, "score_vectors_equal": True}))
    malformed = (
        ("UNMATCHED_SQUARE", "[k"), ("NESTED_SQUARE", "[[k]]"),
        ("UNMATCHED_BRACE", "{k"), ("NESTED_BRACE", "{{k}}"),
        ("UNMATCHED_ANGLE", "<k"), ("NESTED_ANGLE", "<<k>>"),
    )
    parser_rows = tuple(parser_rows)
    for name, replacement_group in malformed:
        changed = (replace(parser_rows[0], groups=(replacement_group, *parser_rows[0].groups[1:])),
                   *parser_rows[1:])
        out.append(mutation_record(name, "PARSER_CANONICAL", row_bytes(changed),
                                   "EXPECTED_HARD_STOP", {"panel_digest_created": False}))
    overlength = {"key": "kkkkkkkkkkk", "entries": entries()}
    out.append(mutation_record("OVERLENGTH_PREIMAGE", "PLANT_000",
                               canonical([*plant.lexicon, overlength]), "EXPECTED_HARD_STOP",
                               {"source_panel_opened": False}))
    first_row = base[0]
    extended = replace(first_row, groups=(*first_row.groups, "kdrslnqymgk"),
                       separators=(*first_row.separators, "."))
    out.append(mutation_record("OVERLENGTH_TOKEN", "PLANT_000",
                               row_bytes((extended, *base[1:])), "EXPECTED_DECLARED_CHANGE",
                               {"always_unmatched": True, "denominator_delta": 1}))
    unknown = tuple(replace(row, groups=tuple(value + "b" for value in row.groups)) for row in base)
    out.append(mutation_record("UNKNOWN_INSERT", "PLANT_000", row_bytes(unknown),
                               "EXPECTED_DECLARED_CHANGE",
                               {"default_vectors_equal": True, "strict_instances_removed": 24576}))
    without_rf = tuple(row for row in base if row.edition != "RF1b")
    out.append(mutation_record("MISSING_EDITION", "PLANT_000", row_bytes(without_rf),
                               "EXPECTED_HARD_STOP", {"missing_rf_rejected": True}))
    first_object = base[0].obj()
    first_object["page"] = "fRos"
    out.append(mutation_record("PAGE_DOMAIN", "PLANT_000",
                               canonical([first_object, *(row.obj() for row in base[1:])]),
                               "EXPECTED_HARD_STOP", {"nonnumeric_page_rejected": True}))
    drift = base[0].obj()
    drift["page"] = "f2r"
    out.append(mutation_record("FOLIO_DRIFT", "PLANT_000",
                               canonical([drift, *(row.obj() for row in base[1:])]),
                               "EXPECTED_HARD_STOP", {"page_locus_disagreement_rejected": True}))
    full = canonical(list(plant.lexicon))
    retained = tuple(value for value in plant.lexicon if reachable(str(value["key"])))
    removed = tuple(value for value in plant.lexicon if not reachable(str(value["key"])))
    if len(removed) != 570:
        raise ValidationStop("unreachable mutation count drift")
    without = canonical(list(retained))
    removed_bytes = canonical(list(removed))
    out.append(mutation_record("UNREACHABLE_REMOVE", "PLANT_000", without,
                               "EXPECTED_BYTE_INVARIANCE",
                               {"raw_vectors_equal": True, "standardized_vectors_equal": True},
                               {"full": digest(full), "removed_records": digest(removed_bytes),
                                "without": digest(without)}))
    restored = canonical(sorted((*retained, *removed), key=lambda value: str(value["key"]).encode()))
    if restored != full:
        raise ValidationStop("unreachable restoration drift")
    out.append(mutation_record("UNREACHABLE_RESTORE_ADD_FROM_REMOVED",
                               "PLANT_000_WITHOUT_UNREACHABLE", restored,
                               "EXPECTED_BYTE_INVARIANCE",
                               {"full_lexicon_bytes_equal": True, "raw_vectors_equal": True,
                                "standardized_vectors_equal": True},
                               {"removed_records": digest(removed_bytes), "restored": digest(restored),
                                "without": digest(without)}))
    if len(out) != 20:
        raise ValidationStop("mutation registry drift")
    return tuple(out)


def assertion_registry(worlds: Sequence[World], mutation_rows: Sequence[Mapping[str, object]]) -> dict[str, list[str]]:
    return {
        "toys": ["TOY4_PLANT_COMPLETE_EQUALITY", "TOY4_NULL_COMPLETE_EQUALITY",
                 "TOY6_PLANT_COMPLETE_EQUALITY", "TOY6_NULL_COMPLETE_EQUALITY"],
        "plants": [f"PLANT_{index:03d}_SUCCESS" for index in range(100)],
        "nulls": [*(f"NULL_{index:03d}_PROBE_INDEPENDENCE" for index in range(128)),
                  "NULL_FALSE_PASS_COUNT_LE_1"],
        "adversaries": [f"ADVERSARY_{value}_SIGNATURE" for value in ADVERSARIES],
        "parser": ["PARSER_PRIMARY_SELECTION", "PARSER_SEPARATOR_STATES",
                   "PARSER_PANEL_INDEPENDENCE", "PARSER_STRICT_PROPAGATION"],
        "mutations": [str(value["assertion_id"]) for value in mutation_rows],
        "conjugacy": ["CONJUGACY_VECTOR_EQUALITY"],
        "workers": ["WORKER_1_32_VECTOR_EQUALITY"],
        "affix_equivalence": [f"AFFIX_{world.world_id}_EQUIVALENCE" for world in worlds],
        "unreachable_invariance": [f"UNREACHABLE_{world.world_id}_INVARIANCE"
                                    for world in worlds if world.width == 10],
    }


def reconstruct_manifest() -> tuple[dict[str, object], tuple[World, ...]]:
    worlds = all_worlds()
    parser_rows, parser_record = parser_fixture()
    plant = next(value for value in worlds if value.world_id == "PLANT_000")
    mutation_rows = mutations(plant, parser_rows)
    ids = assertion_registry(worlds, mutation_rows)
    totals = {name: len(ids[name]) for name in CONTROL_ORDER}
    expected_totals = {"toys": 4, "plants": 100, "nulls": 129, "adversaries": 6,
                       "parser": 4, "mutations": 20, "conjugacy": 1, "workers": 1,
                       "affix_equivalence": 238, "unreachable_invariance": 234}
    if totals != expected_totals or sum(totals.values()) != 737:
        raise ValidationStop("atomic assertion registry drift")
    _, conjugacy = first_nonidentity("conjugacy-permutation", 10)
    protocol = {"labels": list(COUNTER_LABELS), "root": ROOT_DOMAIN}
    manifest = {
        "schema": SCHEMA_MANIFEST,
        "science_spec": {"commit": SCIENCE_COMMIT, "path": SCIENCE_REL, "sha256": SCIENCE_SHA},
        "calibration_spec": {"path": CALIBRATION_REL, "sha256": CALIBRATION_SHA},
        "counter_protocol": {"root": ROOT_DOMAIN, "labels": list(COUNTER_LABELS),
                             "sha256": digest(canonical(protocol))},
        "worlds": [world.manifest() for world in worlds],
        "parser_fixture": parser_record, "mutations": list(mutation_rows),
        "aggregate_expectations": {
            "control_order": list(CONTROL_ORDER), "assertion_ids": ids,
            "totals": totals,
            "generator_fields": {"conjugacy": [value.object() for value in conjugacy]},
            "plant_success_min": 95, "null_false_pass_max": 1,
            "world_count": 238, "atomic_assertion_count": 737,
        },
    }
    return manifest, worlds


def key_code(key: str) -> tuple[int, ...]:
    if not reachable(key):
        raise ValidationStop("attempt to encode unreachable key")
    return tuple(NIBBLE[value] for value in key)


def preimages(keys: Iterable[str], deposited: bool) -> tuple[tuple[int, ...], ...]:
    accepted: set[tuple[int, ...]] = set()
    gallows = (NIBBLE["ṭ"], NIBBLE["p"], NIBBLE["ṣ"])
    standard = (NIBBLE["d"], NIBBLE["l"], NIBBLE["w"])
    for key in keys:
        if not reachable(key):
            continue
        base = key_code(key)
        accepted.add(base)
        if deposited:
            for gp in gallows:
                accepted.add((gp, *base))
                for sp in standard:
                    accepted.add((gp, sp, *base))
            for sp in standard:
                accepted.add((sp, *base))
            accepted.add((*base, NIBBLE["y"], NIBBLE["n"]))
    if any(len(value) > 10 for value in accepted):
        raise ValidationStop("overlength accepted preimage")
    return tuple(sorted(accepted))


def direct_decision(mapped: tuple[int, ...], keys: set[tuple[int, ...]], deposited: bool) -> bool:
    if mapped in keys:
        return True
    if not deposited:
        return False
    gallows = {NIBBLE["ṭ"], NIBBLE["p"], NIBBLE["ṣ"]}
    standard = {NIBBLE["d"], NIBBLE["l"], NIBBLE["w"]}
    if len(mapped) > 1 and mapped[0] in gallows and mapped[1:] in keys:
        return True
    if len(mapped) > 2 and mapped[0] in gallows and mapped[1] in standard and mapped[2:] in keys:
        return True
    if len(mapped) > 1 and mapped[0] in standard and mapped[1:] in keys:
        return True
    return len(mapped) > 2 and mapped[-2:] == (NIBBLE["y"], NIBBLE["n"]) and mapped[:-2] in keys


def literal_preimages(keys: Iterable[str], deposited: bool) -> tuple[tuple[int, ...], ...]:
    """Independent set form of the registered first-match decision paths."""
    output: set[tuple[int, ...]] = set()
    gallows = (NIBBLE["ṭ"], NIBBLE["p"], NIBBLE["ṣ"])
    standard = (NIBBLE["d"], NIBBLE["l"], NIBBLE["w"])
    for spelling in keys:
        if not reachable(spelling):
            continue
        value = key_code(spelling)
        output.add(value)
        if not deposited:
            continue
        output.update((gallows_value, *value) for gallows_value in gallows)
        output.update((gallows_value, standard_value, *value)
                      for gallows_value in gallows for standard_value in standard)
        output.update((standard_value, *value) for standard_value in standard)
        output.add((*value, NIBBLE["y"], NIBBLE["n"]))
    if any(len(value) > 10 for value in output):
        raise ValidationStop("overlength literal accepted preimage")
    return tuple(sorted(output))


def map_template(template: Sequence[int], permutation: Sequence[int]) -> tuple[int, ...]:
    return tuple(value if value > 0 else NIBBLE[CORE_OUT[permutation[-value - 1]]]
                 for value in template)


Constraint = tuple[int, tuple[int, ...]]


def compatible_constraint(template: Sequence[int], accepted: Sequence[int], width: int) -> Constraint | None:
    if len(template) != len(accepted):
        return None
    required = [255] * width
    used = 0
    mask = 0
    for source, target in zip(template, accepted, strict=True):
        if source > 0:
            if source != target:
                return None
            continue
        input_index = -source - 1
        output_index = CORE_OUTPUT_INDEX.get(target)
        if input_index >= width or output_index is None or output_index >= width:
            return None
        if required[input_index] != 255 and required[input_index] != output_index:
            return None
        bit = 1 << output_index
        if required[input_index] == 255 and used & bit:
            return None
        required[input_index] = output_index
        used |= bit
        mask |= 1 << input_index
    return mask, tuple(required)


def type_constraints(template: Sequence[int], accepted: Sequence[Sequence[int]], width: int) -> tuple[Constraint, ...]:
    output = {value for candidate in accepted
              if (value := compatible_constraint(template, candidate, width)) is not None}
    masks = {mask for mask, _ in output}
    if len(masks) > 1:
        raise ValidationStop("one template produced inconsistent variable masks")
    return tuple(sorted(output))


def constraints_disjoint(values: Sequence[Constraint], width: int) -> bool:
    for left_index, (_, left) in enumerate(values):
        for _, right in values[left_index + 1:]:
            conflict = any(left[index] != 255 and right[index] != 255 and
                           left[index] != right[index] for index in range(width))
            if not conflict:
                return False
    return True


def constraint_matches(constraint: Constraint, permutation: Sequence[int]) -> bool:
    return all(required == 255 or permutation[index] == required
               for index, required in enumerate(constraint[1]))


def constraint_count(constraint: Constraint, width: int) -> int:
    return math.factorial(width - constraint[0].bit_count())


def _nonidentity_constraint_ranks(constraint: Constraint, width: int,
                                  audit: object | None = None) -> Iterator[int]:
    """Traverse only lexicographic tree nodes intersecting ``[1,width!)``.

    In particular, the all-zero lexicographic leaf is pruned by its rank
    interval before the final value is assigned.  This routine never builds,
    ranks, tests, compares with, or subtracts a completed identity map.
    """
    _, required = constraint
    orbit = math.factorial(width)
    if audit is not None:
        audit.compiler_interval_requests += 1

    def visit(position: int, remaining: tuple[int, ...], rank_base: int,
              prefix: tuple[int, ...]) -> Iterator[int]:
        child_size = math.factorial(len(remaining) - 1)
        for ordinal, value in enumerate(remaining):
            child_start = rank_base + ordinal * child_size
            child_stop = child_start + child_size
            if child_stop <= 1 or child_start >= orbit:
                if audit is not None:
                    audit.compiler_pruned_nodes += 1
                continue
            required_value = required[position]
            if required_value != 255 and required_value != value:
                if audit is not None:
                    audit.compiler_constraint_pruned_nodes += 1
                continue
            if audit is not None:
                audit.compiler_visited_nodes += 1
            if len(remaining) == 1:
                # The interval test above proves child_start >= 1 before the
                # completed assignment is formed.
                completed = (*prefix, value)
                if len(completed) != width or child_start < 1:
                    if audit is not None and child_start == 0:
                        audit.compiler_completed_rank0_leaves += 1
                    raise ValidationStop("nonidentity compiler leaf invariant")
                if audit is not None:
                    audit.compiler_nonidentity_leaves += 1
                yield child_start
                continue
            next_remaining = remaining[:ordinal] + remaining[ordinal + 1:]
            yield from visit(position + 1, next_remaining, child_start, (*prefix, value))

    yield from visit(0, tuple(range(width)), 0, ())


def completion_ranks(constraint: Constraint, width: int, *, rank_start: int = 0,
                     audit: object | None = None) -> Iterator[int]:
    if rank_start not in (0, 1):
        raise ValidationStop("completion rank lower bound")
    if rank_start == 1:
        yield from _nonidentity_constraint_ranks(constraint, width, audit)
        return
    mask, required = constraint
    free_inputs = [index for index in range(width) if not mask & (1 << index)]
    used = {value for value in required if value != 255}
    free_outputs = [value for value in range(width) if value not in used]
    permutation = list(required)
    for completion in itertools.permutations(free_outputs):
        for input_index, output_index in zip(free_inputs, completion, strict=True):
            permutation[input_index] = output_index
        rank = rank_perm(permutation)
        yield rank


@dataclass(frozen=True, slots=True)
class TypeProfile:
    normalized: str = field(repr=False)
    template: tuple[int, ...] = field(repr=False)
    token_count: int
    folio_counts: tuple[tuple[int, int], ...]


@dataclass(slots=True)
class SurfaceVectors:
    orbit: int
    token: array
    type: array
    folio: array
    folio_numerators: tuple[array, ...]
    token_denominator: int
    type_denominator: int
    folio_denominators: tuple[int, ...]
    variable_types: int
    capacity_folios: int
    affix_equal: bool
    literal_decision_function_sha256: str | None = None
    expanded_decision_function_sha256: str | None = None


def profiles(tokens: Sequence[tuple[Token, bool]], *, strict_only: bool = False,
             delete_top20: bool = False) -> tuple[TypeProfile, ...]:
    kept = [(token, strict) for token, strict in tokens if not strict_only or strict]
    frequencies: dict[str, int] = {}
    for token, _ in kept:
        frequencies[token.normalized] = frequencies.get(token.normalized, 0) + 1
    deleted: set[str] = set()
    if delete_top20:
        if len(frequencies) < 20:
            return ()
        deleted = set(sorted(frequencies, key=lambda value: (-frequencies[value], value.encode()))[:20])
    grouped: dict[str, tuple[tuple[int, ...], dict[int, int]]] = {}
    for token, _ in kept:
        if token.normalized in deleted:
            continue
        if token.normalized not in grouped:
            grouped[token.normalized] = (token.template, {})
        elif grouped[token.normalized][0] != token.template:
            raise ValidationStop("normalized type/template inconsistency")
        folios = grouped[token.normalized][1]
        folios[token.folio] = folios.get(token.folio, 0) + 1
    return tuple(TypeProfile(name, template, sum(counts.values()), tuple(sorted(counts.items())))
                 for name, (template, counts) in sorted(grouped.items(), key=lambda item: item[0].encode()))


def enumerate_constraint_vectors(width: int, constraint_weights: Mapping[Constraint, tuple[int, ...]],
                                 vector_count: int, *, rank_start: int = 0,
                                 rank_audit: object | None = None) -> tuple[array, ...]:
    orbit = math.factorial(width)
    if rank_start not in (0, 1):
        raise ValidationStop("integer vector rank start")
    baseline = [0] * vector_count
    nonempty: list[tuple[Constraint, tuple[int, ...]]] = []
    for constraint, weights in constraint_weights.items():
        if len(weights) != vector_count or any(value < 0 for value in weights):
            raise ValidationStop("constraint weight shape")
        if constraint[0] == 0:
            for index, value in enumerate(weights):
                baseline[index] += value
        else:
            nonempty.append((constraint, weights))
    vectors = tuple(array("I", [value]) * (orbit - rank_start) for value in baseline)
    for constraint, weights in nonempty:
        for rank in completion_ranks(constraint, width, rank_start=rank_start,
                                     audit=rank_audit):
            for index, weight in enumerate(weights):
                value = vectors[index][rank - rank_start] + weight
                if value >= 2**32:
                    raise ValidationStop("uint32 numerator overflow")
                vectors[index][rank - rank_start] = value
    return vectors


def _balanced_folio_vector(folio_vectors: Sequence[array], folio_denominators: Sequence[int],
                           orbit: int) -> array:
    balanced = array("d", [0.0]) * orbit
    for rank in range(orbit):
        terms = [float(vector[rank]) / denominator
                 for vector, denominator in zip(folio_vectors, folio_denominators, strict=True)]
        total = 0.0
        correction = 0.0
        for value in terms:
            updated = total + value
            correction += ((total - updated) + value if abs(total) >= abs(value)
                           else (value - updated) + total)
            total = updated
        balanced[rank] = (total + correction) / len(terms) if terms else 0.0
    return balanced


def literal_type_constraints(template: Sequence[int], encoded_keys: Sequence[tuple[int, ...]],
                             width: int, deposited: bool) -> tuple[Constraint, ...]:
    """Compile the frozen first-match branches without using affix preimages."""
    candidates: list[tuple[int, ...]] = []
    # Branch 1: direct exact key.
    candidates.extend(encoded_keys)
    if deposited:
        gallows = (NIBBLE["ṭ"], NIBBLE["p"], NIBBLE["ṣ"])
        standard = (NIBBLE["d"], NIBBLE["l"], NIBBLE["w"])
        # Branches 2..5 retain the registered direct_decision order.
        candidates.extend((gallows_value, *key) for gallows_value in gallows
                          for key in encoded_keys)
        candidates.extend((gallows_value, standard_value, *key)
                          for gallows_value in gallows for standard_value in standard
                          for key in encoded_keys)
        candidates.extend((standard_value, *key) for standard_value in standard
                          for key in encoded_keys)
        candidates.extend((*key, NIBBLE["y"], NIBBLE["n"])
                          for key in encoded_keys)
    if any(len(value) > 10 for value in candidates):
        raise ValidationStop("literal decision branch overlength")
    output = {value for accepted in candidates
              if (value := compatible_constraint(template, accepted, width)) is not None}
    return tuple(sorted(output))


def append_decision_constraints(body: bytearray,
                                constraints_by_type: Sequence[Sequence[Constraint]],
                                width: int) -> None:
    body.extend(struct.pack("<I", len(constraints_by_type)))
    for constraints in constraints_by_type:
        ordered = tuple(sorted(set(constraints)))
        body.extend(struct.pack("<I", len(ordered)))
        for mask, required in ordered:
            if (not 0 <= mask < 2**16 or len(required) != width or
                    any(value != 255 and not 0 <= value < width for value in required) or
                    mask != sum(1 << index for index, value in enumerate(required)
                                if value != 255)):
                raise ValidationStop("decision-function constraint shape")
            body.extend(struct.pack("<H", mask))
            body.extend(bytes(required))


def decision_function_bytes(constraints_by_type: Sequence[Sequence[Constraint]],
                            width: int) -> bytes:
    body = bytearray(b"DANI001-DECISION-FUNCTION-V1\0")
    body.append(width)
    append_decision_constraints(body, constraints_by_type, width)
    return bytes(body)


def surface_vectors(tokens: Sequence[tuple[Token, bool]], records: Sequence[Mapping[str, object]],
                    width: int, *, deposited: bool, strict_only: bool = False,
                    delete_top20: bool = False, rank_start: int = 0,
                    literal_decision: bool = False,
                    rank_audit: object | None = None,
                    audit_role: str | None = None) -> SurfaceVectors:
    if rank_audit is not None:
        if audit_role is None:
            raise ValidationStop("rank audit requires a surface role")
        rank_audit.record_vector_surface(
            rank_start, math.factorial(width), math.factorial(width) - rank_start,
            audit_role)
    elif audit_role is not None:
        raise ValidationStop("surface audit role without rank audit")
    type_rows = profiles(tokens, strict_only=strict_only, delete_top20=delete_top20)
    folios = sorted({folio for row in type_rows for folio, _ in row.folio_counts})
    folio_columns: list[tuple[int, ...]] = []
    for folio in folios:
        folio_columns.append(tuple(dict(row.folio_counts).get(folio, 0) for row in type_rows))
    unique_columns: list[tuple[int, ...]] = []
    folio_to_column: list[int] = []
    for column in folio_columns:
        if column not in unique_columns:
            unique_columns.append(column)
        folio_to_column.append(unique_columns.index(column))
    columns = [tuple(row.token_count for row in type_rows), tuple(1 for _ in type_rows), *unique_columns]
    reachable_keys = {str(value["key"]) for value in records if reachable(str(value["key"]))}
    expanded = preimages(reachable_keys, deposited)
    literal = literal_preimages(reachable_keys, deposited)
    encoded_keys = tuple(sorted(key_code(value) for value in reachable_keys))
    expanded_constraints = tuple(type_constraints(row.template, expanded, width)
                                 for row in type_rows)
    literal_constraints = tuple(literal_type_constraints(row.template, encoded_keys,
                                                         width, deposited)
                                for row in type_rows)
    affix_equal = (expanded == literal and
                   decision_function_bytes(literal_constraints, width) ==
                   decision_function_bytes(expanded_constraints, width))
    constraints_by_type = literal_constraints if literal_decision else expanded_constraints
    if any(not constraints_disjoint(values, width) for values in constraints_by_type):
        raise ValidationStop("overlapping accepted constraints")
    if rank_start == 1:
        # Count only the authorized closed-open interval.  This never calls a
        # token matcher or obtains/stores a rank-0 numerator.
        nonidentity_count = [sum(
            (len(range(1, math.factorial(width))) if item[0] == 0 else
             sum(1 for _ in completion_ranks(item, width, rank_start=1,
                                             audit=rank_audit)))
            for item in values) for values in constraints_by_type]
    else:
        identity = tuple(range(width))
        nonidentity_count = [sum(constraint_count(item, width) for item in values) -
                             int(any(constraint_matches(item, identity) for item in values))
                             for values in constraints_by_type]
    variable = [0 < count < math.factorial(width) - 1 for count in nonidentity_count]
    capacity_folios = sum(any(flag and dict(row.folio_counts).get(folio, 0)
                              for flag, row in zip(variable, type_rows, strict=True)) for folio in folios)
    constraint_weights: dict[Constraint, list[int]] = {}
    for type_index, constraints in enumerate(constraints_by_type):
        weights = [column[type_index] for column in columns]
        for constraint in constraints:
            current = constraint_weights.setdefault(constraint, [0] * len(columns))
            for index, value in enumerate(weights):
                current[index] += value
    raw = enumerate_constraint_vectors(width,
                                       {key: tuple(value) for key, value in constraint_weights.items()},
                                       len(columns), rank_start=rank_start,
                                       rank_audit=rank_audit)
    orbit = math.factorial(width) - rank_start
    token_vector, type_vector = raw[0], raw[1]
    folio_vectors = tuple(raw[2 + index] for index in folio_to_column)
    folio_denominators = tuple(sum(column) for column in folio_columns)
    balanced = _balanced_folio_vector(folio_vectors, folio_denominators, orbit)
    output = SurfaceVectors(
        orbit, token_vector, type_vector, balanced, folio_vectors,
        sum(row.token_count for row in type_rows), len(type_rows),
        folio_denominators, sum(variable), capacity_folios, affix_equal,
        digest(decision_function_bytes(literal_constraints, width)),
        digest(decision_function_bytes(expanded_constraints, width)))
    return output


def finite_positive_sd(values: Sequence[int] | Sequence[float]) -> bool:
    if not values:
        return False
    first = float(values[0])
    if not math.isfinite(first):
        return False
    different = False
    for index in range(1, len(values)):
        value = float(values[index])
        if not math.isfinite(value):
            return False
        different = different or value != first
    return different


def finite_positive_sd_interval(values: Sequence[int] | Sequence[float], start: int) -> bool:
    if not 0 <= start < len(values):
        return False
    first = float(values[start])
    if not math.isfinite(first):
        return False
    different = False
    for index in range(start + 1, len(values)):
        value = float(values[index])
        if not math.isfinite(value):
            return False
        different = different or value != first
    return different


def little_bytes(values: array, kind: str) -> bytes:
    if sys.byteorder != "little":
        raise ValidationStop("validator requires little-endian host")
    if kind == "<u4" and values.typecode != "I":
        raise ValidationStop("integer vector type drift")
    if kind == "<f8" and values.typecode != "d":
        raise ValidationStop("float vector type drift")
    if (kind == "<u4" and values.itemsize != 4) or (kind == "<f8" and values.itemsize != 8):
        raise ValidationStop("host array width drift")
    return values.tobytes()


def vector_summary(values: array) -> tuple[float, float, float, float]:
    count = len(values)
    mean = math.fsum(float(value) for value in values) / count
    variance = math.fsum((float(value) - mean) ** 2 for value in values) / count
    sd = math.sqrt(variance)
    ordered = sorted(values)
    middle = count // 2
    median = float(ordered[middle]) if count % 2 else (float(ordered[middle - 1]) + float(ordered[middle])) / 2.0
    return mean, sd, median, float(values[0])


def z_vector(values: array) -> tuple[array, float, float]:
    mean, sd, median, _ = vector_summary(values)
    if not math.isfinite(sd) or sd <= 0.0:
        raise ValidationStop("nonpositive vector SD")
    return array("d", ((float(value) - mean) / sd for value in values)), median, sd


def rank_gate(components: Sequence[array], candidate_rank: int) -> tuple[array, float, int, int, float]:
    if not components:
        raise ValidationStop("empty joint score")
    z_values = [z_vector(value)[0] for value in components]
    joint = array("d", (min(values) for values in zip(*z_values, strict=True)))
    observed = joint[candidate_rank]
    strict_better = sum(value > observed for value in joint)
    ties = sum(value == observed for value in joint)
    return joint, observed, strict_better, ties, (strict_better + ties) / len(joint)


SurfaceName = tuple[str, str]
SURFACE_ORDER: tuple[SurfaceName, ...] = tuple(
    (edition, panel) for edition in EDITIONS for panel in PANELS)


def world_tokens(rows: Sequence[Row]) -> dict[SurfaceName, tuple[tuple[Token, bool], ...]]:
    by_edition = {edition: tuple(row for row in rows if row.edition == edition)
                  for edition in EDITIONS}
    output: dict[SurfaceName, tuple[tuple[Token, bool], ...]] = {}
    for edition, panel in SURFACE_ORDER:
        values: list[tuple[Token, bool]] = []
        for row in ordered_rows(by_edition[edition], require_all_editions=False):
            groups = row.groups if panel == "MANUAL_GROUP" else joined_dot_groups(row)
            for raw in groups:
                compiled = compile_token(raw, row.folio)
                if compiled is not None:
                    values.append(compiled)
        output[(edition, panel)] = tuple(values)
    return output


def projected_records(records: Sequence[Mapping[str, object]], view: str) -> tuple[Mapping[str, object], ...]:
    if view in {"FULL_DEPOSITED_AFFIX", "DIRECT_ONLY", "STRICT_LITERAL", "TOP20_DELETED"}:
        return tuple(records)
    output: list[Mapping[str, object]] = []
    omitted = view.removeprefix("LEAVE_").removesuffix("_OUT").lower() if view.startswith("LEAVE_") else None
    for record in records:
        source_entries = record.get("entries")
        if not isinstance(source_entries, list):
            raise ValidationStop("synthetic entry array drift")
        if view == "SOURCE_PRESENT":
            kept = [entry for entry in source_entries
                    if isinstance(entry, dict) and entry.get("source_present") is True]
        elif view == "STRICT_NO_FUNCTION":
            kept = (list(source_entries) if all(isinstance(entry, dict) and
                                                entry.get("domain") != "function"
                                                for entry in source_entries) else [])
        elif omitted is not None:
            kept = [entry for entry in source_entries
                    if isinstance(entry, dict) and entry.get("domain") != omitted]
        else:
            raise ValidationStop("unknown scoring view")
        if kept:
            output.append({"key": record["key"], "entries": kept})
    return tuple(output)


@dataclass(slots=True)
class ViewVectors:
    view: str
    surfaces: dict[SurfaceName, SurfaceVectors]


def build_world_views(world: World) -> dict[str, ViewVectors]:
    if world.width not in (4, 6):
        raise ValidationStop("complete world-view materialization is toy-only")
    tokens = world_tokens(world.rows)
    result: dict[str, ViewVectors] = {}
    cache: dict[tuple[object, ...], SurfaceVectors] = {}
    for view in SCORING_VIEWS:
        records = projected_records(world.lexicon, view)
        deposited = view != "DIRECT_ONLY"
        strict = view == "STRICT_LITERAL"
        top20 = view == "TOP20_DELETED"
        surfaces: dict[SurfaceName, SurfaceVectors] = {}
        key_signature = tuple(str(record["key"]) for record in records)
        for surface_name in SURFACE_ORDER:
            surface_tokens = tokens[surface_name]
            token_signature = tuple((token.normalized, token.template, token.folio, literal)
                                    for token, literal in surface_tokens)
            signature = (token_signature, key_signature, deposited, strict, top20, world.width)
            if signature not in cache:
                cache[signature] = surface_vectors(surface_tokens, records, world.width,
                                                   deposited=deposited, strict_only=strict,
                                                   delete_top20=top20)
            surfaces[surface_name] = cache[signature]
        result[view] = ViewVectors(view, surfaces)
    return result


@dataclass(frozen=True, slots=True)
class ComponentStat:
    mean: float
    sd: float
    median: float


@dataclass(slots=True)
class JointEvaluation:
    view: str
    joint: array
    observed: float
    strict_better: int
    ties: int
    inclusive_tail: float
    component_stats: tuple[ComponentStat, ...]
    raw_effects: tuple[float, ...]
    raw_coverages: tuple[float, ...]
    variable_capacity: bool
    concentration4: bool
    concentration5: bool
    positive_folio_counts: tuple[int, ...]

    @property
    def rank_pass_001_3(self) -> bool:
        return self.inclusive_tail <= 0.001 and self.observed >= 3.0

    @property
    def rank_pass_01_2(self) -> bool:
        return self.inclusive_tail <= 0.01 and self.observed >= 2.0


def component_arrays(view: ViewVectors) -> tuple[array, ...]:
    output: list[array] = []
    for surface_name in SURFACE_ORDER:
        surface = view.surfaces[surface_name]
        output.extend((surface.token, surface.type, surface.folio))
    return tuple(output)


def component_denominators(view: ViewVectors) -> tuple[float, ...]:
    output: list[float] = []
    for surface_name in SURFACE_ORDER:
        surface = view.surfaces[surface_name]
        output.extend((float(surface.token_denominator), float(surface.type_denominator), 1.0))
    return tuple(output)


def view_fingerprint(view: ViewVectors, candidate_rank: int, variable_threshold: int,
                     folio_threshold: int, *, concentration: bool) -> dict[str, object]:
    evaluation = evaluate_joint(view, candidate_rank, variable_threshold, folio_threshold,
                                concentration=concentration)
    components = component_arrays(view)
    raw = [digest(little_bytes(value, "<f8" if value.typecode == "d" else "<u4"))
           for value in components]
    standardized: list[str | None] = []
    raw_summaries: list[dict[str, object]] = []
    standardized_summaries: list[dict[str, object] | None] = []
    for value in components:
        mean, sd, median, _ = vector_summary(value)
        strict_raw = sum(float(item) > float(value[candidate_rank]) for item in value)
        ties_raw = sum(float(item) == float(value[candidate_rank]) for item in value)
        raw_summaries.append({
            "minimum": float(min(value)), "maximum": float(max(value)),
            "mean": mean, "sd": sd, "median": median,
            "observed": float(value[candidate_rank]),
            "strict_better": strict_raw, "ties": ties_raw,
            "inclusive_tail": (strict_raw + ties_raw) / len(value),
        })
        try:
            z_values = z_vector(value)[0]
            standardized.append(digest(little_bytes(z_values, "<f8")))
            z_mean, z_sd, z_median, _ = vector_summary(z_values)
            strict_z = sum(item > z_values[candidate_rank] for item in z_values)
            ties_z = sum(item == z_values[candidate_rank] for item in z_values)
            standardized_summaries.append({
                "minimum": min(z_values), "maximum": max(z_values), "mean": z_mean,
                "sd": z_sd, "median": z_median, "observed": z_values[candidate_rank],
                "strict_better": strict_z, "ties": ties_z,
                "inclusive_tail": (strict_z + ties_z) / len(z_values),
            })
        except ValidationStop:
            standardized.append(None)
            standardized_summaries.append(None)
    joint_summary: dict[str, object] | None = None
    if evaluation.joint:
        joint_mean, joint_sd, joint_median, _ = vector_summary(evaluation.joint)
        joint_summary = {
            "minimum": min(evaluation.joint), "maximum": max(evaluation.joint),
            "mean": joint_mean, "sd": joint_sd, "median": joint_median,
            "observed": evaluation.observed, "strict_better": evaluation.strict_better,
            "ties": evaluation.ties, "inclusive_tail": evaluation.inclusive_tail,
        }
    return {
        "raw": raw, "standardized": standardized,
        "raw_summaries": raw_summaries,
        "standardized_summaries": standardized_summaries,
        "joint_sha256": (digest(little_bytes(evaluation.joint, "<f8"))
                         if evaluation.joint else None),
        "observed": evaluation.observed, "strict_better": evaluation.strict_better,
        "ties": evaluation.ties, "inclusive_tail": evaluation.inclusive_tail,
        "raw_effects": evaluation.raw_effects, "raw_coverages": evaluation.raw_coverages,
        "capacity": evaluation.variable_capacity,
        "concentration4": evaluation.concentration4,
        "concentration5": evaluation.concentration5,
        "positive_folio_counts": evaluation.positive_folio_counts,
        "rank_pass_001_3": evaluation.rank_pass_001_3,
        "rank_pass_01_2": evaluation.rank_pass_01_2,
        "joint_summary": joint_summary,
    }


def score_evidence_array(views: Mapping[str, ViewVectors]) -> list[dict[str, object]]:
    """Anonymous complete score-vector evidence in the frozen nested order."""
    output: list[dict[str, object]] = []
    for view_name in SCORING_VIEWS:
        view = views[view_name]
        for edition, panel in SURFACE_ORDER:
            surface = view.surfaces[(edition, panel)]
            for weighting, values, dtype in (
                    ("TOKEN", surface.token, "<u4"),
                    ("TYPE", surface.type, "<u4"),
                    ("FOLIO", surface.folio, "<f8")):
                standardized: str | None
                try:
                    standardized = digest(little_bytes(z_vector(values)[0], "<f8"))
                except ValidationStop:
                    standardized = None
                output.append({
                    "view": view_name, "edition": edition, "panel": panel,
                    "weighting": weighting, "raw_dtype": dtype,
                    "raw_sha256": digest(little_bytes(values, dtype)),
                    "standardized_sha256": standardized,
                })
    return output


def score_evidence_view(view_name: str, view: ViewVectors) -> list[dict[str, object]]:
    return [
        item
        for edition, panel in SURFACE_ORDER
        for item in _surface_evidence_entries(
            view_name, edition, panel, view.surfaces[(edition, panel)])
    ]


def _surface_evidence_entries(view_name: str, edition: str, panel: str,
                              surface: SurfaceVectors) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for weighting, values, dtype in (
            ("TOKEN", surface.token, "<u4"),
            ("TYPE", surface.type, "<u4"),
            ("FOLIO", surface.folio, "<f8")):
        try:
            standardized: str | None = digest(little_bytes(z_vector(values)[0], "<f8"))
        except ValidationStop:
            standardized = None
        output.append({
            "view": view_name, "edition": edition, "panel": panel,
            "weighting": weighting, "raw_dtype": dtype,
            "raw_sha256": digest(little_bytes(values, dtype)),
            "standardized_sha256": standardized,
        })
    return output


def evidence_digest(schema: str, world_id: str,
                    states: Sequence[tuple[str, Mapping[str, ViewVectors]]], *,
                    extra: Mapping[str, object] | None = None) -> tuple[str, list[list[dict[str, object]]]]:
    arrays = [score_evidence_array(views) for _, views in states]
    payload: dict[str, object] = {"schema": schema, "world_id": world_id}
    if extra is not None:
        payload.update(extra)
    for (name, _), values in zip(states, arrays, strict=True):
        payload[name] = values
    return digest(canonical(payload)), arrays


def build_one_world_view(world: World, view_name: str, *, literal_decision: bool = False,
                         records_override: Sequence[Mapping[str, object]] | None = None,
                         rows_override: Sequence[Row] | None = None,
                         rank_start: int = 0,
                         surface_cache: dict[str, SurfaceVectors] | None = None) -> ViewVectors:
    token_map = world_tokens(tuple(world.rows if rows_override is None else rows_override))
    records = tuple(projected_records(world.lexicon, view_name) if records_override is None
                    else records_override)
    surfaces: dict[SurfaceName, SurfaceVectors] = {}
    cache = {} if surface_cache is None else surface_cache
    for surface_name in SURFACE_ORDER:
        surface_tokens = token_map[surface_name]
        type_rows = profiles(
            surface_tokens, strict_only=view_name == "STRICT_LITERAL",
            delete_top20=view_name == "TOP20_DELETED")
        signature = digest(canonical({
            "schema": "dani001-anonymous-surface-cache-v1",
            "width": world.width, "rank_start": rank_start,
            "deposited": view_name != "DIRECT_ONLY",
            "strict": view_name == "STRICT_LITERAL",
            "top20": view_name == "TOP20_DELETED",
            "literal": literal_decision,
            "profiles": [[list(row.template), row.token_count,
                          [[folio, count] for folio, count in row.folio_counts]]
                         for row in type_rows],
            "key_codes": [list(key_code(str(value["key"]))) for value in records
                          if reachable(str(value["key"]))],
        }))
        if signature not in cache:
            cache[signature] = surface_vectors(
                surface_tokens, records, world.width,
                deposited=view_name != "DIRECT_ONLY", strict_only=view_name == "STRICT_LITERAL",
                delete_top20=view_name == "TOP20_DELETED", rank_start=rank_start,
                literal_decision=literal_decision)
        surfaces[surface_name] = cache[signature]
    return ViewVectors(view_name, surfaces)


def build_literal_world_views(world: World) -> tuple[dict[str, ViewVectors], str, str]:
    """Toy-only complete-state reference for fabricated self-tests."""
    if world.width not in (4, 6):
        raise ValidationStop("complete literal-world reference is toy-only")
    token_map = world_tokens(world.rows)
    literal_function = bytearray(b"DANI001-DECISION-FUNCTION-V1\0")
    expanded_function = bytearray(b"DANI001-DECISION-FUNCTION-V1\0")
    literal_function.append(world.width)
    expanded_function.append(world.width)
    output: dict[str, ViewVectors] = {}
    for view_name in SCORING_VIEWS:
        records = projected_records(world.lexicon, view_name)
        surfaces: dict[SurfaceName, SurfaceVectors] = {}
        for surface_name in SURFACE_ORDER:
            surface_tokens = token_map[surface_name]
            surfaces[surface_name] = surface_vectors(
                surface_tokens, records, world.width,
                deposited=view_name != "DIRECT_ONLY",
                strict_only=view_name == "STRICT_LITERAL",
                delete_top20=view_name == "TOP20_DELETED", literal_decision=True)
            type_rows = profiles(
                surface_tokens, strict_only=view_name == "STRICT_LITERAL",
                delete_top20=view_name == "TOP20_DELETED")
            reachable_keys = tuple(sorted(
                (str(value["key"]) for value in records if reachable(str(value["key"]))),
                key=lambda value: value.encode()))
            encoded_keys = tuple(key_code(value) for value in reachable_keys)
            literal_constraints = tuple(
                literal_type_constraints(row.template, encoded_keys, world.width,
                                         view_name != "DIRECT_ONLY")
                for row in type_rows)
            expanded_codes = preimages(reachable_keys, view_name != "DIRECT_ONLY")
            expanded_constraints = tuple(
                type_constraints(row.template, expanded_codes, world.width)
                for row in type_rows)
            append_decision_constraints(literal_function, literal_constraints, world.width)
            append_decision_constraints(expanded_function, expanded_constraints, world.width)
        output[view_name] = ViewVectors(view_name, surfaces)
    return output, digest(bytes(literal_function)), digest(bytes(expanded_function))


def append_view_decision_functions(world: World, view_name: str,
                                   records: Sequence[Mapping[str, object]],
                                   token_map: Mapping[SurfaceName, Sequence[tuple[Token, bool]]],
                                   literal_function: bytearray,
                                   expanded_function: bytearray) -> None:
    for surface_name in SURFACE_ORDER:
        type_rows = profiles(
            token_map[surface_name], strict_only=view_name == "STRICT_LITERAL",
            delete_top20=view_name == "TOP20_DELETED")
        reachable_keys = tuple(sorted(
            (str(value["key"]) for value in records if reachable(str(value["key"]))),
            key=lambda value: value.encode()))
        encoded_keys = tuple(key_code(value) for value in reachable_keys)
        literal_constraints = tuple(
            literal_type_constraints(row.template, encoded_keys, world.width,
                                     view_name != "DIRECT_ONLY")
            for row in type_rows)
        expanded_codes = preimages(reachable_keys, view_name != "DIRECT_ONLY")
        expanded_constraints = tuple(
            type_constraints(row.template, expanded_codes, world.width)
            for row in type_rows)
        append_decision_constraints(literal_function, literal_constraints, world.width)
        append_decision_constraints(expanded_function, expanded_constraints, world.width)


def binary_match_equivalence(tokens: Sequence[tuple[Token, bool]], records: Sequence[Mapping[str, object]],
                             width: int, *, rank_start: int = 0) -> tuple[bool, str]:
    literal = surface_vectors(tokens, records, width, deposited=True,
                              rank_start=rank_start, literal_decision=True)
    expanded = surface_vectors(tokens, records, width, deposited=True,
                               rank_start=rank_start)
    return (surface_raw_capacity_equal(literal, expanded) and
            literal.literal_decision_function_sha256 ==
            literal.expanded_decision_function_sha256,
            literal.literal_decision_function_sha256 or "")


def view_exact_equal(left: ViewVectors, right: ViewVectors, candidate: int,
                     threshold_types: int, threshold_folios: int,
                     *, concentration: bool) -> bool:
    for surface_name in SURFACE_ORDER:
        left_surface = left.surfaces[surface_name]
        right_surface = right.surfaces[surface_name]
        if (little_bytes(left_surface.token, "<u4") != little_bytes(right_surface.token, "<u4") or
                little_bytes(left_surface.type, "<u4") != little_bytes(right_surface.type, "<u4") or
                little_bytes(left_surface.folio, "<f8") != little_bytes(right_surface.folio, "<f8") or
                any(little_bytes(a, "<u4") != little_bytes(b, "<u4")
                    for a, b in zip(left_surface.folio_numerators,
                                    right_surface.folio_numerators, strict=True))):
            return False
    return view_fingerprint(left, candidate, threshold_types, threshold_folios,
                            concentration=concentration) == view_fingerprint(
                                right, candidate, threshold_types, threshold_folios,
                                concentration=concentration)


def surface_raw_capacity_equal(left: SurfaceVectors, right: SurfaceVectors) -> bool:
    return (
        little_bytes(left.token, "<u4") == little_bytes(right.token, "<u4") and
        little_bytes(left.type, "<u4") == little_bytes(right.type, "<u4") and
        little_bytes(left.folio, "<f8") == little_bytes(right.folio, "<f8") and
        all(little_bytes(a, "<u4") == little_bytes(b, "<u4")
            for a, b in zip(left.folio_numerators, right.folio_numerators, strict=True)) and
        left.variable_types == right.variable_types and
        left.capacity_folios == right.capacity_folios and
        finite_positive_sd(left.token) == finite_positive_sd(right.token) and
        finite_positive_sd(left.type) == finite_positive_sd(right.type) and
        finite_positive_sd(left.folio) == finite_positive_sd(right.folio))


def evaluate_joint(view: ViewVectors, candidate_rank: int, variable_threshold: int,
                   folio_threshold: int, summary_cache: dict[int, ComponentStat] | None = None,
                   numeric_cache: dict[tuple[int, ...], tuple[object, ...]] | None = None,
                   *, concentration: bool = False) -> JointEvaluation:
    components = component_arrays(view)
    if not components or not 0 <= candidate_rank < len(components[0]):
        raise ValidationStop("candidate outside scoring orbit")
    cached = summary_cache if summary_cache is not None else {}
    stats: list[ComponentStat] = []
    for values in components:
        identity = id(values)
        if identity not in cached:
            mean, sd, median, _ = vector_summary(values)
            cached[identity] = ComponentStat(mean, sd, median)
        stats.append(cached[identity])
    positive = all(math.isfinite(value.sd) and value.sd > 0.0 for value in stats)
    powered = positive and all(
        surface.variable_types >= variable_threshold and surface.capacity_folios >= folio_threshold
        for surface in view.surfaces.values())
    denominators = component_denominators(view)
    numeric_key = tuple(id(value) for value in components)
    numeric = numeric_cache.get(numeric_key) if numeric_cache is not None else None
    if numeric is None:
        if positive:
            joint = array("d", [0.0]) * len(components[0])
            for rank in range(len(joint)):
                joint[rank] = min((float(values[rank]) - stat.mean) / stat.sd
                                  for values, stat in zip(components, stats, strict=True))
            observed = joint[candidate_rank]
            strict_better = sum(value > observed for value in joint)
            ties = sum(value == observed for value in joint)
            inclusive = (strict_better + ties) / len(joint)
        else:
            joint = array("d")
            observed, strict_better, ties, inclusive = float("-inf"), len(components[0]), 0, 1.0
        effects = tuple((float(values[candidate_rank]) - stat.median) / denominator
                        if denominator > 0.0 else float("-inf")
                        for values, stat, denominator in zip(components, stats, denominators, strict=True))
        coverages = tuple(float(values[candidate_rank]) / denominator if denominator > 0.0 else 0.0
                          for values, denominator in zip(components, denominators, strict=True))
        numeric = (joint, observed, strict_better, ties, inclusive, effects, coverages)
        if numeric_cache is not None:
            numeric_cache[numeric_key] = numeric
    joint, observed, strict_better, ties, inclusive, effects, coverages = numeric
    gate4 = not concentration
    gate5 = not concentration
    positive_counts: list[int] = []
    if concentration:
        gate4 = True
        gate5 = True
        folio_medians: dict[tuple[int, int], float] = {}
        for surface in view.surfaces.values():
            advantages: list[float] = []
            for folio_vector, denominator in zip(surface.folio_numerators,
                                                 surface.folio_denominators, strict=True):
                if denominator <= 0:
                    advantages.append(float("-inf"))
                    continue
                identity = (id(folio_vector), denominator)
                if identity not in folio_medians:
                    coverage_values = array("d", (float(value) / denominator for value in folio_vector))
                    _, _, folio_medians[identity], _ = vector_summary(coverage_values)
                advantages.append(float(folio_vector[candidate_rank]) / denominator -
                                  folio_medians[identity])
            positives = sorted((max(0.0, value) for value in advantages), reverse=True)
            total = math.fsum(positives)
            positive_count = sum(value > 0.0 for value in advantages)
            positive_counts.append(positive_count)
            gate4 = gate4 and bool(advantages) and positive_count / len(advantages) >= 0.60
            gate5 = gate5 and len(positives) >= 5 and total > 0.0 and positives[0] / total <= 0.10 and math.fsum(positives[:5]) / total <= 0.25
    return JointEvaluation(view.view, joint, observed, strict_better, ties, inclusive,
                           tuple(stats), effects, coverages, powered, gate4, gate5,
                           tuple(positive_counts))


@dataclass(slots=True)
class WorldEvaluation:
    world_id: str
    affix_equivalence: bool
    unreachable_invariance: bool
    primary_all_gates: bool
    plant_success: bool
    null_false_pass: bool
    signature_pass: bool
    affix_evidence_sha256: str
    unreachable_evidence_sha256: str | None


@dataclass(slots=True)
class LiveStateBudget:
    live: int = 0
    peak: int = 0

    def acquire(self) -> None:
        self.live += 1
        self.peak = max(self.peak, self.live)
        if self.live > MAX_LIVE_VECTOR_STATES:
            raise ValidationStop("width-10 live vector-state budget exceeded")

    def release(self) -> None:
        if self.live <= 0:
            raise ValidationStop("vector-state liveness underflow")
        self.live -= 1


def world_memory_preflight(world: World,
                           token_map: Mapping[SurfaceName, Sequence[tuple[Token, bool]]]) -> int:
    """Conservative registered-shape bound before any factorial vector exists."""
    if world.width != 10:
        return 0
    maximum_state = 0
    for view_name in SCORING_VIEWS:
        signatures: set[bytes] = set()
        largest_unique_columns = 0
        for surface_name in SURFACE_ORDER:
            type_rows = profiles(
                token_map[surface_name], strict_only=view_name == "STRICT_LITERAL",
                delete_top20=view_name == "TOP20_DELETED")
            folios = sorted({folio for row in type_rows for folio, _ in row.folio_counts})
            columns = {
                tuple(dict(row.folio_counts).get(folio, 0) for row in type_rows)
                for folio in folios
            }
            largest_unique_columns = max(largest_unique_columns, len(columns))
            anonymous = canonical([
                [list(row.template), row.token_count,
                 [[folio, count] for folio, count in row.folio_counts]]
                for row in type_rows
            ])
            signatures.add(hashlib.sha256(anonymous).digest())
        # token/type <u4, equal-folio <f8, and each unique folio <u4>.
        per_signature = math.factorial(10) * (4 + 4 + 8 + 4 * largest_unique_columns)
        maximum_state = max(maximum_state, len(signatures) * per_signature)
    # Two live raw states plus one joint/standardization scratch allowance.
    estimate = MAX_LIVE_VECTOR_STATES * maximum_state + math.factorial(10) * 16 * 6
    if estimate > WIDTH10_PROCESS_MEMORY_BOUND:
        raise ValidationStop("registered world exceeds frozen streaming memory bound")
    return estimate


def evaluate_world(world: World) -> WorldEvaluation:
    evaluated: dict[str, JointEvaluation] = {}
    expanded_fingerprints: dict[str, dict[str, object]] = {}
    literal_fingerprints: dict[str, dict[str, object]] = {}
    without_fingerprints: dict[str, dict[str, object]] = {}
    restored_fingerprints: dict[str, dict[str, object]] = {}
    thresholds = {
        "FULL_DEPOSITED_AFFIX": (100, 20), "DIRECT_ONLY": (100, 20),
        "STRICT_NO_FUNCTION": (100, 20), "STRICT_LITERAL": (100, 20),
        "TOP20_DELETED": (80, 20), "SOURCE_PRESENT": (30, 10),
        **{f"LEAVE_{domain.upper()}_OUT": (100, 20) for domain in ALL_DOMAINS},
    }
    token_map = world_tokens(world.rows)
    world_memory_preflight(world, token_map)
    live_budget = LiveStateBudget()
    literal_function = bytearray(b"DANI001-DECISION-FUNCTION-V1\0")
    expanded_function = bytearray(b"DANI001-DECISION-FUNCTION-V1\0")
    literal_function.append(world.width)
    expanded_function.append(world.width)
    literal_evidence: list[dict[str, object]] = []
    expanded_evidence: list[dict[str, object]] = []
    full_evidence: list[dict[str, object]] = []
    without_evidence: list[dict[str, object]] = []
    restored_evidence: list[dict[str, object]] = []
    affix = True
    unreachable_ok = True
    raw_facts: dict[str, object] = {}

    def compact(name: str, fingerprint: Mapping[str, object]) -> JointEvaluation:
        summaries = fingerprint["raw_summaries"]
        if not isinstance(summaries, list):
            raise ValidationStop("compact fingerprint summary shape")
        stats = tuple(ComponentStat(float(value["mean"]), float(value["sd"]),
                                    float(value["median"])) for value in summaries)
        return JointEvaluation(
            name, array("d"), float(fingerprint["observed"]),
            int(fingerprint["strict_better"]), int(fingerprint["ties"]),
            float(fingerprint["inclusive_tail"]), stats,
            tuple(float(value) for value in fingerprint["raw_effects"]),
            tuple(float(value) for value in fingerprint["raw_coverages"]),
            bool(fingerprint["capacity"]), bool(fingerprint["concentration4"]),
            bool(fingerprint["concentration5"]),
            tuple(int(value) for value in fingerprint["positive_folio_counts"]))

    for view_name in SCORING_VIEWS:
        records = projected_records(world.lexicon, view_name)
        expanded_cache: dict[str, SurfaceVectors] = {}
        live_budget.acquire()
        expanded_view = build_one_world_view(
            world, view_name, surface_cache=expanded_cache)
        expanded_fp = view_fingerprint(
            expanded_view, world.candidate, *thresholds[view_name],
            concentration=view_name == "FULL_DEPOSITED_AFFIX")
        expanded_fingerprints[view_name] = expanded_fp
        evaluated[view_name] = compact(view_name, expanded_fp)
        expanded_entries = score_evidence_view(view_name, expanded_view)
        expanded_evidence.extend(expanded_entries)
        full_evidence.extend(expanded_entries)

        literal_cache: dict[str, SurfaceVectors] = {}
        live_budget.acquire()
        literal_view = build_one_world_view(
            world, view_name, literal_decision=True, surface_cache=literal_cache)
        literal_fp = view_fingerprint(
            literal_view, world.candidate, *thresholds[view_name],
            concentration=view_name == "FULL_DEPOSITED_AFFIX")
        literal_fingerprints[view_name] = literal_fp
        literal_entries = score_evidence_view(view_name, literal_view)
        literal_evidence.extend(literal_entries)
        affix = (affix and literal_fp == expanded_fp and
                 literal_entries == expanded_entries and all(
                     surface_raw_capacity_equal(
                         expanded_view.surfaces[surface_name],
                         literal_view.surfaces[surface_name]) and
                     literal_view.surfaces[surface_name].literal_decision_function_sha256 ==
                     literal_view.surfaces[surface_name].expanded_decision_function_sha256
                     for surface_name in SURFACE_ORDER))
        append_view_decision_functions(
            world, view_name, records, token_map, literal_function, expanded_function)
        del literal_view, literal_cache
        live_budget.release()

        if world.width == 10:
            reachable_records = tuple(
                record for record in records if reachable(str(record["key"])))
            saved_removed = tuple(
                record for record in records if not reachable(str(record["key"])))
            restored_records = tuple(sorted(
                (*reachable_records, *saved_removed),
                key=lambda value: str(value["key"]).encode()))
            if (len(reachable_records) + len(saved_removed) != len(records) or
                    len(saved_removed) != 570 or
                    any(not str(record["key"]).startswith("u") for record in saved_removed) or
                    len({str(value["key"]) for value in restored_records}) != len(restored_records) or
                    canonical(list(restored_records)) != canonical(list(records))):
                raise ValidationStop("streamed unreachable restoration drift")
            live_budget.acquire()
            without_view = build_one_world_view(
                world, view_name, records_override=reachable_records,
                surface_cache={})
            without_fp = view_fingerprint(
                without_view, world.candidate, *thresholds[view_name],
                concentration=view_name == "FULL_DEPOSITED_AFFIX")
            without_fingerprints[view_name] = without_fp
            without_entries = score_evidence_view(view_name, without_view)
            without_evidence.extend(without_entries)
            unreachable_ok = (unreachable_ok and without_fp == expanded_fp and
                              without_entries == expanded_entries and all(
                                  surface_raw_capacity_equal(
                                      expanded_view.surfaces[surface_name],
                                      without_view.surfaces[surface_name])
                                  for surface_name in SURFACE_ORDER))
            del without_view, without_entries
            live_budget.release()
            live_budget.acquire()
            restored_view = build_one_world_view(
                world, view_name, records_override=restored_records,
                surface_cache={})
            restored_fp = view_fingerprint(
                restored_view, world.candidate, *thresholds[view_name],
                concentration=view_name == "FULL_DEPOSITED_AFFIX")
            restored_fingerprints[view_name] = restored_fp
            restored_entries = score_evidence_view(view_name, restored_view)
            restored_evidence.extend(restored_entries)
            unreachable_ok = (unreachable_ok and restored_fp == expanded_fp and
                              restored_entries == expanded_entries and all(
                                  surface_raw_capacity_equal(
                                      expanded_view.surfaces[surface_name],
                                      restored_view.surfaces[surface_name])
                                  for surface_name in SURFACE_ORDER))
            del restored_view, restored_entries
            live_budget.release()

        if view_name == "FULL_DEPOSITED_AFFIX":
            raw_facts["full_nonidentity_sd_positive"] = all(
                finite_positive_sd_interval(value, 1)
                for value in component_arrays(expanded_view))
            raw_facts["primary_capacity_folios"] = tuple(
                expanded_view.surfaces[name].capacity_folios for name in SURFACE_ORDER)
            if world.world_id == "UNKNOWN_SKIP":
                clean_rows = tuple(replace(row, groups=tuple(value[:-1] for value in row.groups))
                                   for row in world.rows)
                live_budget.acquire()
                clean_view = build_one_world_view(
                    replace(world, rows=clean_rows), view_name, surface_cache={})
                clean_fp = view_fingerprint(
                    clean_view, world.candidate, *thresholds[view_name],
                    concentration=True)
                raw_facts["unknown_clean_equal"] = clean_fp == expanded_fp
                del clean_view
                live_budget.release()
        del expanded_view, expanded_cache
        live_budget.release()

    if live_budget.live != 0 or live_budget.peak > MAX_LIVE_VECTOR_STATES:
        raise ValidationStop("streaming vector-state liveness drift")

    literal_function_sha = digest(bytes(literal_function))
    expanded_function_sha = digest(bytes(expanded_function))
    affix = (affix and literal_function_sha == expanded_function_sha and
             toy_gate_decision(literal_fingerprints) ==
             toy_gate_decision(expanded_fingerprints))
    affix_evidence = digest(canonical({
        "schema": "dani001-affix-evidence-v1", "world_id": world.world_id,
        "literal_decision_function_sha256": literal_function_sha,
        "expanded_decision_function_sha256": expanded_function_sha,
        "literal": literal_evidence, "expanded": expanded_evidence,
    }))
    unreachable_evidence: str | None = None
    if world.width == 10:
        unreachable_ok = (unreachable_ok and
                          toy_gate_decision(expanded_fingerprints) ==
                          toy_gate_decision(without_fingerprints) ==
                          toy_gate_decision(restored_fingerprints))
        unreachable_evidence = digest(canonical({
            "schema": "dani001-unreachable-evidence-v1", "world_id": world.world_id,
            "full": full_evidence, "without": without_evidence,
            "restored": restored_evidence,
        }))
    primary = evaluated["FULL_DEPOSITED_AFFIX"]
    gate3 = all(value >= 0.020 for value in primary.raw_effects)
    gate6 = evaluated["TOP20_DELETED"].variable_capacity and evaluated["TOP20_DELETED"].rank_pass_01_2
    gate7 = evaluated["STRICT_LITERAL"].variable_capacity and evaluated["STRICT_LITERAL"].rank_pass_01_2
    primary_all = (primary.variable_capacity and primary.rank_pass_001_3 and gate3 and
                   primary.concentration4 and primary.concentration5 and gate6 and gate7)
    mechanics = all(evaluated[name].variable_capacity and evaluated[name].rank_pass_01_2
                    for name in ("DIRECT_ONLY", "STRICT_NO_FUNCTION", "SOURCE_PRESENT"))
    leaves = all(evaluated[f"LEAVE_{domain.upper()}_OUT"].variable_capacity and
                 evaluated[f"LEAVE_{domain.upper()}_OUT"].rank_pass_01_2 and
                 all(value > 0.0 for value in evaluated[f"LEAVE_{domain.upper()}_OUT"].raw_effects)
                 for domain in ALL_DOMAINS)
    unique = primary.strict_better == 0 and primary.ties == 1
    plant_success = (world.family in {"PLANT", "TOY_PLANT"} and unique and primary_all and
                     mechanics and leaves and affix and unreachable_ok)
    null_false = world.family in {"NULL", "TOY_NULL"} and primary_all and mechanics and leaves
    signature = adversary_signature(world, evaluated, raw_facts) if world.family == "ADVERSARY" else True
    return WorldEvaluation(world.world_id, affix, unreachable_ok,
                           primary_all, plant_success, null_false, signature,
                           affix_evidence, unreachable_evidence)


def adversary_signature(world: World, views: Mapping[str, JointEvaluation],
                        raw_facts: Mapping[str, object]) -> bool:
    primary = views["FULL_DEPOSITED_AFFIX"]
    primary_core = (primary.variable_capacity and primary.rank_pass_001_3 and
                    all(value >= 0.020 for value in primary.raw_effects))
    primary_all = (primary_core and primary.concentration4 and primary.concentration5 and
                   views["TOP20_DELETED"].variable_capacity and views["TOP20_DELETED"].rank_pass_01_2 and
                   views["STRICT_LITERAL"].variable_capacity and views["STRICT_LITERAL"].rank_pass_01_2)
    if world.world_id == "FIXED_HEAVY_HIGH_COVERAGE":
        return all(coverage >= 0.90 for index, coverage in enumerate(primary.raw_coverages)
                   if index % 3 == 0) and raw_facts.get(
                       "full_nonidentity_sd_positive") is True and not primary.rank_pass_001_3
    if world.world_id == "ONE_TYPE_CONCENTRATION":
        top20 = views["TOP20_DELETED"]
        surface_tokens = world_tokens(world.rows)[SURFACE_ORDER[0]]
        frequencies: dict[str, int] = {}
        for token, _ in surface_tokens:
            frequencies[token.normalized] = frequencies.get(token.normalized, 0) + 1
        deleted = set(sorted(frequencies, key=lambda value: (-frequencies[value], value.encode()))[:20])
        signal = {normalize(concentration_prefix(index)[0] + input_tail(five_tail(index)))[0]
                  for index in range(9)}
        return (primary_core and primary.concentration4 and primary.concentration5 and
                len(deleted) == 20 and signal <= deleted and len(deleted - signal) == 11 and
                all(value == 0.0 for value in top20.raw_coverages) and
                top20.variable_capacity and not top20.rank_pass_01_2)
    if world.world_id == "ONE_FOLIO_CONCENTRATION":
        capacity = raw_facts.get("primary_capacity_folios")
        all_folios_variable = isinstance(capacity, tuple) and capacity == (32,) * 6
        return (primary_core and all_folios_variable and
                primary.positive_folio_counts == (1,) * 6 and
                not primary.concentration4 and not primary.concentration5)
    if world.world_id == "PREFIX_ONLY":
        direct = views["DIRECT_ONLY"]
        return (primary_all and all(value == 0.0 for value in direct.raw_coverages) and
                all(stat.sd == 0.0 for stat in direct.component_stats) and not direct.variable_capacity)
    if world.world_id == "UNKNOWN_SKIP":
        return (raw_facts.get("unknown_clean_equal") is True and primary_core and
                primary.concentration4 and primary.concentration5 and
                views["TOP20_DELETED"].variable_capacity and views["TOP20_DELETED"].rank_pass_01_2 and
                not views["STRICT_LITERAL"].variable_capacity)
    if world.world_id == "ONE_READING_WRONG":
        return (primary.variable_capacity and
                all(value == 0.0 for value in primary.raw_effects[12:18]) and
                not all(value >= 0.020 for value in primary.raw_effects) and
                not primary.rank_pass_001_3)
    raise ValidationStop("unknown adversary")


def scalar_surface_vectors(tokens: Sequence[tuple[Token, bool]], records: Sequence[Mapping[str, object]],
                           width: int, *, deposited: bool, strict_only: bool = False,
                           delete_top20: bool = False) -> SurfaceVectors:
    """Deliberately direct toy reference; it does not use partial constraints."""
    if width not in (4, 6):
        raise ValidationStop("scalar reference is toy-only")
    type_rows = profiles(tokens, strict_only=strict_only, delete_top20=delete_top20)
    folios = sorted({folio for row in type_rows for folio, _ in row.folio_counts})
    orbit = math.factorial(width)
    token_values = array("I", [0]) * orbit
    type_values = array("I", [0]) * orbit
    folio_values = tuple(array("I", [0]) * orbit for _ in folios)
    encoded_keys = {key_code(str(record["key"])) for record in records
                    if reachable(str(record["key"]))}
    match_counts = [0] * len(type_rows)
    for rank in range(orbit):
        permutation = unrank_perm(width, rank)
        for type_index, row in enumerate(type_rows):
            matched = direct_decision(map_template(row.template, permutation), encoded_keys, deposited)
            if not matched:
                continue
            match_counts[type_index] += int(rank != 0)
            token_values[rank] += row.token_count
            type_values[rank] += 1
            counts = dict(row.folio_counts)
            for folio_index, folio in enumerate(folios):
                folio_values[folio_index][rank] += counts.get(folio, 0)
    denominators = tuple(sum(dict(row.folio_counts).get(folio, 0) for row in type_rows)
                         for folio in folios)
    balanced = array("d", [0.0]) * orbit
    for rank in range(orbit):
        total = 0.0
        correction = 0.0
        for values, denominator in zip(folio_values, denominators, strict=True):
            value = float(values[rank]) / denominator
            updated = total + value
            correction += ((total - updated) + value if abs(total) >= abs(value)
                           else (value - updated) + total)
            total = updated
        balanced[rank] = (total + correction) / len(folios) if folios else 0.0
    variable = tuple(0 < count < orbit - 1 for count in match_counts)
    capacity_folios = sum(any(flag and dict(row.folio_counts).get(folio, 0)
                              for flag, row in zip(variable, type_rows, strict=True)) for folio in folios)
    return SurfaceVectors(orbit, token_values, type_values, balanced, folio_values,
                          sum(row.token_count for row in type_rows), len(type_rows), denominators,
                          sum(variable), capacity_folios, True)


def toy_scalar_equality(world: World, optimized: Mapping[str, ViewVectors]) -> bool:
    tokens = world_tokens(world.rows)
    thresholds = {"TOP20_DELETED": (80, 20), "SOURCE_PRESENT": (30, 10)}
    scalar_fingerprints: dict[str, dict[str, object]] = {}
    optimized_fingerprints: dict[str, dict[str, object]] = {}
    for view_name in SCORING_VIEWS:
        records = projected_records(world.lexicon, view_name)
        scalar_surfaces: dict[SurfaceName, SurfaceVectors] = {}
        for surface_name in SURFACE_ORDER:
            direct = scalar_surface_vectors(
                tokens[surface_name], records, world.width,
                deposited=view_name != "DIRECT_ONLY",
                strict_only=view_name == "STRICT_LITERAL",
                delete_top20=view_name == "TOP20_DELETED")
            fast = optimized[view_name].surfaces[surface_name]
            if (little_bytes(direct.token, "<u4") != little_bytes(fast.token, "<u4") or
                    little_bytes(direct.type, "<u4") != little_bytes(fast.type, "<u4") or
                    little_bytes(direct.folio, "<f8") != little_bytes(fast.folio, "<f8") or
                    any(little_bytes(left, "<u4") != little_bytes(right, "<u4")
                        for left, right in zip(direct.folio_numerators,
                                              fast.folio_numerators, strict=True)) or
                    direct.variable_types != fast.variable_types or
                    direct.capacity_folios != fast.capacity_folios):
                return False
            scalar_surfaces[surface_name] = direct
        threshold = thresholds.get(view_name, (100, 20))
        scalar_view = ViewVectors(view_name, scalar_surfaces)
        scalar_fingerprints[view_name] = view_fingerprint(
            scalar_view, world.candidate, *threshold,
            concentration=view_name == "FULL_DEPOSITED_AFFIX")
        optimized_fingerprints[view_name] = view_fingerprint(
            optimized[view_name], world.candidate, *threshold,
            concentration=view_name == "FULL_DEPOSITED_AFFIX")
        if scalar_fingerprints[view_name] != optimized_fingerprints[view_name]:
            return False
    return toy_gate_decision(scalar_fingerprints) == toy_gate_decision(optimized_fingerprints)


def toy_gate_decision(values: Mapping[str, Mapping[str, object]]) -> tuple[bool, ...]:
    primary = values["FULL_DEPOSITED_AFFIX"]
    fixed = (
        bool(primary["rank_pass_001_3"]),
        all(float(value) >= 0.020 for value in primary["raw_effects"]),
        bool(primary["concentration4"]), bool(primary["concentration5"]),
        bool(values["TOP20_DELETED"]["rank_pass_01_2"]),
        bool(values["STRICT_LITERAL"]["rank_pass_01_2"]),
        bool(values["DIRECT_ONLY"]["rank_pass_01_2"]),
        bool(values["STRICT_NO_FUNCTION"]["rank_pass_01_2"]),
    )
    per_view = tuple(bool(values[name]["capacity"]) and bool(values[name]["rank_pass_01_2"])
                     for name in SCORING_VIEWS)
    leaves = tuple(all(float(value) > 0.0 for value in values[name]["raw_effects"])
                   for name in SCORING_VIEWS if name.startswith("LEAVE_"))
    return (*fixed, *per_view, *leaves)


def constraint_weight_table(tokens: Sequence[tuple[Token, bool]], records: Sequence[Mapping[str, object]],
                            width: int, *, deposited: bool,
                            delete_top20: bool = False) -> tuple[dict[Constraint, tuple[int, ...]], int]:
    type_rows = profiles(tokens, delete_top20=delete_top20)
    accepted = preimages((str(record["key"]) for record in records), deposited)
    constraints_by_type = tuple(type_constraints(row.template, accepted, width) for row in type_rows)
    if any(not constraints_disjoint(values, width) for values in constraints_by_type):
        raise ValidationStop("control constraint overlap")
    table: dict[Constraint, list[int]] = {}
    for row, values in zip(type_rows, constraints_by_type, strict=True):
        weights = (row.token_count, 1)
        for value in values:
            current = table.setdefault(value, [0, 0])
            current[0] += weights[0]
            current[1] += weights[1]
    return {key: tuple(value) for key, value in table.items()}, len(type_rows)


def partitioned_constraint_vectors(width: int, table: Mapping[Constraint, tuple[int, ...]],
                                   worker_count: int) -> tuple[array, ...]:
    """Fill disjoint contiguous rank intervals, never constraint partitions."""
    if worker_count not in (1, 32) or not table:
        raise ValidationStop("worker-control contract")
    vector_count = len(next(iter(table.values())))
    baseline = [0] * vector_count
    nonempty: list[tuple[Constraint, tuple[int, ...]]] = []
    for constraint, weights in sorted(table.items()):
        if constraint[0] == 0:
            for index, value in enumerate(weights):
                baseline[index] += value
        else:
            nonempty.append((constraint, weights))
    orbit = math.factorial(width)
    intervals = tuple(((orbit * index) // worker_count,
                       (orbit * (index + 1)) // worker_count)
                      for index in range(worker_count))

    def fill_interval(bounds: tuple[int, int]) -> tuple[array, ...]:
        start, stop = bounds
        output = tuple(array("I", [value]) * (stop - start) for value in baseline)
        for constraint, weights in nonempty:
            for rank in completion_ranks(constraint, width):
                if not start <= rank < stop:
                    continue
                for index, weight in enumerate(weights):
                    updated = output[index][rank - start] + weight
                    if updated >= 2**32:
                        raise ValidationStop("rank-interval uint32 overflow")
                    output[index][rank - start] = updated
        return output

    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        partials = list(pool.map(fill_interval, intervals))
    vectors = tuple(array("I") for _ in range(vector_count))
    for partial in partials:
        for index in range(vector_count):
            vectors[index].extend(partial[index])
    if any(len(value) != orbit for value in vectors):
        raise ValidationStop("rank-interval assembly drift")
    return vectors


def uniform_view_from_two(view_name: str, token: array, type_values: array,
                          type_denominator: int) -> ViewVectors:
    folio = array("d", (float(value) / type_denominator for value in type_values))
    surface = SurfaceVectors(
        len(token), token, type_values, folio, tuple(type_values for _ in range(32)),
        type_denominator * 32, type_denominator, tuple(type_denominator for _ in range(32)),
        type_denominator, 32, True)
    return ViewVectors(view_name, {name: surface for name in SURFACE_ORDER})


def worker_control(plant: World) -> bool:
    tokens = world_tokens(plant.rows)[SURFACE_ORDER[0]]
    table, _ = constraint_weight_table(tokens, plant.lexicon, plant.width, deposited=True)
    one = partitioned_constraint_vectors(plant.width, table, 1)
    thirty_two = partitioned_constraint_vectors(plant.width, table, 32)
    if not all(little_bytes(left, "<u4") == little_bytes(right, "<u4")
               for left, right in zip(one, thirty_two, strict=True)):
        return False
    left_view = uniform_view_from_two("FULL_DEPOSITED_AFFIX", one[0], one[1], 256)
    right_view = uniform_view_from_two("FULL_DEPOSITED_AFFIX", thirty_two[0], thirty_two[1], 256)
    return view_fingerprint(left_view, plant.candidate, 100, 20, concentration=True) == view_fingerprint(
        right_view, plant.candidate, 100, 20, concentration=True)


def conjugacy_control(plant: World) -> bool:
    rho, _ = first_nonidentity("conjugacy-permutation", 10)
    inverse = [0] * 10
    for index, value in enumerate(rho):
        inverse[value] = index
    token_map = world_tokens(plant.rows)
    original_fingerprints: dict[str, dict[str, object]] = {}
    renamed_fingerprints: dict[str, dict[str, object]] = {}

    def renamed_surface(surface_tokens: Sequence[tuple[Token, bool]],
                        records: Sequence[Mapping[str, object]], *, deposited: bool,
                        strict_only: bool, delete_top20: bool) -> tuple[SurfaceVectors, SurfaceVectors]:
        type_rows = profiles(surface_tokens, strict_only=strict_only,
                             delete_top20=delete_top20)
        folios = sorted({folio for row in type_rows for folio, _ in row.folio_counts})
        folio_columns = [tuple(dict(row.folio_counts).get(folio, 0) for row in type_rows)
                         for folio in folios]
        unique_columns: list[tuple[int, ...]] = []
        folio_to_column: list[int] = []
        for column in folio_columns:
            if column not in unique_columns:
                unique_columns.append(column)
            folio_to_column.append(unique_columns.index(column))
        columns = [tuple(row.token_count for row in type_rows),
                   tuple(1 for _ in type_rows), *unique_columns]
        accepted = preimages((str(record["key"]) for record in records), deposited)
        constraints = tuple(type_constraints(row.template, accepted, 10)
                            for row in type_rows)
        transformed_by_type: list[tuple[Constraint, ...]] = []
        for values in constraints:
            renamed_values: set[Constraint] = set()
            for _, required in values:
                renamed_required = [255] * 10
                renamed_mask = 0
                for input_index, output_index in enumerate(required):
                    if output_index == 255:
                        continue
                    renamed_required[rho[input_index]] = rho[output_index]
                    renamed_mask |= 1 << rho[input_index]
                renamed_values.add((renamed_mask, tuple(renamed_required)))
            transformed_by_type.append(tuple(sorted(renamed_values)))
        table: dict[Constraint, list[int]] = {}
        for type_index, values in enumerate(transformed_by_type):
            weights = [column[type_index] for column in columns]
            for value in values:
                current = table.setdefault(value, [0] * len(columns))
                for weight_index, weight in enumerate(weights):
                    current[weight_index] += weight
        renamed_raw = enumerate_constraint_vectors(
            10, {key: tuple(value) for key, value in table.items()}, len(columns))
        orbit = math.factorial(10)
        reindexed = tuple(array("I", [0]) * orbit for _ in renamed_raw)
        for rank in range(orbit):
            permutation = unrank_perm(10, rank)
            conjugated = tuple(rho[permutation[inverse[index]]] for index in range(10))
            renamed_rank = rank_perm(conjugated)
            for weight_index, values in enumerate(renamed_raw):
                reindexed[weight_index][rank] = values[renamed_rank]
        identity = tuple(range(10))
        nonidentity_counts = [sum(constraint_count(value, 10) for value in values) -
                              int(any(constraint_matches(value, identity) for value in values))
                              for values in transformed_by_type]
        variable = [0 < count < orbit - 1 for count in nonidentity_counts]
        capacity_folios = sum(any(flag and dict(row.folio_counts).get(folio, 0)
                                  for flag, row in zip(variable, type_rows, strict=True))
                              for folio in folios)
        folio_vectors = tuple(reindexed[2 + index] for index in folio_to_column)
        folio_denominators = tuple(sum(column) for column in folio_columns)
        transformed = SurfaceVectors(
            orbit, reindexed[0], reindexed[1],
            _balanced_folio_vector(folio_vectors, folio_denominators, orbit),
            folio_vectors, sum(row.token_count for row in type_rows), len(type_rows),
            folio_denominators, sum(variable), capacity_folios,
            preimages((str(record["key"]) for record in records), deposited) ==
            literal_preimages((str(record["key"]) for record in records), deposited))
        original = surface_vectors(
            surface_tokens, records, 10, deposited=deposited,
            strict_only=strict_only, delete_top20=delete_top20)
        return original, transformed

    for view_name in SCORING_VIEWS:
        records = projected_records(plant.lexicon, view_name)
        original_surfaces: dict[SurfaceName, SurfaceVectors] = {}
        renamed_surfaces: dict[SurfaceName, SurfaceVectors] = {}
        for surface_name in SURFACE_ORDER:
            original, transformed = renamed_surface(
                token_map[surface_name], records,
                deposited=view_name != "DIRECT_ONLY",
                strict_only=view_name == "STRICT_LITERAL",
                delete_top20=view_name == "TOP20_DELETED")
            if not surface_raw_capacity_equal(original, transformed):
                return False
            original_surfaces[surface_name] = original
            renamed_surfaces[surface_name] = transformed
        original_view = ViewVectors(view_name, original_surfaces)
        renamed_view = ViewVectors(view_name, renamed_surfaces)
        threshold = ((80, 20) if view_name == "TOP20_DELETED" else
                     (30, 10) if view_name == "SOURCE_PRESENT" else (100, 20))
        original_fingerprints[view_name] = view_fingerprint(
            original_view, plant.candidate, *threshold,
            concentration=view_name == "FULL_DEPOSITED_AFFIX")
        renamed_fingerprints[view_name] = view_fingerprint(
            renamed_view, plant.candidate, *threshold,
            concentration=view_name == "FULL_DEPOSITED_AFFIX")
        if original_fingerprints[view_name] != renamed_fingerprints[view_name]:
            return False
    return toy_gate_decision(original_fingerprints) == toy_gate_decision(renamed_fingerprints)


def parser_assertions(rows: Sequence[Row]) -> dict[str, bool]:
    manual = panel_projection(rows, "MANUAL_GROUP")
    dot = panel_projection(rows, "DOT_ONLY_EMULATION")
    return {
        "PARSER_PRIMARY_SELECTION": all(
            [value["normalized_eva"] for value in manual if value["edition"] == edition] ==
            ["kdr", "lny", "qy", "mg", "kd"] for edition in EDITIONS),
        "PARSER_SEPARATOR_STATES": all(row.separators == (",", "<->", "<~>", ".") for row in rows),
        "PARSER_PANEL_INDEPENDENCE": all(
            [value["normalized_eva"] for value in dot if value["edition"] == edition] ==
            ["kdrlnyqymg", "kd"] for edition in EDITIONS),
        "PARSER_STRICT_PROPAGATION": (
            sum(bool(value["strict_literal_eligible"]) for value in manual) == 6 and
            sum(bool(value["strict_literal_eligible"]) for value in dot) == 3),
    }


def mutation_assertions(plant: World, parser_rows: Sequence[Row],
                        records: Sequence[Mapping[str, object]]) -> dict[str, bool]:
    base = ordered_rows(plant.rows)
    output: dict[str, bool] = {}
    for name, operation in (("EMPTY_PANEL", lambda: ordered_rows(())),
                            ("DUPLICATE_ROW", lambda: ordered_rows((*base, base[0])))):
        try:
            operation()
            output[f"MUTATION_{name}"] = False
        except ValidationStop:
            output[f"MUTATION_{name}"] = True
    first = plant.lexicon[0]
    entries_bytes = json.dumps(first["entries"], sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    key_bytes = json.dumps(first["key"], ensure_ascii=True)
    duplicate_records = [f'{{"entries":{entries_bytes},"key":{key_bytes},"key":{key_bytes}}}']
    duplicate_records.extend(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                        ensure_ascii=True, allow_nan=False)
                             for value in plant.lexicon[1:])
    duplicate = ("[" + ",".join(duplicate_records) + "]\n").encode()
    try:
        strict_json(duplicate)
        output["MUTATION_DUPLICATE_JSON_KEY"] = False
    except ValidationStop:
        output["MUTATION_DUPLICATE_JSON_KEY"] = True
    token_reversed = tuple(replace(row, groups=row.groups[::-1], separators=row.separators[::-1])
                           for row in base)
    output["MUTATION_TOKEN_REVERSE"] = (row_bytes(token_reversed) != row_bytes(base) and all(
        sorted(row.groups) == sorted(changed.groups)
        for row, changed in zip(base, token_reversed, strict=True)))
    output["MUTATION_ROW_REVERSE"] = row_bytes(base[::-1]) != row_bytes(base) and ordered_rows(base[::-1]) == base
    reversed_lexicon = tuple(reversed(plant.lexicon))
    output["MUTATION_LEXICON_REVERSE"] = (
        canonical(list(reversed_lexicon)) != canonical(list(plant.lexicon)) and
        {str(value["key"]) for value in reversed_lexicon} == {str(value["key"]) for value in plant.lexicon})
    malformed = (("UNMATCHED_SQUARE", "[k"), ("NESTED_SQUARE", "[[k]]"),
                 ("UNMATCHED_BRACE", "{k"), ("NESTED_BRACE", "{{k}}"),
                 ("UNMATCHED_ANGLE", "<k"), ("NESTED_ANGLE", "<<k>>"))
    for name, raw in malformed:
        try:
            compile_token(raw, 1)
            output[f"MUTATION_{name}"] = False
        except ValidationStop:
            output[f"MUTATION_{name}"] = True
    try:
        preimages(("kkkkkkkkkkk",), True)
        output["MUTATION_OVERLENGTH_PREIMAGE"] = False
    except ValidationStop:
        output["MUTATION_OVERLENGTH_PREIMAGE"] = True
    overlength = compile_token("kdrslnqymgk", 1)
    output["MUTATION_OVERLENGTH_TOKEN"] = bool(overlength and len(overlength[0].template) == 11 and
                                                not type_constraints(overlength[0].template,
                                                                     preimages((str(v["key"]) for v in records), True), 10))
    unknown_pairs = tuple((compile_token(raw, 1), compile_token(raw + "b", 1))
                          for raw in base_groups(10))
    output["MUTATION_UNKNOWN_INSERT"] = bool(len(base) * len(base_groups(10)) == 24576 and all(
        clean and unknown and clean[0].template == unknown[0].template and clean[1] and not unknown[1]
        for clean, unknown in unknown_pairs))
    missing_rf = tuple(row for row in base if row.edition != "RF1b")
    try:
        ordered_rows(missing_rf)
        output["MUTATION_MISSING_EDITION"] = False
    except ValidationStop:
        output["MUTATION_MISSING_EDITION"] = True
    try:
        Row("ZL3b", "fRos", "P.1", ("kd",), ())
        output["MUTATION_PAGE_DOMAIN"] = False
    except ValidationStop:
        output["MUTATION_PAGE_DOMAIN"] = True
    try:
        Row("ZL3b", "f2r", "P.1", ("kd",), ())
        output["MUTATION_FOLIO_DRIFT"] = False
    except ValidationStop:
        output["MUTATION_FOLIO_DRIFT"] = True
    retained = tuple(value for value in plant.lexicon if reachable(str(value["key"])))
    saved_removed = tuple(value for value in plant.lexicon if not reachable(str(value["key"])))
    full_direct = preimages((str(value["key"]) for value in plant.lexicon), True)
    retained_direct = preimages((str(value["key"]) for value in retained), True)
    output["MUTATION_UNREACHABLE_REMOVE"] = full_direct == retained_direct
    restored = tuple(sorted((*retained, *saved_removed),
                            key=lambda value: str(value["key"]).encode()))
    output["MUTATION_UNREACHABLE_RESTORE_ADD_FROM_REMOVED"] = canonical(list(restored)) == canonical(list(plant.lexicon))
    expected = {f"MUTATION_{name}" for name in (
        "EMPTY_PANEL", "DUPLICATE_ROW", "DUPLICATE_JSON_KEY", "TOKEN_REVERSE", "ROW_REVERSE",
        "LEXICON_REVERSE", *(name for name, _ in malformed), "OVERLENGTH_PREIMAGE", "OVERLENGTH_TOKEN",
        "UNKNOWN_INSERT", "MISSING_EDITION", "PAGE_DOMAIN", "FOLIO_DRIFT", "UNREACHABLE_REMOVE",
        "UNREACHABLE_RESTORE_ADD_FROM_REMOVED")}
    if set(output) != expected or len(output) != 20:
        raise ValidationStop("mutation assertion reconstruction drift")
    output.update(mutation_numeric_assertions(plant))
    return output


def all_world_views_equal(left: Mapping[str, ViewVectors], right: Mapping[str, ViewVectors],
                          candidate: int, *, exclude: set[str] | None = None) -> bool:
    excluded = exclude or set()
    thresholds = {"TOP20_DELETED": (80, 20), "SOURCE_PRESENT": (30, 10)}
    for name in SCORING_VIEWS:
        if name in excluded:
            continue
        threshold = thresholds.get(name, (100, 20))
        if not view_exact_equal(left[name], right[name], candidate, *threshold,
                                concentration=name == "FULL_DEPOSITED_AFFIX"):
            return False
    return True


def world_gate_decision_fingerprint(views: Mapping[str, ViewVectors],
                                    candidate: int) -> tuple[bool, ...]:
    thresholds = {"TOP20_DELETED": (80, 20), "SOURCE_PRESENT": (30, 10)}
    fingerprints = {
        name: view_fingerprint(
            views[name], candidate, *thresholds.get(name, (100, 20)),
            concentration=name == "FULL_DEPOSITED_AFFIX")
        for name in SCORING_VIEWS
    }
    return toy_gate_decision(fingerprints)


def mutation_numeric_assertions(plant: World) -> dict[str, bool]:
    base_rows = ordered_rows(plant.rows)
    token_rows = tuple(replace(row, groups=row.groups[::-1], separators=row.separators[::-1])
                       for row in base_rows)
    row_rows = base_rows[::-1]
    reversed_lexicon = tuple({"key": value["key"], "entries": list(reversed(value["entries"]))}
                             for value in reversed(plant.lexicon))
    output = {
        "MUTATION_TOKEN_REVERSE": True,
        "MUTATION_ROW_REVERSE": True,
        "MUTATION_LEXICON_REVERSE": True,
    }
    first = base_rows[0]
    extended = replace(first, groups=(*first.groups, "kdrslnqymgk"),
                       separators=(*first.separators, "."))
    zero_numerators = True
    denominator_delta = True
    unknown_rows = tuple(replace(row, groups=tuple(value + "b" for value in row.groups))
                         for row in base_rows)
    output["MUTATION_UNKNOWN_INSERT"] = True
    reachable_records = tuple(value for value in plant.lexicon if reachable(str(value["key"])))
    saved_removed = tuple(value for value in plant.lexicon if not reachable(str(value["key"])))
    restored_records = tuple(sorted((*reachable_records, *saved_removed),
                                    key=lambda value: str(value["key"]).encode()))
    output["MUTATION_UNREACHABLE_REMOVE"] = True
    output["MUTATION_UNREACHABLE_RESTORE_ADD_FROM_REMOVED"] = (
        canonical(list(restored_records)) == canonical(list(plant.lexicon)))
    thresholds = {"TOP20_DELETED": (80, 20), "SOURCE_PRESENT": (30, 10)}
    budget = LiveStateBudget()
    for view_name in SCORING_VIEWS:
        threshold = thresholds.get(view_name, (100, 20))
        budget.acquire()
        base_view = build_one_world_view(plant, view_name, surface_cache={})
        for key, changed_world in (
                ("MUTATION_TOKEN_REVERSE", replace(plant, rows=token_rows)),
                ("MUTATION_ROW_REVERSE", replace(plant, rows=row_rows)),
                ("MUTATION_LEXICON_REVERSE", replace(plant, lexicon=reversed_lexicon))):
            budget.acquire()
            changed_view = build_one_world_view(changed_world, view_name, surface_cache={})
            output[key] = output[key] and view_exact_equal(
                base_view, changed_view, plant.candidate, *threshold,
                concentration=view_name == "FULL_DEPOSITED_AFFIX")
            del changed_view
            budget.release()
        budget.acquire()
        overlength_view = build_one_world_view(
            replace(plant, rows=(extended, *base_rows[1:])), view_name,
            surface_cache={})
        for surface_name in SURFACE_ORDER:
            left = base_view.surfaces[surface_name]
            right = overlength_view.surfaces[surface_name]
            affected = surface_name[0] == "ZL3b"
            expected_delta = 1 if affected else 0
            zero_numerators = zero_numerators and (
                little_bytes(left.token, "<u4") == little_bytes(right.token, "<u4") and
                little_bytes(left.type, "<u4") == little_bytes(right.type, "<u4") and
                all(little_bytes(a, "<u4") == little_bytes(b, "<u4")
                    for a, b in zip(left.folio_numerators, right.folio_numerators, strict=True)))
            denominator_delta = denominator_delta and (
                right.token_denominator - left.token_denominator == expected_delta and
                right.type_denominator - left.type_denominator == expected_delta and
                sum(b - a for a, b in zip(left.folio_denominators,
                                          right.folio_denominators, strict=True)) == expected_delta and
                all(b - a in ({0, 1} if affected else {0})
                    for a, b in zip(left.folio_denominators,
                                    right.folio_denominators, strict=True)))
        del overlength_view
        budget.release()
        budget.acquire()
        unknown_view = build_one_world_view(
            replace(plant, rows=unknown_rows), view_name, surface_cache={})
        if view_name == "STRICT_LITERAL":
            output["MUTATION_UNKNOWN_INSERT"] = output["MUTATION_UNKNOWN_INSERT"] and all(
                not unknown_view.surfaces[name].token_denominator for name in SURFACE_ORDER)
        else:
            output["MUTATION_UNKNOWN_INSERT"] = output["MUTATION_UNKNOWN_INSERT"] and view_exact_equal(
                base_view, unknown_view, plant.candidate, *threshold,
                concentration=view_name == "FULL_DEPOSITED_AFFIX")
        del unknown_view
        budget.release()
        for key, records in (("MUTATION_UNREACHABLE_REMOVE", reachable_records),
                             ("MUTATION_UNREACHABLE_RESTORE_ADD_FROM_REMOVED", restored_records)):
            budget.acquire()
            changed_view = build_one_world_view(
                plant, view_name, records_override=projected_records(records, view_name),
                surface_cache={})
            output[key] = output[key] and view_exact_equal(
                base_view, changed_view, plant.candidate, *threshold,
                concentration=view_name == "FULL_DEPOSITED_AFFIX")
            del changed_view
            budget.release()
        del base_view
        budget.release()
    if budget.live != 0 or budget.peak > MAX_LIVE_VECTOR_STATES:
        raise ValidationStop("mutation streaming liveness drift")
    output["MUTATION_OVERLENGTH_TOKEN"] = zero_numerators and denominator_delta
    return output


@dataclass(slots=True)
class SyntheticOutcome:
    controls: dict[str, dict[str, object]]
    gate: bool
    successful_plants: int
    null_false_passes: int
    reconstructed: dict[str, object]


_FORK_WORLDS: tuple[World, ...] = ()


def evaluate_world_index(index: int) -> WorldEvaluation:
    if not 0 <= index < len(_FORK_WORLDS):
        raise ValidationStop("forked world index")
    gc.collect()
    output = evaluate_world(_FORK_WORLDS[index])
    gc.collect()
    return output


def control_member(name: str, assertion_ids: Sequence[str], outcomes: Mapping[str, bool],
                   gate: bool, *, successful: int | None = None,
                   false_passes: int | None = None,
                   evidence: Mapping[str, str] | None = None) -> dict[str, object]:
    assertions: list[dict[str, object]] = []
    for assertion_id in assertion_ids:
        item: dict[str, object] = {
            "id": assertion_id, "passed": bool(outcomes.get(assertion_id, False))}
        if name in {"affix_equivalence", "unreachable_invariance"}:
            value = None if evidence is None else evidence.get(assertion_id)
            if not isinstance(value, str) or not HEX64.fullmatch(value):
                raise ValidationStop("missing invariant assertion evidence digest")
            item["evidence_sha256"] = value
        assertions.append(item)
    passed = sum(bool(value["passed"]) for value in assertions)
    base: dict[str, object] = {
        "control": name, "assertions": assertions, "total": len(assertions),
        "passed": passed, "failed": len(assertions) - passed, "gate": bool(gate),
    }
    if name == "plants":
        if successful is None:
            raise ValidationStop("missing plant aggregate")
        base.update(successful=successful, threshold=95)
    if name == "nulls":
        if false_passes is None:
            raise ValidationStop("missing null aggregate")
        base.update(false_passes=false_passes, threshold=1)
    public = {key: value for key, value in base.items() if key not in {"control", "assertions"}}
    public["aggregate_sha256"] = digest(canonical(base))
    return public


def null_independence(world: World) -> bool:
    if world.family != "NULL" or world.secret is not None or world.alternate is not None:
        return False
    candidate = world.candidate
    # Probe rank is selected in a disjoint label domain and never appears among
    # the frozen null-key-tail call fields.
    key_draws = [value for value in world.draws if value.label == "null-key-tail"]
    probe_draws = [value for value in world.draws if value.label == "null-probe-rank"]
    return bool(key_draws and probe_draws and
                all(len(value.fields) == 4 for value in key_draws) and
                all(value.fields[1] == world.trial for value in key_draws) and
                all(value.fields == (math.factorial(10) - 1, world.trial, collision)
                    for collision, value in enumerate(probe_draws)) and
                candidate == world.candidate)


def run_synthetic(manifest: Mapping[str, object], worlds: Sequence[World]) -> SyntheticOutcome:
    expectations = manifest.get("aggregate_expectations")
    if not isinstance(expectations, dict) or not isinstance(expectations.get("assertion_ids"), dict):
        raise ValidationStop("synthetic expectation schema")
    assertion_ids = expectations["assertion_ids"]
    evaluations: dict[str, WorldEvaluation] = {}
    toy_equalities: dict[str, bool] = {}
    global _FORK_WORLDS
    _FORK_WORLDS = tuple(worlds)
    context = multiprocessing.get_context("fork")
    toy_indices = tuple(index for index, world in enumerate(worlds) if world.width < 10)
    width10_indices = tuple(index for index, world in enumerate(worlds) if world.width == 10)
    toy_scored = tuple(evaluate_world_index(index) for index in toy_indices)
    with ProcessPoolExecutor(max_workers=WIDTH10_WORLD_WORKERS,
                             mp_context=context) as pool:
        width10_scored = tuple(pool.map(evaluate_world_index, width10_indices, chunksize=1))
    by_id = {value.world_id: value for value in (*toy_scored, *width10_scored)}
    scored = tuple(by_id[world.world_id] for world in worlds)
    _FORK_WORLDS = ()
    evaluations.update((value.world_id, value) for value in scored)
    for world in worlds[:4]:
        toy_equalities[world.world_id] = toy_scalar_equality(world, build_world_views(world))
    plant = next(value for value in worlds if value.world_id == "PLANT_000")
    parser_rows, _ = parser_fixture()
    outcomes: dict[str, dict[str, bool]] = {name: {} for name in CONTROL_ORDER}
    toy_ids = assertion_ids["toys"]
    for assertion_id, world in zip(toy_ids, worlds[:4], strict=True):
        outcomes["toys"][assertion_id] = toy_equalities[world.world_id]
    plant_worlds = tuple(value for value in worlds if value.family == "PLANT")
    for assertion_id, world in zip(assertion_ids["plants"], plant_worlds, strict=True):
        outcomes["plants"][assertion_id] = evaluations[world.world_id].plant_success
    null_worlds = tuple(value for value in worlds if value.family == "NULL")
    for assertion_id, world in zip(assertion_ids["nulls"][:-1], null_worlds, strict=True):
        outcomes["nulls"][assertion_id] = null_independence(world)
    null_false_passes = sum(evaluations[world.world_id].null_false_pass for world in null_worlds)
    outcomes["nulls"][assertion_ids["nulls"][-1]] = null_false_passes <= 1
    adversaries = tuple(value for value in worlds if value.family == "ADVERSARY")
    for assertion_id, world in zip(assertion_ids["adversaries"], adversaries, strict=True):
        outcomes["adversaries"][assertion_id] = evaluations[world.world_id].signature_pass
    outcomes["parser"] = parser_assertions(parser_rows)
    outcomes["mutations"] = mutation_assertions(plant, parser_rows, plant.lexicon)
    outcomes["conjugacy"]["CONJUGACY_VECTOR_EQUALITY"] = conjugacy_control(plant)
    outcomes["workers"]["WORKER_1_32_VECTOR_EQUALITY"] = worker_control(plant)
    for assertion_id, world in zip(assertion_ids["affix_equivalence"], worlds, strict=True):
        outcomes["affix_equivalence"][assertion_id] = evaluations[world.world_id].affix_equivalence
    width10 = tuple(value for value in worlds if value.width == 10)
    for assertion_id, world in zip(assertion_ids["unreachable_invariance"], width10, strict=True):
        outcomes["unreachable_invariance"][assertion_id] = evaluations[world.world_id].unreachable_invariance
    evidence_by_control = {
        "affix_equivalence": {
            assertion_id: evaluations[world.world_id].affix_evidence_sha256
            for assertion_id, world in zip(assertion_ids["affix_equivalence"], worlds, strict=True)
        },
        "unreachable_invariance": {
            assertion_id: str(evaluations[world.world_id].unreachable_evidence_sha256)
            for assertion_id, world in zip(assertion_ids["unreachable_invariance"], width10, strict=True)
        },
    }
    successful = sum(evaluations[world.world_id].plant_success for world in plant_worlds)
    gates = {name: all(outcomes[name].get(assertion_id, False)
                       for assertion_id in assertion_ids[name]) for name in CONTROL_ORDER}
    gates["plants"] = successful >= 95
    gates["nulls"] = gates["nulls"] and null_false_passes <= 1
    controls = {
        name: control_member(name, assertion_ids[name], outcomes[name], gates[name],
                             successful=successful if name == "plants" else None,
                             false_passes=null_false_passes if name == "nulls" else None,
                             evidence=evidence_by_control.get(name))
        for name in CONTROL_ORDER
    }
    aggregate = digest(canonical({"schema": "dani001-validator-synthetic-aggregate-v1",
                                  "controls": controls}))
    reconstructed = {
        "world_count": len(worlds),
        "row_count": sum(len(world.rows) for world in worlds),
        "permutation_count": sum(math.factorial(world.width) for world in worlds),
        "vector_component_count": len(worlds) * len(SCORING_VIEWS) * 18,
        "parser_assertion_count": 4,
        "mutation_assertion_count": 20,
        "capacity_view_count": 0,
        "synthetic_aggregate_sha256": aggregate,
    }
    return SyntheticOutcome(controls, all(gates.values()), successful,
                            null_false_passes, reconstructed)


FREEZE_KEYS = (
    "schema", "registered_commit", "science_spec", "calibration_spec",
    "local_inputs", "external_inputs", "code", "synthetic_manifest",
    "runtime", "core_build", "read_allowlist", "network_allowlist",
    "temporary_allowlist", "producer_outputs_absent", "validator_outputs_absent",
    "producer_write_allowlist", "validator_write_allowlist", "static_audit",
)
PRODUCER_KEYS = (
    "schema", "experiment", "status", "claim_ceiling", "registered_science",
    "calibration_spec", "calibration_freeze_sha256", "synthetic_manifest_sha256",
    "runtime", "isolation", "input_checks", "synthetic_controls", "actual_capacity",
    "identity_access", "decision",
)
ISOLATION_KEYS = (
    "read_allowlist_pass", "write_allowlist_pass", "network_allowlist_pass",
    "temporary_allowlist_pass", "output_destinations_absent_pass",
    "acquisition_inventory_pass", "synthetic_gate_actual_access_pass",
    "forbidden_read_count", "forbidden_write_count", "forbidden_network_count",
    "temporary_inventory_violation_count", "output_collision_count",
    "pre_synthetic_actual_local_read_count", "pre_synthetic_lexicon_projection_call_count",
    "post_synthetic_lexicon_projection_call_count",
)
INPUT_CHECK_KEYS = (
    "registered_commit_pass", "science_spec_pass", "calibration_spec_pass",
    "calibration_freeze_pass", "synthetic_manifest_pass", "code_hashes_pass",
    "runtime_pass", "compiler_binary_pass", "core_build_pass",
    "external_pipeline_body_pass", "external_lexicon_body_pass",
    "stable_projection_pass", "local_inputs_pass",
)
IDENTITY_KEYS = (
    "rank0_requests", "rank0_maps_evaluated", "rank0_match_calls",
    "rank0_values_stored", "rank0_values_inferred", "actual_rank_interval_start",
    "actual_rank_interval_stop", "actual_primary_logical_view_surfaces",
    "actual_evidence_logical_view_surfaces", "actual_logical_view_surfaces",
    "actual_primary_logical_map_view_evaluations",
    "actual_evidence_logical_map_view_evaluations",
    "actual_logical_map_view_evaluations",
)
OPAQUE_CODE_RELS = (
    "experiments/semantic_assumptions/dani001_panel.py",
    "experiments/semantic_assumptions/dani001_calibration_generator.py",
    "experiments/semantic_assumptions/dani001_core.py",
    "experiments/semantic_assumptions/dani001_core.h",
    "experiments/semantic_assumptions/dani001_core.cpp",
    "experiments/semantic_assumptions/run_dani001_target_blind_calibration.py",
)
COMPILER_VERSION = (
    "x86_64-linux-gnu-g++-12 (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0\n"
    "Copyright (C) 2022 Free Software Foundation, Inc.\n"
    "This is free software; see the source for copying conditions.  There is NO\n"
    "warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n\n"
).encode()
CORE_ARGV = (
    "/usr/bin/x86_64-linux-gnu-g++-12", "-std=c++20", "-O3", "-DNDEBUG", "-fPIC",
    "-shared", "-fopenmp", "-fno-fast-math", "-ffp-contract=off",
    "dani001_core.cpp", "-o", "libdani001_core.so",
)


def repo_path(relative: str) -> Path:
    if relative.startswith("/") or ".." in Path(relative).parts:
        raise ValidationStop("noncanonical repository path")
    value = (ROOT / relative).resolve()
    if value == ROOT or ROOT not in value.parents:
        raise ValidationStop("path escapes repository")
    return value


class AuditPolicy:
    def __init__(self) -> None:
        initial = (SCIENCE_REL, CALIBRATION_REL, MANIFEST_REL, FREEZE_REL,
                   PRODUCER_RESULT_REL, PRODUCER_REPORT_REL, *OPAQUE_CODE_RELS,
                   str(Path(__file__).resolve().relative_to(ROOT)))
        self.reads = {repo_path(value) for value in initial}
        self.validation_writes = {repo_path(VALIDATION_RESULT_REL), repo_path(VALIDATION_REPORT_REL)}
        self.temporary_roots: set[Path] = set()
        self.network_enabled = False
        self.violations: list[str] = []

    def under_temp(self, value: Path) -> bool:
        return any(value == root or root in value.parents for root in self.temporary_roots)

    def violation(self, detail: str) -> None:
        self.violations.append(detail)
        raise ValidationStop(detail)

    def hook(self, event: str, args: tuple[object, ...]) -> None:
        if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            mode = args[1] if len(args) > 1 else "r"
            flags = args[2] if len(args) > 2 else 0
            writing = ((isinstance(mode, str) and any(value in mode for value in "wax+")) or
                       (isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT))))
            if writing:
                if path not in self.validation_writes and not self.under_temp(path):
                    self.violation("forbidden write")
            elif (path not in self.reads and path not in self.validation_writes and
                  not self.under_temp(path) and
                  not (path == RESULTS.resolve() and isinstance(flags, int) and flags & os.O_DIRECTORY)):
                self.violation("forbidden read")
        elif event in {"socket.connect", "socket.getaddrinfo"} and not self.network_enabled:
            self.violation("forbidden network")
        elif event == "os.mkdir" and args:
            path = Path(os.fsdecode(args[0])).resolve()
            permitted_fresh = (path.parent == Path("/tmp") and
                               path.name.startswith(("dani001-validator-stage-",
                                                     "dani001-validator-acquisition-")))
            if not self.under_temp(path) and not permitted_fresh:
                self.violation("forbidden directory creation")
        elif event in {"os.listdir", "os.scandir"} and args:
            path = Path(os.fsdecode(args[0])).resolve()
            if not self.under_temp(path):
                self.violation("forbidden directory read")
        elif event in {"os.remove", "os.unlink", "os.rename", "os.replace", "os.rmdir"} and args:
            path = Path(os.fsdecode(args[0])).resolve()
            if path not in self.validation_writes and not self.under_temp(path):
                self.violation("forbidden mutation")
        elif event in {"os.link", "os.symlink"} and len(args) >= 2:
            source = Path(os.fsdecode(args[0])).resolve()
            target = Path(os.fsdecode(args[1])).resolve()
            if not self.under_temp(source) or target not in self.validation_writes:
                self.violation("forbidden link")


def path_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValidationStop(f"{label} is not a path object")
    exact_keys(value, ("path", "sha256", "size"), label)
    path, sha, size = value["path"], value["sha256"], value["size"]
    if not isinstance(path, str) or not isinstance(sha, str) or not HEX64.fullmatch(sha):
        raise ValidationStop(f"{label} path/hash drift")
    if type(size) is not int or size < 0:
        raise ValidationStop(f"{label} size drift")
    return value


def verify_bound_path(value: object, expected_rel: str | None, label: str) -> dict[str, object]:
    record = path_object(value, label)
    relative = str(record["path"])
    if expected_rel is not None and relative != expected_rel:
        raise ValidationStop(f"{label} path mismatch")
    sha, size = hash_file(repo_path(relative))
    if sha != record["sha256"] or size != record["size"]:
        raise ValidationStop(f"{label} bytes mismatch")
    return record


def load_contract(expected_freeze_sha: str, policy: AuditPolicy) -> tuple[dict[str, object], bytes, bytes, bytes]:
    if not HEX64.fullmatch(expected_freeze_sha):
        raise ValidationStop("invalid expected freeze SHA-256")
    try:
        process = ctypes.CDLL(None)
        fegetround = process.fegetround
        fegetround.argtypes = []
        fegetround.restype = ctypes.c_int
        rounding_mode = fegetround()
    except (AttributeError, OSError) as error:
        raise ValidationStop("cannot verify live floating-point rounding mode") from error
    if not hasattr(time, "tzset"):
        raise ValidationStop("live timezone reset is unavailable")
    time.tzset()
    if (sys.version_info[:3] != (3, 12, 3) or
            platform.python_implementation() != "CPython" or
            platform.system() != "Linux" or sys.byteorder != "little" or
            platform.machine() != "x86_64" or struct.calcsize("d") != 8 or
            struct.pack("<d", 1.0) != b"\x00\x00\x00\x00\x00\x00\xf0?" or
            LIVE_NUMPY_VERSION != "1.26.4" or rounding_mode != 0 or
            locale.setlocale(locale.LC_ALL, None) != "C" or
            os.environ.get("TZ") != "UTC" or time.tzname != ("UTC", "UTC") or
            time.timezone != 0 or time.daylight != 0):
        raise ValidationStop("validator runtime contract drift")
    science = repo_path(SCIENCE_REL).read_bytes()
    calibration = repo_path(CALIBRATION_REL).read_bytes()
    manifest_bytes = repo_path(MANIFEST_REL).read_bytes()
    freeze_bytes = repo_path(FREEZE_REL).read_bytes()
    if digest(science) != SCIENCE_SHA or digest(calibration) != CALIBRATION_SHA:
        raise ValidationStop("registered prose bytes mismatch")
    if digest(manifest_bytes) != MANIFEST_SHA or digest(freeze_bytes) != expected_freeze_sha:
        raise ValidationStop("manifest/freeze hash mismatch")
    freeze = strict_json(freeze_bytes)
    if not isinstance(freeze, dict):
        raise ValidationStop("freeze is not an object")
    if canonical(freeze) != freeze_bytes:
        raise ValidationStop("calibration freeze is not canonical JSON")
    exact_keys(freeze, FREEZE_KEYS, "calibration freeze")
    if freeze["schema"] != "dani001-target-blind-calibration-freeze-v1" or freeze["registered_commit"] != SCIENCE_COMMIT:
        raise ValidationStop("registered commit drift")
    verify_bound_path(freeze["science_spec"], SCIENCE_REL, "freeze science spec")
    verify_bound_path(freeze["calibration_spec"], CALIBRATION_REL, "freeze calibration spec")
    verify_bound_path(freeze["synthetic_manifest"], MANIFEST_REL, "freeze synthetic manifest")
    local = freeze["local_inputs"]
    if not isinstance(local, list) or len(local) != 5:
        raise ValidationStop("freeze local input array drift")
    local_records = [path_object(value, f"freeze local input[{index}]")
                     for index, value in enumerate(local)]
    expected_local_order = [*SOURCE_REL.values(), ATLAS_REL, ATLAS_VALIDATION_REL]
    if [str(value["path"]) for value in local_records] != expected_local_order or any(
            value["sha256"] != LOCAL_SHA[relative]
            for relative, value in zip(expected_local_order, local_records, strict=True)):
        raise ValidationStop("freeze local input registration drift")
    code = freeze["code"]
    if not isinstance(code, list) or len(code) != 7:
        raise ValidationStop("freeze code array drift")
    expected_code = (*OPAQUE_CODE_RELS, str(Path(__file__).resolve().relative_to(ROOT)))
    for index, (record, expected) in enumerate(zip(code, expected_code, strict=True)):
        verify_bound_path(record, expected, f"freeze code[{index}]")
    static = freeze["static_audit"]
    if not isinstance(static, dict):
        raise ValidationStop("freeze static audit")
    exact_keys(static, ("status", "review_id", "auditor_source_sha256"), "freeze static audit")
    if (static["status"], static["review_id"]) != (
            "GO", "DANI001_CALIBRATION_FREEZE_STATIC_AUDIT_V1") or not isinstance(
                static["auditor_source_sha256"], str) or not HEX64.fullmatch(static["auditor_source_sha256"]):
        raise ValidationStop("freeze static audit not GO")
    expected_read_allowlist = [SCIENCE_REL, CALIBRATION_REL, FREEZE_REL, MANIFEST_REL,
                               *OPAQUE_CODE_RELS,
                               *SOURCE_REL.values(), ATLAS_REL, ATLAS_VALIDATION_REL]
    if freeze["read_allowlist"] != expected_read_allowlist:
        raise ValidationStop("validator read allowlist cannot be derived from freeze")
    external_expected = [
        {"name": "stable_metadata_projection", "url": EXTERNAL_URLS[0],
         "sha256": "780301fd3c4b2c3c328c1f69a1eab65d0b0600f2d491ea9578f81699d36ddfa7",
         "storage": "MEMORY_ONLY_CANONICAL_PROJECTION"},
        {"name": "pipeline_body", "url": EXTERNAL_URLS[1],
         "sha256": "079b6de7b8d2082303a0789fb3904105aecaa491e35600a557090e7981255d6f",
         "storage": "EXTERNAL_TEMPORARY_ONLY_INERT"},
        {"name": "lexicon_body", "url": EXTERNAL_URLS[2],
         "sha256": "348992fa2bf555f1454a5a5485dd1ca9842acc143059f257f2fcdcf237821589",
         "storage": "EXTERNAL_TEMPORARY_ONLY_PROJECT_AFTER_SYNTHETICS"},
    ]
    if freeze["external_inputs"] != external_expected:
        raise ValidationStop("external input freeze projection drift")
    if freeze["network_allowlist"] != [value["url"] for value in external_expected]:
        raise ValidationStop("network allowlist drift")
    if freeze["temporary_allowlist"] != [
            "EXTERNAL_ACQUISITION_EXACT_THREE_FILES", "CORE_BUILD_CPP_HEADER_LIBRARY",
            "OUTPUT_STAGING_TWO_FILES"]:
        raise ValidationStop("temporary allowlist drift")
    producer_outputs = [PRODUCER_RESULT_REL, PRODUCER_REPORT_REL]
    validator_outputs = [VALIDATION_RESULT_REL, VALIDATION_REPORT_REL]
    if freeze["producer_outputs_absent"] != producer_outputs or freeze["producer_write_allowlist"] != producer_outputs:
        raise ValidationStop("producer output arrays drift")
    if freeze["validator_write_allowlist"] != [VALIDATION_RESULT_REL, VALIDATION_REPORT_REL]:
        raise ValidationStop("validator write allowlist drift")
    if freeze["validator_outputs_absent"] != [VALIDATION_RESULT_REL, VALIDATION_REPORT_REL]:
        raise ValidationStop("validator absence list drift")
    runtime = freeze["runtime"]
    if not isinstance(runtime, dict):
        raise ValidationStop("freeze runtime is not an object")
    runtime_keys = ("python", "implementation", "machine", "system", "byteorder", "binary64",
                    "numpy", "locale", "timezone", "workers", "openmp_library_name",
                    "openmp_library_sha256", "runtime_image_sha256")
    exact_keys(runtime, runtime_keys, "freeze runtime")
    expected_runtime_fixed = {
        "python": "3.12.3", "implementation": "CPython", "machine": "x86_64",
        "system": "Linux", "byteorder": "little",
        "binary64": "IEEE754_ROUND_TO_NEAREST", "numpy": "1.26.4",
        "locale": "C", "timezone": "UTC", "workers": [1, 32],
    }
    for name, expected in expected_runtime_fixed.items():
        exact_json_equal(runtime[name], expected, f"freeze runtime.{name}")
    if (type(runtime["openmp_library_name"]) is not str or not runtime["openmp_library_name"] or
            type(runtime["openmp_library_sha256"]) is not str or
            not HEX64.fullmatch(runtime["openmp_library_sha256"])):
        raise ValidationStop("freeze OpenMP runtime drift")
    runtime_preimage = {key: runtime[key] for key in runtime_keys[:-1]}
    if (type(runtime["runtime_image_sha256"]) is not str or
            runtime["runtime_image_sha256"] != digest(canonical(runtime_preimage))):
        raise ValidationStop("freeze runtime-image digest drift")
    core_build = freeze["core_build"]
    if not isinstance(core_build, dict):
        raise ValidationStop("freeze core build is not an object")
    core_keys = ("compiler_path", "compiler_sha256", "compiler_version_stdout_hex", "argv",
                 "shared_library_sha256", "abi_version", "runtime_image_sha256")
    exact_keys(core_build, core_keys, "freeze core build")
    for name, expected in (
            ("compiler_path", "/usr/bin/x86_64-linux-gnu-g++-12"),
            ("compiler_sha256", "1cfb9704049655d08accca3b1aeefd6fc749ef2cfb992ec95a81f39091d7b3ce"),
            ("compiler_version_stdout_hex", COMPILER_VERSION.hex()),
            ("argv", list(CORE_ARGV)), ("abi_version", 1),
            ("runtime_image_sha256", runtime["runtime_image_sha256"])):
        exact_json_equal(core_build[name], expected, f"freeze core_build.{name}")
    if (type(core_build["shared_library_sha256"]) is not str or
            not HEX64.fullmatch(core_build["shared_library_sha256"])):
        raise ValidationStop("freeze core build drift")
    if any(os.path.lexists(repo_path(value)) for value in freeze["validator_outputs_absent"]):
        raise ValidationStop("validation output collision")
    return freeze, manifest_bytes, science, calibration


@dataclass(slots=True)
class ActualRankAudit:
    rank0_requests: int = 0
    rank0_maps_evaluated: int = 0
    rank0_match_calls: int = 0
    rank0_values_stored: int = 0
    rank0_values_inferred: int = 0
    primary_intervals: list[tuple[int, int]] = field(default_factory=list)
    evidence_intervals: list[tuple[int, int]] = field(default_factory=list)
    compiler_interval_requests: int = 0
    compiler_pruned_nodes: int = 0
    compiler_constraint_pruned_nodes: int = 0
    compiler_visited_nodes: int = 0
    compiler_nonidentity_leaves: int = 0
    compiler_completed_rank0_leaves: int = 0
    primary_logical_map_view_evaluations: int = 0
    evidence_logical_map_view_evaluations: int = 0

    def record_vector_surface(self, start: int, stop: int, vector_length: int,
                              role: str) -> None:
        if (start, stop) != (1, 3628800) or vector_length != stop - start:
            self.rank0_requests += int(start == 0)
            raise ValidationStop("actual vector surface rank interval drift")
        if role == "primary":
            self.primary_intervals.append((start, stop))
            self.primary_logical_map_view_evaluations += vector_length
        elif role == "evidence":
            self.evidence_intervals.append((start, stop))
            self.evidence_logical_map_view_evaluations += vector_length
        else:
            raise ValidationStop("actual vector surface audit role")

    def public(self, *, opened: bool) -> dict[str, object]:
        primary_surfaces = len(self.primary_intervals)
        evidence_surfaces = len(self.evidence_intervals)
        total_surfaces = primary_surfaces + evidence_surfaces
        total_evaluations = (self.primary_logical_map_view_evaluations +
                             self.evidence_logical_map_view_evaluations)
        if opened and (primary_surfaces != 72 or evidence_surfaces != 18 or
                       total_surfaces != 90 or
                       self.primary_logical_map_view_evaluations != 261273528 or
                       self.evidence_logical_map_view_evaluations != 65318382 or
                       total_evaluations != 326591910):
            raise ValidationStop("actual logical surface counter drift")
        if opened and (self.compiler_interval_requests <= 0 or
                       self.compiler_visited_nodes <= 0 or
                       self.compiler_nonidentity_leaves <= 0 or
                       self.compiler_completed_rank0_leaves != 0):
            raise ValidationStop("actual compiler instrumentation absent")
        return {
            "rank0_requests": self.rank0_requests,
            "rank0_maps_evaluated": self.rank0_maps_evaluated,
            "rank0_match_calls": self.rank0_match_calls,
            "rank0_values_stored": self.rank0_values_stored,
            "rank0_values_inferred": self.rank0_values_inferred,
            "actual_rank_interval_start": 1 if opened else None,
            "actual_rank_interval_stop": 3628800 if opened else None,
            "actual_primary_logical_view_surfaces": primary_surfaces if opened else 0,
            "actual_evidence_logical_view_surfaces": evidence_surfaces if opened else 0,
            "actual_logical_view_surfaces": total_surfaces if opened else 0,
            "actual_primary_logical_map_view_evaluations": (
                self.primary_logical_map_view_evaluations if opened else 0),
            "actual_evidence_logical_map_view_evaluations": (
                self.evidence_logical_map_view_evaluations if opened else 0),
            "actual_logical_map_view_evaluations": total_evaluations if opened else 0,
        }


def producer_markdown(result: Mapping[str, object], json_sha: str) -> bytes:
    controls = result["synthetic_controls"]
    if not isinstance(controls, dict):
        raise ValidationStop("producer controls schema")
    passed = sum(int(controls[name]["passed"]) for name in CONTROL_ORDER)
    total = sum(int(controls[name]["total"]) for name in CONTROL_ORDER)
    plants = controls["plants"]
    nulls = controls["nulls"]
    actual = result["actual_capacity"]
    actual_label = "NOT_OPENED" if actual is None else ("PASS" if actual["mandatory_capacity_pass"] else "FAIL")
    return (
        "# DANI001 target-blind calibration\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Synthetic controls: `{passed}/{total}`\n"
        f"- Distributed plants: `{plants['successful']}/100` (required >=95)\n"
        f"- Map-independent null false passes: `{nulls['false_passes']}/128` (required <=1)\n"
        f"- Actual mandatory capacity: `{actual_label}`\n"
        "- Real rank-0 evaluations: `0`\n"
        "- Real rank-0 inferences: `0`\n"
        f"- Decision: `{result['decision']}`\n"
        "- Claim ceiling: conditional engineering calibration only; no language, lexeme, plaintext, or translation.\n"
        f"- Result JSON SHA-256: `{json_sha}`\n"
    ).encode("utf-8")


def expected_identity_access(opened: bool) -> dict[str, object]:
    return {
        "rank0_requests": 0, "rank0_maps_evaluated": 0,
        "rank0_match_calls": 0, "rank0_values_stored": 0,
        "rank0_values_inferred": 0,
        "actual_rank_interval_start": 1 if opened else None,
        "actual_rank_interval_stop": 3628800 if opened else None,
        "actual_primary_logical_view_surfaces": 72 if opened else 0,
        "actual_evidence_logical_view_surfaces": 18 if opened else 0,
        "actual_logical_view_surfaces": 90 if opened else 0,
        "actual_primary_logical_map_view_evaluations": 261273528 if opened else 0,
        "actual_evidence_logical_map_view_evaluations": 65318382 if opened else 0,
        "actual_logical_map_view_evaluations": 326591910 if opened else 0,
    }


def validate_actual_capacity_schema(value: object) -> None:
    if not isinstance(value, dict):
        raise ValidationStop("producer actual capacity object type")
    exact_keys(value, (
        "panel_counts", "lexicon_counts", "views", "mandatory_capacity_pass",
        "conditional_view_statuses", "actual_nonidentity_vector_digest_sha256",
        "implementation_invariant_digest_sha256"), "producer actual capacity")
    panel_counts = value["panel_counts"]
    if type(panel_counts) is not list or len(panel_counts) != 6:
        raise ValidationStop("producer panel-count array drift")
    for index, ((edition, panel), item) in enumerate(zip(
            SURFACE_ORDER, panel_counts, strict=True)):
        if not isinstance(item, dict):
            raise ValidationStop("producer panel-count object type")
        exact_keys(item, ("edition", "panel", "token_count", "normalized_type_count",
                          "folio_count", "strict_literal_token_count"),
                   f"producer panel_counts[{index}]")
        exact_json_equal(item["edition"], edition, f"producer panel edition[{index}]")
        exact_json_equal(item["panel"], panel, f"producer panel name[{index}]")
        for name in ("token_count", "normalized_type_count", "folio_count",
                     "strict_literal_token_count"):
            json_int(item[name], f"producer panel_counts[{index}].{name}")
    lexicon = value["lexicon_counts"]
    if not isinstance(lexicon, dict):
        raise ValidationStop("producer lexicon-count object type")
    exact_keys(lexicon, (
        "keys", "entries", "reachable_keys", "unreachable_keys",
        "source_present_keys", "source_present_reachable_keys",
        "strict_no_function_keys", "strict_no_function_reachable_keys", "views"),
        "producer lexicon counts")
    for name in ("keys", "entries", "reachable_keys", "unreachable_keys",
                 "source_present_keys", "source_present_reachable_keys",
                 "strict_no_function_keys", "strict_no_function_reachable_keys"):
        json_int(lexicon[name], f"producer lexicon_counts.{name}")
    public_views = (
        "FULL", "REACHABLE", "SOURCE_PRESENT", "STRICT_NO_FUNCTION",
        "LEAVE_OUT_ASTRO", "LEAVE_OUT_BOTANICAL", "LEAVE_OUT_FUNCTION",
        "LEAVE_OUT_GENERAL", "LEAVE_OUT_MEDICAL", "LEAVE_OUT_PHARMA")
    lexicon_views = lexicon["views"]
    if type(lexicon_views) is not list or len(lexicon_views) != len(public_views):
        raise ValidationStop("producer lexicon view array drift")
    for index, (name, item) in enumerate(zip(public_views, lexicon_views, strict=True)):
        if not isinstance(item, dict):
            raise ValidationStop("producer lexicon view object type")
        exact_keys(item, ("view", "total_key_count", "reachable_key_count",
                          "direct_code_count", "deposited_affix_code_count"),
                   f"producer lexicon view[{index}]")
        exact_json_equal(item["view"], name, f"producer lexicon view name[{index}]")
        for field_name in ("total_key_count", "reachable_key_count", "direct_code_count",
                           "deposited_affix_code_count"):
            json_int(item[field_name], f"producer lexicon view[{index}].{field_name}")
    views = value["views"]
    if type(views) is not list or len(views) != len(SCORING_VIEWS):
        raise ValidationStop("producer actual scoring-view array drift")
    surface_keys = (
        "edition", "panel", "variable_type_count", "capacity_folio_count",
        "token_sd_positive", "type_sd_positive", "folio_sd_positive",
        "token_nonidentity_vector_sha256", "type_nonidentity_vector_sha256",
        "folio_nonidentity_vector_sha256", "affix_equivalence")
    for view_index, (view_name, item) in enumerate(zip(SCORING_VIEWS, views, strict=True)):
        if not isinstance(item, dict):
            raise ValidationStop("producer actual view object type")
        exact_keys(item, ("view", "surfaces"), f"producer actual view[{view_index}]")
        exact_json_equal(item["view"], view_name, f"producer actual view name[{view_index}]")
        surfaces = item["surfaces"]
        if type(surfaces) is not list or len(surfaces) != 6:
            raise ValidationStop("producer actual surface array drift")
        for surface_index, ((edition, panel), surface) in enumerate(zip(
                SURFACE_ORDER, surfaces, strict=True)):
            if not isinstance(surface, dict):
                raise ValidationStop("producer actual surface object type")
            exact_keys(surface, surface_keys,
                       f"producer actual view[{view_index}].surface[{surface_index}]")
            exact_json_equal(surface["edition"], edition, "producer actual surface edition")
            exact_json_equal(surface["panel"], panel, "producer actual surface panel")
            json_int(surface["variable_type_count"], "producer actual variable type count")
            json_int(surface["capacity_folio_count"], "producer actual capacity folio count")
            for field_name in ("token_sd_positive", "type_sd_positive", "folio_sd_positive"):
                json_bool(surface[field_name], f"producer actual {field_name}")
            for field_name in ("token_nonidentity_vector_sha256",
                               "type_nonidentity_vector_sha256",
                               "folio_nonidentity_vector_sha256"):
                if type(surface[field_name]) is not str or not HEX64.fullmatch(surface[field_name]):
                    raise ValidationStop(f"producer actual {field_name} digest drift")
            affix = surface["affix_equivalence"]
            if view_name == "FULL_DEPOSITED_AFFIX":
                json_bool(affix, "producer actual affix equivalence")
            elif affix is not None:
                raise ValidationStop("producer nonprimary affix member must be null")
    json_bool(value["mandatory_capacity_pass"], "producer mandatory capacity pass")
    conditional_names = (
        "SOURCE_PRESENT", "LEAVE_ASTRO_OUT", "LEAVE_BOTANICAL_OUT",
        "LEAVE_FUNCTION_OUT", "LEAVE_GENERAL_OUT", "LEAVE_MEDICAL_OUT",
        "LEAVE_PHARMA_OUT")
    conditional = value["conditional_view_statuses"]
    if type(conditional) is not list or len(conditional) != len(conditional_names):
        raise ValidationStop("producer conditional status array drift")
    for index, (name, item) in enumerate(zip(conditional_names, conditional, strict=True)):
        if not isinstance(item, dict):
            raise ValidationStop("producer conditional status object type")
        exact_keys(item, ("view", "status"), f"producer conditional[{index}]")
        exact_json_equal(item["view"], name, f"producer conditional name[{index}]")
        if type(item["status"]) is not str or item["status"] not in {"POWERED", "INSUFFICIENT"}:
            raise ValidationStop("producer conditional status value drift")
    for name in ("actual_nonidentity_vector_digest_sha256",
                 "implementation_invariant_digest_sha256"):
        if type(value[name]) is not str or not HEX64.fullmatch(value[name]):
            raise ValidationStop(f"producer {name} drift")


def validate_common_producer(result: object, result_bytes: bytes, report_bytes: bytes,
                             freeze: Mapping[str, object], freeze_sha: str,
                             synthetic: SyntheticOutcome) -> Mapping[str, object]:
    if not isinstance(result, dict):
        raise ValidationStop("producer result is not an object")
    exact_keys(result, PRODUCER_KEYS, "producer result")
    if canonical(result) != result_bytes:
        raise ValidationStop("producer JSON is not canonical")
    for name, expected in (("schema", SCHEMA_RESULT), ("experiment", "DANI001"),
                           ("claim_ceiling", CLAIM_CEILING),
                           ("calibration_freeze_sha256", freeze_sha),
                           ("synthetic_manifest_sha256", MANIFEST_SHA)):
        exact_json_equal(result[name], expected, f"producer {name}")
    exact_json_equal(result["registered_science"], freeze["science_spec"],
                     "producer registered science")
    exact_json_equal(result["calibration_spec"], freeze["calibration_spec"],
                     "producer calibration spec")
    if type(result["status"]) is not str or type(result["decision"]) is not str or result[
            "status"] != result["decision"]:
        raise ValidationStop("producer status/decision disagreement")
    exact_json_equal(result["synthetic_controls"], synthetic.controls,
                     "producer synthetic reconstruction")
    exact_json_equal(result["runtime"], freeze["runtime"], "producer runtime")
    isolation = result["isolation"]
    checks = result["input_checks"]
    identity = result["identity_access"]
    if not isinstance(isolation, dict) or not isinstance(checks, dict) or not isinstance(identity, dict):
        raise ValidationStop("producer contract object type")
    exact_keys(isolation, ISOLATION_KEYS, "producer isolation")
    exact_keys(checks, INPUT_CHECK_KEYS, "producer input checks")
    exact_keys(identity, IDENTITY_KEYS, "producer identity access")
    expected_isolation = {
        **{name: True for name in ISOLATION_KEYS[:7]},
        **{name: 0 for name in ISOLATION_KEYS[7:-1]},
        ISOLATION_KEYS[-1]: 1 if synthetic.gate else 0,
    }
    exact_json_equal(isolation, expected_isolation, "producer isolation")
    expected_checks = {
        **{name: True for name in INPUT_CHECK_KEYS[:-1]},
        INPUT_CHECK_KEYS[-1]: True if synthetic.gate else None,
    }
    exact_json_equal(checks, expected_checks, "producer input checks")
    exact_json_equal(identity, expected_identity_access(synthetic.gate),
                     "producer identity access")
    if synthetic.gate:
        validate_actual_capacity_schema(result["actual_capacity"])
    elif result["actual_capacity"] is not None:
        raise ValidationStop("producer opened actual capacity after synthetic failure")
    result_sha = digest(result_bytes)
    if producer_markdown(result, result_sha) != report_bytes:
        raise ValidationStop("producer report byte mismatch")
    return result


def validate_synthetic_failure(result: Mapping[str, object], synthetic: SyntheticOutcome) -> None:
    decision = "STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED"
    if synthetic.gate or result["actual_capacity"] is not None:
        raise ValidationStop("synthetic-failure branch disagreement")
    exact_json_equal(result["decision"], decision, "synthetic-failure decision")
    exact_json_equal(result["identity_access"], expected_identity_access(False),
                     "unopened identity counters")
    if result["input_checks"]["local_inputs_pass"] is not None:
        raise ValidationStop("actual local input was opened after synthetic failure")
    if result["isolation"]["post_synthetic_lexicon_projection_call_count"] != 0:
        raise ValidationStop("lexicon projected after synthetic failure")


@dataclass(frozen=True, slots=True)
class ActualRow:
    edition: str
    page: str
    locus: str
    groups: tuple[str, ...] = field(repr=False)
    separators: tuple[str, ...] = field(repr=False)

    @property
    def folio(self) -> int | None:
        matched = PAGE_REAL.fullmatch(self.page)
        return int(matched.group(1)) if matched else None


def split_source_text(text_value: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    groups: list[str] = []
    separators: list[str] = []
    current: list[str] = []
    cursor = 0
    while cursor < len(text_value):
        pair = text_value[cursor:cursor + 3]
        if pair in {"<->", "<~>"}:
            marker = pair
            cursor += 3
        elif text_value[cursor] in ".,":
            marker = text_value[cursor]
            cursor += 1
        else:
            marker = ""
        if marker:
            value = "".join(current).strip()
            if not value:
                raise ValidationStop("empty or repeated source group boundary")
            groups.append(value)
            separators.append(ATLAS_SEPARATOR[marker])
            current = []
            continue
        value = text_value[cursor]
        if value == "<":
            end = text_value.find(">", cursor + 1)
            if end < 0:
                raise ValidationStop("unterminated source angle form")
            form = text_value[cursor:end + 1]
            if "<" in form[1:-1]:
                raise ValidationStop("nested source angle form")
            if form not in {"<%>", "<$>"}:
                current.append(form)
            cursor = end + 1
            continue
        if value in "[{":
            close = "]" if value == "[" else "}"
            end = text_value.find(close, cursor + 1)
            if end < 0:
                raise ValidationStop("unterminated source annotation form")
            body = text_value[cursor:end + 1]
            if value in body[1:-1] or close in body[1:-1]:
                raise ValidationStop("nested source annotation form")
            current.append(body)
            cursor = end + 1
            continue
        if value in ">]}":
            raise ValidationStop("unmatched source closing delimiter")
        current.append(value)
        cursor += 1
    final = "".join(current).strip()
    if not final or not groups and not final:
        raise ValidationStop("trailing boundary or empty source row")
    groups.append(final)
    if len(separators) != len(groups) - 1:
        raise ValidationStop("source topology drift")
    if any(any(character in value for character in "\t\r\n") for value in groups):
        raise ValidationStop("TSV-unsafe source group")
    return tuple(groups), tuple(separators)


def legacy_fragments(raw: str) -> tuple[str, ...]:
    value = re.sub(r"\[([^:\]]+)(?::[^\]]*)?\]", r"\1", raw)
    value = re.sub(r"\{[^}]*\}", "", value)
    value = re.sub(r"<[^>]*>", " ", value)
    value = value.translate({ord(character): None for character in "?!*'"})
    pieces = re.split(r"[\s.,;:=/\\|+\-]+", value)
    output = []
    for piece in pieces:
        cleaned = "".join(character.lower() for character in piece
                          if "a" <= character <= "z" or "A" <= character <= "Z")
        if cleaned:
            output.append(cleaned)
    return tuple(output)


def reconstruct_atlas(source_bodies: Mapping[str, bytes]) -> tuple[bytes, tuple[ActualRow, ...]]:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=ATLAS_COLUMNS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    actual_rows: list[ActualRow] = []
    seen: set[tuple[str, str]] = set()
    source_rows = 0
    group_rows = 0
    boundaries = 0
    for edition in EDITIONS:
        body = source_bodies.get(edition)
        if not isinstance(body, bytes):
            raise ValidationStop("missing raw source body")
        try:
            lines = body.decode("utf-8", "strict").splitlines()
        except UnicodeDecodeError as error:
            raise ValidationStop("raw source UTF-8 failure") from error
        page: str | None = None
        metadata: dict[str, str] = {}
        source_row_index = 0
        for line in lines:
            header = PAGE_HEADER.match(line)
            if header:
                page = header.group(1).lower()
                metadata = {key: value for key, value in METADATA.findall(header.group(2))}
                continue
            matched = SOURCE_ROW.match(line)
            if not matched:
                continue
            if page is None:
                raise ValidationStop("source row before page header")
            locus, code, _comment, text_value = matched.groups()
            identity = (edition, locus)
            if identity in seen:
                raise ValidationStop("duplicate edition/locus")
            seen.add(identity)
            source_row_index += 1
            groups, separators = split_source_text(text_value)
            fragments = tuple(legacy_fragments(value) for value in groups)
            flattened_count = sum(len(value) for value in fragments)
            next_position = 1
            paragraph_start = int("<%>" in text_value)
            paragraph_end = int("<$>" in text_value)
            section, currier, hand = (metadata.get(value, "") for value in ("I", "L", "H"))
            for group_index, (raw, cleaned) in enumerate(zip(groups, fragments, strict=True), 1):
                positions = tuple(range(next_position, next_position + len(cleaned)))
                next_position += len(cleaned)
                status_value = ("ZERO_ASCII_FRAGMENT" if not cleaned else
                                "ONE_ASCII_FRAGMENT" if len(cleaned) == 1 else "MULTI_ASCII_FRAGMENT")
                writer.writerow({
                    "source_group_id": f"{edition}|{locus}|G{group_index:03d}",
                    "edition": edition, "locus": locus, "page": page,
                    "section": section, "currier": currier, "hand": hand,
                    "code": code, "kind": code[1] if len(code) > 1 else "",
                    "grammar_scope": ("CONFIRMED_PROSE" if len(code) > 1 and code[1] == "P" and
                                      currier in {"A", "B"} else "DIAGNOSTIC_NONPROSE"),
                    "source_row_index": source_row_index, "source_group_index": group_index,
                    "source_group_count": len(groups), "paragraph_start": paragraph_start,
                    "paragraph_end": paragraph_end,
                    "left_separator": "LINE_START" if group_index == 1 else separators[group_index - 2],
                    "right_separator": "LINE_END" if group_index == len(groups) else separators[group_index - 1],
                    "ivtff_group_raw": raw, "clean_ascii_fragments": " ".join(cleaned),
                    "clean_ascii_fragment_count": len(cleaned),
                    "legacy_surface_positions_1based": ",".join(str(value) for value in positions),
                    "legacy_interlinear_row_present": int(flattened_count > 0),
                    "legacy_mapping_status": status_value,
                })
                group_rows += 1
            actual_rows.append(ActualRow(edition, page, locus, groups, separators))
            boundaries += len(separators)
            source_rows += 1
    reconstructed = output.getvalue().encode("utf-8")
    if (source_rows, group_rows, boundaries, len(reconstructed), digest(reconstructed)) != (
            15985, 115470, 99485, 16754953,
            "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0"):
        raise ValidationStop("independent atlas reconstruction count/hash drift")
    return reconstructed, tuple(actual_rows)


def actual_panel_tokens(rows: Sequence[ActualRow]) -> dict[SurfaceName, tuple[tuple[Token, bool], ...]]:
    excluded = tuple(row for row in rows if row.folio is None)
    retained = tuple(row for row in rows if row.folio is not None)
    if (sum(len(row.groups) for row in excluded), len(excluded), len({row.locus for row in excluded}),
        sum(len(row.groups) for row in retained), len(retained)) != (1083, 320, 160, 114387, 15665):
        raise ValidationStop("actual page-domain exclusion counts drift")
    unconsumed = 0
    for row in retained:
        for raw in row.groups:
            normalized, _ = normalize(raw)
            template, complete = scan(normalized)
            unconsumed += int(len(normalized) >= 2 and bool(template) and not complete)
    if unconsumed != 280:
        raise ValidationStop("actual unconsumed-scanner count drift")
    output: dict[SurfaceName, tuple[tuple[Token, bool], ...]] = {}
    for edition, panel in SURFACE_ORDER:
        tokens: list[tuple[Token, bool]] = []
        for row in rows:
            if row.edition != edition or row.folio is None:
                continue
            if panel == "MANUAL_GROUP":
                raw_groups = row.groups
            else:
                joined: list[str] = []
                current = row.groups[0]
                for separator, group in zip(row.separators, row.groups[1:], strict=True):
                    if separator == "DEFINITE_SPACE":
                        joined.append(current)
                        current = group
                    else:
                        current += group
                joined.append(current)
                raw_groups = tuple(joined)
            for raw in raw_groups:
                compiled = compile_token(raw, row.folio)
                if compiled is not None:
                    tokens.append(compiled)
        output[(edition, panel)] = tuple(tokens)
    return output


def stable_metadata_projection(concept_bytes: bytes) -> bytes:
    source = strict_json(concept_bytes)
    if not isinstance(source, dict):
        raise ValidationStop("concept response is not an object")
    try:
        metadata = source["metadata"]
        files = source["files"]
        if not isinstance(metadata, dict) or not isinstance(files, list):
            raise ValidationStop("concept nested container type")
        projected_files = []
        for item in files:
            if not isinstance(item, dict) or not isinstance(item.get("links"), dict):
                raise ValidationStop("concept file object type")
            projected_files.append({
                "key": item["key"], "size": item["size"], "checksum": item["checksum"],
                "url": item["links"]["self"],
            })
        projection = {
            "id": source["id"], "conceptrecid": source["conceptrecid"],
            "revision": source["revision"], "doi": source["doi"],
            "created": source["created"], "updated": source["updated"],
            "metadata": {"title": metadata["title"],
                         "publication_date": metadata["publication_date"],
                         "description": metadata["description"]},
            "files": projected_files,
        }
    except KeyError as error:
        raise ValidationStop("concept projection member absent") from error
    body = canonical(projection)
    if digest(body) != "780301fd3c4b2c3c328c1f69a1eab65d0b0600f2d491ea9578f81699d36ddfa7":
        raise ValidationStop("stable metadata projection hash drift")
    return body


@dataclass(frozen=True, slots=True)
class LexiconProjection:
    records: tuple[dict[str, object], ...] = field(repr=False)
    key_count: int
    entry_count: int
    reachable_count: int
    source_present_count: int
    source_present_reachable_count: int
    strict_no_function_count: int
    strict_no_function_reachable_count: int


def project_lexicon(lexicon_bytes: bytes) -> LexiconProjection:
    source = strict_json(lexicon_bytes)
    if not isinstance(source, dict):
        raise ValidationStop("deposited lexicon is not an object")
    records: list[dict[str, object]] = []
    entry_count = 0
    domains = set(ALL_DOMAINS)
    for key in sorted(source, key=lambda value: value.encode("utf-8")):
        if not isinstance(key, str) or not key:
            raise ValidationStop("empty or nonstring lexicon key")
        raw_entries = source[key]
        if not isinstance(raw_entries, list) or not raw_entries:
            raise ValidationStop("empty or nonarray lexicon entries")
        projected_entries: list[dict[str, object]] = []
        for raw_entry in raw_entries:
            if not isinstance(raw_entry, dict):
                raise ValidationStop("lexicon entry is not an object")
            source_value = raw_entry.get("source")
            if source_value is not None and not isinstance(source_value, str):
                raise ValidationStop("lexicon source type")
            domain = raw_entry.get("domain")
            if domain in (None, ""):
                domain = "missing"
            elif not isinstance(domain, str) or domain not in domains:
                raise ValidationStop("lexicon domain value")
            projected_entries.append({"source_present": bool(source_value), "domain": domain})
            entry_count += 1
        records.append({"key": key, "entries": projected_entries})
    source_records = tuple(projected_records(records, "SOURCE_PRESENT"))
    strict_records = tuple(projected_records(records, "STRICT_NO_FUNCTION"))
    projected = LexiconProjection(
        tuple(records), len(records), entry_count,
        sum(reachable(str(value["key"])) for value in records),
        len(source_records), sum(reachable(str(value["key"])) for value in source_records),
        len(strict_records), sum(reachable(str(value["key"])) for value in strict_records),
    )
    if (projected.key_count, projected.entry_count, projected.reachable_count,
        projected.key_count - projected.reachable_count, projected.source_present_count,
        projected.source_present_reachable_count, projected.strict_no_function_count,
        projected.strict_no_function_reachable_count) != (1389, 1441, 819, 570, 104, 55, 1243, 738):
        raise ValidationStop("deposited lexicon registered totals drift")
    for view in SCORING_VIEWS:
        records_view = projected_records(projected.records, view)
        accepted = preimages((str(value["key"]) for value in records_view), view != "DIRECT_ONLY")
        if any(len(value) > 10 for value in accepted):
            raise ValidationStop("external accepted preimage overlength")
    return projected


def actual_lexicon_counts(projected: LexiconProjection) -> dict[str, object]:
    named_views = (
        ("FULL", "FULL_DEPOSITED_AFFIX"), ("REACHABLE", "FULL_DEPOSITED_AFFIX"),
        ("SOURCE_PRESENT", "SOURCE_PRESENT"), ("STRICT_NO_FUNCTION", "STRICT_NO_FUNCTION"),
        *((f"LEAVE_OUT_{domain.upper()}", f"LEAVE_{domain.upper()}_OUT")
          for domain in ALL_DOMAINS),
    )
    view_rows: list[dict[str, object]] = []
    for public_name, scoring_name in named_views:
        records = (tuple(value for value in projected.records if reachable(str(value["key"])))
                   if public_name == "REACHABLE" else projected_records(projected.records, scoring_name))
        reachable_records = tuple(value for value in records if reachable(str(value["key"])))
        direct_codes = {key_code(str(value["key"])) for value in reachable_records}
        affix_codes = set(preimages((str(value["key"]) for value in reachable_records), True))
        view_rows.append({
            "view": public_name, "total_key_count": len(records),
            "reachable_key_count": len(reachable_records),
            "direct_code_count": len(direct_codes),
            "deposited_affix_code_count": len(affix_codes),
        })
    return {
        "keys": projected.key_count, "entries": projected.entry_count,
        "reachable_keys": projected.reachable_count,
        "unreachable_keys": projected.key_count - projected.reachable_count,
        "source_present_keys": projected.source_present_count,
        "source_present_reachable_keys": projected.source_present_reachable_count,
        "strict_no_function_keys": projected.strict_no_function_count,
        "strict_no_function_reachable_keys": projected.strict_no_function_reachable_count,
        "views": view_rows,
    }


def actual_panel_counts(tokens: Mapping[SurfaceName, Sequence[tuple[Token, bool]]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for edition, panel in SURFACE_ORDER:
        values = tokens[(edition, panel)]
        output.append({
            "edition": edition, "panel": panel, "token_count": len(values),
            "normalized_type_count": len({token.normalized for token, _ in values}),
            "folio_count": len({token.folio for token, _ in values}),
            "strict_literal_token_count": sum(strict for _, strict in values),
        })
    return output


def actual_capacity(tokens: Mapping[SurfaceName, Sequence[tuple[Token, bool]]],
                    projected: LexiconProjection) -> tuple[dict[str, object], str, ActualRankAudit]:
    rank_audit = ActualRankAudit()
    view_rows: list[dict[str, object]] = []
    digest_entries: list[dict[str, object]] = []
    affix_invariant_entries: list[dict[str, object]] = []
    unreachable_invariant_entries: list[dict[str, object]] = []
    affix_invariant_pass = True
    unreachable_invariant_pass = True
    powered_by_view: dict[str, bool] = {}
    thresholds = {
        "FULL_DEPOSITED_AFFIX": (100, 20), "DIRECT_ONLY": (100, 20),
        "STRICT_NO_FUNCTION": (100, 20), "STRICT_LITERAL": (100, 20),
        "TOP20_DELETED": (80, 20), "SOURCE_PRESENT": (30, 10),
        **{f"LEAVE_{domain.upper()}_OUT": (100, 20) for domain in ALL_DOMAINS},
    }
    canonical_full_records = tuple(sorted(
        projected.records, key=lambda value: str(value["key"]).encode()))
    if canonical(list(canonical_full_records)) != canonical(list(projected.records)):
        raise ValidationStop("actual full lexicon ordering invariant")
    full_codes = preimages((str(value["key"]) for value in projected.records), True)
    reachable_codes = preimages((str(value["key"]) for value in projected.records
                                 if reachable(str(value["key"]))), True)
    if full_codes != reachable_codes:
        raise ValidationStop("actual unreachable-key invariant")
    for view_name in SCORING_VIEWS:
        records = projected_records(projected.records, view_name)
        surfaces: list[dict[str, object]] = []
        view_powered = True
        for edition, panel in SURFACE_ORDER:
            surface = surface_vectors(
                tokens[(edition, panel)], records, 10,
                deposited=view_name != "DIRECT_ONLY", strict_only=view_name == "STRICT_LITERAL",
                delete_top20=view_name == "TOP20_DELETED", rank_start=1,
                rank_audit=rank_audit, audit_role="primary")
            literal_surface: SurfaceVectors | None = None
            without_unreachable: SurfaceVectors | None = None
            restored_surface: SurfaceVectors | None = None
            if view_name == "FULL_DEPOSITED_AFFIX":
                reachable_records = tuple(
                    value for value in records if reachable(str(value["key"])))
                saved_removed = tuple(
                    value for value in records if not reachable(str(value["key"])))
                if len(reachable_records) + len(saved_removed) != len(records):
                    raise ValidationStop("actual unreachable split drift")
                without_unreachable = surface_vectors(
                    tokens[(edition, panel)], reachable_records, 10,
                    deposited=True, rank_start=1, rank_audit=rank_audit,
                    audit_role="evidence")
                restored_records = tuple(sorted(
                    (*reachable_records, *saved_removed),
                    key=lambda value: str(value["key"]).encode()))
                if len({str(value["key"]) for value in restored_records}) != len(restored_records):
                    raise ValidationStop("actual unreachable restoration duplicate key")
                restored_surface = surface_vectors(
                    tokens[(edition, panel)], restored_records, 10,
                    deposited=True, rank_start=1, rank_audit=rank_audit,
                    audit_role="evidence")
                unreachable_equal = (
                    canonical(list(restored_records)) == canonical(list(records)) and
                    surface_raw_capacity_equal(surface, without_unreachable) and
                    surface_raw_capacity_equal(surface, restored_surface))
                unreachable_invariant_pass = unreachable_invariant_pass and unreachable_equal
                if not unreachable_equal:
                    raise ValidationStop("actual unreachable raw-vector invariant")
                literal_surface = surface_vectors(
                    tokens[(edition, panel)], records, 10, deposited=True, rank_start=1,
                    literal_decision=True, rank_audit=rank_audit,
                    audit_role="evidence")
                affix_equal = (
                    surface_raw_capacity_equal(surface, literal_surface) and
                    literal_surface.literal_decision_function_sha256 ==
                    literal_surface.expanded_decision_function_sha256 and
                    isinstance(literal_surface.literal_decision_function_sha256, str) and
                    bool(HEX64.fullmatch(
                        literal_surface.literal_decision_function_sha256)))
                affix_invariant_pass = affix_invariant_pass and affix_equal
                if not affix_equal:
                    raise ValidationStop("actual literal-decision/raw-vector invariant")
            digests = {
                "TOKEN": digest(little_bytes(surface.token, "<u4")),
                "TYPE": digest(little_bytes(surface.type, "<u4")),
                "FOLIO": digest(little_bytes(surface.folio, "<f8")),
            }
            sd_values = {
                "TOKEN": finite_positive_sd(surface.token),
                "TYPE": finite_positive_sd(surface.type),
                "FOLIO": finite_positive_sd(surface.folio),
            }
            threshold_types, threshold_folios = thresholds[view_name]
            powered = (surface.variable_types >= threshold_types and
                       surface.capacity_folios >= threshold_folios and all(sd_values.values()))
            view_powered = view_powered and powered
            surfaces.append({
                "edition": edition, "panel": panel,
                "variable_type_count": surface.variable_types,
                "capacity_folio_count": surface.capacity_folios,
                "token_sd_positive": sd_values["TOKEN"],
                "type_sd_positive": sd_values["TYPE"],
                "folio_sd_positive": sd_values["FOLIO"],
                "token_nonidentity_vector_sha256": digests["TOKEN"],
                "type_nonidentity_vector_sha256": digests["TYPE"],
                "folio_nonidentity_vector_sha256": digests["FOLIO"],
                "affix_equivalence": surface.affix_equal if view_name == "FULL_DEPOSITED_AFFIX" else None,
            })
            if view_name == "FULL_DEPOSITED_AFFIX" and not surface.affix_equal:
                raise ValidationStop("actual deposited-affix implementation invariant")
            for weighting, dtype in (("TOKEN", "<u4"), ("TYPE", "<u4"), ("FOLIO", "<f8")):
                digest_entries.append({
                    "view": view_name, "edition": edition, "panel": panel,
                    "weighting": weighting, "dtype": dtype, "rank_start": 1,
                    "rank_stop": 3628800, "sha256": digests[weighting],
                })
                if view_name == "FULL_DEPOSITED_AFFIX":
                    if (literal_surface is None or without_unreachable is None or
                            restored_surface is None):
                        raise ValidationStop("missing actual invariant evidence surface")
                    expanded_values = {"TOKEN": surface.token, "TYPE": surface.type,
                                       "FOLIO": surface.folio}[weighting]
                    literal_values = {"TOKEN": literal_surface.token,
                                      "TYPE": literal_surface.type,
                                      "FOLIO": literal_surface.folio}[weighting]
                    without_values = {"TOKEN": without_unreachable.token,
                                      "TYPE": without_unreachable.type,
                                      "FOLIO": without_unreachable.folio}[weighting]
                    restored_values = {"TOKEN": restored_surface.token,
                                       "TYPE": restored_surface.type,
                                       "FOLIO": restored_surface.folio}[weighting]
                    affix_invariant_entries.append({
                        "edition": edition, "panel": panel, "weighting": weighting,
                        "dtype": dtype,
                        "literal_decision_function_sha256":
                        literal_surface.literal_decision_function_sha256,
                        "literal_raw_sha256": digest(little_bytes(literal_values, dtype)),
                        "expanded_decision_function_sha256":
                        literal_surface.expanded_decision_function_sha256,
                        "expanded_raw_sha256": digest(little_bytes(expanded_values, dtype)),
                    })
                    unreachable_invariant_entries.append({
                        "edition": edition, "panel": panel, "weighting": weighting,
                        "dtype": dtype,
                        "full_raw_sha256": digest(little_bytes(expanded_values, dtype)),
                        "without_raw_sha256": digest(little_bytes(without_values, dtype)),
                        "restored_raw_sha256": digest(little_bytes(restored_values, dtype)),
                    })
        powered_by_view[view_name] = view_powered
        view_rows.append({"view": view_name, "surfaces": surfaces})
    primary = powered_by_view["FULL_DEPOSITED_AFFIX"]
    robustness = all(powered_by_view[name] for name in (
        "DIRECT_ONLY", "STRICT_NO_FUNCTION", "STRICT_LITERAL", "TOP20_DELETED"))
    mandatory = primary and robustness
    conditional = [{"view": name, "status": "POWERED" if powered_by_view[name] else "INSUFFICIENT"}
                   for name in ("SOURCE_PRESENT", "LEAVE_ASTRO_OUT", "LEAVE_BOTANICAL_OUT",
                                "LEAVE_FUNCTION_OUT", "LEAVE_GENERAL_OUT", "LEAVE_MEDICAL_OUT",
                                "LEAVE_PHARMA_OUT")]
    aggregate_digest = digest(canonical({
        "schema": "dani001-actual-nonidentity-vector-digest-v1", "entries": digest_entries}))
    implementation_invariant_digest = digest(canonical({
        "schema": "dani001-actual-implementation-invariants-v1",
        "rank_start": 1, "rank_stop": 3628800,
        "affix": affix_invariant_entries,
        "unreachable": unreachable_invariant_entries,
        "affix_pass": affix_invariant_pass,
        "unreachable_pass": unreachable_invariant_pass,
    }))
    output = {
        "panel_counts": actual_panel_counts(tokens),
        "lexicon_counts": actual_lexicon_counts(projected), "views": view_rows,
        "mandatory_capacity_pass": mandatory,
        "conditional_view_statuses": conditional,
        "actual_nonidentity_vector_digest_sha256": aggregate_digest,
        "implementation_invariant_digest_sha256": implementation_invariant_digest,
    }
    if not primary:
        decision = "STOP_UNPOWERED_BEFORE_RELEASED_MAP_SCORE"
    elif not robustness:
        decision = "STOP_MANDATORY_ROBUSTNESS_CAPACITY_BEFORE_RELEASED_MAP_SCORE"
    else:
        decision = "PASS_TARGET_BLIND_CALIBRATION_AND_CAPACITY_IDENTITY_UNOPENED"
    return output, decision, rank_audit


class ExactRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request: urllib.request.Request, fp: object, code: int,
                         msg: str, headers: object, newurl: str) -> urllib.request.Request | None:
        if newurl not in EXTERNAL_URLS:
            raise ValidationStop("external redirect outside registered endpoint set")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def fetch_external(url: str) -> bytes:
    if url not in EXTERNAL_URLS:
        raise ValidationStop("unregistered external URL")
    opener = urllib.request.build_opener(ExactRedirect(), urllib.request.HTTPSHandler(context=SSL_CONTEXT))
    request = urllib.request.Request(url, headers={"User-Agent": "DANI001-clean-validator/1"})
    try:
        with opener.open(request, timeout=120) as response:
            if response.status != 200 or response.geturl() not in EXTERNAL_URLS:
                raise ValidationStop("external HTTP status/final URL")
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise ValidationStop("external acquisition failed") from error


def write_fsynced(path: Path, body: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def actual_capacity_from_registered_sources(freeze: Mapping[str, object],
                                            producer: Mapping[str, object],
                                            policy: AuditPolicy) -> tuple[dict[str, object], str, ActualRankAudit]:
    policy.network_enabled = True
    try:
        concept = fetch_external(EXTERNAL_URLS[0])
        pipeline = fetch_external(EXTERNAL_URLS[1])
        lexicon_body = fetch_external(EXTERNAL_URLS[2])
    finally:
        policy.network_enabled = False
    if digest(pipeline) != "079b6de7b8d2082303a0789fb3904105aecaa491e35600a557090e7981255d6f":
        raise ValidationStop("external pipeline body hash drift")
    if digest(lexicon_body) != "348992fa2bf555f1454a5a5485dd1ca9842acc143059f257f2fcdcf237821589":
        raise ValidationStop("external lexicon body hash drift")
    projection = stable_metadata_projection(concept)
    concept = b""
    acquisition = Path(tempfile.mkdtemp(prefix="dani001-validator-acquisition-", dir="/tmp")).resolve()
    policy.temporary_roots.add(acquisition)
    paths = {
        "pipeline": acquisition / "pipeline.py.txt",
        "lexicon": acquisition / "lexicon.json",
        "projection": acquisition / "stable_metadata_projection.json",
    }
    try:
        write_fsynced(paths["pipeline"], pipeline)
        write_fsynced(paths["lexicon"], lexicon_body)
        write_fsynced(paths["projection"], projection)
        directory = os.open(acquisition, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        inventory = tuple(sorted(acquisition.iterdir(), key=lambda value: value.name.encode()))
        if tuple(value.name for value in inventory) != (
                "lexicon.json", "pipeline.py.txt", "stable_metadata_projection.json") or any(
                    not value.is_file() or value.is_symlink() for value in inventory):
            raise ValidationStop("external acquisition inventory drift")
        if hash_file(paths["pipeline"])[0] != digest(pipeline) or hash_file(paths["lexicon"])[0] != digest(lexicon_body):
            raise ValidationStop("retained external body drift")
        if paths["projection"].read_bytes() != projection:
            raise ValidationStop("retained stable projection drift")
        projected = project_lexicon(paths["lexicon"].read_bytes())
        local = freeze.get("local_inputs")
        if not isinstance(local, list) or len(local) != 5:
            raise ValidationStop("freeze local input array drift")
        local_records = [path_object(value, "freeze local input") for value in local]
        expected_local_order = [*SOURCE_REL.values(), ATLAS_REL, ATLAS_VALIDATION_REL]
        if [str(value["path"]) for value in local_records] != expected_local_order:
            raise ValidationStop("freeze local input membership drift")
        local_by_path = {str(value["path"]): value for value in local_records}
        if any(record["sha256"] != LOCAL_SHA[relative]
               for relative, record in local_by_path.items()):
            raise ValidationStop("freeze local input registered hash drift")
        policy.reads.update(repo_path(value) for value in local_by_path)
        for relative, record in local_by_path.items():
            verify_bound_path(record, relative, f"actual local input {relative}")
        source_bodies = {edition: repo_path(SOURCE_REL[edition]).read_bytes() for edition in EDITIONS}
        atlas_bytes, rows = reconstruct_atlas(source_bodies)
        if atlas_bytes != repo_path(ATLAS_REL).read_bytes():
            raise ValidationStop("stored atlas differs from independent reconstruction")
        tokens = actual_panel_tokens(rows)
        capacity, decision, rank_audit = actual_capacity(tokens, projected)
        exact_json_equal(producer["actual_capacity"], capacity,
                         "producer actual-capacity reconstruction")
        exact_json_equal(producer["decision"], decision,
                         "producer actual-capacity decision")
        exact_json_equal(producer["identity_access"], rank_audit.public(opened=True),
                         "producer actual identity counters")
        if producer["input_checks"]["local_inputs_pass"] is not True:
            raise ValidationStop("producer did not validate actual local inputs")
        if producer["isolation"]["post_synthetic_lexicon_projection_call_count"] != 1:
            raise ValidationStop("producer lexicon projection-call count drift")
        return capacity, decision, rank_audit
    finally:
        pipeline = b""
        lexicon_body = b""
        projection = b""
        for path in paths.values():
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass
        try:
            os.rmdir(acquisition)
        except FileNotFoundError:
            pass
        policy.temporary_roots.discard(acquisition)


def install_pair(policy: AuditPolicy, result_bytes: bytes, report_bytes: bytes) -> None:
    output_paths = (repo_path(VALIDATION_RESULT_REL), repo_path(VALIDATION_REPORT_REL))
    for path in output_paths:
        if os.path.lexists(path):
            raise ValidationStop("validation output collision")
    stage_root = Path(tempfile.mkdtemp(prefix="dani001-validator-stage-", dir="/tmp")).resolve()
    policy.temporary_roots.add(stage_root)
    linked: list[tuple[Path, Path, bytes]] = []
    try:
        staged: list[Path] = []
        for name, body in (("result.json", result_bytes), ("report.md", report_bytes)):
            path = stage_root / name
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(descriptor, "wb", closefd=True) as handle:
                    handle.write(body)
                    handle.flush()
                    os.fsync(handle.fileno())
            except BaseException:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
                raise
            staged.append(path)
        directory = os.open(stage_root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        for source, target, body in zip(staged, output_paths, (result_bytes, report_bytes), strict=True):
            os.link(source, target)
            linked.append((target, source, body))
        repository_directory = os.open(RESULTS, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(repository_directory)
        finally:
            os.close(repository_directory)
        if policy.violations or any(path.stat().st_size != len(body)
                                    for path, body in zip(output_paths, (result_bytes, report_bytes), strict=True)):
            raise ValidationStop("post-link audit failure")
        for source, target, body in zip(staged, output_paths,
                                        (result_bytes, report_bytes), strict=True):
            source_stat = source.stat()
            target_stat = target.stat()
            expected_sha = digest(body)
            if ((source_stat.st_dev, source_stat.st_ino, source_stat.st_size) !=
                    (target_stat.st_dev, target_stat.st_ino, len(body)) or
                    hash_file(source) != (expected_sha, len(body)) or
                    hash_file(target) != (expected_sha, len(body))):
                raise ValidationStop("post-link SHA/inode/size proof failure")
    except BaseException:
        for path, source, body in reversed(linked):
            try:
                path_stat = path.stat()
                source_stat = source.stat()
                if ((path_stat.st_dev, path_stat.st_ino, path_stat.st_size) ==
                    (source_stat.st_dev, source_stat.st_ino, len(body)) and
                        hash_file(source)[0] == digest(body)):
                    os.unlink(path)
            except FileNotFoundError:
                pass
        raise
    finally:
        for name in ("result.json", "report.md"):
            try:
                os.unlink(stage_root / name)
            except FileNotFoundError:
                pass
        try:
            os.rmdir(stage_root)
        except FileNotFoundError:
            pass
        policy.temporary_roots.discard(stage_root)


def validation_markdown(result: Mapping[str, object]) -> bytes:
    return (
        "# DANI001 target-blind calibration validation\n\n"
        "- Status: `PASS`\n"
        f"- Checks: `{result['checks_passed']}/{result['checks_total']}`\n"
        "- Reconstructed synthetic worlds: `238`\n"
        "- Real rank-0 evaluations: `0`\n"
        "- Real rank-0 inferences: `0`\n"
        f"- Producer decision: `{result['decision']}`\n"
        f"- Producer result SHA-256: `{result['producer_result_sha256']}`\n"
        "- Independent implementation: `true`\n"
    ).encode("utf-8")


def run_registered(expected_freeze_sha: str) -> None:
    policy = AuditPolicy()
    sys.addaudithook(policy.hook)
    freeze, manifest_bytes, _, _ = load_contract(expected_freeze_sha, policy)
    stored_manifest = strict_json(manifest_bytes)
    reconstructed_manifest, worlds = reconstruct_manifest()
    if not isinstance(stored_manifest, dict) or canonical(stored_manifest) != manifest_bytes:
        raise ValidationStop("stored synthetic manifest is not canonical")
    if canonical(reconstructed_manifest) != manifest_bytes:
        raise ValidationStop("independent synthetic manifest reconstruction mismatch")
    producer_result_bytes = repo_path(PRODUCER_RESULT_REL).read_bytes()
    producer_report_bytes = repo_path(PRODUCER_REPORT_REL).read_bytes()
    producer_result = strict_json(producer_result_bytes)
    synthetic = run_synthetic(reconstructed_manifest, worlds)
    result = validate_common_producer(producer_result, producer_result_bytes,
                                      producer_report_bytes, freeze,
                                      expected_freeze_sha, synthetic)
    validator_rank_audit = ActualRankAudit()
    actual_opened = False
    if not synthetic.gate:
        validate_synthetic_failure(result, synthetic)
    else:
        if result["decision"] == "STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED":
            raise ValidationStop("producer/validator synthetic-pass disagreement")
        capacity, _, validator_rank_audit = actual_capacity_from_registered_sources(
            freeze, result, policy)
        actual_opened = True
        synthetic.reconstructed["capacity_view_count"] = 12
        synthetic.reconstructed["vector_component_count"] = int(
            synthetic.reconstructed["vector_component_count"]) + 216
        synthetic.reconstructed["actual_nonidentity_vector_digest_sha256"] = capacity[
            "actual_nonidentity_vector_digest_sha256"]
    checks_total = 737 + 16
    validation = {
        "schema": SCHEMA_VALIDATION, "experiment": "DANI001", "status": "PASS",
        "independent": True, "imported_producer": False, "executed_producer": False,
        "registered_science_sha256": SCIENCE_SHA,
        "calibration_spec_sha256": CALIBRATION_SHA,
        "calibration_freeze_sha256": expected_freeze_sha,
        "synthetic_manifest_sha256": MANIFEST_SHA,
        "producer_result_sha256": digest(producer_result_bytes),
        "producer_report_sha256": digest(producer_report_bytes),
        "checks_total": checks_total, "checks_passed": checks_total, "checks_failed": 0,
        "reconstructed": synthetic.reconstructed,
        "identity_access": {name: validator_rank_audit.public(opened=actual_opened)[name]
                            for name in IDENTITY_KEYS[:5]},
        "decision": result["decision"],
    }
    validation_bytes = canonical(validation)
    report_bytes = validation_markdown(validation)
    install_pair(policy, validation_bytes, report_bytes)


def self_test() -> None:
    if (len(COMPILER_VERSION) != 266 or
            digest(COMPILER_VERSION) !=
            "f5d8ad262fbd6d79034794c9156b9f005633b17b3a171eb379a1604c8ec6c7be" or
            not COMPILER_VERSION.endswith(b"PURPOSE.\n\n") or
            COMPILER_VERSION.endswith(b"\n\n\n")):
        raise ValidationStop("frozen compiler banner byte guard")
    for width in (4, 6):
        for rank in (0, 1, math.factorial(width) // 2, math.factorial(width) - 1):
            if rank_perm(unrank_perm(width, rank)) != rank:
                raise ValidationStop("fabricated Lehmer self-test")
    if counter_hash("toy-map-rank", 4, 7) != counter_hash("toy-map-rank", 4, 7):
        raise ValidationStop("counter determinism self-test")
    try:
        strict_json(b'{"a":1,"a":2}\n')
        raise ValidationStop("duplicate-key self-test did not stop")
    except ValidationStop as error:
        if str(error) == "duplicate-key self-test did not stop":
            raise
    for nonfinite in (b'NaN\n', b'Infinity\n', b'-Infinity\n'):
        try:
            strict_json(nonfinite)
            raise ValidationStop("nonfinite JSON self-test did not stop")
        except ValidationStop as error:
            if str(error) == "nonfinite JSON self-test did not stop":
                raise
    try:
        exact_json_equal({"typed": True}, {"typed": 1}, "fabricated typed JSON")
        raise ValidationStop("bool/int JSON self-test did not stop")
    except ValidationStop as error:
        if str(error) == "bool/int JSON self-test did not stop":
            raise
    groups, boundaries = split_source_text("  kd,<note>rs.<%>ln<$> ")
    if groups != ("kd", "<note>rs", "ln") or boundaries != (
            "UNCERTAIN_SMALL_SPACE", "DEFINITE_SPACE"):
        raise ValidationStop("fabricated source splitter self-test")
    width = 4
    permutation = (1, 0, 3, 2)
    raw_groups = tuple(ordinary_prefix(index)[0] + input_tail(tuple(range(width)))
                       for index in range(8))
    rows = tuple(Row(edition, f"f{folio}r", f"P.{folio}", raw_groups,
                     (".",) * (len(raw_groups) - 1))
                 for edition in EDITIONS for folio in range(1, 3))
    try:
        ordered_rows(tuple(row for row in rows if row.edition != "RF1b"))
        raise ValidationStop("missing-edition self-test did not stop")
    except ValidationStop as error:
        if str(error) == "missing-edition self-test did not stop":
            raise
    keys = tuple(ordinary_prefix(index)[1] + output_tail(permutation, tuple(range(width)), width)
                 for index in range(8))
    records = lexicon(keys, width)
    fabricated_world = World(
        "FABRICATED_ONLY", "TOY", 0, width, rank_perm(permutation),
        rank_perm(permutation), None, (), rows, records, {})
    expanded_views = build_world_views(fabricated_world)
    literal_views, literal_function, expanded_function = build_literal_world_views(
        fabricated_world)
    if (literal_function != expanded_function or
            not all_world_views_equal(expanded_views, literal_views,
                                      fabricated_world.candidate)):
        raise ValidationStop("fabricated decision-function path self-test")
    streamed = evaluate_world(fabricated_world)
    if (not streamed.affix_equivalence or
            not HEX64.fullmatch(streamed.affix_evidence_sha256)):
        raise ValidationStop("fabricated streaming-world self-test")
    fake10_groups = base_groups(10)[:4]
    fake10_rows = uniform_rows(fake10_groups)
    fake10_keys = tuple(
        ordinary_prefix(index)[1] + output_tail(tuple(range(10)), six_tail(index))
        for index in range(4))
    fake10 = World("FABRICATED_WIDTH10", "TOY", 0, 10, 1, 1, None, (),
                   fake10_rows, lexicon(fake10_keys, 10), {})
    estimate = world_memory_preflight(fake10, world_tokens(fake10.rows))
    if not 0 < estimate <= WIDTH10_PROCESS_MEMORY_BOUND:
        raise ValidationStop("fabricated width-10 memory-bound self-test")
    liveness = LiveStateBudget()
    liveness.acquire()
    liveness.acquire()
    try:
        liveness.acquire()
        raise ValidationStop("liveness overflow self-test did not stop")
    except ValidationStop as error:
        if str(error) == "liveness overflow self-test did not stop":
            raise
    liveness.live = MAX_LIVE_VECTOR_STATES
    liveness.release()
    liveness.release()
    tokens = world_tokens(rows)[SURFACE_ORDER[0]]
    fast = surface_vectors(tokens, records, width, deposited=True)
    nonidentity = surface_vectors(tokens, records, width, deposited=True, rank_start=1)
    scalar = scalar_surface_vectors(tokens, records, width, deposited=True)
    if any(little_bytes(left, kind) != little_bytes(right, kind) for left, right, kind in (
            (fast.token, scalar.token, "<u4"), (fast.type, scalar.type, "<u4"),
            (fast.folio, scalar.folio, "<f8"))):
        raise ValidationStop("fabricated scalar/constraint self-test")
    if (little_bytes(nonidentity.token, "<u4") != little_bytes(array("I", scalar.token[1:]), "<u4") or
            little_bytes(nonidentity.type, "<u4") != little_bytes(array("I", scalar.type[1:]), "<u4") or
            little_bytes(nonidentity.folio, "<f8") != little_bytes(array("d", scalar.folio[1:]), "<f8")):
        raise ValidationStop("fabricated nonidentity interval self-test")
    fast_view = ViewVectors("FULL_DEPOSITED_AFFIX", {name: fast for name in SURFACE_ORDER})
    scalar_view = ViewVectors("FULL_DEPOSITED_AFFIX", {name: scalar for name in SURFACE_ORDER})
    if view_fingerprint(fast_view, rank_perm(permutation), 1, 1,
                        concentration=True) != view_fingerprint(
                            scalar_view, rank_perm(permutation), 1, 1, concentration=True):
        raise ValidationStop("fabricated full-distribution fingerprint self-test")
    unconstrained = (0, tuple([255] * width))
    bounded_ranks = tuple(completion_ranks(unconstrained, width, rank_start=1))
    if len(bounded_ranks) != math.factorial(width) - 1 or not bounded_ranks or min(bounded_ranks) != 1:
        raise ValidationStop("fabricated lower-bounded completion self-test")
    table, _ = constraint_weight_table(tokens, records, width, deposited=True)
    one = partitioned_constraint_vectors(width, table, 1)
    thirty_two = partitioned_constraint_vectors(width, table, 32)
    if any(little_bytes(left, "<u4") != little_bytes(right, "<u4")
           for left, right in zip(one, thirty_two, strict=True)):
        raise ValidationStop("fabricated disjoint-rank worker self-test")
    binary_equal, binary_digest = binary_match_equivalence(tokens, records, width, rank_start=1)
    if not binary_equal or not HEX64.fullmatch(binary_digest):
        raise ValidationStop("fabricated literal-binary self-test")
    audit = ActualRankAudit()
    constrained = compatible_constraint(tuple(-index - 1 for index in range(width)),
                                        (NIBBLE["d"], NIBBLE["k"],
                                         NIBBLE["r"], NIBBLE["s"]), width)
    if constrained is None:
        raise ValidationStop("fabricated constraint compiler setup")
    bounded = tuple(completion_ranks(constrained, width, rank_start=1, audit=audit))
    expected = tuple(rank for rank in completion_ranks(constrained, width) if rank >= 1)
    if (bounded != expected or audit.compiler_nonidentity_leaves != len(bounded) or
            any(getattr(audit, name) for name in (
                "rank0_requests", "rank0_maps_evaluated", "rank0_match_calls",
                "rank0_values_stored", "rank0_values_inferred",
                "compiler_completed_rank0_leaves"))):
        raise ValidationStop("fabricated pruned nonidentity compiler self-test")
    for _ in range(72):
        audit.record_vector_surface(1, 3628800, 3628799, "primary")
    for _ in range(18):
        audit.record_vector_surface(1, 3628800, 3628799, "evidence")
    public_audit = audit.public(opened=True)
    if (public_audit["actual_logical_map_view_evaluations"] != 326591910 or
            public_audit["actual_primary_logical_view_surfaces"] != 72 or
            public_audit["actual_evidence_logical_view_surfaces"] != 18):
        raise ValidationStop("fabricated actual-rank audit self-test")
    exact_json_equal(public_audit, expected_identity_access(True),
                     "fabricated expanded identity schema")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-sha256", help="expected calibration-freeze SHA-256")
    parser.add_argument("--self-test", action="store_true",
                        help="run fabricated 4!/6! tests without repository reads")
    values = parser.parse_args(argv)
    if values.self_test == bool(values.freeze_sha256):
        parser.error("choose exactly one of --self-test or --freeze-sha256")
    return values


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.self_test:
            self_test()
            print("DANI001 clean validator fabricated self-test: PASS")
        else:
            run_registered(args.freeze_sha256)
            print("DANI001 clean validator: PASS")
    except ValidationStop as error:
        print(f"DANI001 clean validator output-free stop: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
