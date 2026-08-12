#!/usr/bin/env python3
"""Freeze the Rosettes 3x5 geometry using annotation metadata only."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RD5X3001_ROSETTES_DOORWAY_TOPOLOGY_METHOD.md"
ANN = BASE / "results/existing_human_exact_locus_annotations.tsv"
OUT = BASE / "results/rd5x3001_rosettes_doorway_selection.json"
REPORT = BASE / "results/rd5x3001_rosettes_doorway_selection_report.md"

CANVAS = "1006231"
IMAGE_SHA = "4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    wanted = {f"fRos.{number}" for number in range(146, 161)}
    rows = []
    with ANN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in wanted:
                # Persist geometry/source identifiers only, never filler fields.
                rows.append({
                    "page": row["page"], "locus": row["locus"],
                    "old_locus": row["old_locus"], "unit": row["unit"],
                    "relation_scope": row["relation_scope"], "certainty": row["certainty"],
                })
    rows.sort(key=lambda row: int(row["locus"].split(".")[1]))
    if {row["locus"] for row in rows} != wanted or len(rows) != 15:
        raise SystemExit("doorway locus set mismatch")
    if {row["page"] for row in rows} != {"f85v2"} or {row["unit"] for row in rows} != {"X9"}:
        raise SystemExit("doorway metadata mismatch")
    result = {
        "experiment": "RD5X3001_ROSETTES_DOORWAY_TOPOLOGY",
        "status": "FROZEN_15_ROWS_IMAGE_UNOPENED",
        "decision": "AUTHORIZE_ONE_SOURCE_BOUND_GEOMETRY_INSPECTION",
        "inputs": {"method_sha256": sha(METHOD), "annotation_atlas_sha256": sha(ANN)},
        "source": {
            "canvas_id": CANVAS,
            "official_full_image_url": f"https://collections.library.yale.edu/iiif/2/{CANVAS}/full/full/0/default.jpg",
            "official_full_image_sha256": IMAGE_SHA,
            "official_full_image_dimensions": [7925, 7268],
        },
        "rows": rows,
        "counts": {"physical_folios": 1, "doorways_hypothesized": 5, "rows_per_doorway_hypothesized": 3, "selected_loci": 15},
        "allowed_outcomes": [
            "FIVE_DOORWAY_OWNED_THREE_ROW_LABELS", "ONE_THREE_LINE_PARAGRAPH",
            "MIXED_OR_OTHER_LAYOUT", "UNCERTAIN",
        ],
        "access": {
            "image_opened_by_builder": False,
            "filler_identity_persisted_or_used": False,
            "prior_overlap_diagnostic_accidentally_displayed_fillers": True,
            "formal_or_semantic_feature_used": False,
        },
        "claim_ceiling": (
            "This selection can resolve only the local author-visible 3x5 grouping. It supplies no word, field, "
            "list identity, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# RD5X3-001 Rosettes doorway selection\n\n"
        "Status: **FROZEN_15_ROWS_IMAGE_UNOPENED**\n\n"
        "Fifteen exact human-annotated rows `fRos.146--160` are frozen as one source-visible topology question: "
        "five doorway-owned three-row labels versus one three-line paragraph. The builder stores only geometry "
        "identifiers and source bindings. Image pixels and filler identities are not used.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
