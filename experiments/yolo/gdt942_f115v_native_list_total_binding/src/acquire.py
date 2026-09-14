"""Acquire only the previously registered f115v photograph; verify before viewing."""
from pathlib import Path
import json,hashlib,urllib.request,datetime
from PIL import Image
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2]
lock=json.loads((EXP/'PREREG_LOCK.json').read_text())
for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
s=json.loads((EXP/'src/SOURCE.json').read_text());assert s['page']=='f115v' and '/1006275/' in s['image_url']
p=EXP/'artifacts/SOURCE_F115V.jpg'
if not p.exists():
 with urllib.request.urlopen(s['image_url'],timeout=60) as response:
  data=response.read();ctype=response.headers.get('Content-Type','');assert 'image' in ctype
 p.write_bytes(data)
else:data=p.read_bytes()
im=Image.open(p);assert im.size==(s['width'],s['height']) and im.format=='JPEG'
receipt={'source_url':s['image_url'],'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'width':im.width,'height':im.height,'format':im.format,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registered_utc':lock['registered_utc'],'scope':s['scope'],'credit':s['credit']}
q=EXP/'artifacts/SOURCE_RECEIPT.json'
if not q.exists():q.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
else:assert json.loads(q.read_text())['sha256']==receipt['sha256']
print(json.dumps(receipt,ensure_ascii=False))
