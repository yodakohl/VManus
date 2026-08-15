#!/usr/bin/env python3
"""Fetch and verify the sole new external GDT158 source."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

URL = "https://opus.bibliothek.uni-augsburg.de/opus4/files/98153/Augsburger_Baumeisterb%C3%BCcher_1320_1440.xlsx"
SIZE = 13_847_974
SHA256 = "bed2ff0e4e427cc8c602893b852a759c26fe91d18e9891a26ba80829360160a1"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.output.exists() or args.output.stat().st_size != SIZE:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(URL, headers={"User-Agent": "VManus-GDT158/1"})
        with urllib.request.urlopen(request) as source, args.output.open("wb") as sink:
            while chunk := source.read(1024 * 1024):
                sink.write(chunk)
    assert args.output.stat().st_size == SIZE
    assert digest(args.output) == SHA256
    print(f"VERIFIED\t{args.output}\t{SIZE}\t{SHA256}")


if __name__ == "__main__":
    main()
