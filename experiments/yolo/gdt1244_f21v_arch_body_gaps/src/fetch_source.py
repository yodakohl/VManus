"""Verify or reacquire only the hash-bound original region."""
from pathlib import Path
import hashlib,json,urllib.request
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2]
t=json.loads((D/'artifacts/TARGETS.json').read_text());p=ROOT/t['source_path']
if not p.exists():
 req=urllib.request.Request(t['source_url'],headers={'User-Agent':'VManusSourceResearch/1.0 (public manuscript source verification)'})
 data=urllib.request.urlopen(req,timeout=40).read();assert hashlib.sha256(data).hexdigest()==t['source_sha256'],'Changed source; stop'
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
assert hashlib.sha256(p.read_bytes()).hexdigest()==t['source_sha256']
print('Exact old1242region verified; no new region or full image')
