#!/usr/bin/env python3
import collections,gzip,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 raw=(R/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];data=json.loads(gzip.decompress(raw));result={};pack={}
 for reader in s['readers']:
  rows=data[reader];stats={};badrows=[]
  for q in rows:
   assert q['edition']==reader and q['kind']=='P' and q['left_separator']==q['right_separator']=='DEFINITE_SPACE'
   assert not q['page'].startswith('f84') and q['page']!='f116v'
   assert ''.join(q['units'])==q['ivtff_group_raw'] and set(q['units'])<=set(s['units'])
   pos={u:[i for i,v in enumerate(q['units']) if v==u and i>0] for u in set(q['units'][1:])}
   if pos:badrows.append({'source':q,'noninitial_positions':pos})
  for u in s['units']:
   contains=[q for q in rows if u in q['units']];bad=[q for q in contains if u in q['units'][1:]]
   stats[u]={'unit_occurrences':sum(q['units'].count(u) for q in contains),'groups_containing':len(contains),'initial_groups':sum(q['units'][0]==u for q in contains),'incompatible_groups':len(bad),'incompatible_types':len(set(q['ivtff_group_raw'] for q in bad)),'selectors':len(set(q['page'] for q in bad)),'physical_leaves':len(set(re.match(r'f(\d+)',q['page']).group(1) for q in bad)),'incompatible_share_of_containing':len(bad)/len(contains) if contains else None,'witness_ids':[q['id'] for q in sorted(bad,key=lambda q:q['id'])[:3]],'necessary_pass':bool(contains) and not bad}
  result[reader]={'groups':len(rows),'stats':stats,'survivors':[u for u,z in stats.items() if z['necessary_pass']]};pack[reader]=sorted(badrows,key=lambda z:z['source']['id'])
 status='ALL_DEDICATED_PREFIX_UNITS_EXCLUDED' if all(not z['survivors'] for z in result.values()) else 'NECESSARY_CANDIDATES_ONLY'
 out={'status':status,'readers':result,'scope':'Fixed22unitandstrictwholegroup exclusive-initial role only; not general abbreviation or meaning'}
 (B/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
 (B/'artifacts/COUNTEREXAMPLES.json.gz').write_bytes(gzip.compress(json.dumps(pack,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 print(json.dumps({'status':status,'readers':{r:{'survivors':z['survivors'],'smallest_exception_counts':sorted([(u,v['incompatible_groups'],v['groups_containing']) for u,v in z['stats'].items()],key=lambda x:x[1])[:5]} for r,z in result.items()}},indent=2))
if __name__=='__main__':main()
