#!/usr/bin/env python3
"""Independent nonimporting GDT026 validation."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt026_result.json";VAL=ROOT/"gdt026_validation.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def pmf(n,k,m):
 a=np.zeros(min(k,m)+1);d=math.comb(n,m)
 for x in range(max(0,m-(n-k)),min(m,k)+1):a[x]=math.comb(k,x)*math.comb(n-k,m-x)/d
 return a
def score(keys,pos,ctx,outcome,omit=None,prob=True):
 s=defaultdict(list)
 for k in keys:
  x=ctx[k]
  if omit and x["folio"]==omit:continue
  s[(x["page"],x["state"],x["bin"])].append((k in pos,x[outcome]))
 law=np.array([1.]);obs=0;exp=num=den=0.;ns=0
 for v in s.values():
  n=len(v);m=sum(a for a,y in v);k=sum(y for a,y in v)
  if not(0<m<n and 0<k<n):continue
  ns+=1;o=sum(a and y for a,y in v);obs+=o;exp+=m*k/n;w=m*(n-m)/n;num+=w*(o/m-(k-o)/(n-m));den+=w
  if prob:law=np.convolve(law,pmf(n,k,m))
 e=num/den if den else 0.;p=1.
 if prob and den:
  d=abs(obs-exp);p=min(1.,float(law[np.abs(np.arange(len(law))-exp)>=d-1e-12].sum()))
 return e,p,obs,exp,ns
def close(a,b):return abs(float(a)-float(b))<7e-12
def branch(r):
 f=r["family_surface"]
 if"QJB"in f or"QKB"in f:return"Q_FAMILY"
 if"LJB"in f or"LKB"in f:return"L_FAMILY"
 return"OTHER"
def main():
 checks=[];r=json.loads(RES.read_text());body=dict(r);digest=body.pop("result_content_sha256");checks+=[("schema",r["schema"]=="GDT026_Q_L_BACKWARD_LINK_RESULT_V1"),("content",digest==csha(body))]
 for part in("inputs","implementation","outputs"):
  for n,d in r[part].items():checks.append((part+":"+n,sha(ROOT/n)==d))
 inv=read("gdt016_group_state_inventory.tsv");checks+=[("count",len(inv)==r["inventory_groups"]==15592),("f84",not any(x["locus"].startswith("f84r")for x in inv))];lines=defaultdict(list)
 for x in inv:lines[x["locus"]].append(x)
 keys=set();pos=set();lookup={};prev={};ctx={};phase=Counter()
 for loc,line in lines.items():
  line.sort(key=lambda x:int(x["group_index"]))
  for i,x in enumerate(line):
   b=branch(x)
   if x["currier"]!="B"or x["record_state"]!="DY_RESOLUTION"or b=="OTHER":continue
   n=int(x["group_count"]);z=(int(x["group_index"])-1)/(n-1)if n>1 else.5;k=(loc,int(x["group_index"]));pd=int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION");nd=int(i+1<len(line)and line[i+1]["record_state"]=="DY_RESOLUTION");p="ISOLATED"if not pd and not nd else"CHAIN_START"if not pd and nd else"CHAIN_END"if pd and not nd else"CHAIN_INTERNAL";phase[b,p]+=1;keys.add(k);lookup[k]=x;prev[k]=line[i-1]if i else None
   if b=="Q_FAMILY":pos.add(k)
   ctx[k]={"page":x["page"],"folio":x["physical_folio"],"state":x["record_state"],"bin":min(3,int(z*4)),"PREVIOUS_DY":pd,"NEXT_DY":nd,"LINE_START":int(i==0),"LINE_END":int(i==len(line)-1),"CHAIN_ENTRY":int(not pd and nd)}
 stored={x["branch"]:x for x in read("gdt026_chain_phase_inventory.tsv")}
 for b in("Q_FAMILY","L_FAMILY"):
  x=stored[b];checks.append(("phase:"+b,[int(x[n])for n in("isolated","chain_start","chain_internal","chain_end")]==[phase[b,p]for p in("ISOLATED","CHAIN_START","CHAIN_INTERNAL","CHAIN_END")]and int(x["total"])==sum(phase[b,p]for p in("ISOLATED","CHAIN_START","CHAIN_INTERNAL","CHAIN_END"))))
 tests={x["test_id"]:x for x in read("gdt026_direction_tests.tsv")};folios=sorted({ctx[k]["folio"]for k in keys})
 for outcome in("PREVIOUS_DY","NEXT_DY","LINE_START","LINE_END","CHAIN_ENTRY"):
  e,p,o,x,ns=score(keys,pos,ctx,outcome);lo=[score(keys,pos,ctx,outcome,f,False)[0]for f in folios];z=tests[outcome];checks.append(("direction:"+outcome,int(z["universe"])==len(keys)and int(z["q_family"])==len(pos)and close(z["conditional_effect"],e)and close(z["exact_p"],p)and int(z["observed_q_outcomes"])==o and close(z["expected_q_outcomes"],x)and int(z["informative_strata"])==ns and int(z["lofo_positive_effects"])==sum(v>0 for v in lo)and close(z["lofo_min_effect"],min(lo))and close(z["lofo_max_effect"],max(lo))))
 abl={x["ablation"]:x for x in read("gdt026_backward_link_ablations.tsv")};cases=[("ALL",lambda k:True),("EXCLUDE_EXACT_TOKEN_REPEAT",lambda k:not(ctx[k]["PREVIOUS_DY"]and prev[k]["token"]==lookup[k]["token"])),("EXCLUDE_EXACT_FAMILY_REPEAT",lambda k:not(ctx[k]["PREVIOUS_DY"]and prev[k]["family_surface"]==lookup[k]["family_surface"])),("EXCLUDE_IDENTICAL_HOST_REPEAT",lambda k:not(ctx[k]["PREVIOUS_DY"]and prev[k]["residual_host"]==lookup[k]["residual_host"]))]
 for name,keep in cases:
  k2={k for k in keys if keep(k)};p2=pos&k2;e,p,o,x,ns=score(k2,p2,ctx,"PREVIOUS_DY");z=abl[name];checks.append(("ablation:"+name,int(z["remaining_groups"])==len(k2)and int(z["q_family_groups"])==len(p2)and close(z["conditional_effect"],e)and close(z["exact_p"],p)and int(z["observed_q_previous_dy"])==o and close(z["expected_q_previous_dy"],x)and int(z["informative_strata"])==ns))
 report=" ".join((ROOT/"GDT026_Q_L_BACKWARD_LINK_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks+=[("counts",len(keys)==r["ql_universe"]==1421 and len(pos)==r["q_family_groups"]==1000 and len(tests)==r["direction_tests"]==5 and len(abl)==r["ablations"]==4),("flags",r["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False}),("claims",all(x in report for x in("what came before","not literal copying","one-bit local history flag","f84r was not opened","no role"))),("ledger",ledger.count("GDT026_CKPT001")==1)]
 fail=[n for n,ok in checks if not ok];v={"schema":"GDT026_Q_L_BACKWARD_LINK_VALIDATION_V1","status":"PASS"if not fail else"FAIL","checks":len(checks),"failures":fail,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of phase inventory, five directional tests, all LOFO effects, four repetition ablations, hashes, f84r exclusion, ledger, and claims."};VAL.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps(v,sort_keys=True));
 if fail:raise SystemExit(1)
if __name__=="__main__":main()
