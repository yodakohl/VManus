"""Replay prior certified TYPE-bound arithmetic; no new native census."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3]
D=R/'research_registry/proposals/production_origin_supply_20261003'
a=json.loads((D/'NUCLEUS_CARRIER_LANGUAGE_APPLICATION_20261012.json').read_text())
for p,h in a['primary_hashes'].items():
 assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
p=R/'experiments/yolo/gdt1355_fixed_null_erasure_capacity/artifacts/RESULT.json'
x=json.loads(p.read_text());m=json.loads((p.parents[1]/'experiment.json').read_text())
assert any(v['path']==str(p.relative_to(R)) and v['sha256']==hashlib.sha256(p.read_bytes()).hexdigest() for v in m['outputs'])
b={k:22-v['max_types']['null_types'] for k,v in x['panels'].items()}
assert b==a['bounds']
assert all(v==9 for k,v in b.items() if k.endswith('_GE2'))
assert all(v>8 for v in b.values())
print(json.dumps({'status':'PASS','bounds':b,'scope':'Prior arithmetic and input identity only; mathematical proof independently reviewed, native optima inherited, no phonemes or meanings identified.'},indent=2))
