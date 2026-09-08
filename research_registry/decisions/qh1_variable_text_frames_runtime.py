#!/usr/bin/env python3
"""Recount QH1 fixed-flank/variable-middle frames from guarded TSV output.

The input must be the projected output of vmanus-exp query-tsv; this script
does not open the mixed source TSV directly.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict

FRAMES = [
    ("chedy", "chedy"),
    ("ol", "aiin"),
    ("chol", "daiin"),
    ("daiin", "daiin"),
    ("qokain", "qokain"),
]
READERS = ("ZL3b", "IT2a", "RF1b")
ADJACENT = {"DEFINITE_SPACE", "UNCERTAIN_SMALL_SPACE"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()
    rows = list(csv.DictReader(open(args.input, encoding="utf-8"), delimiter="\t"))
    by = defaultdict(dict)
    for row in rows:
        by[(row["edition"], row["locus"])][int(row["source_group_index"])] = row

    result = {
        "schema": "QH1_VARIABLE_TEXT_FRAMES_V1",
        "scope": {
            "queried_rows": len(rows),
            "selector": "page",
            "allowlist": "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv",
            "source_projection": "experiments/semantic_assumptions/results/source_separator_transcription.tsv",
            "readers": list(READERS),
            "frame_rule": "same edition+locus, consecutive complete groups X A Y, fixed raw X and Y, variable raw A, all four internal separators definite or uncertain small space",
            "forbidden_prefix": "f84",
        },
        "frames": [],
    }
    for left, right in FRAMES:
        frame = {"left": left, "right": right, "readers": {}}
        for edition in READERS:
            hits = []
            for (ed, locus), groups in by.items():
                if ed != edition:
                    continue
                for i, middle in groups.items():
                    if i <= 1 or i >= int(middle["source_group_count"]):
                        continue
                    if i - 1 not in groups or i + 1 not in groups:
                        continue
                    before, after = groups[i - 1], groups[i + 1]
                    if before["ivtff_group_raw"] != left or after["ivtff_group_raw"] != right:
                        continue
                    separators = [
                        before["right_separator"],
                        middle["left_separator"],
                        middle["right_separator"],
                        after["left_separator"],
                    ]
                    if not all(value in ADJACENT for value in separators):
                        continue
                    hits.append(
                        {
                            "locus": locus,
                            "source_group_index": i,
                            "raw_groups": [left, middle["ivtff_group_raw"], right],
                            "source_group_ids": [
                                before["source_group_id"],
                                middle["source_group_id"],
                                after["source_group_id"],
                            ],
                            "internal_separators": separators,
                            "source_row_index": middle["source_row_index"],
                        }
                    )
            hits.sort(key=lambda x: (x["locus"], x["source_group_index"]))
            frame["readers"][edition] = {
                "occurrences": len(hits),
                "distinct_middles": len({hit["raw_groups"][1] for hit in hits}),
                "middle_alternatives": sorted({hit["raw_groups"][1] for hit in hits}),
                "hits": hits,
            }
        result["frames"].append(frame)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
