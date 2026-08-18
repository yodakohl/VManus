#!/usr/bin/env python3
"""Freeze the GDT285 mechanism test before scoring."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;METHOD=R/'GDT285_EXACT_HOST_REUSE_TERMINAL_LOCALIZATION_METHOD.md';DESIGN=R/'gdt285_design.json';MANIFEST=R/'gdt285_freeze_manifest.tsv'
ART=['gdt284_design.json','gdt284_result.json','gdt284_component_scores.tsv','gdt284_summary.tsv','gdt283_result.json','gdt278_native_event_inventory.tsv','gdt276_design.json']
PANELS=['LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 with MANIFEST.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,['artifact','frozen_sha256'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART])
 d={'schema':'GDT285_EXACT_HOST_REUSE_TERMINAL_LOCALIZATION_DESIGN_V1','status':'FROZEN_BEFORE_GDT285_SCORING','panels':PANELS,'events_per_panel':8448,'modes':['STANDARD','EXACT_HOST_EXCLUDED','MATCHED_NONHOST_EXCLUDED'],'components':['INITIAL','INTERNAL','FINAL','EOS'],'recurrence_bins':{'ZERO':[0,0],'ONE':[1,1],'TWO_TO_THREE':[2,3],'FOUR_TO_SEVEN':[4,7],'EIGHT_PLUS':[8,None]},'matched_donor_tiers':['SECTION_CURRIER_HAND_POSITION_LENGTH_FIRST_WRAPPER','SECTION_CURRIER_HAND_LENGTH_FIRST_WRAPPER','LENGTH_FIRST_WRAPPER','LENGTH_FIRST','ANY_NONHOST'],'donor_order_seed':'GDT285_DONOR_ORDER','donor_start_seed':'GDT285_DONOR_START','primary_subset':'TRAINING_EXACT_HOST_RECURRENCE_AT_LEAST_ONE','decision':{'all_required':True,'standard_recurrent_terminal_lt_zero':True,'exact_excluded_recurrent_terminal_gte_zero':True,'exact_terminal_improvement_gt_matched_terminal_improvement':True,'exact_excluded_recurrent_onset_body_gt_zero':True,'pass':'TERMINAL_PENALTY_REQUIRES_EXACT_HOST_REUSE','fail':'TERMINAL_PENALTY_NOT_LOCALIZED_TO_EXACT_HOST_REUSE'},'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':'Exact parsed-host reuse localization of opaque wrapper-conditioned character gain only; no morphology language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'freeze_manifest_sha256':sha(MANIFEST),'method_sha256':sha(METHOD),'implementation':{'freeze_gdt285_exact_host_reuse.py':sha(Path(__file__))}}
 d['content_sha256']=csha(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'content_sha256':d['content_sha256']},sort_keys=True))
if __name__=='__main__':main()
