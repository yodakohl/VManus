from pathlib import Path
import csv,json,hashlib,collections
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
lines=json.loads((D.parent/'P09/INPUT.json').read_text())['lines'];base=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['D1']['lexicon'];rows=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));rels=list(csv.DictReader((D/'RELATIONS.tsv').open(),delimiter='\t'));expected=[];expectedrels=[]
for m in ['E','C']:
 last={}
 for l in lines:
  page=l['locus'].split('.')[0];assert not page.startswith('f84')
  for i,w in enumerate(l['groups']):
   at=l['locus']+':'+str(i+1);gl='verursacht [Beschwerde]' if m=='C' and w in {'qotaiin','shey'} else base[w]['meaning'] if w in base else '⟦'+w+'⟧';expected.append(dict(model=m,at=at,word=w,hypothesis=gl))
   if w in {'qotaiin','shey','qotchy'}:
    r=next(r for r in rels if r['model']==m and r['at']==at);expectedrels.append((m,at));arg=l['groups'][i+1] if i+1<len(l['groups']) else '';assert r['argument']==arg
    if w!='qotchy':assert r['kind']=='HARM';last[page]=(at,arg)
    else:assert (r['linked_harm'],r['linked_target'])==last[page]
assert expected==rows and len(rows)==290 and len(expectedrels)==len(rels)==12
forms={r['argument'] for r in rels};occ=[dict(at=l['locus']+':'+str(i+1),word=w) for l in lines for i,w in enumerate(l['groups']) if w in forms or w=='chkaiin'];assert occ==list(csv.DictReader((D/'ALL_ARGUMENT_AND_EFFICACY_OCCURRENCES.tsv').open(),delimiter='\t')) and len(occ)==8
v=dict(status='PASS',all_source_groups=145,models=2,relations=12,argument_and_efficacy_occurrences=8,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
