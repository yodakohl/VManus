#!/usr/bin/env python3
"""Independent nonimporting validation of GDT024."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt024_result.json";VAL=ROOT/"gdt024_validation.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def has(r,m,f):
 if f.startswith("HOST_EXACT:"):return m=="RESIDUAL_HOST"and r["residual_host"]==f.split(":",1)[1]
 tag,text=("F",r["family_surface"])if m=="SOURCE_FAMILY"else("H",r["residual_host"]);n=int(f[1:f.index(":")]);x=f.split(":",1)[1];p="^"+text+"$";return any(p[i:i+n]==x for i in range(len(p)-n+1))
def pmf(n,k,m):
 a=np.zeros(min(k,m)+1);d=math.comb(n,m)
 for x in range(max(0,m-(n-k)),min(m,k)+1):a[x]=math.comb(k,x)*math.comb(n-k,m-x)/d
 return a
def score(keys,pos,ctx):
 s=defaultdict(list)
 for key in keys:
  x=ctx[key];s[(x["page"],x["state"],x["bin"])].append((key in pos,x["post"]))
 law=np.array([1.]);obs=0;exp=num=den=0.;ns=0
 for v in s.values():
  n=len(v);m=sum(a for a,y in v);k=sum(y for a,y in v)
  if not(0<m<n and 0<k<n):continue
  ns+=1;o=sum(a and y for a,y in v);obs+=o;exp+=m*k/n;w=m*(n-m)/n;num+=w*(o/m-(k-o)/(n-m));den+=w;law=np.convolve(law,pmf(n,k,m))
 e=num/den if den else 0.;p=1.
 if den:
  d=abs(obs-exp);p=min(1.,float(law[np.abs(np.arange(len(law))-exp)>=d-1e-12].sum()))
 return e,p,obs,exp,ns
def close(a,b):return abs(float(a)-float(b))<7e-12
def main():
 checks=[];r=json.loads(RES.read_text());body=dict(r);digest=body.pop("result_content_sha256");checks+=[("schema",r["schema"]=="GDT024_POST_DY_FORM_GENERALIZATION_RESULT_V1"),("content",digest==csha(body))]
 for part in("inputs","implementation","outputs"):
  for n,d in r[part].items():checks.append((part+":"+n,sha(ROOT/n)==d))
 inv=read("gdt016_group_state_inventory.tsv");checks+=[("count",len(inv)==r["inventory_groups"]==15592),("f84",not any(x["locus"].startswith("f84r")for x in inv))];lookup={(x["locus"],int(x["group_index"])):x for x in inv};lines=defaultdict(list)
 for x in inv:lines[x["locus"]].append(x)
 ctx={}
 for loc,line in lines.items():
  line.sort(key=lambda x:int(x["group_index"]));after=0
  for x in line:
   n=int(x["group_count"]);z=(int(x["group_index"])-1)/(n-1)if n>1 else.5;k=(loc,int(x["group_index"]));ctx[k]={"page":x["page"],"state":x["record_state"],"bin":min(3,int(z*4)),"post":after};after=int(x["record_state"]=="DY_RESOLUTION")
 specs=(("QJB","SOURCE_FAMILY","F3:QJB","DY_RESOLUTION"),("KAL","RESIDUAL_HOST","H3:kal","AL_STATE"),("OKAL","RESIDUAL_HOST","HOST_EXACT:okal","AL_STATE"));sets={name:{k for k,x in lookup.items()if has(x,m,f)}for name,m,f,state in specs};allkeys=set(lookup);stored={(x["feature"],x["diagnostic"]):x for x in read("gdt024_dominant_form_deletions.tsv")}
 for name,m,f,state in specs:
  pos=sets[name];post=Counter(lookup[k]["token"]for k in pos if ctx[k]["post"]);total=Counter(lookup[k]["token"]for k in pos);order=[t for t,n in sorted(post.items(),key=lambda z:(-z[1],z[0]))]
  for drop in(0,1,2,4,8,16):
   rem=set(order[:drop]);p={k for k in pos if lookup[k]["token"]not in rem};e,pv,o,x,ns=score(allkeys,p,ctx);z=stored[(name,f"DROP_TOP_{drop}_POSTDY_TOKENS")];checks.append((f"drop:{name}:{drop}",z["removed_tokens"]=="|".join(sorted(rem))and int(z["remaining_token_types"])==len({lookup[k]["token"]for k in p})and int(z["remaining_occurrences"])==len(p)and close(z["conditional_effect"],e)and close(z["exact_p"],pv)and int(z["observed_postdy"])==o and close(z["expected_postdy"],x)and int(z["informative_strata"])==ns))
  p={k for k in pos if total[lookup[k]["token"]]<=5};e,pv,o,x,ns=score(allkeys,p,ctx);z=stored[(name,"RARE_TOKEN_TYPES_TOTAL_LE_5")];checks.append(("tail:"+name,int(z["remaining_token_types"])==len({lookup[k]["token"]for k in p})and int(z["remaining_occurrences"])==len(p)and close(z["conditional_effect"],e)and close(z["exact_p"],pv)and int(z["observed_postdy"])==o and close(z["expected_postdy"],x)))
 checks.append(("deletion_count",len(stored)==r["diagnostics"]==21))
 regs={(x["feature"],x["axis"],x["value"]):x for x in read("gdt024_register_transfer.tsv")}
 for name,m,f,state in specs:
  for axis in("section","currier","hand"):
   for value in sorted({x[axis]for x in inv}):
    keys={k for k,x in lookup.items()if x[axis]==value};e,pv,o,x,ns=score(keys,sets[name]&keys,ctx);z=regs[(name,axis,value)];checks.append((f"reg:{name}:{axis}:{value}",int(z["universe_groups"])==len(keys)and int(z["feature_occurrences"])==len(sets[name]&keys)and close(z["conditional_effect"],e)and close(z["exact_p"],pv)and int(z["observed_postdy"])==o and close(z["expected_postdy"],x)and int(z["informative_strata"])==ns))
 checks.append(("register_count",len(regs)==r["register_tests"]==39));controls={x["feature"]:x for x in read("gdt024_state_restricted_tests.tsv")}
 for name,m,f,state in specs:
  keys={k for k,x in lookup.items()if x["record_state"]==state};e,pv,o,x,ns=score(keys,sets[name]&keys,ctx);z=controls[name];checks.append(("state:"+name,int(z["state_universe_groups"])==len(keys)and int(z["feature_occurrences"])==len(sets[name]&keys)and close(z["conditional_effect"],e)and close(z["exact_p"],pv)and int(z["observed_postdy"])==o and close(z["expected_postdy"],x)))
 report=" ".join((ROOT/"GDT024_POST_DY_FORM_GENERALIZATION_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks+=[("control_count",len(controls)==r["state_controls"]==3),("interpretation",r["interpretation"]=={"QJB":"PRODUCTIVE_FORMAL_SUBTYPE_WITHIN_CURRIER_B","KAL_OKAL":"WHOLE_FORM_DOMINATED_LOCAL_SEQUENCE"}),("claims",all(x in report for x in("not merely recurrence","exact-form-dominated","zero currier-a capacity","f84r was not opened","no diagram role"))),("flags",r["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False}),("ledger",ledger.count("GDT024_CKPT001")==1)]
 fail=[n for n,ok in checks if not ok];v={"schema":"GDT024_POST_DY_FORM_GENERALIZATION_VALIDATION_V1","status":"PASS"if not fail else"FAIL","checks":len(checks),"failures":fail,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent nonimporting reconstruction of 21 dominant-form/tail diagnostics, 39 register tests, three within-state controls, hashes, f84r exclusion, ledger, and claims."};VAL.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps(v,sort_keys=True));
 if fail:raise SystemExit(1)
if __name__=="__main__":main()
