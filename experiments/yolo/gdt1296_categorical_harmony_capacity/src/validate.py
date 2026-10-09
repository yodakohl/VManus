#!/usr/bin/env python3
import gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def parse(raw,units):
 dp=[[] for _ in range(len(raw)+1)];dp[0]=[()]
 for pos in range(len(raw)):
  for u in units:
   if raw.startswith(u,pos):dp[pos+len(u)].extend(x+(u,) for x in dp[pos])
 assert len(dp[-1])==1
 return dp[-1][0]
def main():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 raw=(R/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];data=json.loads(gzip.decompress(raw));result=json.loads((B/'artifacts/RESULT.json').read_text());candidate=json.loads(gzip.decompress((B/'artifacts/CANDIDATES.json.gz').read_bytes()));graphs=json.loads((B/'artifacts/COOCCURRENCE.json').read_text());support=json.loads((B/'artifacts/BEST_SUPPORT.json').read_text());units=s['units'];idx={u:i for i,u in enumerate(units)};total=0;subsets=0
 for reader,rows in data.items():
  seen=[set() for _ in units];byid={}
  for j,q in enumerate(rows):
   seq=parse(q['ivtff_group_raw'],units);assert list(seq)==q['units']
   assert q['kind']=='P' and q['left_separator']==q['right_separator']=='DEFINITE_SPACE'
   assert not q['page'].startswith('f84') and q['page']!='f116v' and q['id'] not in byid
   byid[q['id']]=q
   for u in set(seq):seen[idx[u]].add(j)
   total+=1
  assert all(seen)
  co=[];compatible={i:set() for i in range(len(units))}
  for i,j in itertools.combinations(range(len(units)),2):
   common=seen[i]&seen[j]
   if common:co.append({'units':[units[i],units[j]],'groups':len(common),'first_id':min(rows[k]['id'] for k in common)})
   else:compatible[i].add(j);compatible[j].add(i)
  assert co==graphs[reader]
  # Every valid B contains a pair. Its common compatible vertices contain all of A.
  allA=set();domains=set()
  for i,j in itertools.combinations(range(len(units)),2):
   allowed=compatible[i]&compatible[j];mask=sum(1<<x for x in allowed)
   if len(allowed)<2 or mask in domains:continue
   domains.add(mask);part=mask
   while part:
    if part.bit_count()>=2:allA.add(tuple(i for i in range(len(units)) if part>>i&1))
    part=(part-1)&mask
  rebuilt=[]
  for a in sorted(allA):
   hit=set().union(*(seen[i] for i in a));b=[j for j in range(len(units)) if j not in a and not(hit&seen[j])];assert len(b)>=2
   hb=set().union(*(seen[j] for j in b));assert not(hit&hb);ca=len(hit);cb=len(hb)
   rebuilt.append({'A':list(a),'Bmax':b,'A_groups':ca,'B_groups':cb,'balanced_groups':min(ca,cb),'covered_groups':ca+cb});subsets+=1
  assert rebuilt==candidate[reader]
  def key(c):return (-c['balanced_groups'],-c['covered_groups'],tuple(sorted((tuple(c['A']),tuple(c['Bmax'])))))
  best=min(rebuilt,key=key) if rebuilt else None;N=len(rows);r=result['readers'][reader]
  assert r['groups']==N and r['cooccurrence_edges']==len(co) and r['eligible_A_subsets']==len(rebuilt)
  expected=None if best is None else {**best,'A_units':[units[i] for i in best['A']],'B_units':[units[i] for i in best['Bmax']],'balanced_fraction':best['balanced_groups']/N}
  assert r['best']==expected
  status='NO_ASSIGNMENT' if best is None else 'NECESSARY_CAPACITY_ONLY' if 20*best['balanced_groups']>=N else 'LOW_ACTIVITY';assert r['status']==status
  if best:
   assert 2*best['balanced_groups']<=N
   for role,indices in [('A',best['A']),('B',best['Bmax'])]:assert support[reader][role]==[q['id'] for j,q in enumerate(rows) if any(j in seen[i] for i in indices)]
  else:assert support[reader]=={}
 expected='COMMON_CATEGORICAL_HARMONY_EXCLUDED' if all(v['status'] in ['NO_ASSIGNMENT','LOW_ACTIVITY'] for v in result['readers'].values()) else 'NECESSARY_CAPACITY_OR_UNSCORABLE';assert result['status']==expected
 f=json.loads((B/'artifacts/FIXTURES.json').read_text());assert f['status']=='PASS' and f['all_five_vertex_graphs']==1024
 v={'status':'PASS','independent_raw_group_parses':total,'independent_seed_pair_A_subsets':subsets,'reader_graphs':3,'scope':'Exactcapacityvalue/representativeandallreducedcandidatesverified;notphonology,meaningorallsmallerBlisting'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
