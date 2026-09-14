from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ps=[p for p in json.loads((D.parent/'W56/PARAGRAPHS.json').read_text()) if p['page']=='f75v']
lex={r['form']:r['hypothesis'] for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
rs=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));assert len(rs)==236
for p in ps:
 for model in ['G','S']:
  rows=[r for r in rs if r['edition']==p['edition'] and r['model']==model]
  source=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
  assert [(r['source_id'],r['word']) for r in rows]==source
  for r in rows:
   v=lex.get(r['word'],'⟦'+r['word']+'⟧')
   if model=='S' and r['word']=='cheey':v='benetze'
   assert r['hypothesis']==v
v=dict(status='PASS',scope='source integrity, all236positions and exact declared rival difference',meaning_validated=False,argument_binding_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
