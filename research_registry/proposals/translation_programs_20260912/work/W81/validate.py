from pathlib import Path
import json,csv,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'SOURCE_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ps=json.loads((D/'PARAGRAPHS.json').read_text());lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];m={w for w,v in lex.items() if v['kind']=='MATERIAL'}|{'otchy','qoteey'}
expected=[]
for p in ps:
 assert not p['page'].startswith('f84')
 flat=[(w,s) for l in p['lines'] for w,s in zip(l['words'],l['source_ids'])]
 for i,(w,s) in enumerate(flat):
  if lex.get(w,{}).get('kind')=='QUALITY_OR_STATE':
   prior=next(((a,b) for a,b in reversed(flat[:i]) if a in m),('',''))
   expected.append(dict(edition=p['edition'],paragraph=p['id'],at=s,quality=w,gloss=lex[w]['meaning'],carrier=prior[0],carrier_at=prior[1]))
assert expected==list(csv.DictReader((D/'QUALITIES.tsv').open(),delimiter='\t'))
r=json.loads((D/'RESULT.json').read_text());assert len(expected)==r['qualities']==51
assert [x for x in expected if x['carrier'] in {'otchy','qoteey'}]==r['target_qualities']
for c in r['candidates']:assert c['physical_state_conflicts']==[x for x in expected if x['carrier']==c['liquid'] and x['quality'] in {'chol','oltchy'}]
v={'status':'PASS','quality_bindings':51,'meaning_validated':False};(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
