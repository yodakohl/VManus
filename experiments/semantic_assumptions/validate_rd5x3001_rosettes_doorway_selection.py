#!/usr/bin/env python3
"""Validate the source-only RD5X3-001 selection."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RD5X3001_ROSETTES_DOORWAY_TOPOLOGY_METHOD.md"
ANN = BASE / "results/existing_human_exact_locus_annotations.tsv"
RESULT = BASE / "results/rd5x3001_rosettes_doorway_selection.json"
OUT = BASE / "results/rd5x3001_rosettes_doorway_selection_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text())
    wanted = [f"fRos.{number}" for number in range(146, 161)]
    source = []
    with ANN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in set(wanted):
                source.append(row)
    source.sort(key=lambda row: int(row["locus"].split(".")[1]))
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "annotation_bound": result["inputs"]["annotation_atlas_sha256"] == sha(ANN),
        "exact_fifteen_loci": [row["locus"] for row in source] == wanted == [row["locus"] for row in result["rows"]],
        "one_page_one_unit": {row["page"] for row in source} == {"f85v2"} and {row["unit"] for row in source} == {"X9"},
        "official_canvas_bound": result["source"]["canvas_id"] == "1006231" and result["source"]["official_full_image_sha256"] == "4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed",
        "geometry_only_fields": set(result["rows"][0]) == {"page", "locus", "old_locus", "unit", "relation_scope", "certainty"},
        "image_and_fillers_sealed": not result["access"]["image_opened_by_builder"] and not result["access"]["filler_identity_persisted_or_used"],
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RD5X3001_SELECTION_VALIDATION",
        "status": "PASS_8_CHECK_SOURCE_ONLY_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT), "check_count": len(checks), "checks": checks,
        "image_opened": False, "filler_identity_used": False,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
