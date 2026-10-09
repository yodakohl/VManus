import json,hashlib,datetime
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def read(x):return json.loads(x.read_text())
lock=read(P/'src/REGISTRATION_LOCK.json')
for path,h in lock['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
img=ROOT/'experiments/yolo/gdt861_extended_entity_native_comparison/runtime/1006248.jpg'
assert Image.open(img).size==(2676,3756)
o=read(P/'artifacts/OBSERVATION.json');s=read(P/'artifacts/OBSERVATION_SEAL.json');r=read(P/'artifacts/RESULT.json');v=read(P/'artifacts/VIEW_RECEIPT.json')
assert s['sha256']==hashlib.sha256((P/'artifacts/OBSERVATION.json').read_bytes()).hexdigest()==r['observation_sha256']
assert lock['utc']<=v['utc']<=s['utc']
assert v['source_sha256']==hashlib.sha256(img.read_bytes()).hexdigest()
assert o['visible_basis'] and o['limitations'] and o['observer']=='root aware observer'
if o['category']=='YES':assert o['localized'] and o['endpoint_groups_delimited'];expected='ADJACENT_GROUP_SCOPE_CONTRADICTED'
elif o['category']=='NO':assert o['localized'] and o['endpoint_groups_delimited'];expected='NO_COMPLETE_INTERVENING_GROUP_LOCAL'
else:assert o['category']=='UNCERTAIN';expected='UNRESOLVED_ENDPOINT_GROUP_SCOPE'
assert r['status']==expected
out={'status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'source bytes, dimensions, chronology, seal, schema, decision only; does not validate visual judgment or meanings','decision':expected}
(P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
