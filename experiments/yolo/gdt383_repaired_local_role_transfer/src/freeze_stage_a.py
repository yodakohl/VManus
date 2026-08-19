#!/usr/bin/env python3
"""Freeze GDT383 Stage A before reading the GDT382 hidden oracle."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt383_repaired_local_role_transfer";ART=BASE/"artifacts";G382=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts";G378=ROOT/"experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"
ENC=G382/"gdt382_voynichified_observation_layer.tsv.gz";ORACLE=G378/"gdt378_hidden_oracle.tsv.gz"
ENDPOINTS=["FUNCTION_WORD","ALTERNATIVE_OR","POLARITY_EXCLUSION","UNTIL_STATE_GATE","COORDINATOR","REF_ANAPHORA"]
REPS=["HOST_IDENTITY","COMPLETE_RENDERED_GROUP","CONSTRUCTION_STATE","COMPOSITE_JOINT_STATE","SHORT_CONSTRUCTION_SPAN"]
OUTCOMES=["POST_RETURN_ABC_A","POST_PERSIST_THEN_EXIT","POST_HOMOGENEOUS_3","POST_LOW_DIVERSITY_3","POST_ANY_BOUNDARY_3","POST_WRAPPER_CHANGE_3","POST_RENDERER_STABLE_3","POST_TERMINUS_3"]
CHANNELS=["FREQUENCY","RECURRENCE","LINE_FIELD_POSITION","RECORD_RELATIVE_POSITION","BOUNDARY_CLOSURE","PREVIOUS_STATE","RECORD_LENGTH"]
MODES=["FREE_TOKEN","PREFIX","SUFFIX","WRAPPER_ALTERNATION","BOUNDARY_CHOICE","POSITIONAL_ALTERNATION","ZERO_SUPPLETIVE"]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 ART.mkdir(parents=True,exist_ok=True)
 d={"schema":"GDT383_STAGE_A_FREEZE_V1","status":"FROZEN_BEFORE_POSITIVE_CONTROL_EVALUATION","inputs":{"encoded_observation":{str(ENC.relative_to(ROOT)):sha(ENC)},"hidden_oracle_commitment":{str(ORACLE.relative_to(ROOT)):sha(ORACLE)},"gdt382_result":{str((G382/'gdt382_result.json').relative_to(ROOT)):sha(G382/'gdt382_result.json')}},"endpoints":ENDPOINTS,"resolutions":REPS,"post_only_outcomes":OUTCOMES,"grammar_channels":CHANNELS,"channel_treatments":["EVIDENCE","CONDITIONED_NUISANCE","OMITTED"],"realization_modes":MODES,"development_domains":["COREMA","PCEEC2","CURIOUS_CURES"],"confirmation_domains":["HARLEIAN_COOKERY","QUINTE_ESSENCE"],"leakage_ceiling_source_only_auc":.65,"role_gate":{"macro_auc":.80,"positive_gain_domains":3,"hierarchy_minus_exact_joint_auc":.02,"hierarchy_minus_universal_auc":.10,"max_family_p":.05},"realization_gate":{"cells":42,"minimum_auc":.90,"positive_gain_required":True},"downstream_gate":{"minimum_roles":4,"coordinator_required":True,"positive_each_confirmation_domain":True,"max_family_p":.05},"null":{"worlds":512,"strata":["domain","outer_fold","record_length_bin","pivot_position_bin","pivot_boundary"],"type":"FIXED_CROSSFIT_PREDICTION_MAX_FAMILY"},"source_x":"PIVOT_AND_PRE_PIVOT_ONLY","outcome_y":"STRICTLY_J_PLUS_1_TO_J_PLUS_3_ONLY","gdt381_target_artifacts_allowed":False,"voynich_stage_b_authorized":False,"voynich_rows_read":0,"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"documents":{str((BASE/n).relative_to(ROOT)):sha(BASE/n) for n in ['METHOD.md','README.md','experiment.json']},"implementation":{str((BASE/'src/freeze_stage_a.py').relative_to(ROOT)):sha(BASE/'src/freeze_stage_a.py')}}
 d["content_hash"]=content(d);(ART/"gdt383_stage_a_freeze.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":d["status"],"content_hash":d["content_hash"]}))
if __name__=="__main__":main()
