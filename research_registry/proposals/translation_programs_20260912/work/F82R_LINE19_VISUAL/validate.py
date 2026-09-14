import hashlib,io,json
from pathlib import Path
from urllib.request import urlopen
from PIL import Image
b=Path(__file__).resolve().parent;s=json.loads((b/'SOURCE.json').read_text())
assert hashlib.sha256((b/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
with urlopen(s['image_url'],timeout=30) as response:raw=response.read()
assert hashlib.sha256(raw).hexdigest()==s['sha256']
im=Image.open(io.BytesIO(raw));assert im.size==(1000,1360)
for name,box in s['crops'].items():
 expected=im.crop(tuple(box));actual=Image.open(b/name)
 assert actual.size==expected.size and actual.tobytes()==expected.tobytes()
print('PASS: admitted image bytes and exact crops; not visual or semantic validation')
