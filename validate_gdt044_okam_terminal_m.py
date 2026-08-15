#!/usr/bin/env python3
"""Independent exact reconstruction for GDT044."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";OCC=ROOT/"gdt044_okam_complete_occurrences.tsv";TESTS=ROOT/"gdt044_okam_tests.tsv";RESULT=ROOT/"gdt044_result.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt044_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def section(r):
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 return"OUT"
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def score(lines,base,outcome):
 pm={0:1.};obs=nfam=0
 for line in lines:
  pool=[r for r in line if base(r)];draw=sum(r["residual_host"]=="okam"for r in pool)
  if not draw:continue
  hits=sum(r[outcome]for r in pool);obs+=sum(r["residual_host"]=="okam"and r[outcome]for r in pool);nfam+=draw;pm=conv(pm,hyper(len(pool),hits,draw))
 exp=sum(x*p for x,p in pm.items());return obs,nfam,exp,(obs-exp)/nfam,sum(p for x,p in pm.items()if x>=obs)
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 by=defaultdict(list);checks={"f84_source_excluded":True}
 for r in read(SOURCE):
  checks["f84_source_excluded"]&=not r["locus"].startswith("f84r")
  if section(r)in{"HB","SB"}:by[r["locus"]].append(r)
 lines=[]
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)!=n or{int(r["group_index"])for r in line}!=set(range(1,n+1)):continue
  last=max([-1]+[i for i,r in enumerate(line)if r["record_state"]=="DY_RESOLUTION"]);lines.append([{**r,"target_section":section(r),"physical_line_end":int(i==n-1),"final_open_field":int(i>last)}for i,r in enumerate(line)])
 allrows=[r for line in lines for r in line];occ=[]
 for r in allrows:
  if r["residual_host"]=="okam":occ.append({k:str(r[k])for k in("locus","page","physical_folio","target_section","hand","group_index","group_count","token","stripped_prefix","residual_host","record_state","physical_line_end","final_open_field")})
 occ.sort(key=lambda r:(r["physical_folio"],r["locus"],int(r["group_index"])));checks["occurrences_exact"]=occ==read(OCC)and len(occ)==6
 bases={"ALL_GROUPS":lambda r:True,"WITHIN_TERMINAL_M":lambda r:r["residual_host"].endswith("m"),"WITHIN_TERMINAL_AM":lambda r:r["residual_host"].endswith("am"),"WITHIN_TERMINAL_OKM":lambda r:r["residual_host"].startswith("ok")and r["residual_host"].endswith("m")};actual=read(TESTS);ok=True
 for name,base in bases.items():
  for outcome in("physical_line_end","final_open_field"):
   obs,n,exp,effect,p=score(lines,base,outcome);a=next(r for r in actual if r["contrast"]==name and r["outcome"]==outcome);ok&=a["observed"]==str(obs)and a["family_n"]==str(n)and close(a["null_expected_hits"],exp)and close(a["rate_effect"],effect)and close(a["local_p"],p)
 checks["all_nested_tests_exact"]=ok and len(actual)==8
 result=json.loads(RESULT.read_text());checks["headline_exact"]=close(result["raw_physical_line_end"]["local_p"],6.887052341597797e-05)and close(result["within_terminal_m_physical_line_end"]["rate_effect"],1/12)and result["within_terminal_m_physical_line_end"]["local_p"]==.5 and result["within_terminal_m_final_open_field"]["rate_effect"]==0
 body=dict(result);claim=body.pop("result_content_sha256");checks["result_hash"]=csha(body)==claim;checks["status"]=result["status"]=="OKAM_PLACEMENT_ATTRIBUTED_TO_TERMINAL_M_SYSTEM";checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents")for name,digest in result[fam].items())and all(sha(ROOT/name)==digest for name,digest in result["implementation"].items());checks["f84_sealed"]=not any(result["f84r"].values())
 report=(ROOT/"GDT044_OKAM_TERMINAL_M_REPORT.md").read_text();checks["claim_ceiling"]="does not survive the correct parent control"in report and"No function"in report
 ledger=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT044_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT044_OKAM_TERMINAL_M_VALIDATION_V1","status":"PASS_INDEPENDENT_EXACT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent complete-line inventory and exact nested placement reconstruction."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
