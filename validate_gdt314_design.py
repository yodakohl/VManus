#!/usr/bin/env python3
"""Validate GDT314 freeze."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;PANEL=R/'gdt314_frozen_panel.tsv';CAP=R/'gdt314_capacity.tsv';DESIGN=R/'gdt314_design.json';OUT=R/'gdt314_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');ck('content',stored==can(d));p=read(PANEL);c=read(CAP)[0];ck('capacity',(int(c['cells']),int(c['events']),int(c['s_events']),int(c['folios']))==(15,344,35,78));ck('unique',len(p)==len({x['event_id_sha256'] for x in p}));ck('withheld',{x['s_choice_withheld'] for x in p}=={'WITHHELD_UNTIL_SCORING'});ck('f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in p) and not any(d['f84'].values()));ck('hashes',all(d['inputs'][n]==sha(R/n) for n in d['inputs']) and all(d['outputs'][n]==sha(R/n) for n in d['outputs']));v={'schema':'GDT314_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'design_sha256':sha(DESIGN),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
