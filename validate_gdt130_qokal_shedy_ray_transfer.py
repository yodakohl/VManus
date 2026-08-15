#!/usr/bin/env python3
"""Independently validate corrected GDT130 scoring and bindings."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt130_result.json"
PREDICTION = ROOT / "gdt130_prediction.json"
LOCALIZATION = ROOT / "gdt130_localization.json"
REVIEWS = ROOT / "gdt130_blind_crop_reviews.tsv"
SCORED = ROOT / "gdt130_scored_prediction.tsv"
OUT = ROOT / "gdt130_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION.read_text(encoding="utf-8"))
    reviews = read(REVIEWS)
    scored = read(SCORED)
    counts = [int(row["rays"]) for row in reviews]
    predicted = int(prediction["target"]["prediction"]["rays"])
    checks = {}
    checks["schema"] = result["schema"] == "GDT130_QOKAL_SHEDY_RAY_TRANSFER_RESULT_V1"
    checks["status"] = result["status"] == "QOKAL_SHEDY_SEVEN_RAY_TRANSFER_FAILED_VISUAL_COUNT_8_OR9"
    checks["corrected_freeze"] = prediction["status"] == "CORRECTED_FROZEN_BEFORE_F116R_LINE_TO_STAR_LOCALIZATION" and predicted == 7
    checks["correct_target"] = localization["selected_star_ordinal"] == result["target"]["selected_star_ordinal"] == 9 and localization["target_id"] == result["target"]["target_id"]
    checks["reviewers"] = len(reviews) == 2 and len({row["reviewer_id"] for row in reviews}) == 2 and all(row["reviewer_context"] == "FRESH_FORK_NONE_CROP_ONLY_NO_REPOSITORY_READ" for row in reviews)
    checks["crop_binding"] = all(row["crop_sha256"] == localization["image"]["crop_sha256"] for row in reviews)
    checks["counts"] = set(counts) == {8, 9} and counts == result["review"]["reviewer_counts"]
    checks["failure"] = all(value != predicted for value in counts) and result["review"]["prediction_rejected_by_all_reviewers"] is True and result["review"]["prediction_supported_by_any_reviewer"] is False
    checks["no_adjudication_needed"] = result["review"]["third_review_needed"] is False and result["review"]["third_review_reason"] == "DECISION_INVARIANT_TO_8_VS_9_ADJUDICATION"
    checks["invalid_reviews_excluded"] = result["review"]["invalid_star06_reviewers_excluded"] == 2
    checks["scored"] = len(scored) == 1 and scored[0]["prediction_rejected_by_all_reviewers"] == "1" and scored[0]["decision"] == "FAILED_INVARIANT_TO_8_VS_9_ADJUDICATION"
    checks["f84_sealed"] = all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["output_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["outputs"].items())
    checks["document_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["documents"].items())
    content = dict(result)
    recorded = content.pop("result_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("no number", "star meaning", "plaintext", "translation"))
    status = "PASS_CORRECTED_TARGET_UNANIMOUS_PREDICTION_REJECTION_AND_HASHES" if all(checks.values()) else "FAIL"
    validation = {"schema": "GDT130_QOKAL_SHEDY_RAY_TRANSFER_VALIDATION_V1", "status": status,
                  "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
                  "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
