from pathlib import Path
import json,csv,hashlib,collections
D=Path(__file__).resolve().parent.relative_to(Path.cwd());B=D.parent;sp=Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json');s=json.loads(sp.read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);hits=[];lines=[]
for path in s['sources']:
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==s['hashes'][path]
 d=json.loads(Path(path).read_text());wi=d['group_columns'].index('ivtff_group_raw');si=d['group_columns'].index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');ws=[g[wi] for g in l['groups']];ids=[g[si] for g in l['groups']];line=dict(edition=m['edition'],page=m['page'],locus=m['locus'],words=ws,ids=ids);lines.append(line)
  hits.extend(line|dict(at=ids[i],index=i) for i,w in enumerate(ws) if w=='ychocthy')
loci={r['locus'] for r in hits};src=Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json');ps={(p['edition'],p['id']):p for p in json.loads((B/'W86/PARAGRAPHS.json').read_text()) if p['page']=='f53v'}
for ed,pp in json.loads(src.read_text()).items():
 for p in pp:
  if any(l['locus'] in loci for l in p['lines']):ps[ed,p['id']]=dict(edition=ed,**p)
lex=json.loads((B/'W86/LEXICON.json').read_text())|{'qodal':json.loads((B/'W86/MODELS.json').read_text())['N']};models={'A':dict(meaning='vermische',kind='MIX'),'M':dict(meaning='Krautpräparat',kind='MATERIAL'),'D':dict(meaning='ferner',kind='DISCOURSE')};rows=[];al=[];md=['# W87 ganze Kontextabsätze','Alle Ganzwortwerte hypothetisch. A nimmt die nächsten zwei geschriebenen Gruppen, M/D behaupten keine Mischhandlung.']
for model,v in models.items():
 lx=lex|{'ychocthy':v}
 for h in hits:
  nxt=h['words'][h['index']+1:h['index']+3];status=[]
  for i in range(2):
   w=nxt[i] if i<len(nxt) else '';k=lx.get(w,{}).get('kind');status.append('MISSING' if not w else 'MATERIAL_ASSUMED' if k in {'MATERIAL','MATERIAL_DOSE'} else 'UNKNOWN' if k is None else 'WRONG_KNOWN_ROLE')
  rows.append(dict(model=model,edition=h['edition'],locus=h['locus'],at=h['at'],next1=nxt[0] if nxt else '',next2=nxt[1] if len(nxt)>1 else '',argument1=status[0] if model=='A' else 'NOT_ASSERTED',argument2=status[1] if model=='A' else 'NOT_ASSERTED'))
 for p in ps.values():
  md+=['\n## '+model+' '+p['edition']+' '+p['id']]
  for l in p['lines']:
   gg=[]
   for w,at in zip(l['words'],l['source_ids']):
    val={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+val+'·Uₚ' if val else lx.get(w,{}).get('meaning','⟦'+w+'⟧');gg.append(g);al.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=at,word=w,gloss=g))
   md+=['\n'+l['locus']+' `'+ ' '.join(l['words'])+'`','\n'+' · '.join(gg)]
for name,rr in [('CONSEQUENCES.tsv',rows),('ALIGNMENT.tsv',al)]:
 with (D/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rr[0]),delimiter='\t');wr.writeheader();wr.writerows(rr)
for name,obj in [('OCCURRENCES.json',hits),('READING_VARIANTS.json',[l for l in lines if l['locus'] in loci]),('PARAGRAPHS.json',list(ps.values())),('LEXICON.json',lex),('MODELS.json',models)]: (D/name).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')
(D/'READING.md').write_text('\n'.join(md)+'\n');r=dict(hits=len(hits),readings=dict(collections.Counter(h['edition'] for h in hits)),loci=sorted(loci),paragraphs=len(ps),groups=len(al)//3,action_cases=[r for r in rows if r['model']=='A'],meaning_confirmed=False);(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');paths=[sp,Path(s['allow_source']),src,B/'W86/PARAGRAPHS.json',B/'W86/LEXICON.json',B/'W86/MODELS.json']+[Path(p) for p in s['sources']];(D/'SOURCE_HASHES.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n');print(json.dumps(r))
