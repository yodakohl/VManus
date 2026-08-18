#!/usr/bin/env python3
"""Freeze GDT282 before wrapper-class transfer scoring."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parent
METHOD=R/'GDT282_OUTER_WRAPPER_CLASS_TRANSFER_METHOD.md'; MANIFEST=R/'gdt282_gdt281_freeze_manifest.tsv'; DESIGN=R/'gdt282_design.json'
FROZEN=['GDT281_EDGE_PROFILE_COLLISION_SENSITIVITY_METHOD.md','GDT281_EDGE_PROFILE_COLLISION_SENSITIVITY_REPORT.md','gdt281_design.json','gdt281_design_validation.json','gdt281_gdt280_freeze_manifest.tsv','gdt281_exact_scores.tsv','gdt281_exact_shapley.tsv','gdt281_exact_profiles.tsv','gdt281_null_results.tsv','gdt281_folio_scores.tsv','gdt281_counterexamples.tsv','gdt281_result.json','gdt281_validation.json','run_gdt281_edge_profile_collision_sensitivity.py','validate_gdt281_edge_profile_collision_sensitivity.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):
 q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 parent=json.loads((R/'gdt281_result.json').read_text());valid=json.loads((R/'gdt281_validation.json').read_text())
 assert parent['status']=='HASH_COLLISION_SENSITIVITY_PRESERVES_LATIN_RIGHT_VOYNICH_WRAPPER_SPLIT' and parent['content_sha256']==csha(parent)
 assert valid['status']=='PASS' and valid['result_sha256']==sha(R/'gdt281_result.json')
 rows=[{'artifact':x,'frozen_sha256':sha(R/x)} for x in FROZEN]
 with MANIFEST.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,['artifact','frozen_sha256'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 d={'schema':'GDT282_OUTER_WRAPPER_CLASS_TRANSFER_DESIGN_V1','status':'FROZEN_BEFORE_GDT282_SCORING','parent_result_sha256':sha(R/'gdt281_result.json'),'parent_content_sha256':parent['content_sha256'],'method_sha256':sha(METHOD),'freeze_manifest_sha256':sha(MANIFEST),'primary_panel':'VOYNICH_REFERENCE','calibration_panels':['LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC'],'models':['BASE_NO_WRAPPER','WRAPPER_PRESENCE','Q_BINARY','FULL_WRAPPER_IDENTITY','FULL_WRAPPER_PLUS_Q_REDUNDANCY'],'wrapper_classes':['NONE','q','ch','d','sh','che','t','s'],'class_probe_rule':'EXHAUSTIVE_ONE_VS_REST_BINARY','superseded_invalid_probe':'UNIQUE_RENAME_IS_BIJECTIVE_ZERO_INFORMATION','transfer_regimes':['HELD_FOLIO_LOFO_SAFE','HELD_SECTION_PUBLISHED','HELD_HAND_PUBLISHED'],'powered_sections':['B','C','H','P','S','T'],'powered_hands':['1','2','3','5'],'descriptive_hands':['@'],'null_worlds':64,'null_seed_family':'GDT276_MATCHED_CONTEXT_V1','exact_context':True,'redundancy_tolerance_bits':1e-10,'new_corpora':0,'semantic_assignments':0,'hpr1_semantics_used':0,'page_host_substrings_mined':0,'f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'claim_ceiling':'Transfer of an opaque wrapper-class character-prediction channel only; no function morphology language meaning plaintext or translation.','implementation_sha256':sha(Path(__file__))}
 d['content_sha256']=csha(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'frozen_files':len(rows)},sort_keys=True))
if __name__=='__main__':main()
