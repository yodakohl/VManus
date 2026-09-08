import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((B/'src/SPEC.json').read_text());lock=json.loads((B/'src/PREREG_LOCK.json').read_text())
for path,h in lock.items():assert sha(R/path)==h
for im in s['images']:assert sha(R/im['cache_path'])==im['sha256']
r=json.loads((B/'artifacts/READINGS.json').read_text());assert set(r)==set(s['targets'])
for editions in r.values():
 assert set(editions)=={'ZL3b','IT2a','RF1b'}
 for rows in editions.values():assert [int(x['source_group_index'])for x in rows]==list(range(1,len(rows)+1)) and all(int(x['source_group_count'])==len(rows)for x in rows)
for name in ['VIEWER_A','VIEWER_B']:
 o=json.loads((B/f'artifacts/{name}.json').read_text());assert set(o['observations'])==set(s['targets'])
 for locus,obs in o['observations'].items():
  assert type(obs['localized'])is bool and isinstance(obs['evidence'],str) and obs['evidence']
  assert obs['status'] in ({'ONE_SPATIAL_ENTRY','SEPARATE_VISIBLE_OWNERS','UNRESOLVED'}if locus.startswith('f67')else{'LOCALIZED_READING_DESCRIPTION','UNRESOLVED'})
  if not obs['localized']:assert obs['status']=='UNRESOLVED'
seal=json.loads((B/'artifacts/A_SEAL.json').read_text());assert sha(B/'artifacts/VIEWER_A.json')==seal['sha256']
v={'status':'PASS','coverage':'Source hashes, frozen protocol, four-locus reading and observation coverage, root seal. Native judgements not validated by software.','vision_verified_by_software':False};(B/'artifacts/VALIDATION.json').write_text(json.dumps(v,sort_keys=True)+'\n');print(json.dumps(v))
