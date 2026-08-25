#!/usr/bin/env python3
import csv,hashlib,json,re,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
d=read('PASS935_56_ATOMIC_POCKET_LEXICON.tsv');c=read('PASS935_1384_ATOMIC_CARD_INTERLINEAR.tsv')
checks=[('components_56',len(d)==56,len(d)),('cards_1384',len(c)==1384,len(c)),('atomic_one_token',all(re.fullmatch(r'[A-Z0-9_]+',r['atomic_pocket_value_de']) for r in d),'tokens'),('components_unique',len({r['component'] for r in d})==56,56),('cards_unique',len({r['dictionary_entry_id'] for r in c})==1384,1384),('no_empty',all(r['atomic_pocket_sequence_de'] for r in c),'cards'),('sealed_absent',not any(z in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS935_*') if q.suffix in ('.tsv','.md') for z in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS935_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirty_fifth.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS935_*') if q.suffix in ('.tsv','.md')};checks.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in checks) else 'FAIL','checks':[{'name':n,'pass':v,'detail':z} for n,v,z in checks]};(H/'PASS935_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
