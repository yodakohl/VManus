#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "RRA001_RECURRENT_LABEL_OWNER_ATLAS_METHOD.md"
SELECTION = RES / "rra001_recurrent_label_owner_atlas_selection.json"
SELECTION_VALIDATION = RES / "rra001_recurrent_label_owner_atlas_selection_validation.json"
RESULT = RES / "rra001_recurrent_label_owner_atlas_result.json"
OUT = RES / "rra001_recurrent_label_owner_atlas_result_validation.json"
REPORT = RES / "rra001_recurrent_label_owner_atlas_result_validation_report.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text())
    selection = json.loads(SELECTION.read_text())
    observations = result["observations"]
    grouped = defaultdict(list)
    for row in observations:
        grouped[row["surface"]].append(row)
    derived_types = []
    for surface in sorted(grouped):
        rows = grouped[surface]
        derived_types.append({
            "surface": surface,
            "loci": [row["locus"] for row in rows],
            "singular_owned_count": sum(row["outcome"] == "SINGULAR_COMMON_CLASS_OWNED" for row in rows),
            "occurrence_count": len(rows),
            "passes_all_occurrences": all(row["outcome"] == "SINGULAR_COMMON_CLASS_OWNED" for row in rows),
        })
    counts = Counter(row["outcome"] for row in observations)
    expected_loci = [row["locus"] for row in selection["rows"]]
    expected_outcomes = [
        "PROXIMITY_OR_GROUP_ONLY", "PROXIMITY_OR_GROUP_ONLY",
        "OTHER_CLASS_OR_SLOT_ASSOCIATED", "OTHER_CLASS_OR_SLOT_ASSOCIATED",
        "OTHER_CLASS_OR_SLOT_ASSOCIATED", "SINGULAR_COMMON_CLASS_OWNED",
        "OTHER_CLASS_OR_SLOT_ASSOCIATED", "PROXIMITY_OR_GROUP_ONLY",
        "OTHER_CLASS_OR_SLOT_ASSOCIATED", "SINGULAR_COMMON_CLASS_OWNED",
        "OTHER_CLASS_OR_SLOT_ASSOCIATED", "SINGULAR_COMMON_CLASS_OWNED",
        "PROXIMITY_OR_GROUP_ONLY", "PROXIMITY_OR_GROUP_ONLY",
        "PROXIMITY_OR_GROUP_ONLY", "PROXIMITY_OR_GROUP_ONLY",
        "OTHER_CLASS_OR_SLOT_ASSOCIATED", "SINGULAR_COMMON_CLASS_OWNED",
        "SINGULAR_COMMON_CLASS_OWNED", "OTHER_CLASS_OR_SLOT_ASSOCIATED",
        "SINGULAR_COMMON_CLASS_OWNED",
    ]
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "exact_prior_bindings": result["inputs"] == {str(path.relative_to(ROOT)): sha256(path) for path in (METHOD, SELECTION, SELECTION_VALIDATION)},
        "selection_row_identity": [row["locus"] for row in observations] == expected_loci and [(row["surface"], row["page"], row["canvas_id"]) for row in observations] == [(row["surface"], row["page"], row["canvas_id"]) for row in selection["rows"]],
        "exact_outcomes": [row["outcome"] for row in observations] == expected_outcomes,
        "gate_logic": all((row["outcome"] == "SINGULAR_COMMON_CLASS_OWNED") == all(row["gates"].values()) for row in observations),
        "all_hashes_well_formed": all(len(row["official_full_image_sha256"]) == 64 and len(row["review_region_sha256"]) == 64 for row in observations),
        "type_reconstruction": result["type_results"] == derived_types,
        "zero_passing_types": not any(row["passes_all_occurrences"] for row in derived_types) and result["panel_gate"] == {"every_occurrence_singular_owned_by_type": []},
        "exact_partition": counts == {"SINGULAR_COMMON_CLASS_OWNED": 6, "OTHER_CLASS_OR_SLOT_ASSOCIATED": 8, "PROXIMITY_OR_GROUP_ONLY": 7},
        "count_reconstruction": result["counts"] == {"types": 9, "loci": 21, "physical_folios": 9, "fixed_prior_outcomes": 5, "new_target_judgments": 16, "singular_common_class_owned": 6, "other_class_or_slot_associated": 8, "proximity_or_group_only": 7, "localization_unresolved": 0, "passing_types": 0},
        "stop_decision": result["status"] == "STOP_ZERO_OF_NINE_TYPES_RETAIN_SINGULAR_COMMON_CLASS_OWNERSHIP" and result["decision"].startswith("CLOSE_EXACT_RECURRENT"),
        "access_and_ceiling": result["access"]["ocr_clip_embedding_or_automated_vision_used"] is False and result["access"]["parser_roots_or_roles_used"] is False and all(term in result["claim_ceiling"] for term in ("does not show", "translation")),
    }
    if not all(checks.values()):
        raise SystemExit([name for name, passed in checks.items() if not passed])
    validation = {
        "experiment": "RRA001_RESULT_VALIDATION",
        "schema": "RRA001_RESULT_VALIDATION_V1",
        "status": "PASS_12_CHECK_COMPLETE_ATLAS_AND_ZERO_OF_NINE_STOP_RECONSTRUCTION",
        "source_result_sha256": sha256(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# RRA001 result validation\n\n"
        "Status: **PASS_12_CHECK_COMPLETE_ATLAS_AND_ZERO_OF_NINE_STOP_RECONSTRUCTION**.\n\n"
        "Compact independent code binds the frozen selection and its validation, reconstructs all 21 loci in order, the 6/8/7 outcome partition, all gate vectors, nine type-level all-occurrence decisions, zero passing types, official image and review-region hash fields, canonical bytes, source-only access restrictions, and the claim ceiling. It reconstructs the recorded judgments rather than claiming a second visual inspection.\n"
    )


if __name__ == "__main__":
    main()
