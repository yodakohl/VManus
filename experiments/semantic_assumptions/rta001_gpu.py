#!/usr/bin/env python3
"""Strict ctypes adapter for the proposal-only RTA001 CUDA kernel."""

from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "rta001_cuda_proposer.cu"
FROZEN_NVCC = Path("/usr/bin/nvcc")
FLAGS = ("-std=c++17", "-O3", "--shared", "-Xcompiler", "-fPIC")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class _Info(ctypes.Structure):
    _fields_ = [
        ("device_count", ctypes.c_int),
        ("device", ctypes.c_int),
        ("major", ctypes.c_int),
        ("minor", ctypes.c_int),
        ("total_memory", ctypes.c_uint64),
    ]


@dataclass(frozen=True)
class CudaInfo:
    device_count: int
    device: int
    compute_capability: str
    total_memory: int
    source_sha256: str
    library_sha256: str


class CudaProposer:
    def __init__(self, library: Path):
        self.library_path = library.resolve()
        self._lib = ctypes.CDLL(str(self.library_path))
        self._lib.rta001_cuda_info.argtypes = [ctypes.POINTER(_Info)]
        self._lib.rta001_cuda_info.restype = ctypes.c_int
        self._lib.rta001_assign_many.argtypes = [
            ctypes.POINTER(ctypes.c_int16),
            ctypes.POINTER(ctypes.c_int16),
            ctypes.POINTER(ctypes.c_int16),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int32),
            ctypes.POINTER(ctypes.c_uint64),
        ]
        self._lib.rta001_assign_many.restype = ctypes.c_int

    def info(self) -> CudaInfo:
        raw = _Info()
        rc = self._lib.rta001_cuda_info(ctypes.byref(raw))
        if rc:
            raise RuntimeError(f"CUDA info failed: {rc}")
        return CudaInfo(
            raw.device_count,
            raw.device,
            f"{raw.major}.{raw.minor}",
            int(raw.total_memory),
            sha256(SOURCE),
            sha256(self.library_path),
        )

    def assign_many(
        self, vectors: np.ndarray, medoids: np.ndarray, weights: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        vectors = np.ascontiguousarray(vectors, dtype="<i2")
        medoids = np.ascontiguousarray(medoids, dtype="<i2")
        weights = np.ascontiguousarray(weights, dtype="<i2")
        if vectors.ndim != 2 or medoids.ndim != 3 or weights.ndim != 1:
            raise ValueError("expected vectors[rows,d], medoids[restarts,k,d], weights[d]")
        restarts, k, dimensions = medoids.shape
        rows, vector_dimensions = vectors.shape
        if dimensions != vector_dimensions or weights.shape != (dimensions,):
            raise ValueError("dimension mismatch")
        if np.any(weights < 0):
            raise ValueError("negative weights")
        assignments = np.empty((restarts, rows), dtype="<i4")
        costs = np.empty((restarts, rows), dtype="<u8")
        rc = self._lib.rta001_assign_many(
            vectors.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
            medoids.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
            weights.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
            rows,
            dimensions,
            restarts,
            k,
            assignments.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            costs.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
        )
        if rc:
            raise RuntimeError(f"CUDA assignment failed: {rc}")
        return assignments, costs


def build_cuda_library(destination: Path) -> dict[str, object]:
    if not FROZEN_NVCC.is_file():
        raise RuntimeError("/usr/bin/nvcc is unavailable")
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rta001-cuda-") as temporary:
        tmp = Path(temporary) / "librta001_cuda.so"
        env = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "TZ": "UTC"}
        command = [str(FROZEN_NVCC), *FLAGS, str(SOURCE), "-o", str(tmp)]
        completed = subprocess.run(command, env=env, check=False, capture_output=True)
        if completed.returncode:
            raise RuntimeError(completed.stderr.decode("utf-8", "replace"))
        os.link(tmp, destination)
    return {
        "compiler": str(FROZEN_NVCC),
        "compiler_sha256": sha256(FROZEN_NVCC),
        "flags": list(FLAGS),
        "source_sha256": sha256(SOURCE),
        "library_sha256": sha256(destination),
        "library_size": destination.stat().st_size,
    }
