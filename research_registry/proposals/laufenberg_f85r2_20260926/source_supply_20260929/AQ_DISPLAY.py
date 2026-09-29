#!/usr/bin/env python3
"""Reproduce or verify the three declared source pixel projections; no OCR."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops


RECTANGLES = {
    "AQ_LEFT_COLUMN.png": [300, 340, 860, 2190],
    "AQ_RIGHT_COLUMN.png": [865, 340, 1450, 2190],
    "AQ_SHORT_NOTE.png": [295, 2300, 980, 2590],
}
SOURCE_HASH = "70f2b6f814fce4e7f855c099f64f2386f0f294cf1225e83da24628161ca99fc0"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-missing", action="store_true")
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    source = folder / "AO_LAT18499_f26r_native.jpg"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_HASH
    receipt = json.loads((folder / "AQ_DISPLAY_RECEIPT.json").read_text())
    assert receipt["source_sha256"] == SOURCE_HASH
    assert {r["file"]: r["rectangle"] for r in receipt["displays"]} == RECTANGLES
    checks = []
    with Image.open(source) as original:
        assert original.size == (1920, 2952)
        for row in receipt["displays"]:
            name = row["file"]
            expected = original.crop(tuple(RECTANGLES[name]))
            destination = folder / name
            if args.write_missing and not destination.exists():
                expected.save(destination, format="PNG")
            with Image.open(destination) as actual:
                equal = actual.mode == expected.mode and actual.size == expected.size
                if equal:
                    # Check each band, avoiding an RGB/alpha aggregate ambiguity.
                    equal = all(band.getbbox() is None for band in
                                ImageChops.difference(actual, expected).split())
            checks.append({"file": name, "pixels_equal": equal,
                           "hash_bound": hashlib.sha256(destination.read_bytes()).hexdigest()
                           == row["sha256"]})
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_HASH
    output = {"status": "PASS" if all(r["pixels_equal"] and r["hash_bound"]
              for r in checks) else "FAIL",
              "scope": "exact source hash, declared rectangles and unchanged decoded pixels; not Latin",
              "checks": checks}
    (folder / "AQ_DISPLAY_VALIDATION.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
