#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Read or write the Pass-970 workshop cards.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--decode", metavar="SURFACE")
    mode.add_argument("--encode", metavar="COMPONENT_RECIPE")
    args = parser.parse_args()
    if args.decode is not None:
        rows = {row["surface"]: row for row in read_tsv("PASS970_1078_SURFACE_DECODER.tsv")}
        result = rows.get(args.decode, {"status": "UNSEEN_SURFACE", "surface": args.decode})
    else:
        rows = {row["component_recipe"]: row for row in read_tsv("PASS970_948_RECIPE_ENCODER.tsv")}
        result = rows.get(args.encode, {"status": "UNSEEN_RECIPE", "component_recipe": args.encode})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
