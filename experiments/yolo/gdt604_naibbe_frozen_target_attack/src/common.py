#!/usr/bin/env python3
"""Portable path, hashing, and TSV helpers for the GDT604 bundle."""
from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_repository_root() -> Path:
    """Find VManus without embedding a machine-specific path.

    A published experiment finds the root from its own parents.  A detached
    copy of this bundle can also be run while the current directory is inside
    VManus.  Both markers are required so an unrelated Git checkout is never
    selected accidentally.
    """
    starts = [Path(__file__).resolve().parent, Path.cwd().resolve()]
    visited: set[Path] = set()
    for start in starts:
        for candidate in (start, *start.parents):
            if candidate in visited:
                continue
            visited.add(candidate)
            if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
                return candidate
    raise RuntimeError(
        "VManus root not found: run inside a checkout containing AGENTS.md and .git"
    )


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=fields, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()

