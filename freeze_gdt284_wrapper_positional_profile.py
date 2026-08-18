#!/usr/bin/env python3
"""Freeze GDT284 panels, instrument, and comparison rules before scoring."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
METHOD=R/'GDT284_WRAPPER_POSITIONAL_PROFILE_CALIBRATION_METHOD.md'
DESIGN=R/'gdt284_design.json';MANIFEST=R/'gdt284_freeze_manifest.tsv'
PANELS=['ORDINARY_NATURAL_LANGUAGE','ABBREVIATION_HEAVY_MEDIEVAL','LEARNED_ABBREVIATION_MAP','LEARNED_ABBREVIATION_SAMPLED','AUGSBURG_ACCOUNTS_1402_1424','ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND','LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE']
ARTIFACTS=['gdt283_design.json','gdt283_result.json','gdt283_component_scores.tsv','gdt283_summary.tsv','gdt283_null_results.tsv','run_gdt283_wrapper_host_coupling_localization.py','gdt278_native_event_inventory.tsv','gdt278_control_manifest.tsv','gdt278_result.json','gdt278_validation.json','gdt276_design.json']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 rows=[]
 for name in ARTIFACTS:rows.append({'artifact':name,'frozen_sha256':sha(R/name)})
 with MANIFEST.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=['artifact','frozen_sha256'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 design={'schema':'GDT284_WRAPPER_POSITIONAL_PROFILE_CALIBRATION_DESIGN_V1','status':'CORRECTED_FROZEN_BEFORE_AUTHORITATIVE_GDT284_SCORING','panels':PANELS,'events_per_panel':8448,'components':['INITIAL','INTERNAL','FINAL','EOS'],'modes':['STANDARD_HELD_FOLIO','NESTED_UNSEEN_HOST_BUCKET'],'models':['BASE_NO_WRAPPER','FULL_WRAPPER_IDENTITY'],'host_bucket_count':8,'host_bucket_seed':'GDT283_HOST_FOLD','null_worlds':64,'null_seed_family':'GDT283_FIRSTCHAR_LENGTH_MATCHED_V1','null_strata':['section','currier','hand','within_field_position','host_length','first_host_character'],'maxT_statistic':'MAX_PANEL_STANDARDIZED_TOTAL_GAIN_OVER_NULL_VARIABLE_PANELS','capacity_rule':{'zero_wrapper_mobile_events':'UNSCORED_NO_WRAPPER_CAPACITY','zero_context_reuse_or_null_variance':'UNSCORED_NO_CONTEXT_REUSE','exclude_from_sign_match':True,'exclude_from_standardized_maxT':True,'known_zero_wrapper_capacity_panels':['LEARNED_ABBREVIATION_MAP','LEARNED_ABBREVIATION_SAMPLED'],'known_zero_context_reuse_panels':['ORDINARY_NATURAL_LANGUAGE','ABBREVIATION_HEAVY_MEDIEVAL'],'chronology':'TWO_ZERO_WRAPPER_PANELS_FOUND_PRE_SCORE;TWO_ZERO_CONTEXT_REUSE_PANELS_FOUND_BY_FAILED_FIRST_ATTEMPT_AND_FOUR_WORLD_DIAGNOSTIC;NO_AUTHORITATIVE_ARTIFACTS_OR_NONZERO_RANKS_EXPOSED'},'fingerprint_metrics':['FOUR_SIGNED_COMPONENT_GAINS','ONSET_BODY_SUM','TERMINAL_SUM','TOTAL','EXACT_SIGN_PATTERN','DESCENDING_COMPONENT_RANK','UNSCALED_EUCLIDEAN_DISTANCE_TO_VOYNICH'],'classification':{'two_or_more_architecture_categories_exact_standard_sign_match':'VOYNICH_POSITIONAL_PROFILE_NOT_ARCHITECTURE_SPECIFIC','one_architecture_category_exact_standard_sign_match':'VOYNICH_POSITIONAL_PROFILE_CATEGORY_LOCAL','zero_control_exact_standard_sign_match':'VOYNICH_POSITIONAL_PROFILE_DISTINCT_IN_CURRENT_CONTROLS'},'semantic_assignments':0,'page_host_substrings_mined':0,'threshold_tuned':False,'new_synthetic_worlds':0,'oracle_fields_scored':0,'claim_ceiling':'Positional-profile calibration of opaque wrapper-conditioned character gain only; no morphology language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'freeze_manifest_sha256':sha(MANIFEST),'method_sha256':sha(METHOD),'implementation':{'freeze_gdt284_wrapper_positional_profile.py':sha(Path(__file__))}}
 design['content_sha256']=csha(design);DESIGN.write_text(json.dumps(design,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':design['status'],'panels':len(PANELS),'content_sha256':design['content_sha256']},sort_keys=True))
if __name__=='__main__':main()
