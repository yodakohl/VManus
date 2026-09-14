from pathlib import Path
import json,csv,hashlib,itertools
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
ps=json.loads((D.parent/'W78/PARAGRAPHS.json').read_text());base=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];al=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));vs=list(csv.DictReader((D/'VALUES.tsv').open(),delimiter='\t'));ops=list(csv.DictReader((D/'OPERATIONS.tsv').open(),delimiter='\t'));vals={'dair':'A','dain':'B','daiin':'C'};expected=[];vkeys=[];okeys=[]
for role,dim in itertools.product(['U','Q'],['G','M']):
 m=role+dim;lex={w:dict(r) for w,r in base.items()};lex.update(otchy=dict(meaning='Material T',kind='MATERIAL'),qoteey=dict(meaning='Material U' if role=='U' else 'Eigenschaft U',kind='MATERIAL' if role=='U' else 'QUALITY_OR_STATE'))
 for p in ps:
  last='';quality=''
  for l in p['lines']:
   for i,(at,w) in enumerate(zip(l['source_ids'],l['words'])):
    g=('Grad '+vals[w] if dim=='G' else 'Masse '+vals[w]+'·Uₚ') if w in vals else lex[w]['meaning'] if w in lex else '⟦'+w+'⟧';expected.append(dict(model=m,edition=p['edition'],paragraph=p['id'],at=at,word=w,hypothesis=g))
    kind=lex.get(w,{}).get('kind')
    if kind=='MATERIAL':last=at;quality=''
    if kind=='QUALITY_OR_STATE':quality=at
    if w in vals:
     r=next(r for r in vs if r['model']==m and r['edition']==p['edition'] and r['at']==at);vkeys.append(at);assert r['material']==last and r['quality']==(quality if dim=='G' else '')
    if w in {'qotchy','qotaiin','shey','chkaiin'}:
     r=next(r for r in ops if r['model']==m and r['edition']==p['edition'] and r['at']==at);okeys.append(at);assert r['input']==(l['words'][i+1] if i+1<len(l['words']) else '') and r['recipient']==(last if w in {'qotchy','chkaiin'} else '')
assert expected==al and len(al)==1496 and len(vkeys)==len(vs)==100 and len(okeys)==len(ops)==40
for ed in ['ZL3b','IT2a']:
 r=[r for r in vs if r['model']=='UM' and r['edition']==ed and r['at'] in {ed+'|f19v.3|G003',ed+'|f19v.5|G003'}];assert len(r)==2 and {x['value'] for x in r}=={'C'} and {x['material_word'] for x in r}=={'otchy','qoteey'}
v=dict(status='PASS',alignment_rows=1496,value_rows=100,operations=40,conditional_equal_mass=True,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
