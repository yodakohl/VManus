#!/usr/bin/env python3
"""Independent reconstruction of the GDT019 held-folio model grid."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt019_result.json";VAL=ROOT/"gdt019_validation.json";A=.5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def core(h):
 for x in("ar","al","ol","ed","kal"):
  if x in h:return x.upper()
 return"OTHER"
def close(a,b):return abs(float(a)-float(b))<8e-10
def main():
 checks=[];result=json.loads(RES.read_text());copy=dict(result);digest=copy.pop("result_content_sha256");checks+=[("schema",result["schema"]=="GDT019_DY_PAYLOAD_DECOUPLING_RESULT_V1"),("content",digest==csha(copy))]
 for part in("inputs","implementation","outputs"):
  for n,d in result[part].items():checks.append((part+":"+n,sha(ROOT/n)==d))
 inv=read("gdt016_group_state_inventory.tsv");checks+=[("input",len(inv)==15592),("f84_hard_guard",not any(r["locus"].startswith("f84r")for r in inv))];by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 events=[]
 for line in by.values():
  line.sort(key=lambda r:int(r["group_index"]))
  for i in range(1,len(line)):
   p,r=line[i-1],line[i]
   if p["record_state"]!="DY_RESOLUTION":continue
   pos=min(3,int(((int(r["group_index"])-1)/(int(r["group_count"])-1))*4));h=p["residual_host"];c=core(h);events.append({"folio":r["physical_folio"],"position":pos,"next":r["record_state"],"Q_FLAG":int(p["stripped_prefix"]=="q"),"PREFIX_CLASS":p["stripped_prefix"],"HAS_CANDIDATE_CORE":int(c!="OTHER"),"CORE_CLASS":c,"LONG_HOST":int(len(h)>=4),"HOST_LENGTH_BIN":min(5,len(h)),"FAMILY_INITIAL":p["family_surface"][0],"EXACT_FAMILY":p["family_surface"],"EXACT_HOST":h})
 features=("POSITION_ONLY","Q_FLAG","PREFIX_CLASS","HAS_CANDIDATE_CORE","CORE_CLASS","LONG_HOST","HOST_LENGTH_BIN","FAMILY_INITIAL","EXACT_FAMILY","EXACT_HOST");targets={"NEXT_STATE":lambda e:e["next"],"NEXT_Q":lambda e:int(e["next"]=="Q_OUTER_STATE"),"NEXT_OT_LOCAL":lambda e:int(e["next"].startswith("OT_")),"NEXT_DY":lambda e:int(e["next"]=="DY_RESOLUTION"),"NEXT_CARRIER":lambda e:int(e["next"]=="CARRIER_STATE")};folios=sorted({e["folio"]for e in events});stored={(r["target"],r["feature"]):r for r in read("gdt019_payload_dependency_models.tsv")};reconstructed={}
 for tn,target in targets.items():
  K=len({target(e)for e in events});scores={}
  for feature in features:
   total=0.
   for held in folios:
    counts=defaultdict(Counter);totals=Counter()
    for e in events:
     if e["folio"]==held:continue
     ctx=(e["position"],)if feature=="POSITION_ONLY"else(e["position"],e[feature]);counts[ctx][target(e)]+=1;totals[ctx]+=1
    for e in events:
     if e["folio"]!=held:continue
     ctx=(e["position"],)if feature=="POSITION_ONLY"else(e["position"],e[feature]);total-=math.log2((counts[ctx][target(e)]+A)/(totals[ctx]+A*K))
   scores[feature]=total
  base=scores["POSITION_ONLY"]
  for feature in features:
   levels=1 if feature=="POSITION_ONLY"else len({e[feature]for e in events});extra=0 if feature=="POSITION_ONLY"else 4*(levels-1)*(K-1);penalty=extra/2*math.log2(len(events));raw=base-scores[feature];row=stored[(tn,feature)];checks.append(("model:"+tn+":"+feature,close(row["held_bits"],scores[feature])and close(row["raw_gain_bits"],raw)and int(row["feature_levels"])==levels and int(row["bic_extra_parameters"])==extra and close(row["bic_penalty_bits"],penalty)and close(row["bic_net_gain_bits"],raw-penalty)))
   reconstructed[(tn,feature)]=raw-penalty
 checks+=[("event_count",len(events)==result["events"]==2344),("folios",len(folios)==result["physical_folios"]==84),("grid",len(stored)==50),("no_bic_positive",not any(v>0 for(k,v)in reconstructed.items()if k[1]!="POSITION_ONLY")and result["any_bic_positive"]is False),("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT019_CKPT001")==1),("f84_flags",result["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False})]
 report=(ROOT/"GDT019_DY_PAYLOAD_DECOUPLING_REPORT.md").read_text().lower();checks.append(("claims",all(x in report for x in("does not","partly separated","no morpheme","f84r was absent"))))
 failures=[n for n,ok in checks if not ok];v={"schema":"GDT019_DY_PAYLOAD_DECOUPLING_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction from the frozen f84r-free inventory of all 50 held-folio model cells, penalties, status, hashes, ledger, and claims."};VAL.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps(v,sort_keys=True));
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
