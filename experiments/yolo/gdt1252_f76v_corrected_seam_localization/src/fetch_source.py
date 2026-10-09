import hashlib,json,urllib.request
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
r=json.loads((B/'artifacts/IMAGE_RECEIPT.json').read_text());p=ROOT/r['path']
if not p.exists():
 p.parent.mkdir(exist_ok=True);p.write_bytes(urllib.request.urlopen(r['url'],timeout=45).read())
assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print('Exact fixed image available; no new view performed')
