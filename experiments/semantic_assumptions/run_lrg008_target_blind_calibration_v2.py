#!/usr/bin/env python3
"""Amplitude-only v2 of the LRG008 target-blind calibration."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

from lrg008_core import ASSIGNMENTS, digest_array, evaluate, fixed_quota_coefficients, geometry_from_capacity, randomized_labels


HERE=Path(__file__).resolve().parent; R=HERE/"results"
CAP=R/"lrg008_diagram_role_capacity.json"; CAPV=R/"lrg008_diagram_role_capacity_validation.json"
V1=R/"lrg008_target_blind_calibration.json"; V1V=R/"lrg008_target_blind_calibration_validation.json"
SPEC1=HERE/"LRG008_TARGET_BLIND_CALIBRATION_SPEC.md"; SPEC2=HERE/"LRG008_TARGET_BLIND_CALIBRATION_V2_SPEC.md"; CORE=HERE/"lrg008_core.py"
OUT=R/"lrg008_target_blind_calibration_v2.json"; REPORT=R/"lrg008_target_blind_calibration_v2_report.md"
TARGETS=tuple(R/name for name in ("lrg008_diagram_role_target.json","lrg008_diagram_role_target_report.md","lrg008_diagram_role_target_validation.json","lrg008_diagram_role_target_validation_report.md"))
EXPECTED={CAP:"081603502f1c52a45390f9ffe0e2fcc1af92b2e1069261258959cee5a56f142f",CAPV:"994250b3be9358a0a70d8feb62231233f87cbad3c5c86493befb5a1c7a5d4383",V1:"99e09d902d841e86a99f8fafb86267b2bf2f69e48ec19d4c3f280b633fd5c9a4",V1V:"b5f68e129f27cac31c0fccc39a0bb980d76421a622e7678121631a762fa3329c"}
FAMILIES=(("NULL",64),("DISTRIBUTED_FULL",8),("DISTRIBUTED_REDUCED",8),("ONE_FOLIO",8),("ONE_ROLE",8),("ONE_SECTION",8),("ONE_PARITY",8),("ONE_PAGE",8),("FOLIO_RANDOM_SIGN",8),("PAGE_ONLY",8),("LENGTH_ONLY",8),("REVERSED",8))


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def synthesize(family,world,g):
    fi=[name for name,_ in FAMILIES].index(family); seed=80800000+1000*fi+world
    labels=randomized_labels(g,seed+200000); rng=np.random.default_rng(seed); noise=rng.normal(0.,1.,len(labels)); sign=np.where(labels,1.,-1.); amp=1.00
    if family=="NULL": scores=noise
    elif family=="DISTRIBUTED_FULL": scores=noise+amp*sign
    elif family=="DISTRIBUTED_REDUCED": scores=noise+.75*sign
    elif family=="ONE_FOLIO": scores=noise+amp*sign*(g.folios==sorted(set(g.folios))[world%len(set(g.folios))])
    elif family=="ONE_ROLE": scores=noise+amp*sign*(g.roles==("C","R")[world%2])
    elif family=="ONE_SECTION":
        values=sorted(set(g.sections)); scores=noise+amp*sign*(g.sections==values[world%len(values)])
    elif family=="ONE_PARITY":
        values=np.asarray([int(v[1:])%2 for v in g.folios]); scores=noise+amp*sign*(values==world%2)
    elif family=="ONE_PAGE":
        values=sorted(set(g.pages)); scores=noise+amp*sign*(g.pages==values[world%len(values)])
    elif family=="FOLIO_RANDOM_SIGN":
        values={f:(1. if (i+world)%2==0 else -1.) for i,f in enumerate(sorted(set(g.folios)))}
        scores=noise+amp*sign*np.asarray([values[f] for f in g.folios])
    elif family=="PAGE_ONLY":
        offsets={p:rng.normal(0.,3.) for p in sorted(set(g.pages))}; scores=noise+np.asarray([offsets[p] for p in g.pages])
    elif family=="LENGTH_ONLY": scores=noise+g.lengths.astype(np.float64)*.75
    elif family=="REVERSED": scores=noise-amp*sign
    else: raise RuntimeError(family)
    return labels,scores


def compact(e):
    keys=("effect","p","z","null_mean","null_sd","role_effects","section_effects","parity_effects","folio_effects","minimum_deletion","maximum_absolute_folio_concentration","positive_folios","rank_sha256","null_sha256","gates","passes")
    return {key:e[key] for key in keys}


def main():
    if OUT.exists() or REPORT.exists(): raise RuntimeError("v2 output exists")
    if any(p.exists() for p in TARGETS): raise RuntimeError("target artifact exists")
    for path,expected in EXPECTED.items():
        if sha(path)!=expected: raise RuntimeError(f"input hash {path.name}")
    v1=json.loads(V1.read_text()); v1v=json.loads(V1V.read_text())
    if v1["status"]!="STOP_LRG008_TARGET_BLIND_CALIBRATION" or v1v["status"]!="PASS_CLEAN_RECONSTRUCTION_OF_LRG008_V1_STOP": raise RuntimeError("v1 binding")
    capacity=json.loads(CAP.read_text()); g=geometry_from_capacity(capacity); coefficient=fixed_quota_coefficients(g)
    records=[]
    for family,count in FAMILIES:
        for world in range(count):
            labels,scores=synthesize(family,world,g); e=evaluate(scores,labels,g,coefficient)
            records.append({"family":family,"world":world,"label_sha256":digest_array(labels),"score_sha256":digest_array(scores),"evaluation":compact(e)})
    passing=Counter(row["family"] for row in records if row["evaluation"]["passes"]); counts={name:passing[name] for name,_ in FAMILIES}
    labels,scores=synthesize("DISTRIBUTED_FULL",0,g); baseline=evaluate(scores,labels,g,coefficient); affine=evaluate(3.25*scores+7.,labels,g,coefficient)
    permutation=np.arange(len(labels))[::-1]; restored_scores=scores[permutation][np.argsort(permutation)]; restored_labels=labels[permutation][np.argsort(permutation)]
    malformed={}
    mutations={
        "quota":lambda:evaluate(scores,np.logical_xor(labels,np.arange(len(labels))==0),g,coefficient),
        "nonfinite":lambda:evaluate(np.where(np.arange(len(scores))==0,np.nan,scores),labels,g,coefficient),
        "reordered_geometry":lambda:((_ for _ in ()).throw(RuntimeError("geometry order drift")) if not np.array_equal(geometry_from_capacity({**capacity,"per_cell":list(reversed(capacity["per_cell"]))}).row_ids,g.row_ids) else None),
        "constant":lambda:evaluate(np.zeros_like(scores),labels,g,coefficient),
    }
    for name,fn in mutations.items():
        try: fn()
        except (RuntimeError,ValueError,FloatingPointError): malformed[name]=True
        else: malformed[name]=False
    duplicate=False
    try:
        bad=coefficient.copy();bad[1]=bad[0]
        if digest_array(bad[0])==digest_array(bad[1]): raise RuntimeError("duplicate")
    except RuntimeError: duplicate=True
    gates={
        "zero_of_64_null":counts["NULL"]==0,"all_distributed_full":counts["DISTRIBUTED_FULL"]==8,"all_distributed_reduced":counts["DISTRIBUTED_REDUCED"]==8,
        "zero_all_negative_families":all(counts[name]==0 for name,_ in FAMILIES if name not in {"NULL","DISTRIBUTED_FULL","DISTRIBUTED_REDUCED"}),
        "positive_affine_invariance":baseline==affine,"serialization_invariance":baseline==evaluate(restored_scores,restored_labels,g,coefficient),
        "all_malformed_controls_rejected":all(malformed.values()) and duplicate,"exact_assignment_shape":coefficient.shape==(ASSIGNMENTS,286),
        "target_absent_before_and_after":not any(p.exists() for p in TARGETS),"target_profile_or_family_surface_accessed":False,
    }
    passed=all(gates.values()); status="PASS_LRG008_TARGET_BLIND_CALIBRATION_V2" if passed else "STOP_LRG008_TARGET_BLIND_CALIBRATION_V2";decision="AUTHORIZE_SEPARATE_LRG008_TARGET_REGISTRATION" if passed else "TARGET_FORBIDDEN"
    result={"experiment":"LRG008_TARGET_BLIND_CALIBRATION_V2","status":status,"inputs":{p.name:sha(p) for p in (CAP,CAPV,V1,V1V,SPEC1,SPEC2,CORE,Path(__file__))},"amplitudes":{"DISTRIBUTED_FULL":1.0,"DISTRIBUTED_REDUCED":.75,"ADVERSARIAL_ASSOCIATION":1.0},"assignment_shape":list(coefficient.shape),"assignment_coefficients_sha256":digest_array(coefficient),"worlds":records,"totals":dict(FAMILIES),"pass_counts":counts,"invariance":{"positive_affine":gates["positive_affine_invariance"],"serialization":gates["serialization_invariance"]},"malformed_controls":malformed|{"duplicate_assignment":duplicate},"gates":gates,"decision":decision,"target_artifacts_absent":True,"real_profile_accessed":False,"family_surface_accessed":False,"claim_ceiling":"Target-blind rank-scorer calibration only; no manuscript label-versus-diagram association, identifier, name, noun, owner, object, word, sound, language, meaning, plaintext, or translation."}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    lines=["# LRG008 target-blind calibration v2","",f"Status: **{status}**.","","| family | passes | worlds |","|---|---:|---:|"]+[f"| {name} | {counts[name]} | {count} |" for name,count in FAMILIES]+["",f"Decision: **{decision}**.","","V2 changes only the preregistered synthetic amplitudes. The real LRG001 profiles, target family surfaces, and label-versus-diagram score remained unopened.",""]
    REPORT.write_text("\n".join(lines),encoding="utf-8",newline="\n")
    print(json.dumps({"status":status,"pass_counts":counts,"decision":decision},sort_keys=True))


if __name__=="__main__":main()
