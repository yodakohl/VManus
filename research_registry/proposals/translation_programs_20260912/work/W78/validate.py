from pathlib import Path
import json,csv,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());loci={'f19v.3','f18v.6','f2v.3','f56r.10'};ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}];assert ps==json.loads((D/'PARAGRAPHS.json').read_text())
lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];al=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));ev=list(csv.DictReader((D/'EVENTS.tsv').open(),delimiter='\t'));expected=[];ee=[]
for p in ps:
 for m in ['N','Q']:
  dd={w:dict(v) for w,v in lex.items()};dd['otchy']=dict(meaning='Material T' if m=='N' else 'Eigenschaft T',kind='MATERIAL' if m=='N' else 'QUALITY_OR_STATE');prior=[]
  for l in p['lines']:
   ws=l['words'];ids=l['source_ids']
   for i,w in enumerate(ws):
    expected.append(dict(model=m,edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,hypothesis=dd[w]['meaning'] if w in dd else '⟦'+w+'⟧'));kind=dd.get(w,{}).get('kind')
    if kind=='QUALITY_OR_STATE' or w in {'qotaiin','qotchy','shey','chkaiin'}:
     e=next(e for e in ev if e['model']==m and e['edition']==p['edition'] and e['at']==ids[i]);ee.append(e)
     if kind=='QUALITY_OR_STATE':
      if w=='otchy':cc=[ids[j] for j in [i-1,i+1] if 0<=j<len(ws) and dd.get(ws[j],{}).get('kind')=='MATERIAL'];carrier=cc[0] if cc else ''
      else:carrier=prior[-1] if prior else ''
     else:carrier=ids[i+1] if i+1<len(ids) else ''
     assert e['carrier']==carrier and e['recipient']==(prior[-1] if prior and w in {'qotchy','chkaiin'} else '')
    if kind=='MATERIAL':prior.append(ids[i])
assert expected==al and len(al)==748 and len(ee)==len(ev)==50
v=dict(status='PASS',paragraphs=8,alignment_rows=748,all_events=50,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
