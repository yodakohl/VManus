#!/usr/bin/env python3
"""Run the frozen, target-blind DANI001 engineering calibration.

The module deliberately separates target-free numerical machinery from the
registered I/O phase.  Importing it opens no repository input, performs no
network request, constructs no registered synthetic world, and evaluates no
mapping.  The registered entry point is enabled only by a hash-bound freeze.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import locale
import math
import os
import re
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import time
import types
from collections import defaultdict
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

# NumPy is deliberately imported only by registered calibration execution.
# Freeze construction and source-free smoke perform hashing/pure scalar checks
# without loading a numerical calibration dependency.


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = HERE / "results"

SCIENCE_SPEC_REL = (
    "experiments/semantic_assumptions/DANI001_FIXED_MAPPING_DIAGNOSTIC_SPEC.md"
)
CALIBRATION_SPEC_REL = (
    "experiments/semantic_assumptions/DANI001_TARGET_BLIND_CALIBRATION_SPEC.md"
)
PANEL_REL = "experiments/semantic_assumptions/dani001_panel.py"
GENERATOR_REL = "experiments/semantic_assumptions/dani001_calibration_generator.py"
CORE_PY_REL = "experiments/semantic_assumptions/dani001_core.py"
CORE_H_REL = "experiments/semantic_assumptions/dani001_core.h"
CORE_CPP_REL = "experiments/semantic_assumptions/dani001_core.cpp"
RUNNER_REL = (
    "experiments/semantic_assumptions/run_dani001_target_blind_calibration.py"
)
VALIDATOR_REL = (
    "experiments/semantic_assumptions/validate_dani001_target_blind_calibration.py"
)
MANIFEST_REL = "experiments/semantic_assumptions/DANI001_SYNTHETIC_MANIFEST.json"
FREEZE_REL = "experiments/semantic_assumptions/DANI001_CALIBRATION_FREEZE.json"
OUT_JSON_REL = (
    "experiments/semantic_assumptions/results/"
    "dani001_target_blind_calibration.json"
)
OUT_MD_REL = (
    "experiments/semantic_assumptions/results/"
    "dani001_target_blind_calibration.md"
)
VALIDATION_JSON_REL = (
    "experiments/semantic_assumptions/results/"
    "dani001_target_blind_calibration_validation.json"
)
VALIDATION_MD_REL = (
    "experiments/semantic_assumptions/results/"
    "dani001_target_blind_calibration_validation.md"
)

# The calibration-spec digest is filled only after the amendment is final.
CALIBRATION_SPEC_SHA256 = (
    "f38de851d96e5fbb3a9a8bbb7ecd9c925ee34e4cb1c181970b6f582fbdea9c32"
)
SCIENCE_SPEC_SHA256 = (
    "cc73479b3c35eaa87a3f56184fc3472fe6232b67c13deb3bf30ef8555a6c8426"
)
REGISTERED_COMMIT = "1faa87f"
ORBIT10 = 3_628_800
ACTUAL_BEGIN = 1
ACTUAL_END = ORBIT10
WORKERS = 32
SYNTHETIC_DOMAINS = (
    "astro", "botanical", "function", "general", "medical", "pharma",
)

EDITION_ORDER = ("ZL3b", "IT2a", "RF1b")
PANEL_ORDER = ("DOT_ONLY_EMULATION", "MANUAL_GROUP")
WEIGHT_ORDER = ("TOKEN", "TYPE", "FOLIO")
CORE_INPUTS = ("k", "d", "r", "s", "l", "n", "q", "y", "m", "g")
CORE_OUTPUTS = ("k", "d", "r", "s", "l", "n", "w", "y", "m", "g")
NIBBLE_SYMBOLS = (
    "k", "d", "r", "s", "l", "n", "w", "y", "m", "g", "š", "ṭ", "p", "ṣ",
)
NIBBLE_CODE = {value: index for index, value in enumerate(NIBBLE_SYMBOLS, 1)}
CORE_OUTPUT_INDEX = {NIBBLE_CODE[value]: index for index, value in enumerate(CORE_OUTPUTS)}
GALLOWS_CODES = tuple(NIBBLE_CODE[value] for value in ("ṭ", "p", "ṣ"))
STANDARD_CODES = tuple(NIBBLE_CODE[value] for value in ("d", "l", "w"))
SUFFIX_YN_CODES = (NIBBLE_CODE["y"], NIBBLE_CODE["n"])

VIEW_ORDER = (
    "FULL_DEPOSITED_AFFIX",
    "DIRECT_ONLY",
    "STRICT_NO_FUNCTION",
    "STRICT_LITERAL",
    "TOP20_DELETED",
    "SOURCE_PRESENT",
    "LEAVE_ASTRO_OUT",
    "LEAVE_BOTANICAL_OUT",
    "LEAVE_FUNCTION_OUT",
    "LEAVE_GENERAL_OUT",
    "LEAVE_MEDICAL_OUT",
    "LEAVE_PHARMA_OUT",
)
CONTROL_ORDER = (
    "toys", "plants", "nulls", "adversaries", "parser", "mutations",
    "conjugacy", "workers", "affix_equivalence", "unreachable_invariance",
)
OUTPUT_RELS = (OUT_JSON_REL, OUT_MD_REL)
ALL_OUTPUT_RELS = (
    OUT_JSON_REL, OUT_MD_REL, VALIDATION_JSON_REL, VALIDATION_MD_REL,
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")

LOCAL_INPUT_RELS = (
    "transcription/sources/ZL3b-n.txt",
    "transcription/sources/IT2a-n.txt",
    "transcription/sources/RF1b-e.txt",
    "experiments/semantic_assumptions/results/source_separator_transcription.tsv",
    "experiments/semantic_assumptions/results/source_separator_transcription_validation.json",
)
LOCAL_INPUT_SHA256 = {
    "transcription/sources/ZL3b-n.txt":
        "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "transcription/sources/IT2a-n.txt":
        "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    "transcription/sources/RF1b-e.txt":
        "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
    "experiments/semantic_assumptions/results/source_separator_transcription.tsv":
        "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    "experiments/semantic_assumptions/results/source_separator_transcription_validation.json":
        "8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb",
}
LOCAL_INPUT_SIZE = {
    "transcription/sources/ZL3b-n.txt": 411_671,
    "transcription/sources/IT2a-n.txt": 342_104,
    "transcription/sources/RF1b-e.txt": 362_373,
    "experiments/semantic_assumptions/results/source_separator_transcription.tsv":
        16_754_953,
    "experiments/semantic_assumptions/results/source_separator_transcription_validation.json":
        3_517,
}
TEMPORARY_ALLOWLIST = (
    "EXTERNAL_ACQUISITION_EXACT_THREE_FILES",
    "CORE_BUILD_CPP_HEADER_LIBRARY",
    "OUTPUT_STAGING_TWO_FILES",
)
CODE_RELS = (
    PANEL_REL, GENERATOR_REL, CORE_PY_REL, CORE_H_REL, CORE_CPP_REL,
    RUNNER_REL, VALIDATOR_REL,
)
RUN_READ_RELS = frozenset((
    SCIENCE_SPEC_REL, CALIBRATION_SPEC_REL, FREEZE_REL, MANIFEST_REL,
    PANEL_REL, GENERATOR_REL, CORE_PY_REL, CORE_H_REL, CORE_CPP_REL,
    RUNNER_REL, *LOCAL_INPUT_RELS,
))
FROZEN_CXX = "/usr/bin/x86_64-linux-gnu-g++-12"
FROZEN_CXX_SHA256 = "1cfb9704049655d08accca3b1aeefd6fc749ef2cfb992ec95a81f39091d7b3ce"
FROZEN_CXX_VERSION_STDOUT = (
    "x86_64-linux-gnu-g++-12 (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0\n"
    "Copyright (C) 2022 Free Software Foundation, Inc.\n"
    "This is free software; see the source for copying conditions.  There is NO\n"
    "warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n\n"
).encode("utf-8")
COMPILE_ARGV = (
    FROZEN_CXX, "-std=c++20", "-O3", "-DNDEBUG", "-fPIC", "-shared",
    "-fopenmp", "-fno-fast-math", "-ffp-contract=off",
    "dani001_core.cpp", "-o", "libdani001_core.so",
)
COMPILE_ENV = {
    "HOME": "/nonexistent",
    "LANG": "C",
    "LC_ALL": "C",
    "PATH": "/usr/bin:/bin",
    "SOURCE_DATE_EPOCH": "0",
    "TZ": "UTC",
}
EXTERNAL_BINDINGS = (
    {
        "name": "stable_metadata_projection",
        "url": "https://zenodo.org/api/records/19583305",
        "sha256": "780301fd3c4b2c3c328c1f69a1eab65d0b0600f2d491ea9578f81699d36ddfa7",
        "storage": "MEMORY_ONLY_CANONICAL_PROJECTION",
    },
    {
        "name": "pipeline_body",
        "url": "https://zenodo.org/api/records/19609475/files/pipeline_v31_1.py/content",
        "sha256": "079b6de7b8d2082303a0789fb3904105aecaa491e35600a557090e7981255d6f",
        "storage": "EXTERNAL_TEMPORARY_ONLY_INERT",
    },
    {
        "name": "lexicon_body",
        "url": (
            "https://zenodo.org/api/records/19609475/files/"
            "lexicon_v31_session31_final.json/content"
        ),
        "sha256": "348992fa2bf555f1454a5a5485dd1ca9842acc143059f257f2fcdcf237821589",
        "storage": "EXTERNAL_TEMPORARY_ONLY_PROJECT_AFTER_SYNTHETICS",
    },
)


class DANI001CalibrationError(RuntimeError):
    """A registered engineering, isolation, or numerical invariant failed."""


_AUDIT_INSTALLED = False
_ACTUAL_ACCESS_GRANTED = False
_REGISTERED_EXTERNAL_ROOTS: set[Path] = set()
_REGISTERED_TEMP_ROOTS: set[Path] = set()
_REPOSITORY_READS: list[str] = []
_REPOSITORY_WRITES: list[str] = []
_NETWORK_EVENTS: list[str] = []
_FORBIDDEN_READS = 0
_FORBIDDEN_WRITES = 0
_FORBIDDEN_NETWORK = 0
_TEMP_VIOLATIONS = 0
_OUTPUT_COLLISIONS = 0
_PRE_SYNTHETIC_LOCAL_READS = 0
_PROJECTION_CALLS = 0
_SYNTHETIC_COMPLETE = False


def _repository_relative(value: object) -> str | None:
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


def _external_path_allowed(value: object) -> bool:
    if isinstance(value, int):
        return True
    try:
        path = Path(os.fsdecode(value))
    except (TypeError, ValueError):
        return True
    if not path.is_absolute():
        path = Path.cwd() / path
    resolved = path.resolve(strict=False)
    for root in (*_REGISTERED_EXTERNAL_ROOTS, *_REGISTERED_TEMP_ROOTS):
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _external_read_allowed(value: object) -> bool:
    """Permit only registered acquisition/build/staging roots after isolation."""

    if isinstance(value, int):
        return True
    return _external_path_allowed(value)


def _audit_write(mode: object, flags: object) -> bool:
    if isinstance(mode, str) and any(value in mode for value in "wax+"):
        return True
    if isinstance(flags, int):
        return bool(flags & (
            os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC |
            os.O_APPEND
        ))
    return False


def _audit_hook(event: str, args: tuple[object, ...]) -> None:
    global _FORBIDDEN_READS, _FORBIDDEN_WRITES, _FORBIDDEN_NETWORK
    global _PRE_SYNTHETIC_LOCAL_READS, _OUTPUT_COLLISIONS, _TEMP_VIOLATIONS
    if event == "open" and args:
        relative = _repository_relative(args[0])
        write = _audit_write(
            args[1] if len(args) > 1 else None,
            args[2] if len(args) > 2 else None,
        )
        if relative is not None:
            if write:
                _FORBIDDEN_WRITES += 1
                raise PermissionError(f"repository write denied: {relative}")
            if (
                relative == RESULTS.relative_to(ROOT).as_posix()
                and len(args) > 2
                and isinstance(args[2], int)
                and bool(args[2] & os.O_DIRECTORY)
            ):
                return
            if relative not in RUN_READ_RELS:
                _FORBIDDEN_READS += 1
                raise PermissionError(f"repository read denied: {relative}")
            if relative in LOCAL_INPUT_RELS and not _ACTUAL_ACCESS_GRANTED:
                _PRE_SYNTHETIC_LOCAL_READS += 1
                _FORBIDDEN_READS += 1
                raise PermissionError(f"pre-synthetic actual read denied: {relative}")
            _REPOSITORY_READS.append(relative)
            return
        if write:
            if not _external_path_allowed(args[0]):
                _TEMP_VIOLATIONS += 1
                _FORBIDDEN_WRITES += 1
                raise PermissionError(
                    "external write outside registered temporary roots"
                )
        elif not _external_read_allowed(args[0]):
            _FORBIDDEN_READS += 1
            raise PermissionError("external read outside registered roots")
    elif event == "os.link" and len(args) >= 2:
        source_relative = _repository_relative(args[0])
        destination_relative = _repository_relative(args[1])
        if (
            source_relative is None
            and destination_relative in OUTPUT_RELS
            and _external_path_allowed(args[0])
        ):
            _REPOSITORY_WRITES.append(str(destination_relative))
            return
        _FORBIDDEN_WRITES += 1
        raise PermissionError("unregistered repository hard link")
    elif event in {"os.remove", "os.unlink"} and args:
        relative = _repository_relative(args[0])
        if relative in OUTPUT_RELS and relative in _REPOSITORY_WRITES:
            return
        if relative is not None:
            _FORBIDDEN_WRITES += 1
            raise PermissionError(f"unregistered repository removal: {relative}")
        if not _external_path_allowed(args[0]):
            _TEMP_VIOLATIONS += 1
            _FORBIDDEN_WRITES += 1
            raise PermissionError("unregistered external removal")
    elif event in {"os.rename", "os.replace"} and len(args) >= 2:
        if _repository_relative(args[0]) is not None or _repository_relative(args[1]) is not None:
            _FORBIDDEN_WRITES += 1
            raise PermissionError("repository rename denied")
        if not _external_path_allowed(args[0]) or not _external_path_allowed(args[1]):
            _TEMP_VIOLATIONS += 1
            _FORBIDDEN_WRITES += 1
            raise PermissionError("unregistered external rename")
    elif event in {"os.listdir", "os.scandir"} and args:
        relative = _repository_relative(args[0])
        if relative is not None or not _external_path_allowed(args[0]):
            _FORBIDDEN_READS += 1
            raise PermissionError("directory enumeration outside registered roots")
    elif event in {"socket.connect", "socket.getaddrinfo"}:
        _NETWORK_EVENTS.append(repr(args[:1]))
        _FORBIDDEN_NETWORK += 1
        raise PermissionError("network denied after acquisition")
    elif event in {"subprocess.Popen", "os.system", "ctypes.dlopen"}:
        _FORBIDDEN_READS += 1
        raise PermissionError("post-isolation executable/library access denied")


def _install_audit_hook() -> None:
    global _AUDIT_INSTALLED
    if _AUDIT_INSTALLED:
        raise DANI001CalibrationError("audit hook already installed")
    sys.addaudithook(_audit_hook)
    _AUDIT_INSTALLED = True


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_json(value: object) -> bytes:
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


@dataclass(frozen=True)
class _FileProof:
    device: int
    inode: int
    size: int
    sha256: str


def _enforce_locale_timezone() -> None:
    """Set and prove the registered process-wide locale and civil timezone."""

    os.environ["LANG"] = "C"
    os.environ["LC_ALL"] = "C"
    os.environ["TZ"] = "UTC"
    try:
        applied = locale.setlocale(locale.LC_ALL, "C")
        time.tzset()
        live = locale.setlocale(locale.LC_ALL, None)
    except (locale.Error, OSError) as error:
        raise DANI001CalibrationError(
            "registered locale/timezone could not be applied"
        ) from error
    if (
        applied != "C"
        or live != "C"
        or os.environ.get("LANG") != "C"
        or os.environ.get("LC_ALL") != "C"
        or os.environ.get("TZ") != "UTC"
        or time.tzname != ("UTC", "UTC")
        or time.timezone != 0
        or time.altzone != 0
        or time.daylight != 0
    ):
        raise DANI001CalibrationError(
            "registered locale/timezone live verification failed"
        )


def _regular_file_proof(path: Path) -> _FileProof:
    """Hash one stable pathname without following a symlink."""

    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise DANI001CalibrationError("proof target is not a regular file")
        digest = hashlib.sha256()
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            digest.update(block)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    pathname = path.stat(follow_symlinks=False)
    identity_before = (before.st_dev, before.st_ino, before.st_size)
    identity_after = (after.st_dev, after.st_ino, after.st_size)
    identity_path = (pathname.st_dev, pathname.st_ino, pathname.st_size)
    if identity_before != identity_after or identity_before != identity_path:
        raise DANI001CalibrationError("file changed while proving its bytes")
    return _FileProof(*identity_before, digest.hexdigest())


def _file_proof(path: Path) -> _FileProof:
    return _regular_file_proof(path)


def _prove_freeze_staged_link(
    source: Path, destination: Path, expected: _FileProof
) -> None:
    """Freeze-only proof may hash both staged and installed names."""

    source_now = _file_proof(source)
    destination_now = _file_proof(destination)
    if source_now != expected or destination_now != expected:
        raise DANI001CalibrationError(
            "post-link staged inode/size/SHA-256 proof failed"
        )


def _rollback_freeze_staged_link(
    source: Path, destination: Path, expected: _FileProof
) -> None:
    """Remove only a freeze destination re-proved as the staged file."""

    if not os.path.lexists(destination):
        return
    try:
        _prove_freeze_staged_link(source, destination, expected)
    except (DANI001CalibrationError, OSError) as error:
        raise DANI001CalibrationError(
            "rollback refused raced or foreign destination"
        ) from error
    os.unlink(destination)
    if os.path.lexists(destination):
        raise DANI001CalibrationError("rollback absence proof failed")
    if _file_proof(source) != expected:
        raise DANI001CalibrationError("rollback staged-source proof failed")


def _result_destination_inode_proof(
    destination: Path, expected: _FileProof
) -> None:
    """Prove the result hard-link identity without opening its destination."""

    destination_stat = destination.stat(follow_symlinks=False)
    if (
        not stat.S_ISREG(destination_stat.st_mode)
        or (
            destination_stat.st_dev,
            destination_stat.st_ino,
            destination_stat.st_size,
        ) != (expected.device, expected.inode, expected.size)
    ):
        raise DANI001CalibrationError(
            "result destination staged-inode/size proof failed"
        )


def _prove_result_staged_link(
    source: Path, destination: Path, expected: _FileProof
) -> None:
    """Hash only the staged name; lstat the repository hard-link name."""

    if _file_proof(source) != expected:
        raise DANI001CalibrationError("result staged-source SHA-256 proof failed")
    _result_destination_inode_proof(destination, expected)


def _rollback_result_staged_link(
    source: Path, destination: Path, expected: _FileProof
) -> None:
    """Rollback without opening or reading an installed result destination."""

    if not os.path.lexists(destination):
        return
    try:
        _prove_result_staged_link(source, destination, expected)
    except (DANI001CalibrationError, OSError) as error:
        raise DANI001CalibrationError(
            "result rollback refused raced or foreign destination"
        ) from error
    os.unlink(destination)
    if os.path.lexists(destination):
        raise DANI001CalibrationError("result rollback absence proof failed")
    if _file_proof(source) != expected:
        raise DANI001CalibrationError("result rollback staged-source proof failed")


def _json_no_duplicates(data: bytes) -> object:
    def pairs(values: list[tuple[str, object]]) -> dict[str, object]:
        output: dict[str, object] = {}
        for key, value in values:
            if key in output:
                raise DANI001CalibrationError("duplicate JSON member")
            output[key] = value
        return output

    try:
        return json.loads(data, object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DANI001CalibrationError("malformed JSON input") from error


def _freeze_string(value: object, label: str) -> str:
    if type(value) is not str:
        raise DANI001CalibrationError(f"freeze {label} is not a JSON string")
    return value


def _freeze_sha256(value: object, label: str) -> str:
    text = _freeze_string(value, label)
    if not HEX64.fullmatch(text):
        raise DANI001CalibrationError(f"freeze {label} SHA-256 malformed")
    return text


def _freeze_string_array(value: object, label: str) -> list[str]:
    if type(value) is not list or any(type(member) is not str for member in value):
        raise DANI001CalibrationError(
            f"freeze {label} is not an exact JSON string array"
        )
    return value


def _freeze_path_object(
    value: object, label: str, expected_path: str
) -> dict[str, object]:
    if type(value) is not dict or set(value) != {"path", "sha256", "size"}:
        raise DANI001CalibrationError(f"freeze {label} path schema drift")
    if _freeze_string(value["path"], f"{label}.path") != expected_path:
        raise DANI001CalibrationError(f"freeze {label} path drift")
    _freeze_sha256(value["sha256"], f"{label}.sha256")
    if type(value["size"]) is not int or value["size"] < 0:
        raise DANI001CalibrationError(
            f"freeze {label}.size is not a nonnegative JSON integer"
        )
    return value


def _validate_freeze_schema(freeze: object) -> dict[str, object]:
    """Validate every freeze container and scalar with exact JSON types."""

    exact_top = {
        "schema", "registered_commit", "science_spec", "calibration_spec",
        "local_inputs", "external_inputs", "code", "synthetic_manifest",
        "runtime", "core_build", "read_allowlist", "network_allowlist",
        "temporary_allowlist", "producer_outputs_absent",
        "validator_outputs_absent", "producer_write_allowlist",
        "validator_write_allowlist", "static_audit",
    }
    if type(freeze) is not dict or set(freeze) != exact_top:
        raise DANI001CalibrationError("calibration freeze schema drift")
    if _freeze_string(freeze["schema"], "schema") != (
        "dani001-target-blind-calibration-freeze-v1"
    ):
        raise DANI001CalibrationError("calibration freeze version drift")
    if _freeze_string(freeze["registered_commit"], "registered_commit") != (
        REGISTERED_COMMIT
    ):
        raise DANI001CalibrationError("registered commit drift")

    _freeze_path_object(freeze["science_spec"], "science_spec", SCIENCE_SPEC_REL)
    _freeze_path_object(
        freeze["calibration_spec"], "calibration_spec", CALIBRATION_SPEC_REL
    )
    _freeze_path_object(
        freeze["synthetic_manifest"], "synthetic_manifest", MANIFEST_REL
    )
    local = freeze["local_inputs"]
    if type(local) is not list or len(local) != len(LOCAL_INPUT_RELS):
        raise DANI001CalibrationError("freeze local_inputs schema drift")
    for index, (binding, relative) in enumerate(
        zip(local, LOCAL_INPUT_RELS, strict=True)
    ):
        _freeze_path_object(binding, f"local_inputs[{index}]", relative)
    code = freeze["code"]
    if type(code) is not list or len(code) != len(CODE_RELS):
        raise DANI001CalibrationError("freeze code schema drift")
    for index, (binding, relative) in enumerate(zip(code, CODE_RELS, strict=True)):
        _freeze_path_object(binding, f"code[{index}]", relative)

    external = freeze["external_inputs"]
    if type(external) is not list or len(external) != len(EXTERNAL_BINDINGS):
        raise DANI001CalibrationError("freeze external_inputs schema drift")
    for index, (binding, expected) in enumerate(
        zip(external, EXTERNAL_BINDINGS, strict=True)
    ):
        if type(binding) is not dict or set(binding) != {
            "name", "url", "sha256", "storage",
        }:
            raise DANI001CalibrationError(
                f"freeze external_inputs[{index}] schema drift"
            )
        for key in ("name", "url", "storage"):
            if _freeze_string(
                binding[key], f"external_inputs[{index}].{key}"
            ) != expected[key]:
                raise DANI001CalibrationError(
                    f"freeze external_inputs[{index}].{key} drift"
                )
        if _freeze_sha256(
            binding["sha256"], f"external_inputs[{index}].sha256"
        ) != expected["sha256"]:
            raise DANI001CalibrationError(
                f"freeze external_inputs[{index}].sha256 drift"
            )

    runtime = freeze["runtime"]
    runtime_keys = {
        "python", "implementation", "machine", "system", "byteorder",
        "binary64", "numpy", "locale", "timezone", "workers",
        "openmp_library_name", "openmp_library_sha256",
        "runtime_image_sha256",
    }
    if type(runtime) is not dict or set(runtime) != runtime_keys:
        raise DANI001CalibrationError("freeze runtime schema drift")
    exact_runtime_strings = {
        "python": "3.12.3",
        "implementation": "CPython",
        "machine": "x86_64",
        "system": "Linux",
        "byteorder": "little",
        "binary64": "IEEE754_ROUND_TO_NEAREST",
        "numpy": "1.26.4",
        "locale": "C",
        "timezone": "UTC",
    }
    for key, expected in exact_runtime_strings.items():
        if _freeze_string(runtime[key], f"runtime.{key}") != expected:
            raise DANI001CalibrationError(f"freeze runtime.{key} drift")
    workers = runtime["workers"]
    if (
        type(workers) is not list
        or len(workers) != 2
        or any(type(member) is not int for member in workers)
        or workers != [1, 32]
    ):
        raise DANI001CalibrationError(
            "freeze runtime.workers is not exact JSON integers [1,32]"
        )
    if not _freeze_string(runtime["openmp_library_name"], "runtime.openmp_library_name"):
        raise DANI001CalibrationError("freeze OpenMP library name is empty")
    _freeze_sha256(runtime["openmp_library_sha256"], "runtime.openmp_library_sha256")
    runtime_digest = _freeze_sha256(
        runtime["runtime_image_sha256"], "runtime.runtime_image_sha256"
    )
    runtime_preimage = dict(runtime)
    del runtime_preimage["runtime_image_sha256"]
    if runtime_digest != _sha256(_canonical_json(runtime_preimage)):
        raise DANI001CalibrationError("freeze runtime image digest drift")

    core = freeze["core_build"]
    core_keys = {
        "compiler_path", "compiler_sha256", "compiler_version_stdout_hex",
        "argv", "shared_library_sha256", "abi_version",
        "runtime_image_sha256",
    }
    if type(core) is not dict or set(core) != core_keys:
        raise DANI001CalibrationError("freeze core_build schema drift")
    if _freeze_string(core["compiler_path"], "core_build.compiler_path") != FROZEN_CXX:
        raise DANI001CalibrationError("freeze compiler path drift")
    if _freeze_sha256(core["compiler_sha256"], "core_build.compiler_sha256") != (
        FROZEN_CXX_SHA256
    ):
        raise DANI001CalibrationError("freeze compiler SHA-256 drift")
    version_hex = _freeze_string(
        core["compiler_version_stdout_hex"],
        "core_build.compiler_version_stdout_hex",
    )
    if not version_hex or re.fullmatch(r"[0-9a-f]+", version_hex) is None:
        raise DANI001CalibrationError("freeze compiler version hex malformed")
    argv = _freeze_string_array(core["argv"], "core_build.argv")
    if tuple(argv) != COMPILE_ARGV:
        raise DANI001CalibrationError("freeze compiler argv drift")
    _freeze_sha256(core["shared_library_sha256"], "core_build.shared_library_sha256")
    if type(core["abi_version"]) is not int or core["abi_version"] != 1:
        raise DANI001CalibrationError(
            "freeze core_build.abi_version is not JSON integer 1"
        )
    if _freeze_sha256(
        core["runtime_image_sha256"], "core_build.runtime_image_sha256"
    ) != runtime_digest:
        raise DANI001CalibrationError("freeze core/runtime image binding drift")

    exact_string_arrays = {
        "read_allowlist": (
            SCIENCE_SPEC_REL, CALIBRATION_SPEC_REL, FREEZE_REL, MANIFEST_REL,
            PANEL_REL, GENERATOR_REL, CORE_PY_REL, CORE_H_REL, CORE_CPP_REL,
            RUNNER_REL, *LOCAL_INPUT_RELS,
        ),
        "network_allowlist": tuple(value["url"] for value in EXTERNAL_BINDINGS),
        "temporary_allowlist": TEMPORARY_ALLOWLIST,
        "producer_outputs_absent": OUTPUT_RELS,
        "validator_outputs_absent": (VALIDATION_JSON_REL, VALIDATION_MD_REL),
        "producer_write_allowlist": OUTPUT_RELS,
        "validator_write_allowlist": (VALIDATION_JSON_REL, VALIDATION_MD_REL),
    }
    for key, expected in exact_string_arrays.items():
        if tuple(_freeze_string_array(freeze[key], key)) != expected:
            raise DANI001CalibrationError(f"freeze {key} drift")

    static_audit = freeze["static_audit"]
    if type(static_audit) is not dict or set(static_audit) != {
        "status", "review_id", "auditor_source_sha256",
    }:
        raise DANI001CalibrationError("freeze static_audit schema drift")
    if _freeze_string(static_audit["status"], "static_audit.status") != "GO":
        raise DANI001CalibrationError("static calibration audit is not GO")
    if _freeze_string(
        static_audit["review_id"], "static_audit.review_id"
    ) != "DANI001_CALIBRATION_FREEZE_STATIC_AUDIT_V1":
        raise DANI001CalibrationError("freeze static audit review drift")
    _freeze_sha256(
        static_audit["auditor_source_sha256"],
        "static_audit.auditor_source_sha256",
    )
    return freeze


def _decode_canonical_freeze(data: bytes) -> dict[str, object]:
    freeze = _validate_freeze_schema(_json_no_duplicates(data))
    if _canonical_json(freeze) != data:
        raise DANI001CalibrationError("calibration freeze is not canonical JSON bytes")
    return freeze


def _positive_zero(value: float) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise DANI001CalibrationError("nonfinite binary64 value")
    return 0.0 if result == 0.0 else result


def _u4_digest(values: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(values, dtype="<u4"))
    return _sha256(array.tobytes(order="C"))


def _f8_digest(values: np.ndarray) -> str:
    array = np.array(values, dtype="<f8", order="C", copy=True)
    if not np.all(np.isfinite(array)):
        raise DANI001CalibrationError("nonfinite score vector")
    # Canonicalize either sign of zero without changing any nonzero bit.
    array[array == 0.0] = 0.0
    return _sha256(array.tobytes(order="C"))


def _decode_codes(value: int) -> tuple[int, ...]:
    if type(value) is not int or value < 0 or value >= 1 << 64 or value >> 44:
        raise DANI001CalibrationError("invalid encoded skeleton")
    length = (value >> 40) & 0xF
    if length > 10:
        raise DANI001CalibrationError("overlength encoded skeleton")
    output = tuple((value >> (4 * index)) & 0xF for index in range(length))
    if any(code == 0 or code > 14 for code in output):
        raise DANI001CalibrationError("invalid nibble in encoded skeleton")
    if any((value >> (4 * index)) & 0xF for index in range(length, 10)):
        raise DANI001CalibrationError("nonzero encoded padding")
    return output


def _encode_codes(codes: Sequence[int]) -> int:
    values = tuple(codes)
    if len(values) > 10 or any(type(value) is not int or not 1 <= value <= 14 for value in values):
        raise DANI001CalibrationError("invalid code sequence")
    output = len(values) << 40
    for index, value in enumerate(values):
        output |= value << (4 * index)
    return output


def _accepted_preimages_literal(direct_codes: Iterable[int]) -> tuple[int, ...]:
    """Independent literal expansion of the registered decision paths."""

    accepted: set[int] = set()
    for encoded in direct_codes:
        key = _decode_codes(int(encoded))
        candidates = [key, key + SUFFIX_YN_CODES]
        candidates.extend((standard,) + key for standard in STANDARD_CODES)
        for gallows in GALLOWS_CODES:
            candidates.append((gallows,) + key)
            candidates.extend(
                (gallows, standard) + key for standard in STANDARD_CODES
            )
        for candidate in candidates:
            if len(candidate) > 10:
                raise DANI001CalibrationError("accepted affix preimage exceeds ten")
            accepted.add(_encode_codes(candidate))
    return tuple(sorted(accepted))


def _literal_match_decision(
    skeleton: int, direct_codes: Iterable[int], *, deposited: bool = True
) -> bool:
    """Independent Python transcription of the deposited first-match order."""

    keys = frozenset(int(value) for value in direct_codes)
    mapped = _decode_codes(int(skeleton))
    if int(skeleton) in keys:
        return True
    if not deposited:
        return False
    if len(mapped) > 1 and mapped[0] in GALLOWS_CODES:
        if _encode_codes(mapped[1:]) in keys:
            return True
        if (
            len(mapped) > 2
            and mapped[1] in STANDARD_CODES
            and _encode_codes(mapped[2:]) in keys
        ):
            return True
    if (
        len(mapped) > 1
        and mapped[0] in STANDARD_CODES
        and _encode_codes(mapped[1:]) in keys
    ):
        return True
    return bool(
        len(mapped) > 2
        and mapped[-2:] == SUFFIX_YN_CODES
        and _encode_codes(mapped[:-2]) in keys
    )


def _literal_candidates(direct_codes: Iterable[int]) -> tuple[int, ...]:
    """Construct positives through the literal paths, not the core preimage API."""

    candidates: set[int] = set()
    direct = tuple(sorted(set(int(value) for value in direct_codes)))
    for encoded in direct:
        key = _decode_codes(encoded)
        trial = [key]
        trial.extend((gallows,) + key for gallows in GALLOWS_CODES)
        trial.extend(
            (gallows, standard) + key
            for gallows in GALLOWS_CODES
            for standard in STANDARD_CODES
        )
        trial.extend((standard,) + key for standard in STANDARD_CODES)
        trial.append(key + SUFFIX_YN_CODES)
        for value in trial:
            if len(value) > 10:
                raise DANI001CalibrationError(
                    "literal decision produced overlength preimage"
                )
            packed = _encode_codes(value)
            if not _literal_match_decision(packed, direct, deposited=True):
                raise DANI001CalibrationError("literal positive rejected itself")
            candidates.add(packed)
    return tuple(sorted(candidates))


@dataclass(frozen=True, slots=True)
class PrivateToken:
    folio: int = field(repr=False)
    normalized: str = field(repr=False)
    template: tuple[int, ...] = field(repr=False)
    strict: bool = field(repr=False)


@dataclass(frozen=True, slots=True)
class PrivateSurface:
    edition: str
    panel: str
    tokens: tuple[PrivateToken, ...] = field(repr=False)
    template_sha256: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class TypeBin:
    normalized: str = field(repr=False)
    template: tuple[int, ...] = field(repr=False)
    token_count: int
    folio_counts: tuple[tuple[int, int], ...]


@dataclass(frozen=True, slots=True)
class Constraint:
    mask: int
    required: tuple[int, ...]


@dataclass(slots=True)
class SurfaceVectors:
    token: np.ndarray = field(repr=False)
    type: np.ndarray = field(repr=False)
    folio: np.ndarray = field(repr=False)
    token_denominator: int
    type_denominator: int
    folio_count: int
    variable_type_count: int
    capacity_folio_count: int
    folio_advantages: tuple[float, ...] | None = field(default=None, repr=False)
    folio_numerators: tuple[np.ndarray, ...] | None = field(
        default=None, repr=False
    )
    folio_denominators: tuple[int, ...] | None = field(default=None, repr=False)

    def vector(self, name: str) -> np.ndarray:
        if name == "TOKEN":
            return self.token
        if name == "TYPE":
            return self.type
        if name == "FOLIO":
            return self.folio
        raise KeyError(name)

    def denominator(self, name: str) -> int:
        if name == "TOKEN":
            return self.token_denominator
        if name == "TYPE":
            return self.type_denominator
        if name == "FOLIO":
            return 1
        raise KeyError(name)


def _surface_from_panel(panel: object) -> PrivateSurface:
    tokens = tuple(
        PrivateToken(
            folio=int(token.folio),
            normalized=str(token.normalized_eva),
            template=tuple(int(value) for value in token.emitted_template),
            strict=bool(strict),
        )
        for token, strict in zip(
            panel.tokens, panel.strict_literal_mask, strict=True  # type: ignore[attr-defined]
        )
    )
    return PrivateSurface(
        edition=str(panel.edition),  # type: ignore[attr-defined]
        panel=str(panel.name),  # type: ignore[attr-defined]
        tokens=tokens,
        template_sha256=str(panel.digest),  # type: ignore[attr-defined]
    )


def _surface_from_projection(
    edition: str,
    panel_name: str,
    projection: Sequence[Mapping[str, object]],
) -> PrivateSurface:
    tokens = tuple(
        PrivateToken(
            folio=int(value["folio"]),
            normalized=str(value["normalized_eva"]),
            template=tuple(int(item) for item in value["emitted_template"]),  # type: ignore[arg-type]
            strict=bool(value["strict_literal_eligible"]),
        )
        for value in projection
        if value["edition"] == edition
    )
    digest_payload = [
        {
            "folio": value.folio,
            "normalized_eva": value.normalized,
            "emitted_template": list(value.template),
            "strict_literal_eligible": value.strict,
        }
        for value in tokens
    ]
    return PrivateSurface(
        edition=edition,
        panel=panel_name,
        tokens=tokens,
        template_sha256=_sha256(_canonical_json(digest_payload)),
    )


def _type_bins(
    surface: PrivateSurface,
    *,
    strict_only: bool,
    delete_top20: bool,
) -> tuple[TypeBin, ...]:
    counts: dict[str, dict[str, object]] = {}
    for token in surface.tokens:
        if strict_only and not token.strict:
            continue
        value = counts.setdefault(
            token.normalized,
            {"template": token.template, "count": 0, "folios": defaultdict(int)},
        )
        if value["template"] != token.template:
            raise DANI001CalibrationError("one normalized type has multiple templates")
        value["count"] = int(value["count"]) + 1
        value["folios"][token.folio] += 1  # type: ignore[index]
    if delete_top20:
        if len(counts) < 20:
            return ()
        deleted = {
            name
            for name, _value in sorted(
                counts.items(),
                key=lambda item: (-int(item[1]["count"]), item[0].encode("utf-8")),
            )[:20]
        }
    else:
        deleted = set()
    output = []
    for normalized in sorted(counts, key=lambda value: value.encode("utf-8")):
        if normalized in deleted:
            continue
        value = counts[normalized]
        output.append(TypeBin(
            normalized=normalized,
            template=tuple(value["template"]),  # type: ignore[arg-type]
            token_count=int(value["count"]),
            folio_counts=tuple(sorted(value["folios"].items())),  # type: ignore[union-attr]
        ))
    return tuple(output)


def _constraints_for_template(
    template: Sequence[int],
    accepted_codes: Sequence[int],
    n_core: int,
) -> tuple[Constraint, ...]:
    values = tuple(int(value) for value in template)
    if len(values) > 10:
        return ()
    if not 1 <= n_core <= 10:
        raise DANI001CalibrationError("invalid core size")
    output: set[Constraint] = set()
    for encoded in accepted_codes:
        target = _decode_codes(int(encoded))
        if len(target) != len(values):
            continue
        required = [255] * n_core
        mask = 0
        compatible = True
        used_outputs: set[int] = set()
        for source, observed in zip(values, target, strict=True):
            if source > 0:
                if source != observed:
                    compatible = False
                    break
                continue
            input_index = -source - 1
            output_index = CORE_OUTPUT_INDEX.get(observed)
            if not 0 <= input_index < n_core or output_index is None or output_index >= n_core:
                compatible = False
                break
            prior = required[input_index]
            if prior != 255 and prior != output_index:
                compatible = False
                break
            if prior == 255 and output_index in used_outputs:
                compatible = False
                break
            required[input_index] = output_index
            used_outputs.add(output_index)
            mask |= 1 << input_index
        if compatible:
            output.add(Constraint(mask, tuple(required)))
    return tuple(sorted(output, key=lambda value: (value.mask, value.required)))


def _compiled_bins(
    bins: Sequence[TypeBin],
    accepted_codes: Sequence[int],
    n_core: int,
) -> tuple[tuple[TypeBin, tuple[Constraint, ...]], ...]:
    cache: dict[tuple[int, ...], tuple[Constraint, ...]] = {}
    output = []
    for value in bins:
        constraints = cache.get(value.template)
        if constraints is None:
            constraints = _constraints_for_template(value.template, accepted_codes, n_core)
            cache[value.template] = constraints
        output.append((value, constraints))
    return tuple(output)


def _compiled_bins_literal(
    bins: Sequence[TypeBin],
    direct_codes: Sequence[int],
    n_core: int,
) -> tuple[tuple[TypeBin, tuple[Constraint, ...]], ...]:
    """Compile through the independent literal decision path."""

    accepted = _literal_candidates(direct_codes)
    cache: dict[tuple[int, ...], tuple[Constraint, ...]] = {}
    output = []
    for value in bins:
        constraints = cache.get(value.template)
        if constraints is None:
            constraints = _constraints_for_template(value.template, accepted, n_core)
            cache[value.template] = constraints
        output.append((value, constraints))
    return tuple(output)


def _affix_constraint_equivalence(
    core: object,
    bins: Sequence[TypeBin],
    direct_codes: Sequence[int],
    accepted_codes: Sequence[int],
    n_core: int,
) -> bool:
    """Prove both matchers induce the same binary decision on every type/rank."""

    direct = tuple(sorted(set(int(value) for value in direct_codes)))
    preexpanded = tuple(sorted(set(int(value) for value in accepted_codes)))
    literal = _literal_candidates(direct)
    if literal != preexpanded or literal != _accepted_preimages_literal(direct):
        return False
    if tuple(int(value) for value in core.build_preimages(direct, 1)) != literal:
        return False
    # Exercise the compiled first-match implementation on every positive and a
    # deterministic negative basis.  Exhaustiveness for the actual panel is
    # supplied by exact equality of the induced partial-bijection constraints.
    fixtures = set(literal)
    fixtures.update(_encode_codes((value,)) for value in range(1, 15))
    fixtures.update(
        _encode_codes((left, right))
        for left in range(1, 15)
        for right in range(1, 15)
    )
    if core.check_preimage_equivalence(
        tuple(sorted(fixtures)), direct, preexpanded, 1
    ) != 0:
        return False
    precompiled = _compiled_bins(bins, preexpanded, n_core)
    literal_compiled = _compiled_bins_literal(bins, direct, n_core)
    return all(
        left_constraints == right_constraints
        for (_left, left_constraints), (_right, right_constraints)
        in zip(precompiled, literal_compiled, strict=True)
    )


def _rename_constraints(
    constraints: Sequence[Constraint], rho: Sequence[int]
) -> tuple[Constraint, ...]:
    permutation = tuple(int(value) for value in rho)
    if sorted(permutation) != list(range(len(permutation))):
        raise DANI001CalibrationError("invalid conjugacy permutation")
    output = set()
    for constraint in constraints:
        required = [255] * len(permutation)
        mask = 0
        for source, target in enumerate(constraint.required):
            if target == 255:
                continue
            renamed_source = permutation[source]
            renamed_target = permutation[target]
            required[renamed_source] = renamed_target
            mask |= 1 << renamed_source
        output.add(Constraint(mask, tuple(required)))
    return tuple(sorted(output, key=lambda value: (value.mask, value.required)))


def _enumerate_vectors(
    core: object,
    compiled: Sequence[tuple[TypeBin, tuple[Constraint, ...]]],
    vector_weights: Sequence[Mapping[str, int]],
    *,
    n_core: int,
    rank_begin: int,
    rank_end: int,
    threads: int,
    scalar: bool = False,
) -> np.ndarray:
    if not vector_weights:
        raise DANI001CalibrationError("empty vector request")
    by_constraint: dict[Constraint, list[int]] = {}
    for value, constraints in compiled:
        for constraint in constraints:
            row = by_constraint.setdefault(constraint, [0] * len(vector_weights))
            for index, weights in enumerate(vector_weights):
                increment = int(weights.get(value.normalized, 0))
                row[index] += increment
                if row[index] > 0xFFFFFFFF:
                    raise DANI001CalibrationError("constraint weight overflow")
    width = rank_end - rank_begin
    if not by_constraint:
        return np.zeros((len(vector_weights), width), dtype="<u4")
    constraints = sorted(by_constraint, key=lambda value: (value.mask, value.required))
    raw = core.enumerate_raw(
        n_core=n_core,
        input_masks=[value.mask for value in constraints],
        required_outputs=[item for value in constraints for item in value.required],
        n_vectors=len(vector_weights),
        weights=[item for value in constraints for item in by_constraint[value]],
        rank_begin=rank_begin,
        rank_end=rank_end,
        threads=threads,
        scalar=scalar,
    )
    expected = len(vector_weights) * width * 4
    if len(raw) != expected:
        raise DANI001CalibrationError("integer-core vector byte count drift")
    return np.frombuffer(raw, dtype="<u4").reshape(len(vector_weights), width).copy()


@dataclass(slots=True)
class ActualCoreGuard:
    """Rank-mask boundary for all real-panel core calls."""

    core: object = field(repr=False)
    interval_calls: int = 0
    primary_logical_view_surfaces: int = 0
    evidence_logical_view_surfaces: int = 0
    primary_logical_map_view_evaluations: int = 0
    evidence_logical_map_view_evaluations: int = 0
    match_calls: int = 0
    output_writes: int = 0

    def __post_init__(self) -> None:
        reset = getattr(self.core, "reset_traversal_audit", None)
        read = getattr(self.core, "traversal_audit", None)
        if not callable(reset) or not callable(read):
            raise DANI001CalibrationError("ACTUAL traversal audit unavailable")
        reset()
        initial = read()
        if (
            not isinstance(initial, dict)
            or set(initial) != {
                "optimized_calls", "constraint_traversals",
                "branches_considered", "branches_pruned",
                "completed_assignments", "completed_rank_zero",
            }
            or any(type(value) is not int or value != 0 for value in initial.values())
        ):
            raise DANI001CalibrationError("ACTUAL traversal audit reset failed")

    def enumerate_raw(self, **kwargs: object) -> bytes:
        if (
            kwargs.get("n_core") != 10
            or kwargs.get("rank_begin") != ACTUAL_BEGIN
            or kwargs.get("rank_end") != ACTUAL_END
            or kwargs.get("scalar") is not False
        ):
            raise DANI001CalibrationError(
                "ACTUAL core accepts only the frozen nonidentity interval"
            )
        masks = kwargs.get("input_masks")
        if not isinstance(masks, Sequence):
            raise DANI001CalibrationError("ACTUAL constraint inventory malformed")
        before = self.core.traversal_audit()  # type: ignore[attr-defined]
        result = self.core.enumerate_raw(**kwargs)  # type: ignore[attr-defined]
        after = self.core.traversal_audit()  # type: ignore[attr-defined]
        if (
            after["optimized_calls"] != before["optimized_calls"] + 1
            or after["constraint_traversals"]
            != before["constraint_traversals"] + len(masks)
            or after["branches_considered"] <= before["branches_considered"]
            or after["branches_pruned"] < before["branches_pruned"]
            or after["completed_assignments"] < before["completed_assignments"]
            or before["completed_rank_zero"] != 0
            or after["completed_rank_zero"] != 0
        ):
            raise DANI001CalibrationError(
                "ACTUAL rank-pruned traversal counter contract failed"
            )
        self.interval_calls += 1
        self.match_calls += (
            after["completed_assignments"] - before["completed_assignments"]
        )
        return result

    def build_preimages(
        self, keys: Iterable[int], mode: int
    ) -> tuple[int, ...]:
        return tuple(self.core.build_preimages(keys, mode))  # type: ignore[attr-defined]

    def check_preimage_equivalence(
        self,
        skeletons: Iterable[int],
        keys: Iterable[int],
        accepted: Iterable[int],
        mode: int,
    ) -> int:
        return int(self.core.check_preimage_equivalence(  # type: ignore[attr-defined]
            skeletons, keys, accepted, mode
        ))

    def mark_primary_logical_surface(self) -> None:
        self.primary_logical_view_surfaces += 1
        self.primary_logical_map_view_evaluations += ACTUAL_END - ACTUAL_BEGIN
        if self.primary_logical_view_surfaces > 72:
            raise DANI001CalibrationError(
                "ACTUAL primary logical surface count overflow"
            )

    def mark_evidence_logical_surface(self) -> None:
        self.evidence_logical_view_surfaces += 1
        self.evidence_logical_map_view_evaluations += ACTUAL_END - ACTUAL_BEGIN
        if self.evidence_logical_view_surfaces > 18:
            raise DANI001CalibrationError(
                "ACTUAL evidence logical surface count overflow"
            )

    def mark_output_writes(self, count: int) -> None:
        if type(count) is not int or count < 0:
            raise DANI001CalibrationError("ACTUAL output counter increment invalid")
        self.output_writes += count

    def assert_complete(self, *, outputs: int | None = None) -> None:
        audit = self.core.traversal_audit()  # type: ignore[attr-defined]
        if (
            self.primary_logical_view_surfaces != 72
            or self.evidence_logical_view_surfaces != 18
            or self.primary_logical_map_view_evaluations != 261_273_528
            or self.evidence_logical_map_view_evaluations != 65_318_382
            or (
                self.primary_logical_view_surfaces
                + self.evidence_logical_view_surfaces
            ) != 90
            or (
                self.primary_logical_map_view_evaluations
                + self.evidence_logical_map_view_evaluations
            ) != 326_591_910
            or self.interval_calls <= 0
            or self.match_calls <= 0
            or audit["optimized_calls"] != self.interval_calls
            or audit["constraint_traversals"] <= 0
            or audit["branches_considered"] <= 0
            or audit["branches_pruned"] > audit["branches_considered"]
            or audit["completed_assignments"] != self.match_calls
            or audit["completed_rank_zero"] != 0
        ):
            raise DANI001CalibrationError("ACTUAL monotonic counter contract failed")
        if outputs is not None and self.output_writes != outputs:
            raise DANI001CalibrationError("ACTUAL output-write counter drift")


def _variable_types(
    core: object,
    compiled: Sequence[tuple[TypeBin, tuple[Constraint, ...]]],
    *,
    n_core: int,
    rank_begin: int,
    rank_end: int,
    threads: int,
    batch_size: int = 8,
) -> tuple[set[str], set[int]]:
    """Identify variability exclusively over the requested rank interval."""

    variable: set[str] = set()
    folios: set[int] = set()
    candidates = [(value, constraints) for value, constraints in compiled if constraints]
    for offset in range(0, len(candidates), batch_size):
        batch = candidates[offset:offset + batch_size]
        weights = [{value.normalized: 1} for value, _constraints in batch]
        vectors = _enumerate_vectors(
            core, batch, weights, n_core=n_core, rank_begin=rank_begin,
            rank_end=rank_end, threads=threads,
        )
        for (value, _constraints), vector in zip(batch, vectors, strict=True):
            minimum = int(vector.min())
            maximum = int(vector.max())
            if maximum > 1:
                raise DANI001CalibrationError("type alternatives are not disjoint")
            if minimum == 0 and maximum == 1:
                variable.add(value.normalized)
                folios.update(folio for folio, count in value.folio_counts if count)
    return variable, folios


def _actual_affix_decision_function_equivalence(
    core: ActualCoreGuard,
    bins: Sequence[TypeBin],
    direct_codes: Sequence[int],
    accepted_codes: Sequence[int],
) -> tuple[bool, str, str]:
    """Compare exact decision constraints without evaluating any mapping rank."""

    precompiled = _compiled_bins(bins, accepted_codes, 10)
    literal_compiled = _compiled_bins_literal(bins, direct_codes, 10)
    expected_order = tuple(sorted(
        (value.normalized for value in bins), key=lambda value: value.encode("utf-8")
    ))
    if (
        tuple(value.normalized for value, _constraints in precompiled)
        != expected_order
        or tuple(value.normalized for value, _constraints in literal_compiled)
        != expected_order
    ):
        raise DANI001CalibrationError("actual decision-function type order drift")
    del core  # The proof is rank-free and cannot request actual rank 0.
    expanded_digest = _compiled_decision_function_digest(
        precompiled, n_core=10
    )
    literal_digest = _compiled_decision_function_digest(
        literal_compiled, n_core=10
    )
    equal = all(
        left_constraints == right_constraints
        for (_left, left_constraints), (_right, right_constraints)
        in zip(precompiled, literal_compiled, strict=True)
    )
    return equal and expanded_digest == literal_digest, literal_digest, expanded_digest


def _neumaier_add(total: np.ndarray, correction: np.ndarray, value: np.ndarray) -> None:
    updated = total + value
    prior_dominant = np.abs(total) >= np.abs(value)
    correction += np.where(
        prior_dominant,
        (total - updated) + value,
        (value - updated) + total,
    )
    total[:] = updated


def _surface_vectors(
    core: object,
    surface: PrivateSurface,
    accepted_codes: Sequence[int],
    *,
    n_core: int,
    rank_begin: int,
    rank_end: int,
    threads: int,
    strict_only: bool = False,
    delete_top20: bool = False,
    candidate_rank: int | None = None,
    scalar: bool = False,
    rename_by: Sequence[int] | None = None,
    literal_direct_codes: Sequence[int] | None = None,
    capture_folio_numerators: bool = False,
    capacity_override: tuple[int, int] | None = None,
) -> SurfaceVectors:
    bins = _type_bins(surface, strict_only=strict_only, delete_top20=delete_top20)
    if not bins:
        raise DANI001CalibrationError("view has no eligible normalized types")
    compiled = (
        _compiled_bins_literal(bins, literal_direct_codes, n_core)
        if literal_direct_codes is not None
        else _compiled_bins(bins, tuple(accepted_codes), n_core)
    )
    if rename_by is not None:
        compiled = tuple(
            (value, _rename_constraints(constraints, rename_by))
            for value, constraints in compiled
        )
    token_weights = {value.normalized: value.token_count for value in bins}
    type_weights = {value.normalized: 1 for value in bins}
    raw = _enumerate_vectors(
        core, compiled, (token_weights, type_weights), n_core=n_core,
        rank_begin=rank_begin, rank_end=rank_end, threads=threads, scalar=scalar,
    )
    folio_counts: dict[int, dict[str, int]] = defaultdict(dict)
    folio_denominators: dict[int, int] = defaultdict(int)
    for value in bins:
        for folio, count in value.folio_counts:
            folio_counts[folio][value.normalized] = count
            folio_denominators[folio] += count
    folio_order = tuple(sorted(folio_counts))
    width = rank_end - rank_begin
    total = np.zeros(width, dtype="<f8")
    correction = np.zeros(width, dtype="<f8")
    advantages: list[float] | None = [] if candidate_rank is not None else None
    captured: list[np.ndarray] | None = [] if capture_folio_numerators else None
    candidate_offset = None
    if candidate_rank is not None:
        if not rank_begin <= candidate_rank < rank_end:
            raise DANI001CalibrationError("candidate rank outside scored interval")
        candidate_offset = candidate_rank - rank_begin
    for offset in range(0, len(folio_order), 8):
        folios = folio_order[offset:offset + 8]
        vectors = _enumerate_vectors(
            core, compiled, tuple(folio_counts[value] for value in folios),
            n_core=n_core, rank_begin=rank_begin, rank_end=rank_end,
            threads=threads, scalar=scalar,
        )
        for folio, numerator in zip(folios, vectors, strict=True):
            if captured is not None:
                captured.append(numerator.copy())
            values = numerator.astype("<f8") / folio_denominators[folio]
            _neumaier_add(total, correction, values)
            if advantages is not None and candidate_offset is not None:
                median = _median_vector(values)
                advantages.append(float(values[candidate_offset]) - median)
    equal_folio = (total + correction) / len(folio_order)
    if capacity_override is None:
        variable, capacity_folios = _variable_types(
            core, compiled, n_core=n_core, rank_begin=max(1, rank_begin),
            rank_end=rank_end, threads=threads,
        )
        variable_count = len(variable)
        capacity_folio_count = len(capacity_folios)
    else:
        variable_count, capacity_folio_count = capacity_override
    return SurfaceVectors(
        token=raw[0],
        type=raw[1],
        folio=equal_folio,
        token_denominator=sum(value.token_count for value in bins),
        type_denominator=len(bins),
        folio_count=len(folio_order),
        variable_type_count=variable_count,
        capacity_folio_count=capacity_folio_count,
        folio_advantages=None if advantages is None else tuple(advantages),
        folio_numerators=None if captured is None else tuple(captured),
        folio_denominators=tuple(folio_denominators[value] for value in folio_order),
    )


def _mean_sd(values: np.ndarray) -> tuple[float, float]:
    count = len(values)
    if count == 0:
        raise DANI001CalibrationError("empty distribution")
    mean = math.fsum(float(value) for value in values) / count
    variance = math.fsum((float(value) - mean) ** 2 for value in values) / count
    sd = math.sqrt(variance)
    return _positive_zero(mean), _positive_zero(sd)


def _median_vector(values: np.ndarray) -> float:
    ordered = np.sort(np.asarray(values))
    count = len(ordered)
    if not count:
        raise DANI001CalibrationError("empty median")
    midpoint = count // 2
    if count % 2:
        return float(ordered[midpoint])
    return (float(ordered[midpoint - 1]) + float(ordered[midpoint])) / 2.0


@dataclass(slots=True)
class JointDistribution:
    surfaces: tuple[SurfaceVectors, ...] = field(repr=False)
    standardized: tuple[np.ndarray, ...] = field(repr=False)
    joint_t: np.ndarray = field(repr=False)
    means: tuple[float, ...]
    sds: tuple[float, ...]
    medians: tuple[float, ...]


def _joint_distribution(surfaces: Sequence[SurfaceVectors]) -> JointDistribution:
    if len(surfaces) != 6:
        raise DANI001CalibrationError("joint score requires six surfaces")
    raw_vectors = tuple(
        surface.vector(weight)
        for surface in surfaces
        for weight in WEIGHT_ORDER
    )
    means_sds = tuple(_mean_sd(value) for value in raw_vectors)
    if any(not math.isfinite(sd) or sd <= 0.0 for _mean, sd in means_sds):
        raise DANI001CalibrationError("nonpositive component SD")
    standardized = tuple(
        (value.astype("<f8") - mean) / sd
        for value, (mean, sd) in zip(raw_vectors, means_sds, strict=True)
    )
    joint = standardized[0].copy()
    for value in standardized[1:]:
        np.minimum(joint, value, out=joint)
    return JointDistribution(
        surfaces=tuple(surfaces),
        standardized=standardized,
        joint_t=joint,
        means=tuple(value[0] for value in means_sds),
        sds=tuple(value[1] for value in means_sds),
        medians=tuple(_median_vector(value) for value in raw_vectors),
    )


def _candidate_gates(
    distribution: JointDistribution,
    candidate_rank: int,
    *,
    tail_threshold: float,
    t_threshold: float,
) -> dict[str, object]:
    if not 0 <= candidate_rank < len(distribution.joint_t):
        raise DANI001CalibrationError("synthetic candidate rank outside vector")
    observed_t = float(distribution.joint_t[candidate_rank])
    inclusive = int(np.count_nonzero(distribution.joint_t >= observed_t))
    tail = inclusive / len(distribution.joint_t)
    raw_vectors = tuple(
        surface.vector(weight)
        for surface in distribution.surfaces
        for weight in WEIGHT_ORDER
    )
    denominators = tuple(
        surface.denominator(weight)
        for surface in distribution.surfaces
        for weight in WEIGHT_ORDER
    )
    absolute = tuple(
        (float(vector[candidate_rank]) - median) / denominator
        for vector, median, denominator in zip(
            raw_vectors, distribution.medians, denominators, strict=True
        )
    )
    advantages = tuple(
        surface.folio_advantages or () for surface in distribution.surfaces
    )
    positive_fraction = []
    concentrated = []
    for values in advantages:
        if not values:
            positive_fraction.append(False)
            concentrated.append(False)
            continue
        positives = sorted((max(0.0, value) for value in values), reverse=True)
        total = math.fsum(positives)
        positive_fraction.append(
            sum(value > 0.0 for value in values) / len(values) >= 0.60
        )
        concentrated.append(
            total > 0.0
            and positives[0] / total <= 0.10
            and math.fsum(positives[:5]) / total <= 0.25
        )
    return {
        "tail": _positive_zero(tail),
        "observed_t": _positive_zero(observed_t),
        "inclusive": inclusive,
        "rank_gate": tail <= tail_threshold and observed_t >= t_threshold,
        "absolute_gate": all(value >= 0.020 for value in absolute),
        "folio_positive_gate": all(positive_fraction),
        "folio_concentration_gate": all(concentrated),
        "absolute_effects": absolute,
    }


def _aggregate_assertions(
    control: str,
    assertion_ids: Sequence[str],
    values: Mapping[str, bool],
    *,
    evidence: Mapping[str, str] | None = None,
    successful: int | None = None,
    false_passes: int | None = None,
) -> dict[str, object]:
    if len(assertion_ids) != len(set(assertion_ids)) or set(assertion_ids) != set(values):
        raise DANI001CalibrationError("atomic assertion inventory mismatch")
    ordered = [(value, bool(values[value])) for value in assertion_ids]
    passed = sum(value for _name, value in ordered)
    if control == "plants":
        if successful is None or false_passes is not None:
            raise DANI001CalibrationError("plant aggregate metadata missing")
        gate = successful >= 95
    elif control == "nulls":
        if false_passes is None or successful is not None:
            raise DANI001CalibrationError("null aggregate metadata missing")
        gate = false_passes <= 1 and passed == len(ordered)
    else:
        if successful is not None or false_passes is not None:
            raise DANI001CalibrationError("unexpected aggregate metadata")
        gate = passed == len(ordered)
    evidence_control = control in {"affix_equivalence", "unreachable_invariance"}
    if evidence_control:
        if (
            evidence is None
            or set(evidence) != set(assertion_ids)
            or any(not HEX64.fullmatch(str(value)) for value in evidence.values())
        ):
            raise DANI001CalibrationError("evidence assertion inventory mismatch")
    elif evidence is not None:
        raise DANI001CalibrationError("unexpected assertion evidence")
    assertions = []
    for name, value in ordered:
        assertion: dict[str, object] = {"id": name, "passed": value}
        if evidence_control:
            assert evidence is not None
            assertion["evidence_sha256"] = evidence[name]
        assertions.append(assertion)
    base: dict[str, object] = {
        "control": control,
        "assertions": assertions,
        "total": len(ordered),
        "passed": passed,
        "failed": len(ordered) - passed,
        "gate": gate,
    }
    if control == "plants":
        base.update(successful=successful, threshold=95)
    if control == "nulls":
        base.update(false_passes=false_passes, threshold=1)
    public = {
        key: value for key, value in base.items()
        if key not in {"control", "assertions"}
    }
    public["aggregate_sha256"] = _sha256(_canonical_json(base))
    return public


def _core_view_codes(core: object, direct_codes: Sequence[int], deposited: bool) -> tuple[int, ...]:
    values = tuple(sorted(set(int(value) for value in direct_codes)))
    if not deposited:
        return values
    return tuple(int(value) for value in core.build_preimages(values, 1))


def _synthetic_direct_codes(world: object) -> tuple[int, ...]:
    output = set()
    for record in world.lexicon:  # type: ignore[attr-defined]
        key = record["key"]
        if key and all(value in NIBBLE_CODE for value in key):
            output.add(_encode_codes(tuple(NIBBLE_CODE[value] for value in key)))
    if not output:
        raise DANI001CalibrationError("synthetic lexicon has no reachable key")
    return tuple(sorted(output))


def _synthetic_surfaces(generator: object, world: object) -> tuple[PrivateSurface, ...]:
    output = []
    for edition in EDITION_ORDER:
        for panel_name in PANEL_ORDER:
            projection = generator.panel_projection(world.rows, panel_name)
            output.append(_surface_from_projection(edition, panel_name, projection))
    if len(output) != 6:
        raise DANI001CalibrationError("synthetic surface inventory drift")
    if any(not value.tokens for value in output):
        raise DANI001CalibrationError("synthetic surface has a missing edition/panel")
    return tuple(output)


def _capacity_pass(
    distribution: JointDistribution | None,
    *,
    min_types: int,
    min_folios: int,
) -> bool:
    return bool(
        distribution is not None
        and all(value.variable_type_count >= min_types for value in distribution.surfaces)
        and all(value.capacity_folio_count >= min_folios for value in distribution.surfaces)
        and all(sd > 0.0 and math.isfinite(sd) for sd in distribution.sds)
    )


def _try_joint(surfaces: Sequence[SurfaceVectors]) -> JointDistribution | None:
    try:
        return _joint_distribution(surfaces)
    except DANI001CalibrationError as error:
        if str(error) != "nonpositive component SD":
            raise
        return None


@dataclass(slots=True)
class WorldEvaluation:
    world_id: str
    family: str
    candidate_rank: int
    primary: JointDistribution | None = field(repr=False)
    top20: JointDistribution | None = field(repr=False)
    strict: JointDistribution | None = field(repr=False)
    direct: JointDistribution | None = field(repr=False)
    direct_surfaces: tuple[SurfaceVectors, ...] = field(repr=False)
    robustness: dict[str, JointDistribution | None] = field(repr=False)
    primary_gates: dict[str, object] | None = field(repr=False)
    top20_gates: dict[str, object] | None = field(repr=False)
    strict_gates: dict[str, object] | None = field(repr=False)
    direct_gates: dict[str, object] | None = field(repr=False)
    world_signature: bool
    all_required_gates: bool
    affix_equivalence: bool
    unreachable_invariance: bool
    affix_evidence_sha256: str
    unreachable_evidence_sha256: str | None


def _synthetic_view_records(
    world: object, view_name: str
) -> tuple[Mapping[str, object], ...]:
    records = tuple(world.lexicon)  # type: ignore[attr-defined]
    if view_name in {
        "FULL_DEPOSITED_AFFIX", "DIRECT_ONLY", "STRICT_LITERAL",
        "TOP20_DELETED",
    }:
        selected = records
    elif view_name == "STRICT_NO_FUNCTION":
        selected = tuple(
            record for record in records
            if all(
                entry.get("domain") != "function"
                for entry in record["entries"]
            )
        )
    elif view_name == "SOURCE_PRESENT":
        selected = tuple(
            record for record in records
            if any(
                bool(entry.get("source_present"))
                for entry in record["entries"]
            )
        )
    elif view_name.startswith("LEAVE_") and view_name.endswith("_OUT"):
        domain = view_name.removeprefix("LEAVE_").removesuffix("_OUT").lower()
        if domain not in SYNTHETIC_DOMAINS:
            raise DANI001CalibrationError("unknown synthetic domain view")
        selected = tuple(
            record for record in records
            if any(entry.get("domain") != domain for entry in record["entries"])
        )
    else:
        raise DANI001CalibrationError("unknown synthetic scoring view")
    return selected


def _synthetic_view_direct_codes(world: object, view_name: str) -> tuple[int, ...]:
    selected = _synthetic_view_records(world, view_name)
    output = {
        _encode_codes(tuple(NIBBLE_CODE[value] for value in record["key"]))
        for record in selected
        if record["key"]
        and all(value in NIBBLE_CODE for value in record["key"])
    }
    if not output:
        raise DANI001CalibrationError("synthetic view has no reachable key")
    return tuple(sorted(output))


def _robustness_pass(
    distribution: JointDistribution | None,
    candidate_rank: int,
    *,
    min_types: int,
    min_folios: int,
    require_positive_effects: bool = False,
) -> bool:
    gates = _gates_or_none(
        distribution, candidate_rank, tail_threshold=0.01, t_threshold=2.0
    )
    return bool(
        _capacity_pass(
            distribution, min_types=min_types, min_folios=min_folios
        )
        and gates
        and gates["rank_gate"]
        and (
            not require_positive_effects
            or all(value > 0.0 for value in gates["absolute_effects"])
        )
    )


def _null_probe_independence(world: object) -> bool:
    if world.secret_rank is not None or world.alternate_rank is not None:
        return False
    key_uses = tuple(
        value for value in world.generator_fields
        if value.label == "null-key-tail"
    )
    probe_uses = tuple(
        value for value in world.generator_fields
        if value.label == "null-probe-rank"
    )
    return bool(
        key_uses
        and probe_uses
        and all(len(value.integer_fields) == 4 for value in key_uses)
        and all(
            value.integer_fields[1] == int(world.trial_index)
            for value in key_uses
        )
        and all(
            value.integer_fields[1:] == (int(world.trial_index), 0)
            for value in probe_uses
        )
        and not any(
            value.label == "null-probe-rank" for value in key_uses
        )
    )


def _score_surface_set(
    core: object,
    surfaces: Sequence[PrivateSurface],
    accepted_codes: Sequence[int],
    *,
    n_core: int,
    candidate_rank: int,
    strict_only: bool = False,
    delete_top20: bool = False,
    threads: int = WORKERS,
    scalar: bool = False,
    rename_by: Sequence[int] | None = None,
    literal_direct_codes: Sequence[int] | None = None,
    capture_folio_numerators: bool = False,
    capacity_reference: Sequence[SurfaceVectors] | None = None,
) -> JointDistribution | None:
    scored = _surface_set_vectors(
        core,
        surfaces,
        accepted_codes,
        n_core=n_core,
        candidate_rank=candidate_rank,
        strict_only=strict_only,
        delete_top20=delete_top20,
        threads=threads,
        scalar=scalar,
        rename_by=rename_by,
        literal_direct_codes=literal_direct_codes,
        capture_folio_numerators=capture_folio_numerators,
        capacity_reference=capacity_reference,
    )
    if not scored:
        return None
    return _try_joint(scored)


def _surface_set_vectors(
    core: object,
    surfaces: Sequence[PrivateSurface],
    accepted_codes: Sequence[int],
    *,
    n_core: int,
    candidate_rank: int | None,
    strict_only: bool = False,
    delete_top20: bool = False,
    threads: int = WORKERS,
    scalar: bool = False,
    rename_by: Sequence[int] | None = None,
    literal_direct_codes: Sequence[int] | None = None,
    capture_folio_numerators: bool = False,
    capacity_reference: Sequence[SurfaceVectors] | None = None,
) -> tuple[SurfaceVectors, ...]:
    scored = []
    empty_surface: SurfaceVectors | None = None
    if capacity_reference is not None and len(capacity_reference) != len(surfaces):
        raise DANI001CalibrationError("capacity-reference surface count drift")
    for surface_index, surface in enumerate(surfaces):
        bins = _type_bins(
            surface, strict_only=strict_only, delete_top20=delete_top20
        )
        if not bins:
            if empty_surface is None:
                width = math.factorial(n_core)
                zero_u4 = np.zeros(width, dtype="<u4")
                empty_surface = SurfaceVectors(
                    token=zero_u4,
                    type=zero_u4,
                    folio=np.zeros(width, dtype="<f8"),
                    token_denominator=0,
                    type_denominator=0,
                    folio_count=0,
                    variable_type_count=0,
                    capacity_folio_count=0,
                    folio_advantages=() if candidate_rank is not None else None,
                    folio_numerators=() if capture_folio_numerators else None,
                    folio_denominators=(),
                )
            scored.append(empty_surface)
            continue
        scored.append(_surface_vectors(
            core,
            surface,
            accepted_codes,
            n_core=n_core,
            rank_begin=0,
            rank_end=math.factorial(n_core),
            threads=threads,
            strict_only=strict_only,
            delete_top20=delete_top20,
            candidate_rank=candidate_rank,
            scalar=scalar,
            rename_by=rename_by,
            literal_direct_codes=literal_direct_codes,
            capture_folio_numerators=capture_folio_numerators,
            capacity_override=(
                None if capacity_reference is None else (
                    capacity_reference[surface_index].variable_type_count,
                    capacity_reference[surface_index].capacity_folio_count,
                )
            ),
        ))
    return tuple(scored)


def _gates_or_none(
    distribution: JointDistribution | None,
    candidate_rank: int,
    *,
    tail_threshold: float,
    t_threshold: float,
) -> dict[str, object] | None:
    if distribution is None:
        return None
    return _candidate_gates(
        distribution,
        candidate_rank,
        tail_threshold=tail_threshold,
        t_threshold=t_threshold,
    )


def _vectors_equal(left: JointDistribution | None, right: JointDistribution | None) -> bool:
    if left is None or right is None:
        return left is right
    return (
        all(
            np.array_equal(a.vector(weight), b.vector(weight))
            for a, b in zip(left.surfaces, right.surfaces, strict=True)
            for weight in WEIGHT_ORDER
        )
        and all(np.array_equal(a, b) for a, b in zip(
            left.standardized, right.standardized, strict=True
        ))
        and np.array_equal(left.joint_t, right.joint_t)
        and left.means == right.means
        and left.sds == right.sds
        and left.medians == right.medians
        and all(
            (
                a.token_denominator,
                a.type_denominator,
                a.folio_count,
                a.variable_type_count,
                a.capacity_folio_count,
                a.folio_denominators,
                a.folio_advantages,
            )
            == (
                b.token_denominator,
                b.type_denominator,
                b.folio_count,
                b.variable_type_count,
                b.capacity_folio_count,
                b.folio_denominators,
                b.folio_advantages,
            )
            for a, b in zip(left.surfaces, right.surfaces, strict=True)
        )
        and all(
            a.folio_numerators is None
            or b.folio_numerators is None
            or all(
                np.array_equal(x, y)
                for x, y in zip(
                    a.folio_numerators, b.folio_numerators, strict=True
                )
            )
            for a, b in zip(left.surfaces, right.surfaces, strict=True)
        )
    )


def _surface_vectors_equal(left: SurfaceVectors, right: SurfaceVectors) -> bool:
    return bool(
        all(
            np.array_equal(left.vector(weighting), right.vector(weighting))
            for weighting in WEIGHT_ORDER
        )
        and (
            left.token_denominator,
            left.type_denominator,
            left.folio_count,
            left.variable_type_count,
            left.capacity_folio_count,
            left.folio_denominators,
        )
        == (
            right.token_denominator,
            right.type_denominator,
            right.folio_count,
            right.variable_type_count,
            right.capacity_folio_count,
            right.folio_denominators,
        )
    )


def _surface_vector_digest(value: SurfaceVectors) -> str:
    digest = hashlib.sha256()
    digest.update(b"DANI001_PRIVATE_SURFACE_VECTORS_V1\0")
    digest.update(np.ascontiguousarray(value.token, dtype="<u4").tobytes())
    digest.update(np.ascontiguousarray(value.type, dtype="<u4").tobytes())
    folio = np.array(value.folio, dtype="<f8", order="C", copy=True)
    folio[folio == 0.0] = 0.0
    digest.update(folio.tobytes())
    return digest.hexdigest()


def _distribution_digest(value: JointDistribution | None) -> str:
    """Private aggregate binding of every raw and derived score-vector byte."""

    digest = hashlib.sha256()
    digest.update(b"DANI001_PRIVATE_DISTRIBUTION_V1\0")
    if value is None:
        digest.update(b"NONE")
        return digest.hexdigest()
    for surface in value.surfaces:
        digest.update(np.ascontiguousarray(surface.token, dtype="<u4").tobytes())
        digest.update(np.ascontiguousarray(surface.type, dtype="<u4").tobytes())
        folio = np.array(surface.folio, dtype="<f8", order="C", copy=True)
        folio[folio == 0.0] = 0.0
        digest.update(folio.tobytes())
    for vector in value.standardized:
        standardized = np.array(vector, dtype="<f8", order="C", copy=True)
        standardized[standardized == 0.0] = 0.0
        digest.update(standardized.tobytes())
    joint = np.array(value.joint_t, dtype="<f8", order="C", copy=True)
    joint[joint == 0.0] = 0.0
    digest.update(joint.tobytes())
    digest.update(_canonical_json({
        "means": value.means,
        "sds": value.sds,
        "medians": value.medians,
    }))
    return digest.hexdigest()


def _component_evidence_array(
    private_surfaces: Sequence[PrivateSurface],
    by_view: Mapping[str, Sequence[SurfaceVectors]],
) -> list[dict[str, object]]:
    """Build the registered private-identity-free raw/standardized evidence."""

    expected_surfaces = tuple(
        (edition, panel)
        for edition in EDITION_ORDER for panel in PANEL_ORDER
    )
    if (
        tuple((value.edition, value.panel) for value in private_surfaces)
        != expected_surfaces
        or tuple(by_view) != VIEW_ORDER
    ):
        raise DANI001CalibrationError("synthetic evidence surface/view inventory drift")
    output: list[dict[str, object]] = []
    for view_name in VIEW_ORDER:
        vectors = tuple(by_view[view_name])
        if len(vectors) != len(private_surfaces):
            raise DANI001CalibrationError("synthetic evidence surface count drift")
        for surface, scored in zip(private_surfaces, vectors, strict=True):
            for weighting in WEIGHT_ORDER:
                raw = scored.vector(weighting)
                dtype = "<f8" if weighting == "FOLIO" else "<u4"
                raw_sha = _f8_digest(raw) if weighting == "FOLIO" else _u4_digest(raw)
                mean, sd = _mean_sd(raw)
                standardized_sha: str | None = None
                if math.isfinite(sd) and sd > 0.0:
                    standardized_sha = _f8_digest(
                        (raw.astype("<f8") - mean) / sd
                    )
                output.append({
                    "view": view_name,
                    "edition": surface.edition,
                    "panel": surface.panel,
                    "weighting": weighting,
                    "raw_dtype": dtype,
                    "raw_sha256": raw_sha,
                    "standardized_sha256": standardized_sha,
                })
    if len(output) != 216:
        raise DANI001CalibrationError("synthetic evidence component count drift")
    return output


def _update_decision_function_digest(
    digest: "hashlib._Hash",
    compiled: Sequence[tuple[TypeBin, tuple[Constraint, ...]]],
    *,
    n_core: int,
) -> None:
    digest.update(struct.pack("<I", len(compiled)))
    for _value, constraints in compiled:
        ordered = tuple(sorted(
            set(constraints), key=lambda item: (item.mask, item.required)
        ))
        digest.update(struct.pack("<I", len(ordered)))
        for constraint in ordered:
            if not 0 <= constraint.mask < 1 << n_core:
                raise DANI001CalibrationError("decision constraint mask drift")
            if (
                len(constraint.required) != n_core
                or any(
                    value != 255 and not 0 <= value < n_core
                    for value in constraint.required
                )
            ):
                raise DANI001CalibrationError(
                    "decision required-output tuple drift"
                )
            digest.update(struct.pack("<H", constraint.mask))
            digest.update(bytes(constraint.required))


def _compiled_decision_function_digest(
    compiled: Sequence[tuple[TypeBin, tuple[Constraint, ...]]],
    *,
    n_core: int,
) -> str:
    digest = hashlib.sha256()
    digest.update(b"DANI001-DECISION-FUNCTION-V1\0")
    digest.update(bytes((n_core,)))
    _update_decision_function_digest(digest, compiled, n_core=n_core)
    return digest.hexdigest()


def _decision_function_digest(
    private_surfaces: Sequence[PrivateSurface],
    view_definitions: Mapping[
        str, tuple[Sequence[int], Sequence[int], bool, bool]
    ],
    *,
    n_core: int,
    literal: bool,
    view_order: Sequence[str] = VIEW_ORDER,
) -> str:
    """Hash the registered identity-free canonical Boolean constraint stream."""

    expected_surfaces = tuple(
        (edition, panel)
        for edition in EDITION_ORDER for panel in PANEL_ORDER
    )
    if (
        tuple(view_definitions) != tuple(view_order)
        or tuple((value.edition, value.panel) for value in private_surfaces)
        not in {expected_surfaces, (("ZL3b", "MANUAL_GROUP"),)}
    ):
        raise DANI001CalibrationError("binary evidence view inventory drift")
    digest = hashlib.sha256()
    digest.update(b"DANI001-DECISION-FUNCTION-V1\0")
    digest.update(bytes((n_core,)))
    for view_name in view_order:
        direct_codes, accepted_codes, strict_only, delete_top20 = view_definitions[view_name]
        for surface in private_surfaces:
            bins = _type_bins(
                surface,
                strict_only=strict_only,
                delete_top20=delete_top20,
            )
            compiled = (
                _compiled_bins_literal(bins, direct_codes, n_core)
                if literal and view_name != "DIRECT_ONLY"
                else _compiled_bins(bins, accepted_codes, n_core)
            )
            if tuple(value.normalized for value, _constraints in compiled) != tuple(
                sorted((value.normalized for value in bins), key=lambda value: value.encode("utf-8"))
            ):
                raise DANI001CalibrationError("binary evidence type order drift")
            _update_decision_function_digest(digest, compiled, n_core=n_core)
    return digest.hexdigest()


def _mapped_template(
    template: Sequence[int], permutation: Sequence[int]
) -> tuple[int, ...]:
    return tuple(
        value
        if value > 0
        else NIBBLE_CODE[CORE_OUTPUTS[permutation[-value - 1]]]
        for value in template
    )


def _scalar_surface_vectors(
    surface: PrivateSurface,
    direct_codes: Sequence[int],
    *,
    n_core: int,
    deposited: bool,
    strict_only: bool,
    delete_top20: bool,
    candidate_rank: int,
) -> SurfaceVectors:
    """Direct, constraint-free scalar reference used only by frozen toys."""

    if n_core not in {4, 6}:
        raise DANI001CalibrationError("scalar reference is toy-only")
    bins = _type_bins(
        surface, strict_only=strict_only, delete_top20=delete_top20
    )
    if not bins:
        raise DANI001CalibrationError("scalar toy view has no types")
    orbit = math.factorial(n_core)
    token = np.zeros(orbit, dtype="<u4")
    type_vector = np.zeros(orbit, dtype="<u4")
    folio_order = tuple(sorted({
        folio for value in bins for folio, _count in value.folio_counts
    }))
    folio_index = {folio: index for index, folio in enumerate(folio_order)}
    folio_numerators = tuple(
        np.zeros(orbit, dtype="<u4") for _folio in folio_order
    )
    folio_denominators = tuple(
        sum(dict(value.folio_counts).get(folio, 0) for value in bins)
        for folio in folio_order
    )
    nonidentity_matches = [0] * len(bins)
    for rank, permutation in enumerate(itertools.permutations(range(n_core))):
        for type_index, value in enumerate(bins):
            skeleton = _encode_codes(_mapped_template(value.template, permutation))
            if not _literal_match_decision(
                skeleton, direct_codes, deposited=deposited
            ):
                continue
            if rank != 0:
                nonidentity_matches[type_index] += 1
            token[rank] += value.token_count
            type_vector[rank] += 1
            for folio, count in value.folio_counts:
                folio_numerators[folio_index[folio]][rank] += count
    balanced = np.zeros(orbit, dtype="<f8")
    for rank in range(orbit):
        total = 0.0
        correction = 0.0
        for vector, denominator in zip(
            folio_numerators, folio_denominators, strict=True
        ):
            value = float(vector[rank]) / denominator
            updated = total + value
            correction += (
                (total - updated) + value
                if abs(total) >= abs(value)
                else (value - updated) + total
            )
            total = updated
        balanced[rank] = (total + correction) / len(folio_order)
    variable_flags = tuple(
        0 < count < orbit - 1 for count in nonidentity_matches
    )
    capacity_folios = {
        folio
        for flag, value in zip(variable_flags, bins, strict=True)
        if flag
        for folio, count in value.folio_counts
        if count
    }
    advantages = tuple(
        float(vector[candidate_rank]) / denominator
        - _median_vector(vector.astype("<f8") / denominator)
        for vector, denominator in zip(
            folio_numerators, folio_denominators, strict=True
        )
    )
    return SurfaceVectors(
        token=token,
        type=type_vector,
        folio=balanced,
        token_denominator=sum(value.token_count for value in bins),
        type_denominator=len(bins),
        folio_count=len(folio_order),
        variable_type_count=sum(variable_flags),
        capacity_folio_count=len(capacity_folios),
        folio_advantages=advantages,
        folio_numerators=folio_numerators,
        folio_denominators=folio_denominators,
    )


def _candidate_rank_counts(
    distribution: JointDistribution | None, candidate_rank: int
) -> tuple[int, int, int] | None:
    if distribution is None:
        return None
    observed = distribution.joint_t[candidate_rank]
    better = int(np.count_nonzero(distribution.joint_t > observed))
    ties = int(np.count_nonzero(distribution.joint_t == observed))
    return better, ties, better + ties


def _scalar_joint_distribution(
    surfaces: Sequence[SurfaceVectors],
) -> JointDistribution | None:
    if len(surfaces) != 6:
        raise DANI001CalibrationError("scalar joint surface inventory drift")
    raw = tuple(
        surface.vector(weighting)
        for surface in surfaces
        for weighting in WEIGHT_ORDER
    )
    means: list[float] = []
    sds: list[float] = []
    medians: list[float] = []
    standardized: list[np.ndarray] = []
    for vector in raw:
        values = tuple(float(item) for item in vector)
        mean = math.fsum(values) / len(values)
        variance = math.fsum((item - mean) ** 2 for item in values) / len(values)
        sd = math.sqrt(variance)
        if not math.isfinite(sd) or sd <= 0.0:
            return None
        ordered = sorted(values)
        midpoint = len(ordered) // 2
        median = (
            ordered[midpoint]
            if len(ordered) % 2
            else (ordered[midpoint - 1] + ordered[midpoint]) / 2.0
        )
        means.append(_positive_zero(mean))
        sds.append(_positive_zero(sd))
        medians.append(_positive_zero(median))
        standardized.append(np.asarray(
            tuple((item - mean) / sd for item in values), dtype="<f8"
        ))
    joint = np.asarray(
        tuple(
            min(float(vector[rank]) for vector in standardized)
            for rank in range(len(standardized[0]))
        ),
        dtype="<f8",
    )
    return JointDistribution(
        surfaces=tuple(surfaces),
        standardized=tuple(standardized),
        joint_t=joint,
        means=tuple(means),
        sds=tuple(sds),
        medians=tuple(medians),
    )


def _scalar_candidate_gates(
    distribution: JointDistribution | None,
    candidate_rank: int,
    *,
    tail_threshold: float,
    t_threshold: float,
) -> dict[str, object] | None:
    if distribution is None:
        return None
    observed = float(distribution.joint_t[candidate_rank])
    inclusive = sum(float(value) >= observed for value in distribution.joint_t)
    raw = tuple(
        surface.vector(weighting)
        for surface in distribution.surfaces
        for weighting in WEIGHT_ORDER
    )
    denominators = tuple(
        surface.denominator(weighting)
        for surface in distribution.surfaces
        for weighting in WEIGHT_ORDER
    )
    effects = tuple(
        (float(vector[candidate_rank]) - median) / denominator
        for vector, median, denominator in zip(
            raw, distribution.medians, denominators, strict=True
        )
    )
    gate4 = True
    gate5 = True
    for surface in distribution.surfaces:
        advantages = tuple(surface.folio_advantages or ())
        positives = sorted(
            (max(0.0, value) for value in advantages), reverse=True
        )
        total = math.fsum(positives)
        gate4 = gate4 and bool(advantages) and (
            sum(value > 0.0 for value in advantages) / len(advantages) >= 0.60
        )
        gate5 = gate5 and bool(positives) and total > 0.0 and (
            positives[0] / total <= 0.10
        ) and (
            math.fsum(positives[:5]) / total <= 0.25
        )
    tail = inclusive / len(distribution.joint_t)
    return {
        "tail": _positive_zero(tail),
        "observed_t": _positive_zero(observed),
        "inclusive": inclusive,
        "rank_gate": tail <= tail_threshold and observed >= t_threshold,
        "absolute_gate": all(value >= 0.020 for value in effects),
        "folio_positive_gate": gate4,
        "folio_concentration_gate": gate5,
        "absolute_effects": effects,
    }


def _toy_scalar_equivalence(
    core: object, generator: object, world: object
) -> bool:
    """Compare all twelve complete toy views to a direct Python reference."""

    n_core = int(world.variable_count)
    candidate = int(world.candidate_rank)
    surfaces = _synthetic_surfaces(generator, world)
    for view_name in VIEW_ORDER:
        direct = _synthetic_view_direct_codes(world, view_name)
        deposited = view_name != "DIRECT_ONLY"
        accepted = _core_view_codes(core, direct, deposited)
        strict_only = view_name == "STRICT_LITERAL"
        delete_top20 = view_name == "TOP20_DELETED"
        optimized_surfaces = _surface_set_vectors(
            core,
            surfaces,
            accepted,
            n_core=n_core,
            candidate_rank=candidate,
            strict_only=strict_only,
            delete_top20=delete_top20,
            threads=1,
            capture_folio_numerators=True,
        )
        if not optimized_surfaces:
            return False
        scalar_surfaces = tuple(
            _scalar_surface_vectors(
                surface,
                direct,
                n_core=n_core,
                deposited=deposited,
                strict_only=strict_only,
                delete_top20=delete_top20,
                candidate_rank=candidate,
            )
            for surface in surfaces
        )
        optimized = _try_joint(optimized_surfaces)
        scalar = _scalar_joint_distribution(scalar_surfaces)
        if not _vectors_equal(optimized, scalar):
            return False
        for left, right in zip(
            optimized_surfaces, scalar_surfaces, strict=True
        ):
            if (
                _u4_digest(left.token) != _u4_digest(right.token)
                or _u4_digest(left.type) != _u4_digest(right.type)
                or _f8_digest(left.folio) != _f8_digest(right.folio)
            ):
                return False
        threshold = (0.001, 3.0) if view_name == "FULL_DEPOSITED_AFFIX" else (0.01, 2.0)
        optimized_gates = _gates_or_none(
            optimized, candidate, tail_threshold=threshold[0],
            t_threshold=threshold[1]
        )
        scalar_gates = _scalar_candidate_gates(
            scalar,
            candidate,
            tail_threshold=threshold[0],
            t_threshold=threshold[1],
        )
        scalar_counts = None
        if scalar is not None:
            scalar_observed = float(scalar.joint_t[candidate])
            scalar_better = sum(
                float(value) > scalar_observed for value in scalar.joint_t
            )
            scalar_ties = sum(
                float(value) == scalar_observed for value in scalar.joint_t
            )
            scalar_counts = (
                scalar_better, scalar_ties, scalar_better + scalar_ties
            )
        if (
            optimized_gates != scalar_gates
            or _candidate_rank_counts(optimized, candidate)
            != scalar_counts
        ):
            return False
        if view_name == "TOP20_DELETED":
            capacity = (80, 20)
        elif view_name == "SOURCE_PRESENT":
            capacity = (30, 10)
        else:
            capacity = (100, 20)
        optimized_capacity = _capacity_pass(
            optimized, min_types=capacity[0], min_folios=capacity[1]
        )
        scalar_capacity = _capacity_pass(
            scalar, min_types=capacity[0], min_folios=capacity[1]
        )
        if optimized_capacity != scalar_capacity:
            return False
        require_effect = view_name.startswith("LEAVE_")
        optimized_decision = bool(
            optimized_capacity
            and optimized_gates
            and optimized_gates["rank_gate"]
            and (
                not require_effect
                or all(value > 0.0 for value in optimized_gates["absolute_effects"])
            )
        )
        scalar_decision = bool(
            scalar_capacity
            and scalar_gates
            and scalar_gates["rank_gate"]
            and (
                not require_effect
                or all(value > 0.0 for value in scalar_gates["absolute_effects"])
            )
        )
        if optimized_decision != scalar_decision:
            return False
    return True


def _evaluate_world(
    core: object,
    generator: object,
    world: object,
    *,
    threads: int = WORKERS,
    require_scalar: bool = False,
) -> WorldEvaluation:
    n_core = int(world.variable_count)
    candidate_rank = int(world.candidate_rank)
    surfaces = _synthetic_surfaces(generator, world)
    direct_codes = _synthetic_view_direct_codes(world, "FULL_DEPOSITED_AFFIX")
    literal_affix = _accepted_preimages_literal(direct_codes)
    core_affix = _core_view_codes(core, direct_codes, True)
    affix_constraints_equal = bool(
        literal_affix == core_affix
        and all(
            _affix_constraint_equivalence(
                core,
                _type_bins(
                    surface, strict_only=False, delete_top20=False
                ),
                direct_codes,
                core_affix,
                n_core,
            )
            for surface in surfaces
        )
    )

    # Build the remove state, retain the exact removed records, and construct
    # restoration only by adding that saved set back to the remove state.
    full_records = tuple(world.lexicon)
    reachable_only = tuple(
        record for record in world.lexicon
        if record["key"] and all(value in NIBBLE_CODE for value in record["key"])
    )
    saved_unreachable = tuple(
        record for record in world.lexicon if record not in reachable_only
    )
    if len({str(record["key"]) for record in full_records}) != len(full_records):
        raise DANI001CalibrationError("synthetic full lexicon duplicate key")
    restored_records = tuple(sorted(
        (*reachable_only, *saved_unreachable),
        key=lambda record: str(record["key"]).encode("utf-8"),
    ))
    if (
        len(restored_records) != len(reachable_only) + len(saved_unreachable)
        or _canonical_json(list(restored_records))
        != _canonical_json(list(full_records))
    ):
        raise DANI001CalibrationError("synthetic remove/add restoration drift")
    without_codes = tuple(sorted({
        _encode_codes(tuple(NIBBLE_CODE[value] for value in record["key"]))
        for record in reachable_only
    }))
    unreachable_inputs_equal = (
        without_codes == direct_codes
        and _accepted_preimages_literal(without_codes) == literal_affix
    )

    primary_surfaces = _surface_set_vectors(
        core, surfaces, core_affix, n_core=n_core,
        candidate_rank=candidate_rank, threads=threads,
    )
    primary = _try_joint(primary_surfaces) if primary_surfaces else None
    literal_primary_surfaces = _surface_set_vectors(
        core,
        surfaces,
        core_affix,
        n_core=n_core,
        candidate_rank=candidate_rank,
        threads=threads,
        literal_direct_codes=direct_codes,
        capacity_reference=primary_surfaces,
    )
    literal_primary = (
        _try_joint(literal_primary_surfaces) if literal_primary_surfaces else None
    )
    affix_equivalence = bool(
        affix_constraints_equal
        and _vectors_equal(primary, literal_primary)
        and _distribution_digest(primary) == _distribution_digest(literal_primary)
    )
    if not affix_equivalence:
        raise DANI001CalibrationError(
            "synthetic literal/preexpanded score invariant failed"
        )
    if n_core == 10:
        without_primary_surfaces = _surface_set_vectors(
            core,
            surfaces,
            _core_view_codes(core, without_codes, True),
            n_core=n_core,
            candidate_rank=candidate_rank,
            threads=threads,
            capacity_reference=primary_surfaces,
        )
        without_primary = (
            _try_joint(without_primary_surfaces)
            if without_primary_surfaces else None
        )
        unreachable_invariance = bool(
            unreachable_inputs_equal
            and _vectors_equal(primary, without_primary)
            and _distribution_digest(primary)
            == _distribution_digest(without_primary)
        )
    else:
        without_primary_surfaces = primary_surfaces
        unreachable_invariance = True
    top20_surfaces = _surface_set_vectors(
        core, surfaces, core_affix, n_core=n_core,
        candidate_rank=candidate_rank, delete_top20=True, threads=threads,
    )
    top20 = _try_joint(top20_surfaces) if top20_surfaces else None
    strict_surfaces = _surface_set_vectors(
        core, surfaces, core_affix, n_core=n_core,
        candidate_rank=candidate_rank, strict_only=True, threads=threads,
    )
    strict = _try_joint(strict_surfaces) if strict_surfaces else None
    direct_surfaces = _surface_set_vectors(
        core,
        surfaces,
        direct_codes,
        n_core=n_core,
        candidate_rank=candidate_rank,
        threads=threads,
    )
    direct = _try_joint(direct_surfaces) if direct_surfaces else None
    robustness: dict[str, JointDistribution | None] = {}
    robustness_surfaces: dict[str, tuple[SurfaceVectors, ...]] = {}
    for view_name in (
        "STRICT_NO_FUNCTION", "SOURCE_PRESENT",
        *(f"LEAVE_{domain.upper()}_OUT" for domain in SYNTHETIC_DOMAINS),
    ):
        view_direct = _synthetic_view_direct_codes(world, view_name)
        view_accepted = _core_view_codes(core, view_direct, True)
        if view_accepted == core_affix:
            distribution = primary
            scored_surfaces = primary_surfaces
        else:
            scored_surfaces = _surface_set_vectors(
                core,
                surfaces,
                view_accepted,
                n_core=n_core,
                candidate_rank=candidate_rank,
                threads=threads,
            )
            distribution = _try_joint(scored_surfaces) if scored_surfaces else None
        robustness[view_name] = distribution
        robustness_surfaces[view_name] = scored_surfaces

    expanded_by_view: dict[str, tuple[SurfaceVectors, ...]] = {
        "FULL_DEPOSITED_AFFIX": primary_surfaces,
        "DIRECT_ONLY": direct_surfaces,
        "STRICT_NO_FUNCTION": robustness_surfaces["STRICT_NO_FUNCTION"],
        "STRICT_LITERAL": strict_surfaces,
        "TOP20_DELETED": top20_surfaces,
        "SOURCE_PRESENT": robustness_surfaces["SOURCE_PRESENT"],
        **{
            f"LEAVE_{domain.upper()}_OUT": robustness_surfaces[
                f"LEAVE_{domain.upper()}_OUT"
            ]
            for domain in SYNTHETIC_DOMAINS
        },
    }
    view_definitions: dict[
        str, tuple[tuple[int, ...], tuple[int, ...], bool, bool]
    ] = {}
    literal_by_view: dict[str, tuple[SurfaceVectors, ...]] = {}
    for view_name in VIEW_ORDER:
        view_direct = _synthetic_view_direct_codes(world, view_name)
        deposited = view_name != "DIRECT_ONLY"
        view_accepted = _core_view_codes(core, view_direct, deposited)
        strict_only = view_name == "STRICT_LITERAL"
        delete_top20 = view_name == "TOP20_DELETED"
        view_definitions[view_name] = (
            tuple(view_direct), tuple(view_accepted), strict_only, delete_top20
        )
        if not deposited:
            literal_scored = _surface_set_vectors(
                core,
                surfaces,
                view_accepted,
                n_core=n_core,
                candidate_rank=candidate_rank,
                threads=threads,
                strict_only=strict_only,
                delete_top20=delete_top20,
                capacity_reference=expanded_by_view[view_name],
            )
        elif (
            view_direct == direct_codes
            and not strict_only
            and not delete_top20
        ):
            literal_scored = literal_primary_surfaces
        else:
            literal_scored = _surface_set_vectors(
                core,
                surfaces,
                view_accepted,
                n_core=n_core,
                candidate_rank=candidate_rank,
                threads=threads,
                strict_only=strict_only,
                delete_top20=delete_top20,
                literal_direct_codes=view_direct,
                capacity_reference=expanded_by_view[view_name],
            )
        literal_by_view[view_name] = literal_scored

    expanded_evidence = _component_evidence_array(surfaces, expanded_by_view)
    literal_evidence = _component_evidence_array(surfaces, literal_by_view)
    expanded_decision = _decision_function_digest(
        surfaces,
        view_definitions,
        n_core=n_core,
        literal=False,
    )
    literal_decision = _decision_function_digest(
        surfaces,
        view_definitions,
        n_core=n_core,
        literal=True,
    )
    derived_affix_equal = True
    for view_name in VIEW_ORDER:
        expanded_distribution = (
            _try_joint(expanded_by_view[view_name])
            if expanded_by_view[view_name] else None
        )
        literal_distribution = (
            _try_joint(literal_by_view[view_name])
            if literal_by_view[view_name] else None
        )
        derived_affix_equal = bool(
            derived_affix_equal
            and _vectors_equal(expanded_distribution, literal_distribution)
            and _distribution_digest(expanded_distribution)
            == _distribution_digest(literal_distribution)
        )
        del expanded_distribution, literal_distribution
    affix_equivalence = bool(
        affix_equivalence
        and expanded_decision == literal_decision
        and expanded_evidence == literal_evidence
        and all(
            _surface_vectors_equal(left, right)
            for view_name in VIEW_ORDER
            for left, right in zip(
                expanded_by_view[view_name],
                literal_by_view[view_name],
                strict=True,
            )
        )
        and derived_affix_equal
    )
    if not affix_equivalence:
        raise DANI001CalibrationError(
            "synthetic whole-view affix evidence invariant failed"
        )
    affix_evidence_sha256 = _sha256(_canonical_json({
        "schema": "dani001-affix-evidence-v1",
        "world_id": str(world.world_id),
        "literal_decision_function_sha256": literal_decision,
        "expanded_decision_function_sha256": expanded_decision,
        "literal": literal_evidence,
        "expanded": expanded_evidence,
    }))

    unreachable_evidence_sha256: str | None = None
    if n_core == 10:
        without_by_view = dict(expanded_by_view)
        without_by_view["FULL_DEPOSITED_AFFIX"] = without_primary_surfaces
        restored_by_view = dict(expanded_by_view)
        restored_primary_codes = _core_view_codes(
            core,
            _synthetic_view_direct_codes(
                types.SimpleNamespace(lexicon=restored_records),
                "FULL_DEPOSITED_AFFIX",
            ),
            True,
        )
        restored_primary_surfaces = _surface_set_vectors(
            core,
            surfaces,
            restored_primary_codes,
            n_core=n_core,
            candidate_rank=candidate_rank,
            threads=threads,
            capacity_reference=primary_surfaces,
        )
        restored_by_view["FULL_DEPOSITED_AFFIX"] = (
            restored_primary_surfaces
        )
        for view_name in VIEW_ORDER:
            full_view_codes = _synthetic_view_direct_codes(world, view_name)
            without_view_codes = _synthetic_view_direct_codes(
                types.SimpleNamespace(lexicon=reachable_only), view_name
            )
            restored_view_codes = _synthetic_view_direct_codes(
                types.SimpleNamespace(lexicon=restored_records), view_name
            )
            if not (
                full_view_codes == without_view_codes == restored_view_codes
            ):
                unreachable_invariance = False
        full_evidence = expanded_evidence
        without_evidence = _component_evidence_array(surfaces, without_by_view)
        restored_evidence = _component_evidence_array(surfaces, restored_by_view)
        derived_unreachable_equal = True
        for view_name in VIEW_ORDER:
            full_distribution = (
                _try_joint(expanded_by_view[view_name])
                if expanded_by_view[view_name] else None
            )
            without_distribution = (
                _try_joint(without_by_view[view_name])
                if without_by_view[view_name] else None
            )
            restored_distribution = (
                _try_joint(restored_by_view[view_name])
                if restored_by_view[view_name] else None
            )
            derived_unreachable_equal = bool(
                derived_unreachable_equal
                and _vectors_equal(full_distribution, without_distribution)
                and _vectors_equal(full_distribution, restored_distribution)
                and _distribution_digest(full_distribution)
                == _distribution_digest(without_distribution)
                == _distribution_digest(restored_distribution)
            )
            del full_distribution, without_distribution, restored_distribution
        unreachable_invariance = bool(
            unreachable_invariance
            and full_evidence == without_evidence == restored_evidence
            and derived_unreachable_equal
        )
        if not unreachable_invariance:
            raise DANI001CalibrationError(
                "synthetic whole-view unreachable evidence invariant failed"
            )
        unreachable_evidence_sha256 = _sha256(_canonical_json({
            "schema": "dani001-unreachable-evidence-v1",
            "world_id": str(world.world_id),
            "full": full_evidence,
            "without": without_evidence,
            "restored": restored_evidence,
        }))
    primary_gates = _gates_or_none(
        primary, candidate_rank, tail_threshold=0.001, t_threshold=3.0
    )
    top20_gates = _gates_or_none(
        top20, candidate_rank, tail_threshold=0.01, t_threshold=2.0
    )
    strict_gates = _gates_or_none(
        strict, candidate_rank, tail_threshold=0.01, t_threshold=2.0
    )
    direct_gates = _gates_or_none(
        direct, candidate_rank, tail_threshold=0.01, t_threshold=2.0
    )

    primary_capacity = _capacity_pass(primary, min_types=100, min_folios=20)
    top_capacity = _capacity_pass(top20, min_types=80, min_folios=20)
    strict_capacity = _capacity_pass(strict, min_types=100, min_folios=20)
    direct_capacity = _capacity_pass(direct, min_types=100, min_folios=20)
    core_first_five = bool(
        primary_gates
        and primary_gates["rank_gate"]
        and primary_gates["absolute_gate"]
        and primary_gates["folio_positive_gate"]
        and primary_gates["folio_concentration_gate"]
    )
    primary_all_gates = bool(
        primary_capacity
        and core_first_five
        and top_capacity
        and top20_gates
        and top20_gates["rank_gate"]
        and strict_capacity
        and strict_gates
        and strict_gates["rank_gate"]
        and affix_equivalence
        and unreachable_invariance
    )
    mechanics = all(
        _robustness_pass(
            robustness[name], candidate_rank, min_types=100, min_folios=20
        )
        for name in ("STRICT_NO_FUNCTION",)
    ) and _robustness_pass(
        robustness["SOURCE_PRESENT"],
        candidate_rank,
        min_types=30,
        min_folios=10,
    )
    leaves = all(
        _robustness_pass(
            robustness[f"LEAVE_{domain.upper()}_OUT"],
            candidate_rank,
            min_types=100,
            min_folios=20,
            require_positive_effects=True,
        )
        for domain in SYNTHETIC_DOMAINS
    )
    all_required = bool(
        primary_all_gates
        and direct_capacity
        and direct_gates
        and direct_gates["rank_gate"]
        and mechanics
        and leaves
    )

    world_id = str(world.world_id)
    family = str(world.family)
    if family == "TOY_PLANT":
        signature = primary is not None
    elif family == "TOY_NULL":
        signature = primary is not None
    elif family == "PLANT":
        unique_maximum = bool(
            primary is not None
            and int(np.count_nonzero(
                primary.joint_t == primary.joint_t[candidate_rank]
            )) == 1
            and int(np.argmax(primary.joint_t)) == candidate_rank
        )
        signature = unique_maximum and all_required
    elif family == "NULL":
        # A null assertion is probe independence; its false-pass contribution
        # is separately aggregated from all_required.
        signature = _null_probe_independence(world)
    elif world_id == "FIXED_HEAVY_HIGH_COVERAGE":
        coverage = bool(
            primary is not None
            and all(
                float(value.token[candidate_rank]) / value.token_denominator >= 0.90
                for value in primary.surfaces
            )
        )
        signature = bool(
            coverage
            and primary is not None
            and all(sd > 0.0 and math.isfinite(sd) for sd in primary.sds)
            and primary_gates
            and not primary_gates["rank_gate"]
        )
    elif world_id == "ONE_TYPE_CONCENTRATION":
        top_candidate_zero = bool(
            primary is not None
            and top20 is not None
            and all(
                int(surface.token[candidate_rank]) == 0
                and int(surface.type[candidate_rank]) == 0
                and float(surface.folio[candidate_rank]) == 0.0
                for surface in top20.surfaces
            )
            and all(
                original.type_denominator - deleted.type_denominator == 20
                for original, deleted in zip(
                    primary.surfaces,
                    top20.surfaces,
                    strict=True,
                )
            )
        )
        signature = bool(
            primary_capacity
            and core_first_five
            and top20_gates
            and not top20_gates["rank_gate"]
            and top_candidate_zero
        )
    elif world_id == "ONE_FOLIO_CONCENTRATION":
        one_positive_each = bool(
            primary is not None
            and all(
                sum(value > 0.0 for value in (surface.folio_advantages or ()))
                == 1
                for surface in primary.surfaces
            )
        )
        signature = bool(
            primary_capacity
            and primary_gates
            and primary_gates["rank_gate"]
            and primary_gates["absolute_gate"]
            and not primary_gates["folio_positive_gate"]
            and not primary_gates["folio_concentration_gate"]
            and one_positive_each
        )
    elif world_id == "PREFIX_ONLY":
        direct_zero = bool(
            direct_surfaces
            and all(
                not np.any(surface.token)
                and not np.any(surface.type)
                and not np.any(surface.folio)
                for surface in direct_surfaces
            )
        )
        signature = bool(
            primary_all_gates
            and direct_zero
            and not direct_capacity
            and direct is None
        )
    elif world_id == "UNKNOWN_SKIP":
        clean_rows = tuple(
            replace(
                row,
                groups=tuple(
                    group[:-1] if group.endswith("b") else group
                    for group in row.groups
                ),
            )
            for row in world.rows
        )
        clean_surfaces = _synthetic_surfaces(
            generator, types.SimpleNamespace(rows=clean_rows)
        )
        clean_primary = _score_surface_set(
            core,
            clean_surfaces,
            core_affix,
            n_core=n_core,
            candidate_rank=candidate_rank,
            threads=threads,
        )
        signature = bool(
            primary_all_gates
            and _vectors_equal(primary, clean_primary)
            and _distribution_digest(primary) == _distribution_digest(clean_primary)
            and strict is None
            and not strict_capacity
        )
    elif world_id == "ONE_READING_WRONG":
        rf_effects = (
            tuple(primary_gates["absolute_effects"])[-6:]
            if primary_gates is not None else ()
        )
        signature = bool(
            primary_capacity
            and primary_gates
            and len(rf_effects) == 6
            and all(value == 0.0 for value in rf_effects)
            and not primary_gates["absolute_gate"]
            and not primary_gates["rank_gate"]
        )
    else:
        raise DANI001CalibrationError("unknown synthetic world family")

    if require_scalar:
        signature = signature and _toy_scalar_equivalence(core, generator, world)

    return WorldEvaluation(
        world_id=world_id,
        family=family,
        candidate_rank=candidate_rank,
        primary=primary,
        top20=top20,
        strict=strict,
        direct=direct,
        direct_surfaces=direct_surfaces,
        robustness=robustness,
        primary_gates=primary_gates,
        top20_gates=top20_gates,
        strict_gates=strict_gates,
        direct_gates=direct_gates,
        world_signature=signature,
        all_required_gates=all_required,
        affix_equivalence=affix_equivalence,
        unreachable_invariance=unreachable_invariance,
        affix_evidence_sha256=affix_evidence_sha256,
        unreachable_evidence_sha256=unreachable_evidence_sha256,
    )


def _parser_assertions(generator: object, manifest: Mapping[str, object]) -> dict[str, bool]:
    rows, record = generator.build_parser_fixture()
    if record != manifest["parser_fixture"]:
        raise DANI001CalibrationError("parser fixture manifest mismatch")
    manual = generator.panel_projection(rows, "MANUAL_GROUP")
    dot = generator.panel_projection(rows, "DOT_ONLY_EMULATION")
    per_edition_manual = {
        edition: [value for value in manual if value["edition"] == edition]
        for edition in EDITION_ORDER
    }
    per_edition_dot = {
        edition: [value for value in dot if value["edition"] == edition]
        for edition in EDITION_ORDER
    }
    primary = all(
        [value["normalized_eva"] for value in per_edition_manual[edition]]
        == ["kdr", "lny", "qy", "mg", "kd"]
        for edition in EDITION_ORDER
    )
    separators = all(
        tuple(row.separators) == (",", "<->", "<~>", ".") for row in rows
    )
    independence = all(
        [value["normalized_eva"] for value in per_edition_dot[edition]]
        == ["kdrlnyqymg", "kd"]
        and len(per_edition_manual[edition]) == 5
        for edition in EDITION_ORDER
    )
    strict = all(
        sum(bool(value["strict_literal_eligible"])
            for value in per_edition_manual[edition]) == 2
        and sum(bool(value["strict_literal_eligible"])
                for value in per_edition_dot[edition]) == 1
        for edition in EDITION_ORDER
    )
    return {
        "PARSER_PRIMARY_SELECTION": primary,
        "PARSER_SEPARATOR_STATES": separators,
        "PARSER_PANEL_INDEPENDENCE": independence,
        "PARSER_STRICT_PROPAGATION": strict,
    }


def _expect_rejection(function: object) -> bool:
    try:
        function()  # type: ignore[operator]
    except (DANI001CalibrationError, RuntimeError, ValueError, TypeError):
        return True
    return False


def _duplicate_lexicon_fixture(world: object) -> bytes:
    records = list(world.lexicon)
    if not records:
        raise DANI001CalibrationError("empty duplicate-key fixture base")
    first = records[0]
    entries = json.dumps(
        first["entries"], sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    )
    key = json.dumps(
        first["key"], sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    )
    first_raw = f'{{"entries":{entries},"key":{key},"key":{key}}}'
    rest = [
        json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        )
        for value in records[1:]
    ]
    return ("[" + ",".join((first_raw, *rest)) + "]\n").encode("utf-8")


def _mutation_assertions(
    core: object,
    generator: object,
    manifest: Mapping[str, object],
    plant_zero: object,
    baseline_evaluation: WorldEvaluation,
) -> dict[str, bool]:
    mutation_rows = manifest["mutations"]
    if not isinstance(mutation_rows, list) or len(mutation_rows) != 20:
        raise DANI001CalibrationError("mutation manifest inventory drift")
    by_id = {str(value["mutation_id"]): value for value in mutation_rows}
    base_rows = generator.canonicalize_rows(plant_zero.rows)
    parser_rows, _parser_record = generator.build_parser_fixture()
    output: dict[str, bool] = {}

    output["MUTATION_EMPTY_PANEL"] = _expect_rejection(
        lambda: generator.canonicalize_rows(())
    )
    output["MUTATION_DUPLICATE_ROW"] = _expect_rejection(
        lambda: generator.canonicalize_rows((*base_rows, base_rows[0]))
    )
    duplicate = _duplicate_lexicon_fixture(plant_zero)
    output["MUTATION_DUPLICATE_JSON_KEY"] = (
        _sha256(duplicate) == by_id["DUPLICATE_JSON_KEY"]["mutated_input_sha256"]
        and _expect_rejection(lambda: _json_no_duplicates(duplicate))
    )

    # These three mutations alter only serialized order.  The scorer's frozen
    # sufficient statistics are canonical type/template/folio counts and the
    # sorted code set, so compare those complete score inputs byte for byte.
    baseline_surfaces = _synthetic_surfaces(generator, plant_zero)
    reversed_tokens = tuple(
        replace(row, groups=row.groups[::-1], separators=row.separators[::-1])
        for row in base_rows
    )
    reversed_rows = tuple(reversed(base_rows))
    token_surfaces = tuple(
        _surface_from_projection(
            edition, panel_name,
            generator.panel_projection(reversed_tokens, panel_name),
        )
        for edition in EDITION_ORDER for panel_name in PANEL_ORDER
    )
    row_surfaces = tuple(
        _surface_from_projection(
            edition, panel_name,
            generator.panel_projection(reversed_rows, panel_name),
        )
        for edition in EDITION_ORDER for panel_name in PANEL_ORDER
    )

    def sufficient(surfaces: Sequence[PrivateSurface]) -> bytes:
        return _canonical_json([
            [
                [
                    value.normalized,
                    list(value.template),
                    value.token_count,
                    [list(item) for item in value.folio_counts],
                ]
                for value in _type_bins(surface, strict_only=False, delete_top20=False)
            ]
            for surface in surfaces
        ])

    base_sufficient = sufficient(baseline_surfaces)
    output["MUTATION_TOKEN_REVERSE"] = (
        generator.canonical_json_bytes([row.to_object() for row in reversed_tokens])
        != generator.canonical_json_bytes([row.to_object() for row in base_rows])
        and sufficient(token_surfaces) == base_sufficient
        and any(
            left.template_sha256 != right.template_sha256
            for left, right in zip(baseline_surfaces, token_surfaces, strict=True)
        )
    )
    output["MUTATION_ROW_REVERSE"] = (
        generator.canonical_json_bytes([row.to_object() for row in reversed_rows])
        != generator.canonical_json_bytes([row.to_object() for row in base_rows])
        and sufficient(row_surfaces) == base_sufficient
    )
    reversed_lexicon = tuple(
        {"key": value["key"], "entries": list(reversed(value["entries"]))}
        for value in reversed(plant_zero.lexicon)
    )
    reversed_world = replace(plant_zero, lexicon=reversed_lexicon)

    def baseline_view(view_name: str) -> JointDistribution | None:
        if view_name == "FULL_DEPOSITED_AFFIX":
            return baseline_evaluation.primary
        if view_name == "DIRECT_ONLY":
            return baseline_evaluation.direct
        if view_name == "STRICT_LITERAL":
            return baseline_evaluation.strict
        if view_name == "TOP20_DELETED":
            return baseline_evaluation.top20
        return baseline_evaluation.robustness.get(view_name)

    lexicon_reverse_equal = True
    for view_name in VIEW_ORDER:
        baseline_records = _synthetic_view_records(plant_zero, view_name)
        reversed_records = _synthetic_view_records(reversed_world, view_name)
        baseline_keys = {
            str(value["key"]) for value in baseline_records
        }
        reversed_keys = {
            str(value["key"]) for value in reversed_records
        }
        baseline_direct = _synthetic_view_direct_codes(
            plant_zero, view_name
        )
        reversed_direct = _synthetic_view_direct_codes(
            reversed_world, view_name
        )
        deposited = view_name != "DIRECT_ONLY"
        baseline_codes = _core_view_codes(
            core, baseline_direct, deposited
        )
        reversed_codes = _core_view_codes(
            core, reversed_direct, deposited
        )
        reversed_distribution = _score_surface_set(
            core,
            baseline_surfaces,
            reversed_codes,
            n_core=int(plant_zero.variable_count),
            candidate_rank=int(plant_zero.candidate_rank),
            strict_only=view_name == "STRICT_LITERAL",
            delete_top20=view_name == "TOP20_DELETED",
        )
        original_distribution = baseline_view(view_name)
        lexicon_reverse_equal = bool(
            lexicon_reverse_equal
            and baseline_keys == reversed_keys
            and len(baseline_records) == len(reversed_records)
            and baseline_direct == reversed_direct
            and baseline_codes == reversed_codes
            and original_distribution is not None
            and reversed_distribution is not None
            and _vectors_equal(
                original_distribution, reversed_distribution
            )
            and _distribution_digest(original_distribution)
            == _distribution_digest(reversed_distribution)
        )
        del reversed_distribution
    output["MUTATION_LEXICON_REVERSE"] = lexicon_reverse_equal

    malformed = (
        ("UNMATCHED_SQUARE", "[k"),
        ("NESTED_SQUARE", "[[k]]"),
        ("UNMATCHED_BRACE", "{k"),
        ("NESTED_BRACE", "{{k}}"),
        ("UNMATCHED_ANGLE", "<k"),
        ("NESTED_ANGLE", "<<k>>"),
    )
    for name, raw in malformed:
        output[f"MUTATION_{name}"] = _expect_rejection(
            lambda value=raw: generator.compile_source_token(value, 1)
        )

    output["MUTATION_OVERLENGTH_PREIMAGE"] = _expect_rejection(
        lambda: _accepted_preimages_literal((_encode_codes((1,) * 11),))
    )
    overlength = generator.compile_source_token("kdrslnqymgk", 1)
    mutated_first = replace(
        base_rows[0],
        groups=(*base_rows[0].groups, "kdrslnqymgk"),
        separators=(*base_rows[0].separators, "."),
    )
    overlength_rows = (mutated_first, *base_rows[1:])
    overlength_surfaces = tuple(
        _surface_from_projection(
            edition,
            panel_name,
            generator.panel_projection(overlength_rows, panel_name),
        )
        for edition in EDITION_ORDER
        for panel_name in PANEL_ORDER
    )
    direct_codes = _synthetic_direct_codes(plant_zero)
    accepted_codes = _accepted_preimages_literal(direct_codes)
    denominator_retained = True
    zero_all_ranks = True
    for baseline, mutated in zip(
        baseline_surfaces, overlength_surfaces, strict=True
    ):
        base_bins = _type_bins(
            baseline, strict_only=False, delete_top20=False
        )
        changed_bins = _type_bins(
            mutated, strict_only=False, delete_top20=False
        )
        expected_delta = 1 if baseline.edition == "ZL3b" else 0
        denominator_retained = denominator_retained and (
            sum(value.token_count for value in changed_bins)
            - sum(value.token_count for value in base_bins)
            == expected_delta
            and len(changed_bins) - len(base_bins) == expected_delta
        )
        candidates = tuple(
            value for value in changed_bins
            if value.normalized == "kdrslnqymgk"
        )
        if expected_delta:
            zero_all_ranks = zero_all_ranks and len(candidates) == 1 and not (
                _constraints_for_template(
                    candidates[0].template, accepted_codes, 10
                )
            )
    output["MUTATION_OVERLENGTH_TOKEN"] = bool(
        overlength is not None
        and len(overlength[0].emitted_template) == 11
        and denominator_retained
        and zero_all_ranks
    )
    unknown = [
        generator.compile_source_token(group + "b", 1)
        for group in base_rows[0].groups
    ]
    clean = [
        generator.compile_source_token(group, 1) for group in base_rows[0].groups
    ]
    output["MUTATION_UNKNOWN_INSERT"] = all(
        left is not None and right is not None
        and left[0].emitted_template == right[0].emitted_template
        and left[1] is True and right[1] is False
        for left, right in zip(clean, unknown, strict=True)
    ) and 256 * 32 * 3 == 24_576
    output["MUTATION_MISSING_EDITION"] = (
        _expect_rejection(lambda: _synthetic_surfaces(
            generator,
            types.SimpleNamespace(
                rows=tuple(row for row in base_rows if row.edition != "RF1b")
            ),
        ))
    )
    output["MUTATION_PAGE_DOMAIN"] = _expect_rejection(
        lambda: generator.SyntheticRow(
            "ZL3b", "fRos", "P.1", ("kd",), (),
        )
    )
    output["MUTATION_FOLIO_DRIFT"] = _expect_rejection(
        lambda: generator.SyntheticRow(
            "ZL3b", "f2r", "P.1", ("kd",), (),
        )
    )
    reachable = tuple(
        value for value in plant_zero.lexicon
        if value["key"] and all(item in NIBBLE_CODE for item in value["key"])
    )
    removed = tuple(
        value for value in plant_zero.lexicon
        if not (value["key"] and all(item in NIBBLE_CODE for item in value["key"]))
    )
    full_bytes = generator.canonical_json_bytes(list(plant_zero.lexicon))
    without_bytes = generator.canonical_json_bytes(list(reachable))
    removed_bytes = generator.canonical_json_bytes(list(removed))
    remove_hashes = by_id["UNREACHABLE_REMOVE"]["payload_sha256s"]
    output["MUTATION_UNREACHABLE_REMOVE"] = bool(
        len(removed) == 570
        and remove_hashes == {
            "full": _sha256(full_bytes),
            "removed_records": _sha256(removed_bytes),
            "without": _sha256(without_bytes),
        }
        and _synthetic_direct_codes(plant_zero) == tuple(sorted({
            _encode_codes(tuple(NIBBLE_CODE[item] for item in value["key"]))
            for value in reachable
        }))
    )
    restored = tuple(sorted(
        (*reachable, *removed), key=lambda value: value["key"].encode("utf-8")
    ))
    restore_hashes = by_id["UNREACHABLE_RESTORE_ADD_FROM_REMOVED"]["payload_sha256s"]
    output["MUTATION_UNREACHABLE_RESTORE_ADD_FROM_REMOVED"] = bool(
        generator.canonical_json_bytes(list(restored)) == full_bytes
        and restore_hashes == {
            "removed_records": _sha256(removed_bytes),
            "restored": _sha256(full_bytes),
            "without": _sha256(without_bytes),
        }
    )
    expected = {
        str(value["assertion_id"]) for value in mutation_rows
    }
    if set(output) != expected:
        raise DANI001CalibrationError("mutation assertion IDs drift")
    return output


def _rank_lex_fast(permutation: Sequence[int]) -> int:
    remaining = list(range(len(permutation)))
    rank = 0
    for index, value in enumerate(permutation):
        ordinal = remaining.index(value)
        rank += ordinal * math.factorial(len(permutation) - index - 1)
        remaining.pop(ordinal)
    return rank


def _conjugacy_index(rho: Sequence[int]) -> np.ndarray:
    permutation = tuple(int(value) for value in rho)
    inverse = [0] * len(permutation)
    for index, value in enumerate(permutation):
        inverse[value] = index
    output = np.empty(math.factorial(len(permutation)), dtype="<u4")
    for rank, mapping in enumerate(itertools.permutations(range(len(permutation)))):
        transformed = tuple(
            permutation[mapping[inverse[index]]] for index in range(len(permutation))
        )
        output[rank] = _rank_lex_fast(transformed)
    if len(np.unique(output)) != len(output):
        raise DANI001CalibrationError("conjugacy rank map is not bijective")
    return output


def _conjugacy_control(
    core: object,
    generator: object,
    plant_zero: object,
    base: WorldEvaluation,
) -> bool:
    if base.primary is None:
        return False
    rho, _audit = generator.first_nonidentity_permutation(
        "conjugacy-permutation", 10
    )
    index = _conjugacy_index(rho)
    candidate = int(index[plant_zero.candidate_rank])
    surfaces = _synthetic_surfaces(generator, plant_zero)
    codes = _core_view_codes(core, _synthetic_direct_codes(plant_zero), True)
    renamed = _score_surface_set(
        core, surfaces, codes, n_core=10, candidate_rank=candidate,
        rename_by=rho, threads=WORKERS,
    )
    if renamed is None:
        return False
    for original_surface, renamed_surface in zip(
        base.primary.surfaces, renamed.surfaces, strict=True
    ):
        for weighting in WEIGHT_ORDER:
            if not np.array_equal(
                original_surface.vector(weighting),
                renamed_surface.vector(weighting)[index],
            ):
                return False
    for original, changed in zip(
        base.primary.standardized, renamed.standardized, strict=True
    ):
        if not np.array_equal(original, changed[index]):
            return False
    return np.array_equal(base.primary.joint_t, renamed.joint_t[index])


def _worker_control(
    core: object,
    generator: object,
    plant_zero: object,
    base: WorldEvaluation,
) -> bool:
    if base.primary is None:
        return False
    surfaces = _synthetic_surfaces(generator, plant_zero)
    codes = _core_view_codes(core, _synthetic_direct_codes(plant_zero), True)
    single = _score_surface_set(
        core, surfaces, codes, n_core=10,
        candidate_rank=int(plant_zero.candidate_rank), threads=1,
    )
    return _vectors_equal(base.primary, single)


def _actual_view_definition(
    lexicon: object,
    view_name: str,
) -> tuple[object, tuple[int, ...], bool, bool]:
    """Return lexicon view, codes, strict flag, top-delete flag."""

    if view_name == "FULL_DEPOSITED_AFFIX":
        selected = lexicon.view("FULL")
        return selected, tuple(selected.deposited_affix_codes), False, False
    if view_name == "DIRECT_ONLY":
        selected = lexicon.view("FULL")
        return selected, tuple(selected.direct_codes), False, False
    if view_name == "STRICT_NO_FUNCTION":
        selected = lexicon.view("STRICT_NO_FUNCTION")
        return selected, tuple(selected.deposited_affix_codes), False, False
    if view_name == "STRICT_LITERAL":
        selected = lexicon.view("FULL")
        return selected, tuple(selected.deposited_affix_codes), True, False
    if view_name == "TOP20_DELETED":
        selected = lexicon.view("FULL")
        return selected, tuple(selected.deposited_affix_codes), False, True
    if view_name == "SOURCE_PRESENT":
        selected = lexicon.view("SOURCE_PRESENT")
        return selected, tuple(selected.deposited_affix_codes), False, False
    if view_name.startswith("LEAVE_") and view_name.endswith("_OUT"):
        domain = view_name.removeprefix("LEAVE_").removesuffix("_OUT")
        selected = lexicon.view(f"LEAVE_OUT_{domain}")
        return selected, tuple(selected.deposited_affix_codes), False, False
    raise DANI001CalibrationError("unknown actual capacity view")


def _actual_panel_counts(source: object) -> list[dict[str, object]]:
    observed = {
        (edition, panel): (tokens, strict, types, folios)
        for edition, panel, tokens, strict, types, folios
        in source.counts.panel_counts
    }
    output = []
    for edition in EDITION_ORDER:
        for panel in PANEL_ORDER:
            tokens, strict, types, folios = observed[(edition, panel)]
            output.append({
                "edition": edition,
                "panel": panel,
                "token_count": int(tokens),
                "normalized_type_count": int(types),
                "folio_count": int(folios),
                "strict_literal_token_count": int(strict),
            })
    return output


def _actual_lexicon_counts(lexicon: object) -> dict[str, object]:
    counts = lexicon.counts
    views = [
        {
            "view": str(name),
            "total_key_count": int(total),
            "reachable_key_count": int(reachable),
            "direct_code_count": int(direct),
            "deposited_affix_code_count": int(affix),
        }
        for name, total, reachable, direct, affix in counts.view_counts
    ]
    expected_order = (
        "FULL", "REACHABLE", "SOURCE_PRESENT", "STRICT_NO_FUNCTION",
        "LEAVE_OUT_ASTRO", "LEAVE_OUT_BOTANICAL", "LEAVE_OUT_FUNCTION",
        "LEAVE_OUT_GENERAL", "LEAVE_OUT_MEDICAL", "LEAVE_OUT_PHARMA",
    )
    if tuple(value["view"] for value in views) != expected_order:
        raise DANI001CalibrationError("actual lexicon view order drift")
    return {
        "keys": int(counts.keys),
        "entries": int(counts.entries),
        "reachable_keys": int(counts.reachable_keys),
        "unreachable_keys": int(counts.unreachable_keys),
        "source_present_keys": int(counts.source_present_keys),
        "source_present_reachable_keys": int(counts.source_present_reachable_keys),
        "strict_no_function_keys": int(counts.strict_no_function_keys),
        "strict_no_function_reachable_keys": int(
            counts.strict_no_function_reachable_keys
        ),
        "views": views,
    }


def _capacity_surface_public(
    surface: PrivateSurface,
    vectors: SurfaceVectors,
    *,
    affix_equivalence: bool | None,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    token_mean, token_sd = _mean_sd(vectors.token)
    type_mean, type_sd = _mean_sd(vectors.type)
    folio_mean, folio_sd = _mean_sd(vectors.folio)
    del token_mean, type_mean, folio_mean
    digests = {
        "TOKEN": _u4_digest(vectors.token),
        "TYPE": _u4_digest(vectors.type),
        "FOLIO": _f8_digest(vectors.folio),
    }
    public = {
        "edition": surface.edition,
        "panel": surface.panel,
        "variable_type_count": int(vectors.variable_type_count),
        "capacity_folio_count": int(vectors.capacity_folio_count),
        "token_sd_positive": bool(token_sd > 0.0 and math.isfinite(token_sd)),
        "type_sd_positive": bool(type_sd > 0.0 and math.isfinite(type_sd)),
        "folio_sd_positive": bool(folio_sd > 0.0 and math.isfinite(folio_sd)),
        "token_nonidentity_vector_sha256": digests["TOKEN"],
        "type_nonidentity_vector_sha256": digests["TYPE"],
        "folio_nonidentity_vector_sha256": digests["FOLIO"],
        "affix_equivalence": affix_equivalence,
    }
    entries = [
        {
            "edition": surface.edition,
            "panel": surface.panel,
            "weighting": weighting,
            "dtype": "<f8" if weighting == "FOLIO" else "<u4",
            "rank_start": ACTUAL_BEGIN,
            "rank_stop": ACTUAL_END,
            "sha256": digests[weighting],
        }
        for weighting in WEIGHT_ORDER
    ]
    return public, entries


def _surface_capacity_ok(
    value: Mapping[str, object], *, min_types: int, min_folios: int
) -> bool:
    return bool(
        int(value["variable_type_count"]) >= min_types
        and int(value["capacity_folio_count"]) >= min_folios
        and value["token_sd_positive"] is True
        and value["type_sd_positive"] is True
        and value["folio_sd_positive"] is True
    )


def _actual_implementation_invariant_digest(
    affix: Sequence[Mapping[str, object]],
    unreachable: Sequence[Mapping[str, object]],
) -> str:
    expected_order = tuple(
        (edition, panel, weighting)
        for edition in EDITION_ORDER
        for panel in PANEL_ORDER
        for weighting in WEIGHT_ORDER
    )
    if (
        tuple(
            (str(value.get("edition")), str(value.get("panel")),
             str(value.get("weighting")))
            for value in affix
        ) != expected_order
        or tuple(
            (str(value.get("edition")), str(value.get("panel")),
             str(value.get("weighting")))
            for value in unreachable
        ) != expected_order
    ):
        raise DANI001CalibrationError(
            "actual implementation-invariant entry order drift"
        )
    affix_keys = {
        "edition", "panel", "weighting", "dtype",
        "literal_decision_function_sha256", "literal_raw_sha256",
        "expanded_decision_function_sha256", "expanded_raw_sha256",
    }
    unreachable_keys = {
        "edition", "panel", "weighting", "dtype", "full_raw_sha256",
        "without_raw_sha256", "restored_raw_sha256",
    }
    for entry in affix:
        if set(entry) != affix_keys:
            raise DANI001CalibrationError("actual affix evidence schema drift")
        weighting = str(entry["weighting"])
        expected_dtype = "<f8" if weighting == "FOLIO" else "<u4"
        if (
            entry["dtype"] != expected_dtype
            or not all(
                HEX64.fullmatch(str(entry[name]))
                for name in (
                    "literal_decision_function_sha256",
                    "literal_raw_sha256",
                    "expanded_decision_function_sha256",
                    "expanded_raw_sha256",
                )
            )
            or entry["literal_decision_function_sha256"]
            != entry["expanded_decision_function_sha256"]
            or entry["literal_raw_sha256"] != entry["expanded_raw_sha256"]
        ):
            raise DANI001CalibrationError("actual affix evidence mismatch")
    for entry in unreachable:
        if set(entry) != unreachable_keys:
            raise DANI001CalibrationError(
                "actual unreachable evidence schema drift"
            )
        weighting = str(entry["weighting"])
        expected_dtype = "<f8" if weighting == "FOLIO" else "<u4"
        if (
            entry["dtype"] != expected_dtype
            or not all(
                HEX64.fullmatch(str(entry[name]))
                for name in (
                    "full_raw_sha256", "without_raw_sha256",
                    "restored_raw_sha256",
                )
            )
            or not (
                entry["full_raw_sha256"] == entry["without_raw_sha256"]
                == entry["restored_raw_sha256"]
            )
        ):
            raise DANI001CalibrationError(
                "actual unreachable evidence mismatch"
            )
    return _sha256(_canonical_json({
        "schema": "dani001-actual-implementation-invariants-v1",
        "rank_start": ACTUAL_BEGIN,
        "rank_stop": ACTUAL_END,
        "affix": list(affix),
        "unreachable": list(unreachable),
        "affix_pass": True,
        "unreachable_pass": True,
    }))


def _actual_capacity(
    core: ActualCoreGuard,
    source: object,
    lexicon: object,
) -> dict[str, object]:
    surfaces = tuple(
        _surface_from_panel(source.panel(edition, panel))
        for edition in EDITION_ORDER for panel in PANEL_ORDER
    )
    full = lexicon.view("FULL")
    reachable = lexicon.view("REACHABLE")
    restored = lexicon.restored()
    if (
        tuple(full.direct_codes) != tuple(reachable.direct_codes)
        or tuple(full.deposited_affix_codes)
        != tuple(reachable.deposited_affix_codes)
        or tuple(full.direct_codes) != tuple(restored.direct_codes)
        or tuple(full.deposited_affix_codes)
        != tuple(restored.deposited_affix_codes)
    ):
        raise DANI001CalibrationError("actual unreachable-key invariant failed")
    literal_affix = _accepted_preimages_literal(tuple(full.direct_codes))
    core_affix = _core_view_codes(core, tuple(full.direct_codes), True)
    if (
        literal_affix != tuple(full.deposited_affix_codes)
        or core_affix != literal_affix
    ):
        raise DANI001CalibrationError("actual affix implementation invariant failed")

    public_views = []
    digest_entries = []
    affix_invariant_entries: list[dict[str, object]] = []
    unreachable_invariant_entries: list[dict[str, object]] = []
    by_view: dict[str, list[dict[str, object]]] = {}
    for view_name in VIEW_ORDER:
        _lex_view, accepted, strict_only, top20 = _actual_view_definition(
            lexicon, view_name
        )
        public_surfaces = []
        for surface in surfaces:
            core.mark_primary_logical_surface()
            vectors = _surface_vectors(
                core,
                surface,
                accepted,
                n_core=10,
                rank_begin=ACTUAL_BEGIN,
                rank_end=ACTUAL_END,
                threads=WORKERS,
                strict_only=strict_only,
                delete_top20=top20,
                candidate_rank=None,
            )
            affix_equivalence: bool | None = None
            if view_name == "FULL_DEPOSITED_AFFIX":
                bins = _type_bins(
                    surface, strict_only=False, delete_top20=False
                )
                (
                    binary_equal,
                    literal_decision_sha,
                    expanded_decision_sha,
                ) = _actual_affix_decision_function_equivalence(
                    core,
                    bins,
                    tuple(full.direct_codes),
                    tuple(full.deposited_affix_codes),
                )
                core.mark_evidence_logical_surface()
                literal_vectors = _surface_vectors(
                    core,
                    surface,
                    tuple(full.deposited_affix_codes),
                    n_core=10,
                    rank_begin=ACTUAL_BEGIN,
                    rank_end=ACTUAL_END,
                    threads=WORKERS,
                    candidate_rank=None,
                    literal_direct_codes=tuple(full.direct_codes),
                    capacity_override=(
                        vectors.variable_type_count,
                        vectors.capacity_folio_count,
                    ),
                )
                core.mark_evidence_logical_surface()
                reachable_vectors = _surface_vectors(
                    core,
                    surface,
                    tuple(reachable.deposited_affix_codes),
                    n_core=10,
                    rank_begin=ACTUAL_BEGIN,
                    rank_end=ACTUAL_END,
                    threads=WORKERS,
                    candidate_rank=None,
                    capacity_override=(
                        vectors.variable_type_count,
                        vectors.capacity_folio_count,
                    ),
                )
                core.mark_evidence_logical_surface()
                restored_vectors = _surface_vectors(
                    core,
                    surface,
                    tuple(restored.deposited_affix_codes),
                    n_core=10,
                    rank_begin=ACTUAL_BEGIN,
                    rank_end=ACTUAL_END,
                    threads=WORKERS,
                    candidate_rank=None,
                    capacity_override=(
                        vectors.variable_type_count,
                        vectors.capacity_folio_count,
                    ),
                )
                affix_equivalence = bool(
                    binary_equal
                    and _surface_vectors_equal(vectors, literal_vectors)
                    and _surface_vector_digest(vectors)
                    == _surface_vector_digest(literal_vectors)
                )
                unreachable_equal = bool(
                    _surface_vectors_equal(vectors, reachable_vectors)
                    and _surface_vector_digest(vectors)
                    == _surface_vector_digest(reachable_vectors)
                    and _surface_vectors_equal(vectors, restored_vectors)
                    and _surface_vector_digest(vectors)
                    == _surface_vector_digest(restored_vectors)
                )
                if not affix_equivalence or not unreachable_equal:
                    raise DANI001CalibrationError(
                        "OUTPUT_FREE_IMPLEMENTATION_INVARIANT_STOP"
                    )
                for weighting in WEIGHT_ORDER:
                    dtype = "<f8" if weighting == "FOLIO" else "<u4"
                    expanded_raw = vectors.vector(weighting)
                    literal_raw = literal_vectors.vector(weighting)
                    without_raw = reachable_vectors.vector(weighting)
                    restored_raw = restored_vectors.vector(weighting)
                    raw_digest = _f8_digest if weighting == "FOLIO" else _u4_digest
                    affix_invariant_entries.append({
                        "edition": surface.edition,
                        "panel": surface.panel,
                        "weighting": weighting,
                        "dtype": dtype,
                        "literal_decision_function_sha256": literal_decision_sha,
                        "literal_raw_sha256": raw_digest(literal_raw),
                        "expanded_decision_function_sha256": expanded_decision_sha,
                        "expanded_raw_sha256": raw_digest(expanded_raw),
                    })
                    unreachable_invariant_entries.append({
                        "edition": surface.edition,
                        "panel": surface.panel,
                        "weighting": weighting,
                        "dtype": dtype,
                        "full_raw_sha256": raw_digest(expanded_raw),
                        "without_raw_sha256": raw_digest(without_raw),
                        "restored_raw_sha256": raw_digest(restored_raw),
                    })
            public, entries = _capacity_surface_public(
                surface,
                vectors,
                affix_equivalence=affix_equivalence,
            )
            public_surfaces.append(public)
            for entry in entries:
                digest_entries.append({"view": view_name, **entry})
        by_view[view_name] = public_surfaces
        public_views.append({"view": view_name, "surfaces": public_surfaces})

    mandatory_thresholds = {
        "FULL_DEPOSITED_AFFIX": (100, 20),
        "DIRECT_ONLY": (100, 20),
        "STRICT_NO_FUNCTION": (100, 20),
        "STRICT_LITERAL": (100, 20),
        "TOP20_DELETED": (80, 20),
    }
    mandatory_by_view = {
        name: all(_surface_capacity_ok(value, min_types=threshold[0], min_folios=threshold[1])
                  for value in by_view[name])
        for name, threshold in mandatory_thresholds.items()
    }
    conditional_thresholds = (
        ("SOURCE_PRESENT", 30, 10),
        ("LEAVE_ASTRO_OUT", 100, 20),
        ("LEAVE_BOTANICAL_OUT", 100, 20),
        ("LEAVE_FUNCTION_OUT", 100, 20),
        ("LEAVE_GENERAL_OUT", 100, 20),
        ("LEAVE_MEDICAL_OUT", 100, 20),
        ("LEAVE_PHARMA_OUT", 100, 20),
    )
    conditional = [
        {
            "view": name,
            "status": "POWERED" if all(
                _surface_capacity_ok(value, min_types=min_types, min_folios=min_folios)
                for value in by_view[name]
            ) else "INSUFFICIENT",
        }
        for name, min_types, min_folios in conditional_thresholds
    ]
    if len(digest_entries) != 216:
        raise DANI001CalibrationError("actual component digest inventory drift")
    if (
        len(affix_invariant_entries) != 18
        or len(unreachable_invariant_entries) != 18
    ):
        raise DANI001CalibrationError(
            "actual implementation-invariant evidence inventory drift"
        )
    core.assert_complete()
    digest = _sha256(_canonical_json({
        "schema": "dani001-actual-nonidentity-vector-digest-v1",
        "entries": digest_entries,
    }))
    implementation_invariant_digest = _actual_implementation_invariant_digest(
        affix_invariant_entries,
        unreachable_invariant_entries,
    )
    return {
        "panel_counts": _actual_panel_counts(source),
        "lexicon_counts": _actual_lexicon_counts(lexicon),
        "views": public_views,
        "mandatory_capacity_pass": all(mandatory_by_view.values()),
        "conditional_view_statuses": conditional,
        "actual_nonidentity_vector_digest_sha256": digest,
        "implementation_invariant_digest_sha256": (
            implementation_invariant_digest
        ),
        # This internal-only key is stripped before schema construction.
        "_mandatory_by_view": mandatory_by_view,
    }


def _path_binding(relative: str) -> dict[str, object]:
    path = ROOT / relative
    data = path.read_bytes()
    return {"path": relative, "sha256": _sha256(data), "size": len(data)}


def _assert_registered_local_bindings(values: object) -> None:
    if not isinstance(values, list) or len(values) != len(LOCAL_INPUT_RELS):
        raise DANI001CalibrationError("registered local input inventory drift")
    for value, relative in zip(values, LOCAL_INPUT_RELS, strict=True):
        if (
            not isinstance(value, dict)
            or set(value) != {"path", "sha256", "size"}
            or value["path"] != relative
            or value["sha256"] != LOCAL_INPUT_SHA256[relative]
            or type(value["size"]) is not int
            or value["size"] != LOCAL_INPUT_SIZE[relative]
        ):
            raise DANI001CalibrationError(
                f"registered local input binding drift: {relative}"
            )


def _compiler_version_bytes() -> bytes:
    completed = subprocess.run(
        [FROZEN_CXX, "--version"],
        check=True,
        capture_output=True,
        env=COMPILE_ENV,
    )
    if completed.stderr:
        raise DANI001CalibrationError("frozen compiler emitted version stderr")
    return completed.stdout


def _build_core_from_bytes(
    cpp_bytes: bytes,
    header_bytes: bytes,
    *,
    parent: Path,
) -> tuple[Path, str, bytes]:
    if _sha256_path(Path(FROZEN_CXX)) != FROZEN_CXX_SHA256:
        raise DANI001CalibrationError("frozen compiler binary drift")
    version = _compiler_version_bytes()
    directory = Path(tempfile.mkdtemp(prefix="dani001-core-build-", dir=parent))
    cpp = directory / "dani001_core.cpp"
    header = directory / "dani001_core.h"
    library = directory / "libdani001_core.so"
    try:
        for path, payload in ((cpp, cpp_bytes), (header, header_bytes)):
            with path.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        subprocess.run(
            list(COMPILE_ARGV),
            cwd=directory,
            env=COMPILE_ENV,
            check=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        with library.open("rb") as handle:
            os.fsync(handle.fileno())
        return directory, _sha256_path(library), version
    except BaseException:
        shutil.rmtree(directory, ignore_errors=True)
        raise


def _runtime_projection(*, core_library: Path | None = None) -> dict[str, object]:
    import importlib.metadata
    import platform

    python_version = platform.python_version()
    implementation = platform.python_implementation()
    machine = platform.machine()
    system = platform.system()
    if (
        python_version != "3.12.3"
        or implementation != "CPython"
        or machine != "x86_64"
        or system != "Linux"
    ):
        raise DANI001CalibrationError(
            "registered CPython/x86-64/Linux runtime unavailable"
        )
    if (
        sys.byteorder != "little"
        or struct.calcsize("d") != 8
        or sys.float_info.radix != 2
        or sys.float_info.mant_dig != 53
        or sys.float_info.max_exp != 1024
        or struct.pack("<d", 1.0) != b"\x00\x00\x00\x00\x00\x00\xf0?"
        or struct.pack("<d", 1.0) != struct.pack("=d", 1.0)
    ):
        raise DANI001CalibrationError("registered little-endian binary64 unavailable")
    try:
        process = ctypes.CDLL(None)
        fegetround = process.fegetround
        fegetround.argtypes = []
        fegetround.restype = ctypes.c_int
        rounding_mode = int(fegetround())
    except (AttributeError, OSError) as error:
        raise DANI001CalibrationError(
            "binary64 rounding-mode inspection unavailable"
        ) from error
    if rounding_mode != 0:
        raise DANI001CalibrationError(
            "registered binary64 round-to-nearest mode unavailable"
        )
    numpy_version = importlib.metadata.version("numpy")
    if numpy_version != "1.26.4":
        raise DANI001CalibrationError("registered NumPy 1.26.4 unavailable")
    if core_library is None:
        raise DANI001CalibrationError("core library absent from runtime binding")
    completed = subprocess.run(
        ["/usr/bin/ldd", str(core_library)],
        check=True,
        capture_output=True,
        text=True,
        env=COMPILE_ENV,
    )
    if completed.stderr:
        raise DANI001CalibrationError("ldd emitted runtime-binding stderr")
    candidates: list[tuple[str, Path]] = []
    for line in completed.stdout.splitlines():
        if "=>" not in line:
            continue
        soname, target = line.split("=>", 1)
        if not soname.strip().startswith("libgomp.so"):
            continue
        target_text = target.strip().split()[0]
        reported_candidate = Path(target_text)
        if not reported_candidate.is_absolute():
            raise DANI001CalibrationError("nonabsolute libgomp target")
        try:
            resolved_candidate = reported_candidate.resolve(strict=True)
        except OSError as error:
            raise DANI001CalibrationError("unresolved libgomp target") from error
        if (
            not resolved_candidate.is_file()
            or not reported_candidate.name.startswith("libgomp.so")
            or not resolved_candidate.name.startswith("libgomp.so")
        ):
            raise DANI001CalibrationError("invalid libgomp target")
        candidates.append((reported_candidate.name, resolved_candidate))
    if len(candidates) != 1:
        raise DANI001CalibrationError("unique OpenMP libgomp binding unavailable")
    openmp_library_name, openmp_library = candidates[0]
    openmp_sha256 = _sha256_path(openmp_library)
    projection = {
        "python": python_version,
        "implementation": implementation,
        "machine": machine,
        "system": system,
        "byteorder": sys.byteorder,
        "binary64": "IEEE754_ROUND_TO_NEAREST",
        "numpy": numpy_version,
        "locale": "C",
        "timezone": "UTC",
        "workers": [1, 32],
        "openmp_library_name": openmp_library_name,
        "openmp_library_sha256": openmp_sha256,
    }
    projection["runtime_image_sha256"] = _sha256(_canonical_json(projection))
    return projection


def _all_outputs_absent() -> bool:
    return all(not os.path.lexists(ROOT / relative) for relative in ALL_OUTPUT_RELS)


def _write_no_clobber_one(path: Path, payload: bytes) -> None:
    if os.path.lexists(path):
        raise DANI001CalibrationError("output destination collision")
    staging = Path(tempfile.mkdtemp(prefix="dani001-install-", dir=Path(tempfile.gettempdir())))
    installed = False
    source: Path | None = None
    source_proof: _FileProof | None = None
    try:
        source = staging / path.name
        with source.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        source_proof = _file_proof(source)
        if (source_proof.size, source_proof.sha256) != (
            len(payload), _sha256(payload),
        ):
            raise DANI001CalibrationError("freeze staging byte proof failed")
        try:
            os.link(source, path)
        except FileExistsError as error:
            raise DANI001CalibrationError("output no-clobber race") from error
        installed = True
        _prove_freeze_staged_link(source, path, source_proof)
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except BaseException:
        if installed and source is not None and source_proof is not None:
            _rollback_freeze_staged_link(source, path, source_proof)
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _create_freeze(
    *,
    static_auditor_sha256: str,
) -> str:
    """Create the calibration freeze without importing or running calibration."""

    _enforce_locale_timezone()
    if not HEX64.fullmatch(static_auditor_sha256):
        raise DANI001CalibrationError("static auditor source SHA-256 malformed")
    if CALIBRATION_SPEC_SHA256 == "PENDING_FINAL_REGISTERED_BYTES":
        raise DANI001CalibrationError("runner is not bound to a final calibration spec")
    if not _all_outputs_absent():
        raise DANI001CalibrationError("calibration/validation output already exists")
    if os.path.lexists(ROOT / FREEZE_REL):
        raise DANI001CalibrationError("calibration freeze destination exists")

    science = _path_binding(SCIENCE_SPEC_REL)
    calibration = _path_binding(CALIBRATION_SPEC_REL)
    if science["sha256"] != SCIENCE_SPEC_SHA256:
        raise DANI001CalibrationError("science specification drift")
    if calibration["sha256"] != CALIBRATION_SPEC_SHA256:
        raise DANI001CalibrationError("calibration specification drift")
    local = [_path_binding(value) for value in LOCAL_INPUT_RELS]
    _assert_registered_local_bindings(local)
    code = [_path_binding(value) for value in CODE_RELS]
    manifest = _path_binding(MANIFEST_REL)

    core_directory, library_sha256, compiler_version = _build_core_from_bytes(
        (ROOT / CORE_CPP_REL).read_bytes(),
        (ROOT / CORE_H_REL).read_bytes(),
        parent=Path(tempfile.gettempdir()),
    )
    try:
        library = core_directory / "libdani001_core.so"
        runtime = _runtime_projection(core_library=library)
    finally:
        shutil.rmtree(core_directory, ignore_errors=True)
    if compiler_version != FROZEN_CXX_VERSION_STDOUT:
        raise DANI001CalibrationError("full compiler version bytes drift")

    read_allowlist = [
        SCIENCE_SPEC_REL, CALIBRATION_SPEC_REL, FREEZE_REL, MANIFEST_REL,
        PANEL_REL, GENERATOR_REL, CORE_PY_REL, CORE_H_REL, CORE_CPP_REL,
        RUNNER_REL, *LOCAL_INPUT_RELS,
    ]
    freeze = {
        "schema": "dani001-target-blind-calibration-freeze-v1",
        "registered_commit": REGISTERED_COMMIT,
        "science_spec": science,
        "calibration_spec": calibration,
        "local_inputs": local,
        "external_inputs": [dict(value) for value in EXTERNAL_BINDINGS],
        "code": code,
        "synthetic_manifest": manifest,
        "runtime": runtime,
        "core_build": {
            "compiler_path": FROZEN_CXX,
            "compiler_sha256": FROZEN_CXX_SHA256,
            "compiler_version_stdout_hex": compiler_version.hex(),
            "argv": list(COMPILE_ARGV),
            "shared_library_sha256": library_sha256,
            "abi_version": 1,
            "runtime_image_sha256": runtime["runtime_image_sha256"],
        },
        "read_allowlist": read_allowlist,
        "network_allowlist": [value["url"] for value in EXTERNAL_BINDINGS],
        "temporary_allowlist": list(TEMPORARY_ALLOWLIST),
        "producer_outputs_absent": list(OUTPUT_RELS),
        "validator_outputs_absent": [VALIDATION_JSON_REL, VALIDATION_MD_REL],
        "producer_write_allowlist": list(OUTPUT_RELS),
        "validator_write_allowlist": [VALIDATION_JSON_REL, VALIDATION_MD_REL],
        "static_audit": {
            "status": "GO",
            "review_id": "DANI001_CALIBRATION_FREEZE_STATIC_AUDIT_V1",
            "auditor_source_sha256": static_auditor_sha256,
        },
    }
    payload = _canonical_json(freeze)
    if _decode_canonical_freeze(payload) != freeze:
        raise DANI001CalibrationError("constructed freeze canonical round-trip failed")
    _write_no_clobber_one(ROOT / FREEZE_REL, payload)
    return _sha256(payload)


def _synthetic_suite(
    core: object,
    generator: object,
    manifest: Mapping[str, object],
) -> tuple[dict[str, object], bool]:
    aggregate = manifest.get("aggregate_expectations")
    if not isinstance(aggregate, dict):
        raise DANI001CalibrationError("synthetic aggregate manifest missing")
    assertion_ids = aggregate.get("assertion_ids")
    if not isinstance(assertion_ids, dict) or tuple(assertion_ids) != CONTROL_ORDER:
        raise DANI001CalibrationError("synthetic assertion order drift")
    values: dict[str, dict[str, bool]] = {
        name: {} for name in CONTROL_ORDER
    }
    evidence_values: dict[str, dict[str, str]] = {
        "affix_equivalence": {},
        "unreachable_invariance": {},
    }
    worlds = generator.build_all_worlds()
    if len(worlds) != 238:
        raise DANI001CalibrationError("synthetic world inventory drift")
    plant_successful = 0
    null_false_passes = 0
    plant_zero = None
    for world in worlds:
        evaluation = _evaluate_world(
            core,
            generator,
            world,
            require_scalar=world.family in {"TOY_PLANT", "TOY_NULL"},
        )
        assertion = str(world.expected["assertions"][0]["id"])
        if world.family in {"TOY_PLANT", "TOY_NULL"}:
            values["toys"][assertion] = evaluation.world_signature
        elif world.family == "PLANT":
            values["plants"][assertion] = evaluation.world_signature
            plant_successful += int(evaluation.world_signature)
            if world.world_id == "PLANT_000":
                plant_zero = world
        elif world.family == "NULL":
            values["nulls"][assertion] = evaluation.world_signature
            null_false_passes += int(evaluation.all_required_gates)
        elif world.family == "ADVERSARY":
            values["adversaries"][assertion] = evaluation.world_signature
        else:
            raise DANI001CalibrationError("unknown world aggregate family")
        affix_assertion = f"AFFIX_{world.world_id}_EQUIVALENCE"
        values["affix_equivalence"][affix_assertion] = (
            evaluation.affix_equivalence
        )
        evidence_values["affix_equivalence"][affix_assertion] = (
            evaluation.affix_evidence_sha256
        )
        if world.variable_count == 10:
            unreachable_assertion = (
                f"UNREACHABLE_{world.world_id}_INVARIANCE"
            )
            values["unreachable_invariance"][unreachable_assertion] = (
                evaluation.unreachable_invariance
            )
            if evaluation.unreachable_evidence_sha256 is None:
                raise DANI001CalibrationError(
                    "ten-variable world lacks unreachable evidence"
                )
            evidence_values["unreachable_invariance"][unreachable_assertion] = (
                evaluation.unreachable_evidence_sha256
            )
        del evaluation

    values["nulls"]["NULL_FALSE_PASS_COUNT_LE_1"] = null_false_passes <= 1
    if plant_zero is None:
        raise DANI001CalibrationError("PLANT_000 is absent")
    values["parser"] = _parser_assertions(generator, manifest)
    plant_zero_evaluation = _evaluate_world(core, generator, plant_zero)
    values["mutations"] = _mutation_assertions(
        core, generator, manifest, plant_zero, plant_zero_evaluation
    )

    # These exact whole-orbit controls are intentionally deferred until every
    # ordinary world has completed, so their memory cannot select worlds.
    values["workers"]["WORKER_1_32_VECTOR_EQUALITY"] = _worker_control(
        core, generator, plant_zero, plant_zero_evaluation
    )
    _rho, rho_audit = generator.first_nonidentity_permutation(
        "conjugacy-permutation", 10
    )
    frozen_rho_audit = aggregate.get("generator_fields", {}).get("conjugacy")
    rho_fields_match = (
        frozen_rho_audit == [value.to_manifest() for value in rho_audit]
    )
    values["conjugacy"]["CONJUGACY_VECTOR_EQUALITY"] = bool(
        rho_fields_match
        and _conjugacy_control(
            core, generator, plant_zero, plant_zero_evaluation
        )
    )
    del plant_zero_evaluation

    public: dict[str, object] = {}
    for name in CONTROL_ORDER:
        ids = assertion_ids.get(name)
        if not isinstance(ids, list) or any(not isinstance(value, str) for value in ids):
            raise DANI001CalibrationError("malformed assertion ID array")
        if name == "plants":
            public[name] = _aggregate_assertions(
                name, ids, values[name], successful=plant_successful
            )
        elif name == "nulls":
            public[name] = _aggregate_assertions(
                name, ids, values[name], false_passes=null_false_passes
            )
        elif name in evidence_values:
            public[name] = _aggregate_assertions(
                name, ids, values[name], evidence=evidence_values[name]
            )
        else:
            public[name] = _aggregate_assertions(name, ids, values[name])
    if [public[name]["total"] for name in CONTROL_ORDER] != [
        4, 100, 129, 6, 4, 20, 1, 1, 238, 234,
    ]:
        raise DANI001CalibrationError("public synthetic totals drift")
    gate = all(bool(public[name]["gate"]) for name in CONTROL_ORDER)
    return public, gate


def _validate_path_binding(
    value: object, expected_path: str, *, read_now: bool
) -> bytes | None:
    if not isinstance(value, dict) or set(value) != {"path", "sha256", "size"}:
        raise DANI001CalibrationError("malformed freeze path binding")
    if (
        type(value["path"]) is not str
        or value["path"] != expected_path
        or type(value["sha256"]) is not str
        or not HEX64.fullmatch(value["sha256"])
    ):
        raise DANI001CalibrationError("freeze path/hash binding drift")
    if type(value["size"]) is not int or value["size"] < 0:
        raise DANI001CalibrationError("freeze path size malformed")
    if not read_now:
        return None
    data = (ROOT / expected_path).read_bytes()
    if len(data) != value["size"] or _sha256(data) != value["sha256"]:
        raise DANI001CalibrationError(f"bound bytes drift: {expected_path}")
    return data


def _validate_freeze_and_load(
    freeze_sha256: str,
) -> tuple[dict[str, object], dict[str, bytes], bytes]:
    if not HEX64.fullmatch(freeze_sha256):
        raise DANI001CalibrationError("freeze SHA-256 malformed")
    freeze_bytes = (ROOT / FREEZE_REL).read_bytes()
    if _sha256(freeze_bytes) != freeze_sha256:
        raise DANI001CalibrationError("calibration freeze SHA-256 mismatch")
    freeze = _decode_canonical_freeze(freeze_bytes)
    exact_top = {
        "schema", "registered_commit", "science_spec", "calibration_spec",
        "local_inputs", "external_inputs", "code", "synthetic_manifest",
        "runtime", "core_build", "read_allowlist", "network_allowlist",
        "temporary_allowlist", "producer_outputs_absent",
        "validator_outputs_absent", "producer_write_allowlist",
        "validator_write_allowlist", "static_audit",
    }
    if not isinstance(freeze, dict) or set(freeze) != exact_top:
        raise DANI001CalibrationError("calibration freeze schema drift")
    if freeze["schema"] != "dani001-target-blind-calibration-freeze-v1":
        raise DANI001CalibrationError("calibration freeze version drift")
    if freeze["registered_commit"] != REGISTERED_COMMIT:
        raise DANI001CalibrationError("registered commit drift")
    static = freeze["static_audit"]
    if (
        not isinstance(static, dict)
        or set(static) != {"status", "review_id", "auditor_source_sha256"}
        or static["status"] != "GO"
        or static["review_id"] != "DANI001_CALIBRATION_FREEZE_STATIC_AUDIT_V1"
        or not HEX64.fullmatch(str(static["auditor_source_sha256"]))
    ):
        raise DANI001CalibrationError("static calibration audit is not GO")
    if tuple(freeze["producer_outputs_absent"]) != OUTPUT_RELS:
        raise DANI001CalibrationError("producer absence binding drift")
    if tuple(freeze["validator_outputs_absent"]) != (
        VALIDATION_JSON_REL, VALIDATION_MD_REL,
    ):
        raise DANI001CalibrationError("validator absence binding drift")
    if tuple(freeze["producer_write_allowlist"]) != OUTPUT_RELS:
        raise DANI001CalibrationError("producer write allowlist drift")
    if tuple(freeze["validator_write_allowlist"]) != (
        VALIDATION_JSON_REL, VALIDATION_MD_REL,
    ):
        raise DANI001CalibrationError("validator write allowlist drift")
    expected_read = (
        SCIENCE_SPEC_REL, CALIBRATION_SPEC_REL, FREEZE_REL, MANIFEST_REL,
        PANEL_REL, GENERATOR_REL, CORE_PY_REL, CORE_H_REL, CORE_CPP_REL,
        RUNNER_REL, *LOCAL_INPUT_RELS,
    )
    if tuple(freeze["read_allowlist"]) != expected_read:
        raise DANI001CalibrationError("producer read allowlist drift")
    if tuple(freeze["network_allowlist"]) != tuple(
        value["url"] for value in EXTERNAL_BINDINGS
    ):
        raise DANI001CalibrationError("network allowlist drift")
    if (
        not isinstance(freeze["temporary_allowlist"], list)
        or tuple(freeze["temporary_allowlist"]) != TEMPORARY_ALLOWLIST
    ):
        raise DANI001CalibrationError("temporary allowlist drift")
    if freeze["external_inputs"] != [dict(value) for value in EXTERNAL_BINDINGS]:
        raise DANI001CalibrationError("external input binding drift")
    if not _all_outputs_absent():
        raise DANI001CalibrationError("frozen output absence drift")

    loaded: dict[str, bytes] = {}
    loaded[SCIENCE_SPEC_REL] = _validate_path_binding(
        freeze["science_spec"], SCIENCE_SPEC_REL, read_now=True
    )  # type: ignore[assignment]
    loaded[CALIBRATION_SPEC_REL] = _validate_path_binding(
        freeze["calibration_spec"], CALIBRATION_SPEC_REL, read_now=True
    )  # type: ignore[assignment]
    if _sha256(loaded[SCIENCE_SPEC_REL]) != SCIENCE_SPEC_SHA256:
        raise DANI001CalibrationError("science specification hash drift")
    if _sha256(loaded[CALIBRATION_SPEC_REL]) != CALIBRATION_SPEC_SHA256:
        raise DANI001CalibrationError("calibration specification hash drift")
    loaded[MANIFEST_REL] = _validate_path_binding(
        freeze["synthetic_manifest"], MANIFEST_REL, read_now=True
    )  # type: ignore[assignment]

    code = freeze["code"]
    if not isinstance(code, list) or len(code) != len(CODE_RELS):
        raise DANI001CalibrationError("freeze code inventory drift")
    for binding, relative in zip(code, CODE_RELS, strict=True):
        # Producer is forbidden to read validator source.  Its frozen binding
        # was created in the separately authorized freeze phase.
        read_now = relative != VALIDATOR_REL
        data = _validate_path_binding(binding, relative, read_now=read_now)
        if data is not None:
            loaded[relative] = data
    local = freeze["local_inputs"]
    _assert_registered_local_bindings(local)
    for binding, relative in zip(local, LOCAL_INPUT_RELS, strict=True):
        _validate_path_binding(binding, relative, read_now=False)
    return freeze, loaded, freeze_bytes


def _load_module(name: str, relative: str, payload: bytes) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    module.__package__ = ""
    module.__spec__ = None
    sys.modules[name] = module
    try:
        exec(compile(payload, str(ROOT / relative), "exec", dont_inherit=True), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def _load_registered_modules(
    loaded: Mapping[str, bytes],
) -> tuple[types.ModuleType, types.ModuleType, types.ModuleType]:
    panel = _load_module("dani001_panel", PANEL_REL, loaded[PANEL_REL])
    generator = _load_module(
        "dani001_calibration_generator", GENERATOR_REL, loaded[GENERATOR_REL]
    )
    core = _load_module("dani001_core", CORE_PY_REL, loaded[CORE_PY_REL])
    return panel, generator, core


def _identity_access(
    *, actual_opened: bool, actual_guard: ActualCoreGuard | None
) -> dict[str, object]:
    if actual_opened:
        if actual_guard is None:
            raise DANI001CalibrationError("ACTUAL guard missing")
        actual_guard.assert_complete()
        primary_surfaces = actual_guard.primary_logical_view_surfaces
        evidence_surfaces = actual_guard.evidence_logical_view_surfaces
        primary_evaluations = actual_guard.primary_logical_map_view_evaluations
        evidence_evaluations = actual_guard.evidence_logical_map_view_evaluations
    else:
        if actual_guard is not None:
            raise DANI001CalibrationError("unused ACTUAL guard was constructed")
        primary_surfaces = 0
        evidence_surfaces = 0
        primary_evaluations = 0
        evidence_evaluations = 0
    return {
        "rank0_requests": 0,
        "rank0_maps_evaluated": 0,
        "rank0_match_calls": 0,
        "rank0_values_stored": 0,
        "rank0_values_inferred": 0,
        "actual_rank_interval_start": ACTUAL_BEGIN if actual_opened else None,
        "actual_rank_interval_stop": ACTUAL_END if actual_opened else None,
        "actual_primary_logical_view_surfaces": primary_surfaces,
        "actual_evidence_logical_view_surfaces": evidence_surfaces,
        "actual_logical_view_surfaces": primary_surfaces + evidence_surfaces,
        "actual_primary_logical_map_view_evaluations": primary_evaluations,
        "actual_evidence_logical_map_view_evaluations": evidence_evaluations,
        "actual_logical_map_view_evaluations": (
            primary_evaluations + evidence_evaluations
        ),
    }


def _isolation_object(*, actual_opened: bool) -> dict[str, object]:
    return {
        "read_allowlist_pass": _FORBIDDEN_READS == 0,
        "write_allowlist_pass": _FORBIDDEN_WRITES == 0,
        "network_allowlist_pass": _FORBIDDEN_NETWORK == 0,
        "temporary_allowlist_pass": _TEMP_VIOLATIONS == 0,
        "output_destinations_absent_pass": _all_outputs_absent(),
        "acquisition_inventory_pass": True,
        "synthetic_gate_actual_access_pass": _PRE_SYNTHETIC_LOCAL_READS == 0,
        "forbidden_read_count": _FORBIDDEN_READS,
        "forbidden_write_count": _FORBIDDEN_WRITES,
        "forbidden_network_count": _FORBIDDEN_NETWORK,
        "temporary_inventory_violation_count": _TEMP_VIOLATIONS,
        "output_collision_count": _OUTPUT_COLLISIONS,
        "pre_synthetic_actual_local_read_count": _PRE_SYNTHETIC_LOCAL_READS,
        "pre_synthetic_lexicon_projection_call_count": 0,
        "post_synthetic_lexicon_projection_call_count": (
            _PROJECTION_CALLS if actual_opened else 0
        ),
    }


def _input_checks(*, local_opened: bool) -> dict[str, object]:
    return {
        "registered_commit_pass": True,
        "science_spec_pass": True,
        "calibration_spec_pass": True,
        "calibration_freeze_pass": True,
        "synthetic_manifest_pass": True,
        "code_hashes_pass": True,
        "runtime_pass": True,
        "compiler_binary_pass": True,
        "core_build_pass": True,
        "external_pipeline_body_pass": True,
        "external_lexicon_body_pass": True,
        "stable_projection_pass": True,
        "local_inputs_pass": True if local_opened else None,
    }


def _result_object(
    value: object, keys: Sequence[str], label: str
) -> Mapping[str, object]:
    if not isinstance(value, dict) or set(value) != set(keys):
        raise DANI001CalibrationError(f"{label} schema drift")
    return value


def _result_uint(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise DANI001CalibrationError(f"{label} must be a nonnegative integer")
    return value


def _result_bool(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise DANI001CalibrationError(f"{label} must be an exact boolean")
    return value


def _result_hex(value: object, label: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise DANI001CalibrationError(f"{label} must be lowercase SHA-256")
    return value


def _validate_result_path_object(value: object, label: str) -> None:
    record = _result_object(value, ("path", "sha256", "size"), label)
    if not isinstance(record["path"], str) or not record["path"]:
        raise DANI001CalibrationError(f"{label} path type drift")
    _result_hex(record["sha256"], f"{label}.sha256")
    _result_uint(record["size"], f"{label}.size")


def _validate_result_runtime(value: object) -> None:
    keys = (
        "python", "implementation", "machine", "system", "byteorder",
        "binary64", "numpy", "locale", "timezone", "workers",
        "openmp_library_name", "openmp_library_sha256",
        "runtime_image_sha256",
    )
    runtime = _result_object(value, keys, "result runtime")
    for key in keys[:9]:
        if not isinstance(runtime[key], str):
            raise DANI001CalibrationError(f"result runtime.{key} type drift")
    if (
        not isinstance(runtime["workers"], list)
        or len(runtime["workers"]) != 2
        or any(type(item) is not int for item in runtime["workers"])
        or runtime["workers"] != [1, 32]
        or not isinstance(runtime["openmp_library_name"], str)
        or not runtime["openmp_library_name"]
    ):
        raise DANI001CalibrationError("result runtime worker/OpenMP schema drift")
    _result_hex(
        runtime["openmp_library_sha256"],
        "result runtime.openmp_library_sha256",
    )
    _result_hex(
        runtime["runtime_image_sha256"],
        "result runtime.runtime_image_sha256",
    )


def _validate_result_controls(value: object) -> None:
    controls = _result_object(value, CONTROL_ORDER, "synthetic controls")
    common = ("total", "passed", "failed", "aggregate_sha256", "gate")
    for name in CONTROL_ORDER:
        extras = (
            ("successful", "threshold") if name == "plants"
            else ("false_passes", "threshold") if name == "nulls"
            else ()
        )
        member = _result_object(
            controls[name], (*common, *extras), f"synthetic controls.{name}"
        )
        total = _result_uint(member["total"], f"{name}.total")
        passed = _result_uint(member["passed"], f"{name}.passed")
        failed = _result_uint(member["failed"], f"{name}.failed")
        if passed + failed != total:
            raise DANI001CalibrationError(f"{name} aggregate count drift")
        _result_hex(member["aggregate_sha256"], f"{name}.aggregate_sha256")
        _result_bool(member["gate"], f"{name}.gate")
        if name == "plants":
            _result_uint(member["successful"], "plants.successful")
            if type(member["threshold"]) is not int or member["threshold"] != 95:
                raise DANI001CalibrationError("plants threshold type/value drift")
        elif name == "nulls":
            _result_uint(member["false_passes"], "nulls.false_passes")
            if type(member["threshold"]) is not int or member["threshold"] != 1:
                raise DANI001CalibrationError("nulls threshold type/value drift")


def _validate_result_actual(value: object) -> None:
    actual = _result_object(
        value,
        (
            "panel_counts", "lexicon_counts", "views",
            "mandatory_capacity_pass", "conditional_view_statuses",
            "actual_nonidentity_vector_digest_sha256",
            "implementation_invariant_digest_sha256",
        ),
        "actual capacity",
    )
    panel_counts = actual["panel_counts"]
    if not isinstance(panel_counts, list) or len(panel_counts) != 6:
        raise DANI001CalibrationError("actual panel-count inventory drift")
    for record, (edition, panel) in zip(
        panel_counts,
        ((e, p) for e in EDITION_ORDER for p in PANEL_ORDER),
        strict=True,
    ):
        member = _result_object(
            record,
            (
                "edition", "panel", "token_count", "normalized_type_count",
                "folio_count", "strict_literal_token_count",
            ),
            "actual panel count",
        )
        if member["edition"] != edition or member["panel"] != panel:
            raise DANI001CalibrationError("actual panel-count order drift")
        for key in (
            "token_count", "normalized_type_count", "folio_count",
            "strict_literal_token_count",
        ):
            _result_uint(member[key], f"actual panel count.{key}")

    lexicon = _result_object(
        actual["lexicon_counts"],
        (
            "keys", "entries", "reachable_keys", "unreachable_keys",
            "source_present_keys", "source_present_reachable_keys",
            "strict_no_function_keys", "strict_no_function_reachable_keys",
            "views",
        ),
        "actual lexicon counts",
    )
    for key in (
        "keys", "entries", "reachable_keys", "unreachable_keys",
        "source_present_keys", "source_present_reachable_keys",
        "strict_no_function_keys", "strict_no_function_reachable_keys",
    ):
        _result_uint(lexicon[key], f"actual lexicon counts.{key}")
    public_lexicon_views = (
        "FULL", "REACHABLE", "SOURCE_PRESENT", "STRICT_NO_FUNCTION",
        "LEAVE_OUT_ASTRO", "LEAVE_OUT_BOTANICAL", "LEAVE_OUT_FUNCTION",
        "LEAVE_OUT_GENERAL", "LEAVE_OUT_MEDICAL", "LEAVE_OUT_PHARMA",
    )
    lexicon_views = lexicon["views"]
    if not isinstance(lexicon_views, list) or len(lexicon_views) != 10:
        raise DANI001CalibrationError("actual lexicon-view inventory drift")
    for record, view_name in zip(lexicon_views, public_lexicon_views, strict=True):
        member = _result_object(
            record,
            (
                "view", "total_key_count", "reachable_key_count",
                "direct_code_count", "deposited_affix_code_count",
            ),
            "actual lexicon view",
        )
        if member["view"] != view_name:
            raise DANI001CalibrationError("actual lexicon-view order drift")
        for key in (
            "total_key_count", "reachable_key_count", "direct_code_count",
            "deposited_affix_code_count",
        ):
            _result_uint(member[key], f"actual lexicon view.{key}")

    views = actual["views"]
    if not isinstance(views, list) or len(views) != len(VIEW_ORDER):
        raise DANI001CalibrationError("actual scoring-view inventory drift")
    for view_record, view_name in zip(views, VIEW_ORDER, strict=True):
        view_member = _result_object(
            view_record, ("view", "surfaces"), "actual scoring view"
        )
        if view_member["view"] != view_name:
            raise DANI001CalibrationError("actual scoring-view order drift")
        surface_rows = view_member["surfaces"]
        if not isinstance(surface_rows, list) or len(surface_rows) != 6:
            raise DANI001CalibrationError("actual surface inventory drift")
        for surface_record, (edition, panel) in zip(
            surface_rows,
            ((e, p) for e in EDITION_ORDER for p in PANEL_ORDER),
            strict=True,
        ):
            surface = _result_object(
                surface_record,
                (
                    "edition", "panel", "variable_type_count",
                    "capacity_folio_count", "token_sd_positive",
                    "type_sd_positive", "folio_sd_positive",
                    "token_nonidentity_vector_sha256",
                    "type_nonidentity_vector_sha256",
                    "folio_nonidentity_vector_sha256", "affix_equivalence",
                ),
                "actual surface",
            )
            if surface["edition"] != edition or surface["panel"] != panel:
                raise DANI001CalibrationError("actual surface order drift")
            _result_uint(surface["variable_type_count"], "variable type count")
            _result_uint(surface["capacity_folio_count"], "capacity folio count")
            for key in (
                "token_sd_positive", "type_sd_positive", "folio_sd_positive",
            ):
                _result_bool(surface[key], f"actual surface.{key}")
            for key in (
                "token_nonidentity_vector_sha256",
                "type_nonidentity_vector_sha256",
                "folio_nonidentity_vector_sha256",
            ):
                _result_hex(surface[key], f"actual surface.{key}")
            affix = surface["affix_equivalence"]
            if view_name == "FULL_DEPOSITED_AFFIX":
                _result_bool(affix, "actual surface.affix_equivalence")
            elif affix is not None:
                raise DANI001CalibrationError(
                    "non-affix actual surface has equivalence value"
                )

    _result_bool(actual["mandatory_capacity_pass"], "mandatory capacity pass")
    conditional_names = (
        "SOURCE_PRESENT", "LEAVE_ASTRO_OUT", "LEAVE_BOTANICAL_OUT",
        "LEAVE_FUNCTION_OUT", "LEAVE_GENERAL_OUT", "LEAVE_MEDICAL_OUT",
        "LEAVE_PHARMA_OUT",
    )
    conditional = actual["conditional_view_statuses"]
    if not isinstance(conditional, list) or len(conditional) != 7:
        raise DANI001CalibrationError("conditional-view inventory drift")
    for record, name in zip(conditional, conditional_names, strict=True):
        member = _result_object(
            record, ("view", "status"), "conditional view status"
        )
        if member["view"] != name or member["status"] not in {
            "POWERED", "INSUFFICIENT"
        }:
            raise DANI001CalibrationError("conditional-view order/status drift")
    _result_hex(
        actual["actual_nonidentity_vector_digest_sha256"],
        "actual nonidentity vector digest",
    )
    _result_hex(
        actual["implementation_invariant_digest_sha256"],
        "actual implementation invariant digest",
    )


def _validate_result_identity(value: object, *, opened: bool) -> None:
    keys = (
        "rank0_requests", "rank0_maps_evaluated", "rank0_match_calls",
        "rank0_values_stored", "rank0_values_inferred",
        "actual_rank_interval_start", "actual_rank_interval_stop",
        "actual_primary_logical_view_surfaces",
        "actual_evidence_logical_view_surfaces", "actual_logical_view_surfaces",
        "actual_primary_logical_map_view_evaluations",
        "actual_evidence_logical_map_view_evaluations",
        "actual_logical_map_view_evaluations",
    )
    identity = _result_object(value, keys, "identity access")
    for key in keys[:5]:
        if type(identity[key]) is not int or identity[key] != 0:
            raise DANI001CalibrationError(f"identity access.{key} drift")
    expected = (
        (1, 3_628_800, 72, 18, 90, 261_273_528, 65_318_382, 326_591_910)
        if opened else (None, None, 0, 0, 0, 0, 0, 0)
    )
    actual = tuple(identity[key] for key in keys[5:])
    if actual != expected or any(
        value is not None and type(value) is not int for value in actual
    ):
        raise DANI001CalibrationError("identity access interval/count drift")


def _validate_result_schema(result: object, *, actual_opened: bool) -> None:
    keys = (
        "schema", "experiment", "status", "claim_ceiling",
        "registered_science", "calibration_spec",
        "calibration_freeze_sha256", "synthetic_manifest_sha256", "runtime",
        "isolation", "input_checks", "synthetic_controls", "actual_capacity",
        "identity_access", "decision",
    )
    root = _result_object(result, keys, "producer result")
    allowed_status = {
        "STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED",
        "STOP_UNPOWERED_BEFORE_RELEASED_MAP_SCORE",
        "STOP_MANDATORY_ROBUSTNESS_CAPACITY_BEFORE_RELEASED_MAP_SCORE",
        "PASS_TARGET_BLIND_CALIBRATION_AND_CAPACITY_IDENTITY_UNOPENED",
    }
    if (
        root["schema"] != "dani001-target-blind-calibration-result-v1"
        or root["experiment"] != "DANI001"
        or not isinstance(root["status"], str)
        or root["status"] not in allowed_status
        or root["decision"] != root["status"]
        or root["claim_ceiling"] != (
            "Target-blind engineering calibration only; no language, lexeme, "
            "plaintext, or translation."
        )
    ):
        raise DANI001CalibrationError("producer result header drift")
    if (
        (not actual_opened and root["status"] !=
         "STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED")
        or (actual_opened and root["status"] ==
            "STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED")
    ):
        raise DANI001CalibrationError("producer result actual-open status drift")
    _validate_result_path_object(root["registered_science"], "registered science")
    _validate_result_path_object(root["calibration_spec"], "calibration spec")
    _result_hex(root["calibration_freeze_sha256"], "calibration freeze hash")
    _result_hex(root["synthetic_manifest_sha256"], "synthetic manifest hash")
    _validate_result_runtime(root["runtime"])

    isolation_keys = (
        "read_allowlist_pass", "write_allowlist_pass", "network_allowlist_pass",
        "temporary_allowlist_pass", "output_destinations_absent_pass",
        "acquisition_inventory_pass", "synthetic_gate_actual_access_pass",
        "forbidden_read_count", "forbidden_write_count",
        "forbidden_network_count", "temporary_inventory_violation_count",
        "output_collision_count", "pre_synthetic_actual_local_read_count",
        "pre_synthetic_lexicon_projection_call_count",
        "post_synthetic_lexicon_projection_call_count",
    )
    isolation = _result_object(root["isolation"], isolation_keys, "isolation")
    for key in isolation_keys[:7]:
        if _result_bool(isolation[key], f"isolation.{key}") is not True:
            raise DANI001CalibrationError(f"isolation.{key} is not true")
    for key in isolation_keys[7:]:
        _result_uint(isolation[key], f"isolation.{key}")
    if (
        any(isolation[key] != 0 for key in isolation_keys[7:-1])
        or isolation["post_synthetic_lexicon_projection_call_count"]
        != (1 if actual_opened else 0)
    ):
        raise DANI001CalibrationError("isolation counter value drift")

    check_keys = (
        "registered_commit_pass", "science_spec_pass", "calibration_spec_pass",
        "calibration_freeze_pass", "synthetic_manifest_pass", "code_hashes_pass",
        "runtime_pass", "compiler_binary_pass", "core_build_pass",
        "external_pipeline_body_pass", "external_lexicon_body_pass",
        "stable_projection_pass", "local_inputs_pass",
    )
    checks = _result_object(root["input_checks"], check_keys, "input checks")
    for key in check_keys[:-1]:
        if _result_bool(checks[key], f"input checks.{key}") is not True:
            raise DANI001CalibrationError(f"input checks.{key} is not true")
    if checks["local_inputs_pass"] is not (True if actual_opened else None):
        raise DANI001CalibrationError("input checks.local_inputs_pass drift")

    _validate_result_controls(root["synthetic_controls"])
    if actual_opened:
        _validate_result_actual(root["actual_capacity"])
    elif root["actual_capacity"] is not None:
        raise DANI001CalibrationError("unopened result contains actual capacity")
    _validate_result_identity(root["identity_access"], opened=actual_opened)


def _report_bytes(result: Mapping[str, object], result_sha256: str) -> bytes:
    controls = result["synthetic_controls"]
    passed = sum(int(controls[name]["passed"]) for name in CONTROL_ORDER)
    total = sum(int(controls[name]["total"]) for name in CONTROL_ORDER)
    actual = result["actual_capacity"]
    actual_text = (
        "NOT_OPENED" if actual is None
        else "PASS" if bool(actual["mandatory_capacity_pass"])
        else "FAIL"
    )
    lines = (
        "# DANI001 target-blind calibration",
        "",
        f"- Status: `{result['status']}`",
        f"- Synthetic controls: `{passed}/{total}`",
        f"- Distributed plants: `{controls['plants']['successful']}/100` (required >=95)",
        f"- Map-independent null false passes: `{controls['nulls']['false_passes']}/128` (required <=1)",
        f"- Actual mandatory capacity: `{actual_text}`",
        "- Real rank-0 evaluations: `0`",
        "- Real rank-0 inferences: `0`",
        f"- Decision: `{result['decision']}`",
        "- Claim ceiling: conditional engineering calibration only; no language, lexeme, plaintext, or translation.",
        f"- Result JSON SHA-256: `{result_sha256}`",
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _install_pair(
    json_payload: bytes,
    markdown_payload: bytes,
    actual_guard: ActualCoreGuard | None = None,
) -> None:
    global _OUTPUT_COLLISIONS
    if not _all_outputs_absent():
        _OUTPUT_COLLISIONS += 1
        raise DANI001CalibrationError("output collision before paired install")
    staging = Path(tempfile.mkdtemp(prefix="dani001-output-stage-"))
    _REGISTERED_TEMP_ROOTS.add(staging.resolve())
    installed: list[tuple[Path, Path, _FileProof]] = []
    staged_proofs: dict[Path, _FileProof] = {}
    try:
        staged_json = staging / "result.json"
        staged_md = staging / "report.md"
        for path, payload in ((staged_json, json_payload), (staged_md, markdown_payload)):
            with path.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            staged_proofs[path] = _file_proof(path)
            if (
                staged_proofs[path].size != len(payload)
                or staged_proofs[path].sha256 != _sha256(payload)
            ):
                raise DANI001CalibrationError("staged output byte proof failed")
        for source, relative in (
            (staged_json, OUT_JSON_REL), (staged_md, OUT_MD_REL),
        ):
            destination = ROOT / relative
            try:
                os.link(source, destination)
            except FileExistsError as error:
                _OUTPUT_COLLISIONS += 1
                raise DANI001CalibrationError("paired output no-clobber race") from error
            source_proof = staged_proofs[source]
            installed.append((source, destination, source_proof))
            _prove_result_staged_link(source, destination, source_proof)
        directory_fd = os.open(RESULTS, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        # Hash the staged inode again after both links and the directory
        # durability barrier.  Repository destinations are lstat-only.
        for source, destination, source_proof in installed:
            _prove_result_staged_link(source, destination, source_proof)
        if actual_guard is not None:
            actual_guard.mark_output_writes(len(installed))
            actual_guard.assert_complete(outputs=2)
    except BaseException as original_error:
        rollback_errors: list[str] = []
        for source, destination, proof in reversed(installed):
            try:
                _rollback_result_staged_link(source, destination, proof)
            except DANI001CalibrationError as rollback_error:
                # Never unlink a destination that failed the exact staged-file
                # proof.  Continue so any other exact staged link is recovered.
                rollback_errors.append(str(rollback_error))
        if rollback_errors:
            raise DANI001CalibrationError(
                "paired rollback refused foreign/raced destination: "
                + "; ".join(rollback_errors)
            ) from original_error
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        _REGISTERED_TEMP_ROOTS.discard(staging.resolve())


def _validate_core_build(
    freeze: Mapping[str, object],
    library_sha256: str,
    compiler_version: bytes,
    runtime: Mapping[str, object],
) -> None:
    value = freeze["core_build"]
    exact = {
        "compiler_path", "compiler_sha256", "compiler_version_stdout_hex",
        "argv", "shared_library_sha256", "abi_version",
        "runtime_image_sha256",
    }
    if not isinstance(value, dict) or set(value) != exact:
        raise DANI001CalibrationError("core-build freeze schema drift")
    if (
        value["compiler_path"] != FROZEN_CXX
        or value["compiler_sha256"] != FROZEN_CXX_SHA256
        or value["compiler_version_stdout_hex"] != compiler_version.hex()
        or tuple(value["argv"]) != COMPILE_ARGV
        or value["shared_library_sha256"] != library_sha256
        or value["abi_version"] != 1
        or value["runtime_image_sha256"] != runtime["runtime_image_sha256"]
    ):
        raise DANI001CalibrationError("core-build freeze binding drift")
    if freeze["runtime"] != runtime:
        raise DANI001CalibrationError("runtime freeze binding drift")


def _run_registered(freeze_sha256: str) -> tuple[str, str]:
    global np, _ACTUAL_ACCESS_GRANTED, _PROJECTION_CALLS
    global _SYNTHETIC_COMPLETE

    _enforce_locale_timezone()
    os.environ["OMP_NUM_THREADS"] = "32"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    import numpy as np

    freeze, loaded, freeze_bytes = _validate_freeze_and_load(freeze_sha256)
    panel, generator, core_wrapper = _load_registered_modules(loaded)
    if (
        generator.CALIBRATION_SPEC_SHA256 != CALIBRATION_SPEC_SHA256
        or generator.SCIENCE_SPEC_SHA256 != SCIENCE_SPEC_SHA256
    ):
        raise DANI001CalibrationError("generator specification binding drift")
    manifest_bytes = loaded[MANIFEST_REL]
    manifest = _json_no_duplicates(manifest_bytes)
    if not isinstance(manifest, dict):
        raise DANI001CalibrationError("synthetic manifest is not an object")

    core_directory, library_sha256, compiler_version = _build_core_from_bytes(
        loaded[CORE_CPP_REL], loaded[CORE_H_REL], parent=Path(tempfile.gettempdir())
    )
    library_path = core_directory / "libdani001_core.so"
    runtime = _runtime_projection(core_library=library_path)
    _validate_core_build(freeze, library_sha256, compiler_version, runtime)
    compiled_core = core_wrapper.Dani001Core(library_path)
    if not compiled_core.has_openmp or compiled_core.factorial(10) != ORBIT10:
        shutil.rmtree(core_directory, ignore_errors=True)
        raise DANI001CalibrationError("optimized integer core capability drift")

    controls = None
    actual_public = None
    actual_opened = False
    local_opened = False
    actual_guard: ActualCoreGuard | None = None
    try:
        acquisition_root: Path | None = None
        with panel.acquire_registered_external_files() as acquisition:
            acquisition_root = acquisition.temporary_root.resolve()
            panel._validate_acquisition_lease(acquisition)
            _REGISTERED_EXTERNAL_ROOTS.add(acquisition.temporary_root.resolve())
            _REGISTERED_TEMP_ROOTS.add(core_directory.resolve())
            _install_audit_hook()

            # The first synthetic operation is a byte-exact independent
            # regeneration of the entire source-free manifest.  It opens no
            # retained external body and no local manuscript source.
            regenerated = generator.manifest_bytes(CALIBRATION_SPEC_SHA256)
            if regenerated != manifest_bytes:
                raise DANI001CalibrationError("synthetic manifest reconstruction drift")
            controls, synthetics_pass = _synthetic_suite(
                compiled_core, generator, manifest
            )
            _SYNTHETIC_COMPLETE = True
            panel._validate_acquisition_lease(acquisition)

            if synthetics_pass:
                if _PROJECTION_CALLS != 0:
                    raise DANI001CalibrationError("projection counter drift")
                _PROJECTION_CALLS = 1
                lexicon = panel.project_acquired_lexicon(
                    acquisition, synthetic_gate_passed=True
                )
                if acquisition._projection_calls != [1]:
                    raise DANI001CalibrationError("panel projection counter drift")
                _ACTUAL_ACCESS_GRANTED = True
                # Now and only now may the five local inputs be opened.
                for binding, relative in zip(
                    freeze["local_inputs"], LOCAL_INPUT_RELS, strict=True
                ):
                    _validate_path_binding(binding, relative, read_now=True)
                source = panel.load_registered_source_panels(lexicon, ROOT)
                local_opened = True
                actual_guard = ActualCoreGuard(compiled_core)
                actual_with_internal = _actual_capacity(
                    actual_guard, source, lexicon
                )
                mandatory_by_view = actual_with_internal.pop("_mandatory_by_view")
                actual_public = actual_with_internal
                actual_opened = True
            else:
                mandatory_by_view = None
                if acquisition._projection_calls != [0] or _PROJECTION_CALLS != 0:
                    raise DANI001CalibrationError("failed synthetic gate opened lexicon")
        # External acquisition has now cleaned its exact three-file directory.
        if acquisition_root is None or os.path.lexists(acquisition_root):
            raise DANI001CalibrationError("external acquisition cleanup failed")
    finally:
        shutil.rmtree(core_directory, ignore_errors=True)
        _REGISTERED_TEMP_ROOTS.discard(core_directory.resolve())

    if controls is None:
        raise DANI001CalibrationError("synthetic controls were not completed")
    if not all(bool(value) for key, value in _isolation_object(
        actual_opened=actual_opened
    ).items() if key.endswith("_pass")):
        raise DANI001CalibrationError("isolation contract failed before output")

    if not all(bool(controls[name]["gate"]) for name in CONTROL_ORDER):
        status = "STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED"
        if actual_opened or actual_public is not None:
            raise DANI001CalibrationError("synthetic failure leaked actual capacity")
    else:
        if not actual_opened or actual_public is None or mandatory_by_view is None:
            raise DANI001CalibrationError("synthetic pass failed to run capacity")
        if not bool(mandatory_by_view["FULL_DEPOSITED_AFFIX"]):
            status = "STOP_UNPOWERED_BEFORE_RELEASED_MAP_SCORE"
        elif not all(bool(mandatory_by_view[name]) for name in (
            "DIRECT_ONLY", "STRICT_NO_FUNCTION", "STRICT_LITERAL", "TOP20_DELETED",
        )):
            status = "STOP_MANDATORY_ROBUSTNESS_CAPACITY_BEFORE_RELEASED_MAP_SCORE"
        else:
            status = "PASS_TARGET_BLIND_CALIBRATION_AND_CAPACITY_IDENTITY_UNOPENED"

    isolation = _isolation_object(actual_opened=actual_opened)
    result = {
        "schema": "dani001-target-blind-calibration-result-v1",
        "experiment": "DANI001",
        "status": status,
        "claim_ceiling": (
            "Target-blind engineering calibration only; no language, lexeme, "
            "plaintext, or translation."
        ),
        "registered_science": freeze["science_spec"],
        "calibration_spec": freeze["calibration_spec"],
        "calibration_freeze_sha256": _sha256(freeze_bytes),
        "synthetic_manifest_sha256": _sha256(manifest_bytes),
        "runtime": runtime,
        "isolation": isolation,
        "input_checks": _input_checks(local_opened=local_opened),
        "synthetic_controls": controls,
        "actual_capacity": actual_public,
        "identity_access": _identity_access(
            actual_opened=actual_opened, actual_guard=actual_guard
        ),
        "decision": status,
    }
    _validate_result_schema(result, actual_opened=actual_opened)
    result_bytes = _canonical_json(result)
    result_sha = _sha256(result_bytes)
    report = _report_bytes(result, result_sha)
    _install_pair(result_bytes, report, actual_guard)
    return result_sha, _sha256(report)


def _source_free_smoke() -> dict[str, object]:
    _enforce_locale_timezone()
    exact_type_rejections = 0
    for operation in (
        lambda: _result_uint(True, "fabricated integer"),
        lambda: _result_uint(1.0, "fabricated integer"),
        lambda: _result_bool(1, "fabricated boolean"),
        lambda: _result_bool(1.0, "fabricated boolean"),
    ):
        try:
            operation()
        except DANI001CalibrationError:
            exact_type_rejections += 1
    if exact_type_rejections != 4:
        raise DANI001CalibrationError("exact result-type smoke failed")

    fake_runtime_without_digest: dict[str, object] = {
        "python": "3.12.3", "implementation": "CPython",
        "machine": "x86_64", "system": "Linux", "byteorder": "little",
        "binary64": "IEEE754_ROUND_TO_NEAREST", "numpy": "1.26.4",
        "locale": "C", "timezone": "UTC", "workers": [1, 32],
        "openmp_library_name": "libgomp.so.1",
        "openmp_library_sha256": "0" * 64,
    }
    fake_freeze_runtime = dict(fake_runtime_without_digest)
    fake_freeze_runtime["runtime_image_sha256"] = _sha256(
        _canonical_json(fake_runtime_without_digest)
    )
    fake_path_for = lambda relative: {
        "path": relative, "sha256": "0" * 64, "size": 0,
    }
    fake_freeze: dict[str, object] = {
        "schema": "dani001-target-blind-calibration-freeze-v1",
        "registered_commit": REGISTERED_COMMIT,
        "science_spec": fake_path_for(SCIENCE_SPEC_REL),
        "calibration_spec": fake_path_for(CALIBRATION_SPEC_REL),
        "local_inputs": [fake_path_for(value) for value in LOCAL_INPUT_RELS],
        "external_inputs": [dict(value) for value in EXTERNAL_BINDINGS],
        "code": [fake_path_for(value) for value in CODE_RELS],
        "synthetic_manifest": fake_path_for(MANIFEST_REL),
        "runtime": fake_freeze_runtime,
        "core_build": {
            "compiler_path": FROZEN_CXX,
            "compiler_sha256": FROZEN_CXX_SHA256,
            "compiler_version_stdout_hex": "00",
            "argv": list(COMPILE_ARGV),
            "shared_library_sha256": "0" * 64,
            "abi_version": 1,
            "runtime_image_sha256": fake_freeze_runtime[
                "runtime_image_sha256"
            ],
        },
        "read_allowlist": [
            SCIENCE_SPEC_REL, CALIBRATION_SPEC_REL, FREEZE_REL, MANIFEST_REL,
            PANEL_REL, GENERATOR_REL, CORE_PY_REL, CORE_H_REL, CORE_CPP_REL,
            RUNNER_REL, *LOCAL_INPUT_RELS,
        ],
        "network_allowlist": [value["url"] for value in EXTERNAL_BINDINGS],
        "temporary_allowlist": list(TEMPORARY_ALLOWLIST),
        "producer_outputs_absent": list(OUTPUT_RELS),
        "validator_outputs_absent": [VALIDATION_JSON_REL, VALIDATION_MD_REL],
        "producer_write_allowlist": list(OUTPUT_RELS),
        "validator_write_allowlist": [VALIDATION_JSON_REL, VALIDATION_MD_REL],
        "static_audit": {
            "status": "GO",
            "review_id": "DANI001_CALIBRATION_FREEZE_STATIC_AUDIT_V1",
            "auditor_source_sha256": "0" * 64,
        },
    }
    fake_freeze_bytes = _canonical_json(fake_freeze)
    if _decode_canonical_freeze(fake_freeze_bytes) != fake_freeze:
        raise DANI001CalibrationError("canonical freeze smoke failed")
    freeze_type_rejections = 0
    for path, replacement in (
        (("runtime", "workers", 0), True),
        (("core_build", "abi_version"), True),
        (("local_inputs", 0, "size"), False),
    ):
        malformed = _json_no_duplicates(fake_freeze_bytes)
        cursor = malformed
        for member in path[:-1]:
            cursor = cursor[member]  # type: ignore[index]
        cursor[path[-1]] = replacement  # type: ignore[index]
        try:
            _validate_freeze_schema(malformed)
        except DANI001CalibrationError:
            freeze_type_rejections += 1
    try:
        _decode_canonical_freeze(fake_freeze_bytes[:-1])
    except DANI001CalibrationError:
        freeze_type_rejections += 1
    if freeze_type_rejections != 4:
        raise DANI001CalibrationError("exact freeze-type/canonical smoke failed")

    with tempfile.TemporaryDirectory(prefix="dani001-install-smoke-") as temp_name:
        temporary = Path(temp_name)
        single = temporary / "single.json"
        _write_no_clobber_one(single, b"safe\n")
        if _file_proof(single).sha256 != _sha256(b"safe\n"):
            raise DANI001CalibrationError("single-install proof smoke failed")
        single.unlink()

        staged = temporary / "staged"
        staged.write_bytes(b"staged\n")
        staged_proof = _file_proof(staged)
        destination = temporary / "destination"
        os.link(staged, destination)
        _prove_result_staged_link(staged, destination, staged_proof)
        _rollback_result_staged_link(staged, destination, staged_proof)
        if os.path.lexists(destination):
            raise DANI001CalibrationError("exact rollback smoke failed")

        os.link(staged, destination)
        destination.unlink()
        destination.write_bytes(b"foreign\n")
        foreign_rejected = False
        try:
            _rollback_result_staged_link(staged, destination, staged_proof)
        except DANI001CalibrationError:
            foreign_rejected = True
        if not foreign_rejected or destination.read_bytes() != b"foreign\n":
            raise DANI001CalibrationError("foreign rollback safety smoke failed")
    unopened_identity = _identity_access(
        actual_opened=False, actual_guard=None
    )
    if unopened_identity != {
        "rank0_requests": 0,
        "rank0_maps_evaluated": 0,
        "rank0_match_calls": 0,
        "rank0_values_stored": 0,
        "rank0_values_inferred": 0,
        "actual_rank_interval_start": None,
        "actual_rank_interval_stop": None,
        "actual_primary_logical_view_surfaces": 0,
        "actual_evidence_logical_view_surfaces": 0,
        "actual_logical_view_surfaces": 0,
        "actual_primary_logical_map_view_evaluations": 0,
        "actual_evidence_logical_map_view_evaluations": 0,
        "actual_logical_map_view_evaluations": 0,
    }:
        raise DANI001CalibrationError("unopened identity schema smoke failed")
    fake_controls: dict[str, object] = {}
    for name in CONTROL_ORDER:
        member: dict[str, object] = {
            "total": 0, "passed": 0, "failed": 0,
            "aggregate_sha256": "0" * 64, "gate": False,
        }
        if name == "plants":
            member.update(successful=0, threshold=95)
        elif name == "nulls":
            member.update(false_passes=0, threshold=1)
        fake_controls[name] = member
    fake_runtime = {
        "python": "3.12.3", "implementation": "CPython",
        "machine": "x86_64", "system": "Linux", "byteorder": "little",
        "binary64": "IEEE754_ROUND_TO_NEAREST", "numpy": "1.26.4",
        "locale": "C", "timezone": "UTC", "workers": [1, 32],
        "openmp_library_name": "libgomp.so.1",
        "openmp_library_sha256": "0" * 64,
        "runtime_image_sha256": "0" * 64,
    }
    fake_isolation = {
        name: True if name.endswith("_pass") else 0
        for name in (
            "read_allowlist_pass", "write_allowlist_pass",
            "network_allowlist_pass", "temporary_allowlist_pass",
            "output_destinations_absent_pass", "acquisition_inventory_pass",
            "synthetic_gate_actual_access_pass", "forbidden_read_count",
            "forbidden_write_count", "forbidden_network_count",
            "temporary_inventory_violation_count", "output_collision_count",
            "pre_synthetic_actual_local_read_count",
            "pre_synthetic_lexicon_projection_call_count",
            "post_synthetic_lexicon_projection_call_count",
        )
    }
    fake_checks = {
        name: (None if name == "local_inputs_pass" else True)
        for name in (
            "registered_commit_pass", "science_spec_pass",
            "calibration_spec_pass", "calibration_freeze_pass",
            "synthetic_manifest_pass", "code_hashes_pass", "runtime_pass",
            "compiler_binary_pass", "core_build_pass",
            "external_pipeline_body_pass", "external_lexicon_body_pass",
            "stable_projection_pass", "local_inputs_pass",
        )
    }
    fake_path = {"path": "fake", "sha256": "0" * 64, "size": 0}
    fake_result = {
        "schema": "dani001-target-blind-calibration-result-v1",
        "experiment": "DANI001",
        "status": "STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED",
        "claim_ceiling": (
            "Target-blind engineering calibration only; no language, lexeme, "
            "plaintext, or translation."
        ),
        "registered_science": dict(fake_path),
        "calibration_spec": dict(fake_path),
        "calibration_freeze_sha256": "0" * 64,
        "synthetic_manifest_sha256": "0" * 64,
        "runtime": fake_runtime,
        "isolation": fake_isolation,
        "input_checks": fake_checks,
        "synthetic_controls": fake_controls,
        "actual_capacity": None,
        "identity_access": unopened_identity,
        "decision": "STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED",
    }
    _validate_result_schema(fake_result, actual_opened=False)
    malformed_result = dict(fake_result)
    malformed_identity = dict(unopened_identity)
    malformed_identity["rank0_requests"] = False
    malformed_result["identity_access"] = malformed_identity
    try:
        _validate_result_schema(malformed_result, actual_opened=False)
    except DANI001CalibrationError:
        exact_type_rejections += 1
    if exact_type_rejections != 5:
        raise DANI001CalibrationError("recursive exact result-type smoke failed")
    accepted = _accepted_preimages_literal((_encode_codes((1, 2)),))
    if accepted != _literal_candidates((_encode_codes((1, 2)),)):
        raise DANI001CalibrationError("literal matcher smoke failed")
    if not all(
        _literal_match_decision(
            value, (_encode_codes((1, 2)),), deposited=True
        )
        for value in accepted
    ):
        raise DANI001CalibrationError("literal positive smoke failed")
    template = (-1, -2)
    constraints = _constraints_for_template(template, accepted, 4)
    if not constraints or any(len(value.required) != 4 for value in constraints):
        raise DANI001CalibrationError("constraint smoke failed")
    fake = PrivateSurface(
        edition="ZL3b",
        panel="MANUAL_GROUP",
        tokens=(
            PrivateToken(1, "kd", (-1, -2), True),
            PrivateToken(2, "kdb", (-1, -2), False),
        ),
        template_sha256="0" * 64,
    )
    strict = _type_bins(fake, strict_only=True, delete_top20=False)
    if len(strict) != 1 or strict[0].token_count != 1:
        raise DANI001CalibrationError("private-bin smoke failed")
    direct = (_encode_codes((1, 2)),)
    definitions = {
        view_name: (
            direct,
            direct if view_name == "DIRECT_ONLY" else accepted,
            view_name == "STRICT_LITERAL",
            view_name == "TOP20_DELETED",
        )
        for view_name in VIEW_ORDER
    }
    expanded_function = _decision_function_digest(
        (fake,), definitions, n_core=4, literal=False
    )
    literal_function = _decision_function_digest(
        (fake,), definitions, n_core=4, literal=True
    )
    if expanded_function != literal_function:
        raise DANI001CalibrationError("decision-function evidence smoke failed")
    evidence_id = "AFFIX_FAKE_EQUIVALENCE"
    evidence_aggregate = _aggregate_assertions(
        "affix_equivalence",
        (evidence_id,),
        {evidence_id: True},
        evidence={evidence_id: expanded_function},
    )
    if not HEX64.fullmatch(str(evidence_aggregate["aggregate_sha256"])):
        raise DANI001CalibrationError("evidence aggregate smoke failed")
    affix_fixture = []
    unreachable_fixture = []
    for edition in EDITION_ORDER:
        for panel in PANEL_ORDER:
            for weighting in WEIGHT_ORDER:
                dtype = "<f8" if weighting == "FOLIO" else "<u4"
                affix_fixture.append({
                    "edition": edition, "panel": panel,
                    "weighting": weighting, "dtype": dtype,
                    "literal_decision_function_sha256": expanded_function,
                    "literal_raw_sha256": expanded_function,
                    "expanded_decision_function_sha256": expanded_function,
                    "expanded_raw_sha256": expanded_function,
                })
                unreachable_fixture.append({
                    "edition": edition, "panel": panel,
                    "weighting": weighting, "dtype": dtype,
                    "full_raw_sha256": expanded_function,
                    "without_raw_sha256": expanded_function,
                    "restored_raw_sha256": expanded_function,
                })
    implementation_digest = _actual_implementation_invariant_digest(
        affix_fixture, unreachable_fixture
    )
    if not HEX64.fullmatch(implementation_digest):
        raise DANI001CalibrationError(
            "implementation-invariant digest smoke failed"
        )
    duplicate_rejected = False
    try:
        _json_no_duplicates(b'{"x":1,"x":2}\n')
    except DANI001CalibrationError:
        duplicate_rejected = True
    if not duplicate_rejected:
        raise DANI001CalibrationError("duplicate JSON smoke failed")
    local_bindings = [
        {
            "path": relative,
            "sha256": LOCAL_INPUT_SHA256[relative],
            "size": LOCAL_INPUT_SIZE[relative],
        }
        for relative in LOCAL_INPUT_RELS
    ]
    _assert_registered_local_bindings(local_bindings)
    drifted_bindings = [dict(value) for value in local_bindings]
    drifted_bindings[0]["size"] = int(drifted_bindings[0]["size"]) + 1
    local_drift_rejected = False
    try:
        _assert_registered_local_bindings(drifted_bindings)
    except DANI001CalibrationError:
        local_drift_rejected = True
    if not local_drift_rejected:
        raise DANI001CalibrationError("local-binding drift smoke failed")
    fake_world = types.SimpleNamespace(lexicon=(
        {
            "key": "k",
            "entries": [{"domain": "general", "source_present": True}],
        },
        {
            "key": "d",
            "entries": [{"domain": "general", "source_present": False}],
        },
    ))
    source_present = _synthetic_view_direct_codes(fake_world, "SOURCE_PRESENT")
    if source_present != (_encode_codes((NIBBLE_CODE["k"],)),):
        raise DANI001CalibrationError("source-present projection smoke failed")
    if TEMPORARY_ALLOWLIST != (
        "EXTERNAL_ACQUISITION_EXACT_THREE_FILES",
        "CORE_BUILD_CPP_HEADER_LIBRARY",
        "OUTPUT_STAGING_TWO_FILES",
    ):
        raise DANI001CalibrationError("temporary allowlist smoke failed")
    if (
        len(FROZEN_CXX_VERSION_STDOUT)
        - len(FROZEN_CXX_VERSION_STDOUT.rstrip(b"\n")) != 2
        or not FROZEN_CXX_VERSION_STDOUT.endswith(b"PURPOSE.\n\n")
        or b"\r" in FROZEN_CXX_VERSION_STDOUT
    ):
        raise DANI001CalibrationError(
            "frozen compiler-version terminal-LF smoke failed"
        )
    return {
        "status": "PASS_SOURCE_FREE_RUNNER_SMOKE",
        "accepted_preimages": len(accepted),
        "constraints": len(constraints),
        "decision_function_sha256": expanded_function,
        "implementation_invariant_sha256": implementation_digest,
        "registered_worlds_constructed": 0,
        "network_requests": 0,
        "actual_source_opens": 0,
        "actual_rank0_evaluations": 0,
        "exact_type_rejections": exact_type_rejections,
        "freeze_type_rejections": freeze_type_rejections,
        "race_safe_install_checks": 3,
        "locale_timezone_live": True,
        "local_binding_checks": len(local_bindings),
        "source_present_codes": len(source_present),
        "compiler_version_terminal_lf": 2,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze or run the DANI001 target-blind calibration."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--run-registered-calibration",
        action="store_true",
        help="Run the one frozen registered calibration",
    )
    modes.add_argument(
        "--create-freeze",
        action="store_true",
        help="Hash-only/no-score creation of DANI001_CALIBRATION_FREEZE.json",
    )
    modes.add_argument(
        "--source-free-smoke",
        action="store_true",
        help="Run only tiny fake scalar/parser fixtures",
    )
    parser.add_argument("--freeze-sha256")
    parser.add_argument("--static-auditor-sha256")
    values = parser.parse_args(argv)
    if values.run_registered_calibration:
        if not values.freeze_sha256 or values.static_auditor_sha256:
            parser.error("registered run requires only --freeze-sha256")
    elif values.create_freeze:
        if not values.static_auditor_sha256 or values.freeze_sha256:
            parser.error("freeze creation requires only --static-auditor-sha256")
    elif values.freeze_sha256 or values.static_auditor_sha256:
        parser.error("source-free smoke takes no hash argument")
    return values


def main(argv: Sequence[str] | None = None) -> int:
    values = parse_args(argv)
    if values.source_free_smoke:
        print(json.dumps(_source_free_smoke(), sort_keys=True))
        return 0
    if values.create_freeze:
        digest = _create_freeze(
            static_auditor_sha256=values.static_auditor_sha256
        )
        print(f"DANI001_CALIBRATION_FREEZE.json sha256={digest}")
        return 0
    result_sha, report_sha = _run_registered(values.freeze_sha256)
    print(
        "dani001_target_blind_calibration "
        f"result_sha256={result_sha} report_sha256={report_sha}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
