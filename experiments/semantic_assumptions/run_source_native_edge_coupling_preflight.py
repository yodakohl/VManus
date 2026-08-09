#!/usr/bin/env python3
"""Run the target-free source-native edge-coupling synthetic preflight."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"]="1"; os.environ["OMP_NUM_THREADS"]="1"; os.environ["MKL_NUM_THREADS"]="1"

import csv, hashlib, json, multiprocessing as mp, tempfile
from pathlib import Path
import numpy as np

from source_native_edge_coupling_core import load_panel, passes, score, synthetic_outcomes

BASE=Path(__file__).resolve().parent; RESULTS=BASE/"results"
PANEL_PATH=RESULTS/"source_native_edge_coupling_masked.tsv"
CAPACITY_VALIDATION=RESULTS/"source_native_edge_coupling_capacity_validation.json"
CORE=BASE/"source_native_edge_coupling_core.py"; SPEC=BASE/"SOURCE_NATIVE_EDGE_COUPLING_TEST_SPEC.md"; RUNNER=Path(__file__).resolve()
OUT=RESULTS/"source_native_edge_coupling_preflight.json"; REPORT=RESULTS/"source_native_edge_coupling_preflight_report.md"
TARGET_SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv"; TARGET_OUT=RESULTS/"source_native_edge_coupling_target.json"; TARGET_REPORT=RESULTS/"source_native_edge_coupling_target_report.md"
FROZEN={PANEL_PATH:"db78519f12283f6ac2ae30e0e8898c769f1491f8d48dae1733b5de703154e82c",CAPACITY_VALIDATION:"889f55a0763703c25d9589d1c656e960bc9ff264e20e72deed1a85b6c3af69a5",CORE:"c7ab314c49b9e81c4eafe5d5056fa46dfc68f5dcf63c8933504861e26d267349"}
PANEL=None

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def mutation_controls():
    with PANEL_PATH.open(encoding="utf-8",newline="") as handle:
        reader=csv.DictReader(handle,delimiter="\t"); fields=list(reader.fieldnames or ()); rows=list(reader)
    def rejects(names,values,label):
        with tempfile.TemporaryDirectory(prefix="edge_coupling_mutation_") as directory:
            path=Path(directory)/f"{label}.tsv"
            with path.open("x",encoding="utf-8",newline="") as handle:
                writer=csv.DictWriter(handle,fieldnames=names,delimiter="\t",lineterminator="\n"); writer.writeheader(); writer.writerows(values)
            try: load_panel(path)
            except (ValueError,KeyError): return True
            return False
    duplicate=[dict(row) for row in rows]; duplicate[-1]["unit_id"]=duplicate[-2]["unit_id"]
    extra=fields+["closing_family"]; exposed=[dict(row,closing_family="A") for row in rows]
    missing=[field for field in fields if field!="opening_family"]; missing_rows=[{field:row[field] for field in missing} for row in rows]
    return {"duplicate_unit_rejected":rejects(fields,duplicate,"duplicate"),"target_field_rejected":rejects(extra,exposed,"target"),"missing_predictor_rejected":rejects(missing,missing_rows,"missing")}
def task(value):
    mode,strength,world=value; result=score(PANEL,synthetic_outcomes(PANEL,world,mode,strength))
    if not all(np.isfinite(v) for v in (result["effect_equal_folio"],result["effect_equal_row"],result["sign_p"],result["minimum_leave_one_folio_out"],result["max_abs_contribution_fraction"],*(x for c in result["currier"].values() for x in (c["effect_equal_folio"],c["sign_p"],c["minimum_leave_one_folio_out"])))): raise ValueError("nonfinite control")
    return {"mode":mode,"strength":strength,"world":world,"passes":passes(result),"result":result}

def main():
    global PANEL
    if OUT.exists() or REPORT.exists(): raise SystemExit("refusing to overwrite edge-coupling preflight")
    if TARGET_OUT.exists() or TARGET_REPORT.exists(): raise SystemExit("target artifact exists before preflight")
    for path,expected in FROZEN.items():
        if sha(path)!=expected: raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"]!="PASS_INDEPENDENT_TARGET_MASKED_CAPACITY_RECONSTRUCTION": raise SystemExit("capacity validation is not PASS")
    PANEL=load_panel(PANEL_PATH)
    tasks=[("NULL",0.0,w) for w in range(64)]+[("COUPLED",.2,w) for w in range(8)]+[("ONE_FOLIO",.8,w) for w in range(8)]+[("FOLIO_RANDOM",.8,w) for w in range(8)]
    with mp.get_context("fork").Pool(32) as pool: worlds=pool.map(task,tasks)
    worlds.sort(key=lambda row:(row["mode"],row["strength"],row["world"]))
    select=lambda mode:[row for row in worlds if row["mode"]==mode]
    null,coupled,one,random=select("NULL"),select("COUPLED"),select("ONE_FOLIO"),select("FOLIO_RANDOM")
    labels=synthetic_outcomes(PANEL,0,"COUPLED",.2); permutation=np.asarray([(i*7+3)%24 for i in range(24)],dtype=np.int64)
    if len(set(permutation.tolist()))!=24: raise ValueError("label permutation is not bijective")
    original=score(PANEL,labels); relabeled=score(PANEL,permutation[labels])
    invariant_fields=["effect_equal_folio","effect_equal_row","sign_p","minimum_leave_one_folio_out","max_abs_contribution_fraction"]
    invariant_delta=max(abs(original[key]-relabeled[key]) for key in invariant_fields)
    mutations=mutation_controls()
    gates={
        "exact_capacity":original["eligible_rows"]==14955 and original["physical_folios"]==94,
        "null_at_most_3_of_64":sum(row["passes"] for row in null)<=3,
        "coupled_power_at_least_7_of_8":sum(row["passes"] for row in coupled)>=7,
        "one_folio_zero_of_8":sum(row["passes"] for row in one)==0,
        "folio_random_zero_of_8":sum(row["passes"] for row in random)==0,
        "outcome_relabel_invariance":invariant_delta<=1e-12,
        "mutation_guards":all(mutations.values()),
        "target_absent":not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
    }
    status="PASS_TARGET_FREE_EDGE_COUPLING_PREFLIGHT" if all(gates.values()) else "STOP_EDGE_COUPLING_PREFLIGHT_TARGET_FORBIDDEN"
    aggregates={"null_passes":sum(row["passes"] for row in null),"null_worlds":64,"coupled_passes":sum(row["passes"] for row in coupled),"one_folio_passes":sum(row["passes"] for row in one),"folio_random_passes":sum(row["passes"] for row in random)}
    result={"experiment":"SOURCE_NATIVE_EDGE_COUPLING_PREFLIGHT","status":status,"inputs":{p.name:sha(p) for p in (*FROZEN,SPEC,RUNNER)},"numeric_environment":{"workers":32,"OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1","MKL_NUM_THREADS":"1"},"worlds":worlds,"aggregates":aggregates,"invariants":{"outcome_relabel_max_abs_difference":invariant_delta},"mutations":mutations,"gates":gates,"target_isolation":{"source_exists_checked_only":TARGET_SOURCE.exists(),"source_opened":False,"target_outcomes_accessed":0,"target_scores_computed":0,"target_outputs_absent":not TARGET_OUT.exists() and not TARGET_REPORT.exists()},"decision":"GO_FREEZE_ONE_EDGE_COUPLING_TARGET" if all(gates.values()) else "STOP_TARGET_FORBIDDEN","claim_ceiling":"Synthetic calibration only. A future pass can establish opening-conditioned closing-family selection beyond frozen controls, not an affix, circumfix, sound, word, language, cipher operation, meaning, plaintext, or translation."}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    REPORT.write_text(f"""# Source-native edge-coupling synthetic preflight

Status: **{status}**

The target-free 32-worker grid produced **{aggregates['null_passes']}/64** null,
**{aggregates['coupled_passes']}/8** global-coupling, **{aggregates['one_folio_passes']}/8**
one-folio, and **{aggregates['folio_random_passes']}/8** folio-random passes.
Outcome relabeling, capacity, finite-score, isolation, and target-absence gates
all {'passed' if all(gates.values()) else 'did not all pass'}. The source final
families were existence-tested only and zero target outcomes or scores were
opened.

Decision: **{result['decision']}**. This preflight supplies no affix, word,
meaning, plaintext, or translation.
""")
    print(json.dumps({"status":status,"aggregates":aggregates,"decision":result["decision"]},sort_keys=True))

if __name__=="__main__": main()
