#!/usr/bin/env python3
"""Validate GDT381 target accounting and the nonpromotion audit."""
from __future__ import annotations
import csv,gzip,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt381_relational_topology_transfer";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(o):q=dict(o);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 op=gzip.open if p.suffix==".gz" else open
 with op(p,"rt",encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def bits(y,p):
 import math
 return -sum(int(a)*math.log2(max(1e-9,min(1-1e-9,float(b))))+(1-int(a))*math.log2(max(1e-9,min(1-1e-9,1-float(b)))) for a,b in zip(y,p))
def main():
 result=json.loads((ART/"gdt381_voynich_result.json").read_text());audit=json.loads((ART/"gdt381_target_definition_overlap.json").read_text());events=read(ART/"gdt381_voynich_event_scores.tsv.gz");folds=read(ART/"gdt381_voynich_fold_scores.tsv");regs=read(ART/"gdt381_voynich_register_scores.tsv");null=read(ART/"gdt381_voynich_null.tsv.gz");features=read(ART/"gdt381_target_definition_overlap_features.tsv");checks=[]
 def ck(n,x):checks.append({"check":n,"pass":bool(x)});assert x,n
 ck("result_hash",result["content_hash"]==content(result));ck("audit_hash",audit["content_hash"]==content(audit));ck("events",len(events)==result["events"]==8448);ck("event_ids_unique",len({r["event_id"] for r in events})==len(events));ck("no_formal_identity",all(r["exact_formal_identity_exported"]=="0" for r in events));ck("members",sum(int(r["behavior_class_member"]) for r in events)==result["members"]);ck("folios",len(folds)==result["folios"]==91);ck("registers",len(regs)==result["registers"]==5);ck("null_worlds",len(null)==4096);ck("powered",sum(r["powered"]=="1" for r in folds)==result["powered_folios"]);ck("positive_folds",sum(r["powered"]=="1" and r["positive_both"]=="1" for r in folds)==result["positive_both_folios"]);ck("positive_regs",sum(r["positive_both"]=="1" for r in regs)==result["positive_both_registers"])
 y=[int(r["behavior_class_member"]) for r in events];pn=[float(r["held_probability_nuisance"]) for r in events];pt=[float(r["held_probability_trivial"]) for r in events];pf=[float(r["held_probability_full"]) for r in events];gn=bits(y,pn)-bits(y,pf);gt=bits(y,pt)-bits(y,pf);ck("gain_n",math.isclose(gn,result["total_gain_vs_nuisance_bits"],abs_tol=1e-6));ck("gain_t",math.isclose(gt,result["total_gain_vs_trivial_bits"],abs_tol=1e-6));obs=min(gn,gt);p=(1+sum(float(r["joint_min_gain_bits"])>=obs for r in null))/(1+len(null));ck("null_p",math.isclose(p,result["joint_null_p"],abs_tol=1e-12));ck("primary_gate_arithmetic",result["promotion"] is True and result["status"]=="ANONYMOUS_RELATIONAL_TOPOLOGY_TRANSFER_PASS");ck("audit_nonpromotion",audit["status"]=="PRIMARY_NUMERICAL_PASS_NONPROMOTING_SOURCE_DEFINITION_OVERLAP" and audit["primary_promotion_honored_as_semantic_or_independent_transfer"] is False);ck("audit_feature_count",len(features)==audit["features_total"] and sum(r["classification"]=="CONSERVATIVE_SOURCE_SIDE" for r in features)==audit["conservative_source_side_features"]);ck("overlap_material",audit["source_side_auc_for_frozen_membership"]>=.85 and audit["source_side_full_logit_correlation"]>=.85);ck("no_realization_inspection",not result["formal_realizations_inspected"] and not audit["formal_realizations_inspected"]);ck("f84_false",all(v is False for v in result["f84"].values()) and all(v is False for v in audit["f84"].values()))
 for sec in ["inputs","outputs","implementation"]:
  for path,digest in result[sec].items():ck(sec+"_"+path.replace("/","_"),sha(ROOT/path)==digest)
 for sec in ["inputs","implementation"]:
  for path,digest in audit[sec].items():ck("audit_"+sec+"_"+path.replace("/","_"),sha(ROOT/path)==digest)
 out={"schema":"GDT381_TARGET_VALIDATION_V1","status":"PASS","scope":"PRIMARY_OUTPUT_ARITHMETIC_HASHES_AND_DEFINITION_OVERLAP_NONPROMOTION_NO_MODEL_REFIT","checks_passed":len(checks),"checks_total":len(checks),"checks":checks,"result_hash":sha(ART/"gdt381_voynich_result.json"),"audit_hash":sha(ART/"gdt381_target_definition_overlap.json"),"f84":{"opened":False,"parsed":False,"retained":False,"scored":False}};out["content_hash"]=content(out);(ART/"gdt381_target_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()
