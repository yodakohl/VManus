#!/usr/bin/env python3
"""Hash the curated pre-reset evidence subset and lock active evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / "archive_pre_reset_2026-08-06"
MANIFEST = ARCHIVE / "ARCHIVE_MANIFEST.tsv"
SUMMARY = ARCHIVE / "ARCHIVE_MANIFEST.json"
PRIMARY = ROOT / "experiments" / "semantic_assumptions" / "grammar" / "PRIMARY_EVIDENCE.tsv"
PRIMARY_LOCK = PRIMARY.with_name("PRIMARY_EVIDENCE_LOCK.tsv")
EXCLUDED = {MANIFEST.resolve(), SUMMARY.resolve()}


def is_transient(path: Path) -> bool:
    """Ignore interpreter/build debris that is not research evidence."""
    return "__pycache__" in path.parts or path.suffix == ".pyc" or path.name.endswith(".part")


def digest(path: Path) -> tuple[int, str]:
    before = path.stat()
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            value.update(chunk)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError(f"file changed while hashing: {path}")
    return after.st_size, value.hexdigest()


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    temporary = path.with_suffix(path.suffix + ".part")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()
    if not ARCHIVE.is_dir():
        raise FileNotFoundError(ARCHIVE)
    symlinks = sorted(path for path in ARCHIVE.rglob("*") if path.is_symlink())
    if symlinks:
        raise RuntimeError(f"archive contains symlink: {symlinks[0]}")
    paths = sorted(
        path for path in ARCHIVE.rglob("*")
        if path.is_file() and path.resolve() not in EXCLUDED and not is_transient(path)
    )
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        hashes = list(pool.map(digest, paths))
    rows = [
        {"path": str(path.relative_to(ARCHIVE)), "bytes": size, "sha256": sha}
        for path, (size, sha) in zip(paths, hashes)
    ]
    write_tsv(MANIFEST, ["path", "bytes", "sha256"], rows)
    manifest_bytes, manifest_sha = digest(MANIFEST)

    with PRIMARY.open(encoding="utf-8", newline="") as handle:
        primary_rows = list(csv.DictReader(handle, delimiter="\t"))
    primary_paths = [ROOT / row["path"] for row in primary_rows]
    missing = [path for path in primary_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(missing[0])
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        primary_hashes = list(pool.map(digest, primary_paths))
    locked = []
    for row, (size, sha) in zip(primary_rows, primary_hashes):
        locked.append({**row, "bytes": size, "sha256": sha})
    write_tsv(
        PRIMARY_LOCK,
        ["claim_id", "status", "artifact_role", "path", "bytes", "sha256"],
        locked,
    )

    legacy_ledger = ARCHIVE / "semantic_assumptions" / "ACTIVE_EXPERIMENT_LEDGER.tsv"
    legacy_rows = sum(1 for _ in legacy_ledger.open(encoding="utf-8")) - 1
    payload = {
        "status": "CURATED_PRIMARY_EVIDENCE_ARCHIVE_HASHED",
        "scope": "retained primary evidence only; superseded bulk removed 2026-08-08",
        "archive": str(ARCHIVE.relative_to(ROOT)),
        "file_count_excluding_manifest_files": len(rows),
        "total_bytes_excluding_manifest_files": sum(int(row["bytes"]) for row in rows),
        "manifest_bytes": manifest_bytes,
        "manifest_sha256": manifest_sha,
        "legacy_experiment_rows": legacy_rows,
        "primary_evidence_files": len(locked),
        "workers": args.workers,
        "excluded_self_files": [MANIFEST.name, SUMMARY.name],
    }
    temporary = SUMMARY.with_suffix(SUMMARY.suffix + ".part")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, SUMMARY)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
