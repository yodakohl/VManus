#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt362_remaining_complete_array"
HUMAN = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
G361 = ROOT / "experiments/yolo/gdt361_aq_contact_prospective/artifacts/gdt361_result.json"
OUT_TSV = BASE / "artifacts/gdt362_selection.tsv"
OUT_JSON = BASE / "artifacts/gdt362_freeze.json"
TARGETS = [f"f101v2.{i}" for i in range(10, 19)]


def folio(page: str) -> str:
    match = re.match(r"f(\d+)", page)
    return "f" + match.group(1) if match else page


def main() -> None:
    guard = GuardedTSV(HUMAN, selector_column="page", forbidden_prefixes=("f84",), forbidden_action="skip")
    rows = list(guard)
    by_unit: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["context_class"] == "OBJECT_BEARING" and "LABEL" in row["object_tags"].split(";") and row["unit"].startswith("L"):
            by_unit[(row["page"], row["unit"])].append(row)
    target = sorted(by_unit[("f101v2", "L2")], key=lambda r: int(r["locus"].rsplit(".", 1)[1]))
    assert [r["locus"] for r in target] == TARGETS
    assert "There are 9 plants and 9 labels" in target[0]["local_comment"]

    fields = ["target_id", "page", "physical_folio", "unit", "ordinal", "locus", "certainty",
              "source_provenance", "raw_source_description", "visual_state"]
    output = []
    for i, row in enumerate(target, 1):
        output.append({
            "target_id": "G362-" + hashlib.sha256(row["locus"].encode()).hexdigest()[:12].upper(),
            "page": row["page"], "physical_folio": folio(row["page"]), "unit": "F101V2_L2",
            "ordinal": i, "locus": row["locus"], "certainty": row["certainty"],
            "source_provenance": row["source_path"], "raw_source_description": row["local_comment"],
            "visual_state": "SEALED_PENDING_DIRECT_REVIEW",
        })
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(output)
    payload = {
        "schema": "GDT362_FREEZE_V1",
        "status": "FROZEN_BEFORE_TARGET_IMAGE_REVIEW_OR_FORMAL_QUERY",
        "source_capacity": {
            "retained_units": ["F101V2_L2"], "retained_loci": TARGETS,
            "excluded": {
                "F101V2_L1": "NINE_SOURCE_LABELS_BUT_EIGHT_CURRENT_LOCI",
                "F88R_L1": "EDITORIAL_C1_L1_BOUNDARY",
                "F88R_L2": "EDITORIAL_C2_L2_BOUNDARY",
                "F88V_L1": "EDITORIAL_C1_L1_BOUNDARY",
                "F89_F99_F100_F102": "PREVIOUS_CONTACT_GAP_EXPOSURE",
            },
        },
        "selection": {
            "page": "f101v2", "physical_folio": "f101", "unit": "F101V2_L2",
            "loci": TARGETS, "canvas_id": "1006250", "dimensions": [2698, 3779],
            "image_sha256": "1122f1b13afdf1509402334816f95e5e9baa2b6c94aa9e347b04aa2e4e54f36b",
        },
        "prediction": {
            "predicate": "FIRST_GROUP_PREFIX_2:AQ",
            "alias": "FIRST_GROUP_PREFIX_3:AQA_IF_MASK_IDENTICAL",
            "direction": "CONTACT_PREVALENCE_GREATER_THAN_CLEAR_GAP_PREVALENCE",
            "uncertain": "MISSING_RETAINED_NOT_FORCED",
            "null": "EXACT_WITHIN_ARRAY_STATE_PERMUTATION",
        },
        "access": {"target_image_reviewed": False, "target_formal_values_queried": False, "f84_accessed": False},
        "inputs": {
            str(HUMAN.relative_to(ROOT)): sha256_file(HUMAN),
            str(G361.relative_to(ROOT)): sha256_file(G361),
            "experiments/yolo/gdt362_remaining_complete_array/METHOD.md": sha256_file(BASE / "METHOD.md"),
            "experiments/yolo/gdt362_remaining_complete_array/SOURCE_AUDIT.md": sha256_file(BASE / "SOURCE_AUDIT.md"),
            "experiments/yolo/gdt362_remaining_complete_array/src/freeze.py": sha256_file(Path(__file__)),
        },
        "outputs": {str(OUT_TSV.relative_to(ROOT)): sha256_file(OUT_TSV)},
        "claim_ceiling": "ONE_COMPLETE_NEW_FOLIO_ARRAY_DIRECTION_ONLY_NO_SEMANTIC_OR_TRANSLATION_CLAIM",
    }
    OUT_JSON.write_bytes(canonical_json_bytes(payload))


if __name__ == "__main__": main()
