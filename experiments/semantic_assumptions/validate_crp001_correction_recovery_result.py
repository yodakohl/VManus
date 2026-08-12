#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

BASE=Path(__file__).resolve().parent; RES=BASE/"results"
METHOD=BASE/"CRP001_CORRECTION_RECOVERY_PANEL_METHOD.md"
SELECTION=RES/"crp001_correction_recovery_selection.json"
SELVAL=RES/"crp001_correction_recovery_selection_validation.json"
RESULT=RES/"crp001_correction_recovery_result.json"
OUT=RES/"crp001_correction_recovery_result_validation.json"
REPORT=RES/"crp001_correction_recovery_result_validation_report.md"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->None:
  if OUT.exists() or REPORT.exists():raise SystemExit("refusing overwrite")
  r=json.loads(RESULT.read_text()); t=r["targets"]
  vectors=[list(x["gates"].values()) for x in t]; positives=[all(v) for v in vectors]
  checks={
   "canonical_result":RESULT.read_bytes()==(json.dumps(r,indent=2,sort_keys=True)+"\n").encode(),
   "prior_artifacts_bound":r["inputs"]=={"method_sha256":sha(METHOD),"selection_sha256":sha(SELECTION),"selection_validation_sha256":sha(SELVAL)},
   "exact_registered_order":[x["locus"] for x in t]==["f18r.3","f19r.2","f26v.5"],
   "official_full_image_hashes":[x["official_full_image_sha256"] for x in t]==["01659aa94a6176b56c621f50c9cbe8c467836d6265a03d8edb1e97e236126e78","c05e13bd154a93d77e2f601f11d9bd886fdf4524a49dbae0339b0bd864f7283c","3378e154f7ef8a45405cb008277aa1dc2229388c456cd3c66438bcca54d02c6b"],
   "official_target_region_hashes":[x["target_region_sha256"] for x in t]==["ea31b9bc7b6a2471a5cf695e7355afdab71adcdfe9cd94acee2b23150972cc08","09b2caec423378be026b8d5b369555702e1fd4191fe2b4d8a74ee019b9f60e02","4321f62f4904b46748f0ba4a6a0cecb045ad07e5e22cc18793e7a003e5261ef8"],
   "five_gate_vectors":vectors==[[False,False,True,True,True]]*3 and [x["all_five_gates_passed"] for x in t]==positives,
   "three_intervention_only_outcomes":[x["outcome"] for x in t]==["INTERVENTION_VISIBLE_BEFORE_STATE_NOT_RECOVERABLE"]*3,
   "zero_recoverable_counts":sum(positives)==r["counts"]["recoverable_two_state_corrections"]==0,
   "both_thresholds_fail":r["threshold_passes"]=={"minimum_positive_folios":False,"minimum_recoverable_targets":False},
   "stop_reconstructed":r["panel_passed"] is False and r["status"]=="STOP_ZERO_OF_THREE_RECOVERABLE_TWO_STATE_CORRECTIONS",
   "zero_semantic_access":r["access"]["ocr_clip_embeddings_automated_segmentation_or_recognition_used"] is False and r["access"]["enhancement_or_contrast_transformation_used"] is False and r["counts"]["formal_associations_scored"]==0}
  if not all(checks.values()):raise SystemExit(",".join(k for k,v in checks.items() if not v))
  v={"experiment":"CRP001_RESULT_VALIDATION","schema":"CRP001_RESULT_VALIDATION_V1","status":"PASS_11_CHECK_SOURCE_GATE_AND_PANEL_STOP_RECONSTRUCTION","source_result_sha256":sha(RESULT),"check_count":len(checks),"checks":checks,"scope_note":"This reconstructs recorded source bindings visual gate vectors and frozen arithmetic; it does not claim an independent second visual inspection.","claim_ceiling":r["claim_ceiling"]}
  OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
  REPORT.write_text("# CRP001 result validation\n\nStatus: **PASS_11_CHECK_SOURCE_GATE_AND_PANEL_STOP_RECONSTRUCTION**.\n\nCompact independent code binds the frozen method and selection, exact target order, three official full-image and region hashes, all five gate vectors, three intervention-only outcomes, zero recoverable corrections, both failed thresholds, canonical result, stop decision, and zero-semantic-access ceiling. It reconstructs recorded judgments rather than claiming a second visual inspection.\n")
if __name__=="__main__":main()
