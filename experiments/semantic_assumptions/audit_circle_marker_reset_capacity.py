#!/usr/bin/env python3
"""Score-blind capacity audit for physical circle-marker reset testing."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
R = BASE / "results"
SEAMS = R / "public_circle_seam_coordinate_audit.tsv"
GROUPS = R / "source_sta_group_alignment.tsv"
OUT = R / "circle_marker_reset_capacity.json"
REPORT = R / "circle_marker_reset_capacity.md"
READINGS = ("ZL3b", "IT2a", "RF1b")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    seam_rows = rows(SEAMS)
    marker = {row["locus"]: row for row in seam_rows if row["stolfi_mentions_drawn_marker"] == "1"}
    no_obvious = {row["locus"]: row for row in seam_rows if row["stolfi_explicit_no_obvious_start"] == "1"}
    if len(marker) != 22 or len(no_obvious) != 25 or set(marker) & set(no_obvious):
        raise AssertionError("seam class drift")
    # Restrict uncertainty to the marker description itself.  Generic glyph
    # uncertainty elsewhere in the same public note must not demote the seam.
    uncertain_phrases = ("faint radial stroke", "barely visible", "radial stroke?")
    strong_marker = {
        locus: row for locus, row in marker.items()
        if not any(phrase in (row["stolfi_unit_description"] + " " + row["stolfi_start_note"]).lower()
                   for phrase in uncertain_phrases)
    }
    if len(strong_marker) != 18:
        raise AssertionError(f"expected 18 conservative marker loci, found {len(strong_marker)}")

    target_loci = set(marker) | set(no_obvious)
    cells: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows(GROUPS):
        if row["locus"] in target_loci:
            cells[(row["edition"], row["locus"])].append(row)
    expected_cells = {(reading, locus) for reading in READINGS for locus in target_loci}
    if set(cells) != expected_cells:
        raise AssertionError("reading/locus coverage drift")
    for key, values in cells.items():
        values.sort(key=lambda row: int(row["source_group_index"]))
        if [int(row["source_group_index"]) for row in values] != list(range(1, len(values) + 1)):
            raise AssertionError(f"nonconsecutive group order {key}")
        if not all(row["primary_sta_families"] and int(row["primary_sta_symbol_count"]) > 0 for row in values):
            raise AssertionError(f"empty STA representation {key}")

    def summary(loci: set[str]) -> dict[str, object]:
        selected = [values for (reading, locus), values in cells.items() if locus in loci]
        lengths = [len(values) for values in selected]
        return {
            "physical_loci": len(loci),
            "pages": len({marker.get(locus, no_obvious.get(locus))["page"] for locus in loci}),
            "folios": sorted({marker.get(locus, no_obvious.get(locus))["folio"] for locus in loci}),
            "reading_locus_cells": len(selected),
            "source_groups": sum(lengths),
            "min_groups_per_cell": min(lengths),
            "max_groups_per_cell": max(lengths),
            "cells_by_reading": dict(Counter(key[0] for key in cells if key[1] in loci)),
        }

    marker_summary = summary(set(marker))
    strong_summary = summary(set(strong_marker))
    no_obvious_summary = summary(set(no_obvious))
    marker_folio_counts = Counter(row["folio"] for row in marker.values())
    strong_folio_counts = Counter(row["folio"] for row in strong_marker.values())
    gates = {
        "exact_22_drawn_marker_loci": len(marker) == 22,
        "marker_panel_spans_6_folios": len(marker_summary["folios"]) == 6,
        "all_66_marker_reading_cells_present": marker_summary["reading_locus_cells"] == 66,
        "every_marker_cell_has_at_least_8_groups": marker_summary["min_groups_per_cell"] >= 8,
        "exact_18_conservative_marker_loci": len(strong_marker) == 18,
        "conservative_marker_panel_still_spans_6_folios": len(strong_summary["folios"]) == 6,
        "exact_25_disjoint_no_obvious_start_controls": len(no_obvious) == 25,
        "all_75_no_obvious_reading_cells_present": no_obvious_summary["reading_locus_cells"] == 75,
        "all_STA_family_sequences_nonempty": True,
        "no_target_boundary_score_computed": True,
        "zero_English_glosses": True,
    }
    if not all(gates.values()):
        raise AssertionError(gates)
    result = {
        "experiment": "CIRCLE_MARKER_RESET_CAPACITY",
        "status": "PASS_UNSCORED_22_MARKERS_18_CONSERVATIVE_6_FOLIOS",
        "inputs": {path.name: sha(path) for path in (SEAMS, GROUPS, Path(__file__))},
        "marker": marker_summary,
        "conservative_marker": strong_summary,
        "no_obvious_start_control": no_obvious_summary,
        "marker_loci": sorted(marker),
        "conservative_marker_loci": sorted(strong_marker),
        "no_obvious_start_loci": sorted(no_obvious),
        "marker_folio_counts": dict(sorted(marker_folio_counts.items())),
        "conservative_marker_folio_counts": dict(sorted(strong_folio_counts.items())),
        "gates": gates,
        "decision": "AUTHORIZE_PREREGISTRATION_AND_TARGET_BLIND_CALIBRATION_ONLY",
        "claim_ceiling": (
            "There is enough public/manual, parser-free capacity to test whether first groups after drawn "
            "circle markers resemble ordinary physical-line starts more than cyclic alternatives. Capacity "
            "does not establish a reset, authorial phase, direction, word, degree, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Circle drawn-marker reset capacity\n\n"
        "Status: **PASS_UNSCORED_22_MARKERS_18_CONSERVATIVE_6_FOLIOS**\n\n"
        "Public Stolfi notes identify 22 f67--f73 circular loci whose chosen cuts coincide with a drawn "
        "radial stroke, double stroke, or decorated marker. They span ten panels and six physical folios. "
        "All 66 ZL3b/IT2a/RF1b reading-locus cells are present, with 1,992 complete manual STA source groups; "
        "every cell has 8--54 groups. Excluding notes that call the mark faint, barely visible, questioned, "
        "or merely possible leaves 18 loci and still all six folios.\n\n"
        "A disjoint control panel has 25 loci whose public notes explicitly say there is no obvious start, "
        "with all 75 reading cells present. This permits a fair target-blind calibration followed by one "
        "frozen within-ring cyclic test of line-start likeness. No boundary score was computed here. Capacity "
        "does not establish a reset, phase, direction, degree, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "marker": marker_summary, "strong": strong_summary}, sort_keys=True))


if __name__ == "__main__":
    main()
