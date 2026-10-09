"""Reacquire only the exact previously registered row rectangle; no new images."""
import json,hashlib,urllib.request
from pathlib import Path
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2]
t=json.loads((D/'artifacts/TARGETS.json').read_text())
r=json.loads((ROOT/'experiments/yolo/gdt1208_f45r_repeated_dal_body/artifacts/REGION_IMAGES.json').read_text())[0]
assert t['source_path']==r['path'] and t['source_sha256']==r['sha256']
p=ROOT/t['source_path']
if not p.exists():
 req=urllib.request.Request(r['url'],headers={'User-Agent':'VManusSourceResearch/1.0 (public manuscript source verification)'})
 data=urllib.request.urlopen(req,timeout=40).read()
 assert hashlib.sha256(data).hexdigest()==t['source_sha256'],'Changed source; no replacement accepted'
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
assert hashlib.sha256(p.read_bytes()).hexdigest()==t['source_sha256']
print('Exact old1208rectangle verified; no full-page or new-region request')
