#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
OUTPUT = EXP / "artifacts/COMPACT_MANIFEST.tsv"
EXCLUDED = {EXP / "experiment.json", OUTPUT, EXP / "artifacts/VALIDATION.json"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    files = sorted(
        path
        for path in EXP.rglob("*")
        if path.is_file() and path not in EXCLUDED and "__pycache__" not in path.parts
    )
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["relative_path", "bytes", "sha256"])
        for path in files:
            writer.writerow([path.relative_to(EXP).as_posix(), path.stat().st_size, sha256(path)])
    print(f"COMPACT_MANIFEST_OK {len(files)} files")


if __name__ == "__main__":
    main()
