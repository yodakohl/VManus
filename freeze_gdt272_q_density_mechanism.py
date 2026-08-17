#!/usr/bin/env python3
"""Freeze Q20 density predictors before joining GDT271 q page outcomes."""
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt127_q20_field_inventory.tsv";OUTCOME="gdt271_result.json";RATIONALE="gdt267_result.json";METHOD="GDT272_Q_DENSITY_MECHANISM_METHOD.md"
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def write(name,rows):
 with (R/name).open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def main():
 rows=read(SRC);assert rows and all(not x["page"].startswith("f84") for x in rows);zl=[x for x in rows if x["edition"]=="ZL3b"];pages=defaultdict(set)
 for x in zl:pages[x["page"]].add(int(x["star_ordinal"]))
 out=[]
 for page,values in sorted(pages.items()):
  stars=sorted(values);k=len(stars)//2;early=set(stars[:k]);late=set(stars[-k:]);counts=[]
  for keep in (early,late):
   selected=[x for x in zl if x["page"]==page and int(x["star_ordinal"]) in keep];counts.append((sum(int(x["field_group_count"]) for x in selected),len(selected),len({x["locus"] for x in selected})))
  e,l=counts;out.append({"page":page,"early_records":len(early),"late_records":len(late),"early_groups":e[0],"late_groups":l[0],"early_fields":e[1],"late_fields":l[1],"early_lines":e[2],"late_lines":l[2],"group_count_log_ratio":f"{math.log((e[0]+.5)/(l[0]+.5)):.12f}","field_count_log_ratio":f"{math.log((e[1]+.5)/(l[1]+.5)):.12f}","line_count_log_ratio":f"{math.log((e[2]+.5)/(l[2]+.5)):.12f}","outcome_access":"NOT_JOINED_AT_FREEZE"})
 assert len(out)==13;write("gdt272_frozen_density_predictors.tsv",out)
 pred={"experiment":"GDT272_Q_DENSITY_MECHANISM","freeze_status":"PREDICTORS_FROZEN_BEFORE_GDT271_PAGE_SCORE_JOIN","prediction":"compiler-matched q conditional page score increases with early-versus-late density imbalance","primary_predictor":"GROUP_COUNT_LOG_RATIO","sensitivities":["FIELD_COUNT_LOG_RATIO","LINE_COUNT_LOG_RATIO"],"primary_gate":{"pearson":"POSITIVE","sign_agreement_min":9,"positive_leave_one_page_min":11,"max_three_p_max":0.05},"null_worlds":65536,"null_seed_literal":"GDT272_Q_DENSITY_MECHANISM_NULL_V1","pages":13,"semantic_assignments":0,"f84r":{"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),OUTCOME:sha(OUTCOME),RATIONALE:sha(RATIONALE)},"documents":{METHOD:sha(METHOD)},"implementation":{Path(__file__).name:sha(Path(__file__).name)},"outputs":{"gdt272_frozen_density_predictors.tsv":sha("gdt272_frozen_density_predictors.tsv")}};pred["content_hash"]=hashlib.sha256(json.dumps(pred,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt272_frozen_prediction.json").write_text(json.dumps(pred,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":pred["freeze_status"],"pages":len(out),"predictor_hash":pred["outputs"]["gdt272_frozen_density_predictors.tsv"]},sort_keys=True))
if __name__=="__main__":main()
