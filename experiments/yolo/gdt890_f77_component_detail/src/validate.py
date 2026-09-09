import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
for name,digest in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
observations=[]
for observer in ['A','B']:
 p=E/'artifacts'/('GEOMETRY_'+observer+'.json');x=json.loads(p.read_text())
 assert x['image_sha256']=='6bcedcaccc8107da32d6d1ca950b96708b529538d7902a2108398a3c0b9327df'
 assert {z['id'] for z in x['zones']}=={'U1','U2','U3','U4','U5','U6','M'}
 for z in x['zones']:
  assert isinstance(z['complete_boundary'],bool)
  assert z['port_count'] is None or isinstance(z['port_count'],int) and z['port_count']>=0
  if not z['complete_boundary']:assert z['port_count'] is None
 observations.append(x)
out=dict(status='PASS',scope='source hashes, observation schema and uncertainty preservation; not independent confirmation of visual truth',observers=len(observations),observed_complete_zones={x['observer']:[z['id'] for z in x['zones'] if z['complete_boundary']] for x in observations})
(E/'artifacts/VALIDATION.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
