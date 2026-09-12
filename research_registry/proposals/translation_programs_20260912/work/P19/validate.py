import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P19')
def rr(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
src=json.loads((D/'SOURCE.json').read_text())
for p,h in src['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
lines=[]
for r in json.loads((D.parent/'P11/INPUT.json').read_text())['lines']:lines.append((r['locus'].split('.')[0],r['locus'],r['raw_line'],'HERB4',r['locus'].split('.')[0]))
for folder in ['P12','P28']:
 for r in csv.DictReader((D.parent/folder/'PROSE.tsv').open(),delimiter='\t'):lines.append((r['record_id'],r['locus'],r['zl3b_line'],'BATH3',r['page']))
lines.sort(key=lambda r:0 if r[4]=='f17r' else 1 if r[0]=='F83_P1' else 2)
flat=[]
for rec,line,words,pkg,page in lines:
 for i,w in enumerate(words.split(),1):flat.append((rec,line,f'{line}:{i}',w,pkg,page))
assert [(r['record'],r['line'],r['locus'],r['word'],r['package'],r['page']) for r in rr('INPUT.tsv')]==flat
norm=lambda w:w[:-4]+'ain' if w[-4:]=='aiin' else w
heads={'cthy','chor','ctho','cthaiin','okaiin','shedy','lchedy','qokaiin'};verbs={'chedy','qokeedy','sho','qotchy'};ops=rr('OPERATIONS.tsv');qs=rr('QUANTITIES.tsv')
for mode in ['E','N','G']:
 lex={norm(w) if mode=='N' else w for w in heads};dest=norm('qokaiin') if mode=='N' else 'qokaiin';complete=[]
 for j,t in enumerate(flat):
  transform=norm if mode=='N' else lambda w:w
  w=transform(t[3]);prefix=[(x,transform(x[3])) for x in flat[:j] if x[0]==t[0]]
  materials=[x for x,k in prefix if k in lex and k!=dest];ds=[x for x,k in prefix if k==dest]
  if w in verbs:
   o=next(o for o in ops if o['mode']==mode and o['locus']==t[2]);missing=[]
   if not materials:missing.append('MATERIAL')
   if w=='qokeedy' and not ds:missing.append('DESTINATION')
   status='COMPLETE' if not missing else 'MISSING_'+'_AND_'.join(missing)
   assert o['status']==status
   assert (o['material'],o['material_source'])==((transform(materials[-1][3]),materials[-1][2]) if materials else ('NA','NA'))
   assert (o['destination'],o['destination_source'])==((dest,ds[-1][2]) if ds and w=='qokeedy' else ('NA','NA'))
   if not missing:complete.append(t)
  elif w in ({'dain'} if mode=='N' else {'daiin','dain'}):
   q=next(q for q in qs if q['mode']==mode and q['locus']==t[2]);duration=mode=='G' and t[4]=='BATH3';prev=[x for x in complete if x[0]==t[0]] if duration else materials
   assert q['dimension']==('DURATION' if duration else 'MATERIAL_AMOUNT')
   assert q['value']==('Q' if mode=='N' or w=='daiin' else 'R')
   assert q['reference_source']==(prev[-1][2] if prev else 'NA')
   assert q['status']==('BOUND' if prev else 'MISSING_REFERENCE')
 aa=rr(f'ALIGNMENT_{mode}.tsv');assert [(r['record'],r['line'],r['locus'],r['word'],r['package'],r['page']) for r in aa]==flat
 assert all(r['normalized']==(norm(r['word']) if mode=='N' else r['word']) for r in aa)
 assert all(r['rendering']=='⟦'+r['word']+'⟧' for r in aa if r['kind']=='OPEN')
 text=(D/f'READING_{mode}.md').read_text();assert all('`'+l[2]+'`' in text for l in lines)
 res=json.loads((D/'RESULT.json').read_text())['models'][mode]
 assert res['operations']==dict(Counter(o['status'] for o in ops if o['mode']==mode))
 assert res['quantities']==dict(Counter(q['status'] for q in qs if q['mode']==mode))
 assert res['hypothesis']==sum(r['kind']!='OPEN' for r in aa)
fam=rr('ALL_VARIANT_FAMILIES.tsv');counts=Counter(t[3] for t in flat)
assert {f['long'] for f in fam}=={w for w in counts if w.endswith('aiin')}
for f in fam:assert int(f['long_count'])==counts[f['long']] and int(f['short_count'])==counts[norm(f['long'])]
meta=rr('METADATA_PROJECTION.tsv');assert len(meta)==198
assert {r['page'] for r in meta}=={t[5] for t in flat}
assert {(r['hand'],r['section'],r['language']) for r in meta}=={('1','H','A'),('2','B','B')}
changes=[]
for e in ops:
 if e['mode']!='E':continue
 n=next(o for o in ops if o['mode']=='N' and o['locus']==e['locus'])
 if (norm(e['material']),e['material_source'],norm(e['destination']),e['destination_source'],e['status'])!=(n['material'],n['material_source'],n['destination'],n['destination_source'],n['status']):changes.append(e['locus'])
assert changes==[c['locus'] for c in rr('CHANGED_ACTION_BINDINGS.tsv')]
assert len(changes)==6 and len(flat)==1085
receipt={'status':'PASS','source_hashes':len(src['inputs']),'groups_per_reading':1085,'full_readings':3,'independent_action_rows':len(ops),'independent_quantity_rows':len(qs),'normalization_families':len(fam),'changed_bindings':6,'checks':['all bounded source lines preserved','global terminal normalization','prefix-only material and destination','duration binds last complete event','whole family census','metadata confounding','semantic-source change comparison'],'limit':'Internal consequences only; no meanings or actual scribal convention verified.'}
(D/'VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
