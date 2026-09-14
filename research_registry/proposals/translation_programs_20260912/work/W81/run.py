from pathlib import Path
import json,csv,hashlib
D=Path(__file__).resolve().parent.relative_to(Path.cwd())
sources=[D.parent/'W80/PARAGRAPHS.json',D.parent/'W78/PARAGRAPHS.json',D.parent/'P09/MODELS.json']
ps={}
for s in sources[:2]:
 for p in json.loads(s.read_text()):
  assert not p['page'].startswith('f84')
  k=p['edition'],p['id']
  if k in ps: assert ps[k]==p
  ps[k]=p
lex=json.loads(sources[2].read_text())['models']['R1']['lexicon'];lex.update(otchy=dict(kind='MATERIAL'),qoteey=dict(kind='MATERIAL'))
rows=[]
for p in ps.values():
 last=at=''
 for l in p['lines']:
  for w,sid in zip(l['words'],l['source_ids']):
   if lex.get(w,{}).get('kind')=='MATERIAL':last,at=w,sid
   if lex.get(w,{}).get('kind')=='QUALITY_OR_STATE':
    rows.append(dict(edition=p['edition'],paragraph=p['id'],at=sid,quality=w,gloss=lex[w]['meaning'],carrier=last,carrier_at=at))
with (D/'QUALITIES.tsv').open('w') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');wr.writeheader();wr.writerows(rows)
(D/'PARAGRAPHS.json').write_text(json.dumps(list(ps.values()),ensure_ascii=False,separators=(',',':'))+'\n')
target=[r for r in rows if r['carrier'] in {'otchy','qoteey'}]
candidates=[]
for name,liquid in [('PL','qoteey'),('LP','otchy')]:
 conflicts=[r for r in target if r['carrier']==liquid and r['quality'] in {'chol','oltchy'}]
 candidates.append(dict(candidate=name,liquid=liquid,physical_state_conflicts=conflicts,humoral_quality_discriminator=False))
r=dict(paragraphs=len(ps),groups=sum(len(l['words']) for p in ps.values() for l in p['lines']),qualities=len(rows),target_qualities=target,candidates=candidates,independent_meaning_confirmation=False,prior_W80_role_conflicts=3)
(D/'RESULT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
(D/'SOURCE_HASHES.json').write_text(json.dumps({str(s):hashlib.sha256(s.read_bytes()).hexdigest() for s in sources},indent=2)+'\n')
print(json.dumps(r,ensure_ascii=False))
