#!/usr/bin/env python3
"""Integrity and independent inventory/headline validation for GDT060."""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RESULT=ROOT/"gdt060_result.json";INVENTORY=ROOT/"gdt060_dy_transition_inventory.tsv";SCORES=ROOT/"gdt060_dy_transition_scores.tsv";PERM=ROOT/"gdt060_dy_transition_permutation.tsv";VARIANTS=ROOT/"gdt060_variant_log.tsv";SOURCE=ROOT/"gdt016_group_state_inventory.tsv";FRAMES=ROOT/"gdt046_line_frames.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt060_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-8):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());inv=read(INVENTORY);scores=read(SCORES);perms=read(PERM);variants=read(VARIANTS);checks={}
 checks["inventory_counts"]=len(inv)==r["boundaries"]==7409 and sum(int(x["dy"])for x in inv)==r["dy_boundaries"]==1298 and len({x["locus"]for x in inv})==1149 and r["complete_lines"]==1164 and len({x["physical_folio"]for x in inv})==r["physical_folios"]==92
 src=defaultdict(list)
 for x in read(SOURCE):src[x["locus"]].append(x)
 frame_loci={x["locus"]for x in read(FRAMES)};mismatch=0;expected=0
 for locus in frame_loci:
  z=sorted(src[locus],key=lambda x:int(x["group_index"]));expected+=len(z)-1
  got=sorted((x for x in inv if x["locus"]==locus),key=lambda x:int(x["boundary_index"]))
  if len(got)!=len(z)-1:mismatch+=1;continue
  for i,x in enumerate(got):
   if x["left_token"]!=z[i]["token"]or x["right_token"]!=z[i+1]["token"]or int(x["dy"])!=int(z[i]["dy_closure"]):mismatch+=1;break
 checks["adjacent_source_reconstruction"]=expected==7409 and mismatch==0
 checks["score_grid"]=len(scores)==72 and {(x["evaluation"],x["pre_context"],x["representation"],x["scope"])for x in scores}=={(e,c,p,s)for e in("LEAVE_FOLIO_OUT","LEAVE_REGISTER_OUT")for c in("SUFFIX_1","SUFFIX_2")for p in("RAW_SURFACE","RESIDUAL_ROOT","PAGE_HOST")for s in("ALL","HERBAL_A","HERBAL_B","OTHER_A","OTHER_B","STARS_RECIPE_B")}
 checks["permutation_grid"]=len(perms)==9 and all(int(x["permutation_worlds"])==10000 for x in perms)
 by={(x["evaluation"],x["pre_context"],x["representation"],x["scope"]):x for x in scores};p=by["LEAVE_FOLIO_OUT","SUFFIX_2","PAGE_HOST","ALL"];s1=by["LEAVE_FOLIO_OUT","SUFFIX_1","PAGE_HOST","ALL"];cross=by["LEAVE_REGISTER_OUT","SUFFIX_2","PAGE_HOST","ALL"]
 checks["boundary_channel"]=close(p["boundary_gain_vs_base"],668.3117276835401)and float(p["boundary_gain_vs_base"])>0 and all(float(by["LEAVE_FOLIO_OUT","SUFFIX_2","PAGE_HOST",s]["boundary_gain_vs_base"])>0 for s in("HERBAL_A","HERBAL_B","OTHER_A","OTHER_B","STARS_RECIPE_B"))
 checks["suffix_interaction_negative"]=close(p["joint_gain_vs_pre"],-863.2312367250852)and close(s1["joint_gain_vs_pre"],-854.7467154418264)and float(cross["joint_gain_vs_pre"])<0
 checks["cross_register_disclosure"]=close(cross["boundary_gain_vs_base"],554.721984039672)and float(by["LEAVE_REGISTER_OUT","SUFFIX_2","PAGE_HOST","HERBAL_B"]["boundary_gain_vs_base"])<0
 pm={(x["representation"],x["statistic"]):x for x in perms}["PAGE_HOST","interaction_logodds"]
 checks["matched_interaction"]=int(pm["eligible_dy"])==1197 and close(pm["effect_per_dy"],-.129928451562)and float(pm["maxT_9_p"])<.01
 checks["f84_excluded"]=not any(x["locus"].startswith("f84r")for x in inv)and not any(r["f84r"].values())
 checks["variant_log"]={x["variant_id"]:x["status"]for x in variants}=={"V00":"PRIMARY","V01":"RUN_SENSITIVITY","V02":"RUN_BASELINE","V03":"RUN_BASELINE","V04":"RUN_SENSITIVITY","V05":"RUN_CONTROL","V06":"NOT_RUN"}
 body=dict(r);claim=body.pop("result_content_sha256");checks["result_content_hash"]=csha(body)==claim
 checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 checks["status_and_ceiling"]=r["status"]=="DY_MARKS_POST_BOUNDARY_DISTRIBUTION_TESTED_PREHOST_SUFFIX_INTERACTION_NEGATIVE"and"provisional reset/checkpoint"in r["generative_update"]and"no semantic field"in r["claim_ceiling"]
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT060_CKPT001"];checks["ledger_exact"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT060_DY_PAGE_HOST_TRANSITION_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_INVENTORY_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently reconstructs complete-line adjacent source pairs, counts, grids, published gains, matched statistic, f84 exclusion, hashes, variants, ledger, and ceiling. It does not independently rerun the hierarchical character scorer or permutation engine."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
