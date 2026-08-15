#!/usr/bin/env python3
"""Integrity and independent exported-statistic checks for GDT074."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt074_result.json"
TESTS = ROOT / "gdt074_section_excluded_enclosure_tests.tsv"
EXAMPLES = ROOT / "gdt074_enclosure_class_examples.tsv"
RATES = ROOT / "gdt074_section_excluded_host_rates.tsv"
VARIANTS = ROOT / "gdt074_variant_log.tsv"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt074_validation.json"


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def close(left, right, tolerance=5e-9):
    return abs(float(left) - float(right)) <= tolerance


def main():
    result = json.loads(RESULT.read_text())
    tests = read(TESTS)
    examples = read(EXAMPLES)
    rates = read(RATES)
    checks = {}
    keys = {(row["predicate_id"], row["target_section"]) for row in tests}
    checks["fixed_test_family"] = keys == {
        ("HCLASS_RAIIN_HIGH", "A"),
        ("HCLASS_RAIIN_HIGH", "Z"),
        ("HCLASS_FO_ACTIVE", "A"),
        ("HCLASS_FO_ACTIVE", "Z"),
    } and result["predicates"] == {
        "HCLASS_RAIIN_HIGH": ["R=aiin", 0.25],
        "HCLASS_FO_ACTIVE": ["F=O", 0.1],
    }
    by_test = defaultdict(list)
    for row in examples:
        assert not row["locus"].startswith("f84r")
        by_test[row["predicate_id"], row["target_section"]].append(row)
    checks["example_counts"] = all(
        len(by_test[key]) == int(row["feature_loci"])
        and sum(int(value["relation_enclosure"]) for value in by_test[key]) == int(row["feature_positive"])
        and sum(value["outcome"] == "COUNTEREXAMPLE" for value in by_test[key]) == int(row["feature_negative"])
        for row in tests
        for key in [(row["predicate_id"], row["target_section"])]
    )
    thresholds = {"HCLASS_RAIIN_HIGH": 0.25, "HCLASS_FO_ACTIVE": 0.1}
    checks["thresholds"] = all(
        float(row["outside_section_rate"]) >= thresholds[row["predicate_id"]]
        for row in examples
    )
    checks["outside_section_support"] = all(
        int(row["outside_section_occurrences"]) > 0
        and int(row["outside_section_folios"]) >= 2
        and row["target_section"] in {"A", "Z"}
        for row in rates
    )
    directions = {
        predicate: sum(
            int(row["direction_positive"])
            for row in tests
            if row["predicate_id"] == predicate
        )
        for predicate in ("HCLASS_RAIIN_HIGH", "HCLASS_FO_ACTIVE")
    }
    checks["directions"] = directions == result["direction_positive_sections"] == {
        "HCLASS_RAIIN_HIGH": 2,
        "HCLASS_FO_ACTIVE": 1,
    }
    combined = {}
    for predicate in directions:
        selected = [row for row in tests if row["predicate_id"] == predicate]
        eligible = sum(int(row["eligible_feature_loci"]) for row in selected)
        combined[predicate] = sum(float(row["conditional_effect"]) * int(row["eligible_feature_loci"]) for row in selected) / eligible
    checks["combined_effects"] = all(
        close(value, result["combined"][predicate]["conditional_effect"])
        for predicate, value in combined.items()
    )
    checks["headline"] = (
        result["status"] == "RAIIN_HIGH_ENCLOSURE_LEAD_SURVIVES_SECTION_EXCLUDED_RATE_TRANSPORT"
        and result["leading_candidate"] == "HCLASS_RAIIN_HIGH"
        and result["downgraded_candidate"] == "HCLASS_FO_ACTIVE"
        and "reproduces GDT069" in result["gdt069_overlap_disclosure"]
    )
    checks["variants"] = {row["variant_id"]: row["status"] for row in read(VARIANTS)} == {
        "V00": "PRIMARY",
        "V01": "FIXED_TARGETS",
        "V02": "POSTSELECTED_TRANSPORT",
        "V03": "NOT_RUN",
    }
    checks["f84_seal"] = not any(result["f84r"].values())
    body = dict(result)
    claimed = body.pop("result_content_sha256")
    checks["content_hash"] = content_sha(body) == claimed
    checks["bound_hashes"] = all(
        sha(ROOT / name) == digest
        for family in ("inputs", "outputs", "documents", "implementation")
        for name, digest in result[family].items()
    )
    ledger = [row for row in read(LEDGER) if row["checkpoint_id"] == "GDT074_CKPT001"]
    checks["ledger"] = len(ledger) == 1 and ledger[0]["status"] == result["status"] and ledger[0]["result_artifact"] == RESULT.name
    passed = all(checks.values())
    validation = {
        "schema": "GDT074_SECTION_EXCLUDED_ENCLOSURE_CLASSES_VALIDATION_V1",
        "status": "PASS_EXPORTED_STATISTICS_AND_INTEGRITY" if passed else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Checks exact fixed predicate/section family, exported feature counts/outcomes/thresholds, outside-section support, conditional-effect aggregation, disclosures, seals, hashes, variants and ledger; it does not independently reconstruct host rates from source events.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
