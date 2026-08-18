#!/usr/bin/env python3
"""Freeze GDT293 design and score-blind capacity counts."""
from __future__ import annotations
import csv, hashlib, json
from collections import defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
METHOD=R/'GDT293_EXACT_HOST_RENDERER_COMPLETION_METHOD.md'
DESIGN=R/'gdt293_design.json'; CAP=R/'gdt293_capacity.tsv'; MAN=R/'gdt293_freeze_manifest.tsv'
PANELS=['AUGSBURG_ACCOUNTS_1402_1424','ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND','LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE']
ART=['gdt292_result.json','gdt292_validation.json','gdt288_result.json','gdt286_result.json','gdt165_result.json','gdt278_native_event_inventory.tsv']
COMP=['wrapper','local_frame','inner_d','right_family','dy_closure','b3']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rr):
 with Path(p).open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,rr[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rr)
def main():
 native=read(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native)
 capacity=[]
 for panel in PANELS:
  ev=[x for x in native if x['control_id']==panel];assert len(ev)==8448
  fol=defaultdict(set)
  for x in ev:fol[x['page_host']].add(x['physical_folio'])
  eligible=[x for x in ev if len(fol[x['page_host']])>=2]
  capacity.append({'control_id':panel,'events':len(ev),'folios':len({x['physical_folio'] for x in ev}),'exact_hosts':len(fol),'cross_folio_hosts':sum(len(v)>=2 for v in fol.values()),'eligible_events':len(eligible),'joint_renderer_classes':len({'|'.join(x[k] for k in COMP) for x in ev})})
 write(CAP,capacity)
 with MAN.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,['artifact','frozen_sha256'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART])
 d={'schema':'GDT293_EXACT_HOST_RENDERER_COMPLETION_DESIGN_V1','status':'FROZEN_BEFORE_GDT293_SCORING','panels':PANELS,'events_per_panel':8448,'eligibility':'EXACT_HOST_OCCURS_ON_AT_LEAST_TWO_PHYSICAL_FOLIOS','primary_outcome':'EXACT_WRAPPER_FRAME_INNERD_RIGHT_DY_B3_TUPLE','component_diagnostics':COMP,'models':['LAYOUT_CONTEXT','EXACT_HOST'],'layout_context':['section','currier','hand','register','within_field_position','record_ordinal_bucket','field_ordinal_bucket','physical_group_position','host_length'],'primary_prior_mass':11.0,'voynich_prior_sensitivities':[5.0,22.0],'primary_split':'HELD_PHYSICAL_FOLIO','voynich_transfer_sensitivities':['HELD_SECTION','HELD_HAND'],'sequential_host_features':0,'host_glyph_or_substring_features':0,'null_worlds':64,'null_seed':'GDT293_HELD_RENDERER_ALIGNMENT','null_operation':'PERMUTE_JOINT_RENDERER_TUPLES_WITHIN_EXACT_FOLIO_LAYOUT_STRATA_AFTER_PREDICTIONS_FREEZE','decision':{'support':'EXACT_HOST_RENDERER_COMPLETION_SUPPORTED','fail':'EXACT_HOST_RENDERER_COMPLETION_WEAK_OR_LOCAL','minimum_positive_components':4,'minimum_positive_folios':60,'require_section_and_hand_positive':True,'alpha':.05},'prior_next_host_result':'GDT165_NEGATIVE_NOT_RERUN','new_corpora':0,'new_architectures':0,'semantic_assignments':0,'claim_ceiling':'Opaque exact-host to parser-defined same-group renderer completion only; no lexical identity word code value morpheme sound language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'capacity_sha256':sha(CAP),'freeze_manifest_sha256':sha(MAN),'method_sha256':sha(METHOD),'implementation':{'freeze_gdt293_exact_host_renderer_completion.py':sha(Path(__file__))}}
 d['content_sha256']=csha(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'voynich_capacity':next(x for x in capacity if x['control_id']=='VOYNICH_REFERENCE')},sort_keys=True))
if __name__=='__main__':main()
