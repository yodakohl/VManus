#!/usr/bin/env python3
"""Independent arithmetic and integrity checks for GDT073."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt073_result.json"
SCORES = ROOT / "gdt073_cross_section_scores.tsv"
FOLDS = ROOT / "gdt073_cross_section_folios.tsv"
PREDICTIONS = ROOT / "gdt073_cross_section_predictions.tsv"
EXCLUSIONS = ROOT / "gdt073_cross_section_exclusions.tsv"
VARIANTS = ROOT / "gdt073_variant_log.tsv"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt073_validation.json"
REPS = ("RAW_CHAR3", "PAGE_HOST_CHAR3", "BEHAVIOR_SELF_NEIGHBOR_NOPOS")


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def close(left, right, tolerance=5e-9):
    return abs(float(left) - float(right)) <= tolerance


def main():
    result = json.loads(RESULT.read_text())
    scores = read(SCORES)
    folds = read(FOLDS)
    predictions = read(PREDICTIONS)
    checks = {}
    cells = {(row["external_axis"], row["target_section"]) for row in scores}
    checks["cell_inventory"] = len(cells) == 7 and len(scores) == 21 and all(
        {row["representation"] for row in scores if (row["external_axis"], row["target_section"]) == cell}
        == set(REPS)
        for cell in cells
    )
    checks["target_section_separation"] = all(
        row["target_section"] not in row["training_sections"].split(";") for row in scores
    )
    checks["capacity_counts"] = all(
        int(row["target_loci"]) >= 10
        and 3 <= int(row["target_positive"]) <= int(row["target_loci"]) - 3
        and int(row["target_folios"]) >= 2
        and int(row["training_loci"]) >= 10
        and 3 <= int(row["training_positive"]) <= int(row["training_loci"]) - 3
        for row in scores
    )
    by_cell = defaultdict(list)
    for row in predictions:
        assert not row["target_locus"].startswith("f84r")
        by_cell[row["external_axis"], row["target_section"]].append(row)
    arithmetic = True
    for score in scores:
        selected = by_cell[score["external_axis"], score["target_section"]]
        representation = score["representation"]
        nuisance = sum(
            -math.log2(float(row["nuisance_probability"]) if int(row["observed"]) else 1 - float(row["nuisance_probability"]))
            for row in selected
        )
        held = sum(
            -math.log2(float(row[representation + "_probability"]) if int(row["observed"]) else 1 - float(row[representation + "_probability"]))
            for row in selected
        )
        arithmetic &= (
            len(selected) == int(score["target_loci"])
            and close(nuisance, score["nuisance_bits"])
            and close(held, score["held_bits"])
            and close(nuisance - held, score["gain_bits"])
        )
    checks["prediction_arithmetic"] = arithmetic
    fold_index = defaultdict(float)
    for row in folds:
        fold_index[row["external_axis"], row["target_section"], row["representation"]] += float(row["gain_bits"])
    checks["folio_sums"] = all(
        close(fold_index[row["external_axis"], row["target_section"], row["representation"]], row["gain_bits"])
        for row in scores
    )
    behavior = [row for row in scores if row["representation"] == "BEHAVIOR_SELF_NEIGHBOR_NOPOS"]
    raw = [row for row in scores if row["representation"] == "RAW_CHAR3"]
    checks["headline_summary"] = (
        result["summary"]["cells"] == 7
        and result["summary"]["positive_cells"] == sum(float(row["gain_bits"]) > 0 for row in behavior) == 2
        and result["summary"]["cells_beating_raw"]
        == sum(
            float(row["gain_bits"])
            > float(next(other["gain_bits"] for other in raw if other["external_axis"] == row["external_axis"] and other["target_section"] == row["target_section"]))
            for row in behavior
        )
        == 3
        and close(sum(float(row["gain_bits"]) for row in behavior), result["summary"]["total_gain_bits"])
    )
    axis = result["axis_summary"]
    checks["axis_directions"] = (
        axis["REL_ENCLOSURE"]["positive_cells"] == 2
        and axis["REL_EXPLICIT_ATTACHMENT"]["positive_cells"] == 0
        and axis["REL_ARRAY_OR_GROUP"]["positive_cells"] == 0
    )
    checks["negative_status"] = (
        result["status"] == "BEHAVIOR_PROFILE_CROSS_SECTION_TRANSFER_NOT_SUPPORTED"
        and result["summary"]["total_gain_bits"] < 0
        and result["raw_summary"]["total_gain_bits"] > result["summary"]["total_gain_bits"]
    )
    checks["exclusions_and_variants"] = len(read(EXCLUSIONS)) > 0 and {
        row["variant_id"]: row["status"] for row in read(VARIANTS)
    } == {"V00": "PRIMARY", "V01": "RUN_BASELINES", "V02": "FIXED_AXIS_FAMILY", "V03": "POSTSELECTED_AUDIT", "V04": "NOT_RUN"}
    checks["f84_seal"] = not any(result["f84r"].values()) and not any(
        row["target_locus"].startswith("f84r") for row in predictions
    )
    body = dict(result)
    claimed = body.pop("result_content_sha256")
    checks["content_hash"] = content_sha(body) == claimed
    checks["bound_hashes"] = all(
        sha(ROOT / name) == digest
        for family in ("inputs", "outputs", "documents", "implementation")
        for name, digest in result[family].items()
    )
    ledger = [row for row in read(LEDGER) if row["checkpoint_id"] == "GDT073_CKPT001"]
    checks["ledger"] = len(ledger) == 1 and ledger[0]["status"] == result["status"] and ledger[0]["result_artifact"] == RESULT.name
    passed = all(checks.values())
    validation = {
        "schema": "GDT073_CROSS_SECTION_BEHAVIOR_TRANSFER_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_ARITHMETIC_AND_INTEGRITY" if passed else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independently reconstructs prediction codelengths, cell and folio gains, capacity, section separation, summary directions, seals, hashes, variants, and ledger; it does not independently rebuild PAGE_HOST profiles.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
