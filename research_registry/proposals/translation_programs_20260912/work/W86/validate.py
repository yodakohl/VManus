from pathlib import Path
import json,csv,hashlib
D=Path(__file__).resolve().parent.relative_to(Path.cwd())
for p,h in json.loads((D/'SOURCE_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
sp=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(sp['allow_source']).read_text())['allowed_selectors']);hits=[];lines=[]
for path in sp['sources']:
 d=json.loads(Path(path).read_text());wi=d['group_columns'].index('ivtff_group_raw');si=d['group_columns'].index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');ws=[g[wi] for g in l['groups']];ids=[g[si] for g in l['groups']];line=dict(edition=m['edition'],page=m['page'],locus=m['locus'],words=ws,ids=ids);lines.append(line)
  hits.extend(line|dict(word=w,at=ids[i],index=i) for i,w in enumerate(ws) if w in {'qodal','shodaiin'})
assert hits==json.loads((D/'OCCURRENCES.json').read_text());loci={r['locus'] for r in hits};assert [l for l in lines if l['locus'] in loci]==json.loads((D/'READING_VARIANTS.json').read_text())
lex=json.loads((D/'LEXICON.json').read_text());models=json.loads((D/'MODELS.json').read_text());expected=[]
for m,v in models.items():
 lx=lex|{'qodal':v}
 for h in hits:
  if h['word']!='qodal':continue
  left=h['words'][:h['index']];right=h['words'][h['index']+1:];w=(left[-1] if left else '') if m=='L' else (right[0] if right else '');j=h['index']+(-1 if m=='L' else 1);kind=lx.get(w,{}).get('kind');st='NO_ACTION_ASSERTED' if m=='N' else 'MISSING_PATIENT' if not w else 'ASSUMED_MATERIAL' if kind in {'MATERIAL','MATERIAL_DOSE'} else 'UNKNOWN_PATIENT' if kind is None else 'WRONG_KNOWN_ROLE'
  expected.append(dict(model=m,edition=h['edition'],locus=h['locus'],at=h['at'],patient=w if m!='N' else '',patient_at=h['ids'][j] if w and m!='N' else '',status=st))
assert expected==list(csv.DictReader((D/'CONSEQUENCES.tsv').open(),delimiter='\t'))
ps={(p['edition'],p['id']):p for p in json.loads((D.parent/'W85/PARAGRAPHS.json').read_text()) if p['page']=='f53v'}
for ed,pp in json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text()).items():
 for p in pp:
  if any(l['locus'] in loci for l in p['lines']):ps[ed,p['id']]=dict(edition=ed,**p)
assert list(ps.values())==json.loads((D/'PARAGRAPHS.json').read_text());al=[]
for m,v in models.items():
 lx=lex|{'qodal':v}
 for p in ps.values():
  if p['page']!='f53v':continue
  for l in p['lines']:
   for w,at in zip(l['words'],l['source_ids']):
    n={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+n+'·Uₚ' if n else lx.get(w,{}).get('meaning','⟦'+w+'⟧');al.append(dict(model=m,edition=p['edition'],at=at,word=w,gloss=g))
assert al==list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'))
v=dict(status='PASS',hits=len(hits),paragraphs=len(ps),consequences=len(expected),alignment=len(al),meaning_validated=False);(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
