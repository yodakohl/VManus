#!/usr/bin/env python3
"""Independent nonimporting validator for GDT032."""
from __future__ import annotations
import csv,hashlib,itertools,json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt032_result.json";VAL=ROOT/"gdt032_validation.json"
PRIMARY=("DY_PER_100_GROUPS","INTERNAL_BOUNDARIES_PER_100_POSSIBLE","EXACT_LENGTH_STANDARDIZED_FIELDS_PER_LINE")
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b):return abs(float(a)-float(b))<7e-10
def same(left,right):
 for key,value in right.items():
  if str(left[key])==value:continue
  try:
   if close(left[key],value):continue
  except (TypeError,ValueError):pass
  return False
 return True
def signflip(v):
 obs=sum(v)/len(v);world=[sum(s*x for s,x in zip(z,v))/len(v)for z in itertools.product((-1,1),repeat=len(v))]
 return obs,sum(x>=obs-1e-15 for x in world)/len(world)
def line_metric(rows):
 st=[r["record_state"]for r in sorted(rows,key=lambda r:int(r["group_index"]))];dy=[i for i,x in enumerate(st)if x=="DY_RESOLUTION"]
 return len(st),len(dy),sum(i<len(st)-1 for i in dy),len(dy)+int(not dy or st[-1]!="DY_RESOLUTION")
def main():
 checks=[];result=json.loads(RES.read_text());body=dict(result);digest=body.pop("result_content_sha256");checks +=[("schema",result["schema"]=="GDT032_HERBAL_LENGTH_NORMALIZED_SEGMENTATION_RESULT_V1"),("content",digest==csha(body)),("status",result["status"]=="HERBAL_B_SEGMENTATION_DENSITY_SURVIVES_LENGTH_NORMALIZATION")]
 for section in ("inputs","implementation","outputs"):
  for name,d in result[section].items():checks.append((f"hash:{section}:{name}",sha(ROOT/name)==d))
 inv=read("gdt016_group_state_inventory.tsv");checks +=[("inventory",len(inv)==15592),("f84r",not any(r["locus"].startswith("f84r")for r in inv))];lines=defaultdict(lambda:defaultdict(list))
 for r in inv:
  if r["section"]=="H":lines[r["page"]][r["locus"]].append(r)
 prior={r["page"]:r for r in read("gdt031_herbal_page_architecture.tsv")};pairs=read("gdt031_matched_herbal_pages.tsv");checks.append(("fixed_pairs",len(pairs)==8 and len({r["currier_a_folio"]for r in pairs})==len({r["currier_b_folio"]for r in pairs})==8))
 lm={p:{l:line_metric(rs)for l,rs in x.items()}for p,x in lines.items()};expected=[];pm={}
 for p in sorted(lm):
  v=list(lm[p].values());groups=sum(x[0]for x in v);n=len(v);dy=sum(x[1]for x in v);internal=sum(x[2]for x in v);possible=groups-n
  expected.append({"page":p,"physical_folio":prior[p]["physical_folio"],"currier":prior[p]["currier"],"hand":prior[p]["hand"],"illustration_profile":prior[p]["illustration_profile"],"groups":str(groups),"lines":str(n),"mean_groups_per_line":f"{groups/n:.12f}","dy_checkpoints":str(dy),"dy_per_100_groups":f"{100*dy/groups:.12f}","possible_internal_group_boundaries":str(possible),"internal_field_boundaries":str(internal),"internal_boundaries_per_100_possible":f"{100*internal/possible:.12f}","claim_state":"LENGTH_NORMALIZED_FORMAL_SEGMENTATION_NOT_MEANING"});pm[p]={"DY_PER_100_GROUPS":100*dy/groups,"INTERNAL_BOUNDARIES_PER_100_POSSIBLE":100*internal/possible}
 checks.append(("page_metrics",expected==read("gdt032_herbal_length_normalized_metrics.tsv")));strata=[];pair_rows=[];le={}
 for pair in pairs:
  bins=[]
  for side in ("a","b"):
   d=defaultdict(list)
   for x in lm[pair[f"currier_{side}_page"]].values():d[x[0]].append(x[3])
   bins.append(d)
  A,B=bins;num=weight=count=0
  for g in sorted(set(A)&set(B)):
   w=min(len(A[g]),len(B[g]));am=sum(A[g])/len(A[g]);bm=sum(B[g])/len(B[g]);delta=bm-am;num+=w*delta;weight+=w;count+=1
   strata.append({"pair_id":pair["pair_id"],"illustration_profile":pair["illustration_profile"],"classified_profile":pair["classified_profile"],"groups_per_line":str(g),"a_line_count":str(len(A[g])),"b_line_count":str(len(B[g])),"matched_equivalent_weight":str(w),"a_mean_fields":f"{am:.12f}","b_mean_fields":f"{bm:.12f}","b_minus_a_fields":f"{delta:.12f}","claim_state":"EXACT_LENGTH_STRATUM_NOT_INDEPENDENT_SAMPLE"})
  effect=num/weight if weight else None
  if effect is not None:le[pair["pair_id"]]=effect
  pair_rows.append({"pair_id":pair["pair_id"],"illustration_profile":pair["illustration_profile"],"classified_profile":pair["classified_profile"],"exact_length_overlap":str(int(bool(weight))),"shared_length_strata":str(count),"matched_equivalent_weight":str(weight),"b_minus_a_standardized_fields":f"{effect:.12f}"if effect is not None else"NOT_AVAILABLE","claim_state":"PAGE_PAIR_IS_INFERENTIAL_UNIT"})
 checks +=[("strata",strata==read("gdt032_matched_group_length_strata.tsv")),("pair_results",pair_rows==read("gdt032_exact_length_pair_results.tsv"))];stored={r["feature"]:r for r in read("gdt032_length_normalized_tests.tsv")}
 for feature in PRIMARY:
  eligible=[p for p in pairs if feature!="EXACT_LENGTH_STANDARDIZED_FIELDS_PER_LINE"or p["pair_id"]in le];d=[le[p["pair_id"]]if feature=="EXACT_LENGTH_STANDARDIZED_FIELDS_PER_LINE"else pm[p["currier_b_page"]][feature]-pm[p["currier_a_page"]][feature]for p in eligible];e,pv=signflip(d);c=[x for x,p in zip(d,eligible)if p["classified_profile"]=="1"];ce,cp=signflip(c);r=stored[feature]
  checks.append((f"test:{feature}",int(r["eligible_page_pairs"])==len(eligible)and close(r["b_minus_a_mean"],e)and int(r["positive_pairs"])==sum(x>0 for x in d)and int(r["zero_pairs"])==sum(x==0 for x in d)and close(r["one_sided_exact_p"],pv)and close(r["three_test_adjusted_p"],min(1,3*pv))and int(r["classified_only_pairs"])==len(c)and close(r["classified_only_b_minus_a"],ce)and int(r["classified_only_positive_pairs"])==sum(x>0 for x in c)and int(r["classified_only_zero_pairs"])==sum(x==0 for x in c)and close(r["classified_only_exact_p"],cp)and close(r["classified_only_three_test_adjusted_p"],min(1,3*cp))))
 aggregate={}
 for currier in ("A","B"):
  rows=[r for r in expected if r["currier"]==currier];groups=sum(int(r["groups"])for r in rows);line_count=sum(int(r["lines"])for r in rows);dy=sum(int(r["dy_checkpoints"])for r in rows);possible=sum(int(r["possible_internal_group_boundaries"])for r in rows);internal=sum(int(r["internal_field_boundaries"])for r in rows);aggregate[currier]={"groups":groups,"lines":line_count,"mean_groups_per_line":groups/line_count,"dy_per_100_groups":100*dy/groups,"internal_boundaries_per_100_possible":100*internal/possible}
 checks +=[("counts",result["herbal_pages"]=={"A":95,"B":32}and result["all_herbal_aggregate"]==aggregate and result["fixed_gdt031_pairs"]==8 and result["exact_length_eligible_pairs"]==6 and result["exact_length_strata"]==15 and result["matched_equivalent_line_weight"]==16 and result["no_exact_length_overlap_pairs"]==["HP05","HP07"]),("snapshots",all(same(result["primary_tests"][k],stored[k])for k in PRIMARY)),("flags",result["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False})]
 report=" ".join((ROOT/"GDT032_HERBAL_LENGTH_NORMALIZED_SEGMENTATION_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks +=[("claims",all(x in report for x in("longer b lines do not explain","currier/hand-conditioned","f84r was not opened","no role"))),("ledger",ledger.count("GDT032_CKPT001")==1)]
 failures=[name for name,ok in checks if not ok];validation={"schema":"GDT032_HERBAL_LENGTH_NORMALIZED_SEGMENTATION_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of 127 Herbal page metrics, fixed GDT031 pairs, exact group-length strata, three paired tests, hashes, f84r exclusion, ledger, and claim ceiling."};VAL.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True))
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
