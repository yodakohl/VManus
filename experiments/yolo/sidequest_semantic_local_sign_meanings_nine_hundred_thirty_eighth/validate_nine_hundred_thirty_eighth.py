#!/usr/bin/env python3
import csv,hashlib,json,re,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
l=read('PASS938_56_REVISED_ATOMIC_LEXICON.tsv');s=read('PASS938_11_LOCAL_SIGN_VALUES.tsv');e=read('PASS938_43_SIGN_EVENT_READINGS.tsv');a=read('PASS938_44_SIGN_ATOM_READINGS.tsv')
c=[('lexicon_56',len(l)==56,len(l)),('signs_11',len(s)==11,len(s)),('events_43',len(e)==43,len(e)),('events_unique',len({r['event_id'] for r in e})==43,len({r['event_id'] for r in e})),('atoms_44',len(a)==44,len(a)),('atoms_unique',len({r['sign_atom_id'] for r in a})==44,44),('double_frame',sum(r['event_id']=='P912-E2336' and r['component']=='S_LABEL' for r in a)==2,'salols'),('values_atomic',all(re.fullmatch(r'[A-Z0-9_]+',r['atomic_value_de']) for r in s),'values'),('no_letter_placeholder',all('-ZEICHEN' not in r['atomic_pocket_value_de'] and r['atomic_pocket_value_de'] not in {'F','G','I','D','S','B','M','J'} for r in l if r['component'] in {x['component'] for x in s}),'semantic'),('sealed_absent',not any(z in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS938_*') if q.suffix in ('.tsv','.md') for z in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS938_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirty_eighth.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS938_*') if q.suffix in ('.tsv','.md')};c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':v,'detail':d} for n,v,d in c]};(H/'PASS938_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
