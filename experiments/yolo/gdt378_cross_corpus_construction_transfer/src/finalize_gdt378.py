#!/usr/bin/env python3
"""Assemble the final GDT378 decision without changing any scored artifact."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
ART = BASE / "artifacts"
COMPARATOR = ART / "gdt378_comparator_result.json"
TARGET = ART / "gdt378_voynich_target_result.json"
DIAGNOSTIC = ART / "gdt378_identity_only_diagnostic_result.json"
CANDIDATES = ART / "gdt378_voynich_candidate_atlas.tsv"
DIAGNOSTIC_ROWS = ART / "gdt378_identity_only_diagnostic.tsv"
CORRECTION = ART / "gdt378_target_execution_correction.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj):
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    comparator = json.loads(COMPARATOR.read_text())
    target = json.loads(TARGET.read_text())
    diagnostic = json.loads(DIAGNOSTIC.read_text())
    atlas = {(row["signature_id"], row["resolution"], row["candidate_family"], row["candidate_id"]): row for row in rows(CANDIDATES)}
    leads = []
    for row in rows(DIAGNOSTIC_ROWS):
        original = atlas[(row["signature_id"], row["resolution"], row["candidate_family"], row["candidate_id"])]
        if (
            float(row["identity_only_max_family_p"]) <= .05
            and float(original["held_sse_gain_over_placement"]) > 0
            and float(original["positive_gain_folio_fraction"]) >= .60
            and float(original["mean_placement_residual"]) > 0
            and float(original["positive_residual_folio_fraction"]) >= 2 / 3
            and int(original["positive_residual_registers"]) >= 2
        ):
            leads.append({
                "signature_id": row["signature_id"], "resolution": row["resolution"],
                "candidate_id": row["candidate_id"], "events": int(row["events"]),
                "physical_folios": int(row["physical_folios"]), "registers": int(row["registers"]),
                "mean_placement_residual": float(row["mean_placement_residual"]),
                "held_sse_gain_over_placement": float(row["held_sse_gain_over_placement"]),
                "positive_gain_folio_fraction": float(row["positive_gain_folio_fraction"]),
                "positive_residual_folio_fraction": float(original["positive_residual_folio_fraction"]),
                "positive_residual_registers": int(original["positive_residual_registers"]),
                "identity_only_max_family_p": float(row["identity_only_max_family_p"]),
                "status": "POSTHOC_NONPROMOTING_LEAD",
            })
    result = {
        "schema": "GDT378_FINAL_RESULT_V1",
        "status": "HEAD_FAILED_PRIMARY_TARGET_NULL_DEGENERATE_TWO_POSTHOC_IDENTITY_LEADS",
        "comparator_head_gate_pass": comparator["head_gate_pass"],
        "comparator_head_status": comparator["status"],
        "anonymous_signatures_applied": 4,
        "target_powered_candidates": target["powered_candidates"],
        "target_promoted_candidates": target["promoted_candidates"],
        "primary_null_unique_maxima": diagnostic["primary_null_unique_maxima"],
        "primary_null_interpretation": "DEGENERATE_DUE_TO_SLOT_STATISTIC_INVARIANT_UNDER_REQUIRED_POSITION_CLOSURE_NULL",
        "posthoc_identity_only_leads": leads,
        "posthoc_identity_only_lead_count": len(leads),
        "lead_relation": "The SOURCE_GROUP lead is the d-wrapper realization of the ATOMIC_JOINT_TUPLE lead; this is one linked formal lead at two charged resolutions, not two independent findings.",
        "semantic_assignments": 0,
        "voynich_functional_classes_assigned": 0,
        "gdt377_changed": False,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [COMPARATOR, TARGET, DIAGNOSTIC, CANDIDATES, DIAGNOSTIC_ROWS, CORRECTION]},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
        "claim_ceiling": "ONE_POSTHOC_OPAQUE_FORMAL_LEAD_AT_TWO_RESOLUTIONS_NO_PROMOTION_FUNCTION_OR_SEMANTICS",
    }
    assert result["posthoc_identity_only_lead_count"] == 2
    result["content_hash"] = content(result)
    (ART / "gdt378_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "leads": len(leads), "promoted": target["promoted_candidates"]}))


if __name__ == "__main__":
    main()
