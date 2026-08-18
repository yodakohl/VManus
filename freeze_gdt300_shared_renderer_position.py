#!/usr/bin/env python3
"""Freeze GDT300 shared-renderer positional decomposition before scoring."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
SOURCE=R/'gdt278_native_event_inventory.tsv';METHOD=R/'GDT300_SHARED_RENDERER_POSITIONAL_GRAMMAR_METHOD.md'
CAP=R/'gdt300_capacity.tsv';MAN=R/'gdt300_freeze_manifest.tsv';DESIGN=R/'gdt300_design.json'
ART=['gdt299_result.json','gdt299_design.json','gdt299_capacity.tsv','gdt297_result.json','gdt278_result.json','gdt278_native_event_inventory.tsv']
FIELDS=['wrapper','local_frame','inner_d','right_family','dy_closure','b3']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=read(SOURCE);assert rows and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);caps=[]
 for panel in sorted({x['control_id'] for x in rows}):
  base=[x for x in rows if int(x['group_count'])>=2 and x['control_id']==panel];hf=defaultdict(set);sf=defaultdict(set)
  for x in base:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
  ev=[x for x in base if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2];strata=defaultdict(list)
  for x in ev:strata[(x['physical_folio'],x['section'],x['currier'],x['hand'],x['group_count'],x['page_host'])].append(x)
  mobile=sum(len(v) for v in strata.values() if len({tuple(x[k] for k in FIELDS) for x in v})>1)
  caps.append({'control_id':panel,'eligible_events':len(ev),'eligible_folios':len({x['physical_folio'] for x in ev}),'renderer_mobile_events':mobile,'score_capacity':'POWERED' if len(ev)>=500 else 'UNSCORED_LT500','null_capacity':'VARIABLE' if mobile>=100 else 'DESCRIPTIVE_LOW_MOBILITY'})
 write(CAP,caps);write(MAN,[{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART]);d={'schema':'GDT300_SHARED_RENDERER_POSITIONAL_GRAMMAR_DESIGN_V1','status':'FROZEN_BEFORE_GDT300_SCORING','question':'SHARED_RENDERER_VS_EXACT_HOST_RENDERER_POSITION_FUNCTION','source_identity':'SHA256_ONLY_NO_SOURCE_STRING_INSPECTION','outcome':'PHYSICAL_GROUP_POSITION_FIRST_MIDDLE_LAST','split':'HELD_PHYSICAL_FOLIO','eligibility':'EXACT_GDT299_ELIGIBILITY','layout_context':['section','currier','hand','exact_group_count'],'renderer_fields':FIELDS,'shared_models':FIELDS+['renderer_tuple'],'combination':'NORMALIZED_P_HOST_TIMES_P_COMPONENT_DIVIDED_BY_P_LAYOUT','exact_interaction_model':'HOST_X_RENDERER_BACKED_TO_PAGE_HOST','alpha':.5,'prior_mass':11.0,'voynich_prior_sensitivities':[5.0,22.0],'null_worlds':64,'null_seed':'GDT300_SHARED_RENDERER_POSITION_V1','null_strata':['control_id','physical_folio','section','currier','hand','exact_group_count','page_host'],'max_family':'MAX_SEVEN_PANEL_MODEL_STANDARDIZED_SHARED_GAIN','decision':{'support':'SHARED_RENDERER_POSITIONAL_GRAMMAR_SUPPORTED','host_specific':'POSITION_SIGNAL_HOST_SPECIFIC','reproduction_fail':'WHOLE_FORM_POSITION_SIGNAL_NOT_REPRODUCED','minimum_positive_folios':60,'minimum_shared_fraction':.5,'both_prior_sensitivities_positive':True,'max_seven_p_le':.05,'gdt299_reproduction_tolerance_bits_per_event':1e-9},'claim_ceiling':'Shared physical line-position function of frozen source-form renderer fields across opaque hosts only; no word morpheme linguistic function semantic role code value sound language meaning plaintext or translation.','source_strings_inspected':0,'page_host_substrings_mined':0,'semantic_assignments':0,'f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'capacity_sha256':sha(CAP),'freeze_manifest_sha256':sha(MAN),'method_sha256':sha(METHOD),'implementation':{Path(__file__).name:sha(Path(__file__))}};d['content_sha256']=rch(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'powered':sum(x['score_capacity']=='POWERED' for x in caps),'null_variable':sum(x['null_capacity']=='VARIABLE' for x in caps),'voynich':next(x for x in caps if x['control_id']=='VOYNICH_REFERENCE')},sort_keys=True))
if __name__=='__main__':main()
