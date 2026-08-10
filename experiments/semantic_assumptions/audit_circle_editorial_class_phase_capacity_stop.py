#!/usr/bin/env python3
"""Persist the source-role capacity stop for the frozen f67/f68 phase test."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
METHOD = BASE / "CIRCLE_EDITORIAL_CLASS_PHASE_METHOD.md"
RUNNER = BASE / "run_circle_editorial_class_phase.py"
ALIGN = RESULTS / "source_sta_group_alignment.tsv"
META = RESULTS / "source_separator_transcription.tsv"
PAGES = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
CONTROLS = RESULTS / "circle_editorial_class_phase_controls.json"
CONTROL_VALIDATION = RESULTS / "circle_editorial_class_phase_controls_validation.json"
OUT = RESULTS / "circle_editorial_class_phase_capacity_stop.json"
REPORT = RESULTS / "circle_editorial_class_phase_capacity_stop.md"
TARGET = RESULTS / "circle_editorial_class_phase.json"
TARGET_REPORT = RESULTS / "circle_editorial_class_phase_report.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
FOLIO_PAGES = {
    "f67": ("f67r1", "f67r2", "f67v1", "f67v2"),
    "f68": ("f68r1", "f68r2", "f68r3", "f68v1", "f68v2", "f68v3"),
}
EXPECTED_CLASSES = {
    "f67": ("A", "A", "A", "C"),
    "f68": ("A", "A", "A", "C", "A", "C"),
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if TARGET.exists() or TARGET_REPORT.exists():
        raise SystemExit("target artifact unexpectedly exists")
    controls = json.loads(CONTROLS.read_text(encoding="utf-8"))
    validation = json.loads(CONTROL_VALIDATION.read_text(encoding="utf-8"))
    assert controls["status"] == validation["status"] == "PASS"
    public = {row["page"]: row for row in rows(PAGES)}
    assert len(public) == 228
    derived = {}
    for folio, pages in FOLIO_PAGES.items():
        values = []
        for page in pages:
            description = public[page]["general_description"].lower()
            astro = "this is an astronomical page" in description
            cosmo = "this is a so-called cosmological page" in description
            assert astro != cosmo
            values.append("A" if astro else "C")
        derived[folio] = tuple(values)
    assert derived == EXPECTED_CLASSES

    meta_rows = rows(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    assert len(metadata) == len(meta_rows)
    target_pages = {page for pages in FOLIO_PAGES.values() for page in pages}
    zero_alternative = Counter()
    alternative = Counter()
    kind_groups = Counter()
    kind_loci = defaultdict(set)
    for row in rows(ALIGN):
        info = metadata[row["source_group_id"]]
        page = info["page"]
        if page not in target_pages:
            continue
        key = (page, row["edition"], info["kind"])
        kind_groups[key] += 1
        kind_loci[key].add(info["locus"])
        if info["kind"] == "C":
            if int(row["alternative_site_count"]):
                alternative[(page, row["edition"])] += 1
            else:
                zero_alternative[(page, row["edition"])] += 1

    coverage = {}
    missing = []
    for folio, pages in FOLIO_PAGES.items():
        coverage[folio] = {}
        for page in pages:
            coverage[folio][page] = {}
            for reading in READINGS:
                count = zero_alternative[(page, reading)]
                alt = alternative[(page, reading)]
                coverage[folio][page][reading] = {
                    "zero_alternative_C_groups": count,
                    "alternative_C_groups": alt,
                    "C_loci": len(kind_loci[(page, reading, "C")]),
                }
                if count == 0:
                    missing.append(f"{page}|{reading}")
    eligible_pages = {
        folio: [page for page in pages if all(zero_alternative[(page, reading)] > 0 for reading in READINGS)]
        for folio, pages in FOLIO_PAGES.items()
    }
    non_c_roles = {}
    for page in ("f67r2", "f67v1", "f67v2"):
        non_c_roles[page] = {
            reading: {
                kind: {
                    "groups": kind_groups[(page, reading, kind)],
                    "loci": len(kind_loci[(page, reading, kind)]),
                }
                for kind in ("P", "L", "R") if kind_groups[(page, reading, kind)]
            }
            for reading in READINGS
        }
    gates = {
        "public_ten_page_class_vector_exact": derived == EXPECTED_CLASSES,
        "controls_and_validation_pass": True,
        "all_30_page_reading_C_cells_nonempty": len(missing) == 0,
        "both_folios_have_two_or_more_C_pages": all(len(pages) >= 2 for pages in eligible_pages.values()),
        "f67_has_within_folio_same_and_different_pairs": len(eligible_pages["f67"]) >= 2,
        "target_artifacts_absent": True,
    }
    assert missing == [
        "f67r2|ZL3b", "f67r2|IT2a", "f67r2|RF1b",
        "f67v1|ZL3b", "f67v1|IT2a", "f67v1|RF1b",
        "f67v2|ZL3b", "f67v2|IT2a", "f67v2|RF1b",
    ]
    assert eligible_pages["f67"] == ["f67r1"]
    assert eligible_pages["f68"] == list(FOLIO_PAGES["f68"])
    result = {
        "experiment": "CIRCLE_EDITORIAL_CLASS_PHASE_CAPACITY_STOP",
        "status": "STOP_UNSCORED_INCOMPLETE_C_ROLE_PANEL",
        "decision": "DO_NOT_SCORE_OR_CHANGE_FROZEN_ROLE_SCOPE",
        "inputs": {path.name: sha(path) for path in (ALIGN, META, PAGES, METHOD, RUNNER, CONTROLS, CONTROL_VALIDATION)},
        "public_class_vectors": {folio: list(values) for folio, values in derived.items()},
        "C_coverage": coverage,
        "missing_page_reading_cells": missing,
        "eligible_all_reading_C_pages": eligible_pages,
        "non_C_role_inventory_on_missing_f67_pages": non_c_roles,
        "gates": gates,
        "execution_history": {
            "target_source_opened": True,
            "target_similarity_matrix_constructed": False,
            "target_score_computed": False,
            "target_result_written": False,
        },
        "claim_ceiling": "Capacity stop only: three f67 page panels have no IVTFF C loci. No editorial-class association, object, word, meaning, plaintext, or translation was scored.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Circle editorial-class phase capacity stop\n\n"
        "Status: **STOP_UNSCORED_INCOMPLETE_C_ROLE_PANEL**\n\n"
        "The frozen ten-page public class vector is correct, and the synthetic controls passed. The manuscript target cannot be scored: f67r2, f67v1, and f67v2 have zero IVTFF `C` loci in ZL3b, IT2a, and RF1b. Their text is encoded under `P`, `L`, and/or `R`; only f67r1 has circular-role material, while all six f68 panels do. Consequently f67 has no within-folio same/different `C`-profile contrast and the exact 24-phase statistic is undefined.\n\n"
        "The failed invocation opened the bound source tables but stopped before constructing a similarity matrix, computing a target score, or writing a target result. The role scope will not be changed post-target. No page-class association, object, word, meaning, plaintext, or translation was tested.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "missing_cells": len(missing), "eligible_pages": eligible_pages}, sort_keys=True))


if __name__ == "__main__":
    main()
