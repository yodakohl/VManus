#!/usr/bin/env python3
"""Transport-only gzip correction for the frozen GDT395 scorer."""

from __future__ import annotations

import csv
import gzip
from pathlib import Path

import score_identifiability as v1


def open_tsv_v2(path: Path) -> tuple[object, csv.DictReader]:
    try:
        if path.suffix == ".gz":
            handle = gzip.open(path, "rt", encoding="utf-8", newline="")
        else:
            handle = path.open("r", encoding="utf-8", newline="")
    except OSError:
        raise v1.Refusal(f"cannot open TSV {v1.portable_path(path)}") from None
    reader = csv.DictReader(handle, delimiter="\t")
    if reader.fieldnames is None:
        handle.close()
        raise v1.Refusal(f"TSV has no header: {v1.portable_path(path)}")
    return handle, reader


def main() -> int:
    v1.open_tsv = open_tsv_v2
    return v1.main()


if __name__ == "__main__":
    raise SystemExit(main())

