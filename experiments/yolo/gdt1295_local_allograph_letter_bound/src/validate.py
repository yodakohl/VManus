#!/usr/bin/env python3
"""Independent raw parser, sort/group context reconstruction and subset proof."""
from pathlib import Path
import collections,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
def parse(raw,alphabet):
 options=[[] for _ in range(len(raw)+1)];options[0]=[()]
 for i in range(len(raw)):
  for u in alphabet:
   if raw.startswith(u,i):options[i+len(u)].extend(t+(u,) for t in options[i])
 assert len(options[-1])==1
 return options[-1][0]
def main():
 s=json.loads((B/'src/SPEC.json').read_text());source=(ROOT/s['source']).read_bytes();assert hashlib.sha256(source).hexdigest()==s['source_sha256']
 for p,h in json.loads((B/'src/LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 d=json.loads(gzip.decompress(source));out=json.loads((B/'artifacts/RESULT.json').read_text());saved=json.loads(gzip.decompress((B/'artifacts/CONFLICTS.json.gz').read_bytes()));checked=0;subset_checks=0
 for reader,rows in d.items():
  events=[]
  for q in rows:
   w=parse(q['ivtff_group_raw'],s['units']);assert list(w)==q['units'];checked+=1
   assert q['edition']==reader and q['kind']=='P' and q['left_separator']==q['right_separator']=='DEFINITE_SPACE'
   padded=('BOS',)+w+('EOS',)
   for j in range(1,len(padded)-1):events.append((q['page'],len(w),j-1,padded[j-1],padded[j+1],padded[j],q['id']))
  events.sort();contexts=[];allcells=repeatcells=0
  for key,ev in itertools.groupby(events,key=lambda x:x[:5]):
   members=list(ev);allcells+=1;repeatcells+=int(len(members)>1);v={}
   for z in members:v.setdefault(z[5],[]).append(z[6])
   if len(v)>1:contexts.append({'key':list(key),'centers':{u:sorted(ids) for u,ids in sorted(v.items())}})
  assert contexts==saved[reader]['conflicting_contexts']
  erows=[]
  for pair in itertools.combinations(s['units'],2):
   applicable=[c for c in contexts if all(u in c['centers'] for u in pair)]
   if not applicable:continue
   first=applicable[0];erows.append({'units':list(pair),'contexts':len(applicable),'selectors':len({c['key'][0] for c in applicable}),'physical_leaves':len({re.match(r'f(\d+)',c['key'][0])[1] for c in applicable}),'first_context':first['key'],'first_ids':[min(first['centers'][u]) for u in pair]})
  assert erows==saved[reader]['edges']
  r=out['readers'][reader];assert r['groups']==len(rows) and r['positions']==len(events) and r['all_contexts']==allcells and r['repeated_observation_contexts']==repeatcells and r['multi_center_contexts']==len(contexts)
  for name,minimum in [('FULL',1),('DISPERSED',2)]:
   graph=r['graphs'][name];es={tuple(e['units']) for e in erows if e['physical_leaves']>=minimum};assert graph['edges']==len(es)
   units=s['units'];index={u:i for i,u in enumerate(units)};adj=[0]*len(units)
   for a,b in es:adj[index[a]]|=1<<index[b];adj[index[b]]|=1<<index[a]
   anti=[((1<<len(units))-1)^adj[i]^(1<<i) for i in range(len(units))]
   def isclique(combo):
    mask=sum(1<<i for i in combo)
    return all(not(mask&anti[i]) for i in combo)
   clique=graph['maximum_clique'];m=len(clique);assert m==graph['necessary_letter_lower_bound'] and isclique(tuple(index[u] for u in clique))
   first=None
   for combo in itertools.combinations(range(len(units)),m):
    subset_checks+=1
    if isclique(combo):first=[units[i] for i in combo];break
   assert first==clique
   for combo in itertools.combinations(range(len(units)),m+1):subset_checks+=1;assert not isclique(combo)
   assert graph['excludes_K_at_most11']==(m>11)
   assert graph['clique_edge_witnesses']==[e for e in erows if tuple(e['units']) in set(itertools.combinations(clique,2))]
 expected='ALL_READERS_SMALL_LOCAL_ALLOGRAPH_ALPHABET_EXCLUDED' if all(r['graphs']['FULL']['excludes_K_at_most11'] for r in out['readers'].values()) else 'READER_SPECIFIC_NECESSARY_BOUNDS_ONLY';assert out['status']==expected
 f=json.loads((B/'artifacts/FIXTURES.json').read_text());assert f['status']=='PASS' and f['valid_two_letter_allograph_words']==62
 v={'status':'PASS','independent_raw_group_parses':checked,'graph_subset_checks':subset_checks,'graphs':6,'scope':'Independent event/edge/max-clique reconstruction, not chromatic optimum, writer construction or native meaning'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
