#!/usr/bin/env python3
"""Validate the final GDT381 bound decision."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt381_relational_topology_transfer";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(o):q=dict(o);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads((ART/"gdt381_result.json").read_text());checks=[]
 def ck(n,x):checks.append({"check":n,"pass":bool(x)});assert x,n
 ck("content_hash",r["content_hash"]==content(r));ck("decision",r["status"]=="COMPARATOR_TOPOLOGY_SUPPORTED_TARGET_TRANSFER_UNIDENTIFIABLE_DEFINITION_OVERLAP");ck("comparator_authorized",r["comparator_topology_authorized"] and r["comparator_topology"]=="CMP_TOPOLOGY_04");ck("raw_gate_preserved",r["voynich_primary_numerical_gate_pass"] is True);ck("not_promoted",r["voynich_behavior_class_promoted"] is False);ck("overlap_material",r["source_side_auc_for_membership"]>=.85 and r["source_side_full_logit_correlation"]>=.85);ck("no_realizations",r["formal_realizations_inspected"] is False);ck("f84_false",all(v is False for v in r["f84"].values()))
 for sec in ["inputs","documents","implementation"]:
  for p,d in r[sec].items():ck(sec+"_"+p.replace("/","_"),sha(ROOT/p)==d)
 out={"schema":"GDT381_FINAL_VALIDATION_V1","status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"checks":checks,"result_hash":sha(ART/"gdt381_result.json"),"target_validation_hash":sha(ART/"gdt381_target_validation.json"),"f84":{"opened":False,"parsed":False,"retained":False,"scored":False}};out["content_hash"]=content(out);(ART/"gdt381_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()
