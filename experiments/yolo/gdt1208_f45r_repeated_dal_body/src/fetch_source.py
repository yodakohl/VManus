"""Reacquire only registered images, stopping if source bytes have changed."""
from pathlib import Path
import json,hashlib,urllib.request
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
for receipt in [json.loads((A/'SOURCE_IMAGE.json').read_text()),*json.loads((A/'REGION_IMAGES.json').read_text())]:
 p=ROOT/receipt['path']
 if not p.exists():
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(urllib.request.urlopen(receipt['url'],timeout=45).read())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==receipt['sha256'],f'Source changed; stop without updating receipt: {p.name}'
print('Registered original and one source region match pinned bytes')
