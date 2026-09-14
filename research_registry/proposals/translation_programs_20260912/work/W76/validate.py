from pathlib import Path
import json,csv,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
ps=json.loads((D.parent/'W75/PARAGRAPHS.json').read_text());lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];align=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));args=list(csv.DictReader((D/'ARGUMENTS.tsv').open(),delimiter='\t'));expected=[];aks=[]
for p in ps:
 assert not p['page'].startswith('f84');prior=[]
 for l in p['lines']:
  for i,(sid,w) in enumerate(zip(l['source_ids'],l['words'])):
   expected.append(dict(edition=p['edition'],paragraph=p['id'],at=sid,word=w,hypothesis=lex[w]['meaning'] if w in lex else '⟦'+w+'⟧'))
   if w in {'qotaiin','qotchy','shey','chkaiin'}:
    r=next(r for r in args if r['edition']==p['edition'] and r['at']==sid);aks.append((p['edition'],sid));inp=l['words'][i+1] if i+1<len(l['words']) else '';kind=lex.get(inp,{}).get('kind');status='MISSING_INPUT' if not inp else 'ASSUMED_MATERIAL' if kind=='MATERIAL' else 'UNKNOWN_INPUT' if kind is None else 'WRONG_KNOWN_ROLE';assert r['input']==inp and r['input_status']==status
    need=w in {'qotchy','chkaiin'};assert r['recipient']==(prior[-1] if need and prior else '')
   if lex.get(w,{}).get('kind')=='MATERIAL':prior.append(sid)
assert expected==align and len(align)==654 and len(aks)==len(args)==20
v=dict(status='PASS',source_groups=654,all_operations=20,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
