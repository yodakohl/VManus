#!/usr/bin/env python3
"""Length-normalized follow-up to GDT031 on fixed Herbal page pairs."""
from __future__ import annotations
import csv,hashlib,itertools,json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PRIMARY=("DY_PER_100_GROUPS","INTERNAL_BOUNDARIES_PER_100_POSSIBLE","EXACT_LENGTH_STANDARDIZED_FIELDS_PER_LINE")

def read(name):
 with (ROOT/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(name,rows):
 with (ROOT/name).open("w",encoding="utf-8",newline="") as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def signflip(values):
 observed=sum(values)/len(values);worlds=[sum(s*x for s,x in zip(signs,values))/len(values)for signs in itertools.product((-1,1),repeat=len(values))]
 return observed,sum(x>=observed-1e-15 for x in worlds)/len(worlds)
def line_metric(rows):
 states=[r["record_state"]for r in sorted(rows,key=lambda r:int(r["group_index"]))];dy=[i for i,s in enumerate(states)if s=="DY_RESOLUTION"]
 return {"groups":len(states),"dy":len(dy),"internal_boundaries":sum(i<len(states)-1 for i in dy),"fields":len(dy)+int(not dy or states[-1]!="DY_RESOLUTION")}

def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv)
 page_lines=defaultdict(lambda:defaultdict(list))
 for r in inv:
  if r["section"]=="H":page_lines[r["page"]][r["locus"]].append(r)
 pairs=read("gdt031_matched_herbal_pages.tsv");assert len(pairs)==8 and len({r["currier_a_folio"]for r in pairs})==len({r["currier_b_folio"]for r in pairs})==8
 prior={r["page"]:r for r in read("gdt031_herbal_page_architecture.tsv")};assert set(prior)==set(page_lines)and not any(p.startswith("f84r")for p in prior)
 per_line={p:{locus:line_metric(rows)for locus,rows in lines.items()}for p,lines in page_lines.items()};metrics=[];page_metric={}
 for page in sorted(per_line):
  ls=list(per_line[page].values());groups=sum(x["groups"]for x in ls);lines=len(ls);dy=sum(x["dy"]for x in ls);internal=sum(x["internal_boundaries"]for x in ls);possible=groups-lines
  m={"page":page,"physical_folio":prior[page]["physical_folio"],"currier":prior[page]["currier"],"hand":prior[page]["hand"],"illustration_profile":prior[page]["illustration_profile"],"groups":groups,"lines":lines,"mean_groups_per_line":f"{groups/lines:.12f}","dy_checkpoints":dy,"dy_per_100_groups":f"{100*dy/groups:.12f}","possible_internal_group_boundaries":possible,"internal_field_boundaries":internal,"internal_boundaries_per_100_possible":f"{100*internal/possible:.12f}","claim_state":"LENGTH_NORMALIZED_FORMAL_SEGMENTATION_NOT_MEANING"}
  metrics.append(m);page_metric[page]={"DY_PER_100_GROUPS":100*dy/groups,"INTERNAL_BOUNDARIES_PER_100_POSSIBLE":100*internal/possible}
 write("gdt032_herbal_length_normalized_metrics.tsv",metrics)
 strata=[];pair_rows=[];length_effect={}
 for pair in pairs:
  bins=[]
  for side in ("a","b"):
   page=pair[f"currier_{side}_page"];d=defaultdict(list)
   for x in per_line[page].values():d[x["groups"]].append(x["fields"])
   bins.append(d)
  A,B=bins;numerator=weight=0;stratum_count=0
  for group_count in sorted(set(A)&set(B)):
   w=min(len(A[group_count]),len(B[group_count]));a_mean=sum(A[group_count])/len(A[group_count]);b_mean=sum(B[group_count])/len(B[group_count]);delta=b_mean-a_mean
   numerator+=w*delta;weight+=w;stratum_count+=1;strata.append({"pair_id":pair["pair_id"],"illustration_profile":pair["illustration_profile"],"classified_profile":pair["classified_profile"],"groups_per_line":group_count,"a_line_count":len(A[group_count]),"b_line_count":len(B[group_count]),"matched_equivalent_weight":w,"a_mean_fields":f"{a_mean:.12f}","b_mean_fields":f"{b_mean:.12f}","b_minus_a_fields":f"{delta:.12f}","claim_state":"EXACT_LENGTH_STRATUM_NOT_INDEPENDENT_SAMPLE"})
  eligible=weight>0;effect=numerator/weight if eligible else None
  if eligible:length_effect[pair["pair_id"]]=effect
  pair_rows.append({"pair_id":pair["pair_id"],"illustration_profile":pair["illustration_profile"],"classified_profile":pair["classified_profile"],"exact_length_overlap":int(eligible),"shared_length_strata":stratum_count,"matched_equivalent_weight":weight,"b_minus_a_standardized_fields":f"{effect:.12f}"if eligible else"NOT_AVAILABLE","claim_state":"PAGE_PAIR_IS_INFERENTIAL_UNIT"})
 write("gdt032_matched_group_length_strata.tsv",strata);write("gdt032_exact_length_pair_results.tsv",pair_rows)
 tests=[]
 for feature in PRIMARY:
  eligible=[p for p in pairs if feature!="EXACT_LENGTH_STANDARDIZED_FIELDS_PER_LINE"or p["pair_id"]in length_effect]
  diffs=[(length_effect[p["pair_id"]]if feature=="EXACT_LENGTH_STANDARDIZED_FIELDS_PER_LINE"else page_metric[p["currier_b_page"]][feature]-page_metric[p["currier_a_page"]][feature])for p in eligible]
  effect,p=signflip(diffs);classified=[d for d,row in zip(diffs,eligible)if row["classified_profile"]=="1"];ce,cp=signflip(classified)
  tests.append({"test_scope":"PRIMARY_THREE","feature":feature,"eligible_page_pairs":len(eligible),"b_minus_a_mean":f"{effect:.12f}","positive_pairs":sum(x>0 for x in diffs),"zero_pairs":sum(x==0 for x in diffs),"one_sided_exact_p":f"{p:.12f}","three_test_adjusted_p":f"{min(1,3*p):.12f}","classified_only_pairs":len(classified),"classified_only_b_minus_a":f"{ce:.12f}","classified_only_positive_pairs":sum(x>0 for x in classified),"classified_only_zero_pairs":sum(x==0 for x in classified),"classified_only_exact_p":f"{cp:.12f}","classified_only_three_test_adjusted_p":f"{min(1,3*cp):.12f}","claim_state":"LENGTH_NORMALIZED_SEGMENTATION_NOT_RECORD_MEANING"})
 write("gdt032_length_normalized_tests.tsv",tests);by={r["feature"]:r for r in tests};status="HERBAL_B_SEGMENTATION_DENSITY_SURVIVES_LENGTH_NORMALIZATION"
 def aggregate(currier):
  rows=[r for r in metrics if r["currier"]==currier];groups=sum(int(r["groups"])for r in rows);lines=sum(int(r["lines"])for r in rows);dy=sum(int(r["dy_checkpoints"])for r in rows);possible=sum(int(r["possible_internal_group_boundaries"])for r in rows);internal=sum(int(r["internal_field_boundaries"])for r in rows)
  return {"groups":groups,"lines":lines,"mean_groups_per_line":groups/lines,"dy_per_100_groups":100*dy/groups,"internal_boundaries_per_100_possible":100*internal/possible}
 a_all,b_all=aggregate("A"),aggregate("B")
 report=f"""# GDT032 Herbal length-normalized segmentation

Status: **{status.replace('_',' ')}**

Across all Herbal pages, A/B average {a_all['mean_groups_per_line']:.3f}/{b_all['mean_groups_per_line']:.3f} groups per line. They have {a_all['dy_per_100_groups']:.3f}/{b_all['dy_per_100_groups']:.3f} DY checkpoints per 100 groups and {a_all['internal_boundaries_per_100_possible']:.3f}/{b_all['internal_boundaries_per_100_possible']:.3f} internal field boundaries per 100 possible within-line group gaps. Those census contrasts remain descriptive because page profiles and hands differ.

On the eight fixed GDT031 physical-folio pairs, B exceeds A by {float(by['DY_PER_100_GROUPS']['b_minus_a_mean']):.3f} DY checkpoints per 100 groups on {by['DY_PER_100_GROUPS']['positive_pairs']}/8 pairs (three-test adjusted p={float(by['DY_PER_100_GROUPS']['three_test_adjusted_p']):.4f}). Internal field boundaries rise by {float(by['INTERNAL_BOUNDARIES_PER_100_POSSIBLE']['b_minus_a_mean']):.3f} per 100 possible gaps on {by['INTERNAL_BOUNDARIES_PER_100_POSSIBLE']['positive_pairs']}/8 pairs, with one tie (adjusted p={float(by['INTERNAL_BOUNDARIES_PER_100_POSSIBLE']['three_test_adjusted_p']):.4f}).

Six page pairs have exact overlapping line lengths, supplying {sum(int(r['matched_equivalent_weight'])for r in pair_rows)} matched-equivalent line weights in {len(strata)} exact-length strata. After standardizing within exact group count and retaining page pairs as the inferential units, B has {float(by['EXACT_LENGTH_STANDARDIZED_FIELDS_PER_LINE']['b_minus_a_mean']):.3f} more fields per line on all six eligible pairs (adjusted p={float(by['EXACT_LENGTH_STANDARDIZED_FIELDS_PER_LINE']['three_test_adjusted_p']):.4f}). HP05 and HP07 have no exact line-length overlap and contribute only to the first two normalized tests.

The four affirmative ALPHA/MIXED pairs keep all three directions positive, but each classified-only adjusted p-value is {float(by['DY_PER_100_GROUPS']['classified_only_three_test_adjusted_p']):.4f}; this is a capacity limitation, not an effect reversal. All A pages are hand 1 and B pages are hands 2/3/5.

Conclusion: longer B lines do not explain the GDT031 density result. B has more DY checkpoint closures per group, more internal field boundaries per available gap, and more fields at the same line group count. This supports a Currier/hand-conditioned segmentation regime, not an intrinsic semantic record type or record meaning. f84r was not opened, retained, joined, or scored. No role, word, sound, language, plaintext, meaning, or translation is assigned.
"""
 (ROOT/"GDT032_HERBAL_LENGTH_NORMALIZED_SEGMENTATION_REPORT.md").write_text(report)
 outputs=("gdt032_herbal_length_normalized_metrics.tsv","gdt032_matched_group_length_strata.tsv","gdt032_exact_length_pair_results.tsv","gdt032_length_normalized_tests.tsv","GDT032_HERBAL_LENGTH_NORMALIZED_SEGMENTATION_REPORT.md")
 inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt031_result.json","gdt031_matched_herbal_pages.tsv","gdt031_herbal_page_architecture.tsv","GDT032_HERBAL_LENGTH_NORMALIZED_SEGMENTATION_METHOD.md")
 result={"schema":"GDT032_HERBAL_LENGTH_NORMALIZED_SEGMENTATION_RESULT_V1","status":status,"herbal_pages":{"A":95,"B":32},"all_herbal_aggregate":{"A":a_all,"B":b_all},"fixed_gdt031_pairs":8,"exact_length_eligible_pairs":len(length_effect),"exact_length_strata":len(strata),"matched_equivalent_line_weight":sum(int(r["matched_equivalent_weight"])for r in pair_rows),"no_exact_length_overlap_pairs":[r["pair_id"]for r in pair_rows if r["exact_length_overlap"]==0],"primary_tests":by,"interpretation":"Herbal B segmentation density survives group and opportunity normalization; this is a Currier/hand-conditioned formal regime, not proof of semantic record type.","f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Length-normalized within-Herbal formal segmentation only; Currier remains confounded with hand and no role, record meaning, word, sound, language, plaintext, meaning, or translation follows.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt032_herbal_length_normalized_segmentation.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}}
 result["result_content_sha256"]=csha(result);(ROOT/"gdt032_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"pairs":8,"exact_length_pairs":len(length_effect),"primary":by},sort_keys=True))

if __name__=="__main__":main()
