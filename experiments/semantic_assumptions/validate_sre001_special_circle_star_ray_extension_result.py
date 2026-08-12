#!/usr/bin/env python3
"""Validate SRE001 bindings and frozen decision arithmetic."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
METHOD = BASE / "SRE001_SPECIAL_CIRCLE_STAR_RAY_EXTENSION_METHOD.md"
SELECTION = BASE / "results/sre001_special_circle_star_ray_extension_selection.json"
SELECTION_VALIDATION = BASE / "results/sre001_special_circle_star_ray_extension_selection_validation.json"
TSV = BASE / "results/sre001_special_circle_star_ray_extension_result.tsv"
RESULT = BASE / "results/sre001_special_circle_star_ray_extension_result.json"
REPORT = BASE / "results/sre001_special_circle_star_ray_extension_result_report.md"
OUT = BASE / "results/sre001_special_circle_star_ray_extension_result_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(TSV.open(encoding="utf-8", newline=""), delimiter="\t"))
    outcomes = Counter(row["outcome"] for row in rows)
    image_sha = result["inputs"]["official_image_sha256"]
    checks = {
        "canonical_result": RESULT.read_bytes() == canonical(result),
        "complete_frozen_target_order": [row["opaque_id"] for row in rows] == [row["opaque_id"] for row in selection["targets"]] and len(rows) == 24,
        "exact_outcome_partition": outcomes == Counter({"SLOT_OR_GROUP_ONLY": 18, "NON_STAR_OBJECT": 6}) and all(not row["ray_count"] for row in rows),
        "folio_partition": Counter(row["physical_folio"] for row in rows) == Counter({"f72": 10, "f73": 8, "f69": 6}),
        "all_capacity_gates_fail": result["gates"] and not any(result["gates"].values()),
        "exact_source_bindings": result["inputs"] == {str(METHOD.relative_to(ROOT)): sha(METHOD), str(SELECTION.relative_to(ROOT)): sha(SELECTION), str(SELECTION_VALIDATION.relative_to(ROOT)): sha(SELECTION_VALIDATION), "official_image_sha256": image_sha},
        "four_official_image_hashes": image_sha == {"1006198": "b830e74480830c0d5e8f7b56025473e051743f9ec50685b6fe316ecd493f0f01", "1006203": "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269", "1006206": "5bc8e07dbd61cc1f218cfc4449cd527be118aa7884878ec4c8e568e9c2d89bad", "1006207": "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141"},
        "sealed_text_and_formal_access": result["access"]["voynich_label_surfaces_opened"] is False and result["access"]["formal_features_opened"] is False and result["counts"]["associations_scored"] == 0,
        "native_visual_provenance": result["access"]["machine_authored_source_bound_native_visual_judgments"] is True and result["access"]["ocr_clip_embedding_or_automated_vision_used"] is False,
        "result_tsv_and_report": result["result_tsv_sha256"] == sha(TSV) and REPORT.exists(),
        "stop_and_ceiling": result["status"] == "STOP_ZERO_SINGULAR_STAR_OWNED_TARGETS" and all(word in result["claim_ceiling"] for word in ("number", "meaning", "translation")),
    }
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    validation = {
        "experiment": "SRE001_SPECIAL_CIRCLE_STAR_RAY_EXTENSION_RESULT_VALIDATION",
        "status": "PASS_11_CHECK_SOURCE_BINDING_AND_CAPACITY_STOP_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": list(checks),
        "source_result_sha256": sha(RESULT),
        "source_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation reconstructs the recorded visual judgments and stop arithmetic; it supplies no number, word, meaning, or translation.",
    }
    OUT.write_bytes(canonical(validation))


if __name__ == "__main__":
    main()
