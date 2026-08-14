#!/usr/bin/env python3
"""Independent exact-control validator for GDT015."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from run_gdt013_latent_role_propagation import all_strict_groups
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt015_result.json";VAL=ROOT/"gdt015_validation.json";PAIRS=(("ar","otar"),("al","otal"),("ol","otol"));OUT=("previous_dy","next_dy","previous_q","next_q")
def read(name):
 with (ROOT/name).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def hp(n,k,m):
 d=math.comb(n,m);return{x:Fraction(math.comb(k,x)*math.comb(n-k,m-x),d)for x in range(max(0,m-(n-k)),min(m,k)+1)}
def exact(parts):
 dist={0:Fraction(1)};obs=0;exp=Fraction();num=den=0.;ns=0
 for v in parts:
  n=len(v);m=sum(a for a,y in v);k=sum(y for a,y in v)
  if not(0<m<n and 0<k<n):continue
  ns+=1;x=sum(a and y for a,y in v);w=m*(n-m)/n;num+=w*(x/m-(k-x)/(n-m));den+=w;obs+=x;exp+=Fraction(m*k,n);nxt=defaultdict(Fraction)
  for i,pi in dist.items():
   for j,pj in hp(n,k,m).items():nxt[i+j]+=pi*pj
  dist=nxt
 d=abs(Fraction(obs)-exp);p=sum(v for x,v in dist.items()if abs(Fraction(x)-exp)>=d)if den else Fraction(1);return num/den if den else 0.,float(p),obs,float(exp),ns
def main():
 checks=[];result=json.loads(RES.read_text());copy=dict(result);digest=copy.pop("result_content_sha256");checks.extend([("schema",result["schema"]=="GDT015_POST_RESOLUTION_TRANSITION_RESULT_V1"),("content",digest==csha(copy))])
 for part in("inputs","implementation","outputs"):
  for n,d in result[part].items():checks.append((part+":"+n,sha(ROOT/n)==d))
 rows=[r for r in all_strict_groups()if r["grammar_scope"]=="CONFIRMED_PROSE"];by=defaultdict(list)
 for r in rows:by[r["locus"]].append(r)
 obs=[]
 for line in by.values():
  line.sort(key=lambda r:r["group_index"])
  for i,r in enumerate(line):
   p=(r["group_index"]-1)/(r["group_count"]-1)if r["group_count"]>1 else.5;z=dict(r);z["bin"]=min(3,int(p*4));z["previous_dy"]=int(i>0 and line[i-1]["dy_closure"]);z["next_dy"]=int(i+1<len(line)and line[i+1]["dy_closure"]);z["previous_q"]=int(i>0 and line[i-1]["stripped_prefix"]=="q");z["next_q"]=int(i+1<len(line)and line[i+1]["stripped_prefix"]=="q");obs.append(z)
 tests=read("gdt015_adjacency_tests.tsv");stored={r["test"]:r for r in tests};checks.extend([("corpus",len(rows)==result["strict_prose_groups"]==15592),("grid",len(tests)==13),("f84",not any(r["locus"].startswith("f84r")for r in rows)and result["f84r"]=={"retained":False,"joined":False,"scored":False})])
 for a,b in PAIRS:
  for out in OUT:
   st=defaultdict(list)
   for r in obs:
    if r["residual_host"]in(a,b):st[(r["page"],r["bin"])].append((r["residual_host"]==b,r[out]))
   e,p,o,x,n=exact(st.values());s=stored[a.upper()+"_TO_"+b.upper()+"__"+out.upper()];checks.append(("test:"+s["test"],abs(e-float(s["conditional_effect"]))<6e-13 and abs(p-float(s["exact_p"]))<6e-13 and o==int(s["observed_ot_outcomes"])and abs(x-float(s["expected_ot_outcomes"]))<6e-12 and n==int(s["informative_strata"])))
 st=defaultdict(list)
 for a,b in PAIRS:
  for r in obs:
   if r["residual_host"]in(a,b):st[(a,r["page"],r["bin"])].append((r["residual_host"]==b,r["previous_dy"]))
 e,p,o,x,n=exact(st.values());s=stored["POOLED_OT_VS_BARE__PREVIOUS_DY"];checks.append(("pooled",abs(e-float(s["conditional_effect"]))<6e-13 and abs(p-float(s["exact_p"]))<6e-13 and o==30 and abs(x-float(s["expected_ot_outcomes"]))<6e-12 and n==35))
 examples=read("gdt015_sequence_examples.tsv");checks.extend([("examples",len(examples)==result["examples"]==44 and all(r["previous_token"]!="LINE_START"for r in examples)),("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT015_CKPT001")==1)])
 report=(ROOT/"GDT015_POST_RESOLUTION_TRANSITION_REPORT.md").read_text().lower();checks.extend([("posthoc","post-hoc"in report and"position quartile"in report),("claim",all(x in report for x in("no morpheme","translation","f84r was not retained")))])
 failures=[n for n,ok in checks if not ok];v={"schema":"GDT015_POST_RESOLUTION_TRANSITION_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of twelve core-specific and one pooled exact page+position-quartile conditional tests, examples, f84 exclusion, hashes, ledger, and claims. Reuses validated strict-group loader."};VAL.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps(v,sort_keys=True));
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
