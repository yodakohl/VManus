#!/usr/bin/env python3
"""Validate the score-free GDT381 target freeze."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt381_relational_topology_transfer";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(o):q=dict(o);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 f=json.loads((ART/"gdt381_voynich_target_freeze.json").read_text());r=json.loads((ART/"gdt381_target_freeze_result.json").read_text());checks=[]
 def ck(n,x):checks.append({"check":n,"pass":bool(x)});assert x,n
 ck("freeze_hash",f["content_hash"]==content(f));ck("result_hash",r["content_hash"]==content(r));ck("one_topology",f["authorized_anonymous_topology"]=="CMP_TOPOLOGY_04");ck("label_not_exported",f["comparator_label_exported"] is False);ck("threshold_grid",f["comparator_model"]["held_threshold_grid"]==[.5,.65,.8,.9]);ck("coefficient_shape",len(f["comparator_model"]["coefficients"])==len(f["comparator_model"]["feature_names"]) and len(f["comparator_model"]["training_mean"])==len(f["comparator_model"]["feature_names"])-1);ck("identity_forbidden",f["target"]["exact_identity_as_predictor"] is False);ck("post_forbidden",f["target"]["post_pivot_as_predictor"] is False);ck("not_scored",f["voynich_events_scored"]==r["voynich_events_scored"]==0);ck("f84_false",all(v is False for v in f["f84"].values()) and all(v is False for v in r["f84"].values()))
 for p,d in f["inputs"].items():ck("input_"+p.replace("/","_"),sha(ROOT/p)==d)
 for sec in ["documents","implementation","outputs"]:
  for p,d in r[sec].items():ck(sec+"_"+p.replace("/","_"),sha(ROOT/p)==d)
 out={"schema":"GDT381_TARGET_FREEZE_VALIDATION_V1","status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"checks":checks,"result_hash":sha(ART/"gdt381_target_freeze_result.json"),"f84":{"opened":False,"parsed":False,"retained":False,"scored":False}};out["content_hash"]=content(out);(ART/"gdt381_target_freeze_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()
