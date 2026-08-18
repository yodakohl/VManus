#!/usr/bin/env python3
"""Freeze GDT295 and its line-safe online capacity."""
from __future__ import annotations
import csv,hashlib,itertools,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;METHOD=R/'GDT295_ONLINE_PAGE_LOCAL_RENDERER_METHOD.md';DESIGN=R/'gdt295_design.json';CAP=R/'gdt295_capacity.tsv';MAN=R/'gdt295_freeze_manifest.tsv';PANELS=['AUGSBURG_ACCOUNTS_1402_1424','ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND','LATIN_SCHOLASTIC_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','LATIN_15C_GRAPHEMATIC','VOYNICH_REFERENCE'];ART=['gdt294_result.json','gdt294_validation.json','gdt293_result.json','gdt082_result.json','gdt278_native_event_inventory.tsv','gdt288_result.json']
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
  seen=set();eligible=[]
  for locus,g in itertools.groupby(ev,key=lambda x:x['locus']):
   line=list(g)
   for x in line:
    if len(hf[x['page_host']])>=2 and (x['page'],x['page_host']) in seen:eligible.append(x)
   for x in line:seen.add((x['page'],x['page_host']))
  cap.append({'control_id':p,'events':len(ev),'eligible_events':len(eligible),'eligible_pages':len({x['page'] for x in eligible}),'eligible_folios':len({x['physical_folio'] for x in eligible}),'eligible_hosts':len({x['page_host'] for x in eligible}),'capacity_status':'POWERED' if eligible else 'UNSCORED_ZERO_ONLINE_CAPACITY'})
 write(CAP,cap)
 with MAN.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,['artifact','frozen_sha256'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART])
 powered=[x['control_id'] for x in cap if x['eligible_events']>0];unscored=[x['control_id'] for x in cap if x['eligible_events']==0];d={'schema':'GDT295_ONLINE_PAGE_LOCAL_RENDERER_DESIGN_V1','status':'FROZEN_BEFORE_GDT295_SCORING','panels':PANELS,'powered_panels':powered,'unscored_zero_capacity_panels':unscored,'event_order':'PUBLISHED_GDT278_ROW_ORDER_GROUPED_BY_CONSECUTIVE_LOCUS','same_line_update_forbidden':True,'eligibility':'EXACT_HOST_OUTSIDE_FOLIO_AND_PRIOR_SAME_PAGE_PHYSICAL_LINE','outcome':'EXACT_WRAPPER_FRAME_INNERD_RIGHT_DY_B3_TUPLE','models':['CROSS_FOLIO_HOST_X_POSITION','PAGE_LOCAL_HOST','PAGE_LOCAL_HOST_X_POSITION'],'primary_effect':'CROSS_FOLIO_MINUS_PAGE_LOCAL_HOST_X_POSITION_BITS_PER_EVENT','primary_prior_mass':11.0,'voynich_prior_sensitivities':[5.0,22.0],'null_worlds':64,'null_seed':'GDT295_ONLINE_PAGE_RENDERER_ALIGNMENT','null_operation':'PERMUTE_ELIGIBLE_RENDERER_OUTCOMES_WITHIN_EXACT_PAGE_HOST_AFTER_ALL_ONLINE_PREDICTIONS_FREEZE','decision':{'support':'PAGE_LOCAL_RENDERER_ADAPTATION_SUPPORTED','fail':'PAGE_LOCAL_RENDERER_ADAPTATION_WEAK_OR_LOCAL','minimum_positive_pages':100,'expected_voynich_pages':153,'minimum_positive_sections':4,'expected_voynich_sections':6,'require_both_prior_sensitivities_positive':True,'alpha':.05},'new_corpora':0,'new_architectures':0,'semantic_assignments':0,'claim_ceiling':'Online page-local parser-defined renderer adaptation only; no page vocabulary meaning lexical identity code value word language plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'capacity_sha256':sha(CAP),'freeze_manifest_sha256':sha(MAN),'method_sha256':sha(METHOD),'implementation':{'freeze_gdt295_online_page_local_renderer.py':sha(Path(__file__))}};d['content_sha256']=csha(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'powered':powered,'voynich_capacity':next(x for x in cap if x['control_id']=='VOYNICH_REFERENCE')},sort_keys=True))
if __name__=='__main__':main()
