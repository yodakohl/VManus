#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
d=read('PASS932_1384_BILEVEL_CARD_DICTIONARY.tsv');e=read('PASS932_2511_COMPOSED_EVENT_READINGS.tsv');x=read('PASS932_CROSS_CHANNEL_SURFACE_EXAMPLES.tsv')
c=[('cards_1384',len(d)==1384,len(d)),('events_2511',len(e)==2511,len(e)),('cards_unique',len({r['dictionary_entry_id'] for r in d})==1384,1384),('events_unique',len({r['event_id'] for r in e})==2511,2511),('all_card_ids_bound',set(r['dictionary_entry_id'] for r in d)==set(r['dictionary_entry_id'] for r in e),1384),('no_new_whole',all(r['composition_status']=='FULLY_COMPOSED_NO_NEW_WHOLE_GLOSS' for r in d),'composition'),('cross_examples',len(x)>0,len(x)),('sealed_absent',not any(z in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS932_*') if q.suffix in ('.tsv','.md') for z in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS932_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirty_second.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS932_*') if q.suffix in ('.tsv','.md')};c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':v,'detail':z} for n,v,z in c]};(H/'PASS932_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
