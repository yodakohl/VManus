#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
f=read('PASS928_28_RECIPE_FRAGMENTS.tsv');o=read('PASS928_FRAGMENT_OCCURRENCES.tsv');s=json.loads((H/'PASS928_BUILD_SUMMARY.json').read_text())
c=[('fragments_28',len(f)==28,len(f)),('triples_24',sum(r['steps']=='3' for r in f)==24,sum(r['steps']=='3' for r in f)),('quads_4',sum(r['steps']=='4' for r in f)==4,sum(r['steps']=='4' for r in f)),('occ_unique',len(o)==len({r['occurrence_id'] for r in o}),len(o)),('all_fragments_used',set(r['fragment_id'] for r in f)==set(r['fragment_id'] for r in o),28),('no_broad_five',s['broad_five_step_fragments']==0,s['broad_five_step_fragments']),('sealed_absent',not any(x in p.read_text(encoding='utf-8',errors='ignore') for p in H.glob('PASS928_*') if p.suffix in ('.tsv','.md') for x in ('f84','f84r')),'sealed')]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in H.glob('PASS928_*') if p.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_twenty_eighth.py')],check=True);after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in H.glob('PASS928_*') if p.suffix in ('.tsv','.md')};c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':p,'detail':d} for n,p,d in c]};(H/'PASS928_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
