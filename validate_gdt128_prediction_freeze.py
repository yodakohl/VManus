#!/usr/bin/env python3
"""Validate GDT128 freeze without accessing target image or ray/tail values."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRED = ROOT / "gdt128_prediction.json"
TSV = ROOT / "gdt128_frozen_prediction.tsv"
OUT = ROOT / "gdt128_prediction_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    pred = json.loads(PRED.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(TSV.open(encoding="utf-8"), delimiter="\t"))
    formal = [row for row in csv.DictReader((ROOT / "gdt016_group_state_inventory.tsv").open(encoding="utf-8"), delimiter="\t") if row["locus"] == "f103r.43" and row["group_index"] in {"7", "8"}]
    checks = {}
    checks["schema"] = pred["schema"] == "GDT128_Q20_QOKAL_SHEEDY_TRANSFER_PREDICTION_V1"
    checks["status"] = pred["status"] == "FROZEN_BEFORE_F103R_STAR15_VISUAL_REVIEW"
    checks["single_row"] = len(rows) == 1 and rows[0]["target_id"] == "GDT128_F103R_STAR15"
    checks["target_exact"] = pred["target"]["page"] == "f103r" and pred["target"]["star_ordinal"] == 15 and pred["target"]["open_locus"] == "f103r.43"
    checks["formal_exact"] = [(row["group_index"], row["token"]) for row in sorted(formal, key=lambda row: int(row["group_index"]))] == [("7", "qokal"), ("8", "sheedy")]
    checks["prediction_exact"] = pred["target"]["prediction"] == {"rays": 8, "tail": 1, "color": "UNPREDICTED"}
    checks["analogy_mismatch_disclosed"] = pred["analogy"]["reference_field"] == "qotol|sheedy" and pred["analogy"]["exact_hpr2_skeleton_match"] is False
    checks["target_not_accessed"] = pred["target_access"]["exact_star15_rays_or_tail_joined_at_freeze"] is False and pred["target_access"]["exact_star15_rays_or_tail_inspected_by_gdt128_at_freeze"] is False
    checks["f84_flags"] = all(value is False for value in pred["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in pred["inputs"].items())
    checks["implementation_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in pred["implementation"].items())
    checks["output_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in pred["outputs"].items())
    checks["document_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in pred["documents"].items())
    content = dict(pred)
    recorded_hash = content.pop("prediction_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded_hash
    checks["claim_ceiling"] = all(term in pred["claim_ceiling"] for term in ("postselected", "no star meaning", "plaintext", "translation"))
    status = "PASS_FROZEN_BEFORE_TARGET_VISUAL_REVIEW" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "GDT128_Q20_QOKAL_SHEEDY_TRANSFER_PREDICTION_VALIDATION_V1", "status": status,
        "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
        "prediction_sha256": sha(PRED), "prediction_tsv_sha256": sha(TSV), "validator_sha256": sha(Path(__file__)),
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
