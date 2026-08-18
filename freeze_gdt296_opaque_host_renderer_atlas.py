#!/usr/bin/env python3
"""Freeze GDT296 atlas population and thresholds."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;METHOD=R/'GDT296_OPAQUE_HOST_RENDERER_ATLAS_METHOD.md';DESIGN=R/'gdt296_design.json';POP=R/'gdt296_population.tsv';MAN=R/'gdt296_freeze_manifest.tsv';ART=['gdt295_result.json','gdt295_validation.json','gdt294_result.json','gdt293_result.json','gdt278_native_event_inventory.tsv']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 r=[x for x in rows(R/'gdt278_native_event_inventory.tsv') if x['control_id']=='VOYNICH_REFERENCE'];assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in r);by=defaultdict(list)
 for x in r:by[x['page_host']].append(x)
 pop=[{'page_host':h,'events':len(v),'folios':len({x['physical_folio'] for x in v}),'sections':len({x['section'] for x in v}),'hands':len({x['hand'] for x in v})} for h,v in by.items() if len(v)>=20 and len({x['physical_folio'] for x in v})>=5];pop.sort(key=lambda x:(-x['events'],x['page_host']))
 with POP.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,pop[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(pop)
 with MAN.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,['artifact','frozen_sha256'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART])
 d={'schema':'GDT296_OPAQUE_HOST_RENDERER_ATLAS_DESIGN_V1','status':'FROZEN_BEFORE_GDT296_ATLAS_SCORING','population':{'minimum_events':20,'minimum_physical_folios':5,'hosts':len(pop),'events':sum(x['events'] for x in pop)},'outcome':'EXACT_WRAPPER_FRAME_INNERD_RIGHT_DY_B3_TUPLE','models':['HOST_CANONICAL','HOST_X_POSITION'],'split':'HELD_PHYSICAL_FOLIO','alpha':.5,'position_prior_mass':11.0,'labels':{'canonical':{'top1_min':.70,'entropy_max_bits':1.0},'position_conditioned':{'top1_min':.70,'top1_improvement_min':.10},'otherwise':'VARIABLE_RENDERER'},'p_values':0,'host_substrings_mined':0,'semantic_assignments':0,'claim_ceiling':'Held-folio parser-defined renderer predictability for opaque host IDs only; no lexicality word meaning code value sound language plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'population_sha256':sha(POP),'freeze_manifest_sha256':sha(MAN),'method_sha256':sha(METHOD),'implementation':{'freeze_gdt296_opaque_host_renderer_atlas.py':sha(Path(__file__))}};d['content_sha256']=csha(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'hosts':len(pop),'events':sum(x['events'] for x in pop)},sort_keys=True))
if __name__=='__main__':main()
