#!/usr/bin/env python3
"""Integrity/capacity validation for the GDT139 freeze."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent; I=R/'gdt139_identification_token_inventory.tsv'; P=R/'gdt139_prediction.json'; O=R/'gdt139_prediction_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=list(csv.DictReader(I.open(encoding='utf8'),delimiter='\t')); p=json.loads(P.read_text()); checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
ck('status',p['status']=='FROZEN_NOISY_EXTERNAL_TOKEN_PANEL_BEFORE_FORMAL_SCORING');ck('rows',len(rows)==173 and Counter(r['panel'] for r in rows)==Counter({'ELV':81,'THP':92}));ck('unique',len({(r['panel'],r['page']) for r in rows})==173);ck('folios',all(r['physical_folio'] and not r['page'].startswith('f84') for r in rows));ck('tokens',len(p['eligible_tokens']['ELV'])==6 and len(p['eligible_tokens']['THP'])==13);ck('capacity',all(sum(int(r[f'{s}_{t.upper()}']) for r in rows if r['panel']==s)>=2 for s,ts in p['eligible_tokens'].items() for t in ts));ck('other_panel_zero',all(all(int(r[c])==0 for c in p['eligible_columns'] if not c.startswith(r['panel']+'_')) for r in rows));ck('hashes',all(sha(R/n)==d for n,d in {**p['inputs'],**p['implementation'],**p['outputs']}.items()));ck('f84',p['f84']['all_f84_rows_rejected_before_retention'] and not p['f84']['new_f84r_access']);v={'schema':'GDT139_PREDICTION_VALIDATION_V1','status':'PASS_FREEZE_INTEGRITY_AND_CAPACITY','checks':len(checks),'passed':sum(x['pass'] for x in checks),'prediction_sha256':sha(P),'validator_sha256':sha(Path(__file__)),'check_rows':checks};O.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':v['status'],'checks':v['checks']},sort_keys=True))
