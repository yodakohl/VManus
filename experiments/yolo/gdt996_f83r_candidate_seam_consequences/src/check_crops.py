"""Post-result artifact integrity check; not a visual judgment or scientific input."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
E=Path(__file__).resolve().parents[1];R=E.parents[2]
data=json.loads((E/'artifacts/CROPS.json').read_text());original=Image.open(R/data['original']);checks=[]
for c in data['crops']:
 p=R/c['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256'];crop=Image.open(p);expected=original.crop(c['box']);assert crop.size==expected.size and ImageChops.difference(crop,expected).getbbox() is None;checks.append(dict(path=c['path'],exact_pixels=True))
out=dict(status='PASS',checks=checks,visual_judgments_checked=False)
(E/'artifacts/CROP_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
