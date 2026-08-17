#!/usr/bin/env python3
"""Freeze GDT277 bytes and the GDT278 magnitude endpoint before control admission."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

R=Path(__file__).resolve().parent
METHOD=R/'GDT278_GDT277_MAGNITUDE_CALIBRATION_METHOD.md'
DESIGN=R/'gdt278_magnitude_design.json'
FREEZE=R/'gdt278_gdt277_freeze_manifest.tsv'
REFERENCE=R/'gdt278_reference_magnitude.tsv'

ARTIFACTS=[
 'GDT277_GDT276_SIGNATURE_CALIBRATION_METHOD.md',
 'GDT277_GDT276_SIGNATURE_CALIBRATION_REPORT.md',
 'freeze_gdt277_signature_calibration.py',
 'validate_gdt277_design.py',
 'run_gdt277_signature_calibration.py',
 'validate_gdt277_signature_calibration.py',
 'gdt277_capacity_audit.tsv','gdt277_control_manifest.tsv',
 'gdt277_counterexamples.tsv','gdt277_design.json',
 'gdt277_design_validation.json','gdt277_folio_scores.tsv',
 'gdt277_gdt276_freeze_manifest.tsv','gdt277_matched_event_inventory.tsv',
 'gdt277_null_results.tsv','gdt277_representation_fold_scores.tsv',
 'gdt277_representation_leakage.tsv','gdt277_result.json',
 'gdt277_signature_summary.tsv','gdt277_validation.json',
 'gdt277_world_scores.tsv']

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def content(v)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rows(p:Path):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p:Path,z:list[dict]):
 fields=list(z[0])
 with p.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(z)

def main():
 missing=[p for p in ARTIFACTS if not (R/p).is_file()];assert not missing,missing
 write(FREEZE,[{'artifact':p,'frozen_sha256':sha(R/p),'immutability':'MUST_REMAIN_BYTE_IDENTICAL'} for p in ARTIFACTS])
 g277=[x for x in rows(R/'gdt277_world_scores.tsv') if x['control_id']=='VOYNICH_MATCHED_REFERENCE' and x['model']=='ABBREVIATION_HEAVY_LANGUAGE']
 g276=[x for x in rows(R/'gdt276_world_scores.tsv') if x['world']=='ABBREVIATION_HEAVY_LANGUAGE']
 assert len(g277)==len(g276)==1
 refs=[]
 for view,n,q,skey in [('LENGTH_MATCHED_OVERLAY',4476,g277[0],'matched_savings_bits'),('NATIVE_ORDER',8448,g276[0],'matched_null_savings_bits')]:
  saving=float(q[skey]);sd=float(q['matched_null_sd_bits']);refs.append({'reference_id':'VOYNICH','view':view,'events':n,'saving_bits':f'{saving:.15f}','saving_bits_per_event':f'{saving/n:.15f}','null_sd_bits':f'{sd:.15f}','null_z':f'{saving/sd:.15f}','source_artifact':'gdt277_world_scores.tsv' if view.startswith('LENGTH') else 'gdt276_world_scores.tsv','status':'EXPOSED_FROZEN_REFERENCE'})
 write(REFERENCE,refs)
 design={
  'schema':'GDT278_MAGNITUDE_ENDPOINT_DESIGN_V1',
  'status':'FROZEN_BEFORE_EXPANDED_CONTROL_ADMISSION_OR_SCORING',
  'gdt277_policy':'BYTE_IMMUTABLE',
  'endpoint':{
   'model':'ABBREVIATION_HEAVY_LANGUAGE',
   'saving_bits':'NULL_MEAN_HELD_BITS_MINUS_OBSERVED_HELD_BITS',
   'saving_bits_per_event':'SAVING_BITS_DIVIDED_BY_SCORED_GROUP_EVENTS',
   'null_z':'SAVING_BITS_DIVIDED_BY_POPULATION_SD_OF_64_NULL_HELD_BITS',
   'null_worlds':64,
   'primary_coordinate':'SAVING_BITS_PER_EVENT',
   'mandatory_companion':'NULL_Z'},
  'views':{
   'LENGTH_MATCHED_OVERLAY':{'role':'PRIMARY','events':4476,'scaffold':'EXACT_GDT277','length_quotas':'EXACT_GDT277','native_cross_length_adjacency':False},
   'NATIVE_ORDER':{'role':'SENSITIVITY','reference_events':8448,'target_events_when_available':8448,'minimum_power_fraction':0.8,'source_unit_selection':'SHA256_ORDER_THEN_NATIVE_ORDER_WITHIN_SELECTED_UNITS','final_unit_truncation':'DETERMINISTIC_ALLOWED'}},
  'comparison_rule':{
   'view_reproduced':'CONTROL_S_EVENT_GTE_VMS_S_EVENT_AND_CONTROL_Z_GTE_VMS_Z',
   'robust_reproduction':'BOTH_POWERED_VIEWS_REPRODUCED',
   'tolerance_band':'NONE',
   'composite_score':'NONE',
   'report_ratios_and_ranks':True},
  'representation':{
   'published_full_inventory':'INTEGRITY_ANCHOR',
   'lofo_safe':'MANDATORY_PRIMARY_SENSITIVITY;OPERATION_INVENTORY_AND_ALPHABET_LEARNED_WITHOUT_HELD_FOLIO;OBSERVED_AND_NULL_SCORED_FOLD_LOCAL'},
  'control_admission':'SEPARATE_HASH_BOUND_MANIFEST_AFTER_THIS_FREEZE;ARCHITECTURE_LABEL_INDEPENDENT_OF_SCORE;ORACLE_NOT_SCORED',
  'prohibitions':['HPR1_SEMANTICS','VOYNICH_SUBSTRING_MINING','MEANING','PLAINTEXT','TRANSLATION','POSTHOC_THRESHOLD'],
  'f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},
  'inputs':{'gdt277_freeze_manifest':sha(FREEZE),'reference_magnitude':sha(REFERENCE)},
  'documents':{METHOD.name:sha(METHOD)},
  'implementation':{Path(__file__).name:sha(Path(__file__))}}
 design['content_sha256']=content(design);DESIGN.write_text(json.dumps(design,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':design['status'],'frozen_gdt277_artifacts':len(ARTIFACTS),'references':refs},sort_keys=True))
if __name__=='__main__':main()
