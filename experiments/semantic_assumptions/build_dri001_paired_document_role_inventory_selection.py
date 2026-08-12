#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
from collections import OrderedDict, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "DRI001_PAIRED_DOCUMENT_ROLE_INVENTORY_METHOD.md"
ROLES = RES / "existing_human_locus_roles.tsv"
OUT = RES / "dri001_paired_document_role_inventory_selection.json"
REPORT = RES / "dri001_paired_document_role_inventory_selection_report.md"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"

# Official Yale canvas bindings for the deterministic thirty-page panel.
# Foldout logical pages bind the exact canvas that contains the named part.
CANVAS = {
    "f68v2": ("1006197", "68v", 8135, 3843), "f67r1": ("1006194", "67r", 4972, 3738),
    "f84r": ("1006226", "84r", 2753, 3745), "f77v": ("1006213", "77v", 2861, 3697),
    "f80v": ("1006219", "80v", 2837, 3712), "f75r": ("1006208", "75r", 2852, 3759),
    "f83v": ("1006225", "83v", 2858, 3693), "f82r": ("1006222", "82r", 2753, 3745),
    "f55v": ("1006183", "55v", 2979, 3769), "f13r": ("1006098", "13r", 2601, 3723),
    "f17r": ("1006106", "17r", 2649, 3743), "f2r": ("1006078", "2r", 2691, 3770),
    "f101v": ("1006250", "101v (part)", 2698, 3779), "f100v": ("1006249", "100v and 101r", 7486, 3715),
    "f100r": ("1006248", "100r", 2676, 3756), "f102v1": ("1006252", "102v (part)", 2981, 3795),
    "f88v": ("1006233", "88v and 89r", 9078, 3777), "f89v2": ("1006235", "89v (part) and 90r", 7796, 3761),
    "f102r1": ("1006251", "101v (part) and 102r", 8176, 3864), "f88r": ("1037112", "88r", 2714, 3735),
    "f89r2": ("1006233", "88v and 89r", 9078, 3777), "f102r2": ("1006251", "101v (part) and 102r", 8176, 3864),
    "f107r": ("1006262", "107r", 2641, 3787), "f103r": ("1006254", "103r", 2688, 3805),
    "f86v5": ("1006230", "86v (part) (part of 85-86 foldout)", 4897, 3788), "f85r1": ("1006228", "85r (part) (part of 85-86 foldout)", 2775, 3745),
    "f72v3": ("1006204", "72v (part)", 5976, 3794), "f71v": ("1006203", "71v and 72r", 8865, 3018),
    "f72r2": ("1006203", "71v and 72r", 8865, 3018), "f73v": ("1006207", "73v", 2979, 3724),
}

# Conservatively disclose prior whole-canvas exposure for the full panel. The
# selection is content-independent, and no target role judgment is carried in.
PRIOR_EXPOSED = set(CANVAS)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    if page == "fRos":
        return "fRos"
    match = re.match(r"f(\d+)", page)
    if not match:
        raise ValueError(page)
    return "f" + match.group(1)


def rank_hash(section: str, template: str, page: str) -> str:
    return hashlib.sha256(f"DRI001_ROLE_PAIR_V1|{section}|{template}|{page}".encode()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    pages: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    with ROLES.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            pages.setdefault(row["page"], []).append(row)
    cells: dict[tuple[str, str], list[str]] = defaultdict(list)
    for page, rows in pages.items():
        template = "".join(kind for kind, _ in itertools.groupby(row["kind"] for row in rows))
        cells[(rows[0]["section"], template)].append(page)

    selected = []
    cell_pairs = []
    qualifying = [(cell, candidates) for cell, candidates in sorted(cells.items()) if len({physical_folio(page) for page in candidates}) >= 2]
    for cell_index, ((section, template), candidates) in enumerate(qualifying, 1):
        ranked = sorted(candidates, key=lambda page: rank_hash(section, template, page))
        chosen = []
        used_folios = set()
        for page in ranked:
            folio = physical_folio(page)
            if folio in used_folios:
                continue
            chosen.append(page)
            used_folios.add(folio)
            if len(chosen) == 2:
                break
        cell_pairs.append(tuple(chosen))
        for page in chosen:
            canvas_id, canvas_label, width, height = CANVAS[page]
            selected.append({
                "cell_index": cell_index,
                "cell_id": f"DRC{cell_index:02d}",
                "section": section,
                "kind_run_template": template,
                "page": page,
                "physical_folio": physical_folio(page),
                "selection_rank_sha256": rank_hash(section, template, page),
                "prior_full_canvas_exposure": page in PRIOR_EXPOSED,
                "canvas_id": canvas_id,
                "canvas_label": canvas_label,
                "official_dimensions": [width, height],
                "review_image_url": f"https://collections.library.yale.edu/iiif/2/{canvas_id}/full/1600,/0/default.jpg",
            })
    adjacency = defaultdict(list)
    for left, right in cell_pairs:
        adjacency[left].append((right, 1))
        adjacency[right].append((left, 1))
    by_canvas = defaultdict(list)
    for row in selected:
        by_canvas[row["canvas_id"]].append(row["page"])
    for canvas_pages in by_canvas.values():
        for index, left in enumerate(canvas_pages):
            for right in canvas_pages[index + 1:]:
                adjacency[left].append((right, 0))
                adjacency[right].append((left, 0))
    row_by_page = {row["page"]: row for row in selected}
    colour = {}
    for anchor in sorted(row_by_page, key=lambda page: row_by_page[page]["selection_rank_sha256"]):
        if anchor in colour:
            continue
        colour[anchor] = 0
        queue = deque([anchor])
        while queue:
            left = queue.popleft()
            for right, difference in adjacency[left]:
                expected = colour[left] ^ difference
                if right in colour and colour[right] != expected:
                    raise SystemExit("phase constraints are contradictory")
                if right not in colour:
                    colour[right] = expected
                    queue.append(right)
    for row in selected:
        row["phase"] = "CALIBRATION" if colour[row["page"]] == 0 else "DIAGNOSTIC"
    selected.sort(key=lambda row: (row["cell_index"], 0 if row["phase"] == "CALIBRATION" else 1))
    assert len(selected) == 30 and len({row["cell_id"] for row in selected}) == 15
    assert len({row["physical_folio"] for row in selected}) == 24
    assert all({row["phase"] for row in selected if row["cell_id"] == cell_id} == {"CALIBRATION", "DIAGNOSTIC"} for cell_id in {row["cell_id"] for row in selected})
    assert all(len({row["phase"] for row in selected if row["canvas_id"] == canvas_id}) == 1 for canvas_id in {row["canvas_id"] for row in selected})
    result = {
        "experiment": "DRI001_PAIRED_DOCUMENT_ROLE_INVENTORY_SELECTION",
        "schema": "DRI001_SELECTION_V1",
        "status": "FROZEN_FIFTEEN_CELL_THIRTY_PAGE_TWENTY_FOUR_FOLIO_PAIRED_ROLE_PANEL_BEFORE_IMAGE_ACCESS",
        "decision": "AUTHORIZE_CALIBRATION_IMAGE_ACCESS_ONLY",
        "rubric_roles": ["PROSE_DOMINANT", "OBJECT_WITH_PROSE", "REPEATED_OWNED_RECORDS", "DIAGRAM_PARAMETER_ARRAY", "MIXED_OR_UNRESOLVED"],
        "calibration_gate": {"maximum_unresolved": 3, "rubric_amendment_required": False},
        "diagnostic_gates": {"minimum_resolved_cells": 10, "minimum_role_agreements": 11, "minimum_distinct_nonunresolved_roles": 3},
        "counts": {"cells": 15, "pages": 30, "physical_folios": 24, "calibration_pages": 15, "diagnostic_pages": 15, "prior_exposed_pages": sum(row["prior_full_canvas_exposure"] for row in selected)},
        "rows": selected,
        "inputs": {str(METHOD.relative_to(ROOT)): sha256(METHOD), str(ROLES.relative_to(ROOT)): sha256(ROLES), "yale_manifest_2002046_sha256": MANIFEST_SHA},
        "access": {"selected_image_bodies_opened_by_builder": False, "transcription_surface_family_member_root_or_parser_role_opened": False, "public_page_description_prose_used": False, "ocr_clip_embedding_or_automated_vision_used": False},
        "claim_ceiling": "This freezes a diagnostic paired page-role inventory inside exact section and editorial-kind-run cells. Cross-cell folio reuse prevents treating the fifteen cells as independent. It cannot confirm a manuscript-wide document class or establish a heading caption field name class name word POS sound language cipher plaintext meaning or translation.",
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# DRI001 paired document-role inventory selection\n\n"
        "Status: **FROZEN_FIFTEEN_CELL_THIRTY_FOLIO_PAIRED_ROLE_PANEL_BEFORE_IMAGE_ACCESS**.\n\n"
        "A source-only deterministic rule retains every section × exact editorial-kind-run cell represented on at least two physical folios and selects two different-folio pages by hash order. The panel has 15 cells, 30 logical pages, and 24 physical folios; cross-cell reuse is explicit. Deterministic graph colouring keeps each pair in opposite phases while keeping logical pages on the same official foldout canvas in one phase.\n\n"
        "Only the 15 calibration images may now be inspected under the frozen five-role source-native rubric. No selected page image, transcription identity, formal filler, public description prose, or semantic feature entered selection. The old DOCUMENT_ROLE_ANNOTATION_V2 viewer is provenance-lost; this is a new versioned replacement.\n"
    )


if __name__ == "__main__":
    main()
