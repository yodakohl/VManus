#!/usr/bin/env python3
"""Freeze score-blind GDT301 domain-transfer capacities."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;S=R/'gdt278_native_event_inventory.tsv';M=R/'GDT301_WHOLE_FORM_DOMAIN_TRANSFER_METHOD.md';C=R/'gdt301_capacity.tsv';F=R/'gdt301_freeze_manifest.tsv';D=R/'gdt301_design.json';AX=['physical_folio','register','section','currier','hand'];ART=['gdt300_result.json','gdt299_result.json','gdt278_result.json','gdt278_native_event_inventory.tsv']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=read(S);assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);cap=[]
 for p in sorted({x['control_id'] for x in rows}):
  base=[x for x in rows if x['control_id']==p and int(x['group_count'])>=2]
  for ax in AX:
   n=lev=0
   for v in sorted({x[ax] for x in base}):
    tr=[x for x in base if x[ax]!=v];hs={x['page_host'] for x in tr};ss={x['source_surface_sha256'] for x in tr};z=[x for x in base if x[ax]==v and x['page_host'] in hs and x['source_surface_sha256'] in ss];n+=len(z);lev+=bool(z)
   cap.append({'control_id':p,'held_axis':ax,'eligible_events':n,'held_levels_with_events':lev,'capacity':'POWERED' if n>=500 and lev>=2 else 'UNSCORED'})
 write(C,cap);write(F,[{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART]);d={'schema':'GDT301_WHOLE_FORM_DOMAIN_TRANSFER_DESIGN_V1','status':'FROZEN_BEFORE_GDT301_SCORING','axes':AX,'outcome':'PHYSICAL_GROUP_POSITION_FIRST_MIDDLE_LAST','eligibility':'GROUP_COUNT_GE2_HOST_AND_SURFACE_PRESENT_OUTSIDE_HELD_AXIS_VALUE','models':['GLOBAL','LAYOUT','PAGE_HOST','WHOLE_FORM'],'layout':'EXACT_GROUP_COUNT_PLUS_ALL_METADATA_AXES_EXCEPT_HELD_AXIS','alpha':.5,'prior_mass':11.0,'voynich_prior_sensitivities':[5.0,22.0],'null_worlds':64,'null_seed':'GDT301_WHOLE_FORM_DOMAIN_V1','null_strata':['control_id','physical_folio','register','section','currier','hand','exact_group_count','page_host'],'max_family':'MAX_FIVE_VOYNICH_AXIS_STANDARDIZED_GAIN','decision':{'support':'WHOLE_FORM_ROLE_CROSS_DOMAIN_SUPPORTED','local':'WHOLE_FORM_ROLE_REGISTER_LOCAL','mixed':'WHOLE_FORM_ROLE_DOMAIN_MIXED','required_positive_axes':['section','currier','hand'],'minimum_positive_axes':4,'max_five_p_le':.05,'folio_reproduction_tolerance':1e-9},'claim_ceiling':'Cross-domain stability or locality of opaque complete-form physical placement only; no lexicality word morpheme linguistic function semantic role sound language meaning plaintext or translation.','source_strings_inspected':0,'page_host_substrings_mined':0,'semantic_assignments':0,'f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'capacity_sha256':sha(C),'freeze_manifest_sha256':sha(F),'method_sha256':sha(M),'implementation':{Path(__file__).name:sha(Path(__file__))}};q=dict(d);d['content_sha256']=canonical(q);D.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'powered':sum(x['capacity']=='POWERED' for x in cap),'voynich':[x for x in cap if x['control_id']=='VOYNICH_REFERENCE']},sort_keys=True))
if __name__=='__main__':main()
