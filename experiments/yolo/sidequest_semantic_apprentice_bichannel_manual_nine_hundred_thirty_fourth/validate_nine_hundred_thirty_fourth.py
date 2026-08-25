#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
r=read('PASS934_16_APPRENTICE_RULES.tsv');e=read('PASS934_30_BICHANNEL_EXERCISES.tsv')
c=[('rules_16',len(r)==16,len(r)),('exercises_30',len(e)==30,len(e)),('surfaces_unique',len({x['surface'] for x in e})==30,30),('same_recipes',all(x['component_recipe'] and x['abstract_core_de']!='SURFACE_ALLOGRAPH_RECIPES_DIFFER' for x in e),'recipes'),('two_readings',all(x['workshop_reading_de']!=x['diagram_reading_de'] for x in e),'readings'),('sealed_absent',not any(z in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS934_*') if q.suffix in ('.tsv','.md') for z in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS934_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirty_fourth.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS934_*') if q.suffix in ('.tsv','.md')};c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':v,'detail':z} for n,v,z in c]};(H/'PASS934_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
