#!/usr/bin/env python3
"""Independent validator for GDT037 shared-register inventory."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";RESULT=ROOT/"gdt037_result.json";VALIDATION=ROOT/"gdt037_validation.json"
PRIMARY=("HA","HB","SB","OB");ALL=PRIMARY+("SA","OTHER")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def st(r):
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["section"]=="S"and r["currier"]=="A":return"SA"
 if r["currier"]=="B":return"OB"
 return"OTHER"
def rate(c,n):return(c+.5)/(n+1)
def close(a,b,t=2e-8):return abs(float(a)-float(b))<=t

def build(rows):
 lines=defaultdict(list);events=defaultdict(list);den=Counter();denfolio=Counter()
 for r in rows:
  assert not r["locus"].startswith("f84r");lines[r["locus"]].append(r);s=st(r);den["GROUP",s]+=1;denfolio["GROUP",s,r["physical_folio"]]+=1
  for family,value in(("CORE",r["residual_host"]),("WRAPPER_CORE",r["stripped_prefix"]+"|"+r["residual_host"]),("RECORD_STATE",r["record_state"])):events[family,value,"GROUP"].append((s,r["physical_folio"],r["hand"]))
 for locus,line in lines.items():
  line.sort(key=lambda x:int(x["group_index"]));s=st(line[0]);fol=line[0]["physical_folio"];hand=line[0]["hand"]
  for a,b in zip(line,line[1:]):
   den["TRANSITION",s]+=1;denfolio["TRANSITION",s,fol]+=1
   events["STATE_TRANSITION",a["record_state"]+">"+b["record_state"],"TRANSITION"].append((s,fol,hand));events["WRAPPER_TRANSITION",a["stripped_prefix"]+">"+b["stripped_prefix"],"TRANSITION"].append((s,fol,hand))
  fields=[];cur=[]
  for r in line:
   cur.append(r)
   if r["record_state"]=="DY_RESOLUTION":fields.append((cur,True));cur=[]
  if cur:fields.append((cur,False))
  for field,closed in fields:
   den["FIELD",s]+=1;denfolio["FIELD",s,fol]+=1;states=[x["record_state"]for x in field];exact=">".join(states)+(""if closed else">OPEN");n=len(field);bucket=str(n)if n<=3 else"4PLUS";shape=f'{"CLOSED"if closed else"OPEN"}|LEN_{bucket}|{states[0]}>{states[-1]}'
   events["FIELD_TEMPLATE",exact,"FIELD"].append((s,fol,hand));events["FIELD_SHAPE",shape,"FIELD"].append((s,fol,hand))
   if closed:events["CLOSED_FIELD_CLOSER",field[-1]["residual_host"],"FIELD"].append((s,fol,hand))
 return events,den,denfolio

def lofo(es,den,denfolio,counts,base):
 by=Counter((s,f)for s,f,h in es);folios=sorted({f for s,f,h in es if s in("HB","SB")});vals=[];dtype=es[0][3]if len(es[0])>3 else None
 # denominator type is supplied by caller through global current_denom
 for held in folios:
  rr={s:rate(counts[s]-by[s,held],den[current_denom,s]-denfolio[current_denom,s,held])for s in PRIMARY};vals.append(min(math.log2(rr["HB"]/rr[base]),math.log2(rr["SB"]/rr[base])))
 return min(vals)

def main():
 global current_denom
 checks=[];res=json.loads(RESULT.read_text());body=dict(res);digest=body.pop("result_content_sha256")
 checks +=[("schema",res["schema"]=="GDT037_HERBAL_B_RECIPE_SHARED_REGISTER_RESULT_V1"),("content",digest==csha(body)),("status",res["status"]=="B_S_SHARED_REGISTER_CANDIDATES_ISOLATED_CURRIER_HAND_CONFOUNDED")]
 for section in("inputs","implementation","outputs","documents"):
  for name,d in res[section].items():checks.append((f"hash:{section}:{name}",sha(ROOT/name)==d))
 rows=read(SOURCE);events,den,denfolio=build(rows);atlas=read(ROOT/"gdt037_bs_register_candidates.tsv");lookup={(r["feature_family"],r["feature_value"],r["denominator"]):r for r in atlas}
 checks +=[("denominators",den["GROUP","HA"]==3911 and den["GROUP","HB"]==1323 and den["GROUP","SB"]==4855 and den["GROUP","OB"]==4519),("f84",not any(r["locus"].startswith("f84r")for r in rows)),("eligible",len(atlas)==346),("register_candidates",sum(r["classification"]=="B_S_REGISTER_CANDIDATE"for r in atlas)==24)]
 eligible=[];scores=[]
 for key,es in events.items():
  family,value,dtype=key;counts=Counter(s for s,f,h in es);folios=defaultdict(set)
  for s,f,h in es:folios[s].add(f)
  if counts["HB"]<3 or counts["SB"]<3 or len(folios["HB"])<2 or len(folios["SB"])<2:continue
  eligible.append(key);r=lookup[key];rates={s:rate(counts[s],den[dtype,s])for s in ALL};ea=min(math.log2(rates["HB"]/rates["HA"]),math.log2(rates["SB"]/rates["HA"]));eo=min(math.log2(rates["HB"]/rates["OB"]),math.log2(rates["SB"]/rates["OB"]));bal=abs(math.log2(rates["HB"]/rates["SB"]));rec=min(len(folios["HB"]),len(folios["SB"]));score=min(4,ea)+max(-3,min(3,eo))+math.log2(1+rec)-.5*bal
  current_denom=dtype;la=lofo(es,den,denfolio,counts,"HA");lo=lofo(es,den,denfolio,counts,"OB")
  hbh3=[x for x in es if x[0]=="HB"and x[2]=="3"];sbh3=[x for x in es if x[0]=="SB"and x[2]=="3"];hbn3=[x for x in es if x[0]=="HB"and x[2]!="3"]
  ok=all(int(r[f"{s.lower()}_count"])==counts[s]and int(r[f"{s.lower()}_folios"])==len(folios[s])and close(r[f"{s.lower()}_rate_per_1000"],rates[s]*1000)for s in ALL)
  ok=ok and close(r["shared_a_enrichment_log2"],ea)and close(r["shared_other_b_specificity_log2"],eo)and close(r["hb_sb_abs_log2_rate_difference"],bal)and close(r["rank_score"],score)and close(r["lofo_min_a_enrichment_log2"],la)and close(r["lofo_min_other_b_specificity_log2"],lo)
  same=bool(hbh3 and sbh3)
  if ea>=1 and eo>=.5 and la>0 and lo>0:classification="B_S_REGISTER_CANDIDATE"if same else"B_S_ENRICHED_HAND_CONFOUNDED"
  elif ea>=1 and eo<=0:classification="GENERIC_CURRIER_B_NOT_BS_SPECIFIC"
  elif ea>=1:classification="A_RARE_BS_SHARED_WEAK_SPECIFICITY"
  else:classification="SHARED_NOT_ENRICHED"
  ok=ok and int(r["hb_hand3_count"])==len(hbh3)and int(r["hb_hand3_folios"])==len({x[1]for x in hbh3})and int(r["sb_hand3_count"])==len(sbh3)and int(r["sb_hand3_folios"])==len({x[1]for x in sbh3})and int(r["hb_nonhand3_count"])==len(hbn3)and int(r["hb_nonhand3_folios"])==len({x[1]for x in hbn3})and r["classification"]==classification
  checks.append((f"feature:{family}:{value}",ok));scores.append((score,family,value,dtype))
 checks.append(("eligible_set",set(eligible)==set(lookup)))
 expected_order=[(f,v,d)for score,f,v,d in sorted(scores,key=lambda x:(-x[0],x[1],x[2]))];actual_order=[(r["feature_family"],r["feature_value"],r["denominator"])for r in atlas];checks.append(("rank_order",expected_order==actual_order and all(int(r["rank"])==i for i,r in enumerate(atlas,1))))
 cores=read(ROOT/"gdt037_core_wrapper_atlas.tsv");coremap={r["core"]:r for r in cores};checks +=[("core_rows",set(coremap)=={r["feature_value"]for r in atlas if r["feature_family"]=="CORE"}),("daiin",coremap["daiin"]["hb_count"]=="6"and coremap["daiin"]["sb_count"]=="17"and coremap["daiin"]["formal_function_hint"]=="PREDOMINANT_CARRIER_STATE"),("closure_hosts",all(coremap[x]["formal_function_hint"]=="PREDOMINANT_CLOSURE_HOST"for x in("opch","otch"))),("ckhy_counterexample",coremap["ckhy"]["classification"]=="SHARED_NOT_ENRICHED"and coremap["ckhy"]["ha_count"]=="17"and coremap["ckhy"]["ob_count"]=="52")]
 structural=read(ROOT/"gdt037_field_transition_atlas.tsv");checks.append(("structural_subset",structural==[r for r in atlas if r["feature_family"]in{"RECORD_STATE","FIELD_TEMPLATE","FIELD_SHAPE","CLOSED_FIELD_CLOSER","STATE_TRANSITION","WRAPPER_TRANSITION"}]))
 report=" ".join((ROOT/"GDT037_HERBAL_B_RECIPE_SHARED_REGISTER_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks +=[("claims",all(x in report for x in("does not re-test","other currier-b","candidate register markers, not meanings","ckhy","f84r was not opened"))),("ledger",ledger.count("GDT037_CKPT001")==1),("ceiling",all(not x for x in res["f84r"].values()))]
 fail=[n for n,o in checks if not o];val={"schema":"GDT037_HERBAL_B_RECIPE_SHARED_REGISTER_VALIDATION_V1","status":"PASS"if not fail else"FAIL","checks":len(checks),"failures":fail,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of all group/field/transition denominators, 346 eligible features, counts/rates/folio supports, hand-3 controls, leave-one-target-folio minima, rank order, 24 candidate decisions, core/closure counterexamples, hashes, ledger, and f84r exclusion."};VALIDATION.write_text(json.dumps(val,indent=2,sort_keys=True)+"\n");print(json.dumps(val,sort_keys=True))
 if fail:raise SystemExit(1)
if __name__=="__main__":main()
