#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--image');a.add_argument('--crop');args=a.parse_args()
s=json.loads((p/'artifacts/SOURCE.json').read_text());o=json.loads((p/'artifacts/OBSERVATION.json').read_text())
assert s['canvas']=='1006223' and s['folio']=='f82v' and s['dimensions']==[2821,3709]
assert s['crop_region']==[880,940,1760,250]
assert o['locus']=='f82v.12' and o['classification']=='INTERNAL_LIKE'
assert not o['meaning_assigned'] and not o['linguistic_compound_confirmed'] and len(o['comparisons'])==5
assert o['views']=={'overview':1,'crop':1}
checked=[]
for value,key in [(args.image,'sha256'),(args.crop,'crop_sha256')]:
 if value:
  assert hashlib.sha256(Path(value).read_bytes()).hexdigest()==s[key];checked.append(key)
v={'status':'PASS','scope':'Source/record consistency only, no independent palaeographic judgment','image_hashes_checked':checked}
(p/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
