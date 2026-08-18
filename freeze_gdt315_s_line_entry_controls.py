#!/usr/bin/env python3
"""Freeze powered controls for unchanged GDT314 instrument."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';VMS=R/'gdt314_frozen_panel.tsv';METHOD=R/'GDT315_S_LINE_ENTRY_CONTROL_CALIBRATION_METHOD.md';PANEL=R/'gdt315_frozen_panel.tsv';CAP=R/'gdt315_capacity.tsv';DESIGN=R/'gdt315_design.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 events=read(SOURCE);assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in events);groups=defaultdict(list)
 for x in events:
  if x['control_id']!='VOYNICH_REFERENCE':groups[x['control_id']].append(x)
 out=[];cap=[]
 for panel,rows in sorted(groups.items()):
  cells=defaultdict(list)
  for x in rows:cells[(x['page_host'],x['local_frame'],x['inner_d'],x['right_family'],x['dy_closure'],x['b3'])].append(x)
  eligible={k:v for k,v in cells.items() if sum(x['wrapper']=='s' for x in v)>=2 and sum(x['wrapper']!='s' for x in v)>=2 and len({x['physical_folio'] for x in v if x['wrapper']=='s'})>=2 and len({x['physical_folio'] for x in v if x['wrapper']!='s'})>=2};n=sum(map(len,eligible.values()));s=sum(x['wrapper']=='s' for v in eligible.values() for x in v);folios=len({x['physical_folio'] for v in eligible.values() for x in v});powered=len(eligible)>=5 and n>=100 and folios>=5 and s>=20
  cap.append({'panel':panel,'cells':len(eligible),'events':n,'s_events':s,'folios':folios,'powered':int(powered)})
  if powered:
   for key,rr in eligible.items():
    cid=hashlib.sha256((panel+'|CELL|'+'|'.join(key)).encode()).hexdigest()[:20]
    for x in rr:out.append({'panel':panel,'event_id_sha256':hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20],'cell_id':cid,'physical_folio':x['physical_folio'],'page':x['page'],'locus':x['locus'],'section':x['section'],'register':x['register'],'line_first':int(x['group_index']=='1'),'s_choice_withheld':'WITHHELD_UNTIL_SCORING'})
 # Voynich rows are exactly the already frozen disjoint GDT314 panel.
 for x in read(VMS):out.append({'panel':'VOYNICH_REFERENCE','event_id_sha256':x['event_id_sha256'],'cell_id':x['cell_id'],'physical_folio':x['physical_folio'],'page':x['page'],'locus':x['locus'],'section':x['section'],'register':x['register'],'line_first':x['line_first'],'s_choice_withheld':'WITHHELD_UNTIL_SCORING'})
 cap.append({'panel':'VOYNICH_REFERENCE','cells':15,'events':344,'s_events':35,'folios':78,'powered':1});out.sort(key=lambda x:(x['panel'],x['cell_id'],x['physical_folio'],x['locus'],x['event_id_sha256']));write(PANEL,out);write(CAP,sorted(cap,key=lambda x:x['panel']));powered=sorted({x['panel'] for x in cap if int(x['powered'])});d={'schema':'GDT315_S_LINE_ENTRY_CONTROL_DESIGN_V1','status':'FROZEN_BEFORE_CONTROL_SCORING','powered_panels':powered,'eligibility':{'min_cells':5,'min_events':100,'min_folios':5,'min_s_events':20,'cell_min_s':2,'cell_min_non_s':2,'cell_min_s_folios':2,'cell_min_non_s_folios':2},'instrument':{'ridge':10.0,'fold':'LEAVE_ONE_PHYSICAL_FOLIO_OUT','models':['CELL','CELL_LINE_START'],'null_worlds':8192,'null_seed':31520260818,'null_strata':'CELL_X_REGISTER','null_scope':'FIXED_CROSSFIT_ALIGNMENT_DIAGNOSTIC'},'classification':{'enriched':'VOYNICH_RANK1_GAIN_AND_DELTA','non_specific':'AT_LEAST_TWO_CONTROLS_GAIN_GE_VOYNICH','otherwise':'MIXED'},'claim_ceiling':'Formal s line-entry calibration only; no shared linguistic function meaning sound language identity plaintext or translation.','f84':{'authorized':False,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (SOURCE,VMS,METHOD)},'outputs':{p.name:sha(p) for p in (PANEL,CAP)},'implementation':{Path(__file__).name:sha(Path(__file__))}};d['content_sha256']=can(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'powered':powered,'rows':len(out)},sort_keys=True))
if __name__=='__main__':main()
