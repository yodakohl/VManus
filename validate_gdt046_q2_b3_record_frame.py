#!/usr/bin/env python3
"""Independent exact reconstruction for GDT046."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";CONS=ROOT/"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv";SEP=ROOT/"experiments/semantic_assumptions/results/source_separator_transcription.tsv";LINES=ROOT/"gdt046_line_frames.tsv";ATLAS=ROOT/"gdt046_opener_atlas.tsv";TESTS=ROOT/"gdt046_transfer_tests.tsv";RESULT=ROOT/"gdt046_result.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt046_validation.json";REGS=("HA","HB","SB","OB","OA")
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def reg(r):
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["currier"]=="B":return"OB"
 return"OA"
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def score(rows,member,regs):
 by=defaultdict(list)
 for r in rows:
  if r["register"]in regs:by[r["physical_folio"],r["paragraph_start"],r["length_bucket"]].append(r)
 pm={0:1.};obs=0;exp=0.;strata=0
 for z in by.values():
  n=len(z);O=sum(r["opening_member"]==member for r in z);C=sum(r["closing_member"]=="B3"for r in z)
  if not O or not C:continue
  strata+=1;obs+=sum(r["opening_member"]==member and r["closing_member"]=="B3"for r in z);exp+=O*C/n;pm=conv(pm,hyper(n,O,C))
 return obs,exp,obs-exp,strata,sum(p for x,p in pm.items()if x>=obs),min(pm),max(pm)
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 checks={};inv=read(SOURCE);checks["f84_source_excluded"]=not any(r["locus"].startswith("f84r")for r in inv);by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 complete={l:sorted(z,key=lambda r:int(r["group_index"]))for l,z in by.items()if len(z)==int(z[0]["group_count"])};keys={(l,r["group_index"])for l,z in complete.items()for r in z};cons={};seps={}
 with CONS.open(encoding="utf-8",newline="")as h:
  header=h.readline();fields=next(csv.reader([header],delimiter="\t"))
  for raw in h:
   if raw.startswith("f84r."):continue
   first=raw.split("\t",1)[0];locus,idx=first.rsplit("|C",1);key=(locus,str(int(idx)))
   if key in keys:cons[key]=dict(zip(fields,next(csv.reader([raw],delimiter="\t"))))
 with SEP.open(encoding="utf-8",newline="")as h:
  header=h.readline();fields=next(csv.reader([header],delimiter="\t"))
  for raw in h:
   if raw.startswith(("ZL3b|f84r.","IT2a|f84r.","RF1b|f84r.")):continue
   vals=next(csv.reader([raw],delimiter="\t"));r=dict(zip(fields,vals))
   if r["edition"]=="ZL3b"and r["source_group_index"]=="1"and r["locus"]in complete:seps[r["locus"]]=r
 rows=[]
 for locus,line in complete.items():
  if locus not in seps:continue
  f=cons[(locus,line[0]["group_index"])];l=cons[(locus,line[-1]["group_index"])];fc=tuple(f[x].split()[0]for x in("zl_sta_codes","it_sta_codes","rf_sta_codes"));lc=tuple(l[x].split()[-1]for x in("zl_sta_codes","it_sta_codes","rf_sta_codes"))
  if len(set(fc))>1 or len(set(lc))>1:continue
  n=len(line);rows.append({"locus":locus,"page":line[0]["page"],"physical_folio":line[0]["physical_folio"],"register":reg(line[0]),"hand":line[0]["hand"],"group_count":str(n),"length_bucket":str(n)if n<10 else"10PLUS","paragraph_start":seps[locus]["paragraph_start"],"opening_token":line[0]["token"],"opening_member":fc[0],"closing_token":line[-1]["token"],"closing_member":lc[0],"q2_open":str(int(fc[0]=="Q2")),"b3_close":str(int(lc[0]=="B3"))})
 rows.sort(key=lambda r:(REGS.index(r["register"]),r["physical_folio"],r["locus"]));checks["line_frames_exact"]=rows==read(LINES)and len(rows)==1164 and all((r["opening_token"].startswith("t"))==(r["opening_member"]=="Q2")for r in rows)
 actual=read(TESTS);specs=[("DISCOVERY_HB_SB",("HB","SB")),("TRANSFER_HA_OB_OA",("HA","OB","OA")),("ALL_REGISTERS",REGS)];ok=True
 for name,regs in specs:
  obs,exp,exc,n,p,lo,hi=score(rows,"Q2",regs);a=next(r for r in actual if r["comparison"]==name);ok&=a["observed_pairs"]==str(obs)and close(a["expected_pairs"],exp)and close(a["pair_excess"],exc)and a["eligible_strata"]==str(n)and close(a["one_sided_p"],p)and a["null_min"]==str(lo)and a["null_max"]==str(hi)
 checks["transfer_tests_exact"]=ok
 aa=read(ATLAS);support=Counter(r["opening_member"]for r in rows);ok=len(aa)==10
 for a in aa:
  obs,exp,exc,n,p,lo,hi=score(rows,a["opening_member"],REGS);ok&=int(a["support"])==support[a["opening_member"]]and a["observed_pairs"]==str(obs)and close(a["expected_pairs"],exp)and close(a["one_sided_p"],p)
 checks["opener_atlas_exact"]=ok and aa[0]["opening_member"]=="Q2"and close(aa[0]["bonferroni_p"],float(aa[0]["one_sided_p"])*10)
 result=json.loads(RESULT.read_text());checks["headline_exact"]=result["all_registers"]["observed_pairs"]==31 and close(result["all_registers"]["expected_pairs"],23.933061383061382)and result["transfer"]["observed_pairs"]==11 and result["lofo_min_pair_excess"]>0
 body=dict(result);claim=body.pop("result_content_sha256");checks["result_hash"]=csha(body)==claim;checks["status"]=result["status"]=="Q2_B3_RECORD_FRAME_WEAK_TRANSFERABLE_LEAD";checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents")for name,digest in result[fam].items())and all(sha(ROOT/name)==digest for name,digest in result["implementation"].items());checks["f84_sealed"]=not any(result["f84r"].values())
 report=(ROOT/"GDT046_Q2_B3_RECORD_FRAME_REPORT.md").read_text();checks["claim_ceiling"]="reusable weak"in report and"not a confirmed paired syntax"in report and"Q2 is not called START"in report
 ledger=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT046_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT046_Q2_B3_RECORD_FRAME_VALIDATION_V1","status":"PASS_INDEPENDENT_EXACT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent source-native endpoint join and folio/paragraph/length-stratified frame reconstruction."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
