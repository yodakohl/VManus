#!/usr/bin/env python3
"""Independent ranking and integrity validation for GDT075."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt075_result.json"
FOLDS = ROOT / "gdt075_nested_section_folds.tsv"
RANKINGS = ROOT / "gdt075_candidate_rankings.tsv"
VARIANTS = ROOT / "gdt075_variant_log.tsv"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt075_validation.json"
FIXED = "RATE:R=aiin>=0.25"


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
    folds = read(FOLDS)
    rankings = read(RANKINGS)
    checks = {}
    checks["fold_set"] = {(row["training_section"], row["held_section"]) for row in folds} == {("A", "Z"), ("Z", "A")}
    complete = True
    for fold in folds:
        selected = [row for row in rankings if row["training_section"] == fold["training_section"] and row["held_section"] == fold["held_section"]]
        ranks = [int(row["training_rank"]) for row in selected]
        top = next(row for row in selected if int(row["training_rank"]) == 1)
        raiin = next(row for row in selected if row["candidate"] == FIXED)
        complete &= (
            ranks == list(range(1, len(selected) + 1))
            and len(selected) == int(fold["eligible_candidates"])
            and top["candidate"] == fold["selected_candidate"]
            and close(top["training_conditional_effect"], fold["selected_training_effect"])
            and close(top["held_conditional_effect"], fold["selected_held_effect"])
            and int(raiin["training_rank"]) == int(fold["raiin_training_rank"])
            and close(raiin["training_conditional_effect"], fold["raiin_training_effect"])
            and close(raiin["held_conditional_effect"], fold["raiin_held_effect"])
        )
    checks["rankings_and_folds"] = complete
    checks["selected_fail"] = sum(int(row["selected_transfers_positive"]) for row in folds) == result["selected_positive_transfers"] == 0
    checks["raiin_stable"] = (
        sum(int(row["raiin_transfers_positive"]) for row in folds) == result["raiin_positive_transfers"] == 2
        and [int(row["raiin_training_rank"]) for row in folds] == [3, 12]
    )
    by_fold = {
        section: {row["candidate"]: row for row in rankings if row["training_section"] == section}
        for section in ("A", "Z")
    }
    shared = set(by_fold["A"]) & set(by_fold["Z"])
    stability = sorted(
        (
            min(float(by_fold["A"][candidate]["training_conditional_z"]), float(by_fold["Z"][candidate]["training_conditional_z"])),
            candidate,
        )
        for candidate in shared
    )[::-1]
    stability_rank = next(index for index, (_, candidate) in enumerate(stability, 1) if candidate == FIXED)
    checks["cross_section_stability_rank"] = (
        len(shared) == result["shared_capacity_candidates"] == 76
        and stability_rank == result["raiin_cross_section_stability_rank"] == 3
    )
    checks["headline"] = result["status"] == "TOP_DISCOVERED_BEHAVIOR_PREDICATES_FAIL_CROSS_SECTION_TRANSFER_RAIIN_SUBLEAD_STABLE"
    checks["variants"] = {row["variant_id"]: row["status"] for row in read(VARIANTS)} == {
        "V00": "PRIMARY", "V01": "FIXED_SUBLEAD", "V02": "CAPACITY", "V03": "NOT_RUN"
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
    ledger = [row for row in read(LEDGER) if row["checkpoint_id"] == "GDT075_CKPT001"]
    checks["ledger"] = len(ledger) == 1 and ledger[0]["status"] == result["status"] and ledger[0]["result_artifact"] == RESULT.name
    passed = all(checks.values())
    validation = {
        "schema": "GDT075_NESTED_SECTION_PREDICATE_TRANSFER_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_RANKING_AND_INTEGRITY" if passed else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independently checks complete fold rankings, selected and fixed-sublead effects/ranks/directions, shared-library stability rank, variants, seals, hashes and ledger; it does not rebuild source-event rates.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
