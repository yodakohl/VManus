from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
lex={r['form']:r for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
materials={w for w,r in lex.items() if r['role'] in ('MATERIAL','MATERIAL_DOSE')}|{'sheedy','shey'}
actions={w for w,r in lex.items() if r['role'] in ('ACTION','ACTION_TYPED')}
ps=[p for p in json.loads((D.parent/'W56/PARAGRAPHS.json').read_text()) if p['page']=='f75v']
ev=list(csv.DictReader((D/'ACTIONS.tsv').open(),delimiter='\t'));rs=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));assert len(ev)==28 and len(rs)==236
for p in ps:
 flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
 for model in ('G','S'):
  rows=[r for r in rs if r['edition']==p['edition'] and r['model']==model];assert [(r['at'],r['word']) for r in rows]==flat
  ee=[r for r in ev if r['edition']==p['edition'] and r['model']==model]
  want=[]
  for i,(sid,w) in enumerate(flat):
   if w not in actions:continue
   left=[t for t in flat[:i] if t[1] in materials];target=left[-1] if left else ('MISSING','MISSING');want.append((sid,w,target[0],target[1]))
  assert [(r['at'],r['word'],r['patient_at'],r['patient']) for r in ee]==want
v=dict(status='PASS',scope='complete source coverage and independently enumerated last-material binding',meaning_validated=False,state_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
