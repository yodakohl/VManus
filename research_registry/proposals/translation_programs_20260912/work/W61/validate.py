from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ps=json.loads((D.parent/'W60/PARAGRAPHS.json').read_text());lex={r['form']:r for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')};lex.update(sheedy={'hypothesis':'Zubereitung A','role':'MATERIAL'},shey={'hypothesis':'Zubereitung B','role':'MATERIAL'})
rs=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));links=list(csv.DictReader((D/'LINKS.tsv').open(),delimiter='\t'));assert len(rs)==496 and len(links)==4
for p in ps:
 flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
 for m,v in [('R','mit'),('V','verwende')]:
  rows=[r for r in rs if r['edition']==p['edition'] and r['paragraph']==p['id'] and r['model']==m]
  assert [(r['at'],r['word']) for r in rows]==flat
  for r in rows:assert r['hypothesis']==(v if r['word']=='qolshey' else lex[r['word']]['hypothesis'] if r['word'] in lex else '⟦'+r['word']+'⟧')
 for i,(sid,w) in enumerate(flat):
  if w!='qolshey':continue
  r=next(r for r in links if r['at']==sid)
  j=max(k for k in range(i) if flat[k][1] in lex and lex[flat[k][1]]['role'] in ('ACTION','ACTION_TYPED','REPEAT_ACTION'))
  assert r['R_previous_action']==flat[j][0] and r['intervening']==' '.join(w for _,w in flat[j+1:i])
  assert int(r['unknown_intervening'])==sum(w not in lex for _,w in flat[j+1:i]) and r['V_object']==flat[i+1][0]
v=dict(status='PASS',scope='all496groups and four declared relation/operation comparisons',meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
