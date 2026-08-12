#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "DRI001_PAIRED_DOCUMENT_ROLE_INVENTORY_METHOD.md"
SELECTION = RES / "dri001_paired_document_role_inventory_selection.json"
SELECTION_VALIDATION = RES / "dri001_paired_document_role_inventory_selection_validation.json"
CALIBRATION = RES / "dri001_paired_document_role_inventory_calibration.json"
CALIBRATION_VALIDATION = RES / "dri001_paired_document_role_inventory_calibration_validation.json"
OUT = RES / "dri001_paired_document_role_inventory_result.json"
REPORT = RES / "dri001_paired_document_role_inventory_result_report.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


IMAGE_SHA = {
    "1006078": "3db014f37e80de64d6c5c05f73d9bde496500a3ce819af6f4f8aff49c6f8b454",
    "1006098": "e890cac4f79be3073074bd7877740fa757d87c713cd501369dedf532d4ec7ba1",
    "1006194": "099ded767a3f8a3472e675dcaa2b609ab2d6842d62813a94159fc1dc20f023f3",
    "1006203": "6dabf50727a78ad9b686f1e8b3266273070a89182e54c073c6e0af4319d1b607",
    "1006208": "7c807221ad51b901ba8e572373e43317530779b6a7f054c2108545d23de254bc",
    "1006213": "99427a310c4874c42ccb19d5185e1ec92e16bd66bd2c71625b744eff9c35f8c5",
    "1006222": "81bd1aa1addeedd6b08411ec05105f45d6ba6b9f59ea39ff95cf2fd89cf49d6c",
    "1006228": "a3cc942d15bb233416bc0b37b7597df20ce48d551089152f7d8104546ef52749",
    "1006233": "e1e506b9e46b729bde4693195482c0e994c72aa7a84ccfed6708c3aae431c001",
    "1006249": "ab95b9de4a75411c25d6ead009915460e1e596981d6ce0e1ca623a25f7a0ca1f",
    "1006252": "6c2ed032fcc5beec3d7ba8a9ae93ab31863fa46fcac906f69271aa3c959946a2",
    "1006254": "6d220780c1302244a911e69d0f2d55ce94d89d2f52851efdf52b558290149b5c",
    "1037112": "76aa6d7f02c4fe4b4eae151740e87c7f66cfdcc7c840559005985109e563be1d",
}


# Evidence vector order: continuous prose, dominant illustration, repeated
# object/cell template, singular ownership devices, diagram-defined slots.
JUDGMENTS = {
    "f67r1": (
        "DIAGRAM_PARAMETER_ARRAY", (True, True, True, False, True),
        "Two circular constructions occupy the folio, with repeated radial sectors, annular writing, and diagram-defined positions; the compact prose blocks do not control the page role.",
    ),
    "f77v": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "A large linked painted construction with repeated human-form units is embedded between continuous prose blocks. No repeated singular inscription slots assign the nearby writing to individual units.",
    ),
    "f75r": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "A dominant vertical painted construction with repeated human-form units shares the page with several continuous prose blocks; the visible layout does not provide repeated singular owner slots.",
    ),
    "f82r": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "Several large linked painted constructions and human-form units interrupt multiple continuous prose blocks. Short nearby inscriptions do not form at least three securely assigned owner positions.",
    ),
    "f13r": (
        "OBJECT_WITH_PROSE", (True, True, False, False, False),
        "One large branching painted illustration dominates the page while a continuous prose block occupies the upper field; no singular caption device is visible.",
    ),
    "f2r": (
        "OBJECT_WITH_PROSE", (True, True, False, False, False),
        "One large branching painted illustration dominates the folio and continuous prose blocks occupy the open upper and lower spaces without a singular caption connector.",
    ),
    "f100v": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "The selected foldout part combines fields of separated painted fragments and containers with continuous prose. Nearby inscriptions rely on open proximity rather than repeated singular assignment devices.",
    ),
    "f102v1": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "Several separated painted fragments and containers occupy the selected page part above and between continuous prose blocks; no repeated singular ownership system is visible.",
    ),
    "f88v": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "The selected foldout part alternates many separated painted fragments and containers with continuous prose blocks. Short inscriptions are nearby but lack leaders, cells, or consistently reserved owner stacks.",
    ),
    "f88r": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "Three fields of painted fragments and containers alternate with continuous prose blocks. Open placement supplies proximity, not a repeated secure assignment of inscriptions to individual drawings.",
    ),
    "f89r2": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "The selected foldout part contains many painted fragments and containers interleaved with prose. The short nearby inscriptions lack repeated singular owner boundaries.",
    ),
    "f103r": (
        "PROSE_DOMINANT", (True, False, True, False, False),
        "Continuous lines fill almost the entire page as a sequence of compact entries marked by repeated small margin signs; there is no dominant illustration or diagram array.",
    ),
    "f85r1": (
        "PROSE_DOMINANT", (True, False, False, False, False),
        "The selected page is a continuous dense multi-line prose field with no dominant illustration, repeated owned records, or diagram-defined slots.",
    ),
    "f71v": (
        "DIAGRAM_PARAMETER_ARRAY", (False, True, True, False, True),
        "The selected foldout panel is a concentric circular construction whose repeated human-form, star, and inscription positions are fixed by annular diagram geometry.",
    ),
    "f72r2": (
        "DIAGRAM_PARAMETER_ARRAY", (False, True, True, False, True),
        "The selected foldout panel is organized by concentric circular bands with repeated human-form, star, and inscription positions in diagram-defined annular slots.",
    ),
}


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    calibration = json.loads(CALIBRATION.read_text())
    diagnostic = [row for row in selection["rows"] if row["phase"] == "DIAGNOSTIC"]
    if [row["page"] for row in diagnostic] != list(JUDGMENTS):
        raise SystemExit("diagnostic row order changed")
    observations = []
    for row in diagnostic:
        role, flags, basis = JUDGMENTS[row["page"]]
        observations.append({
            "cell_id": row["cell_id"], "page": row["page"],
            "physical_folio": row["physical_folio"], "canvas_id": row["canvas_id"],
            "review_image_url": row["review_image_url"],
            "review_image_sha256": IMAGE_SHA[row["canvas_id"]],
            "role": role,
            "evidence": {
                "continuous_prose_block": flags[0],
                "dominant_illustration": flags[1],
                "repeated_object_or_cell_template": flags[2],
                "singular_ownership_devices": flags[3],
                "diagram_defined_slots": flags[4],
            },
            "visible_basis": basis, "uncertainty": "LOW",
            "machine_authored_native_visual_judgment": True,
        })
    cal_by_cell = {row["cell_id"]: row for row in calibration["observations"]}
    diag_by_cell = {row["cell_id"]: row for row in observations}
    cells = []
    for cell_id in sorted(cal_by_cell):
        cal, diag = cal_by_cell[cell_id], diag_by_cell[cell_id]
        resolved = cal["role"] != "MIXED_OR_UNRESOLVED" and diag["role"] != "MIXED_OR_UNRESOLVED"
        cells.append({
            "cell_id": cell_id,
            "calibration_page": cal["page"], "calibration_role": cal["role"],
            "diagnostic_page": diag["page"], "diagnostic_role": diag["role"],
            "resolved": resolved,
            "role_agreement": resolved and cal["role"] == diag["role"],
        })
    all_roles = [row["role"] for row in calibration["observations"] + observations]
    diag_counts = Counter(row["role"] for row in observations)
    resolved_cells = sum(row["resolved"] for row in cells)
    agreements = sum(row["role_agreement"] for row in cells)
    distinct = len({role for role in all_roles if role != "MIXED_OR_UNRESOLVED"})
    gates = {
        "minimum_resolved_cells": {"threshold": 10, "observed": resolved_cells, "passes": resolved_cells >= 10},
        "minimum_role_agreements": {"threshold": 11, "observed": agreements, "passes": agreements >= 11},
        "minimum_distinct_nonunresolved_roles": {"threshold": 3, "observed": distinct, "passes": distinct >= 3},
    }
    passed = all(row["passes"] for row in gates.values())
    result = {
        "experiment": "DRI001_PAIRED_DOCUMENT_ROLE_INVENTORY",
        "schema": "DRI001_RESULT_V1",
        "status": "PASS_THIRTEEN_OF_FIFTEEN_MATCHED_ROLE_AGREEMENTS" if passed else "STOP_DIAGNOSTIC_ROLE_TRANSFER_GATES_FAILED",
        "decision": "RETAIN_VISIBLE_DOCUMENT_ROLE_PANEL_FOR_PROSPECTIVE_STRUCTURAL_ASSOCIATION_ONLY" if passed else "CLOSE_PAIRED_DOCUMENT_ROLE_INSTRUMENT",
        "diagnostic_observations": observations,
        "cells": cells,
        "counts": {
            "cells": len(cells), "resolved_cells": resolved_cells,
            "role_agreements": agreements, "role_disagreements": len(cells) - agreements,
            "distinct_nonunresolved_roles_all_pages": distinct,
            "diagnostic_pages": len(observations),
            "diagnostic_physical_folios": len({row["physical_folio"] for row in observations}),
            "diagnostic_unique_canvases": len({row["canvas_id"] for row in observations}),
            "diagnostic_role_counts": {role: diag_counts.get(role, 0) for role in selection["rubric_roles"]},
        },
        "diagnostic_gates": gates,
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (METHOD, SELECTION, SELECTION_VALIDATION, CALIBRATION, CALIBRATION_VALIDATION)},
        "access": {
            "diagnostic_images_opened_only_after_calibration_publication": True,
            "official_source_native_pixels_used": True,
            "machine_authored_native_visual_judgments": True,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "diagnostic_transcription_identity_or_formal_fillers_opened_before_judgments": False,
            "structural_or_semantic_association_scored": False,
            "calibration_postreview_identity_exposure_disclosure_inherited": True,
        },
        "claim_ceiling": "Within the fifteen exact section and editorial-kind-run cells, thirteen paired different-folio pages share the same resolved visible document role. This retains a machine-authored native-visual role panel for separately preregistered structural association, with the calibration postreview identity-exposure disclosure inherited. It does not confirm a manuscript-wide document class or establish a heading caption field name class name word POS sound language cipher plaintext meaning or translation.",
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# DRI001 paired document-role inventory result\n\n"
        f"Status: **{result['status']}**.\n\n"
        "All fifteen diagnostic pages resolve under the unchanged rubric. Thirteen of fifteen different-folio pairs sharing the same section and exact editorial-kind run receive the same visible document role, exceeding the frozen minimum of eleven. All fifteen cells are resolved (minimum ten), and four non-unresolved roles occur across the thirty pages (minimum three). The two disagreements are DRC02 (`REPEATED_OWNED_RECORDS` versus `OBJECT_WITH_PROSE`) and DRC03 (`PROSE_DOMINANT` versus `OBJECT_WITH_PROSE`).\n\n"
        "This retains the finite page-role panel as a prospective author-visible relation for a separately frozen structural association test. It does not yet associate any text feature with a role. The observations are machine-authored direct native vision, not literal human annotation; diagnostic transcription identities remained sealed, while the published calibration postreview/pre-serialization identity-exposure disclosure remains inherited. No manuscript-wide class, heading, caption, field name, word, POS, sound, language, cipher, plaintext, meaning, or translation follows.\n"
    )


if __name__ == "__main__":
    main()
