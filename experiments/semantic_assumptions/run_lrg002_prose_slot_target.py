#!/usr/bin/env python3
"""Execute the frozen aggregate LRG002 prose-slot target once."""

from __future__ import annotations

import os
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

import lrg001_core as l1
import lrg002_core as l2


HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; RES = HERE / "results"
FREEZE = HERE / "LRG002_TARGET_FREEZE.json"
L1_CAPACITY = RES / "lrg001_label_register_capacity.tsv"; L2_CAPACITY = RES / "lrg002_prose_slot_capacity.tsv"
GROUPS = RES / "source_sta_family_consensus_groups.tsv"; L1_TARGET = RES / "lrg001_label_register_target_recovered.json"
OUT = RES / "lrg002_prose_slot_target.json"; REPORT = RES / "lrg002_prose_slot_target_report.md"
VALIDATION = RES / "lrg002_prose_slot_target_validation.json"; VALIDATION_REPORT = RES / "lrg002_prose_slot_target_validation_report.md"
OFFICIAL = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path: Path) -> list[dict[str,str]]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def atomic_new(path: Path, text: str) -> None:
    if path.exists(): raise RuntimeError(f"output exists {path.name}")
    temporary=path.with_suffix(path.suffix+".tmp"); temporary.write_text(text,encoding="utf-8",newline="\n"); os.link(temporary,path); temporary.unlink()


def label_profiles(group_rows: list[dict[str,str]]) -> tuple[np.ndarray,np.ndarray]:
    geometry=l1.load_geometry(L1_CAPACITY); eligible=defaultdict(lambda:{"L":[],"P":[]})
    for row in group_rows:
        if row["strict_zero_alternative"]!="1": continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind: eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    sequences=[]; labels=[]
    for cell in [row for row in rows(L1_CAPACITY) if row["section"] in {"B","P"}]:
        key=cell["page"],int(cell["symbol_count"])
        for kind,value in (("L",1),("P",0)):
            current=sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]); expected=int(cell["label_rows"] if kind=="L" else cell["prose_rows"])
            if len(current)!=expected: raise RuntimeError("LRG001 target drift")
            sequences.extend(row["family_surface"] for row in current); labels.extend([value]*len(current))
    y=np.asarray(labels,dtype=np.int8); matrix=l1.feature_matrix(sequences,geometry.lengths); numbers=np.asarray([int(value[1:]) for value in geometry.folios]); odd=numbers%2==1
    odd_profile=l1.learn_profile(matrix,y,geometry,odd); even_profile=l1.learn_profile(matrix,y,geometry,~odd)
    target=json.loads(L1_TARGET.read_text(encoding="utf-8"))
    if l1.sha256_array(odd_profile)!=target["evaluation"]["odd_profile_sha256"] or l1.sha256_array(even_profile)!=target["evaluation"]["even_profile_sha256"]: raise RuntimeError("LRG001 profile drift")
    return odd_profile,even_profile


def main() -> None:
    output_paths=(OUT,REPORT,VALIDATION,VALIDATION_REPORT)
    if any(path.exists() for path in output_paths): raise RuntimeError("LRG002 target output exists")
    freeze=json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["status"]!="FROZEN_LRG002_SINGLE_TARGET" or freeze["result_paths"]!=[str(path.relative_to(ROOT)) for path in output_paths]: raise RuntimeError("freeze contract")
    for relative,expected in freeze["frozen_files"].items():
        if sha(ROOT/relative)!=expected: raise RuntimeError(f"freeze drift {relative}")
    l1.ALPHABET=OFFICIAL; l1.INDEX={value:index for index,value in enumerate(OFFICIAL)}
    group_rows=rows(GROUPS); by_id={row["consensus_group_id"]:row for row in group_rows}
    if len(by_id)!=len(group_rows): raise RuntimeError("duplicate group ID")
    odd_profile,even_profile=label_profiles(group_rows); geometry=l2.load_geometry(L2_CAPACITY); capacity=rows(L2_CAPACITY)
    if list(geometry.row_ids)!=[row["consensus_group_id"] for row in capacity]: raise RuntimeError("LRG002 row order")
    sequences=[]
    for row in capacity:
        source=by_id.get(row["consensus_group_id"])
        if source is None or source["page"]!=row["page"] or source["symbol_count"]!=row["symbol_count"]: raise RuntimeError("LRG002 source join")
        sequence=source["family_surface"]
        if len(sequence)!=int(row["symbol_count"]) or any(value not in OFFICIAL for value in sequence): raise RuntimeError("LRG002 sequence")
        sequences.append(sequence)
    matrix=l1.feature_matrix(sequences,geometry.lengths); raw=np.empty(len(sequences),dtype=np.float64)
    odd=np.asarray([int(value[1:])%2==1 for value in geometry.folios]); raw[odd]=matrix[odd]@even_profile; raw[~odd]=matrix[~odd]@odd_profile
    shifts={name:l2.rotations(geometry,name) for name in ("INDEPENDENT_SEGMENT","COUPLED_FOLIO")}; coefficients={name:l2.null_coefficients(geometry,value) for name,value in shifts.items()}; evaluation=l2.evaluate(raw,geometry,coefficients)
    passed=bool(evaluation["passes"]); status="CONFIRMED_DISTRIBUTED_LABEL_PROFILE_SLOT" if passed else "FINAL_NONCONFIRMATION_LABEL_PROFILE_SLOT"; decision="AUTHORIZE_ZERO_GLOSS_SLOT_ATLAS_AFTER_VALIDATION" if passed else "CLOSE_EXACT_LRG002_PROJECTION"
    result={
        "status":status,"decision":decision,"claim_ceiling":"Relative LRG001 label-profile likeness may occupy a distributed repeatable corrected-segment position; no coordinate is thereby a word, name, identifier, noun, POS, meaning, plaintext, or translation.",
        "freeze_sha256":sha(FREEZE),"target_rows_accessed":True,"row_scores_emitted":False,"individual_feature_weights_emitted":False,"favorable_forms_emitted":False,
        "counts":{"normalization_rows":len(raw),"primary_rows":int(geometry.primary.sum()),"segments":len(geometry.segment_rows),"folios":len(geometry.folio_names),"pages":len(set(geometry.pages)),"feature_columns":matrix.shape[1]},
        "odd_profile_sha256":l1.sha256_array(odd_profile),"even_profile_sha256":l1.sha256_array(even_profile),"prose_matrix_sha256":l1.sha256_array(matrix),"raw_score_sha256":l1.sha256_array(raw),
        "rotation_digests":{name:l2.sha256_array(value) for name,value in shifts.items()},"coefficient_digests":{name:l2.sha256_array(value) for name,value in coefficients.items()},"evaluation":evaluation,
    }
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"; vector=evaluation["summary"]["overall_vector"]
    report="\n".join(["# LRG002 prose-slot target","",f"Status: **{status}**.","",f"The opposite-parity label profile yields FIRST-minus-CORE **{vector[0]:+.9f}** and LAST-minus-CORE **{vector[1]:+.9f}** after exact page-by-length rank normalization.","",f"Independent-segment p: **{evaluation['pvalues']['INDEPENDENT_SEGMENT']:.9f}**. Coupled-folio p: **{evaluation['pvalues']['COUPLED_FOLIO']:.9f}**. Positive folios: **{evaluation['summary']['positive_folios']}/16**.","",f"Decision: **{decision}**.","","No row score, family weight, favorable form, word, name, identifier, noun, POS, meaning, plaintext, or translation is emitted.",""])
    if any(path.exists() for path in output_paths): raise RuntimeError("concurrent output")
    atomic_new(OUT,text)
    try: atomic_new(REPORT,report)
    except Exception: OUT.unlink(missing_ok=True); raise
    print(text,end="")


if __name__=="__main__": main()
