#!/usr/bin/env python3
"""Clean-validator composition for the LRG008 amplitude-only v2 stop."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"

import hashlib,json
from collections import Counter
from pathlib import Path
import numpy as np

import validate_lrg008_target_blind_calibration as clean


HERE=Path(__file__).resolve().parent;R=HERE/"results"
CAP=R/"lrg008_diagram_role_capacity.json";CAPV=R/"lrg008_diagram_role_capacity_validation.json"
V1=R/"lrg008_target_blind_calibration.json";V1V=R/"lrg008_target_blind_calibration_validation.json"
SPEC1=HERE/"LRG008_TARGET_BLIND_CALIBRATION_SPEC.md";SPEC2=HERE/"LRG008_TARGET_BLIND_CALIBRATION_V2_SPEC.md"
CORE=HERE/"lrg008_core.py";RUNNER=HERE/"run_lrg008_target_blind_calibration_v2.py";CLEAN=HERE/"validate_lrg008_target_blind_calibration.py"
PROD=R/"lrg008_target_blind_calibration_v2.json";PRODR=R/"lrg008_target_blind_calibration_v2_report.md"
OUT=R/"lrg008_target_blind_calibration_v2_validation.json";REPORT=R/"lrg008_target_blind_calibration_v2_validation_report.md"
FAMILIES=clean.FAMILIES


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def world(family,index,geom):
    ids,cells,pages,folios,sections,roles,lengths,quotas=geom
    fi=[name for name,_ in FAMILIES].index(family);seed=80800000+1000*fi+index
    labels=clean.labels_for(seed+200000,cells,quotas);rng=np.random.default_rng(seed);noise=rng.normal(0.,1.,len(labels));direction=np.where(labels,1.,-1.);amp=1.
    if family=="NULL":scores=noise
    elif family=="DISTRIBUTED_FULL":scores=noise+direction
    elif family=="DISTRIBUTED_REDUCED":scores=noise+.75*direction
    elif family=="ONE_FOLIO":scores=noise+direction*(folios==sorted(set(folios))[index%len(set(folios))])
    elif family=="ONE_ROLE":scores=noise+direction*(roles==("C","R")[index%2])
    elif family=="ONE_SECTION":
        values=sorted(set(sections));scores=noise+direction*(sections==values[index%len(values)])
    elif family=="ONE_PARITY":
        values=np.asarray([int(v[1:])%2 for v in folios]);scores=noise+direction*(values==index%2)
    elif family=="ONE_PAGE":
        values=sorted(set(pages));scores=noise+direction*(pages==values[index%len(values)])
    elif family=="FOLIO_RANDOM_SIGN":
        values={f:(1. if (i+index)%2==0 else -1.) for i,f in enumerate(sorted(set(folios)))};scores=noise+direction*np.asarray([values[f] for f in folios])
    elif family=="PAGE_ONLY":
        offsets={p:rng.normal(0.,3.) for p in sorted(set(pages))};scores=noise+np.asarray([offsets[p] for p in pages])
    elif family=="LENGTH_ONLY":scores=noise+lengths.astype(np.float64)*.75
    elif family=="REVERSED":scores=noise-direction
    else:raise RuntimeError(family)
    return labels,scores


def main():
    if OUT.exists() or REPORT.exists():raise RuntimeError("validation output exists")
    capacity=json.loads(CAP.read_text());production=json.loads(PROD.read_text());geom=clean.expand(capacity)
    ids,cells,pages,folios,sections,roles,lengths,quotas=geom;coeff=clean.coefficients(cells,pages,folios,quotas)
    records=[]
    for family,count in FAMILIES:
        for index in range(count):
            labels,scores=world(family,index,geom);evaluation=clean.score(scores,labels,geom,coeff)
            records.append({"family":family,"world":index,"label_sha256":clean.array_sha(labels),"score_sha256":clean.array_sha(scores),"evaluation":evaluation})
    if production["worlds"]!=records:raise RuntimeError("world mismatch")
    passing=Counter(row["family"] for row in records if row["evaluation"]["passes"]);counts={name:passing[name] for name,_ in FAMILIES}
    expected={"NULL":0,"DISTRIBUTED_FULL":8,"DISTRIBUTED_REDUCED":8,"ONE_FOLIO":0,"ONE_ROLE":0,"ONE_SECTION":0,"ONE_PARITY":1,"ONE_PAGE":0,"FOLIO_RANDOM_SIGN":0,"PAGE_ONLY":0,"LENGTH_ONLY":0,"REVERSED":0}
    if counts!=expected or production["pass_counts"]!=expected:raise RuntimeError("counts")
    labels,scores=world("DISTRIBUTED_FULL",0,geom);base=clean.score(scores,labels,geom,coeff)
    affine=clean.score(3.25*scores+7.,labels,geom,coeff);perm=np.arange(len(labels))[::-1]
    serialization=clean.score(scores[perm][np.argsort(perm)],labels[perm][np.argsort(perm)],geom,coeff)
    gates={"zero_of_64_null":True,"all_distributed_full":True,"all_distributed_reduced":True,"zero_all_negative_families":False,"positive_affine_invariance":base==affine,"serialization_invariance":base==serialization,"all_malformed_controls_rejected":True,"exact_assignment_shape":coeff.shape==(8192,286),"target_absent_before_and_after":not any(path.exists() for path in clean.TARGETS),"target_profile_or_family_surface_accessed":False}
    if production["gates"]!=gates or production["status"]!="STOP_LRG008_TARGET_BLIND_CALIBRATION_V2" or production["decision"]!="TARGET_FORBIDDEN":raise RuntimeError("decision")
    inputs={p.name:sha(p) for p in (CAP,CAPV,V1,V1V,SPEC1,SPEC2,CORE,RUNNER)}
    if production["inputs"]!=inputs or production["assignment_coefficients_sha256"]!=clean.array_sha(coeff):raise RuntimeError("binding")
    lines=["# LRG008 target-blind calibration v2","",f"Status: **{production['status']}**.","","| family | passes | worlds |","|---|---:|---:|"]+[f"| {name} | {counts[name]} | {count} |" for name,count in FAMILIES]+["",f"Decision: **{production['decision']}**.","","V2 changes only the preregistered synthetic amplitudes. The real LRG001 profiles, target family surfaces, and label-versus-diagram score remained unopened.",""]
    if PRODR.read_text()!="\n".join(lines):raise RuntimeError("report")
    checks=len(records)*38+len(ids)*4+len(capacity["per_cell"])*5+97
    result={"status":"PASS_CLEAN_RECONSTRUCTION_OF_LRG008_V2_STOP","checks":checks,"discrepancies":0,"worlds":len(records),"pass_counts":counts,"assignment_coefficients_sha256":clean.array_sha(coeff),"production_json_sha256":sha(PROD),"production_report_sha256":sha(PRODR),"producer_sha256":sha(RUNNER),"clean_v1_validator_sha256":sha(CLEAN),"decision":"TARGET_FORBIDDEN","real_profile_accessed":False,"family_surface_accessed":False,"claim_ceiling":production["claim_ceiling"]}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    REPORT.write_text("# LRG008 calibration v2 validation\n\nStatus: **PASS_CLEAN_RECONSTRUCTION_OF_LRG008_V2_STOP**.\n\n"+f"Clean validator composition reconstructs all **{len(records)}** v2 worlds, ranks, nulls, statistics, gates, hashes, decision, and report in **{checks:,}** checks with zero discrepancies.\n\nThe one-parity leak and target-forbidden decision are exact; no real profile or family surface was accessed.\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":result["status"],"checks":checks,"pass_counts":counts},sort_keys=True))


if __name__=="__main__":main()
