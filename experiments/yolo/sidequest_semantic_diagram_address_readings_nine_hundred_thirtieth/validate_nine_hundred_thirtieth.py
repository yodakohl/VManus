#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
e=read('PASS930_501_ADDRESS_EVENT_LEDGER.tsv');u=read('PASS930_10_DIAGRAM_UNIT_READINGS.tsv')
c=[('events_501',len(e)==501,len(e)),('units_10',len(u)==10,len(u)),('events_unique',len({r['event_id'] for r in e})==501,501),('groups_sum',sum(int(r['groups']) for r in u)==501,sum(int(r['groups']) for r in u)),('f70_split',{'f70v1','f70v2'}<=set(r['diagram_unit'] for r in u),'panels'),('all_address',all(r['address_reading_de'] for r in e),'readings'),('sealed_absent',not any(x in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS930_*') if q.suffix in ('.tsv','.md') for x in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS930_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirtieth.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS930_*') if q.suffix in ('.tsv','.md')};c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':v,'detail':d} for n,v,d in c]};(H/'PASS930_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
