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
RESULT = RES / "dri001_paired_document_role_inventory_result.json"
OUT = RES / "dri001_paired_document_role_inventory_result_validation.json"
REPORT = RES / "dri001_paired_document_role_inventory_result_validation_report.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    calibration = json.loads(CALIBRATION.read_text())
    result = json.loads(RESULT.read_text())
    diagnostics = [row for row in selection["rows"] if row["phase"] == "DIAGNOSTIC"]
    observations = result["diagnostic_observations"]
    roles = [
        "DIAGRAM_PARAMETER_ARRAY", "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE",
        "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE",
        "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE",
        "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE", "PROSE_DOMINANT",
        "PROSE_DOMINANT", "DIAGRAM_PARAMETER_ARRAY", "DIAGRAM_PARAMETER_ARRAY",
    ]
    cal_by_cell = {row["cell_id"]: row for row in calibration["observations"]}
    diag_by_cell = {row["cell_id"]: row for row in observations}
    reconstructed_cells = []
    for cell_id in sorted(cal_by_cell):
        cal, diag = cal_by_cell[cell_id], diag_by_cell[cell_id]
        resolved = cal["role"] != "MIXED_OR_UNRESOLVED" and diag["role"] != "MIXED_OR_UNRESOLVED"
        reconstructed_cells.append({"cell_id": cell_id, "calibration_page": cal["page"], "calibration_role": cal["role"], "diagnostic_page": diag["page"], "diagnostic_role": diag["role"], "resolved": resolved, "role_agreement": resolved and cal["role"] == diag["role"]})
    counts = Counter(roles)
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "exact_input_bindings": result["inputs"] == {str(path.relative_to(ROOT)): sha256(path) for path in (METHOD, SELECTION, SELECTION_VALIDATION, CALIBRATION, CALIBRATION_VALIDATION)},
        "exact_diagnostic_rows": [(row["cell_id"], row["page"], row["physical_folio"], row["canvas_id"]) for row in observations] == [(row["cell_id"], row["page"], row["physical_folio"], row["canvas_id"]) for row in diagnostics],
        "exact_diagnostic_roles": [row["role"] for row in observations] == roles,
        "cell_reconstruction": result["cells"] == reconstructed_cells,
        "exact_agreement_pattern": [row["cell_id"] for row in result["cells"] if not row["role_agreement"]] == ["DRC02", "DRC03"] and sum(row["role_agreement"] for row in result["cells"]) == 13,
        "evidence_schema": all(set(row["evidence"]) == {"continuous_prose_block", "dominant_illustration", "repeated_object_or_cell_template", "singular_ownership_devices", "diagram_defined_slots"} and all(type(value) is bool for value in row["evidence"].values()) for row in observations),
        "official_witnesses": len({row["canvas_id"] for row in observations}) == 13 and all(len(row["review_image_sha256"]) == 64 and row["review_image_url"].startswith(f"https://collections.library.yale.edu/iiif/2/{row['canvas_id']}/") for row in observations),
        "count_reconstruction": result["counts"] == {"cells": 15, "resolved_cells": 15, "role_agreements": 13, "role_disagreements": 2, "distinct_nonunresolved_roles_all_pages": 4, "diagnostic_pages": 15, "diagnostic_physical_folios": 14, "diagnostic_unique_canvases": 13, "diagnostic_role_counts": {role: counts.get(role, 0) for role in selection["rubric_roles"]}},
        "all_diagnostic_gates_pass": result["diagnostic_gates"] == {"minimum_resolved_cells": {"threshold": 10, "observed": 15, "passes": True}, "minimum_role_agreements": {"threshold": 11, "observed": 13, "passes": True}, "minimum_distinct_nonunresolved_roles": {"threshold": 3, "observed": 4, "passes": True}},
        "pass_decision": result["status"] == "PASS_THIRTEEN_OF_FIFTEEN_MATCHED_ROLE_AGREEMENTS" and result["decision"] == "RETAIN_VISIBLE_DOCUMENT_ROLE_PANEL_FOR_PROSPECTIVE_STRUCTURAL_ASSOCIATION_ONLY",
        "access_and_ceiling": result["access"] == {"diagnostic_images_opened_only_after_calibration_publication": True, "official_source_native_pixels_used": True, "machine_authored_native_visual_judgments": True, "ocr_clip_embedding_or_automated_vision_used": False, "diagnostic_transcription_identity_or_formal_fillers_opened_before_judgments": False, "structural_or_semantic_association_scored": False, "calibration_postreview_identity_exposure_disclosure_inherited": True} and all(term in result["claim_ceiling"] for term in ("thirteen", "machine-authored", "does not confirm", "translation")),
    }
    if not all(checks.values()):
        raise SystemExit([name for name, passed in checks.items() if not passed])
    value = {"experiment": "DRI001_RESULT_VALIDATION", "schema": "DRI001_RESULT_VALIDATION_V1", "status": "PASS_12_CHECK_DIAGNOSTIC_ROLE_TRANSFER_RECONSTRUCTION", "source_result_sha256": sha256(RESULT), "check_count": len(checks), "checks": checks, "claim_ceiling": result["claim_ceiling"]}
    OUT.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# DRI001 result validation\n\n"
        "Status: **PASS_12_CHECK_DIAGNOSTIC_ROLE_TRANSFER_RECONSTRUCTION**.\n\n"
        "Compact independent code binds the selection and calibration chain, reconstructs all fifteen diagnostic rows and exact role sequence, thirteen agreements with DRC02/DRC03 as the two disagreements, fifteen resolved cells, four-role diversity, thirteen official witness hashes, all gate values, access disclosure, canonical bytes, decision, and ceiling. It validates the recorded judgments and panel arithmetic rather than claiming a second visual inspection.\n"
    )


if __name__ == "__main__":
    main()
