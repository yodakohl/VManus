#!/usr/bin/env python3
"""Freeze disjoint q/NONE event cells without reading positional outcomes."""
import csv, hashlib, json
from collections import defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent; SOURCE=R/'gdt278_native_event_inventory.tsv'; OLD=R/'gdt303_pair_deltas.tsv'; RECENT=R/'gdt305_frozen_pairs.tsv'; METHOD=R/'GDT306_Q_POST_DY_ENTRY_METHOD.md'; PANEL=R/'gdt306_frozen_event_panel.tsv'; CAP=R/'gdt306_capacity.tsv'; DESIGN=R/'gdt306_design.json'
CELL=('page_host','local_frame','inner_d','right_family','dy_closure','b3','register','section','currier','hand')
ALLOWED={'observation_id','page','locus','physical_folio','group_count','control_id','wrapper','source_surface_sha256',*CELL}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows,fields):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 used={v for p in (OLD,RECENT) for x in read(p) for v in (x['source_surface_sha256'],x['target_surface_sha256'])}; cells=defaultdict(lambda:defaultdict(list))
 with SOURCE.open(encoding='utf8',newline='') as h:
  reader=csv.DictReader(h,delimiter='\t');assert ALLOWED<=set(reader.fieldnames)
  for original in reader:
   x={k:original[k] for k in ALLOWED}
   if x['control_id']!='VOYNICH_REFERENCE' or int(x['group_count'])<2 or x['wrapper'] not in ('NONE','q') or x['source_surface_sha256'] in used:continue
   assert not x['page'].startswith('f84') and not x['locus'].startswith('f84')
   cells[tuple(x[k] for k in CELL)][x['wrapper']].append(x)
 panel=[]
 for key,d in sorted(cells.items()):
  if set(d)!= {'NONE','q'}:continue
  sid='G306S'+hashlib.sha256('|'.join(key).encode()).hexdigest()[:12].upper()
  for wrapper in ('NONE','q'):
   for x in sorted(d[wrapper],key=lambda z:z['observation_id']):
    panel.append({'stratum_id':sid,'observation_id':x['observation_id'],'page':x['page'],'locus':x['locus'],'wrapper':wrapper,'source_surface_sha256':x['source_surface_sha256'],'physical_folio':x['physical_folio'],'group_count':x['group_count'],**{k:x[k] for k in CELL}})
 assert len(panel)==98 and len({x['stratum_id'] for x in panel})==39
 write(PANEL,panel,list(panel[0])); variants=[]
 for name,extra in [('PRIMARY_BASE_CELL',()),('WITHIN_FOLIO',('physical_folio',)),('EXACT_GROUP_COUNT',('group_count',)),('WITHIN_FOLIO_EXACT_GROUP_COUNT',('physical_folio','group_count'))]:
  q=defaultdict(set)
  for x in panel:q[(x['stratum_id'],*(x[k] for k in extra))].add(x['wrapper'])
  keys={k for k,v in q.items() if v=={'NONE','q'}};events=sum((x['stratum_id'],*(x[k] for k in extra)) in keys for x in panel);variants.append({'variant':name,'matched_cells':len(keys),'events':events,'capacity':'PRIMARY' if name=='PRIMARY_BASE_CELL' else 'SENSITIVITY'})
 write(CAP,variants,list(variants[0]));design={'schema':'GDT306_Q_POST_DY_ENTRY_DESIGN_V1','status':'FROZEN_BEFORE_PRECEDING_GROUP_OUTCOME_SCORING','cell_fields':list(CELL),'excluded_surface_sources':[OLD.name,RECENT.name],'predictions':{'primary':'Q_MINUS_NONE_PRECEDED_BY_DY_DELTA_POSITIVE','secondary':'Q_MINUS_NONE_LINE_START_DELTA_NEGATIVE'},'decision':{'primary_one_sided_p_le':.05,'require_positive_primary':True,'require_positive_within_folio':True,'require_positive_exact_group_count':True},'null':'EXACT_WITHIN_CELL_WRAPPER_PERMUTATION','claim_ceiling':'Formal q-conditioned post-DY transition only; no grammar semantics sound language plaintext meaning or translation.','f84':{'authorized':False,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (SOURCE,OLD,RECENT,METHOD)},'outputs':{p.name:sha(p) for p in (PANEL,CAP)},'implementation':{Path(__file__).name:sha(Path(__file__))}};design['content_sha256']=can(design);DESIGN.write_text(json.dumps(design,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':design['status'],'strata':39,'events':98,'capacity':variants},sort_keys=True))
if __name__=='__main__':main()
