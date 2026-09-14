from pathlib import Path
import json,csv,itertools,collections
D=Path(__file__).parent
ps=json.loads((D.parent/'W78/PARAGRAPHS.json').read_text());base=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];values={'dair':'A','dain':'B','daiin':'C'};al=[];vs=[];ops=[];md=['# Ganze Rollen- und Dimensionsfassungen','','Alle Begriffe/Werte unbestätigt; gemeinsame Masseneinheit nur hypothetisch.','']
for role,dim in itertools.product(['U','Q'],['G','M']):
 model=role+dim;lex={w:dict(r) for w,r in base.items()};lex.update(otchy=dict(meaning='Material T',kind='MATERIAL'),qoteey=dict(meaning='Material U' if role=='U' else 'Eigenschaft U',kind='MATERIAL' if role=='U' else 'QUALITY_OR_STATE'))
 for p in ps:
  last=None;quality=None;md+=['## '+model+' '+p['edition']+' '+p['id'],'']
  for l in p['lines']:
   ws=l['words'];ids=l['source_ids'];display=[]
   for i,w in enumerate(ws):
    g=('Grad '+values[w] if dim=='G' else 'Masse '+values[w]+'·Uₚ') if w in values else lex[w]['meaning'] if w in lex else '⟦'+w+'⟧';display.append(g);al.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,hypothesis=g))
    kind=lex.get(w,{}).get('kind')
    if kind=='MATERIAL':last=(ids[i],w);quality=None
    if kind=='QUALITY_OR_STATE':quality=(ids[i],w)
    if w in values:
     vs.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,value=values[w],material=last[0] if last else '',material_word=last[1] if last else '',quality=quality[0] if quality and dim=='G' else '',quality_word=quality[1] if quality and dim=='G' else '',status='MISSING_MATERIAL' if not last else 'MISSING_QUALITY' if dim=='G' and not quality else 'ASSUMED_BOUND',dimension=dim))
    if w in {'qotchy','qotaiin','shey','chkaiin'}:
     inp=ws[i+1] if i+1<len(ws) else '';ik=lex.get(inp,{}).get('kind');need=w in {'qotchy','chkaiin'}
     ops.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,input=inp,input_status='MISSING_INPUT' if not inp else 'ASSUMED_MATERIAL' if ik=='MATERIAL' else 'UNKNOWN_INPUT' if ik is None else 'WRONG_KNOWN_ROLE',recipient=last[0] if need and last else '',recipient_word=last[1] if need and last else ''))
   md += [l['locus']+' `'+ ' '.join(ws)+'`','', ' · '.join(display),'']
for name,rr in [('ALIGNMENT.tsv',al),('VALUES.tsv',vs),('OPERATIONS.tsv',ops)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]),delimiter='\t');w.writeheader();w.writerows(rr)
(D/'READING.md').write_text('\n'.join(md)+'\n');res=dict(models=4,alignment_rows=len(al),value_rows=len(vs),operation_rows=len(ops),value_status={m:dict(collections.Counter(r['status'] for r in vs if r['model']==m)) for m in ['UG','UM','QG','QM']},selected=None,meaning_confirmed=False)
(D/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
