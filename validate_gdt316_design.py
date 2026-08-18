#!/usr/bin/env python3
"""Validate GDT316 freeze."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;PANEL=R/'gdt316_frozen_panel.tsv';CAP=R/'gdt316_capacity.tsv';DESIGN=R/'gdt316_design.json';OUT=R/'gdt316_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 c=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  c.append(n)
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');ck('content',stored==can(d));p=read(PANEL);cap=read(CAP)[0];ck('capacity',(int(cap['cells']),int(cap['events']),int(cap['q_events']),int(cap['folios']))==(36,450,137,82));ck('unique',len(p)==len({x['event_id_sha256'] for x in p}));ck('withheld',{x['q_choice_withheld'] for x in p}=={'WITHHELD_UNTIL_SCORING'});ck('f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in p) and not any(d['f84'].values()));ck('hashes',all(d['inputs'][n]==sha(R/n) for n in d['inputs']) and all(d['outputs'][n]==sha(R/n) for n in d['outputs']));v={'schema':'GDT316_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks':c,'design_sha256':sha(DESIGN),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()
