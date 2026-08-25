#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
d=read('PASS931_56_BILEVEL_COMPONENT_DICTIONARY.tsv');a=read('PASS931_6513_COMPONENT_ATOMS.tsv')
c=[('components_56',len(d)==56,len(d)),('atoms_6513',len(a)==6513,len(a)),('components_unique',len({r['component'] for r in d})==56,56),('atoms_unique',len({r['atom_id'] for r in a})==6513,len({r['atom_id'] for r in a})),('all_components_used',set(r['component'] for r in d)==set(r['component'] for r in a),56),('all_values',all(r['abstract_core_de'] and r['workshop_prose_de'] and r['owner_address_de'] for r in d),'values'),('sealed_absent',not any(x in q.read_text(encoding='utf-8',errors='ignore') for q in H.glob('PASS931_*') if q.suffix in ('.tsv','.md') for x in ('f84','f84r')),'sealed')]
before={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS931_*') if q.suffix in ('.tsv','.md')};subprocess.run([sys.executable,str(H/'build_nine_hundred_thirty_first.py')],check=True);after={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in H.glob('PASS931_*') if q.suffix in ('.tsv','.md')};c.append(('deterministic',before==after,len(before)))
out={'status':'PASS' if all(x[1] for x in c) else 'FAIL','checks':[{'name':n,'pass':v,'detail':z} for n,v,z in c]};(H/'PASS931_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False));raise SystemExit(0 if out['status']=='PASS' else 1)
