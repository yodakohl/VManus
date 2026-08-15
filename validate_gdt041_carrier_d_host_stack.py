#!/usr/bin/env python3
"""Independent reconstruction for GDT041 carrier+D host stacking."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";OCC=ROOT/"gdt041_carrier_d_occurrences.tsv";ATLAS=ROOT/"gdt041_base_host_atlas.tsv";TESTS=ROOT/"gdt041_register_tests.tsv";RESULT=ROOT/"gdt041_result.json";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt041_validation.json";REGISTERS=("HB","SB","HA","OB")
def read(path):
 with path.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def reg(r):
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 return"OB"
def inventory(rows):
 out=[]
 for r in rows:
  assert not r["locus"].startswith("f84r");C=r["stripped_prefix"]in{"ch","che","sh"}
  if C and r["residual_host"].startswith("d")and len(r["residual_host"])>1:D=1;base=r["residual_host"][1:]
  elif not C and r["stripped_prefix"]=="d":D=1;base=r["residual_host"]
  else:D=0;base=r["residual_host"]
  if base=="y":continue
  out.append({**r,"register":reg(r),"base_host":base,"outer_carrier":int(C),"inner_d":D,"double":int(C and D)})
 return out
def hyper(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 o=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():o[i+j]+=p*q
 return dict(o)
def exact(rows,regs,dropf=None,droph=None,pm=True):
 z=[r for r in rows if r["register"]in regs and r["physical_folio"]!=dropf and r["base_host"]!=droph];by=defaultdict(list)
 for r in z:by[r["physical_folio"],r["base_host"]].append(r)
 dist={0:1.};obs=0;exp=0.;strata=0
 for a in by.values():
  n=len(a);C=sum(r["outer_carrier"]for r in a);D=sum(r["inner_d"]for r in a)
  if not C or not D:continue
  obs+=sum(r["double"]for r in a);exp+=C*D/n;strata+=1
  if pm:dist=conv(dist,hyper(n,C,D))
 return{"registers":"+".join(regs),"occurrences":len(z),"physical_folios":len({r["physical_folio"]for r in z}),"double_occurrences":sum(r["double"]for r in z),"eligible_double_observed":obs,"eligible_double_expected":exp,"eligible_excess":obs-exp,"eligible_strata":strata,"one_sided_enrichment_p":sum(p for x,p in dist.items()if x>=obs)if pm else None,"one_sided_depletion_p":sum(p for x,p in dist.items()if x<=obs)if pm else None,"null_min":min(dist)if pm else None,"null_max":max(dist)if pm else None}
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 checks={};rows=inventory(read(SOURCE));checks["inventory_scope"]=len(rows)==14822 and not any(r["locus"].startswith("f84r")for r in rows)
 expected=[exact(rows,(r,))for r in REGISTERS]+[exact(rows,("HB","SB"))];combined=expected[-1];pool=[r for r in rows if r["register"]in{"HB","SB"}]
 combined["lofo_min_excess"]=min(exact(rows,("HB","SB"),dropf=f,pm=False)["eligible_excess"]for f in{r["physical_folio"]for r in pool});combined["lohost_min_excess"]=min(exact(rows,("HB","SB"),droph=h,pm=False)["eligible_excess"]for h in{r["base_host"]for r in pool})
 actual=read(TESTS);ok=len(actual)==5
 for stored,want in zip(actual,expected):
  for k in("registers","occurrences","physical_folios","double_occurrences","eligible_double_observed","eligible_strata","null_min","null_max"):ok&=stored[k]==str(want[k])
  for k in("eligible_double_expected","eligible_excess","one_sided_enrichment_p","one_sided_depletion_p"):ok&=close(stored[k],want[k])
  if want["registers"]=="HB+SB":ok&=close(stored["lofo_min_excess"],want["lofo_min_excess"])and close(stored["lohost_min_excess"],want["lohost_min_excess"])
  else:ok&=stored["lofo_min_excess"]=="NA"and stored["lohost_min_excess"]=="NA"
 checks["all_register_exact_tests"]=ok
 atlas=[]
 for host in sorted({r["base_host"]for r in rows}):
  item={"base_host":host};total=0
  for register in REGISTERS:
   z=[r for r in rows if r["base_host"]==host and r["register"]==register];cells=Counter((r["outer_carrier"],r["inner_d"])for r in z);d=[r for r in z if r["double"]]
   for C,D in((0,0),(0,1),(1,0),(1,1)):item[f'{register.lower()}_c{C}d{D}']=str(cells[C,D])
   item[f'{register.lower()}_double_folios']=str(len({r["physical_folio"]for r in d}));total+=len(d)
  item["all_double_occurrences"]=str(total)
  if total:atlas.append(item)
 atlas.sort(key=lambda r:(-(int(r["hb_c1d1"])+int(r["sb_c1d1"])),-int(r["all_double_occurrences"]),r["base_host"]));checks["base_host_atlas_exact"]=read(ATLAS)==atlas
 doubles=[]
 for r in rows:
  if r["double"]:doubles.append({k:str(r[k])for k in("locus","page","physical_folio","register","hand","group_index","group_count","token","stripped_prefix","residual_host","base_host","record_state")})
 doubles.sort(key=lambda r:(REGISTERS.index(r["register"]),r["physical_folio"],r["locus"],int(r["group_index"])));checks["double_occurrences_exact"]=read(OCC)==doubles and len(doubles)==132
 hb=Counter(r["base_host"]for r in rows if r["register"]=="HB"and r["double"]);sb=Counter(r["base_host"]for r in rows if r["register"]=="SB"and r["double"]);shared=sorted(set(hb)&set(sb));checks["shared_hosts_exact"]=shared==["aiin","ain","al","aly","am","ar","o","or"]
 checks["decision_arithmetic"]=combined["one_sided_enrichment_p"]<.001 and combined["lofo_min_excess"]>0 and combined["lohost_min_excess"]>0 and expected[0]["one_sided_enrichment_p"]>.4 and expected[1]["one_sided_enrichment_p"]<.001 and expected[2]["eligible_double_observed"]==1
 result=json.loads(RESULT.read_text());body=dict(result);claimed=body.pop("result_content_sha256");checks["result_content_hash"]=csha(body)==claimed;checks["result_status"]=result["status"]=="CARRIER_D_STACK_IS_B_S_SHARED_S_ENRICHED_NOT_AIIN_SPECIFIC"
 checks["all_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents")for name,digest in result[fam].items())and all(sha(ROOT/name)==digest for name,digest in result["implementation"].items());checks["f84_sealed"]=not any(result["f84r"].values())
 report=(ROOT/"GDT041_CARRIER_D_HOST_STACK_REPORT.md").read_text();checks["claim_precision"]="shared B/S construction with S enrichment"in report and"not a universal Currier-B rule"in report and"No function"in report
 ledger=[r for r in read(LEDGER)if r["checkpoint_id"]=="GDT041_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT041_CARRIER_D_HOST_STACK_VALIDATION_V1","status":"PASS_INDEPENDENT_EXACT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent decomposition, exact base-host by physical-folio null, deletion diagnostics, atlas, hashes, claims, and ledger."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
