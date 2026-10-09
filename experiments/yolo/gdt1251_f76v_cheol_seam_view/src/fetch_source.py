import hashlib,json,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parents[1];A=B/'artifacts';R=B/'runtime';R.mkdir(exist_ok=True)
m=json.loads((A/'CANVAS_METADATA.json').read_text())['canvas'];assert m['label']=={'none':['76v']}
body=m['items'][0]['items'][0]['body'];url=body['id'];assert url=='https://collections.library.yale.edu/iiif/2/1006211/full/full/0/default.jpg'
p=R/'f76v_full.jpg'
if not p.exists():p.write_bytes(urllib.request.urlopen(url,timeout=60).read())
h=hashlib.sha256(p.read_bytes()).hexdigest();size=Image.open(p).size;assert size==(2823,3712)
receipt={'url':url,'path':p.relative_to(B.parents[2]).as_posix(),'sha256':h,'width':size[0],'height':size[1],'bytes':p.stat().st_size,'acquired_utc':datetime.now(timezone.utc).isoformat(),'viewed':False}
old=A/'IMAGE_RECEIPT.json'
if old.exists():assert json.loads(old.read_text())['sha256']==h
else:old.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
