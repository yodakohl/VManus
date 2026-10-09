"""Reacquire the two registered images without changing receipts."""
from pathlib import Path
import json,hashlib,urllib.request
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
for name in ('SOURCE_IMAGE.json','REGION_IMAGE.json'):
 r=json.loads((A/name).read_text());p=ROOT/r['path']
 if not p.exists():
  data=urllib.request.urlopen(r['url'],timeout=45).read()
  assert hashlib.sha256(data).hexdigest()==r['sha256'],'Source changed; stop'
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],'Source changed; stop'
print('Both registered image byte streams match')
