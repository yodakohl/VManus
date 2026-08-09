#!/usr/bin/env python3
"""Run target-free calibration of the second-member increment."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np

import source_native_opening_second_core as core


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL = RESULTS / "source_native_opening_second_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_second_capacity_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_SECOND_PREFLIGHT_SPEC.md"
CORE = BASE / "source_native_opening_second_core.py"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_second_preflight.json"
REPORT = RESULTS / "source_native_opening_second_preflight_report.md"
FUTURE_TARGET = RESULTS / "source_native_opening_second_target.json"
FUTURE_REPORT = RESULTS / "source_native_opening_second_target_report.md"

FROZEN = {
    PANEL: "46f0c8ad22880b870afc54d96852781b4bea9ebdc885dc1164c1da742a7bc581",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    CAPACITY_VALIDATION: "ac78bb1b6f7a232ecb3415073442188f17f8f976cc718373cc80edde9c3d54b7",
    SPEC: "96a192dc4400643417e10f815dcea3a67abd6b64ab8429096205623f2885aecb",
    CORE: "514416f974014d6bcd86bb1103fa306dc5c7ce05468d1fdfe1f34102d9c622c9",
}

TASKS = (
    [("NULL", world) for world in range(64)]
    + [("GLOBAL_SECOND", 100 + world) for world in range(8)]
    + [("BASELINE_ONLY", 200 + world) for world in range(8)]
    + [("ONE_FOLIO", 300 + world) for world in range(8)]
    + [("FOLIO_RANDOM", 400 + world) for world in range(8)]
    + [("ONE_BASE", 500 + world) for world in range(8)]
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install(path: Path, data: bytes) -> None:
    if path.exists():
        raise FileExistsError(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as handle:
        temporary = Path(handle.name); handle.write(data)
    try:
        if path.exists(): raise FileExistsError(path)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    if OUT.exists() or REPORT.exists(): raise SystemExit("refusing overwrite")
    if FUTURE_TARGET.exists() or FUTURE_REPORT.exists(): raise SystemExit("future target exists")
    for path, expected in FROZEN.items():
        if sha(path) != expected: raise SystemExit(f"frozen mismatch: {path.name}")
    capacity = json.loads(CAPACITY_VALIDATION.read_text())
    if capacity["status"] != "PASS_INDEPENDENT_SECOND_MEMBER_CAPACITY_RECONSTRUCTION" or not all(capacity["gates"].values()): raise ValueError("capacity")
    panel = core.load_panel(PANEL, QUOTAS)
    null = core.quota_labels(panel, 2048, "PREFLIGHT_NULL")
    observed = np.asarray([core.plant(panel, mode, world) for mode, world in TASKS])
    values = core.summaries(panel, observed, null)
    records = [{"mode":mode,"world":world,"label_sha256":core.digest(labels),**summary,"PASS":core.passes(summary,.01)} for (mode,world),labels,summary in zip(TASKS,observed,values)]
    modes = ("NULL","GLOBAL_SECOND","BASELINE_ONLY","ONE_FOLIO","FOLIO_RANDOM","ONE_BASE")
    counts = {mode:{"worlds":sum(candidate==mode for candidate,_ in TASKS),"passes":sum(row["PASS"] for row in records if row["mode"]==mode)} for mode in modes}
    large_null = core.quota_labels(panel,8192,"PREFLIGHT_NULL")
    large_observed = np.asarray([core.plant(panel,"NULL",0),core.plant(panel,"GLOBAL_SECOND",100)])
    large_values = core.summaries(panel,large_observed,large_null)
    large = {"NULL_0":{**large_values[0],"PASS":core.passes(large_values[0],.01)},"GLOBAL_SECOND_100":{**large_values[1],"PASS":core.passes(large_values[1],.01)}}
    small_global = next(row for row in records if row["mode"]=="GLOBAL_SECOND" and row["world"]==100)
    mutations = {}
    for name,candidate in (("missing_row",observed[:1,:-1]),("nonbinary",observed[:1].copy()),("quota_drift",observed[:1].copy())):
        if name=="nonbinary": candidate[0,0]=.5
        if name=="quota_drift": candidate[0,panel.cell_rows[0][0]]=1-candidate[0,panel.cell_rows[0][0]]
        try: core.score(panel,candidate)
        except ValueError: mutations[name]=True
        else: mutations[name]=False
    text = PANEL.read_text(); marker="\t1\n"
    if marker not in text: raise ValueError("eligibility fixture")
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="",dir=RESULTS,prefix="second_mutation_",delete=False) as handle:
        altered=Path(handle.name);handle.write(text.replace(marker,"\t0\n",1))
    try:
        try: core.load_panel(altered,QUOTAS)
        except ValueError: mutations["eligibility_drift"]=True
        else: mutations["eligibility_drift"]=False
    finally: altered.unlink(missing_ok=True)
    gates = {
        "zero_of_64_null_passes":counts["NULL"]["passes"]==0,
        "at_least_7_of_8_global_second_passes":counts["GLOBAL_SECOND"]["passes"]>=7,
        "zero_of_8_baseline_only_passes":counts["BASELINE_ONLY"]["passes"]==0,
        "zero_of_8_one_folio_passes":counts["ONE_FOLIO"]["passes"]==0,
        "zero_of_8_folio_random_passes":counts["FOLIO_RANDOM"]["passes"]==0,
        "zero_of_8_one_base_passes":counts["ONE_BASE"]["passes"]==0,
        "target_size_null_rejects":not large["NULL_0"]["PASS"],
        "target_size_global_second_passes":large["GLOBAL_SECOND_100"]["PASS"],
        "target_size_decisions_match":large["NULL_0"]["PASS"]==records[0]["PASS"] and large["GLOBAL_SECOND_100"]["PASS"]==small_global["PASS"],
        "mutation_guards":all(mutations.values()),
        "future_target_absent":not FUTURE_TARGET.exists() and not FUTURE_REPORT.exists(),
    }
    passed=all(gates.values())
    status="PASS_TARGET_FREE_SECOND_MEMBER_PREFLIGHT" if passed else "STOP_SECOND_MEMBER_CALIBRATION"
    decision="GO_INDEPENDENTLY_VALIDATE_SECOND_MEMBER_PREFLIGHT" if passed else "DO_NOT_OPEN_SECOND_MEMBER_TARGET"
    result={
        "experiment":"SOURCE_NATIVE_OPENING_SECOND_PREFLIGHT","status":status,"decision":decision,
        "inputs":{path.name:sha(path) for path in (*FROZEN,RUNNER)},"assignments":2048,"target_size_assignments":8192,
        "records":records,"counts":counts,"target_size_checks":large,"null_label_orbit_sha256":core.digest(null),
        "target_size_null_label_orbit_sha256":core.digest(large_null),"mutations":mutations,"gates":gates,
        "source_sta_table_opened":False,"prior_target_artifact_opened":False,"real_operation_labels_accessed":0,
        "real_target_scores_computed":0,"event_loci_or_pages_stored":0,"english_glosses":0,
        "claim_ceiling":"Target-free synthetic calibration for a second-member increment beyond fixed coarse base and exact first onset only; no longer dependency, morphology, pronunciation, wordhood, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    report=f"""# Second-member incremental synthetic preflight

Status: **{status}**

At 2,048 assignments calibration yields **{counts['NULL']['passes']}/64** null,
**{counts['GLOBAL_SECOND']['passes']}/8** global-second,
**{counts['BASELINE_ONLY']['passes']}/8** baseline-only,
**{counts['ONE_FOLIO']['passes']}/8** one-folio,
**{counts['FOLIO_RANDOM']['passes']}/8** folio-random, and
**{counts['ONE_BASE']['passes']}/8** one-base passes. Representative decisions
are unchanged at 8,192 assignments.

Decision: **{decision}**. No source STA row, prior target artifact, real
operation label, or real target score was opened. This supplies no longer
dependency, morphology, meaning, plaintext, or translation.
"""
    install(OUT,(json.dumps(result,indent=2,sort_keys=True)+"\n").encode())
    try: install(REPORT,report.encode())
    except Exception: OUT.unlink(missing_ok=True);raise
    print(json.dumps({"status":status,"decision":decision,"counts":counts,"gates":gates},sort_keys=True))


if __name__=="__main__":main()
