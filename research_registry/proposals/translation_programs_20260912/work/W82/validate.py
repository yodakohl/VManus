from pathlib import Path
import json,csv,hashlib
D=Path(__file__).resolve().parent.relative_to(Path.cwd())
for p,h in json.loads((D/'SOURCE_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);hits=[]
for path in s['sources']:
 d=json.loads(Path(path).read_text());wc=d['group_columns'].index('ivtff_group_raw');sc=d['group_columns'].index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');ws=[g[wc] for g in l['groups']]
  for i,g in enumerate(l['groups']):
   if g[wc] in {'cthar','ochey'}:hits.append(dict(edition=m['edition'],page=m['page'],locus=m['locus'],at=g[sc],word=g[wc],left=ws[i-1] if i else '',right=ws[i+1] if i+1<len(ws) else '',words=ws))
assert hits==json.loads((D/'OCCURRENCES.json').read_text())
loci={h['locus'] for h in hits};ps={(p['edition'],p['id']):p for p in json.loads((D.parent/'W81/PARAGRAPHS.json').read_text())}
for ed,pp in json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text()).items():
 for p in pp:
  if any(l['locus'] in loci for l in p['lines']):ps[ed,p['id']]=dict(edition=ed,**p)
assert list(ps.values())==json.loads((D/'PARAGRAPHS.json').read_text())
base=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];base.update(otchy=dict(kind='MATERIAL',meaning='Material T'),qoteey=dict(kind='MATERIAL',meaning='Material U'))
events=[];al=[]
for model,extra in json.loads((D/'MODELS.json').read_text()).items():
 lex=base|extra;mat={w for w,v in lex.items() if v['kind']=='MATERIAL'}
 for p in ps.values():
  previous=[]
  for l in p['lines']:
   for i,(w,at) in enumerate(zip(l['words'],l['source_ids'])):
    val={'dair':'A','dain':'B','daiin':'C'}.get(w);gloss='Masse '+val+'·Uₚ' if val else lex.get(w,{}).get('meaning','⟦'+w+'⟧');al.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=at,word=w,gloss=gloss));previous.append((w,at))
    kind='VALUE' if val else 'QUALITY' if lex.get(w,{}).get('kind')=='QUALITY_OR_STATE' else 'OPERATION' if w in {'qotchy','qotaiin','shey','chkaiin'} else ''
    if not kind:continue
    last=next(((x,y) for x,y in reversed(previous) if x in mat),('',''));bind=kind!='OPERATION' or w in {'qotchy','chkaiin'};inp=l['words'][i+1] if kind=='OPERATION' and i+1<len(l['words']) else '';status=''
    if kind=='OPERATION':status='MISSING_INPUT' if not inp else 'ASSUMED_MATERIAL' if inp in mat else 'WRONG_KNOWN_ROLE' if inp in lex else 'UNKNOWN_INPUT'
    events.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=at,word=w,kind=kind,carrier=last[1] if bind else '',carrier_word=last[0] if bind else '',input=inp,input_status=status))
assert events==list(csv.DictReader((D/'EVENTS.tsv').open(),delimiter='\t'))
assert al==list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'))
idx={(r['model'],r['edition'],r['at']):r for r in events};changes=[]
for r in events:
 n=idx['N',r['edition'],r['at']]
 if r['model']!='N' and (r['carrier']!=n['carrier'] or r['input_status']!=n['input_status']):changes.append(r|dict(baseline_carrier=n['carrier'],baseline_carrier_word=n['carrier_word'],baseline_input_status=n['input_status']))
assert changes==list(csv.DictReader((D/'CHANGES.tsv').open(),delimiter='\t'))
assert len(hits)==58 and len(ps)==112 and len(al)==28236 and len(events)==1764 and len(changes)==138
v=dict(status='PASS',hits=len(hits),paragraphs=len(ps),alignment=len(al),events=len(events),changes=len(changes),meaning_validated=False);(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
