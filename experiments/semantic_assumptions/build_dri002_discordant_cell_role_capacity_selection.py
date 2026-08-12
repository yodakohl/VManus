#!/usr/bin/env python3
"""Freeze every unjudged page in DRI001's two discordant layout cells."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "DRI002_DISCORDANT_CELL_ROLE_CAPACITY_METHOD.md"
ROLES = RES / "existing_human_locus_roles.tsv"
DRI_SELECTION = RES / "dri001_paired_document_role_inventory_selection.json"
DRI_RESULT = RES / "dri001_paired_document_role_inventory_result.json"
OUT = RES / "dri002_discordant_cell_role_capacity_selection.json"
REPORT = RES / "dri002_discordant_cell_role_capacity_selection_report.md"

CANVAS = {
    "f77r": ("1006212", 2793, 3752),
    "f78r": ("1006214", 2793, 3761),
    "f82v": ("1006223", 2821, 3709),
    "f76v": ("1006211", 2823, 3712),
    "f78v": ("1006215", 2841, 3706),
    "f79r": ("1006216", 2784, 3755),
    "f79v": ("1006217", 2811, 3714),
    "f81r": ("1006220", 2776, 3737),
    "f84v": ("1006227", 2838, 3697),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.match(r"f(\d+)", page)
    if not match:
        raise ValueError(page)
    return "f" + match.group(1)


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    dri_selection = json.loads(DRI_SELECTION.read_text())
    dri_result = json.loads(DRI_RESULT.read_text())
    discordant_ids = [row["cell_id"] for row in dri_result["cells"] if not row["role_agreement"]]
    if discordant_ids != ["DRC02", "DRC03"]:
        raise SystemExit(discordant_ids)
    cell_key = {}
    for row in dri_selection["rows"]:
        if row["cell_id"] in discordant_ids:
            key = (row["section"], row["kind_run_template"])
            if row["cell_id"] in cell_key and cell_key[row["cell_id"]] != key:
                raise SystemExit("cell key mismatch")
            cell_key[row["cell_id"]] = key
    already_selected = {row["page"] for row in dri_selection["rows"]}
    pages: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    with ROLES.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            pages.setdefault(row["page"], []).append(row)
    candidates = defaultdict(list)
    for page, rows in pages.items():
        template = "".join(kind for kind, _ in itertools.groupby(row["kind"] for row in rows))
        key = (rows[0]["section"], template)
        for cell_id, wanted in cell_key.items():
            if key == wanted and page not in already_selected:
                candidates[cell_id].append(page)
    if dict(candidates) != {
        "DRC02": ["f77r", "f78r", "f82v"],
        "DRC03": ["f76v", "f78v", "f79r", "f79v", "f81r", "f84v"],
    }:
        raise SystemExit(dict(candidates))
    rows = []
    for cell_id in discordant_ids:
        section, template = cell_key[cell_id]
        for page in candidates[cell_id]:
            canvas_id, width, height = CANVAS[page]
            rows.append({
                "cell_id": cell_id,
                "section": section,
                "kind_run_template": template,
                "page": page,
                "physical_folio": physical_folio(page),
                "canvas_id": canvas_id,
                "official_dimensions": [width, height],
                "review_image_url": f"https://collections.library.yale.edu/iiif/2/{canvas_id}/full/1600,/0/default.jpg",
                "prior_full_canvas_exposure_disclosed": True,
            })
    result = {
        "experiment": "DRI002_DISCORDANT_CELL_ROLE_CAPACITY_SELECTION",
        "schema": "DRI002_SELECTION_V1",
        "status": "FROZEN_ALL_NINE_UNJUDGED_PAGES_IN_TWO_DISCORDANT_CELLS",
        "decision": "AUTHORIZE_COMPLETE_NINE_PAGE_NATIVE_VISUAL_CAPACITY_CENSUS",
        "discordant_cells": discordant_ids,
        "counts": {
            "cells": 2,
            "selected_pages": len(rows),
            "selected_physical_folios": len({row["physical_folio"] for row in rows}),
            "pages_by_cell": {cell_id: len(candidates[cell_id]) for cell_id in discordant_ids},
        },
        "rows": rows,
        "rubric_roles": dri_selection["rubric_roles"],
        "capacity_gate": "BOTH_CELLS_REQUIRE_AT_LEAST_TWO_NONUNRESOLVED_ROLES_EACH_ON_AT_LEAST_TWO_PHYSICAL_FOLIOS",
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha256(METHOD),
            str(ROLES.relative_to(ROOT)): sha256(ROLES),
            str(DRI_SELECTION.relative_to(ROOT)): sha256(DRI_SELECTION),
            str(DRI_RESULT.relative_to(ROOT)): sha256(DRI_RESULT),
        },
        "access": {
            "iiif_info_metadata_opened_for_canvas_binding": True,
            "selected_image_bodies_opened_by_builder": False,
            "prior_full_canvas_exposure_disclosed_for_all_pages": True,
            "transcription_surface_family_member_root_or_parser_role_opened": False,
            "ocr_clip_embedding_or_automated_vision_used": False,
        },
        "claim_ceiling": "This freezes every unjudged page in the two DRI001-discordant exact section and kind-run cells for a complete native-visual role-capacity census. It establishes no text association and no heading caption field class name word POS sound language cipher plaintext meaning or translation.",
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# DRI002 discordant-cell role-capacity selection\n\n"
        "Status: **FROZEN_ALL_NINE_UNJUDGED_PAGES_IN_TWO_DISCORDANT_CELLS**.\n\n"
        "The complete source-only rule retains all three remaining pages in DRC02 "
        "(section B, `LPL`) and all six remaining pages in DRC03 (section B, `P`): "
        "nine pages on seven physical folios. No ranking or favorable sampling is used. "
        "All exact Yale canvases are bound before new target inspection.\n\n"
        "Continue to formal scoring only if both cells independently contain at least two "
        "non-unresolved roles supported on at least two physical folios each after combining "
        "these judgments with DRI001. No text association or translation follows from selection.\n"
    )


if __name__ == "__main__":
    main()
