#!/usr/bin/env python3
"""Build or byte-check the canonical GDT621 final source-reading result.

The builder is deterministic and offline.  It reads only the five named public
JSON inputs in this experiment and never opens images, follows symlinks, invokes
subprocesses, consults git, or uses a network resource.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping


# When this file is executed directly, let validate_final_result import this
# exact module instance instead of loading a second copy under its file name.
if __name__ == "__main__":
    sys.modules.setdefault("build_final_result", sys.modules[__name__])


SCHEMA_VERSION = 1
EXPERIMENT_ID = "GDT621"
FINAL_STATUS = "SOURCE_DOUBLE_READING_COMPLETE__TARGET_UNOPENED"
CANONICALIZATION = "UTF-8 JSON; sorted keys; compact separators; LF final byte"
CLAIM_CEILING = (
    "MANUAL_SOURCE_READING_PROTOCOL_ONLY__NO_IMAGE_OPENED_AT_REGISTRATION__"
    "NO_VOYNICH_SIGN_WORD_LANGUAGE_PLAINTEXT_PLANT_OR_MEANING"
)

PUBLIC_CHECKPOINT_BINDING = {
    "public_checkpoint_commit": "2ab45096cc2a46fc59f5bf50aa3be12cde022e25",
    "checkpoint_committed_utc": "2026-08-29T09:15:05Z",
    "canonical_checkpoint_sha256_field": (
        "4b56894b3046e7fd4b1695ff81a381022a72bb81f6fd4a8caf1203a54ef27905"
    ),
    "public_checkpoint_file_sha256": (
        "a49236a0803a7bfd133a7e439cce293bf3db3f50e02bdae701f97154624a8f7b"
    ),
}

RESULT_KEYS = (
    "schema_version",
    "experiment_id",
    "status",
    "dependency",
    "reader_submissions",
    "difference_ledger",
    "reconciled_latin",
    "clm_control",
    "access_audit",
    "latin_checkpoint_public_commit",
    "latin_checkpoint_sha256",
    "latin_checkpoint_file_sha256",
    "canonicalization",
    "claim_ceiling",
    "result_sha256",
)
RESULT_PREIMAGE_KEYS = RESULT_KEYS[:-1]
FINAL_ACCESS_AUDIT_KEYS = (
    "latin_events",
    "clm_events",
    "forbidden_sources_or_methods_attestation",
    "global_access_counts",
)
FINAL_CLM_OBSERVATION_KEYS = (
    "candidate_id",
    "source_sha256",
    "visible_rubric_or_locator_label",
    "notes",
)

INPUT_FILENAMES = {
    "reader_a": "LATIN_READER_A_RAW.json",
    "reader_b": "LATIN_READER_B_RAW.json",
    "checkpoint": "LATIN_RECONCILIATION_FROZEN.json",
    "latin_access_audit": "LATIN_READER_ACCESS_AUDIT.json",
    "clm_observations": "CLM_CONTROL_OBSERVATIONS.json",
}
RESULT_FILENAME = "SOURCE_DOUBLE_READING_RESULT.json"
MAX_JSON_BYTES = 8 * 1024 * 1024


class BuildError(Exception):
    """A deterministic, value-redacted build/check failure."""


def canonical_bytes(value: Any) -> bytes:
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
        raise BuildError("value cannot be encoded as canonical UTF-8 JSON") from exc


def sha256_without(value: Mapping[str, Any], own_hash_key: str) -> str:
    if own_hash_key not in value:
        raise BuildError(f"missing own hash field {own_hash_key}")
    preimage = dict(value)
    del preimage[own_hash_key]
    return hashlib.sha256(canonical_bytes(preimage)).hexdigest()


def experiment_root() -> Path:
    return Path(__file__).resolve().parent.parent


def artifact_paths() -> dict[str, Path]:
    artifacts = experiment_root() / "artifacts"
    return {name: artifacts / filename for name, filename in INPUT_FILENAMES.items()}


def result_path() -> Path:
    return experiment_root() / "artifacts" / RESULT_FILENAME


def read_fixed_file(path: Path) -> bytes:
    label = path.name
    if not path.exists():
        raise BuildError(f"{label}: required file is absent")
    if path.is_symlink():
        raise BuildError(f"{label}: symbolic links are forbidden")
    if not path.is_file():
        raise BuildError(f"{label}: required path is not a regular file")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise BuildError(f"{label}: cannot inspect file metadata") from exc
    if size > MAX_JSON_BYTES:
        raise BuildError(f"{label}: file is too large for a compact JSON artifact")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise BuildError(f"{label}: cannot read file") from exc


def build_result_object(
    sources: Mapping[str, Any],
    binding: Mapping[str, str] = PUBLIC_CHECKPOINT_BINDING,
) -> dict[str, Any]:
    checkpoint = sources["checkpoint"]
    latin_audit = sources["latin_access_audit"]
    clm = sources["clm_observations"]

    clm_control = []
    clm_events = []
    for observation in clm["page_observations"]:
        event = observation["access_event"]
        clm_control.append(
            {
                "candidate_id": event["candidate_id"],
                "source_sha256": event["source_sha256"],
                "visible_rubric_or_locator_label": observation[
                    "visible_rubric_or_locator_label"
                ],
                "notes": observation["notes"],
            }
        )
        clm_events.append(copy.deepcopy(event))

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "status": FINAL_STATUS,
        "dependency": copy.deepcopy(checkpoint["gdt620_binding"]),
        "reader_submissions": copy.deepcopy(checkpoint["raw_bundle_sha256s"]),
        "difference_ledger": copy.deepcopy(checkpoint["difference_ledger"]),
        "reconciled_latin": copy.deepcopy(checkpoint["reconciled_latin"]),
        "clm_control": clm_control,
        "access_audit": {
            "latin_events": copy.deepcopy(latin_audit["events"]),
            "clm_events": clm_events,
            "forbidden_sources_or_methods_attestation": copy.deepcopy(
                clm["forbidden_sources_or_methods_attestation"]
            ),
            "global_access_counts": copy.deepcopy(clm["global_access_counts"]),
        },
        "latin_checkpoint_public_commit": binding["public_checkpoint_commit"],
        "latin_checkpoint_sha256": binding["canonical_checkpoint_sha256_field"],
        "latin_checkpoint_file_sha256": binding["public_checkpoint_file_sha256"],
        "canonicalization": CANONICALIZATION,
        "claim_ceiling": CLAIM_CEILING,
        "result_sha256": "0" * 64,
    }
    result["result_sha256"] = sha256_without(result, "result_sha256")
    return result


def build_result_bytes(
    sources: Mapping[str, Any],
    binding: Mapping[str, str] = PUBLIC_CHECKPOINT_BINDING,
) -> bytes:
    return canonical_bytes(build_result_object(sources, binding))


def _validator_module() -> Any:
    try:
        import validate_final_result
    except ImportError:
        from . import validate_final_result  # type: ignore[no-redef]
    return validate_final_result


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except Exception as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        if isinstance(exc, OSError):
            raise BuildError(f"{path.name}: atomic write failed") from exc
        raise


def run(*, write: bool) -> int:
    validator = _validator_module()
    try:
        sources = validator.load_validated_sources(PUBLIC_CHECKPOINT_BINDING)
        expected = build_result_bytes(sources, PUBLIC_CHECKPOINT_BINDING)
        validator.validate_final_result_bytes(
            expected, sources, PUBLIC_CHECKPOINT_BINDING
        )
        target = result_path()
        if write:
            if target.exists() and read_fixed_file(target) == expected:
                action = "unchanged"
            else:
                _atomic_write(target, expected)
                action = "written"
            result = build_result_object(sources, PUBLIC_CHECKPOINT_BINDING)
            print(
                f"WRITE PASS: {RESULT_FILENAME} {action}; "
                f"result_sha256={result['result_sha256']}"
            )
            return 0

        actual = read_fixed_file(target)
        validated = validator.validate_final_result_bytes(
            actual, sources, PUBLIC_CHECKPOINT_BINDING
        )
        if actual != expected:
            raise BuildError(f"{RESULT_FILENAME}: bytes differ from deterministic builder output")
        print(
            f"CHECK PASS: {RESULT_FILENAME}; "
            f"result_sha256={validated['result_sha256']}"
        )
        return 0
    except BuildError as exc:
        mode = "WRITE" if write else "CHECK"
        print(f"{mode} FAIL: {exc}", file=sys.stderr)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build or byte-check the deterministic offline GDT621 final result."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="atomically write the final artifact")
    mode.add_argument("--check", action="store_true", help="check the existing final artifact")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    return run(write=args.write)


if __name__ == "__main__":
    raise SystemExit(main())
