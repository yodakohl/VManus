#!/usr/bin/env python3
"""Offline structural validator for the three frozen GDT621 Latin artifacts.

This program deliberately handles JSON only.  It does not inspect directories,
open images, fetch network resources, interpret diplomatic text, or consult the
registered profile at runtime.  The constants below are the public values frozen
by REGISTERED_READING_PROFILE.json.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


EXPERIMENT_ID = "GDT621"
CHECKPOINT_STATUS = "LATIN_RECONCILIATION_FROZEN__CLM_UNOPENED"
CANONICALIZATION = "UTF-8 JSON; sorted keys; compact separators; LF final byte"
CLAIM_CEILING = (
    "MANUAL_SOURCE_READING_PROTOCOL_ONLY__NO_IMAGE_OPENED_AT_REGISTRATION__"
    "NO_VOYNICH_SIGN_WORD_LANGUAGE_PLAINTEXT_PLANT_OR_MEANING"
)

CANDIDATE_IDS = ("DEV01", "DEV02", "DEV03", "DEV04", "DEV05")
LATIN_SOURCE_SHA256S = {
    "DEV01": "a12f51056ad4e18ae4ed40739987dae3924618787ebbaac1c481ac0b2976ef2a",
    "DEV02": "470aca9b7d6cdfd9aa3cb321d165f86b01e15f8de8193e50d8a9dbb722c71b11",
    "DEV03": "01397d43449619b004fcee6fdacc3e236dfb3523f689ef0c51d0ff550f30b6b4",
    "DEV04": "055dd108bbec73ca7a8b80f9cfa3c467b3ca560ef9650015f05aaffd2e28ca8d",
    "DEV05": "8091ac2ac1939ac11e88d314501c4ef68d0015e6c38b89ad08a07a30521e0a4a",
}

GDT620_BINDING = {
    "gdt620_acquisition_code_registration_commit": (
        "61a253ce2756ad06a6c69c620e702500f5e640ef"
    ),
    "gdt620_result_publication_commit": (
        "798e05f46e79c4abd2047577669d3a67d561ec51"
    ),
    "gdt620_result_path": (
        "experiments/yolo/gdt620_stage_b_source_page_acquisition/"
        "artifacts/STAGE_B_RESULT.json"
    ),
    "gdt620_result_sha256": (
        "f14976f54fd4ea0424ada9f23d19e7f02424beff739f5b4943dd3b0329ae378e"
    ),
}

RAW_KEYS = ("reader_id", "session_id", "pages", "submitted_utc", "bundle_sha256")
RAW_PREIMAGE_KEYS = ("reader_id", "session_id", "pages", "submitted_utc")
RAW_PAGE_KEYS = (
    "candidate_id",
    "source_sha256",
    "rendering_session_id",
    "full_page_viewed_first",
    "heading_or_rubric",
    "tokens_1_through_12",
    "diplomatic_stream",
    "uncertainties",
    "submitted_utc",
    "access_audit_ref",
)
READING_KEYS = (
    "candidate_id",
    "source_sha256",
    "heading_or_rubric",
    "tokens_1_through_12",
    "diplomatic_stream",
    "uncertainties",
)
CAPTURE_KEYS = (
    "heading_or_rubric",
    "tokens_1_through_12",
    "diplomatic_stream",
    "uncertainties",
)
LEDGER_KEYS = (
    "candidate_id",
    "row_kind",
    "field",
    "position",
    "reader_a",
    "reader_b",
    "difference_type",
    "reconciled_reading",
    "resolution_reason",
    "adjudicator",
    "resolved_utc",
)
AUDIT_KEYS = (
    "adjudicator_id",
    "session_id",
    "started_utc",
    "completed_utc",
    "attested_utc",
    "frozen_reader_a_bundle_sha256",
    "frozen_reader_b_bundle_sha256",
    "only_frozen_bundles_and_five_latin_jpegs_used",
    "clm_access_count",
    "network_access_count",
    "repository_or_profile_access_count",
    "catalog_access_count",
    "edition_access_count",
    "other_source_access_count",
    "voynich_access_count",
    "f84_access_count",
    "f84r_access_count",
)
ZERO_AUDIT_KEYS = (
    "clm_access_count",
    "network_access_count",
    "repository_or_profile_access_count",
    "catalog_access_count",
    "edition_access_count",
    "other_source_access_count",
    "voynich_access_count",
    "f84_access_count",
    "f84r_access_count",
)
CHECKPOINT_KEYS = (
    "experiment_id",
    "status",
    "gdt620_binding",
    "raw_bundle_sha256s",
    "reconciled_latin",
    "difference_ledger",
    "reconciliation_access_audit",
    "canonicalization",
    "claim_ceiling",
    "checkpoint_sha256",
)
CHECKPOINT_PREIMAGE_KEYS = CHECKPOINT_KEYS[:-1]

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SESSION_RES = {
    "READER_A": re.compile(r"^SESSION_A_[A-F0-9]{16}$"),
    "READER_B": re.compile(r"^SESSION_B_[A-F0-9]{16}$"),
}
ADJUDICATOR_RE = re.compile(r"^ADJUDICATOR_[A-F0-9]{16}$")
UTC_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?Z$"
)
SIGN_TAG_PATTERN = r"<SIGN:[^<>\s]+>"
UNCERTAIN_TAG_PATTERN = rf"<UNCERTAIN:(?:[^<>\s]|{SIGN_TAG_PATTERN})+>"
TAG_RE = re.compile(
    rf"(?:{SIGN_TAG_PATTERN}|{UNCERTAIN_TAG_PATTERN}|<UNREADABLE>)"
)
ABSOLUTE_PATH_RE = re.compile(r"(^|[\s\"'])(?:/|[A-Za-z]:[\\/])")
IMAGE_FILENAME_RE = re.compile(
    r"(?i)(?:^|[/\\\s])[A-Za-z0-9_. -]+\.(?:jpe?g|png|gif|tiff?|webp|bmp)(?:$|[\s])"
)
IMAGE_BASE64_RE = re.compile(r"(?i)(?:data:image/|(?:^|[\s\"'])(?:/9j/|iVBORw0KGgo|R0lGOD))")
IMAGE_HEX_RE = re.compile(r"(?i)(?:^|[^0-9a-f])ffd8ffe[0-9a-f]")
URL_RE = re.compile(r"(?i)(?:file|https?|ftp)://")
PRIVATE_COMPONENT_RE = re.compile(
    r"(?i)(?:^|[/\\])(?:home|users?|private|tmp|var|mnt|media|root|workspace)(?:[/\\]|$)"
)
PEM_PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
LONG_BASE64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
FORBIDDEN_KEYS = {
    "absolute_path",
    "base64",
    "blob",
    "bytes",
    "cwd",
    "directory",
    "filename",
    "hostname",
    "image_bytes",
    "image",
    "saved_crop",
    "private_directory",
    "private_filename",
    "private_key",
    "machine_metadata",
    "path",
    "pixels",
    "username",
    "voynich_material",
    "jpeg_bytes",
    "png_bytes",
    "image_base64",
}

MAX_ARTIFACT_BYTES = 4 * 1024 * 1024
MAX_STRING_CODEPOINTS = 1_000_000


class ValidationError(Exception):
    """A deterministic, value-redacted validation failure."""


def _fail(path: str, message: str) -> None:
    raise ValidationError(f"{path}: {message}")


def _canonical_bytes(value: Any) -> bytes:
    try:
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return rendered.encode("utf-8") + b"\n"
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise ValidationError("JSON value cannot be represented as canonical UTF-8") from exc


def _sha256_without(value: Mapping[str, Any], own_hash_key: str) -> str:
    preimage = dict(value)
    if own_hash_key not in preimage:
        _fail("hash", f"missing own hash field {own_hash_key}")
    del preimage[own_hash_key]
    return hashlib.sha256(_canonical_bytes(preimage)).hexdigest()


def _parse_canonical_json(data: bytes, label: str) -> dict[str, Any]:
    if len(data) > MAX_ARTIFACT_BYTES:
        _fail(label, "artifact is too large for a compact text checkpoint")
    if data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a")):
        _fail(label, "image bytes are forbidden")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{label}: not strict UTF-8 JSON") from exc

    def reject_constant(token: str) -> None:
        raise ValidationError(f"{label}: non-finite JSON number is forbidden")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValidationError(f"{label}: duplicate JSON object key")
            result[key] = value
        return result

    try:
        parsed = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except ValidationError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ValidationError(f"{label}: malformed JSON") from exc
    if type(parsed) is not dict:
        _fail(label, "top-level JSON value must be an object")
    if data != _canonical_bytes(parsed):
        _fail(
            label,
            "bytes are not canonical UTF-8 sorted-key compact JSON with one final LF",
        )
    _validate_privacy(parsed, label)
    return parsed


def _validate_privacy(value: Any, path: str, *, _depth: int = 0) -> None:
    if _depth > 64:
        _fail(path, "JSON nesting exceeds the privacy audit limit")
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                _fail(path, "JSON object key is not a string")
            if key.casefold() in FORBIDDEN_KEYS:
                _fail(path, "forbidden private/path/image field is present")
            _validate_privacy(child, f"{path}.{key}", _depth=_depth + 1)
        return
    if type(value) is list:
        if value and all(type(item) is int and 0 <= item <= 255 for item in value):
            prefix = bytes(value[:8])
            if len(value) >= 4096 or prefix.startswith(
                (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a")
            ):
                _fail(path, "embedded binary/image byte array is forbidden")
        for index, child in enumerate(value):
            _validate_privacy(child, f"{path}[{index}]", _depth=_depth + 1)
        return
    if type(value) is str:
        if len(value) > MAX_STRING_CODEPOINTS:
            _fail(path, "oversized string may contain embedded binary material")
        allowed_registered_path = (
            path.endswith(".gdt620_binding.gdt620_result_path")
            and value == GDT620_BINDING["gdt620_result_path"]
        )
        if not allowed_registered_path and (
            ABSOLUTE_PATH_RE.search(value)
            or value.startswith(("\\\\", "~/", "../", "./"))
            or URL_RE.search(value)
            or PRIVATE_COMPONENT_RE.search(value)
        ):
            _fail(path, "absolute/private path or URL is forbidden")
        if IMAGE_FILENAME_RE.search(value):
            _fail(path, "image filename is forbidden")
        if IMAGE_BASE64_RE.search(value) or IMAGE_HEX_RE.search(value):
            _fail(path, "embedded image bytes are forbidden")
        if len(value) >= 4096 and LONG_BASE64_RE.fullmatch(value):
            _fail(path, "large base64-like payload is forbidden")
        if PEM_PRIVATE_KEY_RE.search(value):
            _fail(path, "private-key material is forbidden")


def _expect_dict(value: Any, path: str) -> dict[str, Any]:
    if type(value) is not dict:
        _fail(path, "must be a JSON object")
    return value


def _expect_list(value: Any, path: str) -> list[Any]:
    if type(value) is not list:
        _fail(path, "must be a JSON array")
    return value


def _expect_exact_keys(value: Mapping[str, Any], expected: Sequence[str], path: str) -> None:
    actual = set(value)
    wanted = set(expected)
    if actual != wanted:
        missing = len(wanted - actual)
        unexpected = len(actual - wanted)
        _fail(
            path,
            f"exact schema mismatch ({missing} missing, {unexpected} unexpected keys)",
        )


def _expect_string(value: Any, path: str, *, nonempty: bool = True) -> str:
    if type(value) is not str:
        _fail(path, "must be a string")
    if nonempty and value == "":
        _fail(path, "must be a nonempty string")
    return value


def _expect_nullable_string(value: Any, path: str) -> str | None:
    if value is None:
        return None
    return _expect_string(value, path, nonempty=False)


def _expect_exact(value: Any, expected: Any, path: str) -> None:
    if type(value) is not type(expected) or value != expected:
        _fail(path, "does not equal the registered value")


def _expect_pattern(value: Any, pattern: re.Pattern[str], path: str) -> str:
    string = _expect_string(value, path)
    if pattern.fullmatch(string) is None:
        _fail(path, "does not match the registered pattern")
    return string


def _expect_path_free_identifier(value: Any, path: str) -> str:
    string = _expect_string(value, path)
    if any(character.isspace() for character in string) or "/" in string or "\\" in string:
        _fail(path, "must be a whitespace-free, path-free identifier")
    return string


def _json_bytes_equal(left: Any, right: Any) -> bool:
    return _canonical_bytes(left) == _canonical_bytes(right)


def _field_identifies_token_boundaries(field: str) -> bool:
    parts = set(filter(None, re.split(r"[^a-z0-9]+", field.casefold())))
    return bool(parts & {"token", "tokens"}) and bool(parts & {"boundary", "boundaries"})


def _has_distinct_position_ordinals(position: Any) -> bool:
    if type(position) is not str or position.strip() == "":
        return False
    ordinals = re.findall(r"[0-9]+", position)
    return len(ordinals) >= 2 and ordinals[-2] != ordinals[-1]


def _parse_utc(value: Any, path: str) -> datetime:
    string = _expect_string(value, path)
    if UTC_RE.fullmatch(string) is None:
        _fail(path, "must be an ISO-8601 UTC timestamp ending in Z")
    try:
        return datetime.fromisoformat(string[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationError(f"{path}: invalid UTC calendar timestamp") from exc


def _validate_tags(value: str, path: str) -> None:
    without_registered_tags = TAG_RE.sub("", value)
    if "<" in without_registered_tags or ">" in without_registered_tags:
        _fail(path, "contains an unregistered or whitespace-bearing diplomatic tag")


def _validate_uncertainties(value: Any, path: str) -> list[Any]:
    # The registration fixes this as codepoint-addressed notes, but does not fix
    # an entry schema.  Requiring an array preserves exact values for comparison
    # without inventing note keys or a position syntax.
    notes = _expect_list(value, path)
    for index, note in enumerate(notes):
        if note is None or type(note) not in (str, dict):
            _fail(f"{path}[{index}]", "uncertainty note must be a string or object")
        if type(note) is str and note == "":
            _fail(f"{path}[{index}]", "uncertainty note must not be empty")
    return notes


def _validate_capture_fields(page: Mapping[str, Any], path: str) -> None:
    heading = _expect_string(page["heading_or_rubric"], f"{path}.heading_or_rubric")
    _validate_tags(heading, f"{path}.heading_or_rubric")

    tokens = _expect_list(page["tokens_1_through_12"], f"{path}.tokens_1_through_12")
    if len(tokens) != 12:
        _fail(f"{path}.tokens_1_through_12", "must contain exactly 12 tokens")
    checked_tokens: list[str] = []
    for index, token in enumerate(tokens):
        token_path = f"{path}.tokens_1_through_12[{index}]"
        checked = _expect_string(token, token_path)
        if any(character.isspace() for character in checked):
            _fail(token_path, "token contains whitespace")
        _validate_tags(checked, token_path)
        checked_tokens.append(checked)

    stream = _expect_string(page["diplomatic_stream"], f"{path}.diplomatic_stream")
    _validate_tags(stream, f"{path}.diplomatic_stream")
    if not stream.startswith(heading):
        _fail(f"{path}.diplomatic_stream", "must begin with the exact heading/rubric")
    following = stream[len(heading) :]
    if not heading[-1].isspace() and (not following or not following[0].isspace()):
        _fail(
            f"{path}.diplomatic_stream",
            "must separate the heading/rubric from the following tokens with whitespace",
        )
    if following.split() != checked_tokens:
        _fail(
            f"{path}.diplomatic_stream",
            "must contain exactly the registered 12 token strings after the heading/rubric",
        )
    _validate_uncertainties(page["uncertainties"], f"{path}.uncertainties")


def _validate_raw_bundle(
    obj: Mapping[str, Any], expected_reader: str, label: str
) -> dict[str, Any]:
    bundle = _expect_dict(obj, label)
    _expect_exact_keys(bundle, RAW_KEYS, label)
    _expect_exact(bundle["reader_id"], expected_reader, f"{label}.reader_id")
    session_id = _expect_pattern(
        bundle["session_id"], SESSION_RES[expected_reader], f"{label}.session_id"
    )
    bundle_submitted = _parse_utc(bundle["submitted_utc"], f"{label}.submitted_utc")
    bundle_sha = _expect_pattern(bundle["bundle_sha256"], SHA256_RE, f"{label}.bundle_sha256")
    if tuple(key for key in RAW_PREIMAGE_KEYS) != RAW_KEYS[:-1]:
        _fail(label, "internal raw preimage key contract is inconsistent")
    if bundle_sha != _sha256_without(bundle, "bundle_sha256"):
        _fail(f"{label}.bundle_sha256", "nonrecursive bundle SHA-256 mismatch")

    pages = _expect_list(bundle["pages"], f"{label}.pages")
    if len(pages) != 5:
        _fail(f"{label}.pages", "must contain exactly five readings")
    page_times: list[datetime] = []
    rendering_ids: list[str] = []
    audit_refs: list[str] = []
    checked_pages: list[dict[str, Any]] = []
    for index, candidate_id in enumerate(CANDIDATE_IDS):
        page_path = f"{label}.pages[{index}]"
        if index >= len(pages):
            _fail(page_path, "registered page is missing")
        page = _expect_dict(pages[index], page_path)
        _expect_exact_keys(page, RAW_PAGE_KEYS, page_path)
        _expect_exact(page["candidate_id"], candidate_id, f"{page_path}.candidate_id")
        _expect_exact(
            page["source_sha256"],
            LATIN_SOURCE_SHA256S[candidate_id],
            f"{page_path}.source_sha256",
        )
        if page["full_page_viewed_first"] is not True:
            _fail(f"{page_path}.full_page_viewed_first", "must be exactly true")
        rendering_id = _expect_path_free_identifier(
            page["rendering_session_id"], f"{page_path}.rendering_session_id"
        )
        rendering_ids.append(rendering_id)
        audit_ref = _expect_path_free_identifier(
            page["access_audit_ref"], f"{page_path}.access_audit_ref"
        )
        audit_refs.append(audit_ref)
        submitted = _parse_utc(page["submitted_utc"], f"{page_path}.submitted_utc")
        if submitted > bundle_submitted:
            _fail(f"{page_path}.submitted_utc", "must not be later than bundle submission")
        page_times.append(submitted)
        _validate_capture_fields(page, page_path)
        checked_pages.append(page)

    if page_times != sorted(page_times):
        _fail(f"{label}.pages", "page submission timestamps must follow DEV01..DEV05 order")
    if len(set(rendering_ids)) != 5:
        _fail(f"{label}.pages", "each page requires a fresh rendering session ID")
    if len(set(audit_refs)) != 5:
        _fail(f"{label}.pages", "each page requires a distinct access audit reference")
    return {
        "object": bundle,
        "pages": checked_pages,
        "session_id": session_id,
        "bundle_sha256": bundle_sha,
        "submitted_utc": bundle_submitted,
        "page_submitted_utcs": page_times,
        "rendering_session_ids": rendering_ids,
        "access_audit_refs": audit_refs,
    }


def _validate_reconciled_page(value: Any, index: int, label: str) -> dict[str, Any]:
    path = f"{label}.reconciled_latin[{index}]"
    page = _expect_dict(value, path)
    _expect_exact_keys(page, READING_KEYS, path)
    candidate_id = CANDIDATE_IDS[index]
    _expect_exact(page["candidate_id"], candidate_id, f"{path}.candidate_id")
    _expect_exact(
        page["source_sha256"], LATIN_SOURCE_SHA256S[candidate_id], f"{path}.source_sha256"
    )
    _validate_capture_fields(page, path)
    return page


def _validate_audit(
    value: Any,
    raw_a: Mapping[str, Any],
    raw_b: Mapping[str, Any],
    label: str,
) -> dict[str, Any]:
    path = f"{label}.reconciliation_access_audit"
    audit = _expect_dict(value, path)
    _expect_exact_keys(audit, AUDIT_KEYS, path)
    adjudicator = _expect_pattern(audit["adjudicator_id"], ADJUDICATOR_RE, f"{path}.adjudicator_id")
    session_id = _expect_path_free_identifier(audit["session_id"], f"{path}.session_id")
    started = _parse_utc(audit["started_utc"], f"{path}.started_utc")
    completed = _parse_utc(audit["completed_utc"], f"{path}.completed_utc")
    attested = _parse_utc(audit["attested_utc"], f"{path}.attested_utc")
    if not started <= completed <= attested:
        _fail(path, "timestamps must satisfy started <= completed <= attested")
    if started < max(raw_a["submitted_utc"], raw_b["submitted_utc"]):
        _fail(f"{path}.started_utc", "reconciliation began before both raw bundles froze")
    _expect_exact(
        audit["frozen_reader_a_bundle_sha256"],
        raw_a["bundle_sha256"],
        f"{path}.frozen_reader_a_bundle_sha256",
    )
    _expect_exact(
        audit["frozen_reader_b_bundle_sha256"],
        raw_b["bundle_sha256"],
        f"{path}.frozen_reader_b_bundle_sha256",
    )
    if audit["only_frozen_bundles_and_five_latin_jpegs_used"] is not True:
        _fail(
            f"{path}.only_frozen_bundles_and_five_latin_jpegs_used",
            "must be exactly true",
        )
    for key in ZERO_AUDIT_KEYS:
        if type(audit[key]) is not int or audit[key] != 0:
            _fail(f"{path}.{key}", "must be integer zero")
    return {
        "object": audit,
        "adjudicator_id": adjudicator,
        "session_id": session_id,
        "started_utc": started,
        "completed_utc": completed,
        "attested_utc": attested,
    }


def _capture(page: Mapping[str, Any]) -> dict[str, Any]:
    return {key: page[key] for key in CAPTURE_KEYS}


def _validate_ledger(
    value: Any,
    raw_a_pages: Sequence[Mapping[str, Any]],
    raw_b_pages: Sequence[Mapping[str, Any]],
    reconciled_pages: Sequence[Mapping[str, Any]],
    audit: Mapping[str, Any],
    label: str,
) -> list[dict[str, Any]]:
    path = f"{label}.difference_ledger"
    rows = _expect_list(value, path)
    if not rows:
        _fail(path, "must cover all five pages and cannot be empty")
    by_candidate: dict[str, list[dict[str, Any]]] = {candidate: [] for candidate in CANDIDATE_IDS}
    ranks: list[int] = []
    fingerprints: set[bytes] = set()
    checked_rows: list[dict[str, Any]] = []

    for index, item in enumerate(rows):
        row_path = f"{path}[{index}]"
        row = _expect_dict(item, row_path)
        _expect_exact_keys(row, LEDGER_KEYS, row_path)
        candidate_id = row["candidate_id"]
        if type(candidate_id) is not str or candidate_id not in by_candidate:
            _fail(f"{row_path}.candidate_id", "must be one of DEV01..DEV05")
        ranks.append(CANDIDATE_IDS.index(candidate_id))
        fingerprint = _canonical_bytes(row)
        if fingerprint in fingerprints:
            _fail(row_path, "duplicate ledger row")
        fingerprints.add(fingerprint)

        row_kind = row["row_kind"]
        if row_kind == "AGREEMENT_NO_DIFFERENCE":
            for key in LEDGER_KEYS[2:]:
                if row[key] is not None:
                    _fail(
                        f"{row_path}.{key}",
                        "agreement sentinel fields other than candidate_id/row_kind must be null",
                    )
        elif row_kind == "DIFFERENCE":
            field = _expect_string(row["field"], f"{row_path}.field")
            position = row["position"]
            if type(position) not in (str, int) or type(position) is bool:
                _fail(f"{row_path}.position", "must be a non-null string or integer")
            if (type(position) is str and position == "") or (type(position) is int and position < 0):
                _fail(f"{row_path}.position", "must identify a real nonnegative position")
            reader_a = _expect_nullable_string(row["reader_a"], f"{row_path}.reader_a")
            reader_b = _expect_nullable_string(row["reader_b"], f"{row_path}.reader_b")
            if reader_a in (None, "") and reader_b in (None, ""):
                _fail(row_path, "difference row must contain at least one present reader form")
            difference_type = _expect_string(
                row["difference_type"], f"{row_path}.difference_type"
            )
            if reader_a == reader_b:
                positional_exception = (
                    "POSITION_SHIFT" in difference_type.upper()
                    or _field_identifies_token_boundaries(field)
                )
                if not positional_exception:
                    _fail(
                        row_path,
                        "equal reader forms require an explicit position-shift/token-boundary row",
                    )
                if not _has_distinct_position_ordinals(position):
                    _fail(
                        f"{row_path}.position",
                        "equal-form position row must identify two distinct ordinals",
                    )
            _expect_nullable_string(
                row["reconciled_reading"], f"{row_path}.reconciled_reading"
            )
            _expect_string(row["resolution_reason"], f"{row_path}.resolution_reason")
            _expect_exact(row["adjudicator"], audit["adjudicator_id"], f"{row_path}.adjudicator")
            resolved = _parse_utc(row["resolved_utc"], f"{row_path}.resolved_utc")
            if not audit["started_utc"] <= resolved <= audit["completed_utc"]:
                _fail(f"{row_path}.resolved_utc", "must fall within reconciliation")
            if field.casefold() in FORBIDDEN_KEYS:
                _fail(f"{row_path}.field", "forbidden private/path/image field name")
        else:
            _fail(f"{row_path}.row_kind", "must be DIFFERENCE or AGREEMENT_NO_DIFFERENCE")
        by_candidate[candidate_id].append(row)
        checked_rows.append(row)

    if ranks != sorted(ranks):
        _fail(path, "rows must be grouped in DEV01..DEV05 page order")

    for index, candidate_id in enumerate(CANDIDATE_IDS):
        page_rows = by_candidate[candidate_id]
        if not page_rows:
            _fail(path, f"missing ledger coverage for {candidate_id}")
        a_capture = _capture(raw_a_pages[index])
        b_capture = _capture(raw_b_pages[index])
        reconciled_capture = _capture(reconciled_pages[index])
        equal = _json_bytes_equal(a_capture, b_capture)
        sentinels = [row for row in page_rows if row["row_kind"] == "AGREEMENT_NO_DIFFERENCE"]
        differences = [row for row in page_rows if row["row_kind"] == "DIFFERENCE"]
        if equal:
            if len(page_rows) != 1 or len(sentinels) != 1:
                _fail(path, f"{candidate_id} requires exactly one zero-difference sentinel")
            if not _json_bytes_equal(reconciled_capture, a_capture):
                _fail(
                    f"{label}.reconciled_latin[{index}]",
                    "agreed raw reading must be reused exactly",
                )
        else:
            if sentinels:
                _fail(path, f"{candidate_id} differs and cannot use an agreement sentinel")
            if not differences:
                _fail(path, f"{candidate_id} differs and requires at least one difference row")
            for key in CAPTURE_KEYS:
                if _json_bytes_equal(a_capture[key], b_capture[key]) and not _json_bytes_equal(
                    reconciled_capture[key], a_capture[key]
                ):
                    _fail(
                        f"{label}.reconciled_latin[{index}].{key}",
                        "reader-agreed value changed during reconciliation",
                    )
    return checked_rows


def _validate_checkpoint(
    obj: Mapping[str, Any],
    raw_a: Mapping[str, Any],
    raw_b: Mapping[str, Any],
    label: str,
) -> dict[str, Any]:
    checkpoint = _expect_dict(obj, label)
    _expect_exact_keys(checkpoint, CHECKPOINT_KEYS, label)
    _expect_exact(checkpoint["experiment_id"], EXPERIMENT_ID, f"{label}.experiment_id")
    _expect_exact(checkpoint["status"], CHECKPOINT_STATUS, f"{label}.status")
    _expect_exact(
        checkpoint["canonicalization"], CANONICALIZATION, f"{label}.canonicalization"
    )
    _expect_exact(checkpoint["claim_ceiling"], CLAIM_CEILING, f"{label}.claim_ceiling")

    binding = _expect_dict(checkpoint["gdt620_binding"], f"{label}.gdt620_binding")
    _expect_exact_keys(binding, tuple(GDT620_BINDING), f"{label}.gdt620_binding")
    for key, expected in GDT620_BINDING.items():
        _expect_exact(binding[key], expected, f"{label}.gdt620_binding.{key}")

    bundle_hashes = _expect_dict(
        checkpoint["raw_bundle_sha256s"], f"{label}.raw_bundle_sha256s"
    )
    _expect_exact_keys(bundle_hashes, ("READER_A", "READER_B"), f"{label}.raw_bundle_sha256s")
    _expect_exact(
        bundle_hashes["READER_A"], raw_a["bundle_sha256"], f"{label}.raw_bundle_sha256s.READER_A"
    )
    _expect_exact(
        bundle_hashes["READER_B"], raw_b["bundle_sha256"], f"{label}.raw_bundle_sha256s.READER_B"
    )

    readings = _expect_list(checkpoint["reconciled_latin"], f"{label}.reconciled_latin")
    if len(readings) != 5:
        _fail(f"{label}.reconciled_latin", "must contain exactly five reconciled readings")
    reconciled_pages = [
        _validate_reconciled_page(readings[index], index, label) for index in range(5)
    ]

    audit = _validate_audit(checkpoint["reconciliation_access_audit"], raw_a, raw_b, label)
    ledger = _validate_ledger(
        checkpoint["difference_ledger"],
        raw_a["pages"],
        raw_b["pages"],
        reconciled_pages,
        audit,
        label,
    )

    checkpoint_sha = _expect_pattern(
        checkpoint["checkpoint_sha256"], SHA256_RE, f"{label}.checkpoint_sha256"
    )
    if tuple(key for key in CHECKPOINT_PREIMAGE_KEYS) != CHECKPOINT_KEYS[:-1]:
        _fail(label, "internal checkpoint preimage key contract is inconsistent")
    if checkpoint_sha != _sha256_without(checkpoint, "checkpoint_sha256"):
        _fail(f"{label}.checkpoint_sha256", "nonrecursive checkpoint SHA-256 mismatch")
    return {
        "object": checkpoint,
        "reconciled_pages": reconciled_pages,
        "audit": audit,
        "ledger": ledger,
        "checkpoint_sha256": checkpoint_sha,
    }


def validate_artifact_bytes(
    reader_a_bytes: bytes, reader_b_bytes: bytes, checkpoint_bytes: bytes
) -> dict[str, str]:
    """Validate all artifacts from already-loaded bytes and return bound hashes."""

    a_obj = _parse_canonical_json(reader_a_bytes, "LATIN_READER_A_RAW.json")
    b_obj = _parse_canonical_json(reader_b_bytes, "LATIN_READER_B_RAW.json")
    checkpoint_obj = _parse_canonical_json(
        checkpoint_bytes, "LATIN_RECONCILIATION_FROZEN.json"
    )
    raw_a = _validate_raw_bundle(a_obj, "READER_A", "LATIN_READER_A_RAW.json")
    raw_b = _validate_raw_bundle(b_obj, "READER_B", "LATIN_READER_B_RAW.json")

    if raw_a["session_id"] == raw_b["session_id"]:
        _fail("raw bundles", "reader session IDs must be distinct")
    if set(raw_a["rendering_session_ids"]) & set(raw_b["rendering_session_ids"]):
        _fail("raw bundles", "rendering session IDs must be distinct across readers")
    if set(raw_a["access_audit_refs"]) & set(raw_b["access_audit_refs"]):
        _fail("raw bundles", "access audit references must be distinct across readers")
    if raw_a["submitted_utc"] > min(raw_b["page_submitted_utcs"]):
        _fail("raw bundles", "Reader B began submission before Reader A bundle froze")

    checkpoint = _validate_checkpoint(
        checkpoint_obj, raw_a, raw_b, "LATIN_RECONCILIATION_FROZEN.json"
    )
    return {
        "reader_a_bundle_sha256": raw_a["bundle_sha256"],
        "reader_b_bundle_sha256": raw_b["bundle_sha256"],
        "checkpoint_sha256": checkpoint["checkpoint_sha256"],
    }


def _artifact_paths() -> tuple[Path, Path, Path]:
    root = Path(__file__).resolve().parent.parent
    artifacts = root / "artifacts"
    return (
        artifacts / "LATIN_READER_A_RAW.json",
        artifacts / "LATIN_READER_B_RAW.json",
        artifacts / "LATIN_RECONCILIATION_FROZEN.json",
    )


def _read_json_artifact(path: Path) -> bytes:
    label = path.name
    if not path.exists():
        _fail(label, "required artifact is absent")
    if path.is_symlink():
        _fail(label, "symbolic-link artifacts are forbidden")
    if not path.is_file():
        _fail(label, "required artifact is not a regular file")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValidationError(f"{label}: cannot inspect artifact metadata") from exc
    if size > MAX_ARTIFACT_BYTES:
        _fail(label, "artifact is too large for a compact text checkpoint")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ValidationError(f"{label}: cannot read artifact") from exc


def run_check() -> int:
    paths = _artifact_paths()
    missing = [path.name for path in paths if not path.exists()]
    if missing:
        print(
            "CHECK FAIL: required canonical artifacts are absent: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1
    try:
        result = validate_artifact_bytes(*(_read_json_artifact(path) for path in paths))
    except ValidationError as exc:
        print(f"CHECK FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "CHECK PASS: 3/3 canonical artifacts; "
        f"Reader A {result['reader_a_bundle_sha256']}; "
        f"Reader B {result['reader_b_bundle_sha256']}; "
        f"checkpoint {result['checkpoint_sha256']}"
    )
    return 0


def _seal(mapping: dict[str, Any], key: str) -> None:
    mapping[key] = "0" * 64
    mapping[key] = _sha256_without(mapping, key)


def _synthetic_page(reader: str, index: int, minute: int) -> dict[str, Any]:
    candidate_id = CANDIDATE_IDS[index]
    heading = f"SYNTHETIC_RUBRIC_{candidate_id}"
    tokens = [f"synthetic_{candidate_id}_{number:02d}" for number in range(1, 13)]
    return {
        "candidate_id": candidate_id,
        "source_sha256": LATIN_SOURCE_SHA256S[candidate_id],
        "rendering_session_id": f"R{reader}_{index + 1:02d}_SYNTHETIC",
        "full_page_viewed_first": True,
        "heading_or_rubric": heading,
        "tokens_1_through_12": tokens,
        "diplomatic_stream": heading + " " + " ".join(tokens),
        "uncertainties": [],
        "submitted_utc": f"2026-08-29T00:{minute:02d}:00Z",
        "access_audit_ref": f"LATIN_EVENT_{reader}_{index + 1:02d}",
    }


def _synthetic_fixture(*, with_difference: bool = False) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    a = {
        "reader_id": "READER_A",
        "session_id": "SESSION_A_0123456789ABCDEF",
        "pages": [_synthetic_page("A", index, index + 1) for index in range(5)],
        "submitted_utc": "2026-08-29T00:06:00Z",
        "bundle_sha256": "",
    }
    b = {
        "reader_id": "READER_B",
        "session_id": "SESSION_B_FEDCBA9876543210",
        "pages": [_synthetic_page("B", index, index + 7) for index in range(5)],
        "submitted_utc": "2026-08-29T00:12:00Z",
        "bundle_sha256": "",
    }
    for index in range(5):
        for key in CAPTURE_KEYS:
            b["pages"][index][key] = copy.deepcopy(a["pages"][index][key])

    ledger: list[dict[str, Any]] = []
    if with_difference:
        b["pages"][0]["tokens_1_through_12"][0] = "synthetic_variant"
        b["pages"][0]["diplomatic_stream"] = (
            b["pages"][0]["heading_or_rubric"]
            + " "
            + " ".join(b["pages"][0]["tokens_1_through_12"])
        )
        ledger.append(
            {
                "candidate_id": "DEV01",
                "row_kind": "DIFFERENCE",
                "field": "tokens_1_through_12[0]",
                "position": "token:1",
                "reader_a": a["pages"][0]["tokens_1_through_12"][0],
                "reader_b": b["pages"][0]["tokens_1_through_12"][0],
                "difference_type": "SYNTHETIC_TOKEN_DIFFERENCE",
                "reconciled_reading": a["pages"][0]["tokens_1_through_12"][0],
                "resolution_reason": "synthetic self-test adjudication",
                "adjudicator": "ADJUDICATOR_0011223344556677",
                "resolved_utc": "2026-08-29T00:13:30Z",
            }
        )
    start = 1 if with_difference else 0
    for candidate_id in CANDIDATE_IDS[start:]:
        ledger.append(
            {
                "candidate_id": candidate_id,
                "row_kind": "AGREEMENT_NO_DIFFERENCE",
                "field": None,
                "position": None,
                "reader_a": None,
                "reader_b": None,
                "difference_type": None,
                "reconciled_reading": None,
                "resolution_reason": None,
                "adjudicator": None,
                "resolved_utc": None,
            }
        )
    _seal(a, "bundle_sha256")
    _seal(b, "bundle_sha256")
    reconciled = [
        {key: copy.deepcopy(a["pages"][index][key]) for key in READING_KEYS}
        for index in range(5)
    ]
    checkpoint = {
        "experiment_id": EXPERIMENT_ID,
        "status": CHECKPOINT_STATUS,
        "gdt620_binding": copy.deepcopy(GDT620_BINDING),
        "raw_bundle_sha256s": {
            "READER_A": a["bundle_sha256"],
            "READER_B": b["bundle_sha256"],
        },
        "reconciled_latin": reconciled,
        "difference_ledger": ledger,
        "reconciliation_access_audit": {
            "adjudicator_id": "ADJUDICATOR_0011223344556677",
            "session_id": "RECONCILIATION_SESSION_8899AABBCCDDEEFF",
            "started_utc": "2026-08-29T00:13:00Z",
            "completed_utc": "2026-08-29T00:14:00Z",
            "attested_utc": "2026-08-29T00:15:00Z",
            "frozen_reader_a_bundle_sha256": a["bundle_sha256"],
            "frozen_reader_b_bundle_sha256": b["bundle_sha256"],
            "only_frozen_bundles_and_five_latin_jpegs_used": True,
            **{key: 0 for key in ZERO_AUDIT_KEYS},
        },
        "canonicalization": CANONICALIZATION,
        "claim_ceiling": CLAIM_CEILING,
        "checkpoint_sha256": "",
    }
    _seal(checkpoint, "checkpoint_sha256")
    return a, b, checkpoint


def _reseal_fixture(a: dict[str, Any], b: dict[str, Any], checkpoint: dict[str, Any]) -> None:
    _seal(a, "bundle_sha256")
    _seal(b, "bundle_sha256")
    checkpoint["raw_bundle_sha256s"] = {
        "READER_A": a["bundle_sha256"],
        "READER_B": b["bundle_sha256"],
    }
    checkpoint["reconciliation_access_audit"]["frozen_reader_a_bundle_sha256"] = a[
        "bundle_sha256"
    ]
    checkpoint["reconciliation_access_audit"]["frozen_reader_b_bundle_sha256"] = b[
        "bundle_sha256"
    ]
    _seal(checkpoint, "checkpoint_sha256")


def _bytes_fixture(
    fixture: tuple[dict[str, Any], dict[str, Any], dict[str, Any]]
) -> tuple[bytes, bytes, bytes]:
    return tuple(_canonical_bytes(item) for item in fixture)  # type: ignore[return-value]


def run_selftest() -> int:
    """Exercise accept/reject cases entirely in memory."""

    cases_run = 0
    failures: list[str] = []

    def expect_accept(
        name: str,
        builder: Callable[[], tuple[dict[str, Any], dict[str, Any], dict[str, Any]]],
    ) -> None:
        nonlocal cases_run
        cases_run += 1
        try:
            validate_artifact_bytes(*_bytes_fixture(builder()))
        except Exception as exc:  # self-test must report internal regressions too
            failures.append(f"{name}: unexpectedly rejected ({type(exc).__name__})")

    def expect_reject(
        name: str,
        mutate: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], None],
        *,
        reseal: bool = True,
        with_difference: bool = False,
    ) -> None:
        nonlocal cases_run
        cases_run += 1
        a, b, checkpoint = _synthetic_fixture(with_difference=with_difference)
        mutate(a, b, checkpoint)
        if reseal:
            try:
                _reseal_fixture(a, b, checkpoint)
            except ValidationError:
                pass
        try:
            validate_artifact_bytes(*_bytes_fixture((a, b, checkpoint)))
        except ValidationError:
            return
        except Exception as exc:
            failures.append(f"{name}: validator crashed ({type(exc).__name__})")
            return
        failures.append(f"{name}: unexpectedly accepted")

    expect_accept("valid all-agreement checkpoint", _synthetic_fixture)
    expect_accept(
        "valid adjudicated-difference checkpoint",
        lambda: _synthetic_fixture(with_difference=True),
    )

    def nullable_difference_fixture(
        absent_side: str,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        a, b, checkpoint = _synthetic_fixture(with_difference=True)
        row = checkpoint["difference_ledger"][0]
        row[absent_side] = None
        row["reconciled_reading"] = None
        _reseal_fixture(a, b, checkpoint)
        return a, b, checkpoint

    expect_accept(
        "difference permits null Reader B and reconciled absence",
        lambda: nullable_difference_fixture("reader_b"),
    )
    expect_accept(
        "difference permits null Reader A and reconciled absence",
        lambda: nullable_difference_fixture("reader_a"),
    )

    def equal_position_fixture(
        *, by_boundary_field: bool
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        a, b, checkpoint = _synthetic_fixture(with_difference=True)
        row = checkpoint["difference_ledger"][0]
        row["reader_b"] = row["reader_a"]
        row["position"] = "reader_a_token_6|reader_b_token_7"
        if by_boundary_field:
            row["field"] = "token_boundaries"
            row["difference_type"] = "TOKEN_BOUNDARY_DIFFERENCE"
        else:
            row["difference_type"] = "TOKEN_POSITION_SHIFT"
        _reseal_fixture(a, b, checkpoint)
        return a, b, checkpoint

    expect_accept(
        "equal forms allowed for explicit position shift",
        lambda: equal_position_fixture(by_boundary_field=False),
    )
    expect_accept(
        "equal forms allowed for token-boundary field",
        lambda: equal_position_fixture(by_boundary_field=True),
    )

    def unicode_fixture() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        a, b, checkpoint = _synthetic_fixture()
        for bundle in (a, b):
            bundle["pages"][0]["heading_or_rubric"] = "SYNTHETIC_e\u0301"
            bundle["pages"][0]["diplomatic_stream"] = (
                "SYNTHETIC_e\u0301 " + " ".join(bundle["pages"][0]["tokens_1_through_12"])
            )
        checkpoint["reconciled_latin"][0]["heading_or_rubric"] = "SYNTHETIC_e\u0301"
        checkpoint["reconciled_latin"][0]["diplomatic_stream"] = (
            "SYNTHETIC_e\u0301 "
            + " ".join(checkpoint["reconciled_latin"][0]["tokens_1_through_12"])
        )
        _reseal_fixture(a, b, checkpoint)
        return a, b, checkpoint

    expect_accept("exact non-normalized Unicode preserved", unicode_fixture)

    def notation_fixture() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        a, b, checkpoint = _synthetic_fixture()
        for bundle in (a, b):
            page = bundle["pages"][0]
            page["heading_or_rubric"] = "<SIGN:SYNTHETIC_RUBRIC>"
            page["tokens_1_through_12"][0] = "<UNCERTAIN:x>"
            page["tokens_1_through_12"][1] = "<UNREADABLE>"
            page["diplomatic_stream"] = (
                page["heading_or_rubric"] + " " + " ".join(page["tokens_1_through_12"])
            )
            page["uncertainties"] = [
                {"note": "synthetic note", "position": "token:1"}
            ]
        checkpoint["reconciled_latin"][0] = {
            key: copy.deepcopy(a["pages"][0][key]) for key in READING_KEYS
        }
        _reseal_fixture(a, b, checkpoint)
        return a, b, checkpoint

    expect_accept("registered tags and structured uncertainty note", notation_fixture)

    def composed_tag_fixture() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        a, b, checkpoint = _synthetic_fixture()
        composed_tokens = (
            "<UNCERTAIN:eod<SIGN:OVERBAR>.>",
            "<UNCERTAIN:ij<SIGN:SUPERSCRIPT-O>.>",
        )
        for bundle in (a, b):
            page = bundle["pages"][0]
            page["tokens_1_through_12"][0:2] = composed_tokens
            page["diplomatic_stream"] = (
                page["heading_or_rubric"] + " " + " ".join(page["tokens_1_through_12"])
            )
        checkpoint["reconciled_latin"][0] = {
            key: copy.deepcopy(a["pages"][0][key]) for key in READING_KEYS
        }
        _reseal_fixture(a, b, checkpoint)
        return a, b, checkpoint

    expect_accept("one-level SIGN components inside UNCERTAIN", composed_tag_fixture)

    reject_cases: list[
        tuple[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], None], bool, bool]
    ] = [
        ("raw unexpected top key", lambda a, b, c: a.__setitem__("extra", True), True, False),
        ("raw wrong reader", lambda a, b, c: a.__setitem__("reader_id", "READER_B"), True, False),
        ("raw bad session pattern", lambda a, b, c: a.__setitem__("session_id", "SESSION_A_bad"), True, False),
        ("raw page count", lambda a, b, c: a["pages"].pop(), True, False),
        ("raw page order", lambda a, b, c: a["pages"].reverse(), True, False),
        ("raw source hash", lambda a, b, c: a["pages"][0].__setitem__("source_sha256", "0" * 64), True, False),
        ("recursive page hash", lambda a, b, c: a["pages"][0].__setitem__("submission_sha256", "0" * 64), True, False),
        ("full page false", lambda a, b, c: a["pages"][0].__setitem__("full_page_viewed_first", False), True, False),
        ("eleven tokens", lambda a, b, c: a["pages"][0]["tokens_1_through_12"].pop(), True, False),
        ("whitespace in token", lambda a, b, c: a["pages"][0]["tokens_1_through_12"].__setitem__(0, "two words"), True, False),
        ("stream mismatch", lambda a, b, c: a["pages"][0].__setitem__("diplomatic_stream", "mismatch stream"), True, False),
        ("unregistered tag", lambda a, b, c: a["pages"][0].__setitem__("heading_or_rubric", "<GUESS:x>"), True, False),
        ("nested uncertain tag", lambda a, b, c: a["pages"][0].__setitem__("heading_or_rubric", "<UNCERTAIN:x<UNCERTAIN:y>>"), True, False),
        ("unregistered nested tag", lambda a, b, c: a["pages"][0].__setitem__("heading_or_rubric", "<UNCERTAIN:x<GUESS:y>>"), True, False),
        ("whitespace in nested sign", lambda a, b, c: a["pages"][0].__setitem__("heading_or_rubric", "<UNCERTAIN:x<SIGN:OVER BAR>.>"), True, False),
        ("empty uncertain payload", lambda a, b, c: a["pages"][0].__setitem__("heading_or_rubric", "<UNCERTAIN:>"), True, False),
        ("malformed composed tag", lambda a, b, c: a["pages"][0].__setitem__("heading_or_rubric", "<UNCERTAIN:x<SIGN:OVERBAR>."), True, False),
        ("duplicate rendering session", lambda a, b, c: a["pages"][1].__setitem__("rendering_session_id", a["pages"][0]["rendering_session_id"]), True, False),
        ("cross-reader rendering session reuse", lambda a, b, c: b["pages"][0].__setitem__("rendering_session_id", a["pages"][0]["rendering_session_id"]), True, False),
        ("duplicate audit reference", lambda a, b, c: a["pages"][1].__setitem__("access_audit_ref", a["pages"][0]["access_audit_ref"]), True, False),
        ("page after bundle", lambda a, b, c: a["pages"][4].__setitem__("submitted_utc", "2026-08-29T00:20:00Z"), True, False),
        ("reader order violation", lambda a, b, c: b["pages"][0].__setitem__("submitted_utc", "2026-08-29T00:05:00Z"), True, False),
        ("absolute path privacy", lambda a, b, c: a["pages"][0].__setitem__("heading_or_rubric", "/private/source"), True, False),
        ("image filename privacy", lambda a, b, c: a["pages"][0].__setitem__("heading_or_rubric", "private.jpg"), True, False),
        ("image bytes privacy", lambda a, b, c: a["pages"][0].__setitem__("heading_or_rubric", "data:image/jpeg;base64,/9j/AAAA"), True, False),
        ("checkpoint unexpected key", lambda a, b, c: c.__setitem__("extra", None), True, False),
        ("checkpoint status", lambda a, b, c: c.__setitem__("status", "MANUAL_READING_STOP"), True, False),
        ("binding mismatch", lambda a, b, c: c["gdt620_binding"].__setitem__("gdt620_result_sha256", "0" * 64), True, False),
        ("canonicalization string mismatch", lambda a, b, c: c.__setitem__("canonicalization", "JSON"), True, False),
        ("claim ceiling mismatch", lambda a, b, c: c.__setitem__("claim_ceiling", "SYNTHETIC"), True, False),
        ("checkpoint raw hash not reused", lambda a, b, c: (c["raw_bundle_sha256s"].__setitem__("READER_A", "0" * 64), _seal(c, "checkpoint_sha256")), False, False),
        ("reconciled count", lambda a, b, c: c["reconciled_latin"].pop(), True, False),
        ("reconciled order", lambda a, b, c: c["reconciled_latin"].reverse(), True, False),
        ("reconciled unexpected key", lambda a, b, c: c["reconciled_latin"][0].__setitem__("extra", True), True, False),
        ("audit unexpected key", lambda a, b, c: c["reconciliation_access_audit"].__setitem__("extra", True), True, False),
        ("audit nonaccess nonzero", lambda a, b, c: c["reconciliation_access_audit"].__setitem__("network_access_count", 1), True, False),
        ("audit bool masquerading as zero", lambda a, b, c: c["reconciliation_access_audit"].__setitem__("network_access_count", False), True, False),
        ("audit false allowed-input attestation", lambda a, b, c: c["reconciliation_access_audit"].__setitem__("only_frozen_bundles_and_five_latin_jpegs_used", False), True, False),
        ("audit starts before freeze", lambda a, b, c: c["reconciliation_access_audit"].__setitem__("started_utc", "2026-08-29T00:11:00Z"), True, False),
        ("audit bad adjudicator", lambda a, b, c: c["reconciliation_access_audit"].__setitem__("adjudicator_id", "ADJUDICATOR_bad"), True, False),
        ("audit frozen hash not reused", lambda a, b, c: (c["reconciliation_access_audit"].__setitem__("frozen_reader_a_bundle_sha256", "0" * 64), _seal(c, "checkpoint_sha256")), False, False),
        ("ledger missing page", lambda a, b, c: c["difference_ledger"].pop(), True, False),
        ("ledger page order", lambda a, b, c: c["difference_ledger"].reverse(), True, False),
        ("sentinel nonnull", lambda a, b, c: c["difference_ledger"][0].__setitem__("position", 0), True, False),
        ("sentinel on difference", lambda a, b, c: b["pages"][0]["tokens_1_through_12"].__setitem__(0, "variant"), True, False),
        ("agreed value changed", lambda a, b, c: c["reconciled_latin"][0]["tokens_1_through_12"].__setitem__(0, "changed"), True, False),
        ("difference wrong adjudicator", lambda a, b, c: c["difference_ledger"][0].__setitem__("adjudicator", "ADJUDICATOR_FFFFFFFFFFFFFFFF"), True, True),
        ("difference both-null forms", lambda a, b, c: c["difference_ledger"][0].update({"reader_a": None, "reader_b": None}), True, True),
        ("difference both-empty forms", lambda a, b, c: c["difference_ledger"][0].update({"reader_a": "", "reader_b": ""}), True, True),
        ("difference null-and-empty forms", lambda a, b, c: c["difference_ledger"][0].update({"reader_a": None, "reader_b": ""}), True, True),
        ("difference equal forms", lambda a, b, c: c["difference_ledger"][0].__setitem__("reader_b", c["difference_ledger"][0]["reader_a"]), True, True),
        ("equal position shift same ordinal", lambda a, b, c: c["difference_ledger"][0].update({"reader_b": c["difference_ledger"][0]["reader_a"], "difference_type": "TOKEN_POSITION_SHIFT", "position": "reader_a_token_6|reader_b_token_6"}), True, True),
        ("equal position shift integer descriptor", lambda a, b, c: c["difference_ledger"][0].update({"reader_b": c["difference_ledger"][0]["reader_a"], "difference_type": "TOKEN_POSITION_SHIFT", "position": 7}), True, True),
        ("equal boundary row empty resolution", lambda a, b, c: c["difference_ledger"][0].update({"reader_b": c["difference_ledger"][0]["reader_a"], "field": "token_boundaries", "position": "reader_a_token_6|reader_b_token_7", "resolution_reason": ""}), True, True),
        ("difference resolved after completion", lambda a, b, c: c["difference_ledger"][0].__setitem__("resolved_utc", "2026-08-29T00:20:00Z"), True, True),
        ("bundle hash mismatch", lambda a, b, c: a.__setitem__("bundle_sha256", "0" * 64), False, False),
        ("checkpoint hash mismatch", lambda a, b, c: c.__setitem__("checkpoint_sha256", "0" * 64), False, False),
    ]
    for name, mutate, reseal, with_difference in reject_cases:
        expect_reject(name, mutate, reseal=reseal, with_difference=with_difference)

    # Byte-level canonicalization and parser rejection cases cannot be expressed
    # as object mutations because canonical serialization repairs them.
    cases_run += 1
    a, b, checkpoint = _bytes_fixture(_synthetic_fixture())
    pretty_a = json.dumps(json.loads(a), ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    try:
        validate_artifact_bytes(pretty_a, b, checkpoint)
    except ValidationError:
        pass
    else:
        failures.append("noncanonical JSON bytes: unexpectedly accepted")

    cases_run += 1
    duplicate_a = a.replace(b"{", b'{"reader_id":"READER_A",', 1)
    try:
        validate_artifact_bytes(duplicate_a, b, checkpoint)
    except ValidationError:
        pass
    else:
        failures.append("duplicate JSON key: unexpectedly accepted")

    cases_run += 1
    try:
        validate_artifact_bytes(a[:-1], b, checkpoint)
    except ValidationError:
        pass
    else:
        failures.append("missing final LF: unexpectedly accepted")

    if failures:
        for failure in failures:
            print(f"SELFTEST FAIL: {failure}", file=sys.stderr)
        print(f"SELFTEST FAIL: {cases_run - len(failures)}/{cases_run} cases passed", file=sys.stderr)
        return 1
    print(f"SELFTEST PASS: {cases_run}/{cases_run} in-memory cases")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministically validate frozen GDT621 Latin JSON artifacts offline."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check",
        action="store_true",
        help="check the three fixed artifacts/ JSON files",
    )
    mode.add_argument(
        "--selftest",
        action="store_true",
        help="run accept/reject tests entirely in memory",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    if args.selftest:
        return run_selftest()
    return run_check()


if __name__ == "__main__":
    raise SystemExit(main())
