#!/usr/bin/env python3
"""Freeze the expanded GDT278 ground-truth control panel before scoring."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
METHOD=R/'GDT278_GDT277_MAGNITUDE_CALIBRATION_METHOD.md';AUDIT=R/'GDT278_CONTROL_SOURCE_AUDIT.md'
DESIGN=R/'gdt278_magnitude_design.json';OUT=R/'gdt278_control_manifest.tsv';FREEZE=R/'gdt278_control_source_freeze.json'
ROWS=[
 ('ORDINARY_NATURAL_LANGUAGE','REAL_NATURAL_LANGUAGE','Nuremberg expanded','gdt155_unblinded_lines.tsv','gdt155_blinded_diplomatic.tsv','NUREMBERG_EXPANDED','PAIRED_EXPANSION_TRUTH','MATCHED_AND_NATIVE'),
 ('ABBREVIATION_HEAVY_MEDIEVAL','REAL_DIPLOMATIC_ABBREVIATION','Nuremberg diplomatic','gdt155_blinded_diplomatic.tsv','gdt155_unblinded_lines.tsv','NUREMBERG_DIPLOMATIC','PAIRED_DIPLOMATIC_EXPANSION_TRUTH','MATCHED_AND_NATIVE'),
 ('STE1_EXPANDED_RECIPES','REAL_NATURAL_LANGUAGE','Ste1 expanded recipes','gdt155_unblinded_lines.tsv','gdt155_blinded_diplomatic.tsv','STE1_EXPANDED','PAIRED_EXPANSION_TRUTH','NATIVE_LOW_CAPACITY'),
 ('STE1_DIPLOMATIC_RECIPES','REAL_DIPLOMATIC_ABBREVIATION','Ste1 diplomatic recipes','gdt155_blinded_diplomatic.tsv','gdt155_unblinded_lines.tsv','STE1_DIPLOMATIC','PAIRED_DIPLOMATIC_EXPANSION_TRUTH','NATIVE_LOW_CAPACITY'),
 ('AUGSBURG_ACCOUNTS_1402_1424','REAL_STRUCTURED_NATURAL_LANGUAGE','Augsburg municipal accounts','gdt158_source_freeze.json','gdt158_structured_source_manifest.tsv','AUGSBURG_XLSX','FROZEN_EXTERNAL_XLSX_SHA256','MATCHED_AND_NATIVE'),
 ('LATIN_MEDICAL_GRAPHEMATIC','REAL_DIPLOMATIC_ABBREVIATION','Latin medical graphematic','gdt159_diplomatic_corpora.json.gz','gdt159_diplomatic_source_provenance.json','GDT159_CORPUS_ID','SCHOLARLY_DIPLOMATIC_SOURCE_FREEZE','CAPACITY_CHECK_FROZEN'),
 ('LATIN_15C_GRAPHEMATIC','REAL_DIPLOMATIC_ABBREVIATION','15c Latin graphematic','gdt159_diplomatic_corpora.json.gz','gdt159_diplomatic_source_provenance.json','GDT159_CORPUS_ID','SCHOLARLY_DIPLOMATIC_SOURCE_FREEZE','CAPACITY_CHECK_FROZEN'),
 ('LATIN_SCHOLASTIC_GRAPHEMATIC','REAL_DIPLOMATIC_ABBREVIATION','Latin scholastic graphematic','gdt159_diplomatic_corpora.json.gz','gdt159_diplomatic_source_provenance.json','GDT159_CORPUS_ID','SCHOLARLY_DIPLOMATIC_SOURCE_FREEZE','CAPACITY_CHECK_FROZEN'),
 ('IFORAL_1395_1411_GRAPHEMATIC','REAL_DIPLOMATIC_ABBREVIATION','Latin Portuguese charters','gdt159_diplomatic_corpora.json.gz','gdt159_diplomatic_source_provenance.json','GDT159_CORPUS_ID','SCHOLARLY_DIPLOMATIC_SOURCE_FREEZE','CAPACITY_CHECK_FROZEN'),
 ('LATIN_GERMAN_APOTHECARY_LATE15','REAL_DIPLOMATIC_ABBREVIATION','Latin German apothecary','gdt159_diplomatic_corpora.json.gz','gdt159_diplomatic_source_provenance.json','GDT159_CORPUS_ID','SCHOLARLY_DIPLOMATIC_SOURCE_FREEZE','NATIVE_LOW_CAPACITY_EXPECTED'),
 ('LEARNED_ABBREVIATION_MAP','GENERATED_HISTORICALLY_LEARNED_ABBREVIATION','held-book MAP transducer output','gdt157_generated_diplomatic.tsv','gdt157_result.json','GDT157_MAP','HELD_BOOK_GENERATOR_GROUND_TRUTH','MATCHED_AND_NATIVE'),
 ('LEARNED_ABBREVIATION_SAMPLED','GENERATED_HISTORICALLY_LEARNED_ABBREVIATION','held-book sampled transducer output','gdt157_generated_diplomatic.tsv','gdt157_result.json','GDT157_SAMPLED','HELD_BOOK_GENERATOR_GROUND_TRUTH','MATCHED_AND_NATIVE'),
 ('ARBITRARY_LOCAL_CODEBOOK','SYNTHETIC_LEXICAL_CODEBOOK','GDT172 lexical A','gdt172_blind_parses.json.gz','gdt172_sealed_oracle.json.gz','CONTROL_P','FROZEN_REVERSIBLE_LEXICAL_ID_CODEBOOK','MATCHED_AND_NATIVE'),
 ('COMPOSITIONAL_TECHNICAL_NOTATION','SYNTHETIC_FACTORIAL_TECHNICAL_NOTATION','GDT172 factorial B','gdt172_blind_parses.json.gz','gdt172_sealed_oracle.json.gz','CONTROL_Q','FROZEN_REVERSIBLE_FACTORIAL_DISTRIBUTED_CONTROL','MATCHED_AND_NATIVE'),
 ('HYBRID_SHORTHAND','SYNTHETIC_HUMAN_GROWN_HYBRID','GDT173 human-grown B2','gdt173_blind_parses.json.gz','gdt173_b2_sealed_oracle.json.gz','CONTROL_R','FROZEN_REVERSIBLE_IRREGULAR_DISTRIBUTED_TABLE','MATCHED_AND_NATIVE')]
EXCLUSIONS=[
 {'control_id':'GDT156_IMPOSED_HPR2_ENCODER','reason':'VOYNICH_DERIVED_RULES_PROHIBITED'},
 {'control_id':'FOXTON_FONTANA','reason':'NO_COMPLETE_MACHINE_READABLE_DIPLOMATIC_SURFACE_CORPUS'},
 {'control_id':'COREMA_ROLE_EXPORT','reason':'PUBLISHED_ROLE_OBSERVATION_EXPORT_OMITS_SOURCE_SURFACES'}]
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def content(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def write(p,rows):
 fields=list(rows[0])
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 d=json.loads(DESIGN.read_text());assert d['status']=='FROZEN_BEFORE_EXPANDED_CONTROL_ADMISSION_OR_SCORING'
 out=[]
 for cid,cat,label,obs,oracle,selector,truth,cap in ROWS:
  assert (R/obs).is_file() and (R/oracle).is_file()
  out.append({'control_id':cid,'architecture_category':cat,'label':label,'observation_artifact':obs,'observation_sha256':sha(obs),'architecture_evidence_artifact':oracle,'architecture_evidence_sha256':sha(oracle),'source_selector':selector,'ground_truth_basis':truth,'planned_capacity':cap,'oracle_fields_scored':0,'admitted_before_score':1})
 write(OUT,out)
 obj={'schema':'GDT278_CONTROL_SOURCE_FREEZE_V1','status':'CONTROL_PANEL_FROZEN_BEFORE_GDT278_SCORING','controls':len(out),'categories':sorted({x['architecture_category'] for x in out}),'exclusions':EXCLUSIONS,'augsburg_external_source':{'url':'https://opus.bibliothek.uni-augsburg.de/opus4/files/98153/Augsburger_Baumeisterb%C3%BCcher_1320_1440.xlsx','sha256':'bed2ff0e4e427cc8c602893b852a759c26fe91d18e9891a26ba80829360160a1','tracked_in_git':False},'oracle_fields_scored':0,'voynich_substrings_mined':0,'hpr1_semantics_used':0,'f84':{'inputs':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{'magnitude_design':sha('gdt278_magnitude_design.json'),'magnitude_design_validation':sha('gdt278_magnitude_design_validation.json')},'outputs':{OUT.name:sha(OUT)},'documents':{AUDIT.name:sha(AUDIT),METHOD.name:sha(METHOD)},'implementation':{Path(__file__).name:sha(Path(__file__))}}
 obj['content_sha256']=content(obj);FREEZE.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':obj['status'],'controls':len(out),'categories':len(obj['categories'])},sort_keys=True))
if __name__=='__main__':main()
