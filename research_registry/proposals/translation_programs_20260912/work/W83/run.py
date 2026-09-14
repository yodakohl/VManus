from pathlib import Path
import json,csv,collections,hashlib
D=Path(__file__).resolve().parent.relative_to(Path.cwd());sources=[D.parent/'W82/PARAGRAPHS.json',D.parent/'P09/MODELS.json',D.parent/'W82/MODELS.json'];ps=json.loads(sources[0].read_text());base=json.loads(sources[1].read_text())['models']['R1']['lexicon'];base.update(otchy=dict(kind='MATERIAL',meaning='Material T'),qoteey=dict(kind='MATERIAL',meaning='Material U'));base.update(json.loads(sources[2].read_text())['C'])
models={'V':dict(kind='RELATION_OR_OPERATION',meaning='erwärmen'),'H':dict(kind='QUALITY_OR_STATE',meaning='warm'),'F':dict(kind='QUALITY_OR_STATE',meaning='feucht')};events=[];al=[];md=['# W83 vollständige bedingte Lesefassungen','W82 C ist nur ein gemeinsames hypothetisches Gerüst.'];result={}
for model,shey in models.items():
 lex=base|{'shey':shey};ops={'qotchy','qotaiin','chkaiin'}|({'shey'} if model=='V' else set());ev=[]
 for p in ps:
  assert not p['page'].startswith('f84');last=lastword='';md+=['\n## '+model+' '+p['edition']+' '+p['id']]
  for l in p['lines']:
   gs=[];ws=l['words']
   for i,(w,at) in enumerate(zip(ws,l['source_ids'])):
    val={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+val+'·Uₚ' if val else lex.get(w,{}).get('meaning','⟦'+w+'⟧');gs.append(g);al.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=at,word=w,gloss=g))
    if lex.get(w,{}).get('kind')=='MATERIAL':last,lastword=at,w
    kind='VALUE' if val else 'QUALITY' if lex.get(w,{}).get('kind')=='QUALITY_OR_STATE' else 'OPERATION' if w in ops else ''
    if kind:
     inp=ws[i+1] if kind=='OPERATION' and i+1<len(ws) else '';ik=lex.get(inp,{}).get('kind');bind=kind!='OPERATION' or w in {'qotchy','chkaiin'}
     r=dict(model=model,edition=p['edition'],paragraph=p['id'],at=at,word=w,kind=kind,carrier=last if bind else '',carrier_word=lastword if bind else '',input=inp,input_status=('MISSING_INPUT' if not inp else 'ASSUMED_MATERIAL' if ik=='MATERIAL' else 'UNKNOWN_INPUT' if ik is None else 'WRONG_KNOWN_ROLE') if kind=='OPERATION' else '')
     events.append(r);ev.append(r)
   md+=['\n'+l['locus']+' `'+ ' '.join(ws)+'`','\n'+' · '.join(gs)]
 targets=[r for r in ev if r['word']=='shey'];result[model]=dict(shey_positions=len(targets),shey_kind=targets[0]['kind'],shey_missing_carrier=sum(not r['carrier'] for r in targets) if model!='V' else None,operation_status=dict(collections.Counter(r['input_status'] for r in ev if r['kind']=='OPERATION')),shey_input_status=dict(collections.Counter(r['input_status'] for r in targets)) if model=='V' else None)
for name,rows in [('ALIGNMENT.tsv',al),('EVENTS.tsv',events),('SHEY.tsv',[r for r in events if r['word']=='shey'])]:
 with (D/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');wr.writeheader();wr.writerows(rows)
(D/'READING.md').write_text('\n'.join(md)+'\n');(D/'MODELS.json').write_text(json.dumps(models,ensure_ascii=False,indent=2)+'\n');(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(D/'SOURCE_HASHES.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources+[D.parent/'W82/EVENTS.tsv',D.parent/'W82/ALIGNMENT.tsv']},indent=2)+'\n');print(json.dumps(result))
