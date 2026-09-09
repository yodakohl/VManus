"""Pure exhaustive fitter. Input excludes source answers and all held bodies."""
import json,time
from collections import defaultdict,Counter

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def prefixes(words):return sorted({w[:n] for w in words for n in range(3) if len(w)>n})
def fit_panel(panel,template,deadline=None):
 roles=template['nodes'];training=template['training_roles'];expected={r:Counter(template['rows'][r]) for r in training}
 train=[dict(r,head=tuple(r['head']),body=[tuple(g) for g in r['body']]) for r in panel['train']]
 held=[dict(r,head=tuple(r['head'])) for r in panel['held_heads']]
 assert len({r['paragraph_id'] for r in train+held})==len(train+held)
 solutions=[];complete=True;pairs=0
 for ph in prefixes([r['head'] for r in train]):
  active=[r for r in train if len(r['head'])>len(ph) and r['head'][:len(ph)]==ph]
  hs=[r for r in held if len(r['head'])>len(ph) and r['head'][:len(ph)]==ph]
  if len({r['physical_folio'] for r in active})<5 or not hs:continue
  hb={r['paragraph_id']:r['head'][len(ph):] for r in active}
  odd_by_body=defaultdict(list);held_by_body=defaultdict(list)
  for r in active:odd_by_body[hb[r['paragraph_id']]].append(r)
  for r in hs:held_by_body[r['head'][len(ph):]].append(r['paragraph_id'])
  universe=set(odd_by_body)|set(held_by_body)
  for pc in prefixes([g for r in active for g in r['body']]):
   if deadline is not None and time.monotonic()>deadline:complete=False;break
   pairs+=1;g={};inverse_one=defaultdict(list)
   for r in active:
    count=Counter(v[len(pc):] for v in r['body'] if len(v)>len(pc) and v[:len(pc)]==pc and v[len(pc):] in universe)
    g[r['paragraph_id']]=count
    for body,n in count.items():
     if n==1:inverse_one[body].append(r)
   def partial(assignment,bodies):
    return all(g[r['paragraph_id']][bodies[j]]==expected[i][j] for i,r in assignment.items() for j in bodies)
   for b in active:
    if deadline is not None and time.monotonic()>deadline:complete=False;break
    bid=b['paragraph_id'];bb=hb[bid];gb=g[bid]
    if gb[bb]:continue
    one=[x for x,n in gb.items() if n==1 and x in odd_by_body]
    two=[x for x,n in gb.items() if n==2 and x in held_by_body and x!=bb]
    if len(one)<2 or not two:continue
    for db in one:
     for d in odd_by_body[db]:
      if d['physical_folio']==b['physical_folio'] or g[d['paragraph_id']][bb]!=1:continue
      for lb in one:
       if lb in (bb,db):continue
       for l in odd_by_body[lb]:
        if l['physical_folio'] in {b['physical_folio'],d['physical_folio']}:continue
        for cb,n in g[l['paragraph_id']].items():
         if n!=1 or cb in (bb,db,lb) or cb not in odd_by_body:continue
         for c in odd_by_body[cb]:
          if c['physical_folio'] in {b['physical_folio'],d['physical_folio'],l['physical_folio']}:continue
          assignment={'C':c,'B':b,'D':d,'L':l};bodies={'C':cb,'B':bb,'D':db,'L':lb}
          if not partial(assignment,bodies):continue
          for sb in two:
           if sb in bodies.values():continue
           bs=dict(bodies,S=sb)
           if not partial(assignment,bs):continue
           for m in inverse_one[cb]:
            mb=hb[m['paragraph_id']]
            if mb in bs.values() or m['physical_folio'] in {r['physical_folio'] for r in assignment.values()}:continue
            allb=dict(bs,M=mb);alla=dict(assignment,M=m)
            if not partial(alla,allb):continue
            solutions.append(dict(paragraphs={r:alla[r]['paragraph_id'] for r in training},prefix_head=list(ph),prefix_body=list(pc),bodies={r:list(allb[r]) for r in roles},head_forms={r:list(ph+allb[r]) for r in roles},mention_forms={r:list(pc+allb[r]) for r in roles},held_head_paragraphs=sorted(held_by_body[sb])))
   if not complete:break
  if not complete:break
 solutions.sort(key=canonical)
 assert len(solutions)==len({canonical(s) for s in solutions})
 lexicons={canonical({k:s[k] for k in ['head_forms','mention_forms']}):{k:s[k] for k in ['head_forms','mention_forms']} for s in solutions}
 return dict(complete=complete,solutions=solutions,lexicons=[lexicons[k] for k in sorted(lexicons)],prefix_pairs=pairs)
