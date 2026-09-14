from pathlib import Path
import json,csv,hashlib
D=Path(__file__).resolve().parent.relative_to(Path.cwd())
for p,h in json.loads((D/'SOURCE_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);hits=[];lines=[]
for path in s['sources']:
 d=json.loads(Path(path).read_text());wi=d['group_columns'].index('ivtff_group_raw');si=d['group_columns'].index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');ws=[g[wi] for g in l['groups']];ids=[g[si] for g in l['groups']];line=dict(edition=m['edition'],page=m['page'],locus=m['locus'],words=ws,ids=ids);lines.append(line)
  hits.extend(line|dict(at=ids[i],index=i) for i,w in enumerate(ws) if w=='ychocthy')
assert hits==json.loads((D/'OCCURRENCES.json').read_text());loci={h['locus'] for h in hits};assert [l for l in lines if l['locus'] in loci]==json.loads((D/'READING_VARIANTS.json').read_text())
ps={(p['edition'],p['id']):p for p in json.loads((D.parent/'W86/PARAGRAPHS.json').read_text()) if p['page']=='f53v'}
for ed,pp in json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text()).items():
 for p in pp:
  if any(l['locus'] in loci for l in p['lines']):ps[ed,p['id']]=dict(edition=ed,**p)
assert list(ps.values())==json.loads((D/'PARAGRAPHS.json').read_text());lex=json.loads((D/'LEXICON.json').read_text());models=json.loads((D/'MODELS.json').read_text());rows=[];al=[]
for model,v in models.items():
 lx=lex|{'ychocthy':v}
 for h in hits:
  nxt=h['words'][h['index']+1:];ww=[nxt[i] if len(nxt)>i else '' for i in range(2)];ss=[]
  for w in ww:ss.append('NOT_ASSERTED' if model!='A' else 'MISSING' if not w else 'MATERIAL_ASSUMED' if lx.get(w,{}).get('kind') in {'MATERIAL','MATERIAL_DOSE'} else 'WRONG_KNOWN_ROLE' if w in lx else 'UNKNOWN')
  rows.append(dict(model=model,edition=h['edition'],locus=h['locus'],at=h['at'],next1=ww[0],next2=ww[1],argument1=ss[0],argument2=ss[1]))
 for p in ps.values():
  for l in p['lines']:
   for w,at in zip(l['words'],l['source_ids']):
    n={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+n+'·Uₚ' if n else lx.get(w,{}).get('meaning','⟦'+w+'⟧');al.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=at,word=w,gloss=g))
assert rows==list(csv.DictReader((D/'CONSEQUENCES.tsv').open(),delimiter='\t'));assert al==list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));assert len(hits)==6 and len(ps)==4 and len(al)==1356
v=dict(status='PASS',hits=6,paragraphs=4,consequences=len(rows),alignment=len(al),meaning_validated=False);(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
