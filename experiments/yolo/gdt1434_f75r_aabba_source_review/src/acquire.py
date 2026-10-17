#!/usr/bin/env python3
"""One cached original and one registered native IIIF rectangle; no pixel edits."""
from pathlib import Path
import datetime,hashlib,json,io,shutil,sys
from urllib.request import Request,urlopen
from PIL import Image
D=Path(__file__).resolve().parents[1];R=D.parents[2];A=D/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
s=read(D/'src/SPEC.json');lock=read(D/'src/PROTOCOL_LOCK.json')
for p,h in lock['pins'].items():assert sha(R/p)==h,p
stage,=sys.argv[1:];assert stage in ('overview','detail')
p=A/('original_f75r.jpg' if stage=='overview' else 'native_detail.jpg');receipt=A/(stage.upper()+'_SOURCE.json')
assert not p.exists() and not receipt.exists(),'No repeated acquisition'
started=stamp()
if stage=='overview':
 source=R/'docs/visual_overview/runtime/1006208.jpg';assert sha(source)==s['overview_sha256'];shutil.copyfile(source,p)
 url=s['overview_url'];dims=s['overview_dimensions'];kind='Existing previouslyowned cached original; copy time is not original retrieval time'
else:
 assert (A/'OVERVIEW_SOURCE.json').exists();c=read(A/'CROP_SCOPE.json');x,y,w,h=c['region'];assert all(type(v) is int for v in (x,y,w,h));assert x>=0 and y>=0 and w>0 and h>0 and x+w<=2852 and y+h<=3759
 url=s['detail_url_template'].format(region=','.join(map(str,c['region'])));dims=[w,h];kind='One unaltered official nativeIIIFregionresponse'
 with urlopen(Request(url,headers={'User-Agent':'VManus source research'}),timeout=30) as z:
  assert z.status==200 and z.headers.get_content_type()=='image/jpeg' and z.geturl()==url
  b=z.read(12000000)
 assert len(b)<12000000;p.write_bytes(b)
with Image.open(p) as im:assert im.format=='JPEG' and list(im.size)==dims
v={'url':url,'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size,'width':dims[0],'height':dims[1],'acquired_at':started,'role':kind}
receipt.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
