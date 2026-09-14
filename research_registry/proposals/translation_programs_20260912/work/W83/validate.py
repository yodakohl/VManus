from pathlib import Path
import json,csv,hashlib
D=Path(__file__).resolve().parent.relative_to(Path.cwd())
for p,h in json.loads((D/'SOURCE_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
read=lambda p:list(csv.DictReader(p.open(),delimiter='\t'))
old=[r for r in read(D.parent/'W82/EVENTS.tsv') if r['model']=='C'];oldal=[r for r in read(D.parent/'W82/ALIGNMENT.tsv') if r['model']=='C'];ps=json.loads((D.parent/'W82/PARAGRAPHS.json').read_text());lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];mat={w for w,v in lex.items() if v['kind']=='MATERIAL'}|{'cthar','otchy','qoteey'}
prior={}
for p in ps:
 assert not p['page'].startswith('f84')
 flat=[(w,s) for l in p['lines'] for w,s in zip(l['words'],l['source_ids'])]
 for i,(w,s) in enumerate(flat):prior[p['edition'],s]=next(((x,y) for x,y in reversed(flat[:i]) if x in mat),('',''))
expected=[];al=[]
for m,g in [('V','erwärmen'),('H','warm'),('F','feucht')]:
 for r in old:
  n=r|{'model':m}
  if m!='V' and r['word']=='shey':
   w,s=prior[r['edition'],r['at']];n.update(kind='QUALITY',carrier=s,carrier_word=w,input='',input_status='')
  expected.append(n)
 for r in oldal:al.append(r|{'model':m,'gloss':g if r['word']=='shey' else r['gloss']})
assert expected==read(D/'EVENTS.tsv');assert al==read(D/'ALIGNMENT.tsv');assert [r for r in expected if r['word']=='shey']==read(D/'SHEY.tsv')
assert len(al)==21177 and len(expected)==1323
v=dict(status='PASS',aligned_groups=len(al),events=len(expected),shey_per_model=66,meaning_validated=False);(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
