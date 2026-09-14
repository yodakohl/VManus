from pathlib import Path
import json,csv,hashlib,collections
D=Path(__file__).resolve().parent.relative_to(Path.cwd());S=D.parent/'W84'
for p,h in json.loads((D/'SOURCE_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ps=[p for p in json.loads((S/'PARAGRAPHS.json').read_text()) if p['page'] in {'f15r','f53v'}];assert ps==json.loads((D/'PARAGRAPHS.json').read_text())
lex=json.loads((S/'LEXICON.json').read_text())|json.loads((S/'MODELS.json').read_text())['1'];events=list(csv.DictReader((D/'EVENTS.tsv').open(),delimiter='\t'));al=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));profiles=json.loads((D/'PROFILES.json').read_text());expected=[]
for p,profile in zip(ps,profiles):
 flat=[(w,s) for l in p['lines'] for w,s in zip(l['words'],l['source_ids'])];ix={s:i for i,(w,s) in enumerate(flat)};cut=next(i for i,(w,s) in enumerate(flat) if w=='cthy');rr=[r for r in events if r['edition']==p['edition'] and r['paragraph']==p['id']]
 for r in rr:
  assert r['phase']==('before_cthy' if ix[r['at']]<cut else 'from_cthy')
  assert r['intervening_groups']==(str(ix[r['at']]-ix[r['carrier']]-1) if r['carrier'] else '')
 assert profile['groups']==len(flat) and profile['cthy_mentions']==sum(w=='cthy' for w,s in flat)
 assert profile['max_intervening']==max(int(r['intervening_groups']) for r in rr if r['carrier'] and r['kind'] in {'VALUE','QUALITY'})
 for phase in ['before_cthy','from_cthy']:assert profile['phases'][phase]['counts']==dict(collections.Counter(r['kind'] for r in rr if r['phase']==phase))
 for w,s in flat:
  v={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+v+'·Uₚ' if v else lex.get(w,{}).get('meaning','⟦'+w+'⟧');expected.append(dict(edition=p['edition'],paragraph=p['id'],at=s,word=w,gloss=g))
assert expected==al and len(al)==334
old=[r for r in csv.DictReader((S/'EVENTS.tsv').open(),delimiter='\t') if r['model']=='1' and (r['edition'],r['paragraph']) in {(p['edition'],p['id']) for p in ps}]
assert old==[{k:v for k,v in r.items() if k not in {'phase','intervening_groups'}} for r in events]
v=dict(status='PASS',paragraphs=4,groups=334,events=len(events),meaning_validated=False);(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
