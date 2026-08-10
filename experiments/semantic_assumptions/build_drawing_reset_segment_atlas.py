#!/usr/bin/env python3
"""Build the source-native segment atlas implied by confirmed DIC001."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RES = HERE / "results"
SOURCE = RES / "source_native_structural_interlinear_v1.tsv"
DIC = RES / "dic001_drawing_interruption_target.json"
SPEC = HERE / "DRAWING_RESET_SEGMENT_ATLAS_SPEC.md"
SCRIPT = Path(__file__).resolve()
OUT = RES / "drawing_reset_segment_atlas.tsv"
OUT_JSON = RES / "drawing_reset_segment_atlas.json"
REPORT = RES / "drawing_reset_segment_atlas_report.md"
SOURCE_SHA = "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af"
DIC_SHA = "6d08072850be1fcfa183f72368a1f7657eb96c40b1b7a5d42b11216e398c12e8"
DRAW = "ZL3b:DRAWING_INTERRUPTION;IT2a:DRAWING_INTERRUPTION;RF1b:DRAWING_INTERRUPTION"
ADDED = ["segment_id", "segment_index", "segment_count", "segment_group_index", "segment_group_count",
         "segment_position", "starts_after_drawing", "ends_before_drawing"]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def natural(value): return tuple(int(x) if x.isdigit() else x for x in re.split(r"(\d+)", value))


def position(index, count):
    if count == 1: return "SINGLE"
    if index == 1: return "FIRST"
    if index == count: return "LAST"
    return "CORE"


def main():
    if sha(SOURCE) != SOURCE_SHA or sha(DIC) != DIC_SHA: raise SystemExit("drawing-reset atlas input drift")
    dic = json.loads(DIC.read_text())
    if dic["status"] != "CONFIRMED_DISTRIBUTED_RESET_LIKENESS" or not all(dic["gates"].values()):
        raise SystemExit("DIC001 confirmation absent")
    with SOURCE.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t"); source_fields = reader.fieldnames; rows = list(reader)
    loci = defaultdict(list)
    for row in rows: loci[row["locus"]].append(row)
    output = []; segment_counts = Counter(); boundary_scope = Counter()
    for locus in sorted(loci, key=natural):
        groups = sorted(loci[locus], key=lambda row: int(row["group_index"]))
        cuts = [i + 1 for i, row in enumerate(groups[:-1]) if row["right_boundary_profile"] == DRAW and row["right_boundary_support"] == "3"]
        spans = list(zip([0] + cuts, cuts + [len(groups)]))
        for segment_index, (start, stop) in enumerate(spans, 1):
            segment = groups[start:stop]; segment_id = f"{locus}|S{segment_index:02d}"
            for local_index, row in enumerate(segment, 1):
                enriched = dict(row)
                enriched.update({
                    "segment_id": segment_id, "segment_index": str(segment_index), "segment_count": str(len(spans)),
                    "segment_group_index": str(local_index), "segment_group_count": str(len(segment)),
                    "segment_position": position(local_index, len(segment)),
                    "starts_after_drawing": "1" if start > 0 else "0",
                    "ends_before_drawing": "1" if stop < len(groups) else "0",
                })
                output.append(enriched)
            segment_counts[groups[0]["grammar_scope"]] += 1
        boundary_scope[groups[0]["grammar_scope"]] += len(cuts)
    fields = ADDED + source_fields
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(output)
    counts = {
        "rows": len(output), "physical_loci": len(loci), "segments": sum(segment_counts.values()),
        "drawing_reset_boundaries": sum(boundary_scope.values()), "segments_by_scope": dict(sorted(segment_counts.items())),
        "drawing_boundaries_by_scope": dict(sorted(boundary_scope.items())),
        "multi_segment_loci": sum(1 for groups in loci.values() if any(row["right_boundary_profile"] == DRAW and row["right_boundary_support"] == "3" for row in groups[:-1])),
        "maximum_segments_per_locus": max(int(row["segment_count"]) for row in output),
        "post_drawing_segment_starts": sum(row["starts_after_drawing"] == "1" and row["segment_group_index"] == "1" for row in output),
    }
    result = {
        "experiment": "DRAWING_RESET_SEGMENT_ATLAS", "status": "PASS_COMPLETE_DIC001_SEGMENTATION",
        "inputs": {path.name: sha(path) for path in (SOURCE, DIC, SPEC, SCRIPT)}, "counts": counts,
        "atlas_sha256": sha(OUT), "all_source_rows_preserved_once": len(output) == len(rows) and len({row["consensus_group_id"] for row in output}) == len(rows),
        "english_glosses": 0, "picture_ownership_inferred": False,
        "claim_ceiling": "DIC001-informed source segmentation only; segment positions are not words, POS, meaning, plaintext, language, cipher, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Drawing-reset segment atlas\n\n"
        f"Status: **{result['status']}**.\n\nThe atlas preserves all **{len(output):,}** groups in **{len(loci):,}** physical loci and splits **{sum(boundary_scope.values()):,}** confirmed drawing-reset boundaries into **{sum(segment_counts.values()):,}** segments. **{counts['multi_segment_loci']:,}** loci contain at least one split; the maximum is **{counts['maximum_segments_per_locus']}** segments in one locus.\n\n"
        "This corrects structural unit boundaries only. It does not assign either side to the illustration and supplies no word, meaning, plaintext, or translation.\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__": main()
