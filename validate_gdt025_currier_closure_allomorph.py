#!/usr/bin/env python3
"""Independent nonimporting GDT025 validation."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt025_result.json";VAL=ROOT/"gdt025_validation.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def fisher(a,b,c,d):
 n=a+b+c+d;r=a+b;k=a+c;lo=max(0,r-(n-k));hi=min(r,k)
 def lp(x):return math.lgamma(k+1)-math.lgamma(x+1)-math.lgamma(k-x+1)+math.lgamma(n-k+1)-math.lgamma(r-x+1)-math.lgamma(n-k-r+x+1)-math.lgamma(n+1)+math.lgamma(r+1)+math.lgamma(n-r+1)
 z=lp(a);xs=[lp(x)for x in range(lo,hi+1)if lp(x)<=z+1e-12];m=max(xs);return min(1.,math.exp(m)*sum(math.exp(x-m)for x in xs))
def pmf(n,k,m):
 a=np.zeros(min(k,m)+1);d=math.comb(n,m)
 for x in range(max(0,m-(n-k)),min(m,k)+1):a[x]=math.comb(k,x)*math.comb(n-k,m-x)/d
 return a
def score(keys,pos,ctx):
 s=defaultdict(list)
 for k in keys:
  x=ctx[k];s[(x["page"],x["state"],x["bin"])].append((k in pos,x["post"]))
 law=np.array([1.]);obs=0;exp=num=den=0.;ns=0
 for v in s.values():
  n=len(v);m=sum(a for a,y in v);k=sum(y for a,y in v)
  if not(0<m<n and 0<k<n):continue
  ns+=1;o=sum(a and y for a,y in v);obs+=o;exp+=m*k/n;w=m*(n-m)/n;num+=w*(o/m-(k-o)/(n-m));den+=w;law=np.convolve(law,pmf(n,k,m))
 e=num/den if den else 0.;p=1.
 if den:
  d=abs(obs-exp);p=min(1.,float(law[np.abs(np.arange(len(law))-exp)>=d-1e-12].sum()))
 return e,p,obs,exp,ns
def close(a,b,t=7e-12):return abs(float(a)-float(b))<t
def main():
 checks=[];r=json.loads(RES.read_text());body=dict(r);digest=body.pop("result_content_sha256");checks+=[("schema",r["schema"]=="GDT025_CURRIER_CLOSURE_ALLOMORPH_RESULT_V1"),("content",digest==csha(body))]
 for part in("inputs","implementation","outputs"):
  for n,d in r[part].items():checks.append((part+":"+n,sha(ROOT/n)==d))
 inv=read("gdt016_group_state_inventory.tsv");checks+=[("count",len(inv)==r["inventory_groups"]==15592),("f84",not any(x["locus"].startswith("f84r")for x in inv))];lookup={(x["locus"],int(x["group_index"])):x for x in inv};lines=defaultdict(list)
 for x in inv:lines[x["locus"]].append(x)
 ctx={};prev={};post=Counter();chain=Counter()
 for loc,line in lines.items():
  line.sort(key=lambda x:int(x["group_index"]));after=0
  for i,x in enumerate(line):
   n=int(x["group_count"]);z=(int(x["group_index"])-1)/(n-1)if n>1 else.5;k=(loc,int(x["group_index"]));ctx[k]={"page":x["page"],"state":x["record_state"],"bin":min(3,int(z*4)),"post":after};prev[k]=line[i-1]if i else None
   if i and line[i-1]["record_state"]=="DY_RESOLUTION":post[x["currier"]]+=1;chain[x["currier"]]+=int(x["record_state"]=="DY_RESOLUTION")
   after=int(x["record_state"]=="DY_RESOLUTION")
 stored={x["currier"]:x for x in read("gdt025_currier_closure_inventory.tsv")};cnt={}
 for cur in("A","B"):
  dy=[x for x in inv if x["currier"]==cur and x["record_state"]=="DY_RESOLUTION"];e=sum(x["residual_host"].endswith("e")for x in dy);eo=sum(x["residual_host"].endswith("eo")for x in dy);cnt[cur]=(e,eo);z=stored[cur];checks.append(("inventory:"+cur,int(z["dy_groups"])==len(dy)and int(z["terminal_e"])==e and int(z["terminal_eo"])==eo and int(z["other_terminal"])==len(dy)-e-eo and int(z["dy_followed_internal_boundaries"])==post[cur]and int(z["dy_to_dy"])==chain[cur]and close(z["dy_to_dy_rate"],chain[cur]/post[cur])))
 agg={x["test"]:x for x in read("gdt025_currier_aggregate_tests.tsv")};tables={"TERMINAL_E_VS_EO_BY_CURRIER":(cnt['A'][0],cnt['A'][1],cnt['B'][0],cnt['B'][1]),"DY_TO_DY_RATE_BY_CURRIER":(chain['A'],post['A']-chain['A'],chain['B'],post['B']-chain['B'])}
 for name,(a,b,c,d) in tables.items():
  z=agg[name];checks.append(("aggregate:"+name,[int(z[x])for x in("a","b","c","d")]==[a,b,c,d]and close(z["odds_ratio"],a*d/(b*c))and close(z["fisher_two_sided_p"],fisher(a,b,c,d),2e-70 if name.startswith('TERMINAL')else 2e-16)))
 motifs={"A":("QJAB","QKAB","LJAB","LKAB"),"B":("QJB","QKB","LJB","LKB")};tests={(x["currier"],x["family_motif"]):x for x in read("gdt025_family_branch_tests.tsv")}
 for cur,ms in motifs.items():
  keys={k for k,x in lookup.items()if x["currier"]==cur and x["record_state"]=="DY_RESOLUTION"}
  for m in ms:
   pos={k for k in keys if m in lookup[k]["family_surface"]};e,p,o,x,ns=score(keys,pos,ctx);z=tests[cur,m];checks.append((f"branch:{cur}:{m}",int(z["dy_universe"])==len(keys)and int(z["motif_occurrences"])==len(pos)and int(z["raw_postdy_occurrences"])==sum(ctx[k]["post"]for k in pos)and close(z["conditional_effect"],e)and close(z["exact_p"],p)and int(z["observed_informative"])==o and close(z["expected_informative"],x)and int(z["informative_strata"])==ns))
 repeat={(x["family_motif"],x["ablation"]):x for x in read("gdt025_repeat_ablation.tsv")};keys={k for k,x in lookup.items()if x["currier"]=="B"and x["record_state"]=="DY_RESOLUTION"}
 for m in motifs["B"]:
  base={k for k in keys if m in lookup[k]["family_surface"]};cases=(("ALL",base),("EXCLUDE_EXACT_TOKEN_REPEAT",{k for k in base if not(ctx[k]["post"]and prev[k]["token"]==lookup[k]["token"])}),("EXCLUDE_EXACT_FAMILY_REPEAT",{k for k in base if not(ctx[k]["post"]and prev[k]["family_surface"]==lookup[k]["family_surface"])}))
  for label,pos in cases:
   e,p,o,x,ns=score(keys,pos,ctx);z=repeat[m,label];checks.append((f"repeat:{m}:{label}",int(z["remaining_occurrences"])==len(pos)and close(z["conditional_effect"],e)and close(z["exact_p"],p)and int(z["observed_informative"])==o and close(z["expected_informative"],x)and int(z["informative_strata"])==ns))
 report=" ".join((ROOT/"GDT025_CURRIER_CLOSURE_ALLOMORPH_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks+=[("counts",len(tests)==r["branch_tests"]==8 and len(repeat)==r["repeat_ablations"]==12),("flags",r["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False}),("claims",all(x in report for x in("alternate formal realization","checkpoint-chain","lack of transition capacity","f84r was not opened","no role"))),("ledger",ledger.count("GDT025_CKPT001")==1)]
 fail=[n for n,ok in checks if not ok];v={"schema":"GDT025_CURRIER_CLOSURE_ALLOMORPH_VALIDATION_V1","status":"PASS"if not fail else"FAIL","checks":len(checks),"failures":fail,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent nonimporting reconstruction of Currier closure realization, two exact 2x2 tests, eight subtype tests, twelve repetition ablations, hashes, f84r exclusion, ledger, and claims."};VAL.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps(v,sort_keys=True));
 if fail:raise SystemExit(1)
if __name__=="__main__":main()
