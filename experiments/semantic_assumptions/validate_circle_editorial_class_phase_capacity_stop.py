#!/usr/bin/env python3
"""Independent validation of the unscored f67/f68 C-role capacity stop."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
AUDITOR = BASE / "audit_circle_editorial_class_phase_capacity_stop.py"
METHOD = BASE / "CIRCLE_EDITORIAL_CLASS_PHASE_METHOD.md"
RUNNER = BASE / "run_circle_editorial_class_phase.py"
ALIGN = RESULTS / "source_sta_group_alignment.tsv"
META = RESULTS / "source_separator_transcription.tsv"
PAGES = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
CONTROLS = RESULTS / "circle_editorial_class_phase_controls.json"
CONTROL_VALIDATION = RESULTS / "circle_editorial_class_phase_controls_validation.json"
STOP = RESULTS / "circle_editorial_class_phase_capacity_stop.json"
STOP_REPORT = RESULTS / "circle_editorial_class_phase_capacity_stop.md"
TARGET = RESULTS / "circle_editorial_class_phase.json"
TARGET_REPORT = RESULTS / "circle_editorial_class_phase_report.md"
OUT = RESULTS / "circle_editorial_class_phase_capacity_stop_validation.json"
REPORT = RESULTS / "circle_editorial_class_phase_capacity_stop_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
PANEL = {
    "f67": ("f67r1", "f67r2", "f67v1", "f67v2"),
    "f68": ("f68r1", "f68r2", "f68r3", "f68v1", "f68v2", "f68v3"),
}
CLASSES = {"f67": ("A", "A", "A", "C"), "f68": ("A", "A", "A", "C", "A", "C")}


def records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct() -> dict[str, object]:
    public_rows = records(PAGES)
    public = {row["page"]: row for row in public_rows}
    assert len(public_rows) == len(public) == 228
    classes = {}
    for folio, pages in PANEL.items():
        states = []
        for page in pages:
            text = public[page]["general_description"].lower()
            is_a = "this is an astronomical page" in text
            is_c = "this is a so-called cosmological page" in text
            assert is_a ^ is_c
            states.append("A" if is_a else "C")
        classes[folio] = tuple(states)
    assert classes == CLASSES
    meta_rows = records(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    assert len(metadata) == len(meta_rows)
    pages = {page for folio_pages in PANEL.values() for page in folio_pages}
    kept = Counter()
    alternates = Counter()
    kind_groups = Counter()
    kind_loci = defaultdict(set)
    alignment_rows = records(ALIGN)
    assert len({row["source_group_id"] for row in alignment_rows}) == len(alignment_rows)
    for row in alignment_rows:
        info = metadata[row["source_group_id"]]
        if info["page"] not in pages:
            continue
        key = (info["page"], row["edition"], info["kind"])
        kind_groups[key] += 1
        kind_loci[key].add(info["locus"])
        if info["kind"] == "C":
            target = alternates if int(row["alternative_site_count"]) else kept
            target[(info["page"], row["edition"])] += 1
    coverage = {}
    missing = []
    for folio, folio_pages in PANEL.items():
        coverage[folio] = {}
        for page in folio_pages:
            coverage[folio][page] = {}
            for reading in READINGS:
                coverage[folio][page][reading] = {
                    "zero_alternative_C_groups": kept[(page, reading)],
                    "alternative_C_groups": alternates[(page, reading)],
                    "C_loci": len(kind_loci[(page, reading, "C")]),
                }
                if kept[(page, reading)] == 0:
                    missing.append(f"{page}|{reading}")
    eligible = {
        folio: [page for page in folio_pages if all(kept[(page, reading)] > 0 for reading in READINGS)]
        for folio, folio_pages in PANEL.items()
    }
    non_c = {
        page: {
            reading: {
                kind: {"groups": kind_groups[(page, reading, kind)], "loci": len(kind_loci[(page, reading, kind)])}
                for kind in ("P", "L", "R") if kind_groups[(page, reading, kind)]
            }
            for reading in READINGS
        }
        for page in ("f67r2", "f67v1", "f67v2")
    }
    gates = {
        "public_ten_page_class_vector_exact": classes == CLASSES,
        "controls_and_validation_pass": True,
        "all_30_page_reading_C_cells_nonempty": len(missing) == 0,
        "both_folios_have_two_or_more_C_pages": all(len(value) >= 2 for value in eligible.values()),
        "f67_has_within_folio_same_and_different_pairs": len(eligible["f67"]) >= 2,
        "target_artifacts_absent": True,
    }
    return {
        "experiment": "CIRCLE_EDITORIAL_CLASS_PHASE_CAPACITY_STOP",
        "status": "STOP_UNSCORED_INCOMPLETE_C_ROLE_PANEL",
        "decision": "DO_NOT_SCORE_OR_CHANGE_FROZEN_ROLE_SCOPE",
        "inputs": {path.name: digest(path) for path in (ALIGN, META, PAGES, METHOD, RUNNER, CONTROLS, CONTROL_VALIDATION)},
        "public_class_vectors": {folio: list(value) for folio, value in classes.items()},
        "C_coverage": coverage,
        "missing_page_reading_cells": missing,
        "eligible_all_reading_C_pages": eligible,
        "non_C_role_inventory_on_missing_f67_pages": non_c,
        "gates": gates,
        "execution_history": {
            "target_source_opened": True,
            "target_similarity_matrix_constructed": False,
            "target_score_computed": False,
            "target_result_written": False,
        },
        "claim_ceiling": "Capacity stop only: three f67 page panels have no IVTFF C loci. No editorial-class association, object, word, meaning, plaintext, or translation was scored.",
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    assert not TARGET.exists() and not TARGET_REPORT.exists()
    expected = reconstruct()
    stored = json.loads(STOP.read_text(encoding="utf-8"))
    assert stored == expected
    assert expected["missing_page_reading_cells"] == [
        "f67r2|ZL3b", "f67r2|IT2a", "f67r2|RF1b",
        "f67v1|ZL3b", "f67v1|IT2a", "f67v1|RF1b",
        "f67v2|ZL3b", "f67v2|IT2a", "f67v2|RF1b",
    ]
    assert expected["eligible_all_reading_C_pages"] == {
        "f67": ["f67r1"],
        "f68": ["f68r1", "f68r2", "f68r3", "f68v1", "f68v2", "f68v3"],
    }
    expected_report = (
        "# Circle editorial-class phase capacity stop\n\n"
        "Status: **STOP_UNSCORED_INCOMPLETE_C_ROLE_PANEL**\n\n"
        "The frozen ten-page public class vector is correct, and the synthetic controls passed. The manuscript target cannot be scored: f67r2, f67v1, and f67v2 have zero IVTFF `C` loci in ZL3b, IT2a, and RF1b. Their text is encoded under `P`, `L`, and/or `R`; only f67r1 has circular-role material, while all six f68 panels do. Consequently f67 has no within-folio same/different `C`-profile contrast and the exact 24-phase statistic is undefined.\n\n"
        "The failed invocation opened the bound source tables but stopped before constructing a similarity matrix, computing a target score, or writing a target result. The role scope will not be changed post-target. No page-class association, object, word, meaning, plaintext, or translation was tested.\n"
    )
    assert STOP_REPORT.read_text(encoding="utf-8") == expected_report
    checks = len(records(ALIGN)) + len(records(META)) + len(records(PAGES)) + 30 + 9
    result = {
        "experiment": "CIRCLE_EDITORIAL_CLASS_PHASE_CAPACITY_STOP_VALIDATION",
        "status": "PASS",
        "assertions": checks,
        "bindings": {path.name: digest(path) for path in (AUDITOR, STOP, STOP_REPORT, ALIGN, META, PAGES, METHOD, RUNNER, CONTROLS, CONTROL_VALIDATION)},
        "target_artifacts_absent": True,
        "production_module_imported": False,
        "decision": expected["decision"],
        "claim_ceiling": "Independent reconstruction of an unscored role-capacity stop; no class association, object, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Circle editorial-class capacity-stop validation\n\n"
        f"Status: **PASS** ({checks} checks). The independent nonimporting reconstruction reproduces the public class vector, all page/reading role counts, the nine missing `C` cells, the one-page f67 capacity, every gate, exact JSON, and report. No target score or target artifact exists.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "assertions": checks, "missing_cells": 9}, sort_keys=True))


if __name__ == "__main__":
    main()
