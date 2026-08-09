#!/usr/bin/env python3
"""Execute the single frozen cho/che paragraph-scope target test."""

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
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

from cho_che_scope_core import READINGS, load_panels, panel_capacity, permutation_summary


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
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "cho_che_scope_target.json"
REPORT = RESULTS / "cho_che_scope_target_report.md"

SAFE_FROZEN = {
    MASKED: "41f8b517419d2215a97db9ce245c5639f383b11c41d8c1377a245dea8e37abf3",
    MASKED_VALIDATION: "e7d37a23ca199e421946fab0c42f4547aade0a5fa27579b1e9e69518c0d376ec",
    CORE: "b77dd67d49c4e173d16bce2409c8f691e9cf7aae30b1333ee0eeffd9a98193b8",
    PREFLIGHT_SPEC: "b2b51a91b999ae926170a76ce8ffe8f5b8a7d01f3e71200e93b26cefce900c94",
    PREFLIGHT_AMENDMENT: "36c4bd9817a9583bc786b50a952b65b3d15caacd7077ccaca481ad28cf96ffc0",
    PREFLIGHT: "3748e03fb9217e7c7d389b887611407fc323a8b5526e7a369ac94f90aae5062e",
    PREFLIGHT_VALIDATION: "cc1a92ae052cf3b1e880732713c4b00362173f49ddfdfa177b45ddc28ce1de35",
    TARGET_SOURCE_VALIDATION: "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    SPEC: "5f6406400991877693d38e701a9ac307d463ec55fba1e82c833cd70d2f998327",
}
TARGET_HASH = "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840"
ASSIGNMENTS = 8191
PANELS = None
LABELS = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_pass(summaries: dict) -> bool:
    zl = summaries["ZL3b"]["local"]
    if not (zl["effect"] >= .10 and max(zl["p_by_ensemble"].values()) <= .05 and zl["minimum_leave_one_folio_out"] >= .05 and zl["positive_folios"] >= 21 and zl["folios"] == 35 and zl["max_abs_contribution_fraction"] <= .15):
        return False
    return all(summaries[edition]["local"]["effect"] >= .05 and summaries[edition]["local"]["minimum_leave_one_folio_out"] > 0 and summaries[edition]["local"]["max_abs_contribution_fraction"] <= .18 for edition in ("IT2a", "RF1b"))


def boundary_pass(summaries: dict) -> bool:
    zl = summaries["ZL3b"]["boundary"]
    if not (zl["effect"] >= .10 and max(zl["p_by_ensemble"].values()) <= .05 and zl["minimum_leave_one_folio_out"] >= .05 and zl["positive_folios"] >= 27 and zl["folios"] == 45 and zl["max_abs_contribution_fraction"] <= .15):
        return False
    return all(summaries[edition]["boundary"]["effect"] >= .05 and summaries[edition]["boundary"]["minimum_leave_one_folio_out"] > 0 and summaries[edition]["boundary"]["max_abs_contribution_fraction"] <= .18 for edition in ("IT2a", "RF1b"))


def score_reading(edition: str) -> tuple[str, dict]:
    return edition, permutation_summary(PANELS[edition], LABELS[edition], ASSIGNMENTS, "CHO_CHE_SCOPE_TARGET", chunk=256)


def install_pair(result_bytes: bytes, report_bytes: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("target artifact already exists")
    with tempfile.TemporaryDirectory(prefix="cho_che_scope_target_", dir=RESULTS) as directory:
        result_stage = Path(directory) / "result.json"
        report_stage = Path(directory) / "report.md"
        result_stage.write_bytes(result_bytes)
        report_stage.write_bytes(report_bytes)
        if OUT.exists() or REPORT.exists():
            raise FileExistsError("target artifact appeared during execution")
        os.link(result_stage, OUT)
        try:
            os.link(report_stage, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def main() -> None:
    global PANELS, LABELS
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing a second cho/che scope target run")
    for path, expected in SAFE_FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen prescore input mismatch: {path.name}")
    if json.loads(MASKED_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_COMPLETE_MASKED_UNIVERSE_RECONSTRUCTION":
        raise SystemExit("masked universe validation is not PASS")
    preflight = json.loads(PREFLIGHT.read_text())
    if preflight["status"] != "PASS_TARGET_FREE_SCOPE_PREFLIGHT_V2" or preflight["decision"] != "GO_FREEZE_ONE_TARGET_RUN" or not all(preflight["gates"].values()):
        raise SystemExit("synthetic preflight does not authorize target")
    preflight_validation = json.loads(PREFLIGHT_VALIDATION.read_text())
    if preflight_validation["status"] != "PASS_INDEPENDENT_FULL_V2_PREFLIGHT_RECONSTRUCTION" or not preflight_validation["target_outputs_absent"]:
        raise SystemExit("independent preflight validation does not authorize target")
    if sha(TARGET_SOURCE) != TARGET_HASH:
        raise SystemExit("target source hash mismatch")
    if json.loads(TARGET_SOURCE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION":
        raise SystemExit("target source validation is not PASS")

    PANELS = load_panels(MASKED)
    capacities = {edition: panel_capacity(PANELS[edition]) for edition in READINGS}
    if capacities != preflight["capacities"]:
        raise ValueError("target panel capacity differs from preflight")

    with TARGET_SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    source = {row["source_group_id"]: row for row in source_rows}
    if len(source) != len(source_rows):
        raise ValueError("duplicate target source-group ID")

    LABELS = {}
    outcome_counts = {}
    physical_outcomes = {}
    joined_rows = 0
    for edition in READINGS:
        values = np.empty(len(PANELS[edition].rows), dtype=np.uint8)
        physical_outcomes[edition] = {}
        for index, masked in enumerate(PANELS[edition].rows):
            aligned = source.get(masked["source_group_id"])
            if aligned is None or aligned["edition"] != edition or aligned["alternative_site_count"] != "0":
                raise ValueError("target join or eligibility mismatch")
            projection = aligned["nearest_basic_eva_primary"]
            if re.fullmatch(r"[a-z]+", projection) is None:
                raise ValueError("target projection is not strict lowercase basic EVA")
            sites = list(re.finditer(r"(?:ch|sh)([oe])", projection))
            if len(sites) != 1:
                raise ValueError("target selected-site count mismatch")
            remasked = re.sub(r"((?:ch|sh))[oe]", r"\1X", projection)
            if remasked != masked["masked_template"]:
                raise ValueError("target remasking mismatch")
            value = 1 if sites[0].group(1) == "o" else 0
            values[index] = value
            physical_outcomes[edition][masked["physical_event_key"]] = value
            joined_rows += 1
        LABELS[edition] = values
        outcome_counts[edition] = {"o": int(values.sum()), "e": int(len(values) - values.sum()), "events": len(values)}
    if joined_rows != 30160:
        raise ValueError("target joined-row count mismatch")

    common_keys = set.intersection(*(set(physical_outcomes[edition]) for edition in READINGS))
    patterns = Counter("".join(str(physical_outcomes[edition][key]) for edition in READINGS) for key in common_keys)
    agreement = {
        "common_physical_events": len(common_keys),
        "all_three_exact": sum(count for pattern, count in patterns.items() if pattern in {"000", "111"}),
        "pattern_counts": dict(sorted(patterns.items())),
    }

    with mp.get_context("fork").Pool(3) as pool:
        scored = pool.map(score_reading, READINGS)
    summaries = dict(scored)
    for edition in READINGS:
        for target in ("local", "boundary"):
            values = summaries[edition][target]
            if not all(np.isfinite(value) for value in (values["effect"], values["minimum_leave_one_folio_out"], values["max_abs_contribution_fraction"], *values["p_by_ensemble"].values())):
                raise ValueError("nonfinite target score")
    local = local_pass(summaries)
    boundary = boundary_pass(summaries)
    if local and boundary:
        status = "CONFIRM_LOCAL_AND_DISTANCE_CONTROLLED_EDITORIAL_BOUNDARY_ASSOCIATION"
        decision = "RETAIN_LOCAL_AND_BOUNDARY_FORMAL_SCOPE"
    elif local:
        status = "CONFIRM_MARKED_SPAN_LOCAL_PERSISTENCE_BOUNDARY_UNCONFIRMED"
        decision = "RETAIN_LOCAL_FORMAL_SCOPE_ONLY"
    else:
        status = "NONCONFIRM_CHO_CHE_MARKED_SPAN_LOCAL_SCOPE"
        decision = "CLOSE_EXACT_SCOPE_TEST_WITHOUT_RETUNING"

    result = {
        "experiment": "CHO_CHE_SCOPE_TARGET",
        "status": status,
        "inputs": {path.name: sha(path) for path in (*SAFE_FROZEN, TARGET_SOURCE, RUNNER)},
        "assignments_per_ensemble": ASSIGNMENTS,
        "capacities": capacities,
        "outcome_counts": outcome_counts,
        "cross_reading_agreement": agreement,
        "summaries": summaries,
        "gates": {"LOCAL_PASS": local, "BOUNDARY_PASS": boundary},
        "decision": decision,
        "target_rows_accessed": joined_rows,
        "target_scores_computed": 3,
        "event_level_outcomes_stored": 0,
        "unmasked_surfaces_stored": 0,
        "english_glosses": 0,
        "claim_ceiling": (
            "Formal marked-span-aligned local persistence and, only if its separate gate passes, "
            "a distance-controlled association with ZL editorial paragraph boundaries. No authorial "
            "paragraph, vowel, consonant, sound, word, language, cipher operation, topic, meaning, "
            "plaintext, or translation follows."
        ),
    }
    lines = []
    for edition in READINGS:
        local_value = summaries[edition]["local"]
        boundary_value = summaries[edition]["boundary"]
        lines.append(
            f"- {edition}: local {local_value['effect']:+.6f}, p(max) "
            f"{max(local_value['p_by_ensemble'].values()):.6f}; boundary "
            f"{boundary_value['effect']:+.6f}, p(max) "
            f"{max(boundary_value['p_by_ensemble'].values()):.6f}."
        )
    report = f"""# `cho/che` paragraph-scope target

Status: **{status}**

The one authorized target join scored all **{joined_rows:,}** frozen masked
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
    install_pair((json.dumps(result, indent=2, sort_keys=True) + "\n").encode(), report.encode())
    print(json.dumps({"status": status, "gates": result["gates"], "decision": decision}, sort_keys=True))


if __name__ == "__main__":
    main()
