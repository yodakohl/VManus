from pathlib import Path
import json,csv,collections
D=Path(__file__).parent
ps=json.loads((D/'PARAGRAPHS.json').read_text());lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];lex.update(otchy=dict(meaning='Material T',kind='MATERIAL'),qoteey=dict(meaning='Material U',kind='MATERIAL'));vals={'dair':'A','dain':'B','daiin':'C'};rows=[];vv=[];aa=[];md=['# Ganze UM-Fassung aller qoteey-Kontextabsätze','','Alle Bedeutungen, Mengen und Bezüge hypothetisch.','']
for p in ps:
 last=None;md+=['## '+p['edition']+' '+p['id'],'']
 for l in p['lines']:
  ws=l['words'];ids=l['source_ids'];out=[]
  for i,w in enumerate(ws):
   g='Masse '+vals[w]+'·Uₚ' if w in vals else lex[w]['meaning'] if w in lex else '⟦'+w+'⟧';out.append(g);rows.append(dict(edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,hypothesis=g))
   if lex.get(w,{}).get('kind')=='MATERIAL':last=(ids[i],w)
   if w in vals:vv.append(dict(edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,value=vals[w],material=last[0] if last else '',material_word=last[1] if last else ''))
   if w in {'qotchy','qotaiin','shey','chkaiin'}:
    inp=ws[i+1] if i+1<len(ws) else '';ik=lex.get(inp,{}).get('kind');need=w in {'qotchy','chkaiin'}
    aa.append(dict(edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,input=inp,input_status='MISSING_INPUT' if not inp else 'ASSUMED_MATERIAL' if ik=='MATERIAL' else 'UNKNOWN_INPUT' if ik is None else 'WRONG_KNOWN_ROLE',recipient=last[0] if need and last else '',recipient_word=last[1] if need and last else ''))
  md += [l['locus']+' `'+ ' '.join(ws)+'`','', ' · '.join(out),'']
for name,rs in [('ALIGNMENT.tsv',rows),('VALUES.tsv',vv),('OPERATIONS.tsv',aa)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t');w.writeheader();w.writerows(rs)
(D/'READING.md').write_text('\n'.join(md)+'\n');o=json.loads((D/'OCCURRENCES.json').read_text());res=dict(occurrences=len(o),reading_counts=dict(collections.Counter(r['edition'] for r in o)),loci=len({r['locus'] for r in o}),paragraphs=len(ps),alignment_rows=len(rows),value_rows=len(vv),operation_rows=len(aa),qoteey_inputs=[a for a in aa if a['input']=='qoteey'],qoteey_recipients=[a for a in aa if a['recipient_word']=='qoteey'],qoteey_value_rows=[v for v in vv if v['material_word']=='qoteey'],input_status=dict(collections.Counter(a['input_status'] for a in aa)),meaning_confirmed=False)
(D/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({k:v for k,v in res.items() if not isinstance(v,list)}));print('inputs',res['qoteey_inputs']);print('recipients',res['qoteey_recipients']);print('qoteeyvalues',len(res['qoteey_value_rows']))
