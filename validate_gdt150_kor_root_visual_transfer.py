#!/usr/bin/env python3
"""Independently validate GDT150 scoring, provenance, and bindings."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt150_result.json"
PREDICTION = ROOT / "gdt150_prediction.json"
TARGETS = ROOT / "gdt150_kor_root_targets.tsv"
OBSERVATIONS = ROOT / "gdt150_visual_observations.tsv"
SCORED = ROOT / "gdt150_scored_predictions.tsv"
OUT = ROOT / "gdt150_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    targets = read(TARGETS)
    obs = read(OBSERVATIONS)
    scored = read(SCORED)
    target_map = {row["target_id"]: row for row in targets}
    obs_map = {row["target_id"]: row for row in obs}
    checks = {}
    checks["schema"] = result["schema"] == "GDT150_KOR_ROOT_VISUAL_TRANSFER_RESULT_V1"
    checks["status"] = result["status"] == "KOR_ROOT_GEOMETRY_GLOSS_REJECTED"
    checks["frozen_before_access"] = prediction["status"] == "FROZEN_BEFORE_TARGET_IMAGE_ACCESS" and all(row["image_access_before_freeze"] == "NO" for row in targets)
    checks["two_exact_targets"] = len(targets) == len(obs) == len(scored) == 2 and set(target_map) == set(obs_map) == {"GDT150_F22R", "GDT150_F37R"}
    checks["pages"] = {row["page"] for row in obs} == {"f22r", "f37r"} and all(not row["page"].startswith("f84") for row in obs)
    checks["official_canvases"] = {(row["page"], row["yale_canvas_id"]) for row in obs} == {("f22r", "1006116"), ("f37r", "1006146")}
    checks["image_hashes"] = {(row["page"], row["full_image_sha256"]) for row in obs} == {
        ("f22r", "7bfb7bf49850d6d8df30ebae5a1ea8adc7b27bb714cb0e24453724805bd72a3e"),
        ("f37r", "4daf7373cfed96fcd9e3d6cb6a9a50cf413e27cc93cf507fee17bee93d8f6d28")}
    checks["ai_direct"] = all(row["observation_provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" and row["reviewer_condition"] == "HYPOTHESIS_AWARE_NO_HUMAN_CONFIRMATION" for row in obs)
    checks["negative_calls"] = all(row["visual_call"] == "NEGATIVE" and row["confidence"] == "HIGH" for row in obs)
    checks["frozen_positive"] = all(target_map[key]["frozen_prediction"] == obs_map[key]["frozen_prediction"] == "POSITIVE" for key in target_map)
    checks["zero_hits"] = all(row["prediction_match"] == "0" for row in obs) and result["prediction_summary"]["exact_hits"] == 0
    checks["decision_rule"] = any(row["visual_call"] == "NEGATIVE" for row in obs) and result["status"] == prediction["decision"]["any_negative"]
    checks["f37_counterexample_preserved"] = "one thickened central root mass" in result["counterexample"] and "one rounded thickened" in obs_map["GDT150_F37R"]["visible_geometry"].lower()
    checks["no_automated_vision"] = result["review"]["automated_vision_used"] is False and result["review"]["ocr_used"] is False
    checks["f84_sealed"] = all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["output_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["outputs"].items())
    checks["document_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["documents"].items())
    content = dict(result)
    recorded = content.pop("result_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("no botanical identity", "semantic role", "plaintext", "translation"))
    status = "PASS_PROSPECTIVE_TWO_TARGET_GLOSS_REJECTION_AND_HASHES" if all(checks.values()) else "FAIL"
    validation = {"schema": "GDT150_KOR_ROOT_VISUAL_TRANSFER_VALIDATION_V1", "status": status,
                  "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
                  "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
