#!/usr/bin/env python3
"""Validate the GDT140 fixed five-by-five assignment orbit."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;I=R/'gdt140_herbal_relation_inventory.tsv';A=R/'gdt140_assignment_orbit.tsv';P=R/'gdt140_prediction.json';O=R/'gdt140_prediction_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=list(csv.DictReader(I.open(encoding='utf8'),delimiter='\t'));a=list(csv.DictReader(A.open(encoding='utf8'),delimiter='\t'));p=json.loads(P.read_text());checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
ck('status',p['status']=='FROZEN_UNTOUCHED_5X5_RELATION_ASSIGNMENT_BEFORE_FORMAL_SCORING');ck('ids',[x['relation_id'] for x in rows]==['MHI002','MHI003','MHI004','MHI006','MHI007']);ck('pages',len({x['source_page'] for x in rows})==len({x['target_page'] for x in rows})==5 and len({x[k] for x in rows for k in ('source_page','target_page')})==10);ck('metadata',all(x['panel_class']=='CLEAN_HA_HAND1_5X5' for x in rows));ck('orbit',len(a)==120 and Counter(x['is_true'] for x in a)==Counter({'0':119,'1':1}));ck('unique',len({x['mapping'] for x in a})==120);ck('f84',not any('f84' in x['mapping'] for x in a) and p['f84']['all_f84_rows_rejected_before_retention']);ck('hashes',all(sha(R/n)==d for n,d in {**p['inputs'],**p['implementation'],**p['outputs']}.items()));v={'schema':'GDT140_PREDICTION_VALIDATION_V1','status':'PASS_EXACT_5X5_FREEZE_AND_ORBIT','checks':len(checks),'passed':sum(x['pass'] for x in checks),'prediction_sha256':sha(P),'validator_sha256':sha(Path(__file__)),'check_rows':checks};O.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':v['status'],'checks':v['checks']},sort_keys=True))
