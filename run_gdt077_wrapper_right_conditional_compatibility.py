#!/usr/bin/env python3
"""GDT077: folio-held directional WRAPPER/RIGHT_FAMILY dependence."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
METHOD = ROOT / "GDT077_WRAPPER_RIGHT_CONDITIONAL_COMPATIBILITY_METHOD.md"
REPORT = ROOT / "GDT077_WRAPPER_RIGHT_CONDITIONAL_COMPATIBILITY_REPORT.md"
SCORES = ROOT / "gdt077_model_scores.tsv"
REGISTERS = ROOT / "gdt077_register_scores.tsv"
VARIANTS = ROOT / "gdt077_variant_log.tsv"
RESULT = ROOT / "gdt077_result.json"

GRID = (1, 4, 16, 64, 256)


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main():
    source = read(SOURCE)
    assert len(source) == 15592 and not any(row["locus"].startswith("f84r") for row in source)
    wrappers = sorted({row["wrapper"] for row in source})
    right_families = sorted({row["right_family"] for row in source})
    assert len(wrappers) == 8 and len(right_families) == 6
    totals = {}
    by_register = defaultdict(dict)
    for register_backoff in GRID:
        totals[("HOST_REGISTER_FACTOR", register_backoff, 0)] = 0.0
        by_register[("HOST_REGISTER_FACTOR", register_backoff, 0)] = Counter()
        for joint_backoff in GRID:
            for model in ("RIGHT_GIVEN_WRAPPER", "WRAPPER_GIVEN_RIGHT"):
                totals[(model, register_backoff, joint_backoff)] = 0.0
                by_register[(model, register_backoff, joint_backoff)] = Counter()
    for held_folio in sorted({row["physical_folio"] for row in source}):
        training = [row for row in source if row["physical_folio"] != held_folio]
        held = [row for row in source if row["physical_folio"] == held_folio]
        host = defaultdict(lambda: {"n": 0, "wrapper": Counter(), "right": Counter()})
        host_register = defaultdict(lambda: {"n": 0, "wrapper": Counter(), "right": Counter(), "joint": Counter()})
        for row in training:
            h = host[row["page_host"]]
            h["n"] += 1
            h["wrapper"][row["wrapper"]] += 1
            h["right"][row["right_family"]] += 1
            hr = host_register[row["page_host"], row["register"]]
            hr["n"] += 1
            hr["wrapper"][row["wrapper"]] += 1
            hr["right"][row["right_family"]] += 1
            hr["joint"][row["wrapper"], row["right_family"]] += 1
        for row in held:
            h = host[row["page_host"]]
            hr = host_register[row["page_host"], row["register"]]
            host_wrapper = (h["wrapper"][row["wrapper"]] + 0.5) / (h["n"] + 0.5 * len(wrappers))
            host_right = (h["right"][row["right_family"]] + 0.5) / (h["n"] + 0.5 * len(right_families))
            for register_backoff in GRID:
                wrapper_probability = (hr["wrapper"][row["wrapper"]] + register_backoff * host_wrapper) / (hr["n"] + register_backoff)
                right_probability = (hr["right"][row["right_family"]] + register_backoff * host_right) / (hr["n"] + register_backoff)
                factor_loss = -math.log2(wrapper_probability * right_probability)
                key = ("HOST_REGISTER_FACTOR", register_backoff, 0)
                totals[key] += factor_loss
                by_register[key][row["register"]] += factor_loss
                for joint_backoff in GRID:
                    conditional_right = (hr["joint"][row["wrapper"], row["right_family"]] + joint_backoff * right_probability) / (hr["wrapper"][row["wrapper"]] + joint_backoff)
                    right_loss = -math.log2(wrapper_probability * conditional_right)
                    key = ("RIGHT_GIVEN_WRAPPER", register_backoff, joint_backoff)
                    totals[key] += right_loss
                    by_register[key][row["register"]] += right_loss
                    conditional_wrapper = (hr["joint"][row["wrapper"], row["right_family"]] + joint_backoff * wrapper_probability) / (hr["right"][row["right_family"]] + joint_backoff)
                    wrapper_loss = -math.log2(right_probability * conditional_wrapper)
                    key = ("WRAPPER_GIVEN_RIGHT", register_backoff, joint_backoff)
                    totals[key] += wrapper_loss
                    by_register[key][row["register"]] += wrapper_loss
    score_rows = []
    for (model, register_backoff, joint_backoff), bits in totals.items():
        configurations = len(GRID) if model == "HOST_REGISTER_FACTOR" else len(GRID) ** 2
        score_rows.append(
            {
                "model": model,
                "register_backoff": register_backoff,
                "joint_backoff": joint_backoff if joint_backoff else "NA",
                "groups": len(source),
                "held_bits": bits,
                "bits_per_group": bits / len(source),
                "selector_configurations": configurations,
                "selector_bits": math.log2(configurations),
                "selector_paid_bits": bits + math.log2(configurations),
            }
        )
    best = {
        model: min((row for row in score_rows if row["model"] == model), key=lambda row: row["selector_paid_bits"])
        for model in ("HOST_REGISTER_FACTOR", "RIGHT_GIVEN_WRAPPER", "WRAPPER_GIVEN_RIGHT")
    }
    register_rows = []
    for model, row in best.items():
        key = (model, int(row["register_backoff"]), 0 if row["joint_backoff"] == "NA" else int(row["joint_backoff"]))
        for register in sorted(by_register[key]):
            baseline_key = (
                "HOST_REGISTER_FACTOR",
                int(best["HOST_REGISTER_FACTOR"]["register_backoff"]),
                0,
            )
            register_rows.append(
                {
                    "model": model,
                    "register": register,
                    "held_bits": by_register[key][register],
                    "gain_vs_best_factor_bits": by_register[baseline_key][register] - by_register[key][register],
                }
            )
    factor = best["HOST_REGISTER_FACTOR"]
    right = best["RIGHT_GIVEN_WRAPPER"]
    wrapper = best["WRAPPER_GIVEN_RIGHT"]
    right_gain = factor["selector_paid_bits"] - right["selector_paid_bits"]
    wrapper_gain = factor["selector_paid_bits"] - wrapper["selector_paid_bits"]
    right_gain_fully_paid = right_gain - 1.0
    right_positive_registers = sum(row["gain_vs_best_factor_bits"] > 0 for row in register_rows if row["model"] == "RIGHT_GIVEN_WRAPPER")
    wrapper_positive_registers = sum(row["gain_vs_best_factor_bits"] > 0 for row in register_rows if row["model"] == "WRAPPER_GIVEN_RIGHT")
    status = "WRAPPER_WEAK_REGISTER_DEPENDENTLY_CONDITIONS_RIGHT_FAMILY" if right_gain_fully_paid > 20 and wrapper_gain < 5 else "WRAPPER_RIGHT_CONDITIONAL_DEPENDENCE_NOT_DIRECTIONAL"
    def clean(rows):
        return [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in rows]
    score_rows.sort(key=lambda row: (row["model"], row["selector_paid_bits"], int(row["register_backoff"]), str(row["joint_backoff"])))
    write(SCORES, clean(score_rows), list(score_rows[0]))
    write(REGISTERS, clean(register_rows), list(register_rows[0]))
    variants = [
        {"variant_id": "V00", "status": "BASELINE", "description": "Host marginals adapted to register; five register-backoff values, selector paid."},
        {"variant_id": "V01", "status": "PRIMARY", "description": "RIGHT_FAMILY conditional on WRAPPER within host+register; 25 configurations, selector paid."},
        {"variant_id": "V02", "status": "DIRECTION_CONTROL", "description": "WRAPPER conditional on RIGHT_FAMILY on the same grid and events."},
        {"variant_id": "V03", "status": "NOT_RUN", "description": "No external annotations, semantics, alternate parser, smoothing values, or f84r."},
    ]
    write(VARIANTS, variants, list(variants[0]))
    report = f"""# GDT077 — WRAPPER/RIGHT_FAMILY conditional compatibility

## Outcome

**{status}**

The best selector-paid host+register factor model uses register backoff
{factor['register_backoff']} and costs {factor['selector_paid_bits']:.3f} bits.
Conditioning RIGHT_FAMILY on WRAPPER selects backoffs
{right['register_backoff']}/{right['joint_backoff']} and saves
{right_gain:+.3f} grid-selector-paid bits, or {right_gain_fully_paid:+.3f}
after another bit for choosing between the two directions.  Reversing the direction selects
{wrapper['register_backoff']}/{wrapper['joint_backoff']} and saves only
{wrapper_gain:+.3f} bits.

The dependency is therefore asymmetric, small, and register-dependent.  The
RIGHT-given-WRAPPER gain is positive in only {right_positive_registers}/5
registers, concentrated in Herbal A and Stars/Recipe B; the other three are
slightly negative.  After PAGE_HOST and register,
WRAPPER retains predictive information about the right renderer, while the
right renderer contributes almost nothing to WRAPPER prediction.  This favors
the formal generation order `WRAPPER -> PAGE_HOST -> RIGHT_FAMILY` with
host/register compatibility, rather than independent slot draws.  It does not
establish linguistic morphology, a part of speech, or a meaning.  Complete
configurations and per-register gains are exported.  No semantic class, role,
gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation
is assigned.  f84r was excluded and not opened, retained, queried, joined,
scored, or targeted.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT077_WRAPPER_RIGHT_CONDITIONAL_COMPATIBILITY_RESULT_V1",
        "status": status,
        "groups": len(source),
        "wrapper_states": wrappers,
        "right_family_states": right_families,
        "grid": list(GRID),
        "best_models": best,
        "right_given_wrapper_selector_paid_gain_bits": right_gain,
        "right_given_wrapper_fully_paid_gain_bits": right_gain_fully_paid,
        "wrapper_given_right_selector_paid_gain_bits": wrapper_gain,
        "right_given_wrapper_positive_registers": right_positive_registers,
        "wrapper_given_right_positive_registers": wrapper_positive_registers,
        "preferred_generation_order": "WRAPPER -> PAGE_HOST -> RIGHT_FAMILY",
        "interpretation": "Weak asymmetric formal compatibility after PAGE_HOST and register; not fully independent slots and not whole-form memorization.",
        "claim_ceiling": "No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
        "inputs": {SOURCE.name: sha(SOURCE), "gdt062_result.json": sha(ROOT / "gdt062_result.json"), "gdt064_result.json": sha(ROOT / "gdt064_result.json"), "gdt066_result.json": sha(ROOT / "gdt066_result.json"), "gdt076_result.json": sha(ROOT / "gdt076_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {SCORES.name: sha(SCORES), REGISTERS.name: sha(REGISTERS), VARIANTS.name: sha(VARIANTS)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "best": best, "right_gain": right_gain, "wrapper_gain": wrapper_gain}, sort_keys=True))


if __name__ == "__main__":
    main()
