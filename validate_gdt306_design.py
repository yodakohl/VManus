#!/usr/bin/env python3
"""Independently rebuild and validate the score-blind GDT306 freeze."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';OLD=R/'gdt303_pair_deltas.tsv';RECENT=R/'gdt305_frozen_pairs.tsv';PANEL=R/'gdt306_frozen_event_panel.tsv';CAP=R/'gdt306_capacity.tsv';DESIGN=R/'gdt306_design.json';OUT=R/'gdt306_design_validation.json';CELL=('page_host','local_frame','inner_d','right_family','dy_closure','b3','register','section','currier','hand')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
checks=[]
def ck(n,v):
 if not v:raise AssertionError(n)
 checks.append(n)
def main():
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');ck('design_content_hash',stored==can(d));ck('design_status',d['status']=='FROZEN_BEFORE_PRECEDING_GROUP_OUTCOME_SCORING');used={v for p in (OLD,RECENT) for x in read(p) for v in (x['source_surface_sha256'],x['target_surface_sha256'])};cells=defaultdict(lambda:defaultdict(list));f84=0
 with SOURCE.open(encoding='utf8',newline='') as h:
  for x in csv.DictReader(h,delimiter='\t'):
   if x['control_id']!='VOYNICH_REFERENCE' or int(x['group_count'])<2 or x['wrapper'] not in ('NONE','q') or x['source_surface_sha256'] in used:continue
   f84+=x['page'].startswith('f84') or x['locus'].startswith('f84');cells[tuple(x[k] for k in CELL)][x['wrapper']].append(x)
 expected=[]
 for key,m in sorted(cells.items()):
  if set(m)!= {'NONE','q'}:continue
  sid='G306S'+hashlib.sha256('|'.join(key).encode()).hexdigest()[:12].upper()
  for w in ('NONE','q'):
   for x in sorted(m[w],key=lambda z:z['observation_id']):expected.append((sid,x['observation_id'],x['page'],x['locus'],w,x['source_surface_sha256'],x['physical_folio'],x['group_count'],*key))
 actual=[tuple(x[k] for k in ('stratum_id','observation_id','page','locus','wrapper','source_surface_sha256','physical_folio','group_count',*CELL)) for x in read(PANEL)];ck('exact_panel',actual==expected);ck('panel_counts',len(actual)==98 and len({x[0] for x in actual})==39);ck('f84_zero',f84==0 and not any(x[2].startswith('f84') or x[3].startswith('f84') for x in actual));ck('surface_disjoint',not any(x[5] in used for x in actual));cap=read(CAP);ck('capacity_exact',[(int(x['matched_cells']),int(x['events'])) for x in cap]==[(39,98),(11,22),(11,23),(5,10)]);ck('input_hashes',all(d['inputs'][n]==sha(R/n) for n in d['inputs']));ck('output_hashes',all(d['outputs'][n]==sha(R/n) for n in d['outputs']));out={'schema':'GDT306_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'design_sha256':sha(DESIGN),'f84_rows':0};out['content_sha256']=can(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'events':len(actual)},sort_keys=True))
if __name__=='__main__':main()
