#!/usr/bin/env python3
"""Independent selected-model reconstruction and integrity checks for GDT077."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
RESULT = ROOT / "gdt077_result.json"
SCORES = ROOT / "gdt077_model_scores.tsv"
REGISTERS = ROOT / "gdt077_register_scores.tsv"
VARIANTS = ROOT / "gdt077_variant_log.tsv"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt077_validation.json"


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def close(left, right, tolerance=5e-8):
    return abs(float(left) - float(right)) <= tolerance


def main():
    source = read(SOURCE)
    result = json.loads(RESULT.read_text())
    scores = read(SCORES)
    register_scores = read(REGISTERS)
    checks = {}
    checks["source_and_state_space"] = (
        len(source) == result["groups"] == 15592
        and sorted({row["wrapper"] for row in source}) == result["wrapper_states"]
        and sorted({row["right_family"] for row in source}) == result["right_family_states"]
        and not any(row["locus"].startswith("f84r") for row in source)
    )
    checks["complete_grid"] = (
        len(scores) == 55
        and sum(row["model"] == "HOST_REGISTER_FACTOR" for row in scores) == 5
        and sum(row["model"] == "RIGHT_GIVEN_WRAPPER" for row in scores) == 25
        and sum(row["model"] == "WRAPPER_GIVEN_RIGHT" for row in scores) == 25
    )
    best = {
        model: min((row for row in scores if row["model"] == model), key=lambda row: float(row["selector_paid_bits"]))
        for model in ("HOST_REGISTER_FACTOR", "RIGHT_GIVEN_WRAPPER", "WRAPPER_GIVEN_RIGHT")
    }
    checks["best_configs"] = all(
        int(best[model]["register_backoff"]) == int(result["best_models"][model]["register_backoff"])
        and str(best[model]["joint_backoff"]) == str(result["best_models"][model]["joint_backoff"])
        and close(best[model]["held_bits"], result["best_models"][model]["held_bits"])
        for model in best
    )
    wrappers = result["wrapper_states"]
    rights = result["right_family_states"]
    selected = {
        "HOST_REGISTER_FACTOR": (16, None),
        "RIGHT_GIVEN_WRAPPER": (16, 64),
        "WRAPPER_GIVEN_RIGHT": (16, 256),
    }
    reconstructed = Counter()
    by_register = defaultdict(Counter)
    folios = sorted({row["physical_folio"] for row in source})
    for held_folio in folios:
        host = defaultdict(lambda: {"n": 0, "w": Counter(), "r": Counter()})
        host_register = defaultdict(lambda: {"n": 0, "w": Counter(), "r": Counter(), "j": Counter()})
        for row in source:
            if row["physical_folio"] == held_folio:
                continue
            h = host[row["page_host"]]
            h["n"] += 1; h["w"][row["wrapper"]] += 1; h["r"][row["right_family"]] += 1
            hr = host_register[row["page_host"], row["register"]]
            hr["n"] += 1; hr["w"][row["wrapper"]] += 1; hr["r"][row["right_family"]] += 1; hr["j"][row["wrapper"], row["right_family"]] += 1
        for row in source:
            if row["physical_folio"] != held_folio:
                continue
            h = host[row["page_host"]]
            hr = host_register[row["page_host"], row["register"]]
            pw = (h["w"][row["wrapper"]] + 0.5) / (h["n"] + 0.5 * len(wrappers))
            pr = (h["r"][row["right_family"]] + 0.5) / (h["n"] + 0.5 * len(rights))
            for model, (register_backoff, joint_backoff) in selected.items():
                pwr = (hr["w"][row["wrapper"]] + register_backoff * pw) / (hr["n"] + register_backoff)
                prr = (hr["r"][row["right_family"]] + register_backoff * pr) / (hr["n"] + register_backoff)
                if model == "HOST_REGISTER_FACTOR":
                    probability = pwr * prr
                elif model == "RIGHT_GIVEN_WRAPPER":
                    probability = pwr * (hr["j"][row["wrapper"], row["right_family"]] + joint_backoff * prr) / (hr["w"][row["wrapper"]] + joint_backoff)
                else:
                    probability = prr * (hr["j"][row["wrapper"], row["right_family"]] + joint_backoff * pwr) / (hr["r"][row["right_family"]] + joint_backoff)
                loss = -math.log2(probability)
                reconstructed[model] += loss
                by_register[model][row["register"]] += loss
    checks["selected_exact_reconstruction"] = all(close(reconstructed[model], result["best_models"][model]["held_bits"]) for model in reconstructed)
    checks["register_reconstruction"] = all(
        close(by_register[row["model"]][row["register"]], row["held_bits"])
        for row in register_scores
    )
    factor_paid = result["best_models"]["HOST_REGISTER_FACTOR"]["selector_paid_bits"]
    right_paid = result["best_models"]["RIGHT_GIVEN_WRAPPER"]["selector_paid_bits"]
    wrapper_paid = result["best_models"]["WRAPPER_GIVEN_RIGHT"]["selector_paid_bits"]
    checks["paid_gains"] = (
        close(factor_paid - right_paid, result["right_given_wrapper_selector_paid_gain_bits"])
        and close(factor_paid - right_paid - 1, result["right_given_wrapper_fully_paid_gain_bits"])
        and close(factor_paid - wrapper_paid, result["wrapper_given_right_selector_paid_gain_bits"])
    )
    checks["register_direction"] = (
        result["right_given_wrapper_positive_registers"] == 2
        and result["wrapper_given_right_positive_registers"] == 3
    )
    checks["headline"] = (
        result["status"] == "WRAPPER_WEAK_REGISTER_DEPENDENTLY_CONDITIONS_RIGHT_FAMILY"
        and result["preferred_generation_order"] == "WRAPPER -> PAGE_HOST -> RIGHT_FAMILY"
    )
    checks["variants"] = {row["variant_id"]: row["status"] for row in read(VARIANTS)} == {
        "V00": "BASELINE", "V01": "PRIMARY", "V02": "DIRECTION_CONTROL", "V03": "NOT_RUN"
    }
    checks["f84_seal"] = not any(result["f84r"].values())
    body = dict(result); claimed = body.pop("result_content_sha256")
    checks["content_hash"] = content_sha(body) == claimed
    checks["bound_hashes"] = all(
        sha(ROOT / name) == digest
        for family in ("inputs", "outputs", "documents", "implementation")
        for name, digest in result[family].items()
    )
    ledger = [row for row in read(LEDGER) if row["checkpoint_id"] == "GDT077_CKPT001"]
    checks["ledger"] = len(ledger) == 1 and ledger[0]["status"] == result["status"] and ledger[0]["result_artifact"] == RESULT.name
    passed = all(checks.values())
    validation = {
        "schema": "GDT077_WRAPPER_RIGHT_CONDITIONAL_COMPATIBILITY_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_SELECTED_MODEL_RECONSTRUCTION" if passed else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independently rebuilds the three selected whole-folio-held models and per-register bits from source groups, checks the full configuration grid, selector-paid gains, direction, variants, seals, hashes and ledger.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
