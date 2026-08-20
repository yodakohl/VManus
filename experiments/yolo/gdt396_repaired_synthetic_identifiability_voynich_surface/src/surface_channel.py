#!/usr/bin/env python3
"""Truth-preserving GDT396 paired surface channel.

The constrained surface is represented as raw atom indices.  The letters used
to name the 24 official STA families never enter the visible payload.
"""

from __future__ import annotations

import gzip
import hashlib
import hmac
import itertools
import struct
from pathlib import Path
from typing import Iterable


OFFICIAL_STA_FAMILY_NAMES = "ABCDEFGHJKLMNPQRSTUVWXYZ"
ATOM_COUNT = len(OFFICIAL_STA_FAMILY_NAMES)
MAGIC = b"GDT396VS1\0"

if ATOM_COUNT != 24 or len(set(OFFICIAL_STA_FAMILY_NAMES)) != 24:
    raise RuntimeError("official STA family inventory must contain 24 positions")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def salt_commitment(salt: bytes) -> str:
    return hashlib.sha256(b"GDT396-SURFACE-SALT-V1\0" + salt).hexdigest()


def _rank(salt: bytes, world_id: str, label: bytes) -> bytes:
    return hmac.new(salt, b"GDT396-VS1\0" + world_id.encode("ascii") + b"\0" + label, hashlib.sha256).digest()


def make_mapping(world_id: str, native_alphabet: Iterable[str], salt: bytes) -> dict[str, tuple[int, ...]]:
    alphabet = tuple(native_alphabet)
    if not alphabet or len(alphabet) != len(set(alphabet)):
        raise ValueError(f"{world_id}: native alphabet must be nonempty and unique")
    if any(not value or len(value) != 1 for value in alphabet):
        raise ValueError(f"{world_id}: GDT395 native atoms must be single Unicode code points")
    # Uniform width prevents the observation channel itself from revealing
    # which frozen worlds happen to have more than 24 native atoms.
    width = 2
    candidates = list(itertools.product(range(ATOM_COUNT), repeat=width))
    candidates.sort(key=lambda code: (_rank(salt, world_id, bytes(code)), code))
    native = sorted(alphabet, key=lambda value: (_rank(salt, world_id, value.encode("utf-8")), value))
    mapping = {value: tuple(candidates[index]) for index, value in enumerate(native)}
    if len(set(mapping.values())) != len(mapping):
        raise RuntimeError(f"{world_id}: noninjective constrained mapping")
    return mapping


def encode_group(group: str, mapping: dict[str, tuple[int, ...]]) -> bytes:
    try:
        encoded = bytes(atom for native in group for atom in mapping[native])
    except KeyError as exc:
        raise ValueError(f"surface contains atom outside frozen native alphabet: {exc.args[0]!r}") from exc
    if not encoded:
        raise ValueError("empty visible group")
    if any(value >= ATOM_COUNT for value in encoded):
        raise RuntimeError("constrained atom outside 24-position inventory")
    return encoded


def write_atom_stream(path: Path, payloads: list[bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as out:
            out.write(MAGIC)
            out.write(struct.pack(">I", len(payloads)))
            for payload in payloads:
                if len(payload) > 65535:
                    raise ValueError("visible group exceeds binary length bound")
                out.write(struct.pack(">H", len(payload)))
                out.write(payload)


def read_atom_stream(path: Path) -> list[bytes]:
    with gzip.open(path, "rb") as fh:
        if fh.read(len(MAGIC)) != MAGIC:
            raise ValueError(f"{path}: bad constrained-surface magic")
        count_raw = fh.read(4)
        if len(count_raw) != 4:
            raise ValueError(f"{path}: truncated count")
        count = struct.unpack(">I", count_raw)[0]
        rows: list[bytes] = []
        for _ in range(count):
            size_raw = fh.read(2)
            if len(size_raw) != 2:
                raise ValueError(f"{path}: truncated length")
            size = struct.unpack(">H", size_raw)[0]
            payload = fh.read(size)
            if len(payload) != size:
                raise ValueError(f"{path}: truncated payload")
            if not payload or any(value >= ATOM_COUNT for value in payload):
                raise ValueError(f"{path}: invalid constrained atom payload")
            rows.append(payload)
        if fh.read(1):
            raise ValueError(f"{path}: trailing bytes")
    return rows
