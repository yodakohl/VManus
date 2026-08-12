#!/usr/bin/env python3
"""Serialize the frozen nine-page DRI002 native-visual capacity census."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "DRI002_DISCORDANT_CELL_ROLE_CAPACITY_METHOD.md"
SELECTION = RES / "dri002_discordant_cell_role_capacity_selection.json"
SELECTION_VALIDATION = RES / "dri002_discordant_cell_role_capacity_selection_validation.json"
DRI_RESULT = RES / "dri001_paired_document_role_inventory_result.json"
OUT = RES / "dri002_discordant_cell_role_capacity_result.json"
REPORT = RES / "dri002_discordant_cell_role_capacity_result_report.md"

OBSERVATIONS = {
    "f77r": ("OBJECT_WITH_PROSE", "LOW", "f0c6536d5890e14b5ee30ffd5d58113b0028848cea883f0ed0b3915759007488", True, True, True, False, False,
             "Two large prose blocks coexist with a connected painted apparatus and several human-form units; nearby short inscriptions lack repeated singular owner devices."),
    "f78r": ("OBJECT_WITH_PROSE", "LOW", "519b6459060688d15eecab426795ddfb4bb1faf113902939872ea77e04d34ab1", True, True, True, False, False,
             "A long connected painted apparatus and two large communal figure pools interrupt several continuous prose blocks; no repeated singular inscription assignment is visible."),
    "f82v": ("OBJECT_WITH_PROSE", "LOW", "e26766c5ba18e373ff518ae1a25a2158352632c348a2a81a958019b88c3d358e", True, True, True, False, False,
             "Many separated painted figure-apparatus constructions and a large lower pool surround a dominant continuous prose field; labels rely on open proximity rather than repeated singular devices."),
    "f76v": ("PROSE_DOMINANT", "LOW", "8e801028e741a516c1507037c8415c24e0e9643289348876b1169c0613d2ec2a", True, False, True, False, False,
             "Continuous prose blocks occupy almost the whole page. Small separated marginal figure-apparatus units do not form one dominant illustration or a repeated owned-record system."),
    "f78v": ("OBJECT_WITH_PROSE", "LOW", "62e8dc7fdb8565a2b9f672869d7daf311d5033439a5f2fe95335ce0c25090eea", True, True, True, False, False,
             "A large painted communal figure pool divides two continuous prose blocks and dominates the middle field; there are no repeated singular inscription slots."),
    "f79r": ("OBJECT_WITH_PROSE", "LOW", "925dca406dd52dd24d21a7e2292ee97035a5a707f01cee7dbb2dc2ca0d620285", True, True, True, False, False,
             "A sequence of large linked painted human-apparatus constructions occupies the left and lower fields beside continuous prose; no repeated singular owner system is visible."),
    "f79v": ("OBJECT_WITH_PROSE", "LOW", "328bc1dd1edbff1634ca744de3e27245df5b515e15e7dc6afdb5df26fda7c726", True, True, True, False, False,
             "A tall painted channel with several human-form units and a large lower pool shares the page with continuous prose blocks; no singular caption array controls the layout."),
    "f81r": ("OBJECT_WITH_PROSE", "LOW", "7d045945fc268dd5880803ad7813384e2965e37b49f7a91fb2f70638e6423c09", True, True, True, False, False,
             "Two large communal painted figure pools frame a substantial continuous prose block and occupy much of the page; no repeated singular inscription ownership is visible."),
    "f84v": ("OBJECT_WITH_PROSE", "LOW", "6755a38ae11ece31d16baab87942aadc925ed29720eda8de8b855b86d0c4a72a", True, True, True, False, False,
             "Two large painted communal figure pools interrupt continuous prose fields; the nearby short writing is openly placed and does not make repeated singular owner records."),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    dri = json.loads(DRI_RESULT.read_text())
    if [x["page"] for x in selection["rows"]] != list(OBSERVATIONS):
        raise SystemExit("observation order mismatch")
    observations = []
    for selected in selection["rows"]:
        page = selected["page"]
        role, uncertainty, image_sha, prose, illustration, repeated, singular, diagram, basis = OBSERVATIONS[page]
        observations.append({
            "cell_id": selected["cell_id"], "page": page, "physical_folio": selected["physical_folio"],
            "canvas_id": selected["canvas_id"], "review_image_url": selected["review_image_url"],
            "review_image_sha256": image_sha, "role": role, "uncertainty": uncertainty,
            "machine_authored_native_visual_judgment": True,
            "evidence": {"continuous_prose_block": prose, "dominant_illustration": illustration,
                         "repeated_object_or_cell_template": repeated, "singular_ownership_devices": singular,
                         "diagram_defined_slots": diagram},
            "visible_basis": basis,
        })
    old_by_cell = defaultdict(list)
    for row in dri["cells"]:
        if row["cell_id"] in selection["discordant_cells"]:
            old_by_cell[row["cell_id"]].extend([
                {"page": row["calibration_page"], "physical_folio": "f" + row["calibration_page"][1:].split("r")[0].split("v")[0], "role": row["calibration_role"], "source": "DRI001"},
                {"page": row["diagnostic_page"], "physical_folio": "f" + row["diagnostic_page"][1:].split("r")[0].split("v")[0], "role": row["diagnostic_role"], "source": "DRI001"},
            ])
    cells = []
    for cell_id in selection["discordant_cells"]:
        combined = old_by_cell[cell_id] + [
            {"page": x["page"], "physical_folio": x["physical_folio"], "role": x["role"], "source": "DRI002"}
            for x in observations if x["cell_id"] == cell_id
        ]
        folios_by_role = defaultdict(set)
        for x in combined:
            if x["role"] != "MIXED_OR_UNRESOLVED":
                folios_by_role[x["role"]].add(x["physical_folio"])
        supported = {role: sorted(folios) for role, folios in folios_by_role.items() if len(folios) >= 2}
        passes = len(supported) >= 2
        cells.append({"cell_id": cell_id, "combined_pages": combined,
                      "physical_folios_by_role": {k: sorted(v) for k, v in sorted(folios_by_role.items())},
                      "roles_with_at_least_two_folios": supported, "passes_role_mobility_gate": passes})
    all_pass = all(x["passes_role_mobility_gate"] for x in cells)
    if all_pass:
        raise SystemExit("unexpected capacity pass")
    result = {
        "experiment": "DRI002_DISCORDANT_CELL_ROLE_CAPACITY_RESULT",
        "schema": "DRI002_RESULT_V1",
        "status": "STOP_ONE_OF_TWO_CELLS_LACKS_REPLICATED_ROLE_MOBILITY",
        "decision": "DO_NOT_OPEN_OR_SCORE_FORMAL_ROLE_ASSOCIATION",
        "observations": observations,
        "new_role_counts": {role: sum(x["role"] == role for x in observations) for role in ["PROSE_DOMINANT", "OBJECT_WITH_PROSE", "REPEATED_OWNED_RECORDS", "DIAGRAM_PARAMETER_ARRAY", "MIXED_OR_UNRESOLVED"]},
        "cells": cells,
        "gates": {"DRC02_replicated_role_mobility": cells[0]["passes_role_mobility_gate"],
                  "DRC03_replicated_role_mobility": cells[1]["passes_role_mobility_gate"],
                  "both_cells_pass": all_pass},
        "inputs": {str(p.relative_to(ROOT)): sha256(p) for p in (METHOD, SELECTION, SELECTION_VALIDATION, DRI_RESULT)},
        "access": {"all_nine_selected_images_opened": True, "official_source_native_pixels_used": True,
                   "machine_authored_native_visual_judgments": True, "ocr_clip_embedding_or_automated_vision_used": False,
                   "transcription_identity_or_formal_features_opened_after_selection": False,
                   "structural_or_semantic_association_scored": False},
        "claim_ceiling": "One of two exact section and editorial-kind-run cells lacks two visible roles each supported on two physical folios, so no formal role association is authorized. The census establishes no heading caption field class name word POS sound language cipher plaintext meaning or translation.",
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# DRI002 discordant-cell role-capacity result\n\n"
        "Status: **STOP_ONE_OF_TWO_CELLS_LACKS_REPLICATED_ROLE_MOBILITY**.\n\n"
        "The complete nine-page native-visual census yields one `PROSE_DOMINANT` and eight "
        "`OBJECT_WITH_PROSE` judgments, all at low uncertainty. After combining DRI001 and "
        "DRI002, DRC03 passes: `PROSE_DOMINANT` occurs on f76 and f80, while "
        "`OBJECT_WITH_PROSE` occurs on f75, f78, f79, f81, and f84. DRC02 fails: "
        "`OBJECT_WITH_PROSE` occurs on f77, f78, and f82, but `REPEATED_OWNED_RECORDS` occurs "
        "only on f84. The frozen rule required both cells to pass.\n\n"
        "Stop before every transcription identity or formal role feature. The result neither "
        "tests nor establishes a heading, caption, field, class name, word, POS, sound, "
        "language, cipher, plaintext, meaning, or translation.\n"
    )


if __name__ == "__main__":
    main()
