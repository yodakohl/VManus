#!/usr/bin/env python3
"""Independent reconstruction of GDT057's strict panel and Q2 headline."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt016_group_state_inventory.tsv"
CONS=ROOT/"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"
OCC=ROOT/"gdt057_q2_occurrences.tsv";ATLAS=ROOT/"gdt057_first_member_atlas.tsv";TRANSFER=ROOT/"gdt057_register_transfer.tsv"
RESULT=ROOT/"gdt057_result.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt057_validation.json";REGS=("HA","HB","SB","OB","OA")
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def reg(r):
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["currier"]=="B":return"OB"
 return"OA"
def hyper(n,k):return {0:(n-k)/n,1:k/n} if 0<k<n else ({0:1.} if k==0 else {1:1.})
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def score(lines,m,regs):
 pm={0:1.};obs=N=0;exp=0.;nlines=0
 for line in lines:
  if line[0]["register"]not in regs:continue
  nlines+=1;k=sum(x["first_member"]==m for x in line)
  if not k:continue
  obs+=int(line[0]["first_member"]==m);N+=k;exp+=k/len(line);pm=conv(pm,hyper(len(line),k))
 return {"observed":obs,"member_n":N,"expected_hits":exp,"rate_effect":(obs-exp)/N,"local_p":sum(p for x,p in pm.items()if x>=obs),"line_count":nlines,"opener_recall":obs/nlines}
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 checks={};inv=read(SOURCE);checks["source_f84_excluded"]=not any(r["locus"].startswith("f84r")for r in inv)
 by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 complete=[];keys=set()
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)==n and {int(r["group_index"])for r in line}==set(range(1,n+1)):
   complete.append(line);keys|={(locus,r["group_index"])for r in line}
 cons={}
 with CONS.open(encoding="utf-8",newline="")as h:
  for r in csv.DictReader(h,delimiter="\t"):
   if r["locus"].startswith("f84r"):continue
   key=(r["locus"],str(int(r["consensus_group_index"])))
   if key in keys:cons[key]=r
 lines=[]
 for line in complete:
  z=[];stable=True
  for i,r in enumerate(line):
   c=cons[(r["locus"],r["group_index"])];starts=tuple(c[x].split()[0]for x in("zl_sta_codes","it_sta_codes","rf_sta_codes"));stable&=len(set(starts))==1
   z.append({**r,"register":reg(r),"first_member":starts[0],"physical_line_start":int(i==0)})
  if stable:lines.append(z)
 checks["strict_panel_exact"]=len(lines)==1036 and sum(map(len,lines))==7492 and len(complete)==1193 and len(cons)==8774
 q2=[r for line in lines for r in line if r["first_member"]=="Q2"]
 checks["q2_occurrence_count"]=len(q2)==217 and sum(r["physical_line_start"]for r in q2)==99
 actual=read(TRANSFER);ok=len(actual)==8
 specs=[(x,(x,))for x in REGS]+[("CURRIER_B",("HB","SB","OB")),("CURRIER_A",("HA","OA")),("ALL_REGISTERS",REGS)]
 for name,regs in specs:
  e=score(lines,"Q2",regs);a=next(r for r in actual if r["comparison"]==name)
  ok&=a["observed"]==str(e["observed"])and a["member_n"]==str(e["member_n"])and close(a["expected_hits"],e["expected_hits"])and close(a["rate_effect"],e["rate_effect"])and close(a["local_p"],e["local_p"])
 checks["register_scores_exact"]=ok
 atlas=read(ATLAS);counts=Counter(r["first_member"]for line in lines for r in line);checks["atlas_support_exact"]=len(atlas)==16 and all(int(r["support"])==counts[r["first_member"]]for r in atlas)
 qrow=next(r for r in atlas if r["first_member"]=="Q2");checks["q2_rank_and_correction"]=qrow["rank_by_effect"]=="2"and close(qrow["bonferroni_p"],float(qrow["local_p"])*16)
 occ=read(OCC);checks["occurrence_keys_exact"]={(r["locus"],r["group_index"])for r in occ}=={(r["locus"],r["group_index"])for r in q2}
 result=json.loads(RESULT.read_text());checks["headline_exact"]=result["all_registers"]["observed"]==99 and result["all_registers"]["member_n"]==217 and close(result["all_registers"]["expected_hits"],29.488381063381063)and all(result["per_register"][x]["rate_effect"]>0 for x in REGS)and result["all_registers"]["lofo_min_effect"]>0
 body=dict(result);claim=body.pop("result_content_sha256");checks["result_content_hash"]=csha(body)==claim
 checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents")for name,digest in result[fam].items())and all(sha(ROOT/name)==digest for name,digest in result["implementation"].items())
 checks["status_and_ceiling"]=result["status"]=="Q2_IS_STRONG_TRANSFERABLE_PROBABILISTIC_LINE_OPENER_CLASS"and"Q2+B3"in result["relationship_to_gdt046"]and not any(result["f84r"].values())
 ledger=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT057_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT057_SOURCE_NATIVE_Q2_OPENER_VALIDATION_V1","status":"PASS_INDEPENDENT_EXACT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent strict complete-line panel, source-native first-member join, Q2 exact within-line opener scores, supported-member atlas, hashes, ledger, and claim ceiling."}
 VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
