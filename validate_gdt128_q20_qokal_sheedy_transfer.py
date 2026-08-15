#!/usr/bin/env python3
"""Independently validate GDT128 review consensus, score, and bindings."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt128_result.json"
PREDICTION = ROOT / "gdt128_prediction.json"
REVIEWS = ROOT / "gdt128_blind_visual_reviews.tsv"
SCORED = ROOT / "gdt128_scored_prediction.tsv"
OUT = ROOT / "gdt128_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    reviews = read_tsv(REVIEWS)
    scored = read_tsv(SCORED)
    rays = Counter(int(row["rays"]) for row in reviews)
    tails = Counter(int(row["tail"]) for row in reviews)
    checks = {}
    checks["schema"] = result["schema"] == "GDT128_Q20_QOKAL_SHEEDY_TRANSFER_RESULT_V1"
    checks["status"] = result["status"] == "Q20_QOKAL_SHEEDY_RAY_TRANSFER_HIT_TAIL_TRANSFER_FAILED"
    checks["freeze_status"] = prediction["status"] == "FROZEN_BEFORE_F103R_STAR15_VISUAL_REVIEW"
    checks["review_count"] = len(reviews) == 3 and len({row["reviewer_id"] for row in reviews}) == 3
    checks["source_free"] = all(row["reviewer_context"] == "FRESH_FORK_NONE_SOURCE_FREE_NO_REPOSITORY_READ" for row in reviews)
    checks["same_target"] = all(row["page"] == "f103r" and row["star_ordinal"] == "15" for row in reviews)
    checks["same_image"] = len({row["image_sha256"] for row in reviews}) == 1 and next(iter({row["image_sha256"] for row in reviews})) == "28a65644ebf9a16dc41c073e6535117d924765fae6af474dbd1e3fe2b167beda"
    checks["ray_counts"] = rays == {8: 2, 7: 1} and result["review"]["ray_consensus"] == 8 and result["review"]["ray_consensus_support"] == 2
    checks["tail_counts"] = tails == {0: 3} and result["review"]["tail_consensus"] == 0 and result["review"]["tail_consensus_support"] == 3
    checks["prediction"] = prediction["target"]["prediction"] == {"color": "UNPREDICTED", "rays": 8, "tail": 1}
    checks["score"] = result["score"] == {"ray_prediction_hit": True, "tail_prediction_hit": False, "exact_joint_prediction_hit": False, "statistical_inference": "NONE_SINGLE_POSTSELECTED_TARGET"}
    checks["scored_row"] = len(scored) == 1 and scored[0]["ray_prediction_hit"] == "1" and scored[0]["tail_prediction_hit"] == "0" and scored[0]["exact_joint_prediction_hit"] == "0"
    checks["third_review_disclosed"] = result["review"]["third_reviewer_trigger"] == "FIRST_TWO_DISAGREED_ON_RAYS"
    checks["f84_sealed"] = all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["output_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["outputs"].items())
    checks["document_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["documents"].items())
    content = dict(result)
    recorded = content.pop("result_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("no star", "number", "plaintext", "translation"))
    status = "PASS_INDEPENDENT_REVIEW_CONSENSUS_SCORE_AND_HASHES" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "GDT128_Q20_QOKAL_SHEEDY_TRANSFER_VALIDATION_V1",
        "status": status,
        "checks_total": len(checks),
        "checks_passed": sum(checks.values()),
        "checks": checks,
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
