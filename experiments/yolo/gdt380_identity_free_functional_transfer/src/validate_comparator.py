#!/usr/bin/env python3
"""Validate GDT380 comparator outputs without importing the scorer."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter
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


def read(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks = []

    def check(name: str, ok: bool) -> None:
        checks.append({"check": name, "pass": bool(ok)})
        if not ok:
            raise AssertionError(name)

    design = json.loads((ART / "gdt380_comparator_behavior_freeze.json").read_text())
    result = json.loads((ART / "gdt380_comparator_result.json").read_text())
    signature = json.loads((ART / "gdt380_identity_free_signature_freeze.json").read_text())
    folds = read(ART / "gdt380_comparator_fold_scores.tsv")
    predictions = read(ART / "gdt380_comparator_predictions.tsv.gz")
    summary = read(ART / "gdt380_comparator_family_summary.tsv")
    null = read(ART / "gdt380_comparator_null.tsv.gz")
    features = read(ART / "gdt380_behavior_feature_manifest.tsv")

    check("result_content_hash", result["content_hash"] == content(result))
    check("signature_content_hash", signature["content_hash"] == content(signature))
    check("four_summary_rows", len(summary) == 4 and {r["anonymous_family"] for r in summary} == {f"CMP_FUNCTION_0{i}" for i in range(1, 5)})
    check("four_feature_families", {r["anonymous_family"] for r in features} == {f"CMP_FUNCTION_0{i}" for i in range(1, 5)})
    check("no_identity_features", all(r["exact_identity_value_used"] == "0" for r in features))
    check("null_worlds", len(null) == design["null"]["worlds"] == 1024)
    # CMP_FUNCTION_04 has no CoReMA oracle endpoint; prediction coverage is
    # therefore the exact sum of the held-domain fold sizes, not four times
    # the full five-domain observation layer.
    check("prediction_coverage_matches_folds", len(predictions) == sum(int(r["n"]) for r in folds))
    check("prediction_keys_unique", len({(r["element_key"], r["anonymous_family"]) for r in predictions}) == len(predictions))
    check("fold_family_counts", Counter(r["anonymous_family"] for r in folds) == Counter({"CMP_FUNCTION_01": 5, "CMP_FUNCTION_02": 5, "CMP_FUNCTION_03": 5, "CMP_FUNCTION_04": 4}))
    check("fold_n_accounting", all(sum(int(r["n"]) for r in folds if r["anonymous_family"] == family) == sum(1 for r in predictions if r["anonymous_family"] == family) for family in {r["anonymous_family"] for r in folds}))
    for row in summary:
        family = row["anonymous_family"]
        family_folds = [r for r in folds if r["anonymous_family"] == family]
        floor = sorted((float(r["auc_full"]) for r in family_folds), reverse=True)[2]
        check(f"floor_{family}", math.isclose(floor, float(row["transfer_auc_floor"]), abs_tol=5e-10))
        check(f"gain_count_{family}", sum(float(r["gain_full_vs_nuisance_bits"]) > 0 for r in family_folds) == int(row["positive_gain_domains"]))
        check(f"reduced_gain_count_{family}", sum(float(r["gain_reduced_vs_nuisance_bits"]) > 0 for r in family_folds) == int(row["positive_reduced_gain_domains"]))
        maxima = [float(r["world_max"]) for r in null]
        expected = (1 + sum(value >= floor for value in maxima)) / (1 + len(maxima))
        check(f"maxp_{family}", math.isclose(expected, float(row["max_family_p"]), abs_tol=5e-10))
    eligible = [r["anonymous_family"] for r in summary if r["voynich_mapping_eligible"] == "1"]
    check("eligible_list", eligible == signature["eligible_anonymous_families"] == result["eligible_anonymous_families"])
    check("status_logic", (bool(eligible) and result["status"] == "IDENTITY_FREE_COMPARATOR_SIGNATURES_CALIBRATED") or (not eligible and result["status"] == "NO_IDENTITY_FREE_SIGNATURE_PASSED_COMPARATOR_GATE"))
    check("not_target_scored", not result["voynich_target_scored"] and result["voynich_target_rows_read"] == 0 and not signature["target_scored"])
    check("f1_unused", result["f1_used"] is False)
    check("f84_false", all(v is False for v in result["f84"].values()) and all(v is False for v in signature["f84"].values()))
    for section in ["inputs", "outputs", "implementation"]:
        for path, digest in result[section].items():
            check(section + "_" + path.replace("/", "_"), sha(ROOT / path) == digest)

    validation = {
        "schema": "GDT380_COMPARATOR_VALIDATION_V1",
        "status": "PASS",
        "scope": "OUTPUT_INTEGRITY_METRIC_ACCOUNTING_AND_GATE_RECONSTRUCTION_NO_MODEL_REFIT",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_hash": sha(ART / "gdt380_comparator_result.json"),
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    validation["content_hash"] = content(validation)
    (ART / "gdt380_comparator_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
