"""Fetch only the frozen external source into a caller-selected local cache."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
p=Path(__file__).resolve().parents[1]
s=json.loads((p/'artifacts/SOURCE.json').read_text())
a=argparse.ArgumentParser();a.add_argument('--image-cache',required=True);args=a.parse_args()
with urllib.request.urlopen(s['manifest']) as r: m=json.load(r)
c=[x for x in m['sequences'][0]['canvases'] if x['label']==s['label']]
assert len(c)==1 and c[0]['@id']==s['canvas']
u=c[0]['images'][0]['resource']['service']['@id']+'/full/full/0/default.jpg'
assert u==s['image_url']
with urllib.request.urlopen(u) as r: data=r.read()
assert hashlib.sha256(data).hexdigest()==s['image_sha256']
Path(args.image_cache).write_bytes(data)
print('PASS: frozen external image acquired; visual interpretation requires observation.')
