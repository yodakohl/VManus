#!/usr/bin/env python3
"""Freeze domain-support cells for GDT307 without reading positions."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PAIR=R/'gdt303_pair_deltas.tsv';METHOD=R/'GDT307_RENDERER_OPERATION_DOMAIN_STABILITY_METHOD.md';FOLDS=R/'gdt307_frozen_domain_cells.tsv';CAP=R/'gdt307_capacity.tsv';DESIGN=R/'gdt307_design.json'
OPS=('wrapper:ch>s','wrapper:d>s','wrapper:NONE>q');DOMAINS=('section','register','currier','hand')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 pairs=[x for x in read(PAIR) if x['operation'] in OPS];support={d:defaultdict(lambda:defaultdict(int)) for d in DOMAINS};f84=0
 with SOURCE.open(encoding='utf8',newline='') as h:
  for x in csv.DictReader(h,delimiter='\t'):
   if x['control_id']!='VOYNICH_REFERENCE':continue
   f84+=x['page'].startswith('f84') or x['locus'].startswith('f84')
   for d in DOMAINS:support[d][(x['page_host'],x['source_surface_sha256'])][x[d]]+=1
 assert not f84;out=[]
 for p in pairs:
  pid='G307P'+hashlib.sha256('|'.join(p[k] for k in ('operation','page_host','source_surface_sha256','target_surface_sha256')).encode()).hexdigest()[:12].upper()
  for domain in DOMAINS:
   a=support[domain][(p['page_host'],p['source_surface_sha256'])];b=support[domain][(p['page_host'],p['target_surface_sha256'])]
   for held in sorted(set(a)|set(b)):
    ah=a[held];bh=b[held];at=sum(v for k,v in a.items() if k!=held);bt=sum(v for k,v in b.items() if k!=held)
    if min(ah,bh,at,bt)<2:continue
    out.append({'cell_id':'G307C'+hashlib.sha256(f'{pid}|{domain}|{held}'.encode()).hexdigest()[:12].upper(),'pair_id':pid,'operation':p['operation'],'page_host':p['page_host'],'source_surface_sha256':p['source_surface_sha256'],'target_surface_sha256':p['target_surface_sha256'],'domain_type':domain,'held_domain':held,'source_train_events':at,'target_train_events':bt,'source_held_events':ah,'target_held_events':bh})
 out.sort(key=lambda x:(x['operation'],x['domain_type'],x['held_domain'],x['page_host'],x['pair_id']));write(FOLDS,out);cap=[]
 for op in OPS:
  for d in DOMAINS:
   q=[x for x in out if x['operation']==op and x['domain_type']==d];cap.append({'operation':op,'domain_type':d,'cells':len(q),'hosts':len({x['page_host'] for x in q}),'held_domains':len({x['held_domain'] for x in q}),'held_events':sum(int(x['source_held_events'])+int(x['target_held_events']) for x in q),'capacity':'POWERED' if len(q)>=8 and len({x['page_host'] for x in q})>=4 else 'DESCRIPTIVE'})
 write(CAP,cap);design={'schema':'GDT307_RENDERER_OPERATION_DOMAIN_STABILITY_DESIGN_V1','status':'FROZEN_BEFORE_DOMAIN_POSITION_SCORING','operations':list(OPS),'domain_types':list(DOMAINS),'minimum_events_each_form_inside':2,'minimum_events_each_form_outside':2,'score':'EQUAL_HOST_DOMAIN_MEAN_TRAIN_HELD_POSITION_DELTA_DOT','null_worlds':8192,'null_seed':30720260818,'decision':{'required_domains':['section','hand'],'minimum_direction_accuracy':.60,'max12_p_le':.05},'provenance':'POST_SELECTION_STABILITY_OF_GDT303_OPERATIONS','claim_ceiling':'Selected formal renderer-operation domain stability only; no grammar semantics sound language plaintext meaning or translation.','f84':{'authorized':False,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (SOURCE,PAIR,METHOD)},'outputs':{p.name:sha(p) for p in (FOLDS,CAP)},'implementation':{Path(__file__).name:sha(Path(__file__))}};design['content_sha256']=can(design);DESIGN.write_text(json.dumps(design,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':design['status'],'cells':len(out),'capacity':cap},sort_keys=True))
if __name__=='__main__':main()
