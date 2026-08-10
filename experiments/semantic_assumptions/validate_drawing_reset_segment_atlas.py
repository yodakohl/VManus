#!/usr/bin/env python3
"""Independent reconstruction of the drawing-reset segment atlas."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent; RES = HERE / "results"
SOURCE = RES / "source_native_structural_interlinear_v1.tsv"; ATLAS = RES / "drawing_reset_segment_atlas.tsv"
RESULT = RES / "drawing_reset_segment_atlas.json"; REPORT = RES / "drawing_reset_segment_atlas_report.md"
SPEC = HERE / "DRAWING_RESET_SEGMENT_ATLAS_SPEC.md"; PRODUCER = HERE / "build_drawing_reset_segment_atlas.py"
OUT = RES / "drawing_reset_segment_atlas_validation.json"; OUT_REPORT = RES / "drawing_reset_segment_atlas_validation_report.md"
DRAW = "ZL3b:DRAWING_INTERRUPTION;IT2a:DRAWING_INTERRUPTION;RF1b:DRAWING_INTERRUPTION"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def pos(i, n): return "SINGLE" if n == 1 else "FIRST" if i == 1 else "LAST" if i == n else "CORE"


def main():
    stored = json.loads(RESULT.read_text())
    with SOURCE.open(newline="") as handle: source = list(csv.DictReader(handle, delimiter="\t"))
    with ATLAS.open(newline="") as handle: atlas = list(csv.DictReader(handle, delimiter="\t"))
    source_by_id = {row["consensus_group_id"]: row for row in source}
    by_locus = defaultdict(list)
    for row in source: by_locus[row["locus"]].append(row)
    expected = {}; segments = Counter(); boundaries = Counter(); multi = 0; maximum = 0
    for locus, unordered in by_locus.items():
        rows = sorted(unordered, key=lambda row: int(row["group_index"]))
        cuts = [i + 1 for i, row in enumerate(rows[:-1]) if row["right_boundary_profile"] == DRAW and row["right_boundary_support"] == "3"]
        starts = [0] + cuts; stops = cuts + [len(rows)]; multi += bool(cuts); maximum = max(maximum, len(starts))
        segments[rows[0]["grammar_scope"]] += len(starts); boundaries[rows[0]["grammar_scope"]] += len(cuts)
        for si, (start, stop) in enumerate(zip(starts, stops), 1):
            for gi, row in enumerate(rows[start:stop], 1):
                expected[row["consensus_group_id"]] = {
                    "segment_id": f"{locus}|S{si:02d}", "segment_index": str(si), "segment_count": str(len(starts)),
                    "segment_group_index": str(gi), "segment_group_count": str(stop - start), "segment_position": pos(gi, stop - start),
                    "starts_after_drawing": "1" if start else "0", "ends_before_drawing": "1" if stop < len(rows) else "0",
                }
    errors = []; checks = 0
    if len(atlas) != len(source): errors.append("row count"); checks += 1
    if len({row["consensus_group_id"] for row in atlas}) != len(atlas): errors.append("duplicate group"); checks += 1
    for row in atlas:
        key = row["consensus_group_id"]; checks += 1
        if key not in expected: errors.append("unknown " + key); continue
        for field, value in expected[key].items():
            checks += 1
            if row[field] != value: errors.append(key + ":" + field)
        source_row = source_by_id[key]
        for field, value in source_row.items():
            checks += 1
            if row[field] != value: errors.append(key + ":source:" + field)
    counts = stored["counts"]
    derived = {"rows": len(atlas), "physical_loci": len(by_locus), "segments": sum(segments.values()), "drawing_reset_boundaries": sum(boundaries.values()),
               "segments_by_scope": dict(sorted(segments.items())), "drawing_boundaries_by_scope": dict(sorted(boundaries.items())),
               "multi_segment_loci": multi, "maximum_segments_per_locus": maximum,
               "post_drawing_segment_starts": sum(row["starts_after_drawing"] == "1" and row["segment_group_index"] == "1" for row in atlas)}
    checks += 1
    if counts != derived: errors.append("counts")
    checks += 1
    if stored["atlas_sha256"] != sha(ATLAS): errors.append("atlas hash")
    checks += 1
    expected_report = (
        "# Drawing-reset segment atlas\n\n" f"Status: **{stored['status']}**.\n\nThe atlas preserves all **{len(atlas):,}** groups in **{len(by_locus):,}** physical loci and splits **{sum(boundaries.values()):,}** confirmed drawing-reset boundaries into **{sum(segments.values()):,}** segments. **{multi:,}** loci contain at least one split; the maximum is **{maximum}** segments in one locus.\n\n"
        "This corrects structural unit boundaries only. It does not assign either side to the illustration and supplies no word, meaning, plaintext, or translation.\n")
    if REPORT.read_text() != expected_report: errors.append("report")
    validation = {"experiment": "DRAWING_RESET_SEGMENT_ATLAS_VALIDATION", "status": "PASS" if not errors else "FAIL", "assertions": checks,
                  "discrepancies": errors, "atlas_sha256": sha(ATLAS), "producer_result_sha256": sha(RESULT),
                  "reconstructed_counts": derived, "english_glosses": 0,
                  "claim_ceiling": stored["claim_ceiling"]}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text("# Drawing-reset segment atlas validation\n\n" f"Status: **{validation['status']}** with **{checks:,}** checks and **{len(errors)}** discrepancies.\n")
    print(json.dumps(validation, indent=2, sort_keys=True))
    if errors: raise SystemExit(1)


if __name__ == "__main__": main()
