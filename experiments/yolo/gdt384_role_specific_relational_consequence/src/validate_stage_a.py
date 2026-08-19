#!/usr/bin/env python3
"""Independent retained-prediction and provenance validator for GDT384."""
import csv,gzip,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt384_role_specific_relational_consequence";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(n,gz=False):
 op=gzip.open if gz else open
 with op(ART/n,"rt",encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def rankdata(x):
 a=np.asarray(x,float);o=np.argsort(a,kind="stable");z=np.empty(len(a),float);i=0
 while i<len(a):
  j=i+1
  while j<len(a) and a[o[j]]==a[o[i]]:j+=1
  z[o[i:j]]=(i+j+1)/2;i=j
 return z
def auc(y,s):
 y=np.asarray(y,int);n1=int(y.sum());n0=len(y)-n1;q=rankdata(s);return float((q[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def bits(y,p):y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-9,1-1e-9);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def main():
 checks=[]
 def ck(n,v):checks.append((n,bool(v)))
 r=json.loads((ART/"gdt384_result.json").read_text());ck("content_hash",r["content_hash"]==content(r));ck("status",r["status"]=="PRIORITY_RELATION_UNIDENTIFIABLE_SOURCE_OVERLAP_STOP_BEFORE_VOYNICH")
 for sec in ["inputs","outputs","documents","implementation"]:
  for p,h in r[sec].items():ck(sec+":"+p,(ROOT/p).is_file() and sha(ROOT/p)==h)
 pred=read("gdt384_priority_predictions.tsv.gz",True);fold=read("gdt384_priority_coordinator_folds.tsv");cap=read("gdt384_relation_capacity.tsv");rel=read("gdt384_hidden_relational_oracle.tsv.gz",True);q=r["priority"]
 ck("prediction_rows",len(pred)==q["n"]==27518);ck("unique_predictions",len({x["element_key"] for x in pred})==len(pred));yrole=[int(x["role_y"]) for x in pred];yrel=[int(x["relation_y"]) for x in pred];ck("role_count",sum(yrole)==q["role_positives"]==1292);ck("relation_count",sum(yrel)==q["relation_positives"]==2347)
 role_auc=auc(yrole,[x["p_role"] for x in pred]);role_gain=bits(yrole,[x["p_role_baseline"] for x in pred])-bits(yrole,[x["p_role"] for x in pred]);source_auc=auc(yrel,[x["p_source_relation"] for x in pred]);det=auc(yrel,[x["p_deterministic_overlap"] for x in pred]);full=auc(yrel,[x["p_role_plus_relation"] for x in pred]);gain=bits(yrel,[x["p_source_relation"] for x in pred])-bits(yrel,[x["p_role_plus_relation"] for x in pred])
 for name,a,b in [("role_auc",role_auc,q["role_auc"]),("role_gain",role_gain,q["role_gain_bits"]),("source_auc",source_auc,q["source_overlap_auc"]),("det_auc",det,q["deterministic_overlap_auc"]),("full_auc",full,q["role_plus_relation_auc"]),("auc_increment",full-source_auc,q["auc_increment"]),("relation_gain",gain,q["relation_gain_bits"])]:ck(name,abs(a-b)<1e-8)
 by=defaultdict(list)
 for x in pred:by[x["held_collection"]].append(x)
 ck("folds_84",len(by)==len(fold)==q["held_collections"]==84);positive=0
 for x in fold:
  z=by[x["held_collection"]];yy=[int(a["relation_y"]) for a in z];g=bits(yy,[a["p_source_relation"] for a in z])-bits(yy,[a["p_role_plus_relation"] for a in z]);ck("fold_gain:"+x["held_collection"],abs(g-float(x["gain_bits"]))<1e-8);positive+=g>0
 ck("positive_folds",positive==q["positive_held_collections"]==76)
 fields=set(rel[0]);forbidden={"word","surface","token","pos","parse","concept_id","parent_instruction_ordinal","role_label"};ck("hidden_layer_no_source_fields",not(fields&forbidden));ck("relation_rows",len(rel)==r["relation_oracle_rows"]==54867)
 for x in cap:
  avail=[z for z in rel if z["domain"]==x["domain"] and z[x["role"]+"_available"]=="1"];pos=sum(int(z[x["role"]+"_relation_y"]) for z in avail);ck("capacity:"+x["role"]+":"+x["domain"],len(avail)==int(x["available_rows"]) and pos==int(x["positives"]) and len(avail)-pos==int(x["negatives"]))
 ck("source_overlap_failure",source_auc>.65);ck("no_auc_increment",full-source_auc<.02);ck("pre_null_failed",q["pre_null_gate_pass"]==0 and not r["null_run"]);ck("other_roles_unscored",not r["other_roles_scored"]);ck("stage_b_locked",not r["stage_a_pass"] and not r["voynich_stage_b_authorized"] and not r["voynich_stage_b_created"] and r["voynich_rows_read"]==0 and not r["voynich_scored"]);ck("gdt381_not_read",not r["gdt381_target_artifacts_read"]);ck("f84",not any(r["f84"].values()))
 out={"schema":"GDT384_VALIDATION_V1","status":"PASS" if all(v for _,v in checks) else "FAIL","checks":len(checks),"passed":sum(v for _,v in checks),"details":{k:v for k,v in checks},"result_hash":sha(ART/"gdt384_result.json"),"validator_hash":sha(BASE/"src/validate_stage_a.py")};out["content_hash"]=content(out);(ART/"gdt384_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"passed":out["passed"],"checks":out["checks"]}));
 if out["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
