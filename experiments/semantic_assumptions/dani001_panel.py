#!/usr/bin/env python3
"""Source-native input construction for the registered DANI001 diagnostic.

This module is deliberately limited to input acquisition and compilation.  It
does not enumerate a mapping, evaluate permutation rank 0, calculate coverage,
or write a panel/result artifact.  Returned source surfaces and lexicon keys are
private in-memory inputs for the later frozen calibration and target runners.

The implementation imports neither the deposited pipeline nor any VManus
formal parser.  It reconstructs the source-separator atlas directly from the
three frozen human IVTFF files and uses the deposited Python file as hash-bound
inert evidence only.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import struct
import tempfile
import urllib.error
import urllib.request
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Iterator, Mapping, Sequence


MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parents[1]
RESULTS_DIR = MODULE_DIR / "results"
SPEC_PATH = MODULE_DIR / "DANI001_FIXED_MAPPING_DIAGNOSTIC_SPEC.md"
ATLAS_PATH = RESULTS_DIR / "source_separator_transcription.tsv"
ATLAS_VALIDATION_PATH = RESULTS_DIR / "source_separator_transcription_validation.json"

REGISTERED_SPEC_COMMIT = "1faa87fc33ffdd35b92d1f2f6c69e90e68aeebe4"
REGISTERED_SPEC_SHA256 = "cc73479b3c35eaa87a3f56184fc3472fe6232b67c13deb3bf30ef8555a6c8426"
ATLAS_SHA256 = "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0"
ATLAS_VALIDATION_SHA256 = "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb"

EDITION_ORDER = ("ZL3b", "IT2a", "RF1b")
PANEL_ORDER = ("DOT_ONLY_EMULATION", "MANUAL_GROUP")
SOURCE_RELATIVE_PATHS = MappingProxyType({
    "ZL3b": Path("transcription/sources/ZL3b-n.txt"),
    "IT2a": Path("transcription/sources/IT2a-n.txt"),
    "RF1b": Path("transcription/sources/RF1b-e.txt"),
})
SOURCE_SHA256 = MappingProxyType({
    "ZL3b": "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "IT2a": "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    "RF1b": "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
})

CONCEPT_URL = "https://zenodo.org/api/records/19583305"
CONCEPT_REDIRECT_LOCATION = "/api/records/19609475"
CONCEPT_RESOLVED_URL = "https://zenodo.org/api/records/19609475"
PIPELINE_URL = "https://zenodo.org/api/records/19609475/files/pipeline_v31_1.py/content"
LEXICON_URL = (
    "https://zenodo.org/api/records/19609475/files/"
    "lexicon_v31_session31_final.json/content"
)
EXTERNAL_URLS = (CONCEPT_URL, PIPELINE_URL, LEXICON_URL)
ACQUISITION_URLS = (
    CONCEPT_URL,
    CONCEPT_RESOLVED_URL,
    PIPELINE_URL,
    LEXICON_URL,
)
STABLE_PROJECTION_SHA256 = "780301fd3c4b2c3c328c1f69a1eab65d0b0600f2d491ea9578f81699d36ddfa7"
PIPELINE_SHA256 = "079b6de7b8d2082303a0789fb3904105aecaa491e35600a557090e7981255d6f"
LEXICON_SHA256 = "348992fa2bf555f1454a5a5485dd1ca9842acc143059f257f2fcdcf237821589"

CORE_INPUTS = ("k", "d", "r", "s", "l", "n", "q", "y", "m", "g")
CORE_OUTPUTS = ("k", "d", "r", "s", "l", "n", "w", "y", "m", "g")
NIBBLE_SYMBOLS = ("k", "d", "r", "s", "l", "n", "w", "y", "m", "g", "š", "ṭ", "p", "ṣ")
NIBBLE_CODE = MappingProxyType({symbol: index for index, symbol in enumerate(NIBBLE_SYMBOLS, 1)})
NIBBLE_DECODE = MappingProxyType({index: symbol for symbol, index in NIBBLE_CODE.items()})
CORE_OUTPUT_CODES = tuple(NIBBLE_CODE[symbol] for symbol in CORE_OUTPUTS)

GALLOWS_PREFIXES = ("ṭ", "p", "ṣ")
STANDARD_PREFIXES = ("d", "l", "w")
DOMAINS = ("astro", "botanical", "function", "general", "medical", "pharma")

SEPARATOR_NAMES = MappingProxyType({
    ".": "DEFINITE_SPACE",
    ",": "UNCERTAIN_SMALL_SPACE",
    "<->": "DRAWING_INTERRUPTION",
    "<~>": "DRAWING_INTERRUPTION_UNALIGNED",
})
ATLAS_FIELDS = (
    "source_group_id", "edition", "locus", "page", "section", "currier",
    "hand", "code", "kind", "grammar_scope", "source_row_index",
    "source_group_index", "source_group_count", "paragraph_start",
    "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw",
    "clean_ascii_fragments", "clean_ascii_fragment_count",
    "legacy_surface_positions_1based", "legacy_interlinear_row_present",
    "legacy_mapping_status",
)

PAGE_HEADER_RE = re.compile(r"^<([^>.]+)>\s+<!(.*)>")
LOCUS_RE = re.compile(r"^<([^,]+),([^>]*)>\s*(?:<!([^>]*)>)?\s*(.*)$")
META_RE = re.compile(r"\$([A-Z])=([^\s>]+)")
ADMITTED_PAGE_RE = re.compile(r"^f([0-9]+)[rv][0-9]*$")
LEGACY_SQUARE_RE = re.compile(r"\[([^:\]]+)(?::[^\]]*)?\]")
LEGACY_BRACE_RE = re.compile(r"\{[^}]*\}")
LEGACY_ANGLE_RE = re.compile(r"<[^>]*>")
LEGACY_SPLIT_RE = re.compile(r"[\s.,;:=/\\|+\-]+")

# A negative element is a core-variable placeholder -(core_index + 1).
# A positive element is a fixed nibble code.
ATOM_EMISSIONS: Mapping[str, tuple[int, ...]] = MappingProxyType({
    "cth": (NIBBLE_CODE["ṭ"], NIBBLE_CODE["k"]),
    "ckh": (NIBBLE_CODE["k"], NIBBLE_CODE["k"]),
    "cph": (NIBBLE_CODE["p"], NIBBLE_CODE["k"]),
    "cfh": (NIBBLE_CODE["p"], NIBBLE_CODE["k"]),
    "sh": (NIBBLE_CODE["š"],),
    "ch": (NIBBLE_CODE["k"],),
    **{symbol: (-(index + 1),) for index, symbol in enumerate(CORE_INPUTS)},
    "t": (NIBBLE_CODE["ṭ"],),
    "p": (NIBBLE_CODE["p"],),
    "f": (NIBBLE_CODE["ṣ"],),
    "a": (),
    "o": (),
    "e": (),
    "i": (),
    "x": (),
    "h": (),
})
ATOM_LENGTHS = (3, 2, 1)

REGISTERED_COUNTS = MappingProxyType({
    "source_rows": 15_985,
    "source_groups": 115_470,
    "manual_boundaries": 99_485,
    "retained_source_rows": 15_665,
    "retained_source_groups": 114_387,
    "excluded_fros_rows": 320,
    "excluded_fros_groups": 1_083,
    "excluded_fros_loci": 160,
    "strict_unconsumed_length_eligible_manual_groups": 280,
})


class DANI001InputError(RuntimeError):
    """A frozen input, parser, topology, or isolation contract failed."""


@dataclass(frozen=True, slots=True)
class PanelToken:
    """One private normalized panel token; no mapping has been evaluated."""

    folio: int = field(repr=False)
    normalized_eva: str = field(repr=False)
    emitted_template: tuple[int, ...] = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.folio, int) or self.folio < 1:
            raise DANI001InputError("panel token has invalid physical folio")
        if (
            len(self.normalized_eva) < 2
            or any(not ("a" <= value <= "z") for value in self.normalized_eva)
        ):
            raise DANI001InputError("panel token has invalid normalized EVA")
        if not self.emitted_template:
            raise DANI001InputError("panel token has empty emitted template")
        for value in self.emitted_template:
            if not (-len(CORE_INPUTS) <= value <= len(NIBBLE_SYMBOLS)) or value == 0:
                raise DANI001InputError("panel token has invalid emitted element")

    @property
    def output_length(self) -> int:
        return len(self.emitted_template)


@dataclass(frozen=True, slots=True)
class Panel:
    edition: str
    name: str
    tokens: tuple[PanelToken, ...] = field(repr=False)
    strict_literal_mask: bytes = field(repr=False)
    digest: str

    def __post_init__(self) -> None:
        if len(self.tokens) != len(self.strict_literal_mask):
            raise DANI001InputError("panel token/mask length mismatch")
        if any(value not in (0, 1) for value in self.strict_literal_mask):
            raise DANI001InputError("nonbinary strict-literal mask")

    @property
    def token_count(self) -> int:
        return len(self.tokens)

    @property
    def strict_token_count(self) -> int:
        return sum(self.strict_literal_mask)

    @property
    def type_count(self) -> int:
        return len({token.normalized_eva for token in self.tokens})

    @property
    def folio_count(self) -> int:
        return len({token.folio for token in self.tokens})


@dataclass(frozen=True, slots=True)
class SourceCounts:
    source_rows: int
    source_groups: int
    manual_boundaries: int
    retained_source_rows: int
    retained_source_groups: int
    excluded_fros_rows: int
    excluded_fros_groups: int
    excluded_fros_loci: int
    strict_unconsumed_length_eligible_manual_groups: int
    separator_counts: tuple[tuple[str, int], ...]
    panel_counts: tuple[tuple[str, str, int, int, int, int], ...]


@dataclass(frozen=True, slots=True)
class SourcePanelBundle:
    panels: tuple[Panel, ...] = field(repr=False)
    counts: SourceCounts
    source_hashes: tuple[tuple[str, str], ...]
    atlas_sha256: str
    atlas_validation_sha256: str
    bundle_digest: str

    def panel(self, edition: str, name: str) -> Panel:
        for panel in self.panels:
            if panel.edition == edition and panel.name == name:
                return panel
        raise KeyError((edition, name))


@dataclass(frozen=True, slots=True)
class LexiconView:
    """One key-set view with unreachable strings removed before encoding."""

    name: str
    total_key_count: int
    reachable_key_count: int
    reachable_keys: frozenset[str] = field(repr=False)
    direct_codes: tuple[int, ...] = field(repr=False)
    deposited_affix_codes: tuple[int, ...] = field(repr=False)

    def __post_init__(self) -> None:
        for values in (self.direct_codes, self.deposited_affix_codes):
            if not isinstance(values, tuple) or values != tuple(sorted(set(values))):
                raise DANI001InputError(
                    "core-facing lexicon codes must be sorted unique tuples"
                )


@dataclass(frozen=True, slots=True)
class LexiconCounts:
    keys: int
    entries: int
    reachable_keys: int
    unreachable_keys: int
    source_present_keys: int
    source_present_reachable_keys: int
    strict_no_function_keys: int
    strict_no_function_reachable_keys: int
    view_counts: tuple[tuple[str, int, int, int, int], ...]


@dataclass(frozen=True, slots=True)
class LexiconBundle:
    views: tuple[LexiconView, ...] = field(repr=False)
    counts: LexiconCounts
    restored_view: LexiconView = field(repr=False)

    def view(self, name: str) -> LexiconView:
        for view in self.views:
            if view.name == name:
                return view
        raise KeyError(name)

    def restored(self) -> LexiconView:
        """Return the private remove-then-add restoration control view."""

        return self.restored_view


@dataclass(frozen=True, slots=True)
class ExternalInputBundle:
    stable_projection_bytes: bytes = field(repr=False)
    stable_projection_sha256: str
    pipeline_sha256: str
    lexicon_sha256: str
    lexicon: LexiconBundle
    acquisition_urls: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RegisteredExternalAcquisition:
    """Active, unparsed external-input lease for the calibration gate."""

    stable_projection_bytes: bytes = field(repr=False)
    stable_projection_sha256: str
    pipeline_sha256: str
    lexicon_sha256: str
    acquisition_urls: tuple[str, ...]
    temporary_root: Path = field(repr=False)
    pipeline_path: Path = field(repr=False)
    lexicon_path: Path = field(repr=False)
    stable_projection_path: Path = field(repr=False)
    _projection_calls: list[int] = field(
        default_factory=lambda: [0], repr=False, compare=False
    )


@dataclass(frozen=True, slots=True)
class DANI001InputBundle:
    external: ExternalInputBundle
    source: SourcePanelBundle


@dataclass(frozen=True, slots=True)
class _ScanResult:
    normalized_eva: str = field(repr=False)
    emitted_template: tuple[int, ...] = field(repr=False)
    consumed_all: bool = field(repr=False)
    had_ambiguity: bool = field(repr=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
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


def _reject_duplicate_object(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise DANI001InputError("duplicate JSON object key")
        output[key] = value
    return output


def _json_object(data: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            data.decode("utf-8", errors="strict"),
            object_pairs_hook=_reject_duplicate_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DANI001InputError("invalid UTF-8 JSON input") from error
    if not isinstance(value, dict):
        raise DANI001InputError("expected a JSON object")
    return value


def stable_metadata_projection(metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Return the registered immutable Zenodo projection."""

    try:
        meta = metadata["metadata"]
        files = metadata["files"]
        if not isinstance(meta, Mapping) or not isinstance(files, list):
            raise TypeError
        projection = {
            "id": metadata["id"],
            "conceptrecid": metadata["conceptrecid"],
            "revision": metadata["revision"],
            "doi": metadata["doi"],
            "created": metadata["created"],
            "updated": metadata["updated"],
            "metadata": {
                "title": meta["title"],
                "publication_date": meta["publication_date"],
                "description": meta["description"],
            },
            "files": [
                {
                    "key": item["key"],
                    "size": item["size"],
                    "checksum": item["checksum"],
                    "url": item["links"]["self"],
                }
                for item in files
            ],
        }
    except (KeyError, TypeError) as error:
        raise DANI001InputError("Zenodo metadata projection schema mismatch") from error
    return projection


def encode_skeleton(skeleton: str) -> int:
    """Encode one reachable output skeleton under the frozen nibble codebook."""

    if not isinstance(skeleton, str):
        raise DANI001InputError("skeleton must be a string")
    length = len(skeleton)
    if length > 10:
        raise DANI001InputError("accepted skeleton exceeds ten code points")
    value = length << 40
    for index, symbol in enumerate(skeleton):
        code = NIBBLE_CODE.get(symbol)
        if code is None:
            raise DANI001InputError("unreachable skeleton symbol")
        value |= code << (4 * index)
    if value < 0 or value > (1 << 64) - 1 or value >> 44:
        raise DANI001InputError("encoded skeleton overflow or reserved-bit use")
    return value


def decode_skeleton(value: int) -> str:
    """Decode and validate one frozen nibble value (used by source-free controls)."""

    if not isinstance(value, int) or value < 0 or value > (1 << 64) - 1:
        raise DANI001InputError("encoded skeleton is outside uint64")
    if value >> 44:
        raise DANI001InputError("encoded skeleton has nonzero reserved bits")
    length = (value >> 40) & 0xF
    if length > 10:
        raise DANI001InputError("encoded skeleton length exceeds ten")
    symbols: list[str] = []
    for index in range(10):
        code = (value >> (4 * index)) & 0xF
        if index < length:
            symbol = NIBBLE_DECODE.get(code)
            if symbol is None:
                raise DANI001InputError("padding or unknown nibble inside length")
            symbols.append(symbol)
        elif code:
            raise DANI001InputError("nonzero padding outside declared length")
    return "".join(symbols)


def split_source_groups(text: str) -> tuple[list[str], list[str]]:
    """Split one IVTFF locus into verbatim groups and its four separator states."""

    groups: list[str] = []
    boundaries: list[str] = []
    pending: list[str] = []
    current: list[str] = []
    cursor = 0

    def cut(marker: str) -> None:
        nonlocal current, pending
        group = "".join(current).strip()
        current = []
        if not group and not groups:
            raise DANI001InputError("leading or empty source group")
        if group:
            if groups:
                if len(pending) != 1:
                    raise DANI001InputError("empty group or compound source separator")
                boundaries.append(pending[0])
            groups.append(group)
            pending = []
        pending.append(marker)

    while cursor < len(text):
        if text.startswith("<->", cursor):
            cut("<->")
            cursor += 3
            continue
        if text.startswith("<~>", cursor):
            cut("<~>")
            cursor += 3
            continue
        character = text[cursor]
        if character == "<":
            end = text.find(">", cursor + 1)
            if end < 0:
                raise DANI001InputError("unterminated angle form")
            tag = text[cursor:end + 1]
            if tag not in {"<%>", "<$>"}:
                current.append(tag)
            cursor = end + 1
            continue
        if character in "[{":
            close = "]" if character == "[" else "}"
            end = text.find(close, cursor + 1)
            if end < 0:
                raise DANI001InputError("unterminated square or brace form")
            current.append(text[cursor:end + 1])
            cursor = end + 1
            continue
        if character in ".,":
            cut(character)
            cursor += 1
            continue
        current.append(character)
        cursor += 1

    group = "".join(current).strip()
    if group:
        if groups:
            if len(pending) != 1:
                raise DANI001InputError("empty group or compound source separator")
            boundaries.append(pending[0])
        groups.append(group)
        pending = []
    if pending or not groups or len(boundaries) != len(groups) - 1:
        raise DANI001InputError("invalid source-group topology")
    return groups, boundaries


def _legacy_clean(text: str) -> list[str]:
    selected = LEGACY_SQUARE_RE.sub(lambda match: match.group(1), text)
    selected = LEGACY_BRACE_RE.sub("", selected)
    selected = LEGACY_ANGLE_RE.sub(" ", selected)
    selected = selected.replace("?", "").replace("!", "").replace("*", "").replace("'", "")
    output: list[str] = []
    for part in LEGACY_SPLIT_RE.split(selected):
        letters = re.sub(r"[^A-Za-z]", "", part).lower()
        if letters:
            output.append(letters)
    return output


def normalize_source_text(text: str) -> tuple[str, bool]:
    """Select primary branches, delete annotations, and retain ASCII letters."""

    output: list[str] = []
    had_ambiguity = False
    cursor = 0
    delimiters = "[]{}<>"
    closing = {"]", "}", ">"}
    while cursor < len(text):
        character = text[cursor]
        if character == "[":
            end = text.find("]", cursor + 1)
            if end < 0:
                raise DANI001InputError("unmatched square delimiter")
            body = text[cursor + 1:end]
            if any(value in delimiters for value in body):
                raise DANI001InputError("nested square form")
            output.append(body.split(":", 1)[0])
            had_ambiguity = True
            cursor = end + 1
            continue
        if character == "{":
            end = text.find("}", cursor + 1)
            if end < 0:
                raise DANI001InputError("unmatched brace delimiter")
            body = text[cursor + 1:end]
            if any(value in delimiters for value in body):
                raise DANI001InputError("nested brace form")
            had_ambiguity = True
            cursor = end + 1
            continue
        if character == "<":
            end = text.find(">", cursor + 1)
            if end < 0:
                raise DANI001InputError("unmatched angle delimiter")
            body = text[cursor + 1:end]
            if any(value in delimiters for value in body):
                raise DANI001InputError("nested angle form")
            if text[cursor:end + 1] in {"<->", "<~>"}:
                raise DANI001InputError("separator reached annotation normalizer")
            cursor = end + 1
            continue
        if character in closing:
            raise DANI001InputError("unmatched closing delimiter")
        output.append(character)
        cursor += 1
    lowered = "".join(output).lower()
    return "".join(value for value in lowered if "a" <= value <= "z"), had_ambiguity


def scan_normalized_eva(normalized_eva: str) -> tuple[tuple[int, ...], bool]:
    """Compile EVA atoms to fixed nibbles/core placeholders without a mapping."""

    if not isinstance(normalized_eva, str) or any(not ("a" <= value <= "z") for value in normalized_eva):
        raise DANI001InputError("scanner input is not normalized ASCII EVA")
    emitted: list[int] = []
    consumed_all = True
    cursor = 0
    while cursor < len(normalized_eva):
        atom = None
        for length in ATOM_LENGTHS:
            candidate = normalized_eva[cursor:cursor + length]
            if len(candidate) == length and candidate in ATOM_EMISSIONS:
                atom = candidate
                break
        if atom is None:
            consumed_all = False
            cursor += 1
            continue
        emitted.extend(ATOM_EMISSIONS[atom])
        cursor += len(atom)
    return tuple(emitted), consumed_all


def _scan_source_text(text: str) -> _ScanResult:
    normalized, had_ambiguity = normalize_source_text(text)
    emitted, consumed_all = scan_normalized_eva(normalized)
    return _ScanResult(normalized, emitted, consumed_all, had_ambiguity)


def compile_source_token(raw_text: str, folio: int) -> tuple[PanelToken, bool] | None:
    """Compile one synthetic/source token without evaluating any core assignment."""

    scanned = _scan_source_text(raw_text)
    if len(scanned.normalized_eva) < 2 or not scanned.emitted_template:
        return None
    token = PanelToken(folio, scanned.normalized_eva, scanned.emitted_template)
    strict = scanned.consumed_all and not scanned.had_ambiguity
    return token, strict


def _dot_only_raw_tokens(groups: Sequence[str], boundaries: Sequence[str]) -> list[str]:
    if not groups or len(boundaries) != len(groups) - 1:
        raise DANI001InputError("cannot form dot-only tokens from invalid topology")
    output: list[str] = []
    current = groups[0]
    for boundary, group in zip(boundaries, groups[1:], strict=True):
        if boundary == ".":
            output.append(current)
            current = group
        else:
            current += group
    output.append(current)
    return output


def _panel_digest(edition: str, name: str, tokens: Sequence[PanelToken], mask: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(b"DANI001_PRIVATE_PANEL_V1\0")
    for label in (edition, name):
        encoded = label.encode("ascii")
        digest.update(struct.pack("<I", len(encoded)))
        digest.update(encoded)
    digest.update(struct.pack("<I", len(tokens)))
    for token, strict in zip(tokens, mask, strict=True):
        surface = token.normalized_eva.encode("ascii")
        digest.update(struct.pack("<II", token.folio, len(surface)))
        digest.update(surface)
        digest.update(struct.pack("<I", len(token.emitted_template)))
        digest.update(bytes(value & 0xFF for value in token.emitted_template))
        digest.update(bytes((strict,)))
    return digest.hexdigest()


def _expected_atlas_group(
    *,
    edition: str,
    locus: str,
    page: str,
    metadata: Mapping[str, str],
    code: str,
    row_index: int,
    text: str,
    groups: Sequence[str],
    boundaries: Sequence[str],
    fragments: Sequence[Sequence[str]],
    group_index: int,
) -> dict[str, str]:
    emitted = fragments[group_index - 1]
    position_before = sum(len(value) for value in fragments[:group_index - 1])
    positions = range(position_before + 1, position_before + len(emitted) + 1)
    flat_count = sum(len(value) for value in fragments)
    count = len(emitted)
    state = (
        "ZERO_ASCII_FRAGMENT"
        if count == 0
        else "ONE_ASCII_FRAGMENT"
        if count == 1
        else "MULTI_ASCII_FRAGMENT"
    )
    left = (
        "LINE_START"
        if group_index == 1
        else SEPARATOR_NAMES[boundaries[group_index - 2]]
    )
    right = (
        "LINE_END"
        if group_index == len(groups)
        else SEPARATOR_NAMES[boundaries[group_index - 1]]
    )
    scope = (
        "CONFIRMED_PROSE"
        if len(code) > 1 and code[1] == "P" and metadata.get("L", "") in {"A", "B"}
        else "DIAGNOSTIC_NONPROSE"
    )
    return {
        "source_group_id": f"{edition}|{locus}|G{group_index:03d}",
        "edition": edition,
        "locus": locus,
        "page": page,
        "section": metadata.get("I", ""),
        "currier": metadata.get("L", ""),
        "hand": metadata.get("H", ""),
        "code": code,
        "kind": code[1] if len(code) > 1 else "",
        "grammar_scope": scope,
        "source_row_index": str(row_index),
        "source_group_index": str(group_index),
        "source_group_count": str(len(groups)),
        "paragraph_start": str(int("<%>" in text)),
        "paragraph_end": str(int("<$>" in text)),
        "left_separator": left,
        "right_separator": right,
        "ivtff_group_raw": groups[group_index - 1],
        "clean_ascii_fragments": " ".join(emitted),
        "clean_ascii_fragment_count": str(count),
        "legacy_surface_positions_1based": ",".join(map(str, positions)),
        "legacy_interlinear_row_present": str(int(flat_count > 0)),
        "legacy_mapping_status": state,
    }


def _validate_registered_files(
    repo_root: Path,
) -> tuple[
    dict[str, Path],
    tuple[tuple[str, str], ...],
    Path,
    Path,
]:
    source_paths = {
        edition: repo_root / SOURCE_RELATIVE_PATHS[edition]
        for edition in EDITION_ORDER
    }
    module_dir = repo_root / "experiments" / "semantic_assumptions"
    spec_path = module_dir / SPEC_PATH.name
    atlas_path = module_dir / "results" / ATLAS_PATH.name
    atlas_validation_path = module_dir / "results" / ATLAS_VALIDATION_PATH.name
    observed = tuple((edition, sha256_path(source_paths[edition])) for edition in EDITION_ORDER)
    if dict(observed) != dict(SOURCE_SHA256):
        raise DANI001InputError("frozen human source hash drift")
    if sha256_path(spec_path) != REGISTERED_SPEC_SHA256:
        raise DANI001InputError("registered DANI001 specification hash drift")
    if sha256_path(atlas_path) != ATLAS_SHA256:
        raise DANI001InputError("source-separator atlas hash drift")
    if sha256_path(atlas_validation_path) != ATLAS_VALIDATION_SHA256:
        raise DANI001InputError("source-separator validation hash drift")
    return source_paths, observed, atlas_path, atlas_validation_path


def _assert_registered_lexicon_ready(lexicon: LexiconBundle) -> None:
    expected_names = {
        "FULL",
        "REACHABLE",
        "SOURCE_PRESENT",
        "STRICT_NO_FUNCTION",
        *(f"LEAVE_OUT_{domain.upper()}" for domain in DOMAINS),
    }
    if {view.name for view in lexicon.views} != expected_names:
        raise DANI001InputError("registered lexicon views are incomplete")
    if (
        lexicon.counts.keys != 1_389
        or lexicon.counts.entries != 1_441
        or lexicon.counts.reachable_keys != 819
        or lexicon.counts.unreachable_keys != 570
    ):
        raise DANI001InputError("registered lexicon/preimage bundle is not ready")
    full = lexicon.view("FULL")
    reachable = lexicon.view("REACHABLE")
    if (
        not full.deposited_affix_codes
        or full.direct_codes != reachable.direct_codes
        or full.deposited_affix_codes != reachable.deposited_affix_codes
    ):
        raise DANI001InputError("registered preimage invariant is not ready")


def load_registered_source_panels(
    lexicon: LexiconBundle,
    repo_root: Path = REPO_ROOT,
) -> SourcePanelBundle:
    """Reconstruct the frozen atlas and compile both source-native panels.

    The function reads manuscript source surfaces but performs no mapping or
    score evaluation and creates no file.
    """

    _assert_registered_lexicon_ready(lexicon)
    repo_root = repo_root.resolve()
    (
        source_paths,
        source_hashes,
        atlas_path,
        _atlas_validation_path,
    ) = _validate_registered_files(repo_root)
    token_lists: dict[tuple[str, str], list[PanelToken]] = {
        (edition, panel): [] for edition in EDITION_ORDER for panel in PANEL_ORDER
    }
    masks: dict[tuple[str, str], bytearray] = {
        key: bytearray() for key in token_lists
    }
    totals = Counter()
    separator_counts = Counter()
    excluded_editions: set[str] = set()
    excluded_loci: set[str] = set()
    seen_rows: set[tuple[str, str]] = set()
    reconstructed_atlas = io.StringIO(newline="")
    atlas_writer = csv.DictWriter(
        reconstructed_atlas,
        fieldnames=ATLAS_FIELDS,
        delimiter="\t",
        lineterminator="\n",
    )
    atlas_writer.writeheader()

    for edition in EDITION_ORDER:
        page = ""
        metadata: dict[str, str] = {}
        row_index = 0
        for raw_line in source_paths[edition].read_text(
            encoding="utf-8", errors="strict"
        ).splitlines():
            page_match = PAGE_HEADER_RE.match(raw_line)
            if page_match:
                page = page_match.group(1).lower()
                metadata = dict(META_RE.findall(page_match.group(2)))
                continue
            locus_match = LOCUS_RE.match(raw_line)
            if not locus_match:
                continue
            locus, code, _comment, text = locus_match.groups()
            key = (edition, locus)
            if key in seen_rows:
                raise DANI001InputError("duplicate edition/locus row")
            if not page:
                raise DANI001InputError("locus row before page metadata")
            seen_rows.add(key)
            row_index += 1
            totals["source_rows"] += 1
            groups, boundaries = split_source_groups(text)
            fragments = [_legacy_clean(group) for group in groups]
            scans = [_scan_source_text(group) for group in groups]
            totals["source_groups"] += len(groups)
            totals["manual_boundaries"] += len(boundaries)
            for boundary in boundaries:
                separator_counts[SEPARATOR_NAMES[boundary]] += 1

            for group_index in range(1, len(groups) + 1):
                expected = _expected_atlas_group(
                    edition=edition,
                    locus=locus,
                    page=page,
                    metadata=metadata,
                    code=code,
                    row_index=row_index,
                    text=text,
                    groups=groups,
                    boundaries=boundaries,
                    fragments=fragments,
                    group_index=group_index,
                )
                atlas_writer.writerow(expected)

            for scan in scans:
                if len(scan.normalized_eva) >= 2 and not scan.consumed_all:
                    totals["strict_unconsumed"] += 1

            page_match_admitted = ADMITTED_PAGE_RE.fullmatch(page)
            if page_match_admitted is None:
                if page != "fros":
                    raise DANI001InputError("unexpected nonnumeric page domain")
                totals["excluded_fros_rows"] += 1
                totals["excluded_fros_groups"] += len(groups)
                excluded_editions.add(edition)
                excluded_loci.add(locus)
                continue

            folio = int(page_match_admitted.group(1))
            totals["retained_source_rows"] += 1
            totals["retained_source_groups"] += len(groups)
            for scan in scans:
                if len(scan.normalized_eva) < 2 or not scan.emitted_template:
                    continue
                token_lists[(edition, "MANUAL_GROUP")].append(
                    PanelToken(folio, scan.normalized_eva, scan.emitted_template)
                )
                masks[(edition, "MANUAL_GROUP")].append(
                    int(scan.consumed_all and not scan.had_ambiguity)
                )
            for dot_raw in _dot_only_raw_tokens(groups, boundaries):
                scan = _scan_source_text(dot_raw)
                if len(scan.normalized_eva) < 2 or not scan.emitted_template:
                    continue
                token_lists[(edition, "DOT_ONLY_EMULATION")].append(
                    PanelToken(folio, scan.normalized_eva, scan.emitted_template)
                )
                masks[(edition, "DOT_ONLY_EMULATION")].append(
                    int(scan.consumed_all and not scan.had_ambiguity)
                )

    reconstructed_atlas_bytes = reconstructed_atlas.getvalue().encode("utf-8")
    if reconstructed_atlas_bytes != atlas_path.read_bytes():
        raise DANI001InputError(
            "stored atlas differs from canonical raw-source reconstruction"
        )

    observed_counts = {
        "source_rows": totals["source_rows"],
        "source_groups": totals["source_groups"],
        "manual_boundaries": totals["manual_boundaries"],
        "retained_source_rows": totals["retained_source_rows"],
        "retained_source_groups": totals["retained_source_groups"],
        "excluded_fros_rows": totals["excluded_fros_rows"],
        "excluded_fros_groups": totals["excluded_fros_groups"],
        "excluded_fros_loci": len(excluded_loci),
        "strict_unconsumed_length_eligible_manual_groups": totals["strict_unconsumed"],
    }
    if observed_counts != dict(REGISTERED_COUNTS):
        raise DANI001InputError("registered source/panel count drift")
    if excluded_editions != {"ZL3b", "RF1b"}:
        raise DANI001InputError("fRos edition scope drift")
    if set(separator_counts) != set(SEPARATOR_NAMES.values()):
        raise DANI001InputError("manual separator vocabulary drift")

    panels: list[Panel] = []
    panel_counts: list[tuple[str, str, int, int, int, int]] = []
    bundle_digest = hashlib.sha256()
    bundle_digest.update(b"DANI001_PRIVATE_PANEL_BUNDLE_V1\0")
    for edition in EDITION_ORDER:
        for panel_name in PANEL_ORDER:
            key = (edition, panel_name)
            tokens = tuple(token_lists[key])
            strict_mask = bytes(masks[key])
            digest = _panel_digest(edition, panel_name, tokens, strict_mask)
            panel = Panel(edition, panel_name, tokens, strict_mask, digest)
            panels.append(panel)
            panel_counts.append((
                edition,
                panel_name,
                panel.token_count,
                panel.strict_token_count,
                panel.type_count,
                panel.folio_count,
            ))
            bundle_digest.update(bytes.fromhex(digest))

    counts = SourceCounts(
        source_rows=totals["source_rows"],
        source_groups=totals["source_groups"],
        manual_boundaries=totals["manual_boundaries"],
        retained_source_rows=totals["retained_source_rows"],
        retained_source_groups=totals["retained_source_groups"],
        excluded_fros_rows=totals["excluded_fros_rows"],
        excluded_fros_groups=totals["excluded_fros_groups"],
        excluded_fros_loci=len(excluded_loci),
        strict_unconsumed_length_eligible_manual_groups=totals["strict_unconsumed"],
        separator_counts=tuple(sorted(separator_counts.items())),
        panel_counts=tuple(panel_counts),
    )
    return SourcePanelBundle(
        panels=tuple(panels),
        counts=counts,
        source_hashes=source_hashes,
        atlas_sha256=ATLAS_SHA256,
        atlas_validation_sha256=ATLAS_VALIDATION_SHA256,
        bundle_digest=bundle_digest.hexdigest(),
    )


def _is_reachable_key(key: str) -> bool:
    return bool(key) and all(symbol in NIBBLE_CODE for symbol in key)


def _accepted_preimages(key: str) -> set[str]:
    output = {key, key + "yn"}
    for standard in STANDARD_PREFIXES:
        output.add(standard + key)
    for gallows in GALLOWS_PREFIXES:
        output.add(gallows + key)
        for standard in STANDARD_PREFIXES:
            output.add(gallows + standard + key)
    return output


def _build_lexicon_view(name: str, keys: Iterable[str]) -> LexiconView:
    key_set = set(keys)
    reachable = frozenset(key for key in key_set if _is_reachable_key(key))
    direct_codes = tuple(sorted({encode_skeleton(key) for key in reachable}))
    accepted_codes: set[int] = set()
    for key in reachable:
        for preimage in _accepted_preimages(key):
            if len(preimage) > 10:
                raise DANI001InputError("accepted affix preimage exceeds ten code points")
            accepted_codes.add(encode_skeleton(preimage))
    return LexiconView(
        name=name,
        total_key_count=len(key_set),
        reachable_key_count=len(reachable),
        reachable_keys=reachable,
        direct_codes=direct_codes,
        deposited_affix_codes=tuple(sorted(accepted_codes)),
    )


def _project_entry_list(entries: object, key_ordinal: int) -> tuple[bool, tuple[str, ...], int]:
    """Project one entry list without returning any forbidden source fields."""

    if not isinstance(entries, list) or not entries:
        raise DANI001InputError(
            f"lexicon key ordinal {key_ordinal} has no entry list"
        )
    has_source = False
    domains: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise DANI001InputError("lexicon entry is not an object")
        source = entry.get("source")
        if source is not None and not isinstance(source, str):
            raise DANI001InputError("lexicon source field is not string/null")
        has_source = has_source or bool(source)
        raw_domain = entry.get("domain")
        if raw_domain in (None, ""):
            domain = "missing"
        elif isinstance(raw_domain, str) and raw_domain in DOMAINS:
            domain = raw_domain
        else:
            raise DANI001InputError("lexicon domain field is outside frozen vocabulary")
        domains.append(domain)
    return has_source, tuple(domains), len(entries)


def project_lexicon_bytes(data: bytes, *, enforce_registered: bool = True) -> LexiconBundle:
    """Project a lexicon body to permitted key/source/domain metadata only."""

    document = _json_object(data)
    del data
    projected: dict[str, tuple[bool, tuple[str, ...]]] = {}
    entry_count = 0
    try:
        ordered_keys = sorted(document, key=lambda value: value.encode("utf-8"))
        for key_ordinal, key in enumerate(ordered_keys):
            if not isinstance(key, str) or not key:
                raise DANI001InputError("lexicon contains an invalid key")
            entries = document.pop(key)
            has_source, domains, count = _project_entry_list(entries, key_ordinal)
            projected[key] = (has_source, domains)
            entry_count += count
            del entries
    finally:
        # The top-level object owns every forbidden spelling/meaning/source value.
        # Clearing it immediately leaves only the permitted projection reachable.
        document.clear()

    all_keys = set(projected)
    reachable_keys = {key for key in all_keys if _is_reachable_key(key)}
    source_present = {key for key, value in projected.items() if value[0]}
    strict_no_function = {
        key for key, value in projected.items()
        if all(domain != "function" for domain in value[1])
    }
    view_key_sets: list[tuple[str, set[str]]] = [
        ("FULL", all_keys),
        ("REACHABLE", reachable_keys),
        ("SOURCE_PRESENT", source_present),
        ("STRICT_NO_FUNCTION", strict_no_function),
    ]
    for excluded in DOMAINS:
        view_key_sets.append((
            f"LEAVE_OUT_{excluded.upper()}",
            {
                key for key, value in projected.items()
                if any(domain != excluded for domain in value[1])
            },
        ))
    views = tuple(_build_lexicon_view(name, keys) for name, keys in view_key_sets)
    by_name = {view.name: view for view in views}
    saved_unreachable = all_keys - reachable_keys
    if reachable_keys & saved_unreachable:
        raise DANI001InputError("unreachable remove-state overlap")
    restored_keys = set(reachable_keys)
    before_restore = len(restored_keys)
    restored_keys.update(saved_unreachable)
    if (
        len(restored_keys) != before_restore + len(saved_unreachable)
        or restored_keys != all_keys
    ):
        raise DANI001InputError("unreachable remove/add restoration failed")
    restored_view = _build_lexicon_view("RESTORED", restored_keys)
    if (
        restored_view.total_key_count != by_name["FULL"].total_key_count
        or restored_view.reachable_key_count
        != by_name["FULL"].reachable_key_count
        or restored_view.direct_codes != by_name["FULL"].direct_codes
        or restored_view.deposited_affix_codes
        != by_name["FULL"].deposited_affix_codes
    ):
        raise DANI001InputError("restored/full lexicon projection drift")
    counts = LexiconCounts(
        keys=len(all_keys),
        entries=entry_count,
        reachable_keys=len(reachable_keys),
        unreachable_keys=len(all_keys) - len(reachable_keys),
        source_present_keys=len(source_present),
        source_present_reachable_keys=by_name["SOURCE_PRESENT"].reachable_key_count,
        strict_no_function_keys=len(strict_no_function),
        strict_no_function_reachable_keys=by_name["STRICT_NO_FUNCTION"].reachable_key_count,
        view_counts=tuple(
            (
                view.name,
                view.total_key_count,
                view.reachable_key_count,
                len(view.direct_codes),
                len(view.deposited_affix_codes),
            )
            for view in views
        ),
    )
    if enforce_registered:
        expected = {
            "keys": 1_389,
            "entries": 1_441,
            "reachable_keys": 819,
            "unreachable_keys": 570,
            "source_present_keys": 104,
            "source_present_reachable_keys": 55,
            "strict_no_function_keys": 1_243,
            "strict_no_function_reachable_keys": 738,
        }
        observed = {
            field: getattr(counts, field)
            for field in expected
        }
        if observed != expected:
            raise DANI001InputError("registered lexicon projection count drift")
        if (
            by_name["FULL"].direct_codes != by_name["REACHABLE"].direct_codes
            or by_name["FULL"].deposited_affix_codes
            != by_name["REACHABLE"].deposited_affix_codes
        ):
            raise DANI001InputError("unreachable-key encoding invariant failed")
    projected.clear()
    return LexiconBundle(
        views=views,
        counts=counts,
        restored_view=restored_view,
    )


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def _response_status(response: Any) -> int:
    value = getattr(response, "status", None)
    if value is None:
        value = getattr(response, "code", None)
    if type(value) is not int:
        raise DANI001InputError("external acquisition status is unavailable")
    return value


def _response_locations(response: Any) -> tuple[str, ...]:
    headers = getattr(response, "headers", None)
    if headers is None:
        return ()
    get_all = getattr(headers, "get_all", None)
    if callable(get_all):
        values = get_all("Location")
        if values is None:
            return ()
        if not isinstance(values, list) or any(type(value) is not str for value in values):
            raise DANI001InputError("external acquisition Location header malformed")
        return tuple(values)
    get = getattr(headers, "get", None)
    if not callable(get):
        raise DANI001InputError("external acquisition headers malformed")
    value = get("Location")
    if value is None:
        return ()
    if type(value) is not str:
        raise DANI001InputError("external acquisition Location header malformed")
    return (value,)


def _open_no_redirect(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    timeout: float,
) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-DANI001/1"})
    try:
        return opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        # With _NoRedirectHandler, urllib represents every HTTP redirect as an
        # HTTPError.  Return it as the inert response so the exact status and
        # Location can be checked manually; no automatic follow is possible.
        return error
    except (OSError, urllib.error.URLError) as error:
        raise DANI001InputError("external acquisition failed") from error


def _require_exact_response(
    response: Any,
    *,
    url: str,
    status: int,
    locations: tuple[str, ...],
) -> None:
    if (
        _response_status(response) != status
        or response.geturl() != url
        or _response_locations(response) != locations
    ):
        raise DANI001InputError("external acquisition response contract drift")


def _download_exact(
    opener: urllib.request.OpenerDirector,
    url: str,
    destination: Path,
    *,
    timeout: float,
    byte_limit: int,
) -> None:
    if url not in (PIPELINE_URL, LEXICON_URL):
        raise DANI001InputError("unregistered acquisition endpoint")
    total = 0
    try:
        with _open_no_redirect(opener, url, timeout=timeout) as response:
            _require_exact_response(response, url=url, status=200, locations=())
            with destination.open("xb") as output:
                while True:
                    block = response.read(64 * 1024)
                    if not block:
                        break
                    total += len(block)
                    if total > byte_limit:
                        raise DANI001InputError("external body exceeded byte limit")
                    output.write(block)
                output.flush()
                os.fsync(output.fileno())
    except (OSError, urllib.error.URLError) as error:
        raise DANI001InputError("external acquisition failed") from error


def _download_exact_bytes(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    timeout: float,
    byte_limit: int,
) -> bytes:
    """Fetch one registered body without ever materializing it on disk."""

    if url != CONCEPT_URL:
        raise DANI001InputError("unregistered acquisition endpoint")
    output = bytearray()
    try:
        with _open_no_redirect(opener, url, timeout=timeout) as response:
            _require_exact_response(
                response,
                url=CONCEPT_URL,
                status=302,
                locations=(CONCEPT_REDIRECT_LOCATION,),
            )
        with _open_no_redirect(
            opener, CONCEPT_RESOLVED_URL, timeout=timeout
        ) as response:
            _require_exact_response(
                response,
                url=CONCEPT_RESOLVED_URL,
                status=200,
                locations=(),
            )
            while True:
                block = response.read(64 * 1024)
                if not block:
                    break
                if len(output) + len(block) > byte_limit:
                    raise DANI001InputError("external body exceeded byte limit")
                output.extend(block)
    except (OSError, urllib.error.URLError) as error:
        raise DANI001InputError("external acquisition failed") from error
    return bytes(output)


def _external_temp_base(temp_base: Path | None) -> Path:
    base = (temp_base or Path(tempfile.gettempdir())).resolve()
    try:
        base.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return base
    raise DANI001InputError("external temporary directory is inside repository")


def _validate_acquisition_lease(acquisition: RegisteredExternalAcquisition) -> None:
    if not isinstance(acquisition, RegisteredExternalAcquisition):
        raise DANI001InputError("invalid registered external acquisition lease")
    if (
        not isinstance(acquisition._projection_calls, list)
        or len(acquisition._projection_calls) != 1
        or acquisition._projection_calls[0] not in {0, 1}
    ):
        raise DANI001InputError("external acquisition projection state drift")
    root = acquisition.temporary_root
    expected_paths = {
        "pipeline.py.txt": acquisition.pipeline_path,
        "lexicon.json": acquisition.lexicon_path,
        "stable_metadata_projection.json": acquisition.stable_projection_path,
    }
    if any(path != root / name for name, path in expected_paths.items()):
        raise DANI001InputError("external acquisition path layout drift")
    try:
        inventory = {item.name: item for item in root.iterdir()}
    except OSError as error:
        raise DANI001InputError("external acquisition lease is no longer active") from error
    if inventory != expected_paths:
        raise DANI001InputError("external temporary inventory drift")
    if any(not path.is_file() or path.is_symlink() for path in expected_paths.values()):
        raise DANI001InputError("external temporary inventory contains a non-file")
    if (
        acquisition.stable_projection_sha256 != STABLE_PROJECTION_SHA256
        or acquisition.pipeline_sha256 != PIPELINE_SHA256
        or acquisition.lexicon_sha256 != LEXICON_SHA256
        or acquisition.acquisition_urls != ACQUISITION_URLS
    ):
        raise DANI001InputError("external acquisition binding drift")
    if sha256_path(acquisition.pipeline_path) != PIPELINE_SHA256:
        raise DANI001InputError("deposited pipeline hash drift")
    if sha256_path(acquisition.lexicon_path) != LEXICON_SHA256:
        raise DANI001InputError("deposited lexicon hash drift")
    projection_bytes = acquisition.stable_projection_path.read_bytes()
    if (
        projection_bytes != acquisition.stable_projection_bytes
        or sha256_bytes(projection_bytes) != STABLE_PROJECTION_SHA256
    ):
        raise DANI001InputError("stable Zenodo projection binding drift")


@contextmanager
def acquire_registered_external_files(
    *,
    timeout: float = 60.0,
    temp_base: Path | None = None,
) -> Iterator[RegisteredExternalAcquisition]:
    """Acquire and hash inputs without parsing the deposited lexicon.

    The yielded lease is valid only inside the context.  Its temporary directory
    contains exactly the inert pipeline body, lexicon body, and canonical safe
    metadata projection.  Raw concept metadata is held in memory only.
    """

    base = _external_temp_base(temp_base)
    opener = urllib.request.build_opener(_NoRedirectHandler())
    with tempfile.TemporaryDirectory(prefix="dani001-external-", dir=base) as directory:
        temporary = Path(directory)
        paths = {
            PIPELINE_URL: temporary / "pipeline.py.txt",
            LEXICON_URL: temporary / "lexicon.json",
        }
        limits = {
            CONCEPT_URL: 8 * 1024 * 1024,
            PIPELINE_URL: 256 * 1024,
            LEXICON_URL: 2 * 1024 * 1024,
        }
        concept_bytes = _download_exact_bytes(
            opener,
            CONCEPT_URL,
            timeout=timeout,
            byte_limit=limits[CONCEPT_URL],
        )
        for url in (PIPELINE_URL, LEXICON_URL):
            _download_exact(
                opener,
                url,
                paths[url],
                timeout=timeout,
                byte_limit=limits[url],
            )
        if sha256_path(paths[PIPELINE_URL]) != PIPELINE_SHA256:
            raise DANI001InputError("deposited pipeline hash drift")
        if sha256_path(paths[LEXICON_URL]) != LEXICON_SHA256:
            raise DANI001InputError("deposited lexicon hash drift")
        try:
            paths[PIPELINE_URL].read_bytes().decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise DANI001InputError("deposited pipeline is not UTF-8 text") from error
        metadata = _json_object(concept_bytes)
        del concept_bytes
        try:
            projection_bytes = canonical_json(stable_metadata_projection(metadata))
        finally:
            metadata.clear()
        if sha256_bytes(projection_bytes) != STABLE_PROJECTION_SHA256:
            raise DANI001InputError("stable Zenodo projection hash drift")
        projection_path = temporary / "stable_metadata_projection.json"
        with projection_path.open("xb") as projection_output:
            projection_output.write(projection_bytes)
            projection_output.flush()
            os.fsync(projection_output.fileno())
        directory_fd = os.open(temporary, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        acquisition = RegisteredExternalAcquisition(
            stable_projection_bytes=projection_bytes,
            stable_projection_sha256=STABLE_PROJECTION_SHA256,
            pipeline_sha256=PIPELINE_SHA256,
            lexicon_sha256=LEXICON_SHA256,
            acquisition_urls=ACQUISITION_URLS,
            temporary_root=temporary,
            pipeline_path=paths[PIPELINE_URL],
            lexicon_path=paths[LEXICON_URL],
            stable_projection_path=projection_path,
        )
        _validate_acquisition_lease(acquisition)
        yield acquisition


def project_acquired_lexicon(
    acquisition: RegisteredExternalAcquisition,
    *,
    synthetic_gate_passed: bool,
) -> LexiconBundle:
    """Parse one active acquisition only after an explicit synthetic PASS."""

    if synthetic_gate_passed is not True:
        raise DANI001InputError("external lexicon parse attempted before synthetic PASS")
    _validate_acquisition_lease(acquisition)
    if acquisition._projection_calls[0] != 0:
        raise DANI001InputError("external lexicon projection attempted more than once")
    acquisition._projection_calls[0] = 1
    return project_lexicon_bytes(
        acquisition.lexicon_path.read_bytes(),
        enforce_registered=True,
    )


def acquire_registered_external_inputs(
    *,
    timeout: float = 60.0,
    temp_base: Path | None = None,
) -> ExternalInputBundle:
    """Immediate convenience loader; calibration runners must use the split API."""

    with acquire_registered_external_files(
        timeout=timeout,
        temp_base=temp_base,
    ) as acquisition:
        lexicon = project_acquired_lexicon(
            acquisition,
            synthetic_gate_passed=True,
        )
        projection_bytes = acquisition.stable_projection_bytes
    return ExternalInputBundle(
        stable_projection_bytes=projection_bytes,
        stable_projection_sha256=STABLE_PROJECTION_SHA256,
        pipeline_sha256=PIPELINE_SHA256,
        lexicon_sha256=LEXICON_SHA256,
        lexicon=lexicon,
        acquisition_urls=ACQUISITION_URLS,
    )


def load_registered_inputs(
    repo_root: Path = REPO_ROOT,
    *,
    timeout: float = 60.0,
    temp_base: Path | None = None,
) -> DANI001InputBundle:
    """Acquire external evidence first, then reconstruct private source panels."""

    external = acquire_registered_external_inputs(timeout=timeout, temp_base=temp_base)
    source = load_registered_source_panels(external.lexicon, repo_root)
    return DANI001InputBundle(external=external, source=source)


def source_free_smoke_test() -> dict[str, int | str]:
    """Exercise parser/encoding/projection primitives without source or network."""

    groups, boundaries = split_source_groups("a.b,c<->d<~>e")
    if groups != ["a", "b", "c", "d", "e"]:
        raise DANI001InputError("synthetic separator groups failed")
    if boundaries != [".", ",", "<->", "<~>"]:
        raise DANI001InputError("synthetic separator states failed")
    normalized, ambiguous = normalize_source_text("[ch:sh][ol:or]{drop}<note>")
    if normalized != "chol" or not ambiguous:
        raise DANI001InputError("synthetic primary/annotation selection failed")
    token_result = compile_source_token("cthody", 7)
    if token_result is None or not token_result[1]:
        raise DANI001InputError("synthetic scanner failed")
    encoded = encode_skeleton("ṭkyn")
    if decode_skeleton(encoded) != "ṭkyn":
        raise DANI001InputError("synthetic nibble round trip failed")
    fake = canonical_json({
        "k": [{"domain": "general", "source": "discard-me", "meaning": "discard-me"}],
        "d": [{"domain": "function", "syriac": "discard-me"}],
        "zz": [{"domain": "medical", "vowel_hint": "discard-me"}],
    })
    lexicon = project_lexicon_bytes(fake, enforce_registered=False)
    if lexicon.counts.keys != 3 or lexicon.counts.reachable_keys != 2:
        raise DANI001InputError("synthetic lexicon projection failed")
    if lexicon.view("FULL").direct_codes != lexicon.view("REACHABLE").direct_codes:
        raise DANI001InputError("synthetic unreachable-key invariant failed")
    return {
        "status": "PASS_SOURCE_FREE_SMOKE",
        "separator_states": len(boundaries),
        "emitted_template_length": token_result[0].output_length,
        "fake_lexicon_keys": lexicon.counts.keys,
        "fake_reachable_keys": lexicon.counts.reachable_keys,
    }


__all__ = [
    "CORE_INPUTS",
    "CORE_OUTPUTS",
    "CORE_OUTPUT_CODES",
    "DANI001InputBundle",
    "DANI001InputError",
    "ExternalInputBundle",
    "LexiconBundle",
    "LexiconCounts",
    "LexiconView",
    "Panel",
    "PanelToken",
    "RegisteredExternalAcquisition",
    "SourceCounts",
    "SourcePanelBundle",
    "acquire_registered_external_files",
    "acquire_registered_external_inputs",
    "canonical_json",
    "compile_source_token",
    "decode_skeleton",
    "encode_skeleton",
    "load_registered_inputs",
    "load_registered_source_panels",
    "normalize_source_text",
    "project_lexicon_bytes",
    "project_acquired_lexicon",
    "scan_normalized_eva",
    "source_free_smoke_test",
    "split_source_groups",
    "stable_metadata_projection",
]
