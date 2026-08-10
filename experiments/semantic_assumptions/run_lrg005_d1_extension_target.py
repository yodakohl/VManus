#!/usr/bin/env python3
"""Run the frozen one-shot LRG005 manuscript target."""
from __future__ import annotations
import os
for v in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[v]="32"
import csv,hashlib,json,math,re
from collections import Counter
from pathlib import Path
import numpy as np
from lrg005_core import array_hash,assignment_coefficients,evaluate,load_geometry
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/"results";FREEZE=HERE/"LRG005_TARGET_FREEZE.json";GROUPS=R/"source_sta_family_consensus_groups.tsv";PANEL=R/"lrg005_d1_extension_capacity.tsv";QUOTAS=R/"lrg005_d1_extension_quotas.tsv";SCORE_CAP=R/"lrg005_d1_specificity_capacity.json";CAL=R/"lrg005_target_blind_calibration.json";CALVAL=R/"lrg005_target_blind_calibration_validation.json";OUT=R/"lrg005_d1_extension_target.json";REPORT=R/"lrg005_d1_extension_target_report.md";VALIDATION=R/"lrg005_d1_extension_target_validation.json";VALIDATION_REPORT=R/"lrg005_d1_extension_target_validation_report.md";FIELDS=("zl_sta_codes","it_sta_codes","rf_sta_codes")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tab(p):
 with p.open(encoding="utf8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def fol(p):
 m=re.fullmatch(r"(f\d+)(?:[rv](?:\d+)?)?",p)
 if not m:raise RuntimeError("page")
 return m.group(1)
def uid(x):return "LRG005-U"+hashlib.sha256(("LRG005-D1|"+x).encode()).hexdigest()[:20]
def seq(r):return tuple(r[x] for x in FIELDS)
def atomic(path,text):
 if path.exists():raise RuntimeError("output exists")
 temp=path.with_suffix(path.suffix+".tmp");temp.write_text(text,encoding="utf8",newline="\n");os.link(temp,path);temp.unlink()
def main():
 outputs=(OUT,REPORT,VALIDATION,VALIDATION_REPORT)
 if any(p.exists() for p in outputs):raise RuntimeError("target output exists")
 freeze=json.loads(FREEZE.read_text());expected_paths=[str(p.relative_to(ROOT)) for p in outputs]
 if freeze["status"]!="FROZEN_LRG005_D1_EXTENSION_TARGET" or freeze["result_paths"]!=expected_paths:raise RuntimeError("freeze contract")
 for relative,expected in freeze["frozen_files"].items():
  if sha(ROOT/relative)!=expected:raise RuntimeError(f"freeze drift {relative}")
 if json.loads(CAL.read_text())["status"]!="PASS_TARGET_BLIND_LRG005_CALIBRATION" or json.loads(CALVAL.read_text())["status"]!="PASS_CLEAN_LRG005_CALIBRATION_RECONSTRUCTION":raise RuntimeError("calibration not passed")
 groups=tab(GROUPS);panel=tab(PANEL);lookup={uid(r["consensus_group_id"]):r for r in groups}
 if len(panel)!=536 or any(p["unit_id"] not in lookup for p in panel):raise RuntimeError("join")
 prose=[r for r in groups if r["strict_zero_alternative"]=="1" and r["kind"]=="P" and r["grammar_scope"]=="CONFIRMED_PROSE"];bare=Counter();anyext=Counter();d1=Counter()
 for r in prose:
  f=fol(r["page"]);s=seq(r);bare[f,s]+=1;parts=[x.split() for x in s]
  if min(map(len,parts))>=2:
   suffix=tuple(" ".join(x[1:]) for x in parts);anyext[f,suffix]+=1
   if all(x[0]=="D1" for x in parts):d1[f,suffix]+=1
 def total(c):
  z=Counter()
  for (_f,s),n in c.items():z[s]+=n
  return z
 tb,ta,td=map(total,(bare,anyext,d1));scores=[];labels=[]
 for p in panel:
  r=lookup[p["unit_id"]];f=p["physical_folio"];s=seq(r);nb=tb[s]-bare[f,s];na=ta[s]-anyext[f,s];nd=td[s]-d1[f,s];no=na-nd
  if min(nb,no,nd)<0:raise RuntimeError("counts")
  scores.append((math.log((nd+.5)/(nb+.5)),math.log((nd+.5)/(no+.5))))
  if r["kind"]=="L":labels.append(1)
  elif r["kind"]=="P" and r["grammar_scope"]=="CONFIRMED_PROSE":labels.append(0)
  else:raise RuntimeError("target role")
 matrix=np.asarray(scores,dtype=np.float64);y=np.asarray(labels,dtype=np.int8)
 if array_hash(matrix)!=json.loads(SCORE_CAP.read_text())["score_matrix_sha256"] or int(y.sum())!=144:raise RuntimeError("target matrix or role drift")
 g=load_geometry(PANEL,QUOTAS)
 for c,h in g.labels_per_cell.items():
  idx=np.flatnonzero(g.cell_ids==c)
  if int(y[idx].sum())!=h:raise RuntimeError("target quota drift")
 coef=assignment_coefficients(g);evaluation=evaluate(matrix,y,g,coef);passed=bool(evaluation["joint_pass"]);status="CONFIRMED_D1_SPECIFIC_CROSS_REGISTER_EXTENSION_RELATION" if passed else "FINAL_NONCONFIRMATION_LRG005_D1_EXTENSION";decision="AUTHORIZE_D1_EXTENDED_AND_BARE_A_STRUCTURAL_TAGS_AFTER_VALIDATION" if passed else "CLOSE_EXACT_LRG005_RELATION"
 result={"status":status,"decision":decision,"claim_ceiling":"A pass establishes only a D1-specific exact cross-register extended/bare construction relation among conditioned A-initial groups. It does not establish a prefix classifier morpheme POS sound word language cipher meaning plaintext or translation.","freeze_sha256":sha(FREEZE),"score_capacity_sha256":sha(SCORE_CAP),"calibration_sha256":sha(CAL),"calibration_validation_sha256":sha(CALVAL),"counts":{"rows":len(y),"labels":int(y.sum()),"prose":int(len(y)-y.sum()),"cells":len(g.cells),"folios":len(g.folio_names),"channels":2},"coefficient_sha256":array_hash(coef),"score_matrix_sha256":array_hash(matrix),"evaluation":evaluation,"individual_rows_emitted":False,"row_scores_emitted":False,"member_sequences_emitted":False,"source_surfaces_emitted":False}
 text=json.dumps(result,indent=2,sort_keys=True)+"\n";lines=["# LRG005 D1-specific extension target","",f"Status: **{status}**.","",f"Joint two-channel pass: **{passed}**.","","| channel | effect | p | z | positive folios | B | P | odd | even | section balance | parity balance | min deletion | concentration | pass |","|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",*[f"| {m['channel']} | {m['effect']:+.9f} | {m['p']:.9f} | {m['z']:.4f} | {m['positive_folios']}/13 | {m['section_effects']['B']:+.9f} | {m['section_effects']['P']:+.9f} | {m['parity_effects']['ODD']:+.9f} | {m['parity_effects']['EVEN']:+.9f} | {m['section_balance_ratio']:.4f} | {m['parity_balance_ratio']:.4f} | {m['minimum_deletion']:+.9f} | {m['maximum_absolute_folio_concentration']:.4f} | {m['passes']} |" for m in evaluation['metrics']],"",f"Decision: **{decision}**.","","No row score, member sequence, source surface, prefix function, word, POS, sound, meaning, plaintext, or translation is emitted.",""];report="\n".join(lines)
 if any(p.exists() for p in outputs):raise RuntimeError("concurrent output")
 atomic(OUT,text)
 try:atomic(REPORT,report)
 except Exception:OUT.unlink(missing_ok=True);raise
 print(text,end="")
if __name__=="__main__":main()
