#!/usr/bin/env python3
"""Source/record validation, not independent palaeography."""
import argparse,hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--image');a.add_argument('--crop');args=a.parse_args()
s=json.loads((p/'artifacts/SOURCE.json').read_text());o=json.loads((p/'artifacts/OBSERVATION.json').read_text())
assert s['canvas']=='1006090' and s['folio']=='f8r'
assert s['dimensions']==[2660,3719] and s['crop_region']==[330,1360,1850,380]
assert o['status']=='UNRESOLVED' and o['meaning_assigned'] is False
assert o['views']=={'overview':1,'crop':1} and o['scope_deviation']
checked=[]
for value,key in [(args.image,'full_sha256'),(args.crop,'crop_sha256')]:
 if value:
  assert hashlib.sha256(Path(value).read_bytes()).hexdigest()==s[key]
  checked.append(key)
v={'status':'PASS','scope':'Record consistency and optional exact image bytes only; no independent visual judgment','image_hashes_checked':checked,'native_meanings':0}
(p/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
