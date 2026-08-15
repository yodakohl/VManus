#!/usr/bin/env python3
"""Independent metric and integrity validation for GDT076."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt076_result.json"
PAIRS = ROOT / "gdt076_register_host_rates.tsv"
FAMILIES = ROOT / "gdt076_right_family_stability.tsv"
REGISTERS = ROOT / "gdt076_register_summary.tsv"
NULLS = ROOT / "gdt076_null_results.tsv"
VARIANTS = ROOT / "gdt076_variant_log.tsv"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt076_validation.json"
FAMILY_NAMES = ("aiin", "air", "ain", "ar", "al")


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def close(left, right, tolerance=5e-9):
    return abs(float(left) - float(right)) <= tolerance


def corr(left, right):
    lm = sum(left) / len(left)
    rm = sum(right) / len(right)
    denominator = math.sqrt(sum((x - lm) ** 2 for x in left) * sum((y - rm) ** 2 for y in right))
    return sum((x - lm) * (y - rm) for x, y in zip(left, right)) / denominator if denominator else 0.0


def metrics(predicted, observed):
    tp = sum(p and y for p, y in zip(predicted, observed))
    fp = sum(p and not y for p, y in zip(predicted, observed))
    fn = sum(not p and y for p, y in zip(predicted, observed))
    tn = len(predicted) - tp - fp - fn
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "balanced_accuracy": (recall + specificity) / 2}


def main():
    result = json.loads(RESULT.read_text())
    pairs = read(PAIRS)
    families = {row["right_family"]: row for row in read(FAMILIES)}
    register_rows = read(REGISTERS)
    checks = {}
    checks["pair_inventory"] = (
        len(pairs) == result["register_host_pairs"] == 229
        and len({row["page_host"] for row in pairs}) == result["distinct_hosts"] == 69
        and len({row["held_register"] for row in pairs}) == len(result["registers"]) == 5
        and all(int(row["training_occurrences"]) >= 20 and int(row["held_occurrences"]) >= 5 and int(row["training_folios"]) >= 3 and int(row["held_folios"]) >= 2 for row in pairs)
    )
    family_ok = True
    for family in FAMILY_NAMES:
        training = [float(row[f"training_{family}_rate"]) for row in pairs]
        held = [float(row[f"held_{family}_rate"]) for row in pairs]
        family_ok &= (
            close(corr(training, held), families[family]["training_held_correlation"])
            and close(sum(abs(x - y) for x, y in zip(training, held)) / len(training), families[family]["mean_absolute_error"])
            and sum(x > 0 or y > 0 for x, y in zip(training, held)) == int(families[family]["nonzero_either_pairs"])
        )
    checks["family_metrics"] = family_ok
    predicted = [row["training_aiin_high"] == "1" for row in pairs]
    observed = [row["held_aiin_high"] == "1" for row in pairs]
    frequency = [row["frequency_control_high"] == "1" for row in pairs]
    aiin = metrics(predicted, observed)
    freq = metrics(frequency, observed)
    checks["aiin_confusion"] = all(close(aiin[key], result["aiin_class_metrics"][key]) for key in aiin)
    checks["frequency_confusion"] = all(close(freq[key], result["frequency_control_metrics"][key]) for key in freq)
    checks["register_metrics"] = all(
        metrics(
            [row["training_aiin_high"] == "1" for row in pairs if row["held_register"] == register["held_register"]],
            [row["held_aiin_high"] == "1" for row in pairs if row["held_register"] == register["held_register"]],
        )["tp"] == int(register["aiin_tp"])
        and metrics(
            [row["frequency_control_high"] == "1" for row in pairs if row["held_register"] == register["held_register"]],
            [row["held_aiin_high"] == "1" for row in pairs if row["held_register"] == register["held_register"]],
        )["tp"] == int(register["frequency_tp"])
        for register in register_rows
    )
    null = read(NULLS)[0]
    rng = random.Random(int(null["seed"]))
    strata = []
    for register in result["registers"]:
        selected = [index for index, row in enumerate(pairs) if row["held_register"] == register]
        selected.sort(key=lambda index: (int(pairs[index]["training_occurrences"]), pairs[index]["page_host"]))
        for quartile in range(4):
            start = quartile * len(selected) // 4
            end = (quartile + 1) * len(selected) // 4
            if end > start:
                strata.append(selected[start:end])
    values = []
    for _ in range(int(null["draws"])):
        shuffled = predicted[:]
        for indices in strata:
            block = [shuffled[index] for index in indices]
            rng.shuffle(block)
            for index, value in zip(indices, block):
                shuffled[index] = value
        values.append(metrics(shuffled, observed)["balanced_accuracy"])
    checks["matched_null"] = (
        close(sum(values) / len(values), null["null_mean_balanced_accuracy"])
        and close(max(values), null["null_max_balanced_accuracy"])
        and close((sum(value >= aiin["balanced_accuracy"] for value in values) + 1) / (len(values) + 1), null["inclusive_p"])
    )
    checks["headline"] = (
        result["status"] == "AIIN_PROPENSITY_IS_TRANSFERABLE_PAGE_HOST_FORMAL_CLASS"
        and result["aiin_class_metrics"]["balanced_accuracy"] > 0.85
        and result["aiin_class_metrics"]["balanced_accuracy"] > result["frequency_control_metrics"]["balanced_accuracy"]
        and result["matched_null"]["inclusive_p"] < 0.001
    )
    checks["variants"] = {row["variant_id"]: row["status"] for row in read(VARIANTS)} == {
        "V00": "PRIMARY", "V01": "FIXED_CLASS", "V02": "FREQUENCY_CONTROL", "V03": "MATCHED_NULL", "V04": "NOT_RUN"
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
    ledger = [row for row in read(LEDGER) if row["checkpoint_id"] == "GDT076_CKPT001"]
    checks["ledger"] = len(ledger) == 1 and ledger[0]["status"] == result["status"] and ledger[0]["result_artifact"] == RESULT.name
    passed = all(checks.values())
    validation = {
        "schema": "GDT076_RIGHT_FAMILY_HOST_PROPENSITY_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_METRICS_NULL_AND_INTEGRITY" if passed else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independently reconstructs family correlations/errors, aiin and frequency confusion, register TPs, the complete frequency-quartile permutation null, variants, seals, hashes and ledger from exported pairs; it does not rebuild pair rates from source groups.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
