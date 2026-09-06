import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];s=json.loads((E/'src/SPEC.json').read_text());sources=json.loads((E/'artifacts/SOURCES.json').read_text())
assert {r['page'] for r in sources['images']}==set(s['pages'])
for r in sources['images']:
 p=E/'runtime'/f"{r['page']}.jpg"
 if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
a=json.loads((E/'artifacts/VIEWER_A.json').read_text());b=json.loads((E/'artifacts/VIEWER_B.json').read_text());seal=json.loads((E/'artifacts/A_SEAL.json').read_text());assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256']
assert set(a)==set(b)=={r['id'] for r in s['targets']}
for obs in [a,b]:
 for k,r in obs.items():
  assert r['localized'] in [True,False] and r['small_elements'] in [0,1,2,3,'UNCERTAIN'] and r['looped_following'] in ['PRESENT','ABSENT','UNCERTAIN'] and isinstance(r['note'],str)
(E/'artifacts/VALIDATION.json').write_text(json.dumps({'status':'PASS_SOURCE_HASHES_AND_OBSERVATION_SCHEMA_ONLY','targets':4,'vision_independently_validated':False},indent=2)+'\n');print('PASS')
