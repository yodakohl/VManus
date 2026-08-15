#!/usr/bin/env python3
"""Independent reconstruction for GDT042."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";OCC=ROOT/"gdt042_complete_carrier_contexts.tsv";TESTS=ROOT/"gdt042_context_tests.tsv";RESULT=ROOT/"gdt042_result.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt042_validation.json";FEATURES=("late_half","field_start","preclose_or_close","after_dy","before_dy","physical_line_end")
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def reconstruct(rows):
 lines=defaultdict(list)
 for r in rows:assert not r["locus"].startswith("f84r");lines[r["locus"]].append(r)
 out=[]
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)!=n or {int(r["group_index"])for r in line}!=set(range(1,n+1)):continue
  reg="HB"if line[0]["section"]=="H"and line[0]["currier"]=="B"else"SB"if line[0]["section"]=="S"and line[0]["currier"]=="B"else"OUT"
  if reg=="OUT":continue
  fields=[];cur=[]
  for i,r in enumerate(line):
   cur.append((i,r))
   if r["record_state"]=="DY_RESOLUTION":fields.append((cur,True));cur=[]
  if cur:fields.append((cur,False))
  address={i:(fi,j)for fi,(f,c)in enumerate(fields)for j,(i,r)in enumerate(f)}
  for i,r in enumerate(line):
   if r["stripped_prefix"]not in{"ch","che","sh"}:continue
   inner=r["residual_host"].startswith("d")and len(r["residual_host"])>1;base=r["residual_host"][1:]if inner else r["residual_host"]
   if base=="y":continue
   fi,j=address[i];f,closed=fields[fi];size=len(f);position="SINGLE"if size==1 else"FIELD_START"if j==0 else"FIELD_CLOSE"if closed and j==size-1 else"OPEN_FIELD_END"if j==size-1 else"PRECLOSE"if closed and j==size-2 else"FIELD_INTERNAL"
   out.append({"locus":locus,"physical_folio":r["physical_folio"],"register":reg,"hand":r["hand"],"group_index":r["group_index"],"group_count":r["group_count"],"token":r["token"],"wrapper":r["stripped_prefix"],"residual_host":r["residual_host"],"base_host":base,"inner_d":str(int(inner)),"field_position":position,"late_half":str(int(n==1 or i/(n-1)>=.5)),"field_start":str(int(position=="FIELD_START")),"preclose_or_close":str(int(position in{"PRECLOSE","FIELD_CLOSE"})),"after_dy":str(int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION")),"before_dy":str(int(i+1<n and line[i+1]["record_state"]=="DY_RESOLUTION")),"physical_line_end":str(int(i==n-1))})
 out.sort(key=lambda r:(("HB","SB").index(r["register"]),r["physical_folio"],r["locus"],int(r["group_index"])));return out
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def test(rows,regs,feature):
 z=[r for r in rows if r["register"]in regs];by=defaultdict(list)
 for r in z:by[r["physical_folio"],r["base_host"]].append(r)
 pm={0:1.};N=obs=0;exp=0.;strata=0
 for a in by.values():
  n=len(a);D=sum(r["inner_d"]=="1"for r in a);K=sum(r[feature]=="1"for r in a)
  if not D:continue
  N+=D;obs+=sum(r["inner_d"]=="1"and r[feature]=="1"for r in a);exp+=D*K/n;strata+=int(0<K<n);pm=conv(pm,hyper(n,K,D))
 ep=sum(p for x,p in pm.items()if x>=obs);dp=sum(p for x,p in pm.items()if x<=obs);two=min(1.,2*min(ep,dp))
 return{"registers":"+".join(regs),"feature":feature,"carrier_occurrences":len(z),"inner_d_occurrences":N,"observed_hits":obs,"expected_hits":exp,"rate_effect":(obs-exp)/N,"eligible_strata":strata,"enrichment_p":ep,"depletion_p":dp,"two_sided_p":two,"null_min":min(pm),"null_max":max(pm),"bonferroni_18_p":min(1.,two*18)}
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 checks={};rows=reconstruct(read(SOURCE));checks["occurrences_exact"]=read(OCC)==rows and len(rows)==674 and sum(r["inner_d"]=="1"for r in rows)==63
 expected=[test(rows,regs,f)for regs in(("HB",),("SB",),("HB","SB"))for f in FEATURES];actual=read(TESTS);ok=len(actual)==18
 for a,e in zip(actual,expected):
  for k in("registers","feature","carrier_occurrences","inner_d_occurrences","observed_hits","eligible_strata","null_min","null_max"):ok&=a[k]==str(e[k])
  for k in("expected_hits","rate_effect","enrichment_p","depletion_p","two_sided_p","bonferroni_18_p"):ok&=close(a[k],e[k])
 checks["all_18_exact_tests"]=ok
 pooled=[r for r in expected if r["registers"]=="HB+SB"];checks["no_passing_context"]=not any(abs(r["rate_effect"])>=.1 and r["bonferroni_18_p"]<=.05 and next(x for x in expected if x["registers"]=="HB"and x["feature"]==r["feature"])["rate_effect"]*next(x for x in expected if x["registers"]=="SB"and x["feature"]==r["feature"])["rate_effect"]>0 for r in pooled)and max(abs(r["rate_effect"])for r in pooled)<.03
 result=json.loads(RESULT.read_text());body=dict(result);claim=body.pop("result_content_sha256");checks["result_hash"]=csha(body)==claim;checks["status"]=result["status"]=="CARRIER_D_STACK_HAS_NO_STABLE_COARSE_LOCAL_CONTEXT_FUNCTION";checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents")for name,digest in result[fam].items())and all(sha(ROOT/name)==digest for name,digest in result["implementation"].items());checks["f84_sealed"]=not any(result["f84r"].values())
 report=(ROOT/"GDT042_CARRIER_D_CONTEXT_FUNCTION_REPORT.md").read_text();checks["claim_ceiling"]="real combinatorial"in report and"does not consistently select"in report and"No meaning"in report
 ledger=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT042_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT042_CARRIER_D_CONTEXT_FUNCTION_VALIDATION_V1","status":"PASS_INDEPENDENT_EXACT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent complete-line context reconstruction and exact base-host by physical-folio tests."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
