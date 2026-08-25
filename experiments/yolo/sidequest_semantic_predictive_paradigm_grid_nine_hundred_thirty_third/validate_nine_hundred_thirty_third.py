#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
g=read('PASS933_112_PARADIGM_CELLS.tsv');p=read('PASS933_MISSING_CELL_PREDICTIONS.tsv')
c=[('cells_112',len(g)==112,len(g)),('recipes_unique',len({r['component_recipe'] for r in g})==112,112),('predictions_partition',len(p)+sum(r['status']=='OBSERVED' for r in g)==112,len(p)),('chekedy',any(r['component_recipe']=='CHK+E+DY' and r['candidate_bare_surface']=='chekedy' and r['status']!='OBSERVED' for r in g),'CHK+E+DY'),('all_semantic',all(r['workshop_prediction_de'] and r['owner_address_prediction_de'] for r in g),'values'),('sealed_absent',not any(z in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS933_*') if q.suffix in ('.tsv','.md') for z in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS933_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirty_third.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS933_*') if q.suffix in ('.tsv','.md')};c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':v,'detail':z} for n,v,z in c]};(H/'PASS933_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
