#!/usr/bin/env python3
"""Independently validate the RD5X3-001 formal follow-up stop."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "results/source_sta_group_alignment.tsv"
TOPOLOGY = BASE / "results/rd5x3001_rosettes_doorway_topology_result.json"
RESULT = BASE / "results/rd5x3001_formal_followup_stop.json"
OUT = BASE / "results/rd5x3001_formal_followup_stop_validation.json"
REPORT = BASE / "results/rd5x3001_formal_followup_stop_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    rows = []
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            locus = row["locus"]
            if locus.startswith("fRos.") and 146 <= int(locus.split(".", 1)[1]) <= 160:
                rows.append((row["edition"], locus, int(row["source_group_index"]), int(row["source_group_count"])))
    editions = Counter(row[0] for row in rows)
    loci = {edition: len({row[1] for row in rows if row[0] == edition}) for edition in ("ZL3b", "IT2a", "RF1b")}
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "source_bound": result["inputs"]["source_sta_group_alignment_sha256"] == sha(SOURCE),
        "topology_bound": result["inputs"]["topology_result_sha256"] == sha(TOPOLOGY),
        "exact_32_rows": len(rows) == 32 and editions == Counter({"ZL3b": 16, "RF1b": 16}),
        "exact_locus_coverage": loci == {"ZL3b": 15, "IT2a": 0, "RF1b": 15},
        "only_fros151_is_doubled": sorted({locus for edition, locus, _, count in rows if edition == "ZL3b" and count == 2}) == ["fRos.151"],
        "zero_scoring": result["counts"]["formal_associations_scored"] == 0 and result["counts"]["p_values_computed"] == 0,
        "exposure_disclosed": result["access"]["formal_family_sequence_previously_displayed_during_capacity_diagnostic"] is True,
        "stop_reconstructed": result["decision"] == "DO_NOT_SCORE_RD5X3_FILLER_OR_POSITION_ASSOCIATIONS",
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RD5X3001_FORMAL_FOLLOWUP_STOP_VALIDATION",
        "status": "PASS_9_CHECK_METADATA_ONLY_STOP_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RD5X3-001 formal follow-up stop validation\n\n"
        "Status: **PASS_9_CHECK_METADATA_ONLY_STOP_RECONSTRUCTION**\n\n"
        "Independent compact code reconstructs the 32 metadata rows, 15/0/15 locus coverage, sole doubled locus, "
        "input hashes, exposure disclosure, zero-scoring state, canonical result, and stop decision. It never reads "
        "or emits the formal-family or EVA fields.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
