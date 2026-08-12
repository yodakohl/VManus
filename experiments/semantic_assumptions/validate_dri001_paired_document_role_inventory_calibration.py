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
RESULT = RES / "dri001_paired_document_role_inventory_calibration.json"
OUT = RES / "dri001_paired_document_role_inventory_calibration_validation.json"
REPORT = RES / "dri001_paired_document_role_inventory_calibration_validation_report.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    result = json.loads(RESULT.read_text())
    observations = result["observations"]
    selected = [row for row in selection["rows"] if row["phase"] == "CALIBRATION"]
    roles = [
        "DIAGRAM_PARAMETER_ARRAY", "REPEATED_OWNED_RECORDS", "PROSE_DOMINANT",
        "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE",
        "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE",
        "OBJECT_WITH_PROSE", "OBJECT_WITH_PROSE", "PROSE_DOMINANT",
        "PROSE_DOMINANT", "DIAGRAM_PARAMETER_ARRAY", "DIAGRAM_PARAMETER_ARRAY",
    ]
    role_counts = Counter(roles)
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "exact_input_bindings": result["inputs"] == {str(path.relative_to(ROOT)): sha256(path) for path in (METHOD, SELECTION, SELECTION_VALIDATION)},
        "exact_calibration_rows": [(row["cell_id"], row["page"], row["physical_folio"], row["canvas_id"]) for row in observations] == [(row["cell_id"], row["page"], row["physical_folio"], row["canvas_id"]) for row in selected],
        "diagnostic_phase_sealed": result["access"]["diagnostic_images_opened_during_calibration"] is False,
        "exact_roles": [row["role"] for row in observations] == roles,
        "evidence_schema": all(set(row["evidence"]) == {"continuous_prose_block", "dominant_illustration", "repeated_object_or_cell_template", "singular_ownership_devices", "diagram_defined_slots"} and all(type(value) is bool for value in row["evidence"].values()) for row in observations),
        "official_witness_hashes": len({row["canvas_id"] for row in observations}) == 14 and all(len(row["review_image_sha256"]) == 64 and row["review_image_url"].startswith(f"https://collections.library.yale.edu/iiif/2/{row['canvas_id']}/") for row in observations),
        "count_reconstruction": result["counts"] == {"pages": 15, "physical_folios": 14, "unique_canvases": 14, "unresolved": 0, "distinct_nonunresolved_roles": 4, "role_counts": {role: role_counts.get(role, 0) for role in selection["rubric_roles"]}},
        "calibration_gate": result["calibration_gate"] == {"maximum_unresolved": 3, "observed_unresolved": 0, "rubric_amendment_required": False, "passes": True},
        "decision": result["status"] == "PASS_CALIBRATION_ZERO_UNRESOLVED_NO_RUBRIC_AMENDMENT" and result["decision"] == "AUTHORIZE_SEALED_DIAGNOSTIC_IMAGE_ACCESS",
        "provenance_and_ceiling": result["access"]["machine_authored_native_visual_judgments"] is True and result["access"]["ocr_clip_embedding_or_automated_vision_used"] is False and result["access"]["transcription_identity_or_formal_fillers_used"] is False and all(term in result["claim_ceiling"] for term in ("machine-authored", "not literal human annotation", "translation")),
    }
    if not all(checks.values()):
        raise SystemExit([name for name, passed in checks.items() if not passed])
    value = {
        "experiment": "DRI001_CALIBRATION_VALIDATION",
        "schema": "DRI001_CALIBRATION_VALIDATION_V1",
        "status": "PASS_11_CHECK_CALIBRATION_GATE_AND_PROVENANCE_RECONSTRUCTION",
        "source_result_sha256": sha256(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# DRI001 calibration validation\n\n"
        "Status: **PASS_11_CHECK_CALIBRATION_GATE_AND_PROVENANCE_RECONSTRUCTION**.\n\n"
        "Compact independent code binds the frozen selection, reconstructs all fifteen calibration rows, exact role sequence and 3/8/1/3/0 partition, fourteen official witness hashes, evidence-vector schema, zero-unresolved gate, sealed diagnostic phase, canonical bytes, native-visual machine authorship, excluded methods, and claim ceiling. It validates the recorded judgments and arithmetic rather than claiming a second visual inspection.\n"
    )


if __name__ == "__main__":
    main()
