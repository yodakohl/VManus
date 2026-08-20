#!/usr/bin/env python3
"""Nonimporting source and retained-prediction validation for GDT385."""
from __future__ import annotations
import csv,gzip,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

def find_root(p):
 for x in (p,*p.parents):
  if (x/"AGENTS.md").is_file() and (x/".git").exists():return x
 raise RuntimeError("repository root not found")
ROOT=find_root(Path(__file__).resolve());BASE=ROOT/"experiments/yolo/gdt385_corema_parent_link_consequence";ART=BASE/"artifacts"
ROUTES={"CMP_PARENT_01":lambda r:r["role"]=="REF","CMP_PARENT_02":lambda r:r["role"]=="TIME","CMP_PARENT_03":lambda r:r["role"]=="ALTERNATIVE","CMP_PARENT_04":lambda r:r["annotation_flags"]=="exclusion"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rankdata(x):
 a=np.asarray(x,float);o=np.argsort(a,kind="stable");z=np.empty(len(a));i=0
 while i<len(a):
  j=i+1
  while j<len(a) and a[o[j]]==a[o[i]]:j+=1
  z[o[i:j]]=(i+j+1)/2;i=j
 return z
def auc(y,s):
 y=np.asarray(y,int);n1=int(y.sum());n0=len(y)-n1
 if not n1 or not n0:return float("nan")
 q=rankdata(s);return float((q[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def bbin(y,p):
 y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-12,1-1e-12);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def close(a,b,tol=1e-8):return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)
check_groups=Counter();failures=[]
def ck(n,x):
 group=n.split(":",1)[0];check_groups[group]+=1
 if not x:failures.append(n);raise AssertionError(n)

result=json.loads((ART/"gdt385_result.json").read_text());q=dict(result);given=q.pop("content_hash");ck("result_content_hash",given==hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest())
for p,h in result["inputs"].items():ck("input_hash:"+p,sha(ROOT/p)==h)
for p,h in result["outputs"].items():ck("output_hash:"+p,sha(ROOT/p)==h)
for p,h in result["implementation"].items():ck("implementation_hash:"+p,sha(ROOT/p)==h)
ck("no_voynich",result["voynich_rows_read"]==0 and result["voynich_stage_authorized"] is False)
ck("f84_false",not any(result["f84"].values()))

with gzip.open(ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz","rt",encoding="utf-8",newline="") as f:obs=[r for r in csv.DictReader(f,delimiter="\t") if r["domain"]=="COREMA"]
oracle=list(csv.DictReader((ROOT/"gdt176_corema_role_oracle.tsv").open(encoding="utf-8",newline=""),delimiter="\t"));om={f"COREMA:{r['collection_id']}:{r['recipe_id']}:{r['element_ordinal']}":r for r in oracle};keys={r["element_key"] for r in obs};by=defaultdict(list)
for r in oracle:by[(r["collection_id"],r["recipe_id"])].append(r)
expected={};invalid=[]
for (c,rec),rows in by.items():
 rows.sort(key=lambda r:int(r["element_ordinal"]));ins=[r for r in rows if r["role"]=="INSTRUCTION"]
 for r in rows:
  k=f"COREMA:{c}:{rec}:{r['element_ordinal']}"
  if k not in keys or int(r["element_ordinal"])<=1:continue
  p=int(r["parent_instruction_ordinal"])
  if not p:expected[k]=(0,"NONE");continue
  if p>len(ins):invalid.append(k);continue
  t=ins[p-1];tk=f"COREMA:{c}:{rec}:{t['element_ordinal']}";d=int(r["element_ordinal"])-int(t["element_ordinal"])
  if tk not in keys or d<=0 or d>=14:invalid.append(k);continue
  expected[k]=(d,tk)
ck("source_observations",len(obs)==27349);ck("eligible_pivots",len(expected)==26169);ck("valid_links",sum(d>0 for d,t in expected.values())==11415);ck("invalid_links",len(invalid)==87)

with gzip.open(ART/"gdt385_predictions.tsv.gz","rt",encoding="utf-8",newline="") as f:pred=list(csv.DictReader(f,delimiter="\t"))
scores={r["route_id"]:r for r in csv.DictReader((ART/"gdt385_route_scores.tsv").open(),delimiter="\t")};folds=list(csv.DictReader((ART/"gdt385_collection_folds.tsv").open(),delimiter="\t"));null=list(csv.DictReader((ART/"gdt385_null_worlds.tsv").open(),delimiter="\t"))
ck("prediction_count",len(pred)==4*len(expected));ck("prediction_unique",len({(r["route_id"],r["element_key"]) for r in pred})==len(pred));ck("null_worlds",len(null)==2048)
byroute=defaultdict(list)
for r in pred:byroute[r["route_id"]].append(r)
for route,fn in ROUTES.items():
 rr=byroute[route];ck(route+":keys",{r["element_key"] for r in rr}==set(expected));yrole=[];pr=[];pr0=[];pj=[];sb=fb=0.;sok=fok=0;linkn=0;lookup_n=lookup_ok=0;fg=Counter();fnn=Counter()
 for r in rr:
  d,t=expected[r["element_key"]];role=int(fn(om[r["element_key"]]));ck(route+":role_y",int(r["role_y"])==role);ck(route+":relation_y",r["relation_class"]==("NONE" if d==0 else "D"+str(d)));ck(route+":target",r["target_element_key"]==t)
  yrole.append(role);pr.append(float(r["p_role"]));pr0.append(float(r["p_role_baseline"]));pj.append(float(r["p_exact_joint_role"]));sb-=math.log2(float(r["source_true_probability"]));fb-=math.log2(float(r["role_true_probability"]));true="NONE" if d==0 else "D"+str(d);sok+=r["source_prediction"]==true;fok+=r["role_prediction"]==true;linkn+=d>0;fold=r["held_collection"];fg[fold]-=math.log2(float(r["role_true_probability"]));fnn[fold]-=math.log2(float(r["source_true_probability"]));lp=r["exact_source_lookup_prediction"]
  if lp!="UNSEEN":lookup_n+=1;lookup_ok+=lp==true
 s=scores[route];ck(route+":role_auc",close(auc(yrole,pr),s["role_auc"]));ck(route+":role_gain",close(bbin(yrole,pr0)-bbin(yrole,pr),s["role_gain_bits"]));ck(route+":joint_auc",close(auc(yrole,pj),s["exact_joint_role_auc"]));ck(route+":source_bits",close(sb,s["source_relation_bits"]));ck(route+":full_bits",close(fb,s["role_relation_bits"]));ck(route+":gain",close(sb-fb,s["relation_gain_bits"]));ck(route+":top1_source",close(sok/len(rr),s["source_relation_top1"]));ck(route+":top1_full",close(fok/len(rr),s["role_relation_top1"]));ck(route+":lookup",lookup_n==int(s["exact_signature_coverage"]) and close(lookup_ok/lookup_n,s["exact_signature_accuracy"]));ck(route+":positive_folds",sum(fg[f]<fnn[f] for f in fg)==int(s["positive_gain_collections"]));
 for fr in [x for x in folds if x["route_id"]==route]:ck(route+":fold:"+fr["held_collection"],close(fnn[fr["held_collection"]],fr["source_bits"]) and close(fg[fr["held_collection"]],fr["role_bits"]) and close(fnn[fr["held_collection"]]-fg[fr["held_collection"]],fr["gain_bits"]))
 p=(1+sum(float(x["max4_gain_bits"])>=float(s["relation_gain_bits"]) for x in null))/2049;ck(route+":max4_p",close(p,s["joint_max4_p"]))
 gate=float(s["role_auc"])>=.60 and float(s["role_gain_bits"])>0 and int(s["visible_role_links"])>=50 and int(s["link_collections"])>=5 and not int(s["exact_signature_perfect"]) and float(s["relation_gain_bits"])>0 and int(s["positive_gain_collections"])>=4 and float(s["target_mrr_delta"])>=0 and float(s["mobile_fraction"])>=.20 and float(s["joint_max4_p"])<=.05;ck(route+":gate",int(gate)==int(s["gate_pass"]))
passed=sum(int(x["gate_pass"]) for x in scores.values());priority=bool(int(scores["CMP_PARENT_01"]["gate_pass"]));ck("decision",result["routes_passing"]==passed and result["priority_route_pass"]==priority and result["instrument_pass"]==(priority and passed>=3) and result["status"]=="COMPARATOR_PARENT_LINK_INSTRUMENT_FAILED_STOP_BEFORE_VOYNICH")
total=sum(check_groups.values());out={"schema":"GDT385_VALIDATION_V1","status":"PASS","scope":"INDEPENDENT_SOURCE_AND_RETAINED_PREDICTION_VALIDATION","checks_passed":total,"checks_total":total,"check_groups":dict(sorted(check_groups.items())),"failures":failures,"result_hash":sha(ART/"gdt385_result.json")}
(ART/"gdt385_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {total}/{total}")
