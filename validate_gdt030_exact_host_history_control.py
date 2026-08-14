#!/usr/bin/env python3
"""Independent nonimporting GDT030 validation."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt030_result.json";VAL=ROOT/"gdt030_validation.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def branch(f):
 if"QJB"in f or"QKB"in f:return"Q"
 if"LJB"in f or"LKB"in f:return"L"
 return"OTHER"
def pmf(n,k,m):
 out=np.zeros(min(k,m)+1);den=math.comb(n,m)
 for x in range(max(0,m-(n-k)),min(m,k)+1):out[x]=math.comb(k,x)*math.comb(n-k,m-x)/den
 return out
def score(rows,level):
 strata=defaultdict(list)
 for x in rows:strata[(x[level],x["host"],x["state"],x["position_bin"])].append((x["branch"]=="Q",x["previous_dy"]))
 law=np.array([1.]);obs=0;exp=num=den=0.;nstr=0
 for v in strata.values():
  n=len(v);m=sum(q for q,y in v);k=sum(y for q,y in v)
  if not(0<m<n and 0<k<n):continue
  nstr+=1;o=sum(q and y for q,y in v);obs+=o;exp+=m*k/n;w=m*(n-m)/n;num+=w*(o/m-(k-o)/(n-m));den+=w;law=np.convolve(law,pmf(n,k,m))
 effect=num/den if den else 0.;p=1.
 if den:d=abs(obs-exp);p=min(1.,float(law[np.abs(np.arange(len(law))-exp)>=d-1e-12].sum()))
 return effect,p,nstr,obs,exp
def close(a,b):return abs(float(a)-float(b))<7e-10
def main():
 checks=[];result=json.loads(RES.read_text());body=dict(result);digest=body.pop("result_content_sha256");checks +=[("schema",result["schema"]=="GDT030_EXACT_HOST_HISTORY_CONTROL_RESULT_V1"),("content",digest==csha(body)),("status",result["status"]=="EXACT_HOST_CONTROLLED_HISTORY_OPERATOR_NOT_CONFIRMED")]
 for section in("inputs","implementation","outputs"):
  for name,digest in result[section].items():checks.append((f"hash:{section}:{name}",sha(ROOT/name)==digest))
 inv=read("gdt016_group_state_inventory.tsv");checks +=[("inventory",len(inv)==15592),("f84r",not any(r["locus"].startswith("f84r")for r in inv))];lines=defaultdict(list)
 for r in inv:lines[r["locus"]].append(r)
 data=[]
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]))
  for i,r in enumerate(line):
   b=branch(r["family_surface"])
   if r["currier"]!="B"or b=="OTHER":continue
   n=int(r["group_count"]);z=(int(r["group_index"])-1)/(n-1)if n>1 else.5;data.append({"branch":b,"host":r["residual_host"],"state":r["record_state"],"page":r["page"],"folio":r["physical_folio"],"section":r["section"],"position_bin":min(3,int(z*4)),"previous_dy":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION"),"token":r["token"]})
 seen=defaultdict(set)
 for x in data:seen[x["host"],x["state"]].add(x["branch"])
 eligible={k for k,v in seen.items()if v=={"Q","L"}};panel=[x for x in data if(x["host"],x["state"])in eligible];expected=[]
 for host,state in sorted(eligible):
  x=[r for r in panel if r["host"]==host and r["state"]==state];c=Counter((r["branch"],r["previous_dy"])for r in x);expected.append({"residual_host":host,"state":state,"groups":str(len(x)),"q_postdy":str(c["Q",1]),"q_not_postdy":str(c["Q",0]),"l_postdy":str(c["L",1]),"l_not_postdy":str(c["L",0]),"q_tokens":"|".join(sorted({r["token"]for r in x if r["branch"]=="Q"})),"l_tokens":"|".join(sorted({r["token"]for r in x if r["branch"]=="L"})),"claim_state":"EXACT_HOST_BRANCH_CAPACITY_NOT_MEANING"})
 checks.append(("overlap_inventory",expected==read("gdt030_exact_host_overlap_inventory.tsv")));stored={(r["partition"],r["matching_level"]):r for r in read("gdt030_exact_host_history_tests.tsv")}
 for partition,rows in[("ALL",panel)]+[(s,[x for x in panel if x["state"]==s])for s in sorted({x["state"]for x in panel})]:
  for level in("page","folio","section"):
   e,p,n,o,z=score(rows,level);r=stored[partition,level.upper()];checks.append((f"test:{partition}:{level}",int(r["groups"])==len(rows)and close(r["effect"],e)and close(r["exact_p"],p)and int(r["informative_strata"])==n and int(r["observed_q_postdy"])==o and close(r["expected_q_postdy"],z)))
 def same_snapshot(left,right):
  numeric=("effect","exact_p","expected_q_postdy")
  return all(close(left[k],right[k])for k in numeric)and all(str(left[k])==right[k]for k in right if k not in numeric)
 checks +=[("counts",result["groups"]==len(panel)==350 and result["eligible_host_state_cells"]==len(eligible)==8 and result["tests"]==len(stored)==12),("snapshots",same_snapshot(result["primary"],stored["ALL","PAGE"])and same_snapshot(result["folio"],stored["ALL","FOLIO"])and same_snapshot(result["section"],stored["ALL","SECTION"])),("flags",result["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False})]
 report=" ".join((ROOT/"GDT030_EXACT_HOST_HISTORY_CONTROL_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks +=[("claims",all(x in report for x in("does not establish a separable q/l history operator","too coarse","small","f84r was not opened","no role"))),("ledger",ledger.count("GDT030_CKPT001")==1)]
 failures=[n for n,ok in checks if not ok];validation={"schema":"GDT030_EXACT_HOST_HISTORY_CONTROL_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of eight exact host-state overlap cells and all twelve page/folio/section conditional tests, hashes, f84r exclusion, ledger, and claims."};VAL.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True));
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
