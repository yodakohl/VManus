from pathlib import Path
import json,csv,hashlib,collections
D=Path(__file__).resolve().parent.relative_to(Path.cwd());B=D.parent;sp=Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json');s=json.loads(sp.read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);hits=[];lines=[]
for path in s['sources']:
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==s['hashes'][path]
 d=json.loads(Path(path).read_text());wi=d['group_columns'].index('ivtff_group_raw');si=d['group_columns'].index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');ws=[g[wi] for g in l['groups']];ids=[g[si] for g in l['groups']];line=dict(edition=m['edition'],page=m['page'],locus=m['locus'],words=ws,ids=ids);lines.append(line)
  for i,w in enumerate(ws):
   if w in {'qodal','shodaiin'}:hits.append(line|dict(word=w,at=ids[i],index=i))
loci={r['locus'] for r in hits};src=Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json');ps={(p['edition'],p['id']):p for p in json.loads((B/'W85/PARAGRAPHS.json').read_text()) if p['page']=='f53v'}
for ed,pp in json.loads(src.read_text()).items():
 for p in pp:
  if any(l['locus'] in loci for l in p['lines']):ps[ed,p['id']]=dict(edition=ed,**p)
lex=json.loads((B/'W84/LEXICON.json').read_text())|json.loads((B/'W84/MODELS.json').read_text())['1'];old={r['form']:r for r in csv.DictReader((B/'W02/LEXICON.tsv').open(),delimiter='\t')};new={w:dict(meaning=old[w]['hypothesis'],kind=old[w]['role']) for w in ['odaiin','oky','or','sheey','shodaiin','shody']};lex.update(new)
models={'N':dict(meaning='abgemessene Materialportion',kind='MATERIAL'),'L':dict(meaning='miss das unmittelbar vorherige Material ab',kind='ACTION'),'R':dict(meaning='miss das unmittelbar folgende Material ab',kind='ACTION')};rows=[]
for model,v in models.items():
 lx=lex|{'qodal':v}
 for h in hits:
  if h['word']!='qodal':continue
  j=h['index']+(-1 if model=='L' else 1);w=h['words'][j] if 0<=j<len(h['words']) else '';at=h['ids'][j] if w else '';kind=lx.get(w,{}).get('kind');status='NO_ACTION_ASSERTED' if model=='N' else 'MISSING_PATIENT' if not w else 'ASSUMED_MATERIAL' if kind in {'MATERIAL','MATERIAL_DOSE'} else 'UNKNOWN_PATIENT' if kind is None else 'WRONG_KNOWN_ROLE';rows.append(dict(model=model,edition=h['edition'],locus=h['locus'],at=h['at'],patient=w if model!='N' else '',patient_at=at if model!='N' else '',status=status))
md=['# W86 ganze f53v-Absätze','Alle Bedeutungen hypothetisch. Keine Wirkung oder Identität ergänzt.'];al=[]
for model,v in models.items():
 lx=lex|{'qodal':v}
 for p in ps.values():
  if p['page']!='f53v':continue
  md+=['\n## '+model+' '+p['edition']+' '+p['id']]
  for l in p['lines']:
   gg=[]
   for w,at in zip(l['words'],l['source_ids']):
    val={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+val+'·Uₚ' if val else lx.get(w,{}).get('meaning','⟦'+w+'⟧');gg.append(g);al.append(dict(model=model,edition=p['edition'],at=at,word=w,gloss=g))
   md+=['\n'+l['locus']+' `'+ ' '.join(l['words'])+'`','\n'+' · '.join(gg)]
for name,rr in [('CONSEQUENCES.tsv',rows),('ALIGNMENT.tsv',al)]:
 with (D/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rr[0]),delimiter='\t');wr.writeheader();wr.writerows(rr)
for name,obj in [('OCCURRENCES.json',hits),('READING_VARIANTS.json',[l for l in lines if l['locus'] in loci]),('PARAGRAPHS.json',list(ps.values())),('LEXICON.json',lex),('ADDITIONS.json',new),('MODELS.json',models)]: (D/name).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')
(D/'READING.md').write_text('\n'.join(md)+'\n');r=dict(hits=dict(collections.Counter(h['word']+'|'+h['edition'] for h in hits)),paragraphs=len(ps),qodal_loci=len({h['locus'] for h in hits if h['word']=='qodal'}),models={m:dict(collections.Counter(r['status'] for r in rows if r['model']==m)) for m in models},meaning_confirmed=False);(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');paths=[sp,Path(s['allow_source']),src,B/'W85/PARAGRAPHS.json',B/'W84/LEXICON.json',B/'W84/MODELS.json',B/'W02/LEXICON.tsv']+[Path(p) for p in s['sources']];(D/'SOURCE_HASHES.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n');print(json.dumps(r))
