#!/usr/bin/env python3
import collections,gzip,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def parse(raw,units):
 paths=[[] for _ in range(len(raw)+1)];paths[0]=[()]
 for i in range(len(raw)):
  for u in units:
   if raw.startswith(u,i):paths[i+len(u)]+=[p+(u,) for p in paths[i]]
 assert len(paths[-1])==1
 return paths[-1][0]
def main():
 s=json.loads((B/'src/SPEC.json').read_text());raw=(R/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256']
 for p,h in json.loads((B/'src/LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 source=json.loads(gzip.decompress(raw));out=json.loads((B/'artifacts/RESULT.json').read_text());packet=json.loads(gzip.decompress((B/'artifacts/COUNTEREXAMPLES.json.gz').read_bytes()));checked=0
 for reader,rows in source.items():
  C={u:collections.Counter() for u in s['units']};types={u:set() for u in s['units']};pages={u:set() for u in s['units']};leaves={u:set() for u in s['units']};ids={u:[] for u in s['units']};pack={x['source']['id']:x for x in packet[reader]}
  for q in rows:
   seq=parse(q['ivtff_group_raw'],s['units']);assert list(seq)==q['units'];checked+=1
   expected={};hist=collections.Counter(seq)
   for u,count in hist.items():
    C[u]['occ']+=count;C[u]['contains']+=1;C[u]['initial']+=int(seq[0]==u)
    positions=[i for i,v in enumerate(seq) if v==u]
    if max(positions)>0:
     C[u]['bad']+=1;types[u].add(q['ivtff_group_raw']);pages[u].add(q['page']);leaves[u].add(re.match(r'f(\d+)',q['page'])[1]);ids[u].append(q['id']);expected[u]=[i for i in positions if i!=0]
   if expected:assert pack.pop(q['id'])=={'source':q,'noninitial_positions':expected}
  assert not pack
  for u,c in C.items():
   actual={'unit_occurrences':c['occ'],'groups_containing':c['contains'],'initial_groups':c['initial'],'incompatible_groups':c['bad'],'incompatible_types':len(types[u]),'selectors':len(pages[u]),'physical_leaves':len(leaves[u]),'incompatible_share_of_containing':c['bad']/c['contains'] if c['contains'] else None,'witness_ids':sorted(ids[u])[:3],'necessary_pass':bool(c['contains']) and c['bad']==0}
   assert actual==out['readers'][reader]['stats'][u]
  assert len(rows)==out['readers'][reader]['groups']
  assert out['readers'][reader]['survivors']==[u for u in s['units'] if C[u]['contains'] and not C[u]['bad']]
 expected_status='ALL_DEDICATED_PREFIX_UNITS_EXCLUDED' if all(not x['survivors'] for x in out['readers'].values()) else 'NECESSARY_CANDIDATES_ONLY';assert out['status']==expected_status
 fixtures=[('ra',True),('rar',False),('ar',False),('aa',None)]
 for w,expected in fixtures:
  got=None if 'r' not in w else all(i==0 for i,x in enumerate(w) if x=='r');assert got==expected
 v={'status':'PASS','independent_raw_unit_parses':checked,'unit_role_rows':len(s['units'])*len(source),'source_free_fixtures':len(fixtures),'scope':'Independent raw segmentation and counters; no independent native/palaeographic observation'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
