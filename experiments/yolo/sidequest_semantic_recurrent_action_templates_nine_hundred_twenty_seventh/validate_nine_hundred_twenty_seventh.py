#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
t=read('PASS927_22_ACTION_TEMPLATES.tsv');o=read('PASS927_TEMPLATE_OCCURRENCES.tsv')
c=[('templates_22',len(t)==22,len(t)),('occ_unique',len(o)==len({r['occurrence_id'] for r in o}),len(o)),('all_templates_used',set(r['template_id'] for r in t)==set(r['template_id'] for r in o),len(set(r['template_id'] for r in o))),('broad_templates',sum(int(r['pages'])>=4 for r in t)>=18,sum(int(r['pages'])>=4 for r in t)),('sealed_absent',not any(x in p.read_text(encoding='utf-8',errors='ignore') for p in H.glob('PASS927_*') if p.suffix in ('.tsv','.md') for x in ('f84','f84r')),'sealed')]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in H.glob('PASS927_*') if p.suffix in ('.tsv','.md')}
subprocess.run([sys.executable,str(H/'build_nine_hundred_twenty_seventh.py')],check=True)
after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in H.glob('PASS927_*') if p.suffix in ('.tsv','.md')}
c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':p,'detail':d} for n,p,d in c]}
(H/'PASS927_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
