"""Fixed original acquisition and root-declared orientation packaging only."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
FIXED={'1006194':(4972,3738),'1006196':(7993,3828)}
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(path):return json.loads(path.read_text())
def write(path,x):path.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def lock():
 d=read(E/'src/PREREG_LOCK.json');assert d
 for p,h in d.items():
  path=(ROOT/p).resolve();assert path.is_relative_to(ROOT) and digest(path)==h,p
 required={str((E/p).relative_to(ROOT)) for p in ['src/run.py','src/validate.py','src/SPEC.json','SOURCES.json','METHOD.md','PREREGISTRATION.md','src/PAGE_ADMISSIONS.tsv']};assert required<=set(d)
def observation(o,metadata,ceiling):
 assert o['observer']=='ROOT' and o['mode']=='NATIVE_FULL_ORIGINAL' and o['claim_ceiling']==ceiling
 assert len(o['observations'])==2 and {x['canvas_id'] for x in o['observations']}==set(FIXED)
 for x in o['observations']:
  assert x['viewed'] is True and x['source_sha256']==metadata[x['canvas_id']]['sha256']
  assert isinstance(x['viewed_at_utc'],str) and x['viewed_at_utc'].strip()
  assert isinstance(x['notes'],list) and x['notes'] and all(isinstance(n,str) and n.strip() for n in x['notes'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--acquire',action='store_true');a=p.parse_args();lock();s=read(E/'src/SPEC.json');sources=read(E/'SOURCES.json')['source_images'];assert len(sources)==2 and {x['canvas_id'] for x in sources}==set(FIXED)
 if a.acquire:
  result=[]
  for q in sources:
   cid=q['canvas_id'];url=f'https://collections.library.yale.edu/iiif/2/{cid}/full/full/0/default.jpg';assert q['image_url']==url and (q['width'],q['height'])==FIXED[cid]
   path=E/'runtime'/f'{cid}.jpg';path.parent.mkdir(exist_ok=True)
   if not path.exists():
    with urllib.request.urlopen(url,timeout=60) as r:
     assert r.geturl()==url
     data=r.read(30000001);assert len(data)<=30000000
    path.write_bytes(data)
   with Image.open(path) as image:assert image.size==FIXED[cid] and image.format=='JPEG'
   sha=digest(path)
   if q.get('sha256'):assert sha==q['sha256']
   if cid=='1006194':assert sha=='0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c'
   result.append(dict(canvas_id=cid,image_url=url,width=q['width'],height=q['height'],sha256=sha,bytes=path.stat().st_size,viewed_at_acquisition=False))
  write(E/'artifacts/IMAGE_METADATA.json',dict(source_images=result));print('ACQUIRED_METADATA_ONLY_NOT_VIEWED');return
 m={x['canvas_id']:x for x in read(E/'artifacts/IMAGE_METADATA.json')['source_images']};assert set(m)==set(FIXED)
 for cid in FIXED:assert digest(E/'runtime'/f'{cid}.jpg')==m[cid]['sha256']
 observation(read(E/'artifacts/OBSERVATION.json'),m,s['claim_ceiling'])
 write(E/'artifacts/RESULT.json',dict(status='COMPLETE_PERSONAL_ORIENTATION_SOURCE_BOUNDARY',source_sha256={k:v['sha256'] for k,v in m.items()},claim_ceiling=s['claim_ceiling']));print('COMPLETE_PERSONAL_ORIENTATION_SOURCE_BOUNDARY')
if __name__=='__main__':main()
