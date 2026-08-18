#!/usr/bin/env python3
"""Freeze GDT294 before scoring."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;METHOD=R/'GDT294_HOST_POSITION_RENDERER_TUPLE_METHOD.md';DESIGN=R/'gdt294_design.json';CAP=R/'gdt294_capacity.tsv';MAN=R/'gdt294_freeze_manifest.tsv';PANELS=['AUGSBURG_ACCOUNTS_1402_1424','ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND','LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE'];ART=['gdt293_result.json','gdt293_validation.json','gdt291_result.json','gdt286_result.json','gdt278_native_event_inventory.tsv','gdt288_result.json']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rr):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rr[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rr)
def main():
 native=rows(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);cap=[]
 for p in PANELS:
  ev=[x for x in native if x['control_id']==p];hf=defaultdict(set)
  for x in ev:hf[x['page_host']].add(x['physical_folio'])
  eligible=[x for x in ev if len(hf[x['page_host']])>=2];hp=defaultdict(set)
  for x in eligible:hp[x['page_host'],x['within_field_position']].add(x['physical_folio'])
  cap.append({'control_id':p,'events':len(ev),'exact_host_eligible_events':len(eligible),'cross_folio_host_position_cells':sum(len(v)>=2 for v in hp.values()),'host_position_supported_events':sum(len(hp[x['page_host'],x['within_field_position']]-{x['physical_folio']})>0 for x in eligible)})
 write(CAP,cap)
 with MAN.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,['artifact','frozen_sha256'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART])
 d={'schema':'GDT294_HOST_POSITION_RENDERER_TUPLE_DESIGN_V1','status':'FROZEN_BEFORE_GDT294_SCORING','panels':PANELS,'events_per_panel':8448,'eligibility':'EXACT_HOST_OCCURS_ON_AT_LEAST_TWO_PHYSICAL_FOLIOS','outcome':'EXACT_WRAPPER_FRAME_INNERD_RIGHT_DY_B3_TUPLE','models':['LAYOUT_CONTEXT','BOUNDARY_CONTEXT','EXACT_HOST','HOST_X_POSITION','HOST_X_RECORD_SLOT'],'primary_effect':'EXACT_HOST_MINUS_HOST_X_POSITION_BITS_PER_EVENT','secondary_effect':'HOST_X_POSITION_MINUS_HOST_X_RECORD_SLOT_BITS_PER_EVENT','layout_context':['section','currier','hand','register','within_field_position','record_ordinal_bucket','field_ordinal_bucket','physical_group_position','host_length'],'boundary_context':['line_close','paragraph_close','known_label_renderer'],'primary_prior_mass':11.0,'voynich_prior_sensitivities':[5.0,22.0],'primary_split':'HELD_PHYSICAL_FOLIO','voynich_transfer_sensitivities':['HELD_SECTION','HELD_HAND'],'null_worlds':64,'null_seed':'GDT294_HELD_HOST_POSITION_RENDERER_ALIGNMENT','null_operation':'PERMUTE_RENDERER_WITHIN_EXACT_FOLIO_HOST_RECORD_BOUNDARY_STRATA_EXCLUDING_WITHIN_FIELD_POSITION_AFTER_PREDICTIONS_FREEZE','decision':{'support':'HOST_POSITION_RENDERER_TUPLE_SUPPORTED','fail':'HOST_POSITION_RENDERER_TUPLE_WEAK_OR_LOCAL','minimum_positive_folios':60,'require_section_and_hand_positive':True,'alpha':.05},'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'claim_ceiling':'Opaque host-specific positional renderer distribution only; no productive morphology lexical class word code value language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'capacity_sha256':sha(CAP),'freeze_manifest_sha256':sha(MAN),'method_sha256':sha(METHOD),'implementation':{'freeze_gdt294_host_position_renderer_tuple.py':sha(Path(__file__))}};d['content_sha256']=csha(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'voynich_capacity':next(x for x in cap if x['control_id']=='VOYNICH_REFERENCE')},sort_keys=True))
if __name__=='__main__':main()
