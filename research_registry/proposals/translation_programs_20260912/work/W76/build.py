from pathlib import Path
import json,csv,collections
D=Path(__file__).parent
ps=json.loads((D.parent/'W75/PARAGRAPHS.json').read_text());lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];actions={'qotaiin','qotchy','shey','chkaiin'};out=[];args=[];md=['# Vollständiger P09-R1-Rezeptgegenentwurf','','Alle Bedeutungen hypothetisch; rohe Eingabeplätze ohne bekannte Materialrolle bleiben unbekannt.','']
for p in ps:
 last=None;md+=['## '+p['edition']+' '+p['id'],'']
 for l in p['lines']:
  ws=l['words'];ids=l['source_ids'];md+=[l['locus']+' `'+ ' '.join(ws)+'`','', ' · '.join(lex[w]['meaning'] if w in lex else '⟦'+w+'⟧' for w in ws),'']
  for i,w in enumerate(ws):
   out.append(dict(edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,hypothesis=lex[w]['meaning'] if w in lex else '⟦'+w+'⟧'))
   if lex.get(w,{}).get('kind')=='MATERIAL':last=(ids[i],w)
   if w not in actions:continue
   inp=ws[i+1] if i+1<len(ws) else '';kind=lex.get(inp,{}).get('kind');need=w in {'qotchy','chkaiin'}
   r=dict(edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,meaning=lex[w]['meaning'],input=inp,input_at=ids[i+1] if inp else '',input_status='MISSING_INPUT' if not inp else 'ASSUMED_MATERIAL' if kind=='MATERIAL' else 'UNKNOWN_INPUT' if kind is None else 'WRONG_KNOWN_ROLE',recipient=last[0] if need and last else '',recipient_word=last[1] if need and last else '',recipient_status='NOT_REQUIRED_IN_MINIMAL_FRAME' if not need else 'ASSUMED_PRIOR_MATERIAL' if last else 'MISSING_RECIPIENT')
   args.append(r);md+=['- '+r['at']+': '+r['meaning']+' ⟦'+inp+'⟧ ('+r['input_status']+'); '+r['recipient_status']+' '+r['recipient_word']]
  md+=['']
for name,rows in [('ALIGNMENT.tsv',out),('ARGUMENTS.tsv',args)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
(D/'READING.md').write_text('\n'.join(md)+'\n');r=dict(paragraph_readings=len(ps),source_groups=len(out),actions=len(args),input_counts=dict(collections.Counter(r['input_status'] for r in args)),recipient_counts=dict(collections.Counter(r['recipient_status'] for r in args)),meaning_confirmed=False,selected=None)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));print(json.dumps([r for r in args if r['word']=='qotchy']))
