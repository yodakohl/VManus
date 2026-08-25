#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
p=read('PASS929_12_CONCRETE_PAGE_READINGS.tsv');b=read('PASS929_354_CLAUSE_BINDINGS.tsv')
c=[('pages_12',len(p)==12,len(p)),('clauses_354',len(b)==354,len(b)),('events_2010',sum(int(r['events']) for r in p)==2010,sum(int(r['events']) for r in p)),('page_unique',len({r['physical_page'] for r in p})==12,12),('clause_unique',len({r['clause_id'] for r in b})==354,354),('all_concrete',all(len(r['concrete_page_reading_de'].split())>=25 for r in p),'readings'),('sealed_absent',not any(x in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS929_*') if q.suffix in ('.tsv','.md') for x in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS929_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_twenty_ninth.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS929_*') if q.suffix in ('.tsv','.md')};c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':v,'detail':d} for n,v,d in c]};(H/'PASS929_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
