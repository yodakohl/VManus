#!/usr/bin/env python3
"""Validate GDT126 pair census, arithmetic, hashes, and decision."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt126_result.json"
INV = ROOT / "gdt126_q20_record_boundary_inventory.tsv"
SCORES = ROOT / "gdt126_q20_record_boundary_scores.tsv"
FOLDS = ROOT / "gdt126_q20_record_boundary_folds.tsv"
NULL = ROOT / "gdt126_q20_record_boundary_null.tsv"
COUNTER = ROOT / "gdt126_q20_record_boundary_counterexamples.tsv"
OUT = ROOT / "gdt126_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b, tolerance=2e-10):
    return abs(float(a) - float(b)) <= tolerance


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    inventory, scores, folds, nulls, counters = map(read, (INV, SCORES, FOLDS, NULL, COUNTER))
    checks = {}
    checks["schema"] = result["schema"] == "GDT126_Q20_RECORD_BOUNDARY_RESET_RESULT_V1"
    checks["inventory_count"] = len(inventory) == 1692 and Counter(row["edition"] for row in inventory) == {"ZL3b": 564, "IT2a": 564, "RF1b": 564}
    checks["class_counts"] = all(Counter(row["boundary_class"] for row in inventory if row["edition"] == edition) == {"WITHIN_RECORD": 408, "CROSS_RECORD": 156} for edition in ("ZL3b", "IT2a", "RF1b"))
    checks["within_identity"] = all(row["star_ordinal_left"] == row["star_ordinal_right"] for row in inventory if row["boundary_class"] == "WITHIN_RECORD")
    checks["cross_consecutive"] = all(int(row["star_ordinal_right"]) == int(row["star_ordinal_left"]) + 1 for row in inventory if row["boundary_class"] == "CROSS_RECORD")
    checks["pair_geometry"] = all(row["left_locus"] != row["right_locus"] and int(row["left_groups"]) > 0 and int(row["right_groups"]) > 0 for row in inventory)
    checks["f84_absent"] = not any(row["page"].startswith("f84r") or row["left_locus"].startswith("f84r") or row["right_locus"].startswith("f84r") for row in inventory)
    checks["score_shape"] = len(scores) == len(nulls) == 12 and Counter(row["edition"] for row in scores) == {"ZL3b": 4, "IT2a": 4, "RF1b": 4}
    checks["fold_shape"] = len(folds) == 252 and all(row["unit_type"] in {"PAGE", "LEAVE_FOLIO_OUT"} for row in folds)
    score_key = {(row["edition"], row["model"]): row for row in scores}
    checks["page_fold_counts"] = all(sum(row["edition"] == edition and row["model"] == model and row["unit_type"] == "PAGE" for row in folds) == 13 for edition, model in score_key)
    checks["folio_fold_counts"] = all(sum(row["edition"] == edition and row["model"] == model and row["unit_type"] == "LEAVE_FOLIO_OUT" for row in folds) == 8 for edition, model in score_key)
    checks["positive_pages"] = all(int(score["positive_pages"]) == sum(row["edition"] == edition and row["model"] == model and row["unit_type"] == "PAGE" and float(row["effect"]) > 0 for row in folds) for (edition, model), score in score_key.items())
    checks["minimum_lofo"] = all(close(score["minimum_leave_folio_effect"], min(float(row["effect"]) for row in folds if row["edition"] == edition and row["model"] == model and row["unit_type"] == "LEAVE_FOLIO_OUT")) for (edition, model), score in score_key.items())
    checks["null_binding"] = all((row["edition"], row["model"]) in score_key and int(row["worlds"]) == 4096 and close(row["true_effect"], score_key[(row["edition"], row["model"])]["residual_similarity_effect"]) for row in nulls)
    primary = score_key[("ZL3b", "COMPILER12")]
    checks["primary_exact"] = close(primary["residual_similarity_effect"], .009798898188) and int(primary["positive_pages"]) == 8 and close(primary["minimum_leave_folio_effect"], .000594753494) and close(primary["max_four_p"], .339272638516)
    expected_gates = {
        "positive_effect": float(primary["residual_similarity_effect"]) > 0,
        "positive_all_leave_folio": float(primary["minimum_leave_folio_effect"]) > 0,
        "max_four_p_le_005": float(primary["max_four_p"]) <= .05,
        "all_readings_positive": all(float(score_key[(edition, "COMPILER12")]["residual_similarity_effect"]) > 0 for edition in ("ZL3b", "IT2a", "RF1b")),
        "beats_string_controls": float(primary["residual_similarity_effect"]) >= max(float(score_key[("ZL3b", model)]["residual_similarity_effect"]) for model in ("RAW_CHAR3_HASH32", "HOST_CHAR3_HASH32")),
    }
    checks["gates"] = result["gates"] == expected_gates
    expected_status = "Q20_STAR_BOUNDARY_HAS_COMPILER_RESET" if all(expected_gates.values()) else "Q20_STAR_BOUNDARY_RESET_WEAK_NONCONFIRMING" if float(primary["residual_similarity_effect"]) > 0 else "Q20_STAR_BOUNDARY_COMPILER_RESET_NOT_SUPPORTED"
    checks["decision"] = result["status"] == expected_status == "Q20_STAR_BOUNDARY_RESET_WEAK_NONCONFIRMING"
    checks["counterexamples"] = all(row["counterexample"] == "NONPOSITIVE_LEAVE_FOLIO_EFFECT" for row in counters)
    checks["result_scores"] = len(result["scores"]) == 12 and close(result["primary"]["residual_similarity_effect"], primary["residual_similarity_effect"])
    checks["f84_flags"] = all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["output_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["outputs"].items())
    checks["document_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["documents"].items())
    content = dict(result)
    recorded_hash = content.pop("result_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded_hash
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("Formal record-boundary", "no bullet meaning", "plaintext", "translation"))
    status = "PASS_PAIR_CENSUS_ARITHMETIC_AND_DECISION" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "GDT126_Q20_RECORD_BOUNDARY_RESET_VALIDATION_V1", "status": status,
        "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
        "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)),
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
