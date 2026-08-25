#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
s=read('PASS937_ACTION_SEGMENTS.tsv');c=read('PASS937_354_MACRO_CLAUSE_TRANSLATIONS.tsv');z=json.loads((H/'PASS937_BUILD_SUMMARY.json').read_text())
checks=[('clauses_354',len(c)==354,len(c)),('action_tokens_1758',sum(int(r['action_tokens']) for r in s)==1758,sum(int(r['action_tokens']) for r in s)),('segments_unique',len({r['segment_id'] for r in s})==len(s),len(s)),('clause_unique',len({r['clause_id'] for r in c})==354,354),('events_2010',sum(int(r['events']) for r in c)==2010,sum(int(r['events']) for r in c)),('partition',z['macro_action_tokens']+z['single_action_tokens']==1758,z['macro_action_tokens']),('all_natural',all(r['natural_macro_translation_de'].endswith('.') for r in c),'translations'),('sealed_absent',not any(x in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS937_*') if q.suffix in ('.tsv','.md') for x in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS937_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirty_seventh.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS937_*') if q.suffix in ('.tsv','.md')};checks.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in checks) else 'FAIL','checks':[{'name':n,'pass':v,'detail':d} for n,v,d in checks]};(H/'PASS937_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
