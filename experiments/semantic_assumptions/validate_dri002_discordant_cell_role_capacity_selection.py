#!/usr/bin/env python3
"""Independent compact validation of DRI002's source-only selection."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "DRI002_DISCORDANT_CELL_ROLE_CAPACITY_METHOD.md"
ROLES = RES / "existing_human_locus_roles.tsv"
DRI_SELECTION = RES / "dri001_paired_document_role_inventory_selection.json"
DRI_RESULT = RES / "dri001_paired_document_role_inventory_result.json"
PRODUCER = BASE / "build_dri002_discordant_cell_role_capacity_selection.py"
RESULT = RES / "dri002_discordant_cell_role_capacity_selection.json"
REPORT = RES / "dri002_discordant_cell_role_capacity_selection_report.md"
OUT = RES / "dri002_discordant_cell_role_capacity_selection_validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    r = json.loads(RESULT.read_text())
    ds = json.loads(DRI_SELECTION.read_text())
    dr = json.loads(DRI_RESULT.read_text())
    pages: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    with ROLES.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            pages.setdefault(row["page"], []).append(row)
    discordant = [x["cell_id"] for x in dr["cells"] if not x["role_agreement"]]
    cell_keys = {}
    for row in ds["rows"]:
        if row["cell_id"] in discordant:
            cell_keys[row["cell_id"]] = (row["section"], row["kind_run_template"])
    used = {x["page"] for x in ds["rows"]}
    expected = {cell_id: [] for cell_id in discordant}
    for page, rows in pages.items():
        key = (rows[0]["section"], "".join(k for k, _ in itertools.groupby(x["kind"] for x in rows)))
        for cell_id, wanted in cell_keys.items():
            if key == wanted and page not in used:
                expected[cell_id].append(page)
    observed = {cell_id: [x["page"] for x in r["rows"] if x["cell_id"] == cell_id] for cell_id in discordant}
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "source_inputs_bound": r["inputs"] == {
            str(METHOD.relative_to(ROOT)): sha256(METHOD),
            str(ROLES.relative_to(ROOT)): sha256(ROLES),
            str(DRI_SELECTION.relative_to(ROOT)): sha256(DRI_SELECTION),
            str(DRI_RESULT.relative_to(ROOT)): sha256(DRI_RESULT),
        },
        "two_published_discordant_cells": discordant == r["discordant_cells"] == ["DRC02", "DRC03"],
        "complete_remaining_page_sets": expected == observed == {
            "DRC02": ["f77r", "f78r", "f82v"],
            "DRC03": ["f76v", "f78v", "f79r", "f79v", "f81r", "f84v"],
        },
        "nine_pages_seven_folios": r["counts"] == {"cells": 2, "pages_by_cell": {"DRC02": 3, "DRC03": 6}, "selected_pages": 9, "selected_physical_folios": 7},
        "exact_canvas_bindings": [(x["page"], x["canvas_id"], x["official_dimensions"]) for x in r["rows"]] == [
            ("f77r", "1006212", [2793, 3752]), ("f78r", "1006214", [2793, 3761]), ("f82v", "1006223", [2821, 3709]),
            ("f76v", "1006211", [2823, 3712]), ("f78v", "1006215", [2841, 3706]), ("f79r", "1006216", [2784, 3755]),
            ("f79v", "1006217", [2811, 3714]), ("f81r", "1006220", [2776, 3737]), ("f84v", "1006227", [2838, 3697]),
        ],
        "sealed_visual_and_formal_access": r["access"]["selected_image_bodies_opened_by_builder"] is False and r["access"]["transcription_surface_family_member_root_or_parser_role_opened"] is False,
        "all_prior_exposure_disclosed": all(x["prior_full_canvas_exposure_disclosed"] is True for x in r["rows"]),
        "fixed_capacity_gate_and_ceiling": r["capacity_gate"].startswith("BOTH_CELLS_REQUIRE") and "translation" in r["claim_ceiling"],
        "report_present": REPORT.is_file() and "nine pages on seven physical folios" in REPORT.read_text(),
    }
    if not all(checks.values()):
        raise SystemExit({k: v for k, v in checks.items() if not v})
    out = {
        "experiment": "DRI002_DISCORDANT_CELL_ROLE_CAPACITY_SELECTION_VALIDATION",
        "schema": "DRI002_SELECTION_VALIDATION_V1",
        "status": "PASS_10_CHECK_COMPLETE_SOURCE_ONLY_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": list(checks),
        "producer_sha256": sha256(PRODUCER),
        "validated_result_sha256": sha256(RESULT),
        "reconstructed": {"cells": discordant, "pages_by_cell": expected, "pages": 9, "physical_folios": 7},
        "claim_ceiling": "Validation authorizes only the complete nine-page visual capacity census and supplies no text association word meaning plaintext or translation.",
    }
    OUT.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
