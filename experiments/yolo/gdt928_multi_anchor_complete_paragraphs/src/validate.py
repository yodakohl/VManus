"""Independent direct matching and complete trigram pair coverage; no run import."""
import collections, hashlib, itertools, json, re
from pathlib import Path
E=Path(__file__).resolve().parents[1]; R=E.parents[2]
for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():
 assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
panels=json.loads((E/'artifacts/PARAGRAPHS.json').read_text()); results=json.loads((E/'artifacts/PAIRS.json').read_text()); counts={}
P=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
allowed=set(json.loads((P/'src/SPEC.json').read_text())['allowed_selectors'])
for ed,paras in panels.items():
 raw={}; pages=collections.defaultdict(list)
 for phase in ['DISCOVERY','EVALUATION']:
  d=json.loads((P/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text())
  for row in d['lines']:
   m=row['metadata']; assert m['page'] in allowed and not m['page'].startswith('f84')
   if m['kind']=='P':
    gs=[dict(zip(d['group_columns'],g)) for g in row['groups']]
    raw[m['locus']]=(m,gs); pages[m['page']].append(m)
 expected=set()
 for page,ms in pages.items():
  ms.sort(key=lambda m:int(m['source_row_index']))
  for i,m in enumerate(ms):
   if m['paragraph_start']!='1':continue
   for j in range(i,len(ms)):
    if j>i and ms[j]['paragraph_start']=='1':break
    if ms[j]['paragraph_end']=='1':
     ns=[int(x['locus'].split('.')[-1]) for x in ms[i:j+1]]
     if ns==list(range(ns[0],ns[0]+len(ns))):expected.add(page+'|'+m['locus']+'-'+ms[j]['locus'])
     break
 assert expected=={p['id'] for p in paras}
 idx=collections.defaultdict(set); pm={p['id']:p for p in paras}
 for p in paras:
  off=0
  for l in p['lines']:
   m,gs=raw[l['locus']];w=[g['ivtff_group_raw'] for g in gs]
   assert w==l['words'] and l['source_ids']==[g['source_group_id'] for g in gs] and l['offset']==off
   eligible=len(w)>=2 and all(re.fullmatch('[a-z]+',x) for x in w) and all(a['right_separator']==b['left_separator']=='DEFINITE_SPACE' and int(b['source_group_index'])-int(a['source_group_index'])==1 for a,b in zip(gs,gs[1:]))
   assert eligible==l['anchor_eligible'];off+=len(w)
   if eligible:
    for i in range(len(w)-2):
     t=tuple(w[i:i+3])
     if len(set(t))>1:idx[t].add(p['id'])
  assert off==p['groups']
 coverage=set()
 for ids in idx.values():
  coverage.update((a,b) for a,b in itertools.combinations(sorted(ids),2) if pm[a]['leaf']!=pm[b]['leaf'])
 assert coverage=={(p['a'],p['b']) for p in results[ed]}
 for pair in results[ed]:
  direct=set()
  for a in pm[pair['a']]['lines']:
   if not a['anchor_eligible']:continue
   for b in pm[pair['b']]['lines']:
    if not b['anchor_eligible']:continue
    x,y=a['words'],b['words']
    for i in range(len(x)):
     for j in range(len(y)):
      if i and j and x[i-1]==y[j-1]:continue
      n=0
      while i+n<len(x) and j+n<len(y) and x[i+n]==y[j+n]:n+=1
      if n>=3 and len(set(x[i:i+n]))>1:direct.add((a['locus'],i,b['locus'],j,n))
  assert direct=={(m['a_locus'],m['a_start'],m['b_locus'],m['b_start'],m['length']) for m in pair['matches']}
  ds=[]
  for i,j in itertools.combinations(range(len(pair['matches'])),2):
   a,b=pair['matches'][i],pair['matches'][j]
   aset=set(range(a['a_offset'],a['a_offset']+a['length'])); bset=set(range(b['a_offset'],b['a_offset']+b['length']))
   cset=set(range(a['b_offset'],a['b_offset']+a['length'])); dset=set(range(b['b_offset'],b['b_offset']+b['length']))
   if not aset&bset and not cset&dset:ds.append((i,j))
  assert ds==[(x['match1'],x['match2']) for x in pair['disjoint_match_pairs']]
  assert pair['qualifies']==bool(ds)
 counts[ed]={'complete_paragraphs':len(paras),'directly_checked_pairs':len(coverage),'qualifying_pairs':sum(p['qualifies'] for p in results[ed])}
out={'status':'PASS','checks':['input and preregistration hashes','independent complete paragraph coverage','raw group provenance and eligibility','all shared trigram pair coverage','direct maximal substring enumeration','independent interval disjointness'],'panels':counts}
(E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
