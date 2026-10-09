import collections,gzip,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 data=json.loads(gzip.decompress((R/s['source']).read_bytes()));out=json.loads((B/'artifacts/RESULT.json').read_text());graphs=json.loads((B/'artifacts/GRAPHS.json').read_text());checks=[]
 assert [(g['reader'],g['panel']) for g in graphs]==[(r,p) for r in s['readers'] for p in s['panels']]
 for g,info in zip(graphs,out['panels']):
  allrows=data[g['reader']];types=collections.defaultdict(list)
  for row in allrows:
   assert not row['page'].startswith('f84') and row['page']!='f116v';types[tuple(row['units'])].append(row)
  selected=set()
  for word,rows in types.items():
   leafset={int(re.match(r'f([0-9]+)',row['page']).group(1)) for row in rows}
   if g['panel']=='FULL' or(g['panel']=='TYPE_COUNT_GE2' and len(rows)>=2) or(g['panel']=='PHYSICAL_LEAVES_GE2' and len(leafset)>=2):selected.add(word)
  rows=[r for r in allrows if tuple(r['units']) in selected];mass=collections.Counter();edges=collections.defaultdict(list)
  for row in rows:
   mass.update(row['units'])
   for j in range(len(row['units'])-1):edges[(row['units'][j],row['units'][j+1])].append((row,j))
  assert dict(mass)==g['unit_counts'];assert len(rows)==info['groups'] and len(selected)==info['types'];vertices=sorted(mass);assert vertices==info['active_units']
  assert info['absent_units']==sorted(set(s['working_units'])-set(vertices))
  assert {(e['from'],e['to']) for e in g['edges']}==set(edges) and info['edges']==len(edges)
  for e in g['edges']:
   hits=edges[(e['from'],e['to'])];assert e['occurrences']==len(hits) and e['whole_types']==len({tuple(row['units']) for row,j in hits})
   assert e['physical_leaves']==len({int(re.match(r'f(\d+)',row['page'])[1]) for row,j in hits})
   row,j=min(hits,key=lambda x:(-len(types[tuple(x[0]['units'])]),x[0]['id'],x[1]));assert e['witness']==row and e['witness_offset']==j and e['witness_whole_type_count']==len(types[tuple(row['units'])])
  # Independent per-vertex directed search, rather than Floyd closure.
  reach={}
  for start in vertices:
   visited={start};stack=[start]
   while stack:
    a=stack.pop()
    for x,b in edges:
     if x==a and b not in visited:visited.add(b);stack.append(b)
   reach[start]=visited
  remaining=set(vertices);components=[]
  while remaining:
   a=min(remaining);p=sorted(b for b in remaining if b in reach[a] and a in reach[b]);components.append(p);remaining-=set(p)
  assert components==info['components'] and len(components)==info['maximum_distinct_classes'];assert info['component_unit_token_mass']==[sum(mass[u] for u in p) for p in components]
  assert [c['members'] for c in g['certificates']]==components
  for c in g['certificates']:
   assert c['root']==min(c['members']) and [x['member'] for x in c['paths']]==c['members']
   for w in c['paths']:
    assert w['out'][0]==c['root'] and w['out'][-1]==w['member'] and w['back'][0]==w['member'] and w['back'][-1]==c['root']
    for p in [w['out'],w['back']]:assert set(p)<=set(c['members']) and all((a,b) in edges for a,b in zip(p,p[1:]))
  status='NO_ACTIVE_UNITS' if not vertices else 'NONTRIVIAL_FIXED_CLASS_PARTITION_EXCLUDED' if len(components)==1 else 'ORDERED_CLASS_CAPACITY_ONLY';assert status==info['status']
  checks.append({'reader':g['reader'],'panel':g['panel'],'active_units':len(vertices),'maximum_classes':len(components),'edges_reconstructed':len(edges),'certificates':'PASS'})
 val={'status':'PASS','checks':checks,'independence':'Reconstruct all scopes/edges and mutual reachability by searches; verify every raw witness/path; imports no primary program.','limits':'Exact graph condition under stated source units and boundaries, not native meanings or actual sorting history.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(val,indent=2)+'\n');print(json.dumps(val,indent=2))
if __name__=='__main__':main()
