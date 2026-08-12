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
RESULT = RES / "dri001_paired_document_role_inventory_selection.json"
OUT = RES / "dri001_paired_document_role_inventory_selection_validation.json"
REPORT = RES / "dri001_paired_document_role_inventory_selection_validation_report.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    if page == "fRos":
        return "fRos"
    return "f" + re.match(r"f(\d+)", page).group(1)


def rank_hash(section: str, template: str, page: str) -> str:
    return hashlib.sha256(f"DRI001_ROLE_PAIR_V1|{section}|{template}|{page}".encode()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    stored = json.loads(RESULT.read_text())
    pages: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    with ROLES.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            pages.setdefault(row["page"], []).append(row)
    cells = defaultdict(list)
    for page, rows in pages.items():
        template = "".join(kind for kind, _ in itertools.groupby(row["kind"] for row in rows))
        cells[(rows[0]["section"], template)].append(page)
    expected_pairs = []
    for section, template in sorted(cells):
        candidates = cells[(section, template)]
        if len({folio(page) for page in candidates}) < 2:
            continue
        chosen = []
        for page in sorted(candidates, key=lambda value: rank_hash(section, template, value)):
            if folio(page) in {folio(value) for value in chosen}:
                continue
            chosen.append(page)
            if len(chosen) == 2:
                break
        expected_pairs.append((section, template, chosen))
    rows = stored["rows"]
    reconstructed = [(section, template, set(chosen)) for section, template, chosen in expected_pairs]
    observed = []
    for index in range(0, len(rows), 2):
        pair = rows[index:index + 2]
        observed.append((pair[0]["section"], pair[0]["kind_run_template"], {row["page"] for row in pair}))
    adjacency = defaultdict(list)
    for _, _, chosen in expected_pairs:
        left, right = chosen
        adjacency[left].append((right, 1)); adjacency[right].append((left, 1))
    by_canvas = defaultdict(list)
    for row in rows:
        by_canvas[row["canvas_id"]].append(row["page"])
    for canvas_pages in by_canvas.values():
        for index, left in enumerate(canvas_pages):
            for right in canvas_pages[index + 1:]:
                adjacency[left].append((right, 0)); adjacency[right].append((left, 0))
    stored_by_page = {row["page"]: row for row in rows}
    colour = {}
    for anchor in sorted(stored_by_page, key=lambda page: rank_hash(stored_by_page[page]["section"], stored_by_page[page]["kind_run_template"], page)):
        if anchor in colour: continue
        colour[anchor] = 0; queue = deque([anchor])
        while queue:
            left = queue.popleft()
            for right, difference in adjacency[left]:
                expected = colour[left] ^ difference
                if right in colour and colour[right] != expected: raise SystemExit("phase contradiction")
                if right not in colour: colour[right] = expected; queue.append(right)
    checks = {
        "canonical": RESULT.read_bytes() == (json.dumps(stored, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "source_bindings": stored["inputs"][str(METHOD.relative_to(ROOT))] == sha256(METHOD) and stored["inputs"][str(ROLES.relative_to(ROOT))] == sha256(ROLES),
        "complete_cell_reconstruction": observed == reconstructed and len(observed) == 15,
        "exact_hash_selection": all(row["selection_rank_sha256"] == rank_hash(row["section"], row["kind_run_template"], row["page"]) for row in rows),
        "phase_and_folio_separation": all([row["phase"] for row in rows[index:index + 2]] == ["CALIBRATION", "DIAGNOSTIC"] and len({row["physical_folio"] for row in rows[index:index + 2]}) == 2 for index in range(0, 30, 2)),
        "foldout_phase_seal": all(len({row["phase"] for row in rows if row["canvas_id"] == canvas_id}) == 1 for canvas_id in {row["canvas_id"] for row in rows}) and all(row["phase"] == ("CALIBRATION" if colour[row["page"]] == 0 else "DIAGNOSTIC") for row in rows),
        "panel_counts": stored["counts"]["cells"] == 15 and stored["counts"]["pages"] == 30 and stored["counts"]["physical_folios"] == 24 and len(rows) == 30 and len({row["physical_folio"] for row in rows}) == 24,
        "official_witness_fields": all(row["canvas_id"].isdigit() and row["review_image_url"].startswith(f"https://collections.library.yale.edu/iiif/2/{row['canvas_id']}/") and len(row["official_dimensions"]) == 2 for row in rows),
        "access_seal": stored["access"] == {"selected_image_bodies_opened_by_builder": False, "transcription_surface_family_member_root_or_parser_role_opened": False, "public_page_description_prose_used": False, "ocr_clip_embedding_or_automated_vision_used": False},
        "rubric_and_gates": len(stored["rubric_roles"]) == 5 and stored["calibration_gate"] == {"maximum_unresolved": 3, "rubric_amendment_required": False} and stored["diagnostic_gates"] == {"minimum_resolved_cells": 10, "minimum_role_agreements": 11, "minimum_distinct_nonunresolved_roles": 3},
        "ceiling": all(term in stored["claim_ceiling"] for term in ("diagnostic", "cannot confirm", "translation")),
    }
    if not all(checks.values()):
        raise SystemExit([name for name, value in checks.items() if not value])
    value = {"experiment": "DRI001_SELECTION_VALIDATION", "schema": "DRI001_SELECTION_VALIDATION_V1", "status": "PASS_11_CHECK_SOURCE_ONLY_PAIRED_PANEL_AND_FOLDOUT_SEAL_RECONSTRUCTION", "source_result_sha256": sha256(RESULT), "check_count": len(checks), "checks": checks, "claim_ceiling": stored["claim_ceiling"]}
    OUT.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text("# DRI001 selection validation\n\nStatus: **PASS_11_CHECK_SOURCE_ONLY_PAIRED_PANEL_AND_FOLDOUT_SEAL_RECONSTRUCTION**.\n\nIndependent compact code reconstructs all 15 repeated section × exact kind-run cells, deterministic different-folio hash pairs, graph-coloured phases, the no-cross-phase shared-canvas seal, 30-page/24-folio counts and cross-cell reuse, witness fields, rubric, gates, access seal, canonical bytes, and ceiling. It opens no selected image or transcription content.\n")


if __name__ == "__main__":
    main()
