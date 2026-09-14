from pathlib import Path
import csv,json,itertools,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text())
base={r['form']:r['hypothesis'] for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')};base.update(sheedy='Zubereitung A',shey='Zubereitung B')
rows=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));assert len(rows)==4640
models=list(csv.DictReader((D/'CANDIDATES.tsv').open(),delimiter='\t'));assert {m['model'] for m in models}=={''.join(x) for x in itertools.product('NA','RM','CV')}
expected=[];targets=[]
for m in models:
 s,o,c=m['model'];assert m['sheckhy']==('Mischung' if s=='N' else 'vermische');assert m['ol']==('mit' if o=='R' else 'Zubereitungsposten');assert m['chey']==('prüfe' if c=='C' else 'nicht [Bereich offen]')
 lex=dict(base,**{k:m[k] for k in ('sheckhy','ol','chey')})
 for p in ps:
  assert not p['page'].startswith('f84')
  for l in p['lines']:
   for i,(sid,w) in enumerate(zip(l['source_ids'],l['words'])):
    expected.append(dict(model=m['model'],edition=p['edition'],paragraph=p['id'],at=sid,word=w,hypothesis=lex.get(w,'⟦'+w+'⟧')))
    if w=='sheckhy':
     ws=l['words'][max(0,i-1):i+2];targets.append(dict(model=m['model'],edition=p['edition'],at=sid,raw=' '.join(ws),hypothesis=' · '.join(lex.get(x,'⟦'+x+'⟧') for x in ws)))
assert rows==expected
assert targets==list(csv.DictReader((D/'TARGETS.tsv').open(),delimiter='\t')) and len(targets)==80
v=dict(status='PASS',source_groups_per_model=580,models=8,target_rows=80,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
