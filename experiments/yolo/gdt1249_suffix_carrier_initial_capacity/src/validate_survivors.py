"""Independent dynamic-programming literal membership and source check."""
from pathlib import Path
import json,gzip,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
S=json.loads((D/'src/SPEC.json').read_text());R=json.loads((A/'RESULT.json').read_text());C=json.loads((A/'POST_RESULT_SURVIVOR_CHECK.json').read_text())
raw=(ROOT/S['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==S['source_sha256']
source=json.loads(gzip.decompress(raw));byid={r['id']:r for rows in source.values() for r in rows}
expected=set()
for ed,d in R['readers'].items():
 for w in next(h for h in d['heads'] if h['head']=='a')['witnesses']:
  if w['follower'] in ['i','n','m']:expected.add((ed,w['follower'],w['id']))
expected.add(('IT2a','i','IT2a|f108v.52|G009'))
assert expected=={(c['reader'],c['head'],c['id']) for c in C['cases']}
for c in C['cases']:
 r=byid[c['id']];u=c['units'];h=c['head']
 assert u==r['units'] and c['word']==r['ivtff_group_raw'] and u[0]!=h
 assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE' and r['kind']=='P'
 reachable={0}
 for end in range(1,len(u)+1):
  if end-1 in reachable and u[end-1]!=h:reachable.add(end)
  if end>=3 and end-3 in reachable and u[end-3]==h and u[end-2]!=h:reachable.add(end)
 assert c['excluded']==(len(u) not in reachable)
remaining={ed:[h for h in d['survivors'] if not any(c['reader']==ed and c['head']==h and c['excluded'] for c in C['cases'])] for ed,d in R['readers'].items()}
assert remaining==C['remaining'] and all(not r for r in remaining.values())
assert C['registered_initial_status']==R['status']
out={'status':'PASS','scope':'Same-author independent DP and exact-source validation of the disclosed post-result extension; no independent palaeography.','checks':len(C['cases']),'remaining':remaining}
(A/'POST_RESULT_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
