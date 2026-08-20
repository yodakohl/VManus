#!/usr/bin/env python3
"""Load one GDT396 blind surface channel without cross-channel linkage."""

from __future__ import annotations

import csv
import gzip
import struct
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
CORPORA = EXP / ".work/corpora"
MAGIC = b"GDT396VS1\0"
BLIND_MANIFEST_FIELDS = (
    "world_id", "corpus_seed", "seed_block", "events",
    "free_observation_relpath", "free_observation_sha256",
    "voynich_metadata_relpath", "voynich_metadata_sha256",
    "voynich_surface_relpath", "voynich_surface_sha256", "mapping_width",
)


def _rows(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _atoms(path: Path) -> list[tuple[int, ...]]:
    with gzip.open(path, "rb") as fh:
        if fh.read(len(MAGIC)) != MAGIC:
            raise ValueError("bad GDT396 atom stream")
        raw = fh.read(4)
        if len(raw) != 4:
            raise ValueError("truncated atom count")
        count = struct.unpack(">I", raw)[0]
        out = []
        for _ in range(count):
            raw = fh.read(2)
            if len(raw) != 2:
                raise ValueError("truncated atom length")
            size = struct.unpack(">H", raw)[0]
            value = fh.read(size)
            if len(value) != size or not value or any(atom >= 24 for atom in value):
                raise ValueError("invalid atom payload")
            out.append(tuple(value))
        if fh.read(1):
            raise ValueError("trailing atom bytes")
    return out


def block_manifest(block: str) -> list[dict]:
    path = CORPORA / f"gdt396_{block}_paired_manifest_v2.tsv"
    if not path.is_file():
        raise FileNotFoundError(f"blind block unavailable: {block}")
    # Never expose oracle paths/hashes, trace digests, or the mapping
    # commitment through the decoder-facing observation API.
    return [{key: row[key] for key in BLIND_MANIFEST_FIELDS} for row in _rows(path)]


def load_seed(block: str, world_id: str, corpus_seed: int, surface_id: str) -> list[dict]:
    matches = [row for row in block_manifest(block) if row["world_id"] == world_id and int(row["corpus_seed"]) == corpus_seed]
    if len(matches) != 1:
        raise ValueError(f"expected one blind corpus for {block}/{world_id}/{corpus_seed}")
    item = matches[0]
    if surface_id == "FREE_SURFACE":
        rows = _rows(CORPORA / item["free_observation_relpath"])
        for row in rows:
            value = row.pop("visible_group")
            row["visible_surface"] = tuple(value)
    elif surface_id == "VOYNICH_SURFACE":
        rows = _rows(CORPORA / item["voynich_metadata_relpath"])
        payloads = _atoms(CORPORA / item["voynich_surface_relpath"])
        if len(rows) != len(payloads):
            raise ValueError("metadata/surface count mismatch")
        for index, (row, value) in enumerate(zip(rows, payloads, strict=True)):
            if row.pop("surface_channel") != "VOYNICH_SURFACE" or int(row.pop("surface_payload_index")) != index:
                raise ValueError("surface metadata order mismatch")
            row["visible_surface"] = value
    else:
        raise ValueError(surface_id)
    record_counts: dict[str, int] = {}
    for global_rank, row in enumerate(rows):
        record = row["record_id"]
        ordinal = record_counts.get(record, 0); record_counts[record] = ordinal + 1
        row["corpus_seed"] = int(row["corpus_seed"])
        row["event_index"] = int(row["event_index"])
        row["group_index"] = int(row["group_index"])
        row["global_event_rank"] = global_rank
        row["record_event_ordinal"] = ordinal
        row["surface_id"] = surface_id
    return rows


def load_world_block(block: str, world_id: str, surface_id: str) -> list[dict]:
    seeds = sorted(int(row["corpus_seed"]) for row in block_manifest(block) if row["world_id"] == world_id)
    return [event for seed in seeds for event in load_seed(block, world_id, seed, surface_id)]


def available_worlds(block: str) -> tuple[str, ...]:
    return tuple(sorted({row["world_id"] for row in block_manifest(block)}))


def available_seeds(block: str) -> tuple[int, ...]:
    return tuple(sorted({int(row["corpus_seed"]) for row in block_manifest(block)}))
