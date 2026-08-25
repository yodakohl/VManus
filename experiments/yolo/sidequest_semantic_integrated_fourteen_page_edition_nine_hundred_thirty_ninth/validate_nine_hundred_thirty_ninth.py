#!/usr/bin/env python3
import csv,hashlib,json,re,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
l=read('PASS939_56_CURRENT_ATOMIC_LEXICON.tsv');s=read('PASS939_1078_CURRENT_SURFACE_DICTIONARY.tsv');e=read('PASS939_2511_CURRENT_EVENT_INTERLINEAR.tsv');c=read('PASS939_354_CURRENT_CLAUSE_TRANSLATIONS.tsv');p=read('PASS939_14_PAGE_SUMMARY.tsv')
checks=[('lexicon_56',len(l)==56,len(l)),('surfaces_1078',len(s)==1078,len(s)),('events_2511',len(e)==2511,len(e)),('clauses_354',len(c)==354,len(c)),('pages_14',len(p)==14,len(p)),('event_unique',len({r['event_id'] for r in e})==2511,2511),('surface_unique',len({r['surface'] for r in s})==1078,1078),('page_event_sum',sum(int(r['events']) for r in p)==2511,sum(int(r['events']) for r in p)),('no_letter_placeholder',not any(re.search(r'\b[fgidsbmjz]-Zeichen\b',r['current_compositional_reading_de'],re.I) for r in e),'semantic signs'),('sealed_absent',not any(z in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS939_*') if q.suffix in ('.tsv','.md') for z in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS939_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirty_ninth.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS939_*') if q.suffix in ('.tsv','.md')};checks.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in checks) else 'FAIL','checks':[{'name':n,'pass':v,'detail':d} for n,v,d in checks]};(H/'PASS939_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
