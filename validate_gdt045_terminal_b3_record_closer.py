#!/usr/bin/env python3
"""Independent exact reconstruction for GDT045."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";CONS=ROOT/"experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv";OCC=ROOT/"gdt045_b3_occurrences.tsv";ATLAS=ROOT/"gdt045_final_member_atlas.tsv";TRANSFER=ROOT/"gdt045_register_transfer.tsv";RESULT=ROOT/"gdt045_result.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt045_validation.json";REGS=("HA","HB","SB","OB","OA")
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
def score(lines,member,regs):
 pm={0:1.};obs=N=0;exp=0.;nlines=0
 for line in lines:
  if line[0]["register"]not in regs:continue
  nlines+=1;draw=sum(r["final_member"]==member for r in line)
  if not draw:continue
  actual=sum(r["final_member"]==member and r["physical_line_end"]for r in line);obs+=actual;N+=draw;exp+=draw/len(line);pm=conv(pm,hyper(len(line),1,draw))
 return{"observed":obs,"member_n":N,"observed_rate":obs/N,"expected_hits":exp,"expected_rate":exp/N,"rate_effect":(obs-exp)/N,"local_p":sum(p for x,p in pm.items()if x>=obs),"null_min":min(pm),"null_max":max(pm),"line_count":nlines,"endpoint_recall":obs/nlines}
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 checks={};inv=read(SOURCE);checks["f84_source_excluded"]=not any(r["locus"].startswith("f84r")for r in inv);by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 complete=[];keys=set()
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)==n and{int(r["group_index"])for r in line}==set(range(1,n+1)):complete.append(line);keys|={(locus,r["group_index"])for r in line}
 cons={}
 with CONS.open(encoding="utf-8",newline="")as h:
  header=h.readline();fields=next(csv.reader([header],delimiter="\t"))
  for raw in h:
   if raw.startswith("f84r."):continue
   first=raw.split("\t",1)[0];locus,idx=first.rsplit("|C",1);key=(locus,str(int(idx)))
   if key in keys:cons[key]=dict(zip(fields,next(csv.reader([raw],delimiter="\t"))))
 lines=[]
 for line in complete:
  z=[]
  for i,r in enumerate(line):
   c=cons[(r["locus"],r["group_index"])];ends=tuple(c[x].split()[-1]for x in("zl_sta_codes","it_sta_codes","rf_sta_codes"));z.append({**r,"register":reg(r),"physical_line_end":int(i==len(line)-1),"final_member":ends[0]if len(set(ends))==1 else"TRANSCRIPTION_UNSTABLE"})
  lines.append(z)
 checks["inventory_exact"]=len(lines)==1193 and sum(map(len,lines))==8774 and len(cons)==8774
 b3=[r for line in lines for r in line if r["final_member"]=="B3"];m=[r for line in lines for r in line if r["residual_host"].endswith("m")];checks["b3_m_equivalence"]={(r["locus"],r["group_index"])for r in b3}=={(r["locus"],r["group_index"])for r in m}and len(b3)==213 and not any(int(r["dy_closure"])for r in b3)
 occ=[{k:str(r[k])for k in("locus","page","physical_folio","register","hand","group_index","group_count","token","residual_host","final_member","physical_line_end") }for r in b3];occ.sort(key=lambda r:(REGS.index(r["register"]),r["physical_folio"],r["locus"],int(r["group_index"])));checks["occurrences_exact"]=occ==read(OCC)
 specs=[("DISCOVERY_HB_SB",("HB","SB")),("TRANSFER_HA_OB_OA",("HA","OB","OA"))]+[(x,(x,))for x in REGS]+[("ALL_REGISTERS",REGS)];actual=read(TRANSFER);ok=True
 for name,regs in specs:
  e=score(lines,"B3",regs);a=next(x for x in actual if x["comparison"]==name)
  for k in("observed","member_n","null_min","null_max","line_count"):ok&=a[k]==str(e[k])
  for k in("observed_rate","expected_hits","expected_rate","rate_effect","local_p","endpoint_recall"):ok&=close(a[k],e[k])
 checks["transfer_scores_exact"]=ok and len(actual)==8
 mc=Counter(r["final_member"]for line in lines for r in line);aa=read(ATLAS);ok=len(aa)==12
 for a in aa:
  e=score(lines,a["final_member"],REGS);ok&=int(a["support"])==mc[a["final_member"]]and a["observed"]==str(e["observed"])and close(a["rate_effect"],e["rate_effect"])and close(a["local_p"],e["local_p"])
 checks["member_atlas_exact"]=ok and aa[0]["final_member"]=="B3"and close(aa[0]["bonferroni_p"],float(aa[0]["local_p"])*12)
 result=json.loads(RESULT.read_text());checks["headline_exact"]=result["all_registers"]["observed"]==148 and result["transfer"]["observed"]==67 and result["transfer"]["member_n"]==104 and all(result["per_register"][x]["lofo_min_effect"]>0 for x in REGS)
 body=dict(result);claim=body.pop("result_content_sha256");checks["result_hash"]=csha(body)==claim;checks["status"]=result["status"]=="TERMINAL_B3_IS_TRANSFERABLE_RECORD_CLOSING_MARKER_CLASS";checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents")for name,digest in result[fam].items())and all(sha(ROOT/name)==digest for name,digest in result["implementation"].items());checks["f84_sealed"]=not any(result["f84r"].values())
 report=(ROOT/"GDT045_TERMINAL_B3_RECORD_CLOSER_REPORT.md").read_text();checks["claim_ceiling"]="record-closing marker"in report and"does not assert punctuation"in report and"No word"in report
 ledger=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT045_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT045_TERMINAL_B3_RECORD_CLOSER_VALIDATION_V1","status":"PASS_INDEPENDENT_EXACT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent source-native member join, complete-line endpoint tests, held-register transfer, and member max-search reconstruction."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
