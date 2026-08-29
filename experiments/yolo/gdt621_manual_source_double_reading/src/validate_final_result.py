#!/usr/bin/env python3
"""Strict offline validator for the canonical GDT621 final result."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable, Mapping, Sequence

try:
    import build_final_result as builder
    import validate_latin_checkpoint as checkpoint_validator
except ImportError:
    from . import build_final_result as builder  # type: ignore[no-redef]
    from . import validate_latin_checkpoint as checkpoint_validator  # type: ignore[no-redef]


class ValidationError(builder.BuildError):
    """A deterministic, value-redacted final-result validation failure."""


CANDIDATE_IDS = ("DEV01", "DEV02", "DEV03", "DEV04", "DEV05")
LATIN_SOURCE_SHA256S = checkpoint_validator.LATIN_SOURCE_SHA256S
CLM_SOURCE_SHA256S = {
    "DEV01": "82b476a028ad94ba7392520a4cba527c9dc521a577207bbec5842d0f7e266c50",
    "DEV02": "e0c56b10b19e823c7b0247881d1cf27a1302cced0bd432956b98c47aab78746f",
    "DEV03": "4d87c0f033236b88abbb0ce6a5fe24a3664d63660080e15e0763642d9444aee0",
    "DEV04": "f5a112fd194f45db72518e1a146f05bd2eec239e346a1b137cba7f1eab24e035",
    "DEV05": "808ff7b43c074ee0e67770cf51d7a38f683254c1a11883bf799bc9deeee1f4a8",
}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
CONTROLLER_RE = re.compile(r"^CONTROLLER_[A-F0-9]{16}$")
CLM_SESSION_RE = re.compile(r"^CLM_SESSION_[A-F0-9]{16}$")
UTC_RE = re.compile(
    r"^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T"
    r"(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})"
    r"(?:\.(?P<fraction>[0-9]{1,9}))?Z$"
)

GLOBAL_COUNT_KEYS = (
    "f84_access_count",
    "f84r_access_count",
    "target_access_count",
    "voynich_access_count",
)
LATIN_AUDIT_KEYS = (
    "created_utc",
    "events",
    "experiment_id",
    "global_required_values",
    "status",
)
LATIN_EVENT_KEYS = (
    "sequence",
    "reader_id",
    "session_id",
    "candidate_id",
    "source_sha256",
    "reader_packet_sha256",
    "reader_packet_exact_keys_verified",
    "opened_utc",
    "closed_utc",
    "attested_utc",
    "full_page_viewed_first",
    "only_opaque_packet_used",
    "profile_not_consulted",
    "repository_not_consulted",
    "catalog_not_consulted",
    "edition_not_consulted",
    "network_not_consulted",
    "other_sources_not_consulted",
    "other_reader_material_not_seen",
    "ocr_or_automation_used",
)
LATIN_TRUE_FIELDS = (
    "reader_packet_exact_keys_verified",
    "full_page_viewed_first",
    "only_opaque_packet_used",
    "profile_not_consulted",
    "repository_not_consulted",
    "catalog_not_consulted",
    "edition_not_consulted",
    "network_not_consulted",
    "other_sources_not_consulted",
    "other_reader_material_not_seen",
)

CLM_TOP_KEYS = (
    "checkpoint_bindings",
    "controller_id",
    "experiment_id",
    "forbidden_sources_or_methods_attestation",
    "global_access_counts",
    "page_observations",
    "session_id",
    "status",
)
CHECKPOINT_BINDING_KEYS = (
    "bindings_attested_before_first_open",
    "canonical_checkpoint_sha256_field",
    "checkpoint_committed_utc",
    "public_checkpoint_commit",
    "public_checkpoint_file_sha256",
)
FORBIDDEN_ATTESTATION_KEYS = (
    "attested",
    "catalogs_accessed",
    "crops_or_derivatives_saved",
    "editions_accessed",
    "files_written",
    "image_recognition_used",
    "latin_source_jpegs_accessed",
    "network_accessed",
    "ocr_used",
    "other_agents_accessed",
    "repository_accessed",
    "running_text_transcribed",
)
CLM_OBSERVATION_KEYS = (
    "access_event",
    "notes",
    "visible_rubric_or_locator_label",
)
CLM_EVENT_KEYS = (
    "sequence",
    "controller_id",
    "session_id",
    "candidate_id",
    "source_sha256",
    "checkpoint_committed_utc",
    "opened_utc",
    "closed_utc",
    "attested_utc",
    "full_page_viewed_first",
    "public_checkpoint_commit",
    "public_checkpoint_sha256",
    "public_checkpoint_commit_verified",
    "public_checkpoint_hash_verified",
    "clm_changed_latin",
    "ocr_or_automation_used",
)


def _fail(path: str, message: str) -> None:
    raise ValidationError(f"{path}: {message}")


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
        _fail(
            path,
            f"exact schema mismatch ({len(wanted - actual)} missing, "
            f"{len(actual - wanted)} unexpected keys)",
        )


def _expect_exact(value: Any, expected: Any, path: str) -> None:
    if type(value) is not type(expected) or value != expected:
        _fail(path, "does not equal the registered value")


def _expect_string(value: Any, path: str, *, nonempty: bool = True) -> str:
    if type(value) is not str:
        _fail(path, "must be a string")
    if nonempty and value == "":
        _fail(path, "must be a nonempty string")
    return value


def _expect_pattern(value: Any, pattern: re.Pattern[str], path: str) -> str:
    string = _expect_string(value, path)
    if pattern.fullmatch(string) is None:
        _fail(path, "does not match the registered pattern")
    return string


def _expect_zero_counts(value: Any, path: str) -> dict[str, int]:
    counts = _expect_dict(value, path)
    _expect_exact_keys(counts, GLOBAL_COUNT_KEYS, path)
    for key in GLOBAL_COUNT_KEYS:
        if type(counts[key]) is not int or counts[key] != 0:
            _fail(f"{path}.{key}", "must be integer zero")
    return counts


def _parse_utc(value: Any, path: str) -> tuple[int, int]:
    string = _expect_string(value, path)
    match = UTC_RE.fullmatch(string)
    if match is None:
        _fail(path, "must be an ISO-8601 UTC timestamp with at most 9 fractional digits")
    try:
        base = datetime.strptime(
            f"{match.group('date')}T{match.group('time')}", "%Y-%m-%dT%H:%M:%S"
        ).replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValidationError(f"{path}: invalid UTC calendar timestamp") from exc
    fraction = match.group("fraction") or ""
    nanoseconds = int(fraction.ljust(9, "0")) if fraction else 0
    return (int(base.timestamp()), nanoseconds)


def _json_equal(left: Any, right: Any) -> bool:
    return builder.canonical_bytes(left) == builder.canonical_bytes(right)


def _parse_canonical(data: bytes, label: str) -> dict[str, Any]:
    try:
        return checkpoint_validator._parse_canonical_json(data, label)
    except checkpoint_validator.ValidationError as exc:
        raise ValidationError(str(exc)) from exc


def _parse_structured_source(data: bytes, label: str) -> dict[str, Any]:
    """Parse a noncanonical source JSON without weakening syntax or privacy."""

    if len(data) > builder.MAX_JSON_BYTES:
        _fail(label, "file is too large for a structured JSON artifact")
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
    try:
        checkpoint_validator._validate_privacy(parsed, label)
    except checkpoint_validator.ValidationError as exc:
        raise ValidationError(str(exc)) from exc
    return parsed


def _validate_public_binding(binding: Mapping[str, str], path: str) -> None:
    _expect_exact_keys(binding, builder.PUBLIC_CHECKPOINT_BINDING.keys(), path)
    _expect_pattern(binding["public_checkpoint_commit"], COMMIT_RE, f"{path}.public_checkpoint_commit")
    _parse_utc(binding["checkpoint_committed_utc"], f"{path}.checkpoint_committed_utc")
    _expect_pattern(
        binding["canonical_checkpoint_sha256_field"],
        SHA256_RE,
        f"{path}.canonical_checkpoint_sha256_field",
    )
    _expect_pattern(
        binding["public_checkpoint_file_sha256"],
        SHA256_RE,
        f"{path}.public_checkpoint_file_sha256",
    )


def _validate_latin_audit(
    audit_value: Any,
    reader_a: Mapping[str, Any],
    reader_b: Mapping[str, Any],
) -> dict[str, Any]:
    path = "LATIN_READER_ACCESS_AUDIT.json"
    audit = _expect_dict(audit_value, path)
    _expect_exact_keys(audit, LATIN_AUDIT_KEYS, path)
    _expect_exact(audit["experiment_id"], builder.EXPERIMENT_ID, f"{path}.experiment_id")
    _expect_exact(audit["status"], "BOTH_RAW_COMMITMENTS_FROZEN", f"{path}.status")
    created = _parse_utc(audit["created_utc"], f"{path}.created_utc")
    _expect_zero_counts(audit["global_required_values"], f"{path}.global_required_values")

    events = _expect_list(audit["events"], f"{path}.events")
    if len(events) != 10:
        _fail(f"{path}.events", "must contain exactly ten Latin access events")
    latest_attestation = (0, 0)
    for index in range(10):
        event_path = f"{path}.events[{index}]"
        event = _expect_dict(events[index], event_path)
        _expect_exact_keys(event, LATIN_EVENT_KEYS, event_path)
        reader = reader_a if index < 5 else reader_b
        reader_id = "READER_A" if index < 5 else "READER_B"
        reader_letter = "A" if index < 5 else "B"
        page_index = index if index < 5 else index - 5
        candidate_id = CANDIDATE_IDS[page_index]
        raw_page = reader["pages"][page_index]

        _expect_exact(event["sequence"], index + 1, f"{event_path}.sequence")
        _expect_exact(event["reader_id"], reader_id, f"{event_path}.reader_id")
        _expect_exact(event["session_id"], reader["session_id"], f"{event_path}.session_id")
        _expect_exact(event["candidate_id"], candidate_id, f"{event_path}.candidate_id")
        _expect_exact(
            event["source_sha256"],
            LATIN_SOURCE_SHA256S[candidate_id],
            f"{event_path}.source_sha256",
        )
        _expect_pattern(event["reader_packet_sha256"], SHA256_RE, f"{event_path}.reader_packet_sha256")
        expected_ref = f"LATIN_EVENT_{reader_letter}_{page_index + 1:02d}"
        _expect_exact(raw_page["access_audit_ref"], expected_ref, f"raw.{reader_id}.{candidate_id}.access_audit_ref")
        for key in LATIN_TRUE_FIELDS:
            if event[key] is not True:
                _fail(f"{event_path}.{key}", "must be exactly true")
        if event["ocr_or_automation_used"] is not False:
            _fail(f"{event_path}.ocr_or_automation_used", "must be exactly false")

        opened = _parse_utc(event["opened_utc"], f"{event_path}.opened_utc")
        closed = _parse_utc(event["closed_utc"], f"{event_path}.closed_utc")
        attested = _parse_utc(event["attested_utc"], f"{event_path}.attested_utc")
        if not opened <= closed <= attested:
            _fail(event_path, "timestamps must satisfy opened <= closed <= attested")
        _expect_exact(
            event["attested_utc"], raw_page["submitted_utc"], f"{event_path}.attested_utc"
        )
        latest_attestation = max(latest_attestation, attested)
    if created < latest_attestation:
        _fail(f"{path}.created_utc", "must not precede any Latin event attestation")
    _expect_exact(audit["created_utc"], reader_b["submitted_utc"], f"{path}.created_utc")
    return audit


def _validate_forbidden_attestation(value: Any, path: str) -> dict[str, Any]:
    attestation = _expect_dict(value, path)
    _expect_exact_keys(attestation, FORBIDDEN_ATTESTATION_KEYS, path)
    if attestation["attested"] is not True:
        _fail(f"{path}.attested", "must be exactly true")
    for key in FORBIDDEN_ATTESTATION_KEYS[1:]:
        if attestation[key] is not False:
            _fail(f"{path}.{key}", "must be exactly false")
    return attestation


def _validate_clm_observations(
    value: Any,
    checkpoint: Mapping[str, Any],
    checkpoint_file_sha256: str,
    binding: Mapping[str, str],
) -> dict[str, Any]:
    path = "CLM_CONTROL_OBSERVATIONS.json"
    clm = _expect_dict(value, path)
    _expect_exact_keys(clm, CLM_TOP_KEYS, path)
    _expect_exact(clm["experiment_id"], builder.EXPERIMENT_ID, f"{path}.experiment_id")
    _expect_exact(
        clm["status"],
        "CLM_CONTROL_COMPLETE__LATIN_UNCHANGED__TARGET_UNOPENED",
        f"{path}.status",
    )
    controller = _expect_pattern(clm["controller_id"], CONTROLLER_RE, f"{path}.controller_id")
    session = _expect_pattern(clm["session_id"], CLM_SESSION_RE, f"{path}.session_id")

    bindings = _expect_dict(clm["checkpoint_bindings"], f"{path}.checkpoint_bindings")
    _expect_exact_keys(bindings, CHECKPOINT_BINDING_KEYS, f"{path}.checkpoint_bindings")
    if bindings["bindings_attested_before_first_open"] is not True:
        _fail(
            f"{path}.checkpoint_bindings.bindings_attested_before_first_open",
            "must be exactly true",
        )
    for key in (
        "canonical_checkpoint_sha256_field",
        "checkpoint_committed_utc",
        "public_checkpoint_commit",
        "public_checkpoint_file_sha256",
    ):
        _expect_exact(bindings[key], binding[key], f"{path}.checkpoint_bindings.{key}")
    _expect_exact(
        checkpoint["checkpoint_sha256"],
        binding["canonical_checkpoint_sha256_field"],
        "checkpoint.checkpoint_sha256",
    )
    _expect_exact(
        checkpoint_file_sha256,
        binding["public_checkpoint_file_sha256"],
        "checkpoint.file_sha256",
    )

    _validate_forbidden_attestation(
        clm["forbidden_sources_or_methods_attestation"],
        f"{path}.forbidden_sources_or_methods_attestation",
    )
    _expect_zero_counts(clm["global_access_counts"], f"{path}.global_access_counts")

    observations = _expect_list(clm["page_observations"], f"{path}.page_observations")
    if len(observations) != 5:
        _fail(f"{path}.page_observations", "must contain exactly five Clm observations")
    commit_time = _parse_utc(
        binding["checkpoint_committed_utc"], "public_binding.checkpoint_committed_utc"
    )
    previous_opened: tuple[int, int] | None = None
    for index, candidate_id in enumerate(CANDIDATE_IDS):
        observation_path = f"{path}.page_observations[{index}]"
        observation = _expect_dict(observations[index], observation_path)
        _expect_exact_keys(observation, CLM_OBSERVATION_KEYS, observation_path)
        _expect_string(
            observation["visible_rubric_or_locator_label"],
            f"{observation_path}.visible_rubric_or_locator_label",
        )
        _expect_string(observation["notes"], f"{observation_path}.notes")
        event_path = f"{observation_path}.access_event"
        event = _expect_dict(observation["access_event"], event_path)
        _expect_exact_keys(event, CLM_EVENT_KEYS, event_path)
        _expect_exact(event["sequence"], index + 1, f"{event_path}.sequence")
        _expect_exact(event["controller_id"], controller, f"{event_path}.controller_id")
        _expect_exact(event["session_id"], session, f"{event_path}.session_id")
        _expect_exact(event["candidate_id"], candidate_id, f"{event_path}.candidate_id")
        _expect_exact(
            event["source_sha256"], CLM_SOURCE_SHA256S[candidate_id], f"{event_path}.source_sha256"
        )
        _expect_exact(
            event["checkpoint_committed_utc"],
            binding["checkpoint_committed_utc"],
            f"{event_path}.checkpoint_committed_utc",
        )
        _expect_exact(
            event["public_checkpoint_commit"],
            binding["public_checkpoint_commit"],
            f"{event_path}.public_checkpoint_commit",
        )
        _expect_exact(
            event["public_checkpoint_sha256"],
            binding["canonical_checkpoint_sha256_field"],
            f"{event_path}.public_checkpoint_sha256",
        )
        for key in (
            "full_page_viewed_first",
            "public_checkpoint_commit_verified",
            "public_checkpoint_hash_verified",
        ):
            if event[key] is not True:
                _fail(f"{event_path}.{key}", "must be exactly true")
        for key in ("clm_changed_latin", "ocr_or_automation_used"):
            if event[key] is not False:
                _fail(f"{event_path}.{key}", "must be exactly false")
        opened = _parse_utc(event["opened_utc"], f"{event_path}.opened_utc")
        closed = _parse_utc(event["closed_utc"], f"{event_path}.closed_utc")
        attested = _parse_utc(event["attested_utc"], f"{event_path}.attested_utc")
        if not commit_time < opened:
            _fail(f"{event_path}.opened_utc", "must be strictly later than checkpoint commit")
        if not opened <= closed <= attested:
            _fail(event_path, "timestamps must satisfy opened <= closed <= attested")
        if previous_opened is not None and opened <= previous_opened:
            _fail(f"{event_path}.opened_utc", "Clm events must follow registered page order")
        previous_opened = opened
    return clm


def validate_source_bytes(
    reader_a_bytes: bytes,
    reader_b_bytes: bytes,
    checkpoint_bytes: bytes,
    latin_audit_bytes: bytes,
    clm_observation_bytes: bytes,
    binding: Mapping[str, str] = builder.PUBLIC_CHECKPOINT_BINDING,
) -> dict[str, Any]:
    _validate_public_binding(binding, "public_binding")
    try:
        checkpoint_validator.validate_artifact_bytes(
            reader_a_bytes, reader_b_bytes, checkpoint_bytes
        )
    except checkpoint_validator.ValidationError as exc:
        raise ValidationError(str(exc)) from exc

    reader_a = _parse_canonical(reader_a_bytes, "LATIN_READER_A_RAW.json")
    reader_b = _parse_canonical(reader_b_bytes, "LATIN_READER_B_RAW.json")
    checkpoint = _parse_canonical(checkpoint_bytes, "LATIN_RECONCILIATION_FROZEN.json")
    latin_audit = _parse_canonical(latin_audit_bytes, "LATIN_READER_ACCESS_AUDIT.json")
    clm = _parse_structured_source(
        clm_observation_bytes, "CLM_CONTROL_OBSERVATIONS.json"
    )
    checkpoint_file_sha256 = hashlib.sha256(checkpoint_bytes).hexdigest()

    _expect_exact(
        checkpoint["checkpoint_sha256"],
        binding["canonical_checkpoint_sha256_field"],
        "checkpoint.checkpoint_sha256",
    )
    _expect_exact(
        checkpoint_file_sha256,
        binding["public_checkpoint_file_sha256"],
        "checkpoint.file_sha256",
    )
    _validate_latin_audit(latin_audit, reader_a, reader_b)
    _validate_clm_observations(clm, checkpoint, checkpoint_file_sha256, binding)
    if not _json_equal(
        latin_audit["global_required_values"], clm["global_access_counts"]
    ):
        _fail("global_access_counts", "Latin and Clm zero-count maps differ")
    return {
        "reader_a": reader_a,
        "reader_b": reader_b,
        "checkpoint": checkpoint,
        "latin_access_audit": latin_audit,
        "clm_observations": clm,
        "checkpoint_file_sha256": checkpoint_file_sha256,
    }


def load_validated_sources(
    binding: Mapping[str, str] = builder.PUBLIC_CHECKPOINT_BINDING,
) -> dict[str, Any]:
    paths = builder.artifact_paths()
    payloads = {name: builder.read_fixed_file(path) for name, path in paths.items()}
    return validate_source_bytes(
        payloads["reader_a"],
        payloads["reader_b"],
        payloads["checkpoint"],
        payloads["latin_access_audit"],
        payloads["clm_observations"],
        binding,
    )


def _validate_clm_projection(value: Any, sources: Mapping[str, Any], path: str) -> None:
    rows = _expect_list(value, path)
    if len(rows) != 5:
        _fail(path, "must contain exactly five projected Clm observations")
    source_rows = sources["clm_observations"]["page_observations"]
    for index, candidate_id in enumerate(CANDIDATE_IDS):
        row_path = f"{path}[{index}]"
        row = _expect_dict(rows[index], row_path)
        _expect_exact_keys(row, builder.FINAL_CLM_OBSERVATION_KEYS, row_path)
        event = source_rows[index]["access_event"]
        expected = {
            "candidate_id": candidate_id,
            "source_sha256": CLM_SOURCE_SHA256S[candidate_id],
            "visible_rubric_or_locator_label": source_rows[index][
                "visible_rubric_or_locator_label"
            ],
            "notes": source_rows[index]["notes"],
        }
        if not _json_equal(row, expected):
            _fail(row_path, "does not exactly project the registered Clm observation")
        _expect_exact(row["candidate_id"], event["candidate_id"], f"{row_path}.candidate_id")


def validate_final_result_bytes(
    data: bytes,
    sources: Mapping[str, Any],
    binding: Mapping[str, str] = builder.PUBLIC_CHECKPOINT_BINDING,
) -> dict[str, Any]:
    path = builder.RESULT_FILENAME
    result = _parse_canonical(data, path)
    _expect_exact_keys(result, builder.RESULT_KEYS, path)
    _expect_exact(result["schema_version"], builder.SCHEMA_VERSION, f"{path}.schema_version")
    _expect_exact(result["experiment_id"], builder.EXPERIMENT_ID, f"{path}.experiment_id")
    _expect_exact(result["status"], builder.FINAL_STATUS, f"{path}.status")
    _expect_exact(result["canonicalization"], builder.CANONICALIZATION, f"{path}.canonicalization")
    _expect_exact(result["claim_ceiling"], builder.CLAIM_CEILING, f"{path}.claim_ceiling")

    checkpoint = sources["checkpoint"]
    exact_copies = (
        ("dependency", checkpoint["gdt620_binding"]),
        ("reader_submissions", checkpoint["raw_bundle_sha256s"]),
        ("difference_ledger", checkpoint["difference_ledger"]),
        ("reconciled_latin", checkpoint["reconciled_latin"]),
    )
    for key, expected in exact_copies:
        if not _json_equal(result[key], expected):
            _fail(f"{path}.{key}", "is not an exact canonical deep copy of the checkpoint")

    _validate_clm_projection(result["clm_control"], sources, f"{path}.clm_control")
    access = _expect_dict(result["access_audit"], f"{path}.access_audit")
    _expect_exact_keys(access, builder.FINAL_ACCESS_AUDIT_KEYS, f"{path}.access_audit")
    expected_access = {
        "latin_events": sources["latin_access_audit"]["events"],
        "clm_events": [
            row["access_event"]
            for row in sources["clm_observations"]["page_observations"]
        ],
        "forbidden_sources_or_methods_attestation": sources["clm_observations"][
            "forbidden_sources_or_methods_attestation"
        ],
        "global_access_counts": sources["clm_observations"]["global_access_counts"],
    }
    if not _json_equal(access, expected_access):
        _fail(f"{path}.access_audit", "does not exactly combine the registered access records")
    if len(access["latin_events"]) != 10 or len(access["clm_events"]) != 5:
        _fail(f"{path}.access_audit", "must contain exactly 10 Latin and 5 Clm events")
    _expect_zero_counts(
        access["global_access_counts"], f"{path}.access_audit.global_access_counts"
    )
    _validate_forbidden_attestation(
        access["forbidden_sources_or_methods_attestation"],
        f"{path}.access_audit.forbidden_sources_or_methods_attestation",
    )

    _expect_exact(
        result["latin_checkpoint_public_commit"],
        binding["public_checkpoint_commit"],
        f"{path}.latin_checkpoint_public_commit",
    )
    _expect_exact(
        result["latin_checkpoint_sha256"],
        binding["canonical_checkpoint_sha256_field"],
        f"{path}.latin_checkpoint_sha256",
    )
    _expect_exact(
        result["latin_checkpoint_file_sha256"],
        binding["public_checkpoint_file_sha256"],
        f"{path}.latin_checkpoint_file_sha256",
    )
    result_sha = _expect_pattern(result["result_sha256"], SHA256_RE, f"{path}.result_sha256")
    if result_sha != builder.sha256_without(result, "result_sha256"):
        _fail(f"{path}.result_sha256", "nonrecursive result SHA-256 mismatch")

    expected_bytes = builder.build_result_bytes(sources, binding)
    if data != expected_bytes:
        _fail(path, "does not byte-equal deterministic builder output")
    return {"object": result, "result_sha256": result_sha}


def _shift_utc(value: str, seconds: int) -> str:
    parsed = datetime.fromisoformat(value[:-1] + "+00:00") + timedelta(seconds=seconds)
    return parsed.isoformat(timespec="seconds").replace("+00:00", "Z")


def _synthetic_latin_audit(
    reader_a: Mapping[str, Any], reader_b: Mapping[str, Any]
) -> dict[str, Any]:
    events = []
    for index in range(10):
        reader = reader_a if index < 5 else reader_b
        reader_id = "READER_A" if index < 5 else "READER_B"
        page_index = index if index < 5 else index - 5
        page = reader["pages"][page_index]
        attested = page["submitted_utc"]
        events.append(
            {
                "sequence": index + 1,
                "reader_id": reader_id,
                "session_id": reader["session_id"],
                "candidate_id": page["candidate_id"],
                "source_sha256": page["source_sha256"],
                "reader_packet_sha256": hashlib.sha256(
                    f"synthetic-packet-{index}".encode("ascii")
                ).hexdigest(),
                "reader_packet_exact_keys_verified": True,
                "opened_utc": _shift_utc(attested, -20),
                "closed_utc": _shift_utc(attested, -10),
                "attested_utc": attested,
                "full_page_viewed_first": True,
                "only_opaque_packet_used": True,
                "profile_not_consulted": True,
                "repository_not_consulted": True,
                "catalog_not_consulted": True,
                "edition_not_consulted": True,
                "network_not_consulted": True,
                "other_sources_not_consulted": True,
                "other_reader_material_not_seen": True,
                "ocr_or_automation_used": False,
            }
        )
    return {
        "created_utc": reader_b["submitted_utc"],
        "events": events,
        "experiment_id": builder.EXPERIMENT_ID,
        "global_required_values": {key: 0 for key in GLOBAL_COUNT_KEYS},
        "status": "BOTH_RAW_COMMITMENTS_FROZEN",
    }


def _synthetic_clm(binding: Mapping[str, str]) -> dict[str, Any]:
    controller = "CONTROLLER_0123456789ABCDEF"
    session = "CLM_SESSION_FEDCBA9876543210"
    observations = []
    for index, candidate_id in enumerate(CANDIDATE_IDS):
        minute = index + 1
        opened = f"2026-08-29T01:{minute:02d}:00.123456789Z"
        observations.append(
            {
                "access_event": {
                    "sequence": index + 1,
                    "controller_id": controller,
                    "session_id": session,
                    "candidate_id": candidate_id,
                    "source_sha256": CLM_SOURCE_SHA256S[candidate_id],
                    "checkpoint_committed_utc": binding["checkpoint_committed_utc"],
                    "opened_utc": opened,
                    "closed_utc": f"2026-08-29T01:{minute:02d}:10.223456789Z",
                    "attested_utc": f"2026-08-29T01:{minute:02d}:11.323456789Z",
                    "full_page_viewed_first": True,
                    "public_checkpoint_commit": binding["public_checkpoint_commit"],
                    "public_checkpoint_sha256": binding[
                        "canonical_checkpoint_sha256_field"
                    ],
                    "public_checkpoint_commit_verified": True,
                    "public_checkpoint_hash_verified": True,
                    "clm_changed_latin": False,
                    "ocr_or_automation_used": False,
                },
                "notes": f"synthetic observation notes {candidate_id}",
                "visible_rubric_or_locator_label": f"SYNTHETIC_LABEL_{candidate_id}",
            }
        )
    return {
        "checkpoint_bindings": {
            "bindings_attested_before_first_open": True,
            **copy.deepcopy(binding),
        },
        "controller_id": controller,
        "experiment_id": builder.EXPERIMENT_ID,
        "forbidden_sources_or_methods_attestation": {
            "attested": True,
            **{key: False for key in FORBIDDEN_ATTESTATION_KEYS[1:]},
        },
        "global_access_counts": {key: 0 for key in GLOBAL_COUNT_KEYS},
        "page_observations": observations,
        "session_id": session,
        "status": "CLM_CONTROL_COMPLETE__LATIN_UNCHANGED__TARGET_UNOPENED",
    }


def _synthetic_source_objects() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]
]:
    reader_a, reader_b, checkpoint = checkpoint_validator._synthetic_fixture(
        with_difference=True
    )
    checkpoint_bytes = checkpoint_validator._canonical_bytes(checkpoint)
    binding = {
        "public_checkpoint_commit": "a" * 40,
        "checkpoint_committed_utc": "2026-08-29T01:00:00Z",
        "canonical_checkpoint_sha256_field": checkpoint["checkpoint_sha256"],
        "public_checkpoint_file_sha256": hashlib.sha256(checkpoint_bytes).hexdigest(),
    }
    latin_audit = _synthetic_latin_audit(reader_a, reader_b)
    clm = _synthetic_clm(binding)
    return reader_a, reader_b, checkpoint, latin_audit, clm, binding


def _validate_synthetic_objects(
    fixture: tuple[
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, str],
    ]
) -> dict[str, Any]:
    reader_a, reader_b, checkpoint, latin_audit, clm, binding = fixture
    return validate_source_bytes(
        checkpoint_validator._canonical_bytes(reader_a),
        checkpoint_validator._canonical_bytes(reader_b),
        checkpoint_validator._canonical_bytes(checkpoint),
        builder.canonical_bytes(latin_audit),
        builder.canonical_bytes(clm),
        binding,
    )


def run_selftest() -> int:
    cases = 0
    failures: list[str] = []

    def accept(name: str, action: Callable[[], None]) -> None:
        nonlocal cases
        cases += 1
        try:
            action()
        except Exception as exc:
            failures.append(f"{name}: unexpectedly rejected ({type(exc).__name__})")

    def reject_source(
        name: str,
        mutate: Callable[
            [dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]],
            None,
        ],
    ) -> None:
        nonlocal cases
        cases += 1
        fixture = _synthetic_source_objects()
        mutate(*fixture)
        try:
            _validate_synthetic_objects(fixture)
        except (ValidationError, checkpoint_validator.ValidationError):
            return
        except Exception as exc:
            failures.append(f"{name}: validator crashed ({type(exc).__name__})")
            return
        failures.append(f"{name}: unexpectedly accepted")

    def reject_result(
        name: str,
        mutate: Callable[[dict[str, Any]], None],
        *,
        reseal: bool = True,
    ) -> None:
        nonlocal cases
        cases += 1
        fixture = _synthetic_source_objects()
        sources = _validate_synthetic_objects(fixture)
        binding = fixture[-1]
        result = builder.build_result_object(sources, binding)
        mutate(result)
        if reseal:
            result["result_sha256"] = builder.sha256_without(result, "result_sha256")
        try:
            validate_final_result_bytes(builder.canonical_bytes(result), sources, binding)
        except ValidationError:
            return
        except Exception as exc:
            failures.append(f"{name}: validator crashed ({type(exc).__name__})")
            return
        failures.append(f"{name}: unexpectedly accepted")

    def valid_source() -> None:
        _validate_synthetic_objects(_synthetic_source_objects())

    def valid_result() -> None:
        fixture = _synthetic_source_objects()
        sources = _validate_synthetic_objects(fixture)
        payload = builder.build_result_bytes(sources, fixture[-1])
        validate_final_result_bytes(payload, sources, fixture[-1])

    def valid_pretty_clm_source() -> None:
        reader_a, reader_b, checkpoint, latin_audit, clm, binding = (
            _synthetic_source_objects()
        )
        pretty_clm = json.dumps(clm, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
        validate_source_bytes(
            checkpoint_validator._canonical_bytes(reader_a),
            checkpoint_validator._canonical_bytes(reader_b),
            checkpoint_validator._canonical_bytes(checkpoint),
            builder.canonical_bytes(latin_audit),
            pretty_clm,
            binding,
        )

    accept("valid source inputs", valid_source)
    accept("valid deterministic final result", valid_result)
    accept("valid structured noncompact Clm input", valid_pretty_clm_source)
    reject_source(
        "Latin event order",
        lambda a, b, c, audit, clm, binding: audit["events"].reverse(),
    )
    reject_source(
        "Latin nonaccess false",
        lambda a, b, c, audit, clm, binding: audit["events"][0].__setitem__(
            "network_not_consulted", False
        ),
    )
    reject_source(
        "Latin event timestamp order",
        lambda a, b, c, audit, clm, binding: audit["events"][0].__setitem__(
            "closed_utc", "2026-08-29T00:00:00Z"
        ),
    )
    reject_source(
        "Clm wrong source hash",
        lambda a, b, c, audit, clm, binding: clm["page_observations"][0][
            "access_event"
        ].__setitem__("source_sha256", "0" * 64),
    )
    reject_source(
        "Clm opened at checkpoint commit",
        lambda a, b, c, audit, clm, binding: clm["page_observations"][0][
            "access_event"
        ].__setitem__("opened_utc", binding["checkpoint_committed_utc"]),
    )
    reject_source(
        "Clm OCR attestation",
        lambda a, b, c, audit, clm, binding: clm[
            "forbidden_sources_or_methods_attestation"
        ].__setitem__("ocr_used", True),
    )
    reject_source(
        "Clm changed Latin",
        lambda a, b, c, audit, clm, binding: clm["page_observations"][0][
            "access_event"
        ].__setitem__("clm_changed_latin", True),
    )
    reject_source(
        "global target access",
        lambda a, b, c, audit, clm, binding: clm["global_access_counts"].__setitem__(
            "target_access_count", 1
        ),
    )
    reject_source(
        "public commit mismatch",
        lambda a, b, c, audit, clm, binding: clm["checkpoint_bindings"].__setitem__(
            "public_checkpoint_commit", "b" * 40
        ),
    )
    reject_source(
        "Clm observation unexpected key",
        lambda a, b, c, audit, clm, binding: clm["page_observations"][0].__setitem__(
            "extra", True
        ),
    )
    reject_result("result unexpected key", lambda result: result.__setitem__("extra", True))
    reject_result(
        "checkpoint ledger changed",
        lambda result: result["difference_ledger"].pop(),
    )
    reject_result(
        "Latin audit event omitted",
        lambda result: result["access_audit"]["latin_events"].pop(),
    )
    reject_result(
        "checkpoint commit changed",
        lambda result: result.__setitem__("latin_checkpoint_public_commit", "b" * 40),
    )
    reject_result(
        "private path in result",
        lambda result: result["clm_control"][0].__setitem__(
            "notes", "".join(("/", "home", "/private/control.jpg"))
        ),
    )
    reject_result(
        "result hash mismatch",
        lambda result: result.__setitem__("result_sha256", "0" * 64),
        reseal=False,
    )

    cases += 1
    fixture = _synthetic_source_objects()
    sources = _validate_synthetic_objects(fixture)
    canonical = builder.build_result_bytes(sources, fixture[-1])
    noncanonical = canonical[:-1]
    try:
        validate_final_result_bytes(noncanonical, sources, fixture[-1])
    except ValidationError:
        pass
    else:
        failures.append("missing final LF: unexpectedly accepted")

    if failures:
        for failure in failures:
            print(f"SELFTEST FAIL: {failure}", file=sys.stderr)
        print(f"SELFTEST FAIL: {cases - len(failures)}/{cases} cases passed", file=sys.stderr)
        return 1
    print(f"SELFTEST PASS: {cases}/{cases} in-memory cases")
    return 0


def run_check() -> int:
    try:
        sources = load_validated_sources(builder.PUBLIC_CHECKPOINT_BINDING)
        payload = builder.read_fixed_file(builder.result_path())
        result = validate_final_result_bytes(
            payload, sources, builder.PUBLIC_CHECKPOINT_BINDING
        )
    except builder.BuildError as exc:
        print(f"CHECK FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        f"CHECK PASS: {builder.RESULT_FILENAME}; "
        f"result_sha256={result['result_sha256']}"
    )
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Strictly validate the offline GDT621 final source-reading result."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="validate the fixed final artifact")
    mode.add_argument(
        "--selftest", action="store_true", help="run focused mutation tests entirely in memory"
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    if args.selftest:
        return run_selftest()
    return run_check()


if __name__ == "__main__":
    raise SystemExit(main())
