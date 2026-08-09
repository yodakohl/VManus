#!/usr/bin/env python3
"""Production-free reconstruction of the one-time cho/che scope target."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import multiprocessing as mp
import re
from collections import Counter
from pathlib import Path

import numpy as np

import validate_cho_che_scope_synthetic_preflight_v2 as clean


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
MASKED = RESULTS / "cho_che_scope_masked_events.tsv"
MASKED_VALIDATION = RESULTS / "cho_che_scope_masked_universe_validation.json"
CORE = BASE / "cho_che_scope_core.py"
PREFLIGHT_SPEC = BASE / "CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_SPEC.md"
PREFLIGHT_AMENDMENT = BASE / "CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_V2_AMENDMENT.md"
PREFLIGHT = RESULTS / "cho_che_scope_synthetic_preflight_v2.json"
PREFLIGHT_VALIDATION = RESULTS / "cho_che_scope_synthetic_preflight_v2_validation.json"
TARGET_SOURCE = RESULTS / "source_sta_group_alignment.tsv"
TARGET_SOURCE_VALIDATION = RESULTS / "source_sta_group_alignment_validation.json"
SPEC = BASE / "CHO_CHE_SCOPE_TARGET_SPEC.md"
RUNNER = BASE / "run_cho_che_scope_target.py"
CLEAN_VALIDATOR = BASE / "validate_cho_che_scope_synthetic_preflight_v2.py"
PRODUCTION = RESULTS / "cho_che_scope_target.json"
PRODUCTION_REPORT = RESULTS / "cho_che_scope_target_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "cho_che_scope_target_validation.json"
REPORT = RESULTS / "cho_che_scope_target_validation_report.md"

HASHES = {
    MASKED: "41f8b517419d2215a97db9ce245c5639f383b11c41d8c1377a245dea8e37abf3",
    MASKED_VALIDATION: "e7d37a23ca199e421946fab0c42f4547aade0a5fa27579b1e9e69518c0d376ec",
    CORE: "b77dd67d49c4e173d16bce2409c8f691e9cf7aae30b1333ee0eeffd9a98193b8",
    PREFLIGHT_SPEC: "b2b51a91b999ae926170a76ce8ffe8f5b8a7d01f3e71200e93b26cefce900c94",
    PREFLIGHT_AMENDMENT: "36c4bd9817a9583bc786b50a952b65b3d15caacd7077ccaca481ad28cf96ffc0",
    PREFLIGHT: "3748e03fb9217e7c7d389b887611407fc323a8b5526e7a369ac94f90aae5062e",
    PREFLIGHT_VALIDATION: "cc1a92ae052cf3b1e880732713c4b00362173f49ddfdfa177b45ddc28ce1de35",
    TARGET_SOURCE: "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    TARGET_SOURCE_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    SPEC: "5f6406400991877693d38e701a9ac307d463ec55fba1e82c833cd70d2f998327",
    RUNNER: "98a9232f1e4c6ff8e7db67164928bb68ba3935de73ba322c36fc586186c8b468",
    CLEAN_VALIDATOR: "9182e9caad0ae1caf96bc3fc3d7ff8b398fed607d9a4682955b6b0cd42196342",
    PRODUCTION: "e0293079676ea6a584f48864ed58fa24292f5c76d6054deedd54c3c32cabe3cb",
    PRODUCTION_REPORT: "1efd5df768864eca22d905a2bec253c295cfedd79f88d765f6f52286e44d6393",
}
READINGS = ("ZL3b", "IT2a", "RF1b")
PANELS = None
LABELS = None
CHECKS = 0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def worker(edition):
    return edition, clean.summary(PANELS[edition], LABELS[edition], 8191, "CHO_CHE_SCOPE_TARGET")


def compare(actual, expected, path="root"):
    global CHECKS
    CHECKS += 1
    if isinstance(actual, dict) and isinstance(expected, dict):
        if set(actual) != set(expected):
            raise AssertionError(f"key mismatch {path}")
        for key in actual:
            compare(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(actual, list) and isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(f"length mismatch {path}")
        for i, (left, right) in enumerate(zip(actual, expected)):
            compare(left, right, f"{path}[{i}]")
    elif isinstance(actual, (int, float)) and isinstance(expected, (int, float)) and not isinstance(actual, bool) and not isinstance(expected, bool):
        if abs(float(actual) - float(expected)) > 1e-12:
            raise AssertionError(f"numeric mismatch {path}: {actual} != {expected}")
    elif actual != expected:
        raise AssertionError(f"value mismatch {path}: {actual} != {expected}")


def main():
    global PANELS, LABELS, CHECKS
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite target validation")
    for path, expected in HASHES.items():
        CHECKS += 1
        if sha(path) != expected:
            raise AssertionError(f"hash {path.name}")
    if json.loads(MASKED_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_COMPLETE_MASKED_UNIVERSE_RECONSTRUCTION":
        raise AssertionError("masked validation")
    if json.loads(PREFLIGHT_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_FULL_V2_PREFLIGHT_RECONSTRUCTION":
        raise AssertionError("preflight validation")
    if json.loads(TARGET_SOURCE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION":
        raise AssertionError("source validation")

    PANELS = clean.build_panels()
    with TARGET_SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    source = {row["source_group_id"]: row for row in source_rows}
    if len(source) != len(source_rows):
        raise AssertionError("source IDs")
    LABELS = {}
    counts = {}
    by_physical = {}
    joined = 0
    for edition in READINGS:
        panel = PANELS[edition]
        values = np.empty(len(panel["rows"]), dtype=np.uint8)
        by_physical[edition] = {}
        for index, masked in enumerate(panel["rows"]):
            aligned = source[masked["source_group_id"]]
            if aligned["edition"] != edition or aligned["alternative_site_count"] != "0":
                raise AssertionError("join eligibility")
            projection = aligned["nearest_basic_eva_primary"]
            if re.fullmatch(r"[a-z]+", projection) is None:
                raise AssertionError("projection")
            sites = list(re.finditer(r"(?:ch|sh)([oe])", projection))
            if len(sites) != 1:
                raise AssertionError("site count")
            if re.sub(r"((?:ch|sh))[oe]", r"\1X", projection) != masked["masked_template"]:
                raise AssertionError("remasking")
            value = int(sites[0].group(1) == "o")
            values[index] = value
            if masked["physical_event_key"] in by_physical[edition]:
                raise AssertionError("physical event duplicate")
            by_physical[edition][masked["physical_event_key"]] = value
            joined += 1
        LABELS[edition] = values
        counts[edition] = {"o": int(values.sum()), "e": int(len(values)-values.sum()), "events": len(values)}
    if joined != 30160:
        raise AssertionError("join total")
    common = set.intersection(*(set(by_physical[edition]) for edition in READINGS))
    patterns = Counter("".join(str(by_physical[edition][key]) for edition in READINGS) for key in common)
    agreement = {"common_physical_events": len(common), "all_three_exact": sum(value for key, value in patterns.items() if key in {"000", "111"}), "pattern_counts": dict(sorted(patterns.items()))}

    with mp.get_context("fork").Pool(3) as pool:
        summaries = dict(pool.map(worker, READINGS))
    summaries = {edition: {"edition": edition, "assignments_per_ensemble": 8191, **summaries[edition]} for edition in READINGS}
    local = clean.lpass(summaries)
    boundary = clean.bpass(summaries)
    status = "CONFIRM_LOCAL_AND_DISTANCE_CONTROLLED_EDITORIAL_BOUNDARY_ASSOCIATION" if local and boundary else ("CONFIRM_MARKED_SPAN_LOCAL_PERSISTENCE_BOUNDARY_UNCONFIRMED" if local else "NONCONFIRM_CHO_CHE_MARKED_SPAN_LOCAL_SCOPE")
    decision = "RETAIN_LOCAL_AND_BOUNDARY_FORMAL_SCOPE" if local and boundary else ("RETAIN_LOCAL_FORMAL_SCOPE_ONLY" if local else "CLOSE_EXACT_SCOPE_TEST_WITHOUT_RETUNING")

    production = json.loads(PRODUCTION.read_text())
    compare(counts, production["outcome_counts"], "counts")
    compare(agreement, production["cross_reading_agreement"], "agreement")
    compare(summaries, production["summaries"], "summaries")
    compare({"LOCAL_PASS": local, "BOUNDARY_PASS": boundary}, production["gates"], "gates")
    compare(status, production["status"], "status")
    compare(decision, production["decision"], "decision")
    expected_inputs = {path.name: sha(path) for path in (MASKED, MASKED_VALIDATION, CORE, PREFLIGHT_SPEC, PREFLIGHT_AMENDMENT, PREFLIGHT, PREFLIGHT_VALIDATION, TARGET_SOURCE_VALIDATION, SPEC, TARGET_SOURCE, RUNNER)}
    compare(expected_inputs, production["inputs"], "inputs")
    if production["target_rows_accessed"] != 30160 or production["target_scores_computed"] != 3 or production["event_level_outcomes_stored"] != 0 or production["unmasked_surfaces_stored"] != 0 or production["english_glosses"] != 0:
        raise AssertionError("output ceiling")

    lines = []
    for edition in READINGS:
        lv, bv = summaries[edition]["local"], summaries[edition]["boundary"]
        lines.append(f"- {edition}: local {lv['effect']:+.6f}, p(max) {max(lv['p_by_ensemble'].values()):.6f}; boundary {bv['effect']:+.6f}, p(max) {max(bv['p_by_ensemble'].values()):.6f}.")
    expected_report = f"""# `cho/che` paragraph-scope target

Status: **{status}**

The one authorized target join scored all **{joined:,}** frozen masked
events with 8,191 corrected rotations in each of two ensembles.

{os.linesep.join(lines)}

`LOCAL_PASS` is **{str(local).lower()}** and `BOUNDARY_PASS` is
**{str(boundary).lower()}**. The decision is **{decision}**. The three manual
readings are alternate descriptions, not replications.

No event-level outcomes or unmasked surfaces are stored. This result concerns
only formal construction-site scope relative to ZL editorial layout. It does
not establish an authorial paragraph, vowel, consonant, sound, word, language,
cipher operation, topic, meaning, plaintext, or translation.
"""
    if PRODUCTION_REPORT.read_text() != expected_report:
        raise AssertionError("report bytes")
    CHECKS += 1
    result = {
        "experiment": "CHO_CHE_SCOPE_TARGET_VALIDATION",
        "status": "PASS_PRODUCTION_FREE_TARGET_NONCONFIRM_RECONSTRUCTION",
        "checks": CHECKS,
        "validator_sha256": sha(VALIDATOR), "production_sha256": sha(PRODUCTION),
        "target_rows_reconstructed": joined, "reading_scores_reconstructed": 3,
        "gates": {"LOCAL_PASS": local, "BOUNDARY_PASS": boundary}, "decision": decision,
        "event_level_outcomes_stored": 0, "unmasked_surfaces_stored": 0, "english_glosses": 0,
        "failures": [], "claim_ceiling": production["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    REPORT.write_text(f"""# `cho/che` paragraph-scope target validation

Status: **{result['status']}**

A production-free implementation rejoined all **{joined:,}** masked events,
reconstructed the complete binary outcome vector in each reading, all 8,191
rotations under both ensembles, every local and boundary statistic, gate,
decision, input binding, and exact report in **{CHECKS:,}** checks.

The frozen result is a nonconfirmation: local effects are only
{summaries['ZL3b']['local']['effect']:+.6f} ZL,
{summaries['IT2a']['local']['effect']:+.6f} IT, and
{summaries['RF1b']['local']['effect']:+.6f} RF; boundary effects are negative
in all readings. This closes only the exact scope test and supplies no word,
meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": CHECKS, "decision": decision}, sort_keys=True))


if __name__ == "__main__":
    main()
