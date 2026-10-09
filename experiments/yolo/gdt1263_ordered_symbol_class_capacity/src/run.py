import collections,gzip,hashlib,itertools,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def components(vertices,edges):
 reach={(a,a) for a in vertices}|set(edges)
 for k in vertices:
  for a in vertices:
   if (a,k) in reach:
    for b in vertices:
     if (k,b) in reach:reach.add((a,b))
 remaining=set(vertices);parts=[]
 while remaining:
  a=min(remaining);part=sorted(b for b in remaining if (a,b) in reach and (b,a) in reach);parts.append(part);remaining.difference_update(part)
 return parts

def controls():
 verts=['a','b','c'];possible=[(a,b) for a in verts for b in verts if a!=b]
 for mask in range(1<<len(possible)):
  edges=[e for j,e in enumerate(possible) if mask>>j&1];parts=components(verts,edges);n=max(len(set(rank)) for rank in itertools.product(range(3),repeat=3) if all(rank[verts.index(a)]<=rank[verts.index(b)] for a,b in edges));assert n==len(parts)
 return 64

def main():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 data=json.loads(gzip.decompress((R/s['source']).read_bytes()));graphs=[];summary=[]
 for reader in s['readers']:
  allrows=data[reader];freq=collections.Counter(tuple(r['units']) for r in allrows);leaves=collections.defaultdict(set)
  for r in allrows:
   assert not r['page'].startswith('f84') and r['page']!='f116v' and set(r['units'])<=set(s['working_units']);leaves[tuple(r['units'])].add(int(re.match(r'f(\d+)',r['page'])[1]))
  for panel in s['panels']:
   rows=[r for r in allrows if panel=='FULL' or (panel=='TYPE_COUNT_GE2' and freq[tuple(r['units'])]>=2) or (panel=='PHYSICAL_LEAVES_GE2' and len(leaves[tuple(r['units'])])>=2)]
   mass=collections.Counter(u for r in rows for u in r['units']);vertices=sorted(mass);edges=collections.defaultdict(list)
   for r in rows:
    for j,(a,b) in enumerate(zip(r['units'],r['units'][1:])):edges[(a,b)].append((r,j))
   parts=components(vertices,edges);adj={v:sorted(b for a,b in edges if a==v) for v in vertices}
   def path(start,end):
    back={start:None};todo=collections.deque([start])
    while todo and end not in back:
     here=todo.popleft()
     for nxt in adj[here]:
      if nxt not in back:back[nxt]=here;todo.append(nxt)
    assert end in back;out=[end]
    while out[-1]!=start:out.append(back[out[-1]])
    return out[::-1]
   cert=[{'members':p,'root':p[0],'paths':[{'member':v,'out':path(p[0],v),'back':path(v,p[0])} for v in p]} for p in parts]
   records=[]
   for (a,b),hits in sorted(edges.items()):
    r,j=min(hits,key=lambda z:(-freq[tuple(z[0]['units'])],z[0]['id'],z[1]));records.append({'from':a,'to':b,'occurrences':len(hits),'whole_types':len({tuple(r['units']) for r,j in hits}),'physical_leaves':len({int(re.match(r'f(\d+)',r['page'])[1]) for r,j in hits}),'witness':r,'witness_offset':j,'witness_whole_type_count':freq[tuple(r['units'])]})
   status='NO_ACTIVE_UNITS' if not vertices else 'NONTRIVIAL_FIXED_CLASS_PARTITION_EXCLUDED' if len(parts)==1 else 'ORDERED_CLASS_CAPACITY_ONLY'
   result={'reader':reader,'panel':panel,'groups':len(rows),'types':len({tuple(r['units']) for r in rows}),'active_units':vertices,'absent_units':sorted(set(s['working_units'])-set(vertices)),'edges':len(edges),'components':parts,'maximum_distinct_classes':len(parts),'component_unit_token_mass':[sum(mass[u] for u in p) for p in parts],'status':status}
   graphs.append({'reader':reader,'panel':panel,'unit_counts':dict(mass),'edges':records,'certificates':cert});summary.append(result)
 result={'status':'ALL_PANELS_FIXED_CLASS_PARTITION_EXCLUDED' if all(r['maximum_distinct_classes']==1 for r in summary) else 'PANEL_DEPENDENT_ORDERED_CLASS_CAPACITY','panels':summary,'source_free_rank_controls':controls(),'claim_ceiling':'One monotone run per group, fixed rank per working unit; no language, meaning, sorting history or general morphology claim.'}
 (B/'artifacts/GRAPHS.json').write_text(json.dumps(graphs,indent=2)+'\n');(B/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 import sys
 if '--controls' in sys.argv:print(controls())
 else:main()
