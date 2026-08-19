#!/usr/bin/env python3
"""Fit/freeze the authorized comparator topology and target design before scoring."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt381_relational_topology_transfer"
ART = BASE / "artifacts"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
RUNNER = BASE / "src/run_comparator.py"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def content(obj: dict) -> str:
    clone=dict(obj);clone.pop("content_hash",None)
    return hashlib.sha256(json.dumps(clone,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def write(path: Path,obj: dict) -> None:
    obj["content_hash"]=content(obj);path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def balanced_accuracy(y,pred):
    y=np.asarray(y,int);pred=np.asarray(pred,bool);return ((pred[y==1].mean() if y.sum() else 0)+(~pred[y==0]).mean() if (y==0).sum() else 0)/2


def main() -> None:
    signature=json.loads((ART/"gdt381_topology_signature_freeze.json").read_text());assert signature["eligible_anonymous_topologies"]==["CMP_TOPOLOGY_04"] and not signature["voynich_target_scored"]
    spec=importlib.util.spec_from_file_location("gdt381_runner",RUNNER);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    obs=module.read_tsv(module.OBS);oracle=module.read_tsv(module.ORACLE);contract=json.loads(module.CONTRACT.read_text());domains=np.array([r["domain"] for r in obs]);domain_indices={d:np.where(domains==d)[0].tolist() for d in sorted(set(domains))};design=json.loads(module.DESIGN.read_text())
    _,_,nuisance,trivial,relational,nn,tn,rn,_,_,_,meta=module.build_topology(obs,domain_indices,design);X=np.column_stack([nuisance,trivial,relational]);y=np.array([int(r["COORDINATOR"]) for r in oracle]);available=contract["availability"]["COORDINATOR"]
    held=np.full(len(obs),np.nan)
    for domain in available:
        train=np.where(np.isin(domains,[d for d in available if d!=domain]))[0];test=np.where(domains==domain)[0];held[test]=module.predict(module.fit(X[train],y[train],domains[train].tolist()),X[test])
    quantiles=[.50,.65,.80,.90];quality=[]
    for q in quantiles:
        values=[]
        for domain in available:
            ids=np.where(domains==domain)[0];cut=float(np.quantile(held[ids],q));values.append(balanced_accuracy(y[ids],held[ids]>=cut))
        quality.append((float(np.mean(values)),q))
    threshold_quality,threshold_q=max(quality,key=lambda x:(x[0],x[1]))
    ids=np.where(np.isin(domains,available))[0];model=module.fit(X[ids],y[ids],domains[ids].tolist());beta,mu,sd=model
    # The target is bound and checked for f84 but no event is scored or
    # clustered here.
    raw=SOURCE.read_text(encoding="utf-8");header=raw.splitlines()[0].split("\t");required={"page","physical_folio","locus","joint_tuple_id","register","section","record_ordinal","field_ordinal","line_first","prev_dy","dy_closure","b3"};assert required.issubset(header)
    for line in raw.splitlines()[1:]:
        row=dict(zip(header,line.split("\t")))
        if any(row[k].startswith("f84") for k in ["page","physical_folio","locus"]):raise ValueError("f84 row in target source")
    freeze={"schema":"GDT381_VOYNICH_TARGET_FREEZE_V1","status":"FROZEN_BEFORE_VOYNICH_TOPOLOGY_SCORING","authorized_anonymous_topology":"CMP_TOPOLOGY_04","comparator_label_exported":False,"behavior_class_id":"CMP04_BEHAVIOR_CLASS_A","comparator_model":{"feature_names":nn+tn+rn,"coefficients":[float(x) for x in beta],"training_mean":[float(x) for x in mu],"training_sd":[float(x) for x in sd],"l2":4.0,"available_domains":available,"held_threshold_grid":quantiles,"selected_within_domain_quantile":threshold_q,"selected_macro_balanced_accuracy":threshold_quality,"domain_local_k":{d:m["k"] for d,m in meta.items()}},"target":{"source":"gdt327_joint_tuple_interlinear.tsv","source_sha256":sha(SOURCE),"latent_class_scope":"INDEPENDENT_WITHIN_REGISTER","boundary_before":"LINE_FIRST_OR_PREV_DY","boundary_after":"DY_OR_B3_OR_PHYSICAL_LINE_END","record_key":"PAGE_RECORD_ORDINAL","collection_key":"PHYSICAL_FOLIO","exact_identity_as_predictor":False,"post_pivot_as_predictor":False,"formal_realizations_inspected_before_pass":False},"held_test":{"outer_fold":"LEAVE_ONE_PHYSICAL_FOLIO_OUT","null_worlds":4096,"seed":381201,"minimum_mobile_events":256,"minimum_powered_folios":20,"minimum_powered_registers":3,"positive_folio_fraction":.60,"minimum_auc":.60,"maxT_p_max":.05,"positive_total_gain_over_both_baselines":True},"inputs":{str(p.relative_to(ROOT)):sha(p) for p in [ART/"gdt381_comparator_result.json",ART/"gdt381_comparator_validation.json",ART/"gdt381_topology_signature_freeze.json",SOURCE]},"implementation":{str((BASE/"src/freeze_target.py").relative_to(ROOT)):sha(BASE/"src/freeze_target.py"),str(RUNNER.relative_to(ROOT)):sha(RUNNER)},"voynich_events_scored":0,"semantic_state":"UNASSIGNED","forbidden_interpretations":["COORDINATION","AND","OR","NOT","UNTIL","POS","MEANING","LANGUAGE","PLAINTEXT","TRANSLATION"],"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"claim_ceiling":"FROZEN_ANONYMOUS_RELATION_TOPOLOGY_TARGET_ONLY"};write(ART/"gdt381_voynich_target_freeze.json",freeze)
    result={"schema":"GDT381_TARGET_FREEZE_RESULT_V1","status":"FROZEN_NOT_RUN","inputs":freeze["inputs"],"documents":{str((BASE/n).relative_to(ROOT)):sha(BASE/n) for n in ["METHOD.md","TARGET_METHOD.md","README.md","experiment.json"]},"implementation":{str((BASE/"src/freeze_target.py").relative_to(ROOT)):sha(BASE/"src/freeze_target.py")},"outputs":{str((ART/"gdt381_voynich_target_freeze.json").relative_to(ROOT)):sha(ART/"gdt381_voynich_target_freeze.json")},"voynich_events_scored":0,"semantic_state":"UNASSIGNED","f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"claim_ceiling":"PRETARGET_FREEZE_ONLY"};write(ART/"gdt381_target_freeze_result.json",result);print(json.dumps({"status":result["status"],"threshold_quantile":threshold_q,"balanced_accuracy":threshold_quality}))


if __name__=="__main__":main()
