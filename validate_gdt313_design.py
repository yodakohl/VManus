#!/usr/bin/env python3
"""Validate GDT313 frozen capacity and split."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;PANEL=R/'gdt313_frozen_panel.tsv';CAP=R/'gdt313_capacity.tsv';DESIGN=R/'gdt313_design.json';OUT=R/'gdt313_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');ck('content',stored==can(d));p=read(PANEL);c=read(CAP);ck('capacity',len(p)==476 and sum(int(x['training_events']) for x in c)==273 and sum(int(x['test_events']) for x in c)==203 and len(c)==2);ck('choice_withheld',{x['choice_withheld'] for x in p}=={'WITHHELD_UNTIL_SCORING'});ck('split',all((int(hashlib.sha256(f"GDT311_SPLIT_V1|{x['physical_folio']}".encode()).hexdigest()[:8],16)%3==0)==(x['split']=='TEST') for x in p));ck('unique',len(p)==len({x['event_id_sha256'] for x in p}));ck('f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in p) and not any(d['f84'].values()));ck('hashes',all(d['inputs'][n]==sha(R/n) for n in d['inputs']) and all(d['outputs'][n]==sha(R/n) for n in d['outputs']));v={'schema':'GDT313_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'design_sha256':sha(DESIGN),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
