#!/usr/bin/env python3
"""Validate GDT125 inventory, fold arithmetic, hashes, and decision."""
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt125_result.json"
INV = ROOT / "gdt125_q20_open_incremental_inventory.tsv"
SCORES = ROOT / "gdt125_q20_open_incremental_scores.tsv"
FOLDS = ROOT / "gdt125_q20_open_incremental_folds.tsv"
NULL = ROOT / "gdt125_q20_open_incremental_null.tsv"
COUNTER = ROOT / "gdt125_q20_open_incremental_counterexamples.tsv"
OUT = ROOT / "gdt125_validation.json"


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
    checks["schema"] = result["schema"] == "GDT125_Q20_OPEN_INCREMENTAL_RECORD_SELECTOR_RESULT_V1"
    checks["inventory_count"] = len(inventory) == 405 and Counter(row["edition"] for row in inventory) == {"ZL3b": 135, "IT2a": 135, "RF1b": 135}
    checks["inventory_identity"] = len({(row["edition"], row["unit_id"]) for row in inventory}) == 405
    checks["inventory_depth"] = all(row["body1_locus"] and row["tail_loci"] and int(row["body1_groups"]) > 0 and int(row["tail_groups"]) > 0 for row in inventory)
    checks["folio_count"] = all(len({row["physical_folio"] for row in inventory if row["edition"] == edition}) == 8 for edition in ("ZL3b", "IT2a", "RF1b"))
    checks["f84_absent"] = not any(row["page"].startswith("f84r") or row["open_locus"].startswith("f84r") or "f84r" in row["tail_loci"] for row in inventory)
    checks["score_shape"] = len(scores) == len(nulls) == 18 and Counter(row["edition"] for row in scores) == {"ZL3b": 6, "IT2a": 6, "RF1b": 6}
    checks["fold_shape"] = len(folds) == 144 and all(int(row["held_records"]) > 0 for row in folds)
    checks["counter_shape"] = len(counters) == 36 and all(row["counterexample"] == "WORST_INCREMENTAL_HELD_FOLIO" for row in counters)
    score_key = {(row["edition"], row["model"]): row for row in scores}
    fold_key = Counter()
    positive_key = Counter()
    for row in folds:
        key = (row["edition"], row["model"])
        fold_key[key] += float(row["pseudo_gain_bits"])
        positive_key[key] += int(float(row["pseudo_gain_bits"]) > 0)
    checks["fold_sums"] = all(close(row["pseudo_gain_bits"], fold_key[key]) for key, row in score_key.items())
    checks["positive_folios"] = all(int(row["positive_folios"]) == positive_key[key] for key, row in score_key.items())
    checks["selector_cost"] = all(close(row["selector_paid_gain_bits"], float(row["pseudo_gain_bits"]) - math.log2(6)) for row in scores)
    checks["null_binding"] = all((row["edition"], row["model"]) in score_key and int(row["worlds"]) == 4096 and close(row["true_gain_bits"], score_key[(row["edition"], row["model"])]["pseudo_gain_bits"]) for row in nulls)
    primary = score_key[("ZL3b", "OPEN_COMPILER_AFTER_BODY1")]
    reverse = score_key[("ZL3b", "BODY1_COMPILER_AFTER_OPEN")]
    checks["primary_exact"] = close(primary["pseudo_gain_bits"], 2.823466165404) and int(primary["positive_folios"]) == 6 and close(primary["max_six_p"], 0.845252623871)
    checks["reverse_exact"] = close(reverse["pseudo_gain_bits"], 1.083194904540) and int(reverse["positive_folios"]) == 4
    expected_gates = {
        "selector_paid_positive": float(primary["selector_paid_gain_bits"]) > 0,
        "six_of_eight_positive_folios": int(primary["positive_folios"]) >= 6,
        "max_six_p_le_005": float(primary["max_six_p"]) <= .05,
        "all_readings_positive": all(float(score_key[(edition, "OPEN_COMPILER_AFTER_BODY1")]["pseudo_gain_bits"]) > 0 for edition in ("ZL3b", "IT2a", "RF1b")),
    }
    checks["gates"] = result["gates"] == expected_gates
    expected_status = "Q20_OPEN_RETAINS_INCREMENTAL_RECORD_SELECTOR_SIGNAL" if all(expected_gates.values()) else "Q20_FIRST_BODY_EXPLAINS_RECORD_SETPOINT" if float(reverse["pseudo_gain_bits"]) > float(primary["pseudo_gain_bits"]) else "Q20_OPEN_INCREMENTAL_SIGNAL_WEAK_OR_UNSTABLE"
    checks["decision"] = result["status"] == expected_status == "Q20_OPEN_INCREMENTAL_SIGNAL_WEAK_OR_UNSTABLE"
    checks["result_scores"] = len(result["scores"]) == 18 and close(result["primary"]["pseudo_gain_bits"], primary["pseudo_gain_bits"])
    checks["f84_flags"] = all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["output_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["outputs"].items())
    checks["document_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["documents"].items())
    content = dict(result)
    expected_hash = content.pop("result_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == expected_hash
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("Formal record-selector", "no heading", "plaintext", "translation"))
    status = "PASS_INVENTORY_FOLD_ARITHMETIC_AND_DECISION" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "GDT125_Q20_OPEN_INCREMENTAL_RECORD_SELECTOR_VALIDATION_V1",
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
