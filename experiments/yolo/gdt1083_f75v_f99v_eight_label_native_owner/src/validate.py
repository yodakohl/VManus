#!/usr/bin/env python3
"""Independent mechanical audit of GDT1083 coverage, source, and reduction."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name):
    with (BASE / name).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file, delimiter="\t"))


def main():
    result = json.loads((BASE / "artifacts/RESULT.json").read_text(encoding="utf-8"))
    loci = rows("src/LOCI.tsv")
    observed = rows("src/OBSERVATIONS.tsv")
    assert sha(BASE / "METHOD.md") == result["method_sha256"] == "a0e3e60771e7edf4a25b9d8c7c2ef16d67677121981379db3b46dc21cb6db542"
    assert sha(BASE / "src/LOCI.tsv") == result["loci_sha256"] == "1a58f93aa9e5ef9fb74a86565b1612dd53f8dd1f3142bc41130e18b26b2b8d41"
    assert sha(BASE / "src/OBSERVATIONS.tsv") == result["observations_sha256"]
    assert len(loci) == len(observed) == result["loci"] == 8
    assert len({r["locus"] for r in loci}) == len({r["locus"] for r in observed}) == 8
    for loc, obs in zip(loci, observed):
        assert (loc["page"], loc["locus"], loc["surface"]) == (obs["page"], obs["locus"], obs["surface"])
        assert obs["status"] in {"SINGULAR", "AMBIGUOUS", "NONE", "UNLOCATABLE"}
        assert obs["candidate_owner"] and obs["rival_or_failure"] and obs["native_observation"]
    sources = {
        "f75v": ROOT / "experiments/yolo/gdt852_f75v_native_join_split_spacing/runtime/f75v.jpg",
        "f99v": ROOT / "experiments/yolo/gdt881_f99v_text_graphic_stroke_interface/runtime/1006247.jpg",
    }
    assert set(sources) == set(result["pages"]) == {r["page"] for r in loci}
    assert {page: sha(path) for page, path in sources.items()} == result["image_sha256"]
    counts = dict(sorted(Counter(r["status"] for r in observed).items()))
    assert counts == result["status_counts"]
    singular = [r["locus"] for r in observed if r["status"] == "SINGULAR"]
    assert singular == result["singular_loci"]
    assert result["status"] == ("NATIVE_SINGULAR_OWNER_FOUND" if singular else "NO_NATIVE_SINGULAR_OWNER")
    assert result["previous_exposure"] and result["independent_confirmation_capacity"] == result["confirmed_meanings"] == 0
    validation = {"status": "PASS", "eight_frozen_loci_covered": True, "verified_image_hashes": sorted(sources), "status_counts": counts, "meaning_validated": False}
    (BASE / "artifacts/VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
