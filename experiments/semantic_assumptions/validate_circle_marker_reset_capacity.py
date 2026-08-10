#!/usr/bin/env python3
"""Independent validator for the circle drawn-marker reset capacity panel."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
R = BASE / "results"
S = R / "public_circle_seam_coordinate_audit.tsv"
G = R / "source_sta_group_alignment.tsv"
P = R / "circle_marker_reset_capacity.json"
M = R / "circle_marker_reset_capacity.md"
OUT = R / "circle_marker_reset_capacity_validation.json"
OUT_MD = R / "circle_marker_reset_capacity_validation.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing overwrite")
    checks = 0
    def verify(value: bool, label: str) -> None:
        nonlocal checks
        if not value:
            raise AssertionError(label)
        checks += 1

    with S.open(encoding="utf-8", newline="") as handle:
        seams = list(csv.DictReader(handle, delimiter="\t"))
    markers = {row["locus"]: row for row in seams if row["stolfi_mentions_drawn_marker"] == "1"}
    controls = {row["locus"]: row for row in seams if row["stolfi_explicit_no_obvious_start"] == "1"}
    verify(len(markers) == 22, "marker count")
    verify(len(controls) == 25, "control count")
    verify(not set(markers) & set(controls), "disjoint classes")
    strong = {}
    for locus, row in markers.items():
        text = (row["stolfi_unit_description"] + " " + row["stolfi_start_note"]).lower()
        if not any(phrase in text for phrase in ("faint radial stroke", "barely visible", "radial stroke?")):
            strong[locus] = row
    verify(len(strong) == 18, "conservative count")

    selected = set(markers) | set(controls)
    cells = defaultdict(list)
    with G.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in selected:
                cells[(row["edition"], row["locus"])].append(row)
    expected = {(edition, locus) for edition in ("ZL3b", "IT2a", "RF1b") for locus in selected}
    verify(set(cells) == expected, "complete cell set")
    for key, rows in cells.items():
        rows.sort(key=lambda row: int(row["source_group_index"]))
        verify([int(row["source_group_index"]) for row in rows] == list(range(1, len(rows) + 1)), "consecutive group order")
        verify(all(row["primary_sta_families"] and int(row["primary_sta_symbol_count"]) > 0 for row in rows), "nonempty STA groups")

    def summarize(loci: set[str]) -> dict[str, object]:
        x = [rows for (edition, locus), rows in cells.items() if locus in loci]
        lengths = list(map(len, x))
        source = markers | controls
        return {
            "physical_loci": len(loci),
            "pages": len({source[locus]["page"] for locus in loci}),
            "folios": sorted({source[locus]["folio"] for locus in loci}),
            "reading_locus_cells": len(x),
            "source_groups": sum(lengths),
            "min_groups_per_cell": min(lengths),
            "max_groups_per_cell": max(lengths),
            "cells_by_reading": dict(Counter(edition for edition, locus in cells if locus in loci)),
        }

    prod = json.loads(P.read_text(encoding="utf-8"))
    verify(prod["marker"] == summarize(set(markers)), "marker summary exact")
    verify(prod["conservative_marker"] == summarize(set(strong)), "conservative summary exact")
    verify(prod["no_obvious_start_control"] == summarize(set(controls)), "control summary exact")
    verify(prod["marker_loci"] == sorted(markers), "marker IDs exact")
    verify(prod["conservative_marker_loci"] == sorted(strong), "conservative IDs exact")
    verify(prod["no_obvious_start_loci"] == sorted(controls), "control IDs exact")
    verify(prod["inputs"][S.name] == sha(S), "seam hash")
    verify(prod["inputs"][G.name] == sha(G), "group hash")
    verify(prod["status"] == "PASS_UNSCORED_22_MARKERS_18_CONSERVATIVE_6_FOLIOS", "status")
    verify(prod["decision"] == "AUTHORIZE_PREREGISTRATION_AND_TARGET_BLIND_CALIBRATION_ONLY", "decision")
    verify(all(prod["gates"].values()), "gates")
    report = M.read_text(encoding="utf-8")
    verify("No boundary score was computed here" in report, "report ceiling")

    result = {
        "experiment": "CIRCLE_MARKER_RESET_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_141_CELL_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "bindings": {
            "producer_result_sha256": sha(P),
            "producer_report_sha256": sha(M),
            "validator_sha256": sha(Path(__file__)),
        },
        "decision": "VALIDATED_CAPACITY_ONLY",
        "claim_ceiling": prod["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Circle marker reset capacity validation\n\n"
        "Status: **PASS_INDEPENDENT_141_CELL_RECONSTRUCTION**\n\n"
        f"A nonimporting validator passed {checks:,} checks and independently reconstructed the 22 marker "
        "loci, 18 conservative markers, 25 disjoint no-obvious-start controls, all 141 reading-locus cells, "
        "source-group order and coverage, hashes, gates, and the unscored decision. No boundary score or "
        "semantic assignment was computed.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
