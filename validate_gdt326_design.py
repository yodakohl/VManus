#!/usr/bin/env python3
"""Validate the frozen GDT326 novel-edge panel."""
import csv, hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parent; OUT=R/'gdt326_design_validation.json'; COORD=("local_frame","inner_d","right_family","dy_closure","b3")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v): return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(n):
 with (R/n).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def check(n,c):
  if not c: raise AssertionError(n)
  checks.append(n)
 d=json.loads((R/'gdt326_design.json').read_text()); stored=d.pop('content_sha256');check('content',stored==can(d));rows=[x for x in read('gdt278_native_event_inventory.tsv') if x['control_id']=='VOYNICH_REFERENCE'];check('f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));expected=[]
 for f in sorted({x['physical_folio'] for x in rows}):
  tr=[x for x in rows if x['physical_folio']!=f];te=[x for x in rows if x['physical_folio']==f];H={x['page_host'] for x in tr};C={tuple(x[k] for k in COORD) for x in tr};E={(x['page_host'],)+tuple(x[k] for k in COORD) for x in tr}
  expected += [hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20] for x in te if x['page_host'] in H and tuple(x[k] for k in COORD) in C and (x['page_host'],)+tuple(x[k] for k in COORD) not in E]
 panel=read('gdt326_frozen_panel.tsv');check('ids',sorted(x['event_id_sha256'] for x in panel)==sorted(expected));check('capacity',len(panel)==315 and len({x['physical_folio'] for x in panel})==76);check('withheld',all(x['target_coordinate']=='WITHHELD_UNTIL_SCORING' for x in panel));check('models',d['models']==['REGISTER_TABLE','HOST_TABLE','HOST_FACTORIAL','HOST_FACTORIAL_REGISTER']);check('hashes',all(d['inputs'][n]==sha(R/n) for n in d['inputs']) and all(d['outputs'][n]==sha(R/n) for n in d['outputs']));v={'schema':'GDT326_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'design_sha256':sha(R/'gdt326_design.json'),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
