#!/usr/bin/env python3
"""Freeze GDT299 capacities and design before physical-role scoring."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';METHOD=R/'GDT299_WHOLE_FORM_PHYSICAL_ROLE_TRANSFER_METHOD.md';CAP=R/'gdt299_capacity.tsv';MAN=R/'gdt299_freeze_manifest.tsv';DESIGN=R/'gdt299_design.json'
ART=['gdt298_result.json','gdt297_result.json','gdt296_result.json','gdt293_result.json','gdt278_result.json','gdt278_native_event_inventory.tsv']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=read(SOURCE);assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);caps=[]
 for panel in sorted({x['control_id'] for x in rows}):
  base=[x for x in rows if x['control_id']==panel and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
  for x in base:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
  eligible=[x for x in base if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2];strata=defaultdict(list)
  for x in eligible:strata[(x['physical_folio'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(x)
  mobile=sum(len(v) for v in strata.values() if len({x['source_surface_sha256'] for x in v})>1)
  caps.append({'control_id':panel,'multi_group_events':len(base),'eligible_events':len(eligible),'eligible_folios':len({x['physical_folio'] for x in eligible}),'null_mobile_events':mobile,'score_capacity':'POWERED' if len(eligible)>=500 else 'UNSCORED_LT500','null_capacity':'VARIABLE' if mobile>=100 else 'DESCRIPTIVE_LOW_MOBILITY'})
 write(CAP,caps);write(MAN,[{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART]);d={'schema':'GDT299_WHOLE_FORM_PHYSICAL_ROLE_TRANSFER_DESIGN_V1','status':'FROZEN_BEFORE_GDT299_SCORING','source_identity':'SHA256_ONLY_NO_SOURCE_STRING_INSPECTION','outcome':'PHYSICAL_GROUP_POSITION_FIRST_MIDDLE_LAST','split':'HELD_PHYSICAL_FOLIO','eligibility':'GROUP_COUNT_GE2_AND_EXACT_HOST_AND_SURFACE_HASH_OUTSIDE_HELD_FOLIO','models':['LAYOUT','PAGE_HOST','WHOLE_FORM'],'layout_context':['section','currier','hand','exact_group_count'],'alpha':.5,'prior_mass':11.0,'voynich_prior_sensitivities':[5.0,22.0],'minimum_scored_events':500,'minimum_null_mobile_events':100,'null_worlds':64,'null_seed':'GDT299_WHOLE_FORM_POSITION_ALIGNMENT_V1','null_strata':['control_id','physical_folio','section','currier','hand','exact_group_count','page_host'],'decision':{'support':'WHOLE_FORM_PHYSICAL_ROLE_TRANSFERS','fail':'WHOLE_FORM_PHYSICAL_ROLE_WEAK_OR_LOCAL','gain_positive':True,'minimum_positive_voynich_folios':60,'both_prior_sensitivities_positive':True,'max_family_p_le':.05},'claim_ceiling':'Held-folio opaque whole-form physical-line placement only; no word morphology function semantic role code value language meaning plaintext or translation.','page_host_substrings_mined':0,'source_strings_inspected':0,'semantic_assignments':0,'f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'capacity_sha256':sha(CAP),'freeze_manifest_sha256':sha(MAN),'method_sha256':sha(METHOD),'implementation':{Path(__file__).name:sha(Path(__file__))}};d['content_sha256']=rch(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'powered':sum(x['score_capacity']=='POWERED' for x in caps),'null_variable':sum(x['null_capacity']=='VARIABLE' for x in caps),'voynich':next(x for x in caps if x['control_id']=='VOYNICH_REFERENCE')},sort_keys=True))
if __name__=='__main__':main()
