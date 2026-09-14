from pathlib import Path
import json,hashlib,csv
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);forms={'qotchol','yteol','otchy','odaiin','cfhy','taiin'};expected=[]
for path in s['sources']:
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==s['hashes'][path]
 d=json.loads(Path(path).read_text());cols=d['group_columns'];wi=cols.index('ivtff_group_raw');ai=cols.index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');ws=[g[wi] for g in l['groups']]
  expected.extend((m['edition'],m['locus'],g[ai],g[wi],ws) for g in l['groups'] if g[wi] in forms)
o=json.loads((D/'OCCURRENCES.json').read_text());assert expected==[(r['edition'],r['locus'],r['at'],r['word'],r['words']) for r in o] and len(o)==468
cs=[r for r in o if r['left'] in {'qotaiin','shey','qotchy','sho','chkaiin'}];assert cs==json.loads((D/'CONTACTS.json').read_text()) and len(cs)==25
loci={r['locus'] for r in cs};src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}];assert ps==json.loads((D/'PARAGRAPHS.json').read_text()) and len(ps)==12
rr=list(csv.DictReader((D/'PARAGRAPH_RELATIONS.tsv').open(),delimiter='\t'));exp=[]
for p in ps:
 prior=[]
 for l in p['lines']:
  for i,w in enumerate(l['words']):
   if w not in {'qotaiin','shey','qotchy'}:continue
   exp.append((p['edition'],p['id'],l['source_ids'][i],w,prior[-1] if w=='qotchy' and prior else ''))
   if w!='qotchy':prior.append(l['source_ids'][i])
assert exp==[(r['edition'],r['paragraph'],r['at'],r['word'],r['linked_harm']) for r in rr]
v=dict(status='PASS',occurrences=468,contacts=25,paragraphs=12,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
