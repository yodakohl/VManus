#!/usr/bin/env python3
"""Validate the score-blind GDT307 domain-cell freeze."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;DESIGN=R/'gdt307_design.json';FOLDS=R/'gdt307_frozen_domain_cells.tsv';CAP=R/'gdt307_capacity.tsv';OUT=R/'gdt307_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');ck('content_hash',stored==can(d));ck('status',d['status']=='FROZEN_BEFORE_DOMAIN_POSITION_SCORING');rows=read(FOLDS);ck('unique_cells',len(rows)==len({x['cell_id'] for x in rows}));ck('support_minimum',all(min(int(x[k]) for k in ('source_train_events','target_train_events','source_held_events','target_held_events'))>=2 for x in rows));counts=Counter((x['operation'],x['domain_type']) for x in rows);expected={('wrapper:NONE>q','section'):75,('wrapper:NONE>q','register'):76,('wrapper:NONE>q','currier'):36,('wrapper:NONE>q','hand'):70,('wrapper:ch>s','section'):13,('wrapper:ch>s','register'):13,('wrapper:ch>s','currier'):14,('wrapper:ch>s','hand'):15,('wrapper:d>s','section'):19,('wrapper:d>s','register'):19,('wrapper:d>s','currier'):14,('wrapper:d>s','hand'):19};ck('capacity_counts',counts==expected);ck('input_hashes',all(d['inputs'][n]==sha(R/n) for n in d['inputs']));ck('output_hashes',all(d['outputs'][n]==sha(R/n) for n in d['outputs']));ck('f84_flags',not any(d['f84'].values()));v={'schema':'GDT307_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'domain_cells':len(rows),'design_sha256':sha(DESIGN),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'cells':len(rows)},sort_keys=True))
if __name__=='__main__':main()
