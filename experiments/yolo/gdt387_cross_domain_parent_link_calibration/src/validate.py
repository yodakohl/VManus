#!/usr/bin/env python3
from __future__ import annotations
import csv,gzip,hashlib,json,math
from collections import Counter
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt387_cross_domain_parent_link_calibration";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 op=gzip.open if p.suffix==".gz" else open
 with op(p,"rt",encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def rankdata(x):
 a=np.asarray(x,float);o=np.argsort(a,kind="stable");z=np.empty(len(a),float);i=0
 while i<len(a):
  j=i+1
  while j<len(a) and a[o[j]]==a[o[i]]:j+=1
  z[o[i:j]]=(i+j+1)/2;i=j
 return z
def auc(y,s):
 y=np.asarray(y,int);n1=int(y.sum());n0=len(y)-n1;q=rankdata(s);return float((q[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def bitsbin(y,p):
 y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-15,1-1e-15);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
c=[]
def ck(n,x):assert x,n;c.append(n)
def main():
 result=json.loads((ART/"gdt387_result.json").read_text());q=dict(result);h=q.pop("content_hash");ck("content",h==hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest())
 for p,h in result["inputs"].items():ck("input:"+p,sha(ROOT/p)==h)
 for p,h in result["outputs"].items():ck("output:"+p,sha(ROOT/p)==h)
 for p,h in result["implementation"].items():ck("implementation:"+p,sha(ROOT/p)==h)
 score=read(ART/"gdt387_route_score.tsv")[0];folds=read(ART/"gdt387_file_folds.tsv");pred=read(ART/"gdt387_predictions.tsv.gz");oracle=read(ART/"gdt387_hidden_governor_oracle.tsv.gz");null=read(ART/"gdt387_null_worlds.tsv")
 ck("oracle_schema",set(oracle[0])=={"element_key","source_file","record_id","element_ordinal","anonymous_role_y","governor_key","governor_ordinal","signed_distance","distance_class"})
 ck("oracle_unique",len({x["element_key"] for x in oracle})==len(oracle));ck("prediction_join",{x["element_key"] for x in pred}.issubset({x["element_key"] for x in oracle}) and len(pred)==int(score["n"]))
 y=np.array([int(x["anonymous_role_y"]) for x in pred]);pb=np.array([float(x["p_role_baseline"]) for x in pred]);pr=np.array([float(x["p_role"]) for x in pred]);t0=np.array([float(x["source_true_target_probability"]) for x in pred]);t1=np.array([float(x["role_true_target_probability"]) for x in pred]);sr=np.array([int(x["source_target_rank"]) for x in pred]);fr=np.array([int(x["role_target_rank"]) for x in pred])
 rg=bitsbin(y,pb)-bitsbin(y,pr);sg=float(-np.log2(t0).sum());fg=float(-np.log2(t1).sum());gain=sg-fg
 ck("role_counts",int(y.sum())==110 and len({x["held_file"] for x in pred if x["anonymous_role_y"]=="1"})==47);ck("role_metrics",abs(auc(y,pr)-float(score["role_auc"]))<1e-9 and abs(rg-float(score["role_gain_bits"]))<1e-8)
 ck("target_bits",abs(sg-float(score["source_governor_bits"]))<1e-7 and abs(fg-float(score["role_governor_bits"]))<1e-7 and abs(gain-float(score["governor_gain_bits"]))<1e-7)
 ck("target_ranks",abs(np.mean(sr==1)-float(score["source_target_top1"]))<1e-12 and abs(np.mean(fr==1)-float(score["role_target_top1"]))<1e-12 and abs(np.mean(1/sr)-float(score["source_target_mrr"]))<1e-12 and abs(np.mean(1/fr)-float(score["role_target_mrr"]))<1e-12)
 ck("folds",len(folds)==84 and sum(int(x["n"]) for x in folds)==len(pred) and sum(float(x["gain_bits"])>0 for x in folds)==int(score["positive_files"]))
 ck("fold_additivity",abs(sum(float(x["gain_bits"]) for x in folds)-gain)<1e-6);ck("null",len(null)==2048 and abs((1+sum(float(x["gain_bits"])>=gain for x in null))/2049-float(score["permutation_p"]))<1e-12)
 gate=bool(int(score["role_pivots"])>=100 and int(score["role_files"])>=40 and float(score["role_auc"])>=.65 and float(score["role_gain_bits"])>0 and gain>0 and int(score["positive_files"])>=42 and float(score["target_mrr_delta"])>=0 and float(score["mobile_fraction"])>=.2 and float(score["permutation_p"])<=.05)
 ck("gate",int(gate)==int(score["gate_pass"]));ck("status",result["status"]==("CROSS_DOMAIN_PARENT_LINK_SIGNATURE_SUPPORTED" if gate else "CROSS_DOMAIN_PARENT_LINK_SIGNATURE_NOT_SUPPORTED"));ck("no_voynich",result["voynich_rows_read"]==0 and not any(result["f84"].values()))
 out={"schema":"GDT387_VALIDATION_V1","status":"PASS","scope":"INDEPENDENT_RETAINED_PREDICTION_ACCOUNTING_NOT_MODEL_REFIT","checks_passed":len(c),"checks_total":len(c),"checks":c,"result_hash":sha(ART/"gdt387_result.json")};(ART/"gdt387_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(c)}/{len(c)}")
if __name__=="__main__":main()
