#!/usr/bin/env python3
"""Freeze GDT384 relational definitions before hidden relation construction."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt384_role_specific_relational_consequence"
ART=BASE/"artifacts"
G382=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts"
G378=ROOT/"experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"
G383=ROOT/"experiments/yolo/gdt383_repaired_local_role_transfer/artifacts"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d): return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 ART.mkdir(parents=True,exist_ok=True)
 docs=[BASE/n for n in ["METHOD.md","SOURCE_AUDIT.md","README.md","experiment.json","gdt384_relation_manifest.tsv"]]
 inputs=[G382/"gdt382_voynichified_observation_layer.tsv.gz",G378/"gdt378_hidden_oracle.tsv.gz",ROOT/"gdt176_corema_role_oracle.tsv",G383/"gdt383_stage_a_result.json"]
 out={
  "schema":"GDT384_STAGE_A_FREEZE_V1","status":"FROZEN_BEFORE_RELATION_CONSTRUCTION_OR_SCORING",
  "priority_role":"COORDINATOR","roles":["COORDINATOR","ALTERNATIVE_OR","REF_ANAPHORA","UNTIL_STATE_GATE","POLARITY_EXCLUSION","FUNCTION_WORD"],
  "resolutions":["HOST_IDENTITY","COMPLETE_RENDERED_GROUP","CONSTRUCTION_STATE","COMPOSITE_JOINT_STATE","SHORT_CONSTRUCTION_SPAN"],
  "grammar_channels":["FREQUENCY","RECURRENCE","LINE_FIELD_POSITION","RECORD_RELATIVE_POSITION","BOUNDARY_CLOSURE","PREVIOUS_STATE","RECORD_LENGTH"],
  "channel_treatments":["EVIDENCE","CONDITIONED_NUISANCE","OMITTED"],
  "relation_gate":{"minimum_positive":50,"minimum_negative":50,"source_overlap_auc_max":.65,"deterministic_overlap_auc_max":.65,"relation_auc_increment":.02,"positive_gain_each_gold_domain":True,"positive_held_collection_blocks":4,"max_family_p":.05},
  "role_gate":{"macro_auc":.80,"positive_gain":True,"hierarchy_minus_exact_joint_auc":.02,"hierarchy_minus_universal_auc":.10},
  "full_stage_gate":{"all_six_roles":True,"priority_coordinator_required":True,"all_42_realization_controls":True},
  "null":{"worlds":2048,"family":"SIX_ROLES_X_RELATION_VARIANTS_X_RESOLUTIONS_X_CHANNELS_X_HORIZONS","strata":["domain","held_collection","record_length_bin","pivot_position_bin","boundary_state"],"type":"REBUILD_FOLD_TRAINED_ROLE_CONTRIBUTION_MAX_FAMILY"},
  "inputs":{str(p.relative_to(ROOT)):sha(p) for p in inputs},
  "documents":{str(p.relative_to(ROOT)):sha(p) for p in docs},
  "implementation":{str((BASE/"src/freeze_stage_a.py").relative_to(ROOT)):sha(BASE/"src/freeze_stage_a.py")},
  "voynich_rows_read":0,"voynich_stage_b_authorized":False,"gdt381_target_artifacts_allowed":False,
  "f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"claim_ceiling":"COMPARATOR_ROLE_RELATION_INSTRUMENT_FREEZE_ONLY"}
 out["content_hash"]=content(out);(ART/"gdt384_stage_a_freeze.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":out["status"],"roles":len(out["roles"]),"worlds":out["null"]["worlds"]}))
if __name__=="__main__": main()
