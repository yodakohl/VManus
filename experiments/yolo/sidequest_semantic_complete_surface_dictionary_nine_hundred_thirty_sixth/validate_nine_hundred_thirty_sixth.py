#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
d=read('PASS936_1078_COMPLETE_SURFACE_DICTIONARY.tsv')
c=[('surfaces_1078',len(d)==1078,len(d)),('events_2511',sum(int(r['events']) for r in d)==2511,sum(int(r['events']) for r in d)),('surface_unique',len({r['surface'] for r in d})==1078,1078),('one_recipe',all('|' not in r['component_recipe'] for r in d),'recipes'),('all_atomic',all(r['atomic_pocket_gloss_de'] for r in d),'atomic'),('bichannel_107',sum(r['channel_class']=='BICHANNEL' for r in d)==107,sum(r['channel_class']=='BICHANNEL' for r in d)),('sealed_absent',not any(z in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS936_*') if q.suffix in ('.tsv','.md') for z in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS936_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirty_sixth.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS936_*') if q.suffix in ('.tsv','.md')};c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':v,'detail':z} for n,v,z in c]};(H/'PASS936_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
