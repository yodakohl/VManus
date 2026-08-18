#!/usr/bin/env python3
"""Freeze GDT289 before wrapper-outcome scoring."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
METHOD=R/'GDT289_CROSS_HOST_WRAPPER_POSITION_TRANSFER_METHOD.md'
DESIGN=R/'gdt289_design.json';MAN=R/'gdt289_freeze_manifest.tsv'
PANELS=['AUGSBURG_ACCOUNTS_1402_1424','ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND','LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE']
ART=['gdt286_result.json','gdt286_validation.json','gdt284_result.json','gdt278_native_event_inventory.tsv','gdt288_result.json']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 with MAN.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,['artifact','frozen_sha256'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART])
 d={'schema':'GDT289_CROSS_HOST_WRAPPER_POSITION_TRANSFER_DESIGN_V1','status':'CORRECTED_FROZEN_BEFORE_GDT289_SCORING','panels':PANELS,'events_per_panel':8448,'host_bucket_count':8,'host_bucket_seed':'GDT289_HOST_BUCKET','outcome':'FROZEN_WRAPPER_CLASS','models':['POSITION_CONTEXT','OTHER_POSITION_HOST_BAG','CROSS_HOST_POSITION_TRANSFER'],'target_cell_rule':'FORBID_TARGET_HOST_TARGET_POSITION_PROFILE','transition_training_rule':'EXCLUDE_HELD_FOLIO_AND_TARGET_HOST_BUCKET','transition_estimator':'HOST_EQUAL_NORMALIZED_PROFILE_OUTER_PRODUCTS_DIRICHLET_ONE_HALF','forecast_combination':'SOURCE_POSITION_COUNT_WEIGHTED_MEAN_WITH_OTHER_POSITION_EFFECTIVE_COUNT','shape_context':['section','currier','hand','register','within_field_position','host_length','first_host_character','last_host_character'],'global_prior':'DIRICHLET_ONE_HALF','hierarchical_prior_mass':11.0,'primary_split':'HELD_PHYSICAL_FOLIO','voynich_sensitivities':['HELD_SECTION','HELD_HAND'],'null_worlds':64,'null_seed':'GDT289_HELD_WRAPPER_ALIGNMENT','null_operation':'PERMUTE_HELD_WRAPPER_OUTCOMES_WITHIN_EXACT_FOLIO_REGISTER_POSITION_LENGTH_AND_HOST_EDGE_STRATA_AFTER_PREDICTIONS_FREEZE','maxT':'MAX_STANDARDIZED_TRANSFER_GAIN_OVER_8_PANELS','minimum_voynich_scored_events':1000,'decision':{'support':'LOW_COMPLEXITY_CROSS_HOST_POSITION_RULE_SUPPORTED','fail':'HOST_POSITION_EFFECT_REQUIRES_HOST_SPECIFIC_TABLE','capacity':'INSUFFICIENT_CROSS_POSITION_HOST_CAPACITY','minimum_positive_host_buckets':6,'minimum_positive_positions':3,'require_held_section_and_hand_positive':True,'alpha':0.05},'correction_chronology':'NULL_OPERATION_REPLACED_AFTER_CAPACITY_ONLY_AUDIT_AND_BEFORE_ANY_WRAPPER_OUTCOME_SCORE','new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':'Reusable opaque wrapper-position transfer only; no morphology lexical class function abbreviation sound language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'freeze_manifest_sha256':sha(MAN),'method_sha256':sha(METHOD),'implementation':{'freeze_gdt289_cross_host_wrapper_position.py':sha(Path(__file__))}}
 d['content_sha256']=csha(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'content_sha256':d['content_sha256']},sort_keys=True))
if __name__=='__main__':main()
