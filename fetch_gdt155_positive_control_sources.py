#!/usr/bin/env python3
"""Fetch the two public GDT155 text sources and verify their frozen hashes."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

SOURCES = (
    (
        "ste1.xml",
        "https://gams.uni-graz.at/o:corema.ste1/TEI_SOURCE",
        37206,
        "3db06c80345e584e5b6af7e062af839964312b92bcf1edb8b88aa05110024df6",
        "",
    ),
    (
        "nuremberg_labels.zip",
        "https://zenodo.org/api/records/13881575/files/labels.zip/content",
        262212368,
        "59e5264acb4546477567e78c8b3d444c472f1a0a5256ee0ee7d0407a70904652",
        "ce2c6150d9fc45ac4b4ea2a439b7aa8e",
    ),
)


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, url, size, expected_sha, expected_md5 in SOURCES:
        target = args.output_dir / name
        if not target.exists() or target.stat().st_size != size:
            request = urllib.request.Request(url, headers={"User-Agent": "VManus-GDT155/1"})
            with urllib.request.urlopen(request) as source, target.open("wb") as sink:
                while chunk := source.read(1024 * 1024):
                    sink.write(chunk)
        assert target.stat().st_size == size, (name, target.stat().st_size, size)
        assert digest(target, "sha256") == expected_sha, name
        if expected_md5:
            assert digest(target, "md5") == expected_md5, name
        print(f"VERIFIED\t{name}\t{size}\t{expected_sha}")


if __name__ == "__main__":
    main()
