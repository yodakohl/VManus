#!/usr/bin/env python3
"""Build the score-blind LRG002 corrected-segment capacity panel."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RES = HERE / "results"
SOURCE = RES / "drawing_reset_segment_atlas.tsv"
SOURCE_VALIDATION = RES / "drawing_reset_segment_atlas_validation.json"
LRG_VALIDATION = RES / "lrg001_label_register_target_recovered_validation.json"
SPEC = HERE / "LRG002_PROSE_SLOT_PROJECTION_CAPACITY_SPEC.md"
OUT = RES / "lrg002_prose_slot_capacity.tsv"
OUT_JSON = RES / "lrg002_prose_slot_capacity.json"
REPORT = RES / "lrg002_prose_slot_capacity_report.md"
FIELDS = [
    "consensus_group_id", "segment_id", "page", "physical_folio", "section",
    "symbol_count", "segment_group_index", "segment_group_count",
    "segment_position", "folio_parity", "primary_slot_eligible",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"(f\d+)", page)
    if not match:
        raise RuntimeError(f"invalid page {page}")
    return match.group(1)


def main() -> None:
    if any(path.exists() for path in (OUT, OUT_JSON, REPORT)):
        raise RuntimeError("LRG002 capacity output exists")
    validation = json.loads(SOURCE_VALIDATION.read_text(encoding="utf-8"))
    lrg = json.loads(LRG_VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS":
        raise RuntimeError("drawing segment validation absent")
    if lrg["status"] != "PASS_RECIPROCAL_LRG001_RECOVERY_RECONSTRUCTION":
        raise RuntimeError("LRG001 validation absent")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = [
            row for row in csv.DictReader(handle, delimiter="\t")
            if row["grammar_scope"] == "CONFIRMED_PROSE" and row["section"] in {"B", "P"}
        ]
    segments: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        segments[row["segment_id"]].append(row)
    output = []
    for row in rows:
        physical = folio(row["page"])
        eligible = len(segments[row["segment_id"]]) >= 3
        output.append({
            "consensus_group_id": row["consensus_group_id"],
            "segment_id": row["segment_id"],
            "page": row["page"],
            "physical_folio": physical,
            "section": row["section"],
            "symbol_count": row["symbol_count"],
            "segment_group_index": row["segment_group_index"],
            "segment_group_count": row["segment_group_count"],
            "segment_position": row["segment_position"],
            "folio_parity": "ODD" if int(physical[1:]) % 2 else "EVEN",
            "primary_slot_eligible": "1" if eligible else "0",
        })
    primary = [row for row in output if row["primary_slot_eligible"] == "1"]
    primary_segments: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in primary:
        primary_segments[row["segment_id"]].append(row)
    for identifier, group in primary_segments.items():
        positions = Counter(row["segment_position"] for row in group)
        if positions["FIRST"] != 1 or positions["LAST"] != 1 or positions["CORE"] != len(group) - 2:
            raise RuntimeError(f"invalid primary segment {identifier}")
    counts = {
        "normalization_rows": len(output),
        "normalization_segments": len(segments),
        "primary_rows": len(primary),
        "primary_segments": len(primary_segments),
        "pages": len({row["page"] for row in output}),
        "physical_folios": len({row["physical_folio"] for row in output}),
        "rows_by_section": dict(sorted(Counter(row["section"] for row in primary).items())),
        "rows_by_position": dict(sorted(Counter(row["segment_position"] for row in primary).items())),
        "segments_by_folio": dict(sorted(Counter(row["physical_folio"] for row in primary if row["segment_position"] == "FIRST").items(), key=lambda item: int(item[0][1:]))),
        "parities": sorted({row["folio_parity"] for row in output}),
    }
    expected = (5824, 742, 5769, 705, 34, 16)
    observed = tuple(counts[key] for key in ("normalization_rows", "normalization_segments", "primary_rows", "primary_segments", "pages", "physical_folios"))
    if observed != expected or set(counts["rows_by_section"]) != {"B", "P"} or counts["parities"] != ["EVEN", "ODD"]:
        raise RuntimeError(f"LRG002 capacity drift {observed}")
    with OUT.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(output)
    result = {
        "status": "PASS_SCORE_BLIND_LRG002_CAPACITY",
        "counts": counts,
        "inputs": {path.name: sha(path) for path in (SOURCE, SOURCE_VALIDATION, LRG_VALIDATION, SPEC, Path(__file__))},
        "capacity_sha256": sha(OUT),
        "profile_reconstructed": False,
        "position_scores_computed": False,
        "family_sequence_used_for_selection": False,
        "decision": "GO_TARGET_BLIND_LRG002_CALIBRATION",
        "claim_ceiling": "Score-blind positional capacity only; no label-like slot, word, name, identifier, POS, meaning, plaintext, or translation is established.",
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT_JSON.write_text(text, encoding="utf-8", newline="\n")
    REPORT.write_text(
        "# LRG002 prose-slot capacity\n\n"
        "Status: **PASS_SCORE_BLIND_LRG002_CAPACITY**.\n\n"
        "The fixed B/P universe contains **5,824** confirmed-prose groups in **742** corrected segments. The primary position panel contains **5,769** groups in **705** segments on **34** pages and **16** physical folios; every primary segment has one FIRST, one LAST, and at least one CORE group.\n\n"
        "No LRG001 profile, sequence score, or position association was computed. This is capacity only, not a word, name, identifier, POS, meaning, plaintext, or translation.\n",
        encoding="utf-8", newline="\n",
    )
    print(text, end="")


if __name__ == "__main__":
    main()
