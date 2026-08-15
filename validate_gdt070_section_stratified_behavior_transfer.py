#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT070."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt070_result.json";SCORES=ROOT/"gdt070_section_stratified_scores.tsv";FOLDS=ROOT/"gdt070_section_stratified_folds.tsv";VARIANTS=ROOT/"gdt070_variant_log.tsv";SOURCE=ROOT/"gdt062_right_family_inventory.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt070_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());scores=read(SCORES);folds=read(FOLDS);src=read(SOURCE);checks={}
 checks["source_panel_seal"]=len(src)==r["groups"]==15592 and r["eligible_loci"]==332 and not any(x["locus"].startswith("f84r")for x in src)and not any(r["f84r"].values())
 keys={(x["external_axis"],x["section"],x["currier"])for x in scores};checks["cell_score_shape"]=len(keys)==r["mixed_cells"]==12 and len(scores)==36 and all(sum((q["external_axis"],q["section"],q["currier"])==k for q in scores)==3 for k in keys)
 expected_pos={('STAR_OR_SKY','C'):27,('FIGURE','B'):38,('PLANT','P'):68,('WATER_OR_APPARATUS','B'):38,('REL_PROXIMITY','A'):17,('REL_EXPLICIT_ATTACHMENT','B'):12,('REL_EXPLICIT_ATTACHMENT','P'):12,('REL_EXPLICIT_ATTACHMENT','Z'):5,('REL_ENCLOSURE','A'):18,('REL_ENCLOSURE','Z'):14,('REL_ARRAY_OR_GROUP','B'):27,('REL_ARRAY_OR_GROUP','P'):6};checks["cell_outcomes"]=all(int(x["positive_loci"])==expected_pos[x["external_axis"],x["section"]]for x in scores)
 summary={}
 for rep in r["summary"]:
  q=[x for x in scores if x["representation"]==rep];summary[rep]={"cells":len(q),"positive_cells":sum(float(x["gain_bits"])>0 for x in q),"cell_mean_gain_per_prediction":sum(float(x["gain_per_prediction"])for x in q)/len(q),"total_gain_bits":sum(float(x["gain_bits"])for x in q),"cells_beating_raw":sum(float(x["gain_bits"])>float(next(z for z in scores if z["external_axis"]==x["external_axis"]and z["section"]==x["section"]and z["currier"]==x["currier"]and z["representation"]=="RAW_CHAR3")["gain_bits"])for x in q)}
 checks["summary_reconstruction"]=all(all(close(summary[k][m],r["summary"][k][m])if isinstance(summary[k][m],float)else summary[k][m]==r["summary"][k][m]for m in summary[k])for k in summary)
 fsum=defaultdict(float)
 for x in folds:fsum[x["external_axis"],x["section"],x["currier"],x["representation"]]+=float(x["gain_bits"])
 checks["fold_binding"]=all(close(float(x["gain_bits"]),fsum[x["external_axis"],x["section"],x["currier"],x["representation"]])for x in scores)
 behavior=[x for x in scores if x["representation"]=="BEHAVIOR_SELF_NEIGHBOR_NOPOS"];multi={}
 for axis in sorted({x["external_axis"]for x in behavior}):
  q=[x for x in behavior if x["external_axis"]==axis]
  if len(q)>=2:multi[axis]={"cells":len(q),"positive_cells":sum(float(x["gain_bits"])>0 for x in q),"sections":";".join(sorted(x["section"]for x in q)),"mean_gain_per_prediction":sum(float(x["gain_per_prediction"])for x in q)/len(q)}
 checks["multi_section_axes"]=set(multi)==set(r["multi_section_axes"])and all(multi[k]["cells"]==r["multi_section_axes"][k]["cells"]and multi[k]["positive_cells"]==r["multi_section_axes"][k]["positive_cells"]and close(multi[k]["mean_gain_per_prediction"],r["multi_section_axes"][k]["mean_gain_per_prediction"])for k in multi)
 top=max(behavior,key=lambda x:float(x["gain_per_prediction"]));bottom=min(behavior,key=lambda x:float(x["gain_per_prediction"]));checks["extremes"]=top["external_axis"]==r["strongest_behavior_cell"]["external_axis"]=="WATER_OR_APPARATUS"and bottom["external_axis"]==r["weakest_behavior_cell"]["external_axis"]=="REL_EXPLICIT_ATTACHMENT"and close(top["gain_per_prediction"],r["strongest_behavior_cell"]["gain_per_prediction"])and close(bottom["gain_per_prediction"],r["weakest_behavior_cell"]["gain_per_prediction"])
 checks["variants"]={x["variant_id"]:x["status"]for x in read(VARIANTS)}=={"V00":"PRIMARY","V01":"RUN_BASELINES","V02":"CAPACITY_RULE","V03":"POSTSELECTED_AUDIT","V04":"NOT_RUN"}
 checks["status_ceiling"]=r["status"]=="BEHAVIOR_PROFILE_LEAD_PARTLY_SURVIVES_SECTION_STRATIFICATION"and"selected in GDT068"in r["selection_disclosure"]and"no independent validation"in r["interpretation"]and"No semantic class"in r["claim_ceiling"]
 body=dict(r);claim=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claim;checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT070_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT070_SECTION_STRATIFIED_BEHAVIOR_TRANSFER_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks source/panel/seal, exact mixed-cell outcomes and score shape, summaries, fold sums, multi-section axes, extremes, variants, hashes, ledger and ceiling; does not rerun every nearest-neighbour prediction."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
