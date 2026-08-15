#!/usr/bin/env python3
"""Integrity and decision validation for GDT154 visual transfer."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
P = R / "gdt154_prediction.json"; PT = R / "gdt154_os_visual_predictions.tsv"
O = R / "gdt154_visual_observations.tsv"; S = R / "gdt154_scored_predictions.tsv"
C = R / "gdt154_counterexamples.tsv"; RESULT = R / "gdt154_result.json"
OUT = R / "gdt154_validation.json"


def read(path):
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    prediction = json.loads(P.read_text(encoding="utf8")); result = json.loads(RESULT.read_text(encoding="utf8"))
    pred, obs, scored, counter = read(PT), read(O), read(S), read(C)
    joins = {(r["target_id"], r["page"], r["physical_folio"]) for r in pred}
    obs_joins = {(r["target_id"], r["page"], r["physical_folio"]) for r in obs}
    hits = sum(r["joint_call"] == "POSITIVE" for r in obs)
    component = {
        "dark_leaf": {state: sum(r["dark_leaf_call"] == state for r in obs) for state in ("POSITIVE", "NEGATIVE", "UNCERTAIN")},
        "light_root": {state: sum(r["light_root_call"] == state for r in obs) for state in ("POSITIVE", "NEGATIVE", "UNCERTAIN")},
    }
    checks = {
        "schema": result["schema"] == "GDT154_OS_VISUAL_TRANSFER_RESULT_V1",
        "prediction_precedes_result": prediction["status"] == "FROZEN_BEFORE_TARGET_IMAGE_ACCESS",
        "two_targets": len(pred) == len(obs) == len(scored) == 2,
        "exact_joins": joins == obs_joins == {("OSVT01", "f15r", "f15"), ("OSVT02", "f27r", "f27")},
        "official_canvases": [(r["page"], r["yale_canvas_id"], r["image_dimensions"]) for r in obs] == [("f15r", "1006102", "2648x3729"), ("f27r", "1006126", "2708x3743")],
        "image_hash_shapes": all(len(r["full_image_sha256"]) == 64 and set(r["full_image_sha256"]) <= set("0123456789abcdef") for r in obs),
        "provenance": all(r["observation_provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" and r["reviewer_condition"] == "HYPOTHESIS_AWARE_NO_HUMAN_CONFIRMATION" for r in obs),
        "f15_component_failure": next(r for r in obs if r["page"] == "f15r")["light_root_call"] == "NEGATIVE",
        "f27_joint_hit": next(r for r in obs if r["page"] == "f27r")["joint_call"] == "POSITIVE",
        "decision": hits == result["joint_hits"] == 1 and result["status"] == "OS_DARK_LEAF_LIGHT_ROOT_GLOSS_UNSTABLE_LOCAL_ONLY",
        "component_counts": component == result["component_counts"],
        "scored_matches": [int(r["joint_prediction_match"]) for r in scored] == [0, 1],
        "counterexamples": len(counter) == 5 and any(r["type"] == "DIRECT_COMPONENT_CONTRADICTION" for r in counter),
        "f84_absent": not any(r["page"].startswith("f84") for r in pred + obs + scored) and all(v is False for v in result["f84r"].values()),
        "input_hashes": all((R / n).exists() and sha(R / n) == h for n, h in result["inputs"].items()),
        "implementation_hash": all((R / n).exists() and sha(R / n) == h for n, h in result["implementation"].items()),
        "output_hashes": all((R / n).exists() and sha(R / n) == h for n, h in result["outputs"].items()),
        "document_hashes": all((R / n).exists() and sha(R / n) == h for n, h in result["documents"].items()),
    }
    content = dict(result); recorded = content.pop("content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest() == recorded
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("no word", "plaintext", "translation"))
    status = "PASS_INTEGRITY_AND_FROZEN_DECISION_RECONSTRUCTION" if all(checks.values()) else "FAIL"
    out = {"schema": "GDT154_OS_VISUAL_TRANSFER_VALIDATION_V1", "status": status,
           "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
           "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__": main()
