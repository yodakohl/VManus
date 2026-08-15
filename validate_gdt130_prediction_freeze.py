#!/usr/bin/env python3
"""Validate the GDT130 formal target and pre-visual freeze."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREDICTION = ROOT / "gdt130_prediction.json"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
FROZEN = ROOT / "gdt130_frozen_prediction.tsv"
OUT = ROOT / "gdt130_prediction_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    frozen = list(csv.DictReader(FROZEN.open(encoding="utf-8"), delimiter="\t"))
    observed = {}
    starts = []
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] != "f116r":
                continue
            if row["edition"] == "ZL3b" and row["source_group_index"] == "1" and row["paragraph_start"] == "1":
                starts.append(row["locus"])
            if row["locus"] == "f116r.23" and row["source_group_index"] in {"5", "6"}:
                observed[(row["edition"], row["source_group_index"])] = row["ivtff_group_raw"]
    checks = {}
    checks["schema"] = prediction["schema"] == "GDT130_QOKAL_SHEDY_RAY_TRANSFER_PREDICTION_V1"
    checks["status"] = prediction["status"] == "FROZEN_BEFORE_F116R_STAR06_VISUAL_REVIEW"
    checks["row"] = len(frozen) == 1 and frozen[0]["page"] == "f116r" and frozen[0]["star_ordinal"] == "6"
    checks["ordinal"] = starts[5] == "f116r.18" and int(starts[5].split(".")[1]) <= 23 < int(starts[6].split(".")[1])
    checks["primary_readings"] = [observed[(edition, str(index))] for edition in ("ZL3b", "IT2a") for index in (5, 6)] == ["qokal", "shedy", "qokal", "shedy"]
    checks["rf_uncertain"] = observed[("RF1b", "5")] == "qokal" and observed[("RF1b", "6")] == "she@152;y" and prediction["target"]["reading_state"] == "ZL_IT_EXACT_RF_UNCERTAIN"
    checks["prediction"] = prediction["target"]["prediction"] == {"rays": 7, "tail": "UNPREDICTED", "color": "UNPREDICTED"}
    checks["pair"] = prediction["near_minimal_pair"]["reference_form"] == "qokal|sheedy" and prediction["near_minimal_pair"]["target_form_primary"] == "qokal|shedy"
    checks["image_not_opened"] = prediction["target_access"] == {"f116r_image_opened_by_gdt130_at_freeze": False, "star06_visual_state_joined_at_freeze": False}
    checks["f84_sealed"] = all(value is False for value in prediction["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in prediction["inputs"].items())
    checks["implementation_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in prediction["implementation"].items())
    checks["output_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in prediction["outputs"].items())
    checks["document_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in prediction["documents"].items())
    content = dict(prediction)
    recorded = content.pop("prediction_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded
    status = "PASS_FROZEN_BEFORE_F116R_VISUAL_REVIEW" if all(checks.values()) else "FAIL"
    validation = {"schema": "GDT130_QOKAL_SHEDY_RAY_TRANSFER_PREDICTION_VALIDATION_V1", "status": status,
                  "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
                  "prediction_sha256": sha(PREDICTION), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
