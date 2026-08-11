#!/usr/bin/env python3
"""Minimal ctypes binding for the anonymous DANI001 integer core.

This module does not parse manuscript sources, external files, lexicons, or
identities.  Callers supply already-compiled partial-bijection constraints and
nonnegative vector weights.  Returned bytes are vector-major raw ``<u4``.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
CPP_SOURCE = HERE / "dani001_core.cpp"
CPP_HEADER = HERE / "dani001_core.h"
FROZEN_CXX = Path("/usr/bin/x86_64-linux-gnu-g++-12")
FROZEN_CXX_SHA256 = "1cfb9704049655d08accca3b1aeefd6fc749ef2cfb992ec95a81f39091d7b3ce"
FROZEN_CXX_VERSION_LINE = (
    "x86_64-linux-gnu-g++-12 (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0"
)
FROZEN_COMPILE_ENV = {
    "HOME": "/nonexistent",
    "LANG": "C",
    "LC_ALL": "C",
    "PATH": "/usr/bin:/bin",
    "SOURCE_DATE_EPOCH": "0",
    "TZ": "UTC",
}

STATUS = {
    0: "OK",
    1: "INVALID_ARGUMENT",
    2: "INVALID_CORE_SIZE",
    3: "INVALID_RANK_RANGE",
    4: "INVALID_CONSTRAINT",
    5: "WEIGHT_OVERFLOW",
    6: "INVALID_ENCODING",
    7: "OVERLENGTH_PREIMAGE",
    8: "BUFFER_TOO_SMALL",
    9: "OPENMP_UNAVAILABLE",
    10: "UNSUPPORTED_SCALAR_SIZE",
}

DIRECT = 0
DEPOSITED_AFFIX = 1


class Dani001CoreError(RuntimeError):
    """Raised when the compiled core rejects an input."""


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compile_shared(
    output_path: str | os.PathLike[str],
    cxx: str | os.PathLike[str] = FROZEN_CXX,
) -> Path:
    """Build with the frozen compiler into a fresh external no-clobber path."""
    requested = Path(output_path)
    if not requested.name or requested.name in {".", ".."}:
        raise Dani001CoreError("invalid shared-library output name")
    try:
        parent = requested.parent.resolve(strict=True)
    except OSError as error:
        raise Dani001CoreError("shared-library output parent does not exist") from error
    output = parent / requested.name
    try:
        parent.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise Dani001CoreError("shared-library output must be outside repository")
    if os.path.lexists(output):
        raise Dani001CoreError("refusing to clobber shared-library output")

    try:
        compiler = Path(cxx).resolve(strict=True)
    except OSError as error:
        raise Dani001CoreError("frozen compiler is unavailable") from error
    if compiler != FROZEN_CXX or _sha256_path(compiler) != FROZEN_CXX_SHA256:
        raise Dani001CoreError("frozen compiler identity mismatch")
    version = subprocess.run(
        [str(compiler), "--version"],
        check=True,
        capture_output=True,
        text=True,
        env=FROZEN_COMPILE_ENV,
        cwd=HERE,
    ).stdout.splitlines()
    if not version or version[0] != FROZEN_CXX_VERSION_LINE:
        raise Dani001CoreError("frozen compiler version mismatch")

    with tempfile.TemporaryDirectory(prefix="dani001-core-build-", dir=parent) as directory:
        build_directory = Path(directory)
        staged_source = build_directory / CPP_SOURCE.name
        staged_header = build_directory / CPP_HEADER.name
        staged = build_directory / "libdani001_core.so"
        for source, destination in (
            (CPP_SOURCE, staged_source),
            (CPP_HEADER, staged_header),
        ):
            descriptor = os.open(
                destination,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
            try:
                with os.fdopen(descriptor, "wb", closefd=False) as handle:
                    handle.write(source.read_bytes())
                    handle.flush()
                    os.fsync(handle.fileno())
            finally:
                os.close(descriptor)
        subprocess.run(
            [
                str(compiler),
                "-std=c++20",
                "-O3",
                "-DNDEBUG",
                "-fPIC",
                "-shared",
                "-fopenmp",
                "-fno-fast-math",
                "-ffp-contract=off",
                staged_source.name,
                "-o",
                staged.name,
            ],
            check=True,
            env=FROZEN_COMPILE_ENV,
            cwd=build_directory,
        )
        with staged.open("rb") as handle:
            os.fsync(handle.fileno())
        try:
            os.link(staged, output)
        except FileExistsError as error:
            raise Dani001CoreError("refusing raced shared-library clobber") from error
        directory_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    return output


def _checked_int(value: object, *, bits: int, label: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must contain exact Python integers")
    upper = (1 << bits) - 1
    if value < 0 or value > upper:
        raise ValueError(f"{label} value outside uint{bits}")
    return value


def _checked_values(values: Iterable[int], *, bits: int, label: str) -> tuple[int, ...]:
    try:
        materialized = tuple(values)
    except TypeError as error:
        raise TypeError(f"{label} must be an integer iterable") from error
    return tuple(
        _checked_int(value, bits=bits, label=label) for value in materialized
    )


def _canonical_u64_values(values: Iterable[int], *, label: str) -> tuple[int, ...]:
    return tuple(sorted(set(_checked_values(values, bits=64, label=label))))


def _checked_mode(mode: object) -> int:
    checked = _checked_int(mode, bits=32, label="match mode")
    if checked not in {DIRECT, DEPOSITED_AFFIX}:
        raise ValueError("match mode must be DIRECT or DEPOSITED_AFFIX")
    return checked


def _checked_core_size(n_core: object) -> int:
    checked = _checked_int(n_core, bits=32, label="n_core")
    if not 1 <= checked <= 10:
        raise ValueError("n_core must be in [1, 10]")
    return checked


def _checked_count(value: object, *, label: str, positive: bool = False) -> int:
    checked = _checked_int(value, bits=32, label=label)
    if positive and checked == 0:
        raise ValueError(f"{label} must be positive")
    return checked


def _u16(values: Iterable[int], *, label: str = "uint16 values") -> ctypes.Array[ctypes.c_uint16]:
    checked = _checked_values(values, bits=16, label=label)
    return (ctypes.c_uint16 * len(checked))(*checked)


def _u8(values: Iterable[int], *, label: str = "uint8 values") -> ctypes.Array[ctypes.c_uint8]:
    checked = _checked_values(values, bits=8, label=label)
    return (ctypes.c_uint8 * len(checked))(*checked)


def _u32(values: Iterable[int], *, label: str = "uint32 values") -> ctypes.Array[ctypes.c_uint32]:
    checked = _checked_values(values, bits=32, label=label)
    return (ctypes.c_uint32 * len(checked))(*checked)


def _u64(values: Iterable[int], *, label: str = "uint64 values") -> ctypes.Array[ctypes.c_uint64]:
    checked = _checked_values(values, bits=64, label=label)
    return (ctypes.c_uint64 * len(checked))(*checked)


class Dani001Core:
    """Loaded C ABI with no source/data acquisition behavior."""

    def __init__(self, library_path: str | os.PathLike[str]) -> None:
        if sys.byteorder != "little" or ctypes.sizeof(ctypes.c_uint32) != 4:
            raise Dani001CoreError("DANI001 requires little-endian 32-bit uint32")
        self._lib = ctypes.CDLL(str(Path(library_path).resolve()))
        self._bind()
        if self._lib.dani001_abi_version() != 1:
            raise Dani001CoreError("unsupported DANI001 core ABI")

    def _bind(self) -> None:
        lib = self._lib
        u8p = ctypes.POINTER(ctypes.c_uint8)
        u16p = ctypes.POINTER(ctypes.c_uint16)
        u32p = ctypes.POINTER(ctypes.c_uint32)
        u64p = ctypes.POINTER(ctypes.c_uint64)

        lib.dani001_abi_version.argtypes = []
        lib.dani001_abi_version.restype = ctypes.c_uint32
        lib.dani001_has_openmp.argtypes = []
        lib.dani001_has_openmp.restype = ctypes.c_uint32
        lib.dani001_factorial.argtypes = [ctypes.c_uint32]
        lib.dani001_factorial.restype = ctypes.c_uint64
        lib.dani001_reset_traversal_audit.argtypes = []
        lib.dani001_reset_traversal_audit.restype = None
        lib.dani001_get_traversal_audit.argtypes = [u64p] * 6
        lib.dani001_get_traversal_audit.restype = ctypes.c_int
        lib.dani001_rank_lex.argtypes = [ctypes.c_uint32, u8p, u32p]
        lib.dani001_rank_lex.restype = ctypes.c_int
        lib.dani001_unrank_lex.argtypes = [ctypes.c_uint32, ctypes.c_uint32, u8p]
        lib.dani001_unrank_lex.restype = ctypes.c_int
        enumeration = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            u16p,
            u8p,
            ctypes.c_uint32,
            u32p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        lib.dani001_enumerate_constraints.argtypes = enumeration + [ctypes.c_uint32, u32p]
        lib.dani001_enumerate_constraints.restype = ctypes.c_int
        lib.dani001_enumerate_constraints_scalar.argtypes = enumeration + [u32p]
        lib.dani001_enumerate_constraints_scalar.restype = ctypes.c_int
        lib.dani001_encode_codes.argtypes = [u8p, ctypes.c_uint32, u64p]
        lib.dani001_encode_codes.restype = ctypes.c_int
        lib.dani001_decode_codes.argtypes = [ctypes.c_uint64, u8p, u32p]
        lib.dani001_decode_codes.restype = ctypes.c_int
        lib.dani001_direct_match.argtypes = [
            ctypes.c_uint64,
            u64p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            u32p,
        ]
        lib.dani001_direct_match.restype = ctypes.c_int
        lib.dani001_build_preimages.argtypes = [
            u64p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            u64p,
            ctypes.c_uint32,
            u32p,
        ]
        lib.dani001_build_preimages.restype = ctypes.c_int
        lib.dani001_preimage_match.argtypes = [
            ctypes.c_uint64,
            u64p,
            ctypes.c_uint32,
            u32p,
        ]
        lib.dani001_preimage_match.restype = ctypes.c_int
        lib.dani001_check_preimage_equivalence.argtypes = [
            u64p,
            ctypes.c_uint32,
            u64p,
            ctypes.c_uint32,
            u64p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            u32p,
        ]
        lib.dani001_check_preimage_equivalence.restype = ctypes.c_int

    @staticmethod
    def _check(status: int) -> None:
        if status != 0:
            raise Dani001CoreError(f"DANI001 core: {STATUS.get(status, f'UNKNOWN_{status}')}")

    @property
    def has_openmp(self) -> bool:
        return bool(self._lib.dani001_has_openmp())

    def factorial(self, n_core: int) -> int:
        checked_n_core = _checked_core_size(n_core)
        value = int(self._lib.dani001_factorial(checked_n_core))
        if not value:
            raise Dani001CoreError("DANI001 core: INVALID_CORE_SIZE")
        return value

    def reset_traversal_audit(self) -> None:
        """Reset process-local optimized-traversal counters.

        The caller must serialize this operation with enumeration calls.
        """

        self._lib.dani001_reset_traversal_audit()

    def traversal_audit(self) -> dict[str, int]:
        """Read live counters emitted by optimized compiler traversals."""

        values = [ctypes.c_uint64() for _ in range(6)]
        self._check(
            self._lib.dani001_get_traversal_audit(
                *(ctypes.byref(value) for value in values)
            )
        )
        names = (
            "optimized_calls",
            "constraint_traversals",
            "branches_considered",
            "branches_pruned",
            "completed_assignments",
            "completed_rank_zero",
        )
        return {
            name: int(value.value)
            for name, value in zip(names, values, strict=True)
        }

    def rank(self, permutation: Sequence[int]) -> int:
        checked_permutation = _checked_values(
            permutation, bits=8, label="permutation"
        )
        n_core = _checked_core_size(len(checked_permutation))
        if sorted(checked_permutation) != list(range(n_core)):
            raise ValueError("permutation must be a bijection over range(n_core)")
        packed = _u8(checked_permutation, label="permutation")
        result = ctypes.c_uint32()
        self._check(self._lib.dani001_rank_lex(n_core, packed, ctypes.byref(result)))
        return int(result.value)

    def unrank(self, n_core: int, rank: int) -> tuple[int, ...]:
        checked_n_core = _checked_core_size(n_core)
        checked_rank = _checked_int(rank, bits=32, label="rank")
        if checked_rank >= self.factorial(checked_n_core):
            raise ValueError("rank must be below n_core factorial")
        result = (ctypes.c_uint8 * checked_n_core)()
        self._check(
            self._lib.dani001_unrank_lex(checked_n_core, checked_rank, result)
        )
        return tuple(int(value) for value in result)

    def enumerate_raw(
        self,
        *,
        n_core: int,
        input_masks: Sequence[int],
        required_outputs: Sequence[int],
        n_vectors: int,
        weights: Sequence[int],
        rank_begin: int,
        rank_end: int,
        threads: int = 1,
        scalar: bool = False,
    ) -> bytes:
        """Return vector-major raw ``<u4`` numerators for a half-open rank mask."""
        checked_n_core = _checked_core_size(n_core)
        checked_n_vectors = _checked_count(
            n_vectors, label="n_vectors", positive=True
        )
        checked_rank_begin = _checked_int(rank_begin, bits=32, label="rank_begin")
        checked_rank_end = _checked_int(rank_end, bits=32, label="rank_end")
        checked_threads = _checked_count(threads, label="threads", positive=True)
        if type(scalar) is not bool:
            raise TypeError("scalar must be an exact Python bool")
        factorial = self.factorial(checked_n_core)
        if checked_rank_begin > checked_rank_end:
            raise ValueError("rank_end must be at least rank_begin")
        if checked_rank_end > factorial:
            raise ValueError("rank_end must be at most n_core factorial")

        checked_masks = _checked_values(
            input_masks, bits=16, label="input_masks"
        )
        checked_required = _checked_values(
            required_outputs, bits=8, label="required_outputs"
        )
        checked_weights = _checked_values(weights, bits=32, label="weights")
        n_constraints = _checked_count(
            len(checked_masks), label="n_constraints"
        )
        if len(checked_required) != n_constraints * checked_n_core:
            raise ValueError("required_outputs length must be constraints * n_core")
        if len(checked_weights) != n_constraints * checked_n_vectors:
            raise ValueError("weights length must be constraints * n_vectors")

        valid_mask = (1 << checked_n_core) - 1
        seen_constraints: set[tuple[int, tuple[int, ...]]] = set()
        vector_sums = [0] * checked_n_vectors
        for constraint, mask in enumerate(checked_masks):
            if mask & ~valid_mask:
                raise ValueError("input mask sets a bit outside n_core")
            row = checked_required[
                constraint * checked_n_core:(constraint + 1) * checked_n_core
            ]
            assigned_outputs: list[int] = []
            for input_index, required in enumerate(row):
                assigned = bool(mask & (1 << input_index))
                if not assigned:
                    if required != 255:
                        raise ValueError(
                            "unassigned constraint positions must be exact 0xff"
                        )
                elif required >= checked_n_core:
                    raise ValueError("assigned output must be below n_core")
                else:
                    assigned_outputs.append(required)
            if len(set(assigned_outputs)) != len(assigned_outputs):
                raise ValueError("constraint outputs must be injective")
            identity = (mask, row)
            if identity in seen_constraints:
                raise ValueError(
                    "duplicate compiled constraints must be consolidated"
                )
            seen_constraints.add(identity)
            for vector in range(checked_n_vectors):
                vector_sums[vector] += checked_weights[
                    constraint * checked_n_vectors + vector
                ]
                if vector_sums[vector] > (1 << 32) - 1:
                    raise ValueError("per-vector weight upper bound exceeds uint32")

        masks_array = _u16(checked_masks, label="input_masks")
        required_array = _u8(checked_required, label="required_outputs")
        weights_array = _u32(checked_weights, label="weights")
        count = checked_n_vectors * (checked_rank_end - checked_rank_begin)
        if count > sys.maxsize // ctypes.sizeof(ctypes.c_uint32):
            raise ValueError("requested output is too large for this host")
        output = (ctypes.c_uint32 * count)()
        if scalar:
            if checked_n_core > 6:
                raise ValueError("scalar reference supports n_core at most 6")
            status = self._lib.dani001_enumerate_constraints_scalar(
                checked_n_core,
                n_constraints,
                masks_array,
                required_array,
                checked_n_vectors,
                weights_array,
                checked_rank_begin,
                checked_rank_end,
                output,
            )
        else:
            status = self._lib.dani001_enumerate_constraints(
                checked_n_core,
                n_constraints,
                masks_array,
                required_array,
                checked_n_vectors,
                weights_array,
                checked_rank_begin,
                checked_rank_end,
                checked_threads,
                output,
            )
        self._check(status)
        return bytes(output)

    def encode_codes(self, codes: Sequence[int]) -> int:
        checked_codes = _checked_values(codes, bits=8, label="codes")
        length = _checked_count(len(checked_codes), label="code length")
        if length > 10:
            raise ValueError("code sequence length must be at most ten")
        if any(code == 0 or code > 14 for code in checked_codes):
            raise ValueError("each nibble code must be in [1, 14]")
        packed = _u8(checked_codes, label="codes")
        result = ctypes.c_uint64()
        self._check(self._lib.dani001_encode_codes(packed, length, ctypes.byref(result)))
        return int(result.value)

    def decode_codes(self, encoded: int) -> tuple[int, ...]:
        checked_encoded = _checked_int(encoded, bits=64, label="encoded value")
        codes = (ctypes.c_uint8 * 10)()
        length = ctypes.c_uint32()
        self._check(
            self._lib.dani001_decode_codes(checked_encoded, codes, ctypes.byref(length))
        )
        return tuple(int(codes[index]) for index in range(length.value))

    def direct_match(self, skeleton: int, keys: Iterable[int], mode: int) -> int:
        checked_skeleton = _checked_int(skeleton, bits=64, label="skeleton")
        checked_keys = _canonical_u64_values(keys, label="keys")
        n_keys = _checked_count(len(checked_keys), label="n_keys")
        checked_mode = _checked_mode(mode)
        packed_keys = _u64(checked_keys, label="keys")
        label = ctypes.c_uint32()
        self._check(
            self._lib.dani001_direct_match(
                checked_skeleton,
                packed_keys,
                n_keys,
                checked_mode,
                ctypes.byref(label),
            )
        )
        return int(label.value)

    def build_preimages(self, keys: Iterable[int], mode: int) -> tuple[int, ...]:
        checked_keys = _canonical_u64_values(keys, label="keys")
        n_keys = _checked_count(len(checked_keys), label="n_keys")
        checked_mode = _checked_mode(mode)
        packed_keys = _u64(checked_keys, label="keys")
        count = ctypes.c_uint32()
        self._check(
            self._lib.dani001_build_preimages(
                packed_keys, n_keys, checked_mode, None, 0, ctypes.byref(count)
            )
        )
        output = (ctypes.c_uint64 * count.value)()
        self._check(
            self._lib.dani001_build_preimages(
                packed_keys,
                n_keys,
                checked_mode,
                output,
                count.value,
                ctypes.byref(count),
            )
        )
        return tuple(int(value) for value in output)

    def preimage_match(self, skeleton: int, accepted: Iterable[int]) -> bool:
        checked_skeleton = _checked_int(skeleton, bits=64, label="skeleton")
        checked_accepted = _canonical_u64_values(
            accepted, label="accepted preimages"
        )
        n_preimages = _checked_count(
            len(checked_accepted), label="n_preimages"
        )
        packed = _u64(checked_accepted, label="accepted preimages")
        matched = ctypes.c_uint32()
        self._check(
            self._lib.dani001_preimage_match(
                checked_skeleton, packed, n_preimages, ctypes.byref(matched)
            )
        )
        return bool(matched.value)

    def check_preimage_equivalence(
        self,
        skeletons: Iterable[int],
        keys: Iterable[int],
        accepted: Iterable[int],
        mode: int,
    ) -> int:
        checked_skeletons = _checked_values(
            skeletons, bits=64, label="skeletons"
        )
        checked_keys = _canonical_u64_values(keys, label="keys")
        checked_accepted = _canonical_u64_values(
            accepted, label="accepted preimages"
        )
        n_skeletons = _checked_count(
            len(checked_skeletons), label="n_skeletons"
        )
        n_keys = _checked_count(len(checked_keys), label="n_keys")
        n_preimages = _checked_count(
            len(checked_accepted), label="n_preimages"
        )
        checked_mode = _checked_mode(mode)
        packed_skeletons = _u64(checked_skeletons, label="skeletons")
        packed_keys = _u64(checked_keys, label="keys")
        packed_accepted = _u64(
            checked_accepted, label="accepted preimages"
        )
        mismatches = ctypes.c_uint32()
        self._check(
            self._lib.dani001_check_preimage_equivalence(
                packed_skeletons,
                n_skeletons,
                packed_keys,
                n_keys,
                packed_accepted,
                n_preimages,
                checked_mode,
                ctypes.byref(mismatches),
            )
        )
        return int(mismatches.value)
