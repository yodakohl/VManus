#!/usr/bin/env python3
"""Freeze fresh s/non-s cells before GDT314 scoring."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PAIRS=R/'gdt303_pair_deltas.tsv';METHOD=R/'GDT314_FRESH_S_LINE_ENTRY_METHOD.md';PANEL=R/'gdt314_frozen_panel.tsv';CAP=R/'gdt314_capacity.tsv';DESIGN=R/'gdt314_design.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 used=set()
 for p in read(PAIRS):
  if p['operation'] in ('wrapper:ch>s','wrapper:d>s'):used|={p['source_surface_sha256'],p['target_surface_sha256']}
 events=[x for x in read(SOURCE) if x['control_id']=='VOYNICH_REFERENCE'];assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in events);cells=defaultdict(list)
 for x in events:
  if x['source_surface_sha256'] in used:continue
  key=(x['page_host'],x['local_frame'],x['inner_d'],x['right_family'],x['dy_closure'],x['b3']);cells[key].append(x)
 eligible={k:v for k,v in cells.items() if sum(x['wrapper']=='s' for x in v)>=2 and sum(x['wrapper']!='s' for x in v)>=2 and len({x['physical_folio'] for x in v if x['wrapper']=='s'})>=2 and len({x['physical_folio'] for x in v if x['wrapper']!='s'})>=2};out=[];truth={}
 for key,rows in eligible.items():
  cid=hashlib.sha256(('CELL|'+'|'.join(key)).encode()).hexdigest()[:20]
  for x in rows:
   eid=hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20];truth[eid]=int(x['wrapper']=='s');out.append({'event_id_sha256':eid,'cell_id':cid,'opaque_host_id_sha256':hashlib.sha256(key[0].encode()).hexdigest()[:20],'physical_folio':x['physical_folio'],'page':x['page'],'locus':x['locus'],'section':x['section'],'register':x['register'],'line_first':int(x['group_index']=='1'),'s_choice_withheld':'WITHHELD_UNTIL_SCORING'})
 out.sort(key=lambda x:(x['cell_id'],x['physical_folio'],x['locus'],x['event_id_sha256']));write(PANEL,out);cap=[{'cells':len(eligible),'events':len(out),'s_events':sum(truth.values()),'folios':len({x['physical_folio'] for x in out}),'powered_sections':'B|H|S','excluded_gdt303_surface_hashes':len(used)}];write(CAP,cap);d={'schema':'GDT314_FRESH_S_LINE_ENTRY_DESIGN_V1','status':'FROZEN_BEFORE_FRESH_S_SCORING','models':{'CELL':[],'CELL_LINE_START':['line_first']},'ridge':10.0,'fold':'LEAVE_ONE_PHYSICAL_FOLIO_OUT','null':{'worlds':8192,'seed':31420260818,'strata':'CELL_X_REGISTER','scope':'FIXED_CROSSFIT_PREDICTION_ALIGNMENT_DIAGNOSTIC'},'decision':{'gain_positive':True,'matched_delta_positive':True,'positive_coefficients_min':60,'positive_powered_sections_min':2,'alignment_p_le':.05},'forbidden':['ALL_GDT303_CH_D_S_SURFACES','same_group_renderer_as_predictor','host_glyphs','host_substrings'],'claim_ceiling':'Fresh-surface physical-line-entry tendency only; no morpheme POS meaning sound language plaintext or translation.','f84':{'authorized':False,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (SOURCE,PAIRS,METHOD)},'outputs':{p.name:sha(p) for p in (PANEL,CAP)},'implementation':{Path(__file__).name:sha(Path(__file__))}};d['content_sha256']=can(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'capacity':cap[0]},sort_keys=True))
if __name__=='__main__':main()
