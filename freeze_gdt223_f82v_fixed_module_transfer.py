#!/usr/bin/env python3
"""Create GDT223 prediction freeze without loading target formal rows."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
MAN=R/'gdt223_f82v_assembly_prediction.tsv'; MOD=R/'gdt222_module_manifest.tsv'
METHOD=R/'GDT223_F82V_FIXED_MODULE_TRANSFER_FREEZE_METHOD.md'; OUT=R/'gdt223_prediction_freeze.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
rows=list(csv.DictReader(MAN.open(),delimiter='\t'))
assert len(rows)==2 and {r['assembly'] for r in rows}=={'TOP','BOTTOM'}
assert all(r['page']=='f82v' and r['physical_folio']=='f82' for r in rows)
assert not any(r['page'].startswith('f84') for r in rows)
assert set(rows[0]['label_loci'].split(','))|set(rows[1]['label_loci'].split(','))=={'f82v.1','f82v.2','f82v.4','f82v.41','f82v.43','f82v.44','f82v.46','f82v.48'}
assert set(rows[0]['prose_loci'].split(','))|set(rows[1]['prose_loci'].split(','))=={'f82v.5','f82v.8','f82v.9','f82v.13','f82v.18','f82v.25','f82v.27','f82v.28','f82v.29','f82v.34','f82v.35','f82v.38'}
v={'schema':'GDT223_F82V_FIXED_MODULE_TRANSFER_FREEZE_V1','status':'FROZEN_BEFORE_TARGET_MODULE_REVEAL','page':'f82v','physical_folio':'f82','assemblies':2,'selected_label_loci':8,'excluded_lateral_label_loci':['f82v.39','f82v.40'],'selected_prose_lines':12,'complete_prose_lines':12,'modules':['ar','ol','dal','dar','sy','te','tee','dy'],'predictions':{'positive_correct_assignment_lead':True,'ar_discriminates_exactly_one_matching_assembly_side':True,'ar_side':'UNPREDICTED'},'access':{'geometry_role_metadata_inspected':True,'completeness_counts_inspected':True,'target_tokens_displayed_in_this_pass':False,'target_module_presence_displayed_in_this_pass':False},'f84':{'accessed':False,'retained':False,'joined':False,'scored':False},'inputs':{MAN.name:sha(MAN),MOD.name:sha(MOD)},'documents':{METHOD.name:sha(METHOD)},'implementation':{Path(__file__).name:sha(Path(__file__))}}
v['freeze_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(v['status'])
