#!/usr/bin/env python3
"""Reduce the eight frozen native observations to the registered decision."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
IMAGES = {
    "f75v": (ROOT / "experiments/yolo/gdt852_f75v_native_join_split_spacing/runtime/f75v.jpg", "654edf15a65d1a2bb0d7bb4995f8f6fba1625d5eed847c9b6969d1c44e385a23"),
    "f99v": (ROOT / "experiments/yolo/gdt881_f99v_text_graphic_stroke_interface/runtime/1006247.jpg", "111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5"),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path):
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file, delimiter="\t"))


def main():
    loci = table(BASE / "src/LOCI.tsv")
    observations = table(BASE / "src/OBSERVATIONS.tsv")
    assert len(loci) == len(observations) == 8
    assert len({r["locus"] for r in loci}) == 8
    frozen = {(r["page"], r["locus"], r["surface"]) for r in loci}
    assert frozen == {(r["page"], r["locus"], r["surface"]) for r in observations}
    assert set(IMAGES) == {r["page"] for r in loci}
    assert all(r["status"] in {"SINGULAR", "AMBIGUOUS", "NONE", "UNLOCATABLE"} for r in observations)
    assert all(r["candidate_owner"] and r["rival_or_failure"] and r["native_observation"] for r in observations)
    for image_path, expected in IMAGES.values():
        assert digest(image_path) == expected, image_path
    counts = Counter(r["status"] for r in observations)
    result = {
        "experiment": "GDT1083",
        "status": "NATIVE_SINGULAR_OWNER_FOUND" if counts["SINGULAR"] else "NO_NATIVE_SINGULAR_OWNER",
        "pages": sorted(IMAGES),
        "loci": len(loci),
        "status_counts": dict(sorted(counts.items())),
        "singular_loci": [r["locus"] for r in observations if r["status"] == "SINGULAR"],
        "method_sha256": digest(BASE / "METHOD.md"),
        "loci_sha256": digest(BASE / "src/LOCI.tsv"),
        "observations_sha256": digest(BASE / "src/OBSERVATIONS.tsv"),
        "image_sha256": {page: expected for page, (_, expected) in IMAGES.items()},
        "previous_exposure": True,
        "independent_confirmation_capacity": 0,
        "confirmed_meanings": 0,
    }
    (BASE / "artifacts/RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
