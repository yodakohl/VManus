from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ps=[p for p in json.loads((D.parent/'W56/PARAGRAPHS.json').read_text()) if p['page']=='f75v'];old=list(csv.DictReader((D.parent/'W58/ACTIONS.tsv').open(),delimiter='\t'))
q=list(csv.DictReader((D/'QOKAIN.tsv').open(),delimiter='\t'));b=list(csv.DictReader((D/'WETTING.tsv').open(),delimiter='\t'))
assert len(q)==8 and len(b)==12
for p in ps:
 ed=p['edition'];flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
 assert [r['at'] for r in q if r['edition']==ed]==[sid for sid,w in flat if w=='qokain']
 selected=[a for a in old if a['edition']==ed and a['action']=='benetze'];rows=[r for r in b if r['edition']==ed]
 assert [(r['model'],r['at'],r['patient']) for r in rows]==[(a['model'],a['at'],a['patient']) for a in selected]
 for r in rows:
  line=next(l for l in p['lines'] if r['at'] in l['source_ids']);i=line['source_ids'].index(r['at']);n=i+1
  expected=line['source_ids'][n] if n<len(line['words']) and line['words'][n]=='qokain' else 'UNBOUND'
  assert r['I_medium']==expected and r['Q_medium']=='UNBOUND'
v=dict(status='PASS',scope='all qokain and wetting occurrences, fixed patients, immediate-medium candidate',meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
