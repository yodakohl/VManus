#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--image');a.add_argument('--crop');args=a.parse_args()
s=json.loads((p/'artifacts/SOURCE.json').read_text());o=json.loads((p/'artifacts/OBSERVATION.json').read_text())
assert s['canvas']=='1006247' and s['folio']=='f99v'
assert s['dimensions']==[2802,3697] and s['crop_region']==[1500,600,600,350]
assert o['status']=='AVOIDANCE_COMPATIBLE' and o['qualifying_neighboring_baselines']>=2 and o['clear_ink_truncations']==0
assert len(o['line_notes'])==o['qualifying_neighboring_baselines'] and not o['word_transcription'] and not o['meaning_assigned']
assert o['views']=={'overview':1,'crop':1}
checked=[]
for value,key in [(args.image,'sha256'),(args.crop,'crop_sha256')]:
 if value:
  assert hashlib.sha256(Path(value).read_bytes()).hexdigest()==s[key];checked.append(key)
v={'status':'PASS','scope':'Source-byte/record consistency only, not independent visual or chronological verification','image_hashes_checked':checked}
(p/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
