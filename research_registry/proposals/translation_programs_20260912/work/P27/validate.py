#!/usr/bin/env python3
import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P27');read=lambda n:list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text())
for r in s['sources']:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
m=json.loads((D/'MODEL.json').read_text());rels=read('RELATIONS.tsv');chains=read('PRODUCT_USES.tsv')
source=json.loads(Path(s['sources'][0]['path']).read_text())['lines'];bath=list(csv.DictReader(Path(s['sources'][1]['path']).open(),delimiter='\t'))
raw=[(r['locus']+':'+str(i),w) for r in source for i,w in enumerate(r['groups'],1)]+[(r['locus']+':'+str(i),w) for r in bath for i,w in enumerate(r['zl3b_line'].split(),1)]
for world in ['M','B']:
 for identity in ['FRESH','REUSE']:
  a=read('ALIGNMENT_'+world+'_'+identity+'.tsv');assert [(x['locus'],x['word']) for x in a]==raw and len(a)==486
  index={x['locus']:i for i,x in enumerate(a)};lookup={x['locus']:x for x in a};rr=[r for r in rels if r['world']==world and r['identity']==identity];assert len(rr)==30
  er={r['locus']:r for r in rr}
  for r in rr:
   assert lookup[r['locus']]['word'] in m['relations']
   for side in ['left','right']:
    loc=r[side+'_locus']
    if loc=='MISSING':continue
    x=lookup[loc];assert x['record']==r['record'] and x['word']==r[side+'_word'] and x['entity_id']==r[side+'_id']
    assert (index[loc]<index[r['locus']]) if side=='left' else (index[loc]>index[r['locus']])
   if r['right_locus']!='MISSING':
    mid=a[index[r['locus']]+1:index[r['right_locus']]]
    assert all(x['word'] not in m[world] and x['word'] not in m['relations'] for x in mid)
    assert (' '.join(x['word'] for x in mid) or 'NONE')==r['intervening_words']
  for c in chains:
   if c['world']!=world or c['identity']!=identity:continue
   p=er[c['producer']];q=er[c['consumer']];assert p['relation']=='BECOMES' and p['right_id']==q['left_id']==c['product_id']
   assert index[p['right_locus']]<index[q['locus']]
   assert int(c['producer_complete'])==int(p['left_id']!='MISSING')
   assert int(c['consumer_complete'])==int(q['right_id']!='MISSING')
  # Independent transitive closure for each directed relation graph.
  expected=set()
  for rec in {r['record'] for r in rr}:
   for graph in ['MEREOLOGY','ORIGIN','TRANSFORMATION']:
    edges=[]
    for r in rr:
     if r['record']!=rec or 'MISSING' in [r['left_id'],r['right_id']]:continue
     role=r['relation'];x,y=r['left_id'],r['right_id']
     if graph=='MEREOLOGY' and role in ['PART_OF','CONTAINS']:edges.append((y,x,r['locus']) if role=='PART_OF' else (x,y,r['locus']))
     if graph=='ORIGIN' and role=='FROM':edges.append((x,y,r['locus']))
     if graph=='TRANSFORMATION' and role=='BECOMES':edges.append((x,y,r['locus']))
    reach={(x,y) for x,y,z in edges}
    while True:
     new=reach|{(x,v) for x,y in reach for u,v in reach if y==u}
     if new==reach:break
     reach=new
    expected|={(rec,graph,z) for x,y,z in edges if (y,x) in reach}
  observed={(x['record'],x['graph'],x['edge']) for x in read('CYCLES.tsv') if x['world']==world and x['identity']==identity};assert expected==observed
out={'status':'PASS','scope':'four full source sequences; all120relation rows; all product links with both endpoint completeness flags; independent graph closure; no semantic validation','confirmed_meanings':0}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
