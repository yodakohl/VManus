#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt361_aq_contact_prospective"
HUMAN = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
GDT360 = ROOT / "experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_result.json"
SELECTION = BASE / "artifacts/gdt361_selection.tsv"
FREEZE = BASE / "artifacts/gdt361_freeze.json"
TARGETS = [f"f102v2.{i}" for i in range(10, 17)]


def main() -> None:
    guard = GuardedTSV(
        HUMAN,
        selector_column="page",
        allowed_values={"f102v2"},
        forbidden_prefixes=("f84",),
        forbidden_action="skip",
    )
    by_locus = {row["locus"]: row for row in guard if row["locus"] in TARGETS}
    assert list(sorted(by_locus, key=lambda x: int(x.rsplit(".", 1)[1]))) == TARGETS
    assert all(by_locus[x]["unit"] == "L2" for x in TARGETS)
    assert all(by_locus[x]["local_relation_tags"] == "REL_PROXIMITY" for x in TARGETS)

    fieldnames = [
        "target_id", "page", "physical_folio", "locus", "unit", "ordinal",
        "normalized_code", "certainty", "source_provenance", "raw_source_description",
        "prospective_score_eligible", "exclusion_reason", "visual_state",
    ]
    rows = []
    for ordinal, locus in enumerate(TARGETS, 1):
        source = by_locus[locus]
        rows.append({
            "target_id": "G361-" + hashlib.sha256(locus.encode()).hexdigest()[:12].upper(),
            "page": "f102v2",
            "physical_folio": "f102",
            "locus": locus,
            "unit": "F102V2_L2",
            "ordinal": ordinal,
            "normalized_code": source["normalized_code"],
            "certainty": source["certainty"],
            "source_provenance": source["source_path"],
            "raw_source_description": source["local_comment"],
            "prospective_score_eligible": "0" if locus == "f102v2.10" else "1",
            "exclusion_reason": "FORMAL_VALUE_DISPLAYED_DURING_PRE_FREEZE_AUDIT" if locus == "f102v2.10" else "",
            "visual_state": "SEALED_PENDING_DIRECT_REVIEW",
        })
    SELECTION.parent.mkdir(parents=True, exist_ok=True)
    with SELECTION.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "schema": "GDT361_FREEZE_V1",
        "status": "FROZEN_BEFORE_VISUAL_STATE_REVIEW_AND_SIX_ROW_FORMAL_QUERY",
        "selection": {
            "page": "f102v2", "physical_folio": "f102", "unit": "F102V2_L2",
            "all_loci": TARGETS,
            "prospective_scoring_loci": TARGETS[1:],
            "preexposed_excluded_loci": [TARGETS[0]],
            "basis": "SOURCE_DESCRIBED_SEQUENTIAL_SEVEN_LABEL_ROW_SELECTED_WITHOUT_TARGET_VISUAL_STATES",
            "official_canvas_id": "1006253", "official_dimensions": [2838, 3697],
            "official_image_sha256": "e3ed770ad77b1c1127b8e60b2ee2d9e226ab4089d4861b85dbf22299925397ce",
        },
        "prediction": {
            "formal_predicate": "FIRST_GROUP_PREFIX_2:AQ",
            "panel_alias": "FIRST_GROUP_PREFIX_3:AQA_IF_MASK_IDENTICAL",
            "direction": "CONTACT_PREVALENCE_GREATER_THAN_CLEAR_GAP_PREVALENCE",
            "visual_states": ["CONTACT", "CLEAR_GAP", "UNCERTAIN"],
            "uncertain_handling": "MISSING_RETAINED_NOT_FORCED",
            "primary_scope": "SIX_UNEXPOSED_LOCI_ONLY",
            "primary_statistic": "CONTACT_MINUS_GAP_PREDICATE_PREVALENCE",
            "null": "EXACT_WITHIN_ARRAY_STATE_PERMUTATION_CONDITIONAL_ON_HARD_STATE_AND_PREDICATE_COUNTS",
        },
        "access": {
            "visual_states_reviewed_before_freeze": False,
            "formal_values_of_six_scored_loci_queried_before_freeze": False,
            "f102v2_10_formal_value_displayed_and_excluded": True,
            "gdt360_global_state_blind_join_preexisting": True,
            "f84_accessed": False,
        },
        "inputs": {
            str(HUMAN.relative_to(ROOT)): sha256_file(HUMAN),
            str(GDT360.relative_to(ROOT)): sha256_file(GDT360),
            "experiments/yolo/gdt361_aq_contact_prospective/METHOD.md": sha256_file(BASE / "METHOD.md"),
            "experiments/yolo/gdt361_aq_contact_prospective/SOURCE_AUDIT.md": sha256_file(BASE / "SOURCE_AUDIT.md"),
            "experiments/yolo/gdt361_aq_contact_prospective/src/freeze.py": sha256_file(Path(__file__)),
        },
        "outputs": {str(SELECTION.relative_to(ROOT)): sha256_file(SELECTION)},
        "claim_ceiling": "ONE_NEW_ARRAY_DIRECTIONAL_CONTACT_ASSOCIATION_ONLY_NO_SEMANTIC_OR_TRANSLATION_CLAIM",
    }
    FREEZE.write_bytes(canonical_json_bytes(payload))


if __name__ == "__main__":
    main()
