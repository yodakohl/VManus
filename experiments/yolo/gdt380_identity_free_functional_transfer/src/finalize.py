#!/usr/bin/env python3
"""Bind the GDT380 comparator stop, report, and validation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt380_identity_free_functional_transfer"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    comparator = json.loads((ART / "gdt380_comparator_result.json").read_text())
    validation = json.loads((ART / "gdt380_comparator_validation.json").read_text())
    signature = json.loads((ART / "gdt380_identity_free_signature_freeze.json").read_text())
    assert comparator["status"] == "NO_IDENTITY_FREE_SIGNATURE_PASSED_COMPARATOR_GATE"
    assert validation["status"] == "PASS"
    assert not signature["eligible_anonymous_families"]
    result = {
        "schema": "GDT380_FINAL_RESULT_V1",
        "status": "NO_IDENTITY_FREE_SIGNATURE_PASSED_COMPARATOR_GATE",
        "comparator_rows": comparator["rows"],
        "comparator_records": comparator["records"],
        "anonymous_families_tested": 4,
        "eligible_anonymous_families": [],
        "voynich_target_stage": "NOT_AUTHORIZED_NOT_RUN",
        "voynich_target_rows_read": 0,
        "f1": "CLOSED_FOR_SEMANTIC_INTERPRETATION_RETAINED_ONLY_AS_EXPOSED_F1_X_F1_ANOMALY",
        "inputs": {
            str(path.relative_to(ROOT)): sha(path)
            for path in [
                ART / "gdt380_comparator_behavior_freeze.json",
                ART / "gdt380_comparator_result.json",
                ART / "gdt380_comparator_validation.json",
                ART / "gdt380_identity_free_signature_freeze.json",
                ART / "gdt380_counterexamples.tsv",
                ART / "gdt380_null_capacity.tsv",
            ]
        },
        "documents": {
            str((BASE / name).relative_to(ROOT)): sha(BASE / name)
            for name in ["METHOD.md", "README.md", "REPORT.md", "experiment.json"]
        },
        "implementation": {
            str((BASE / "src/finalize.py").relative_to(ROOT)): sha(BASE / "src/finalize.py")
        },
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "semantic_state": "UNASSIGNED",
        "claim_ceiling": "COMPARATOR_STAGE_IDENTITY_FREE_INSTRUMENT_STOP_NO_VOYNICH_FUNCTION_CLASS",
    }
    result["content_hash"] = content(result)
    (ART / "gdt380_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
