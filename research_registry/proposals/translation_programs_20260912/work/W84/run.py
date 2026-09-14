from pathlib import Path
import json,csv,hashlib,collections
D=Path(__file__).resolve().parent.relative_to(Path.cwd());spec=Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json');s=json.loads(spec.read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);hits=[];all_lines=[]
for path in s['sources']:
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==s['hashes'][path]
 d=json.loads(Path(path).read_text());wi=d['group_columns'].index('ivtff_group_raw');si=d['group_columns'].index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');ws=[g[wi] for g in l['groups']];all_lines.append(dict(edition=m['edition'],page=m['page'],locus=m['locus'],words=ws))
  for i,w in enumerate(ws):
   if w in {'tshor','tchaly','chtols'}:hits.append(dict(edition=m['edition'],page=m['page'],locus=m['locus'],at=l['groups'][i][si],word=w,left=ws[i-1] if i else '',right=ws[i+1] if i+1<len(ws) else '',words=ws))
source=Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json');loci={h['locus'] for h in hits};(D/'READING_VARIANTS.json').write_text(json.dumps([l for l in all_lines if l['locus'] in loci],ensure_ascii=False,indent=2)+'\n');ps={(p['edition'],p['id']):p for p in json.loads((D.parent/'W82/PARAGRAPHS.json').read_text())}
for ed,pp in json.loads(source.read_text()).items():
 for p in pp:
  if loci & {l['locus'] for l in p['lines']}:ps[(ed,p['id'])]=dict(edition=ed,**p)
base=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];base.update(otchy=dict(kind='MATERIAL',meaning='Material T'),qoteey=dict(kind='MATERIAL',meaning='Material U'))
base.update(cthar=dict(kind='MATERIAL',meaning='Krautportion'),shey=dict(kind='QUALITY_OR_STATE',meaning='feucht'))
names=['tshor','tchaly','chtols'];models={''.join(str(i+1) for i in range(3) if mask&(1<<i)) or 'N':{w:dict(kind='MATERIAL',meaning='Material ['+w+']') for i,w in enumerate(names) if mask&(1<<i)} for mask in range(8)}
rows=[];al=[];read=['# W82 vollständige hypothetische Fassungen','Alle Bedeutungen und Bindungen sind Annahmen; unbekannte Wörter bleiben sichtbar.'];summary={}
for model,extra in models.items():
 lex=base|extra;events=[]
 for p in ps.values():
  last=lastword='';read+=['\n## '+model+' '+p['edition']+' '+p['id']]
  for l in p['lines']:
   gloss=[];ws=l['words']
   for i,(w,at) in enumerate(zip(ws,l['source_ids'])):
    val={'dair':'A','dain':'B','daiin':'C'}.get(w);g=('Masse '+val+'·Uₚ') if val else lex.get(w,{}).get('meaning','⟦'+w+'⟧');gloss.append(g);al.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=at,word=w,gloss=g))
    if lex.get(w,{}).get('kind')=='MATERIAL':last,lastword=at,w
    kind='VALUE' if val else 'QUALITY' if lex.get(w,{}).get('kind')=='QUALITY_OR_STATE' else 'OPERATION' if w in {'qotchy','qotaiin','chkaiin'} else ''
    if kind:
     inp=ws[i+1] if kind=='OPERATION' and i+1<len(ws) else '';ik=lex.get(inp,{}).get('kind');bind=kind!='OPERATION' or w in {'qotchy','chkaiin'}
     r=dict(model=model,edition=p['edition'],paragraph=p['id'],at=at,word=w,kind=kind,carrier=last if bind else '',carrier_word=lastword if bind else '',input=inp,input_status=('MISSING_INPUT' if not inp else 'ASSUMED_MATERIAL' if ik=='MATERIAL' else 'UNKNOWN_INPUT' if ik is None else 'WRONG_KNOWN_ROLE') if kind=='OPERATION' else '')
     rows.append(r);events.append(r)
   read += ['\n'+l['locus']+' `'+ ' '.join(ws)+'`','\n'+' · '.join(gloss)]
 summary[model]=dict(events=len(events),input_status=dict(collections.Counter(r['input_status'] for r in events if r['kind']=='OPERATION')),U_dry=[r['at'] for r in events if r['kind']=='QUALITY' and r['carrier_word']=='qoteey' and r['word'] in {'chol','oltchy'}])
lookup={(r['model'],r['edition'],r['at']):r for r in rows};changes=[]
for r in rows:
 n=lookup['N',r['edition'],r['at']]
 if r['model']!='N' and any(r[k]!=n[k] for k in ['carrier','input_status']):changes.append(r|dict(baseline_carrier=n['carrier'],baseline_carrier_word=n['carrier_word'],baseline_input_status=n['input_status']))
for name,rr in [('EVENTS.tsv',rows),('CHANGES.tsv',changes)]:
 with (D/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rr[0]),delimiter='\t');wr.writeheader();wr.writerows(rr)
for name,obj in [('OCCURRENCES.json',hits),('PARAGRAPHS.json',list(ps.values())),('MODELS.json',models)]: (D/name).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')
(D/'LEXICON.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n')
r=dict(hits=len(hits),counts=dict(collections.Counter(h['word']+'|'+h['edition'] for h in hits)),loci=len(loci),paragraphs=len(ps),groups=len(al)//8,models=summary,changed_events=len(changes),meaning_confirmed=False)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
paths=[spec,Path(s['allow_source']),source,D.parent/'W82/PARAGRAPHS.json',D.parent/'P09/MODELS.json']+[Path(p) for p in s['sources']]
(D/'SOURCE_HASHES.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n');print(json.dumps(r))
