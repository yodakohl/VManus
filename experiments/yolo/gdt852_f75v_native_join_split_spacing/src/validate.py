import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def read(n):return json.loads((E/'artifacts'/n).read_text())
s=read('SOURCES.json');assert s['page']=='f75v' and s['label']=={'none':['75v']}
p=E/'runtime/f75v.jpg'
if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
a=read('VIEWER_A.json');b=read('VIEWER_B.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==read('A_SEAL.json')['sha256']
for obs in [a,b]:
 assert set(obs['targets'])=={'T1','T2'}
 for t in obs['targets'].values():
  assert isinstance(t['localized'],bool) and t['seam'] in ['SPACE_LIKE','INTERNAL_LIKE','UNCERTAIN'] and isinstance(t['note'],str)
 assert obs['comparison'] in ['LOCAL_SEAM_CONTRAST','WHOLE_SPAN_SCALING_COMPATIBLE','NO_CLEAR_CONTRAST','UNCERTAIN']
 assert isinstance(obs['comparison_note'],str)
supported=all(obs['comparison']=='LOCAL_SEAM_CONTRAST' and all(t['localized'] for t in obs['targets'].values()) and obs['targets']['T1']['seam']=='SPACE_LIKE' and obs['targets']['T2']['seam']=='INTERNAL_LIKE' for obs in [a,b])
(E/'artifacts/VALIDATION.json').write_text(json.dumps(dict(status='PASS_SOURCE_HASH_SEAL_SCHEMA_AND_FIXED_DECISION_LOGIC_ONLY',fixed_visual_support=supported,vision_verified_by_software=False),indent=2)+'\n');print('PASS',supported)
