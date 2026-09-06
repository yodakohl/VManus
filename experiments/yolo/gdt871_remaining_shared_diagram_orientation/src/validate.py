"""Independent record and header validation; does not validate native perception."""
import argparse,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
C={'1006194':(4972,3738),'1006196':(7993,3828)}
def load(p):return json.loads(p.read_text())
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):d.update(b)
 return d.hexdigest()
def check_observation(o,hashes,ceiling):
 assert o['observer']=='ROOT' and o['mode']=='NATIVE_FULL_ORIGINAL' and o['claim_ceiling']==ceiling
 assert isinstance(o['observations'],list) and len(o['observations'])==2
 seen=set()
 for item in o['observations']:
  cid=item['canvas_id'];assert cid in C and cid not in seen;seen.add(cid)
  assert item['viewed'] is True and item['source_sha256']==hashes[cid]
  assert isinstance(item['viewed_at_utc'],str) and item['viewed_at_utc'].strip()
  assert isinstance(item['notes'],list) and item['notes'] and all(isinstance(n,str) and n.strip() for n in item['notes'])
def controls():
 import copy
 h={k:'fixture' for k in C};o=dict(observer='ROOT',mode='NATIVE_FULL_ORIGINAL',claim_ceiling='fixture',observations=[dict(canvas_id=k,source_sha256='fixture',viewed=True,viewed_at_utc='fixture',notes=['Synthetic fixture']) for k in C]);check_observation(o,h,'fixture')
 for bad in [dict(o,mode='CROP'),copy.deepcopy(o)]:
  if bad['mode']!='CROP':bad['observations'][0]['viewed']=False
  try:check_observation(bad,h,'fixture')
  except AssertionError:pass
  else:raise AssertionError('invalid observation accepted')
 return dict(status='CONTROLS_PASS',false_view_rejected=True,crop_rejected=True)
def validate():
 lock=load(E/'src/PREREG_LOCK.json');required={str((E/p).relative_to(ROOT)) for p in ['src/run.py','src/validate.py','src/SPEC.json','SOURCES.json','METHOD.md','PREREGISTRATION.md','src/PAGE_ADMISSIONS.tsv']};assert required<=set(lock)
 for p,h in lock.items():
  f=(ROOT/p).resolve();assert f.is_relative_to(ROOT) and sha(f)==h
 spec=load(E/'src/SPEC.json');assert spec['experiment_id']=='GDT871' and set(spec['sealed_data'])=={'f84','f84r'} and set(spec['source_scope'])=={'f67r1','f67r2','f68r1','f68r2','f68r3'}
 with (E/'src/PAGE_ADMISSIONS.tsv').open() as f:admissions=list(csv.DictReader(f,delimiter='\t'))
 assert len(admissions)==3 and {(r['physical_page'],r['source_selector']) for r in admissions}=={(k,k) for k in ['f67r1','f68r2','f68r3']} and all(r['decision']=='ADMITTED' for r in admissions)
 sources=load(E/'SOURCES.json')['source_images'];meta=load(E/'artifacts/IMAGE_METADATA.json')['source_images'];assert len(sources)==len(meta)==2
 assert {x['canvas_id'] for x in sources}==set(C)=={x['canvas_id'] for x in meta};hashes={}
 from PIL import Image
 for q in sources:
  cid=q['canvas_id'];m=next(x for x in meta if x['canvas_id']==cid);url=f'https://collections.library.yale.edu/iiif/2/{cid}/full/full/0/default.jpg'
  assert q['image_url']==url and (q['width'],q['height'])==C[cid]
  f=E/'runtime'/f'{cid}.jpg';h=sha(f);hashes[cid]=h
  assert m['sha256']==h and m['bytes']==f.stat().st_size and m['viewed_at_acquisition'] is False
  for key in ['canvas_id','image_url','width','height']:assert m[key]==q[key]
  if q.get('sha256'):assert h==q['sha256']
  if cid=='1006194':assert h=='0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c'
  with Image.open(f) as im:assert im.format=='JPEG' and im.size==C[cid]
 check_observation(load(E/'artifacts/OBSERVATION.json'),hashes,spec['claim_ceiling'])
 result=load(E/'artifacts/RESULT.json');assert result==dict(status='COMPLETE_PERSONAL_ORIENTATION_SOURCE_BOUNDARY',source_sha256=hashes,claim_ceiling=spec['claim_ceiling'])
 return dict(status='PASS',source_sha256=hashes,new_admission_mappings=3,locked_files=len(lock),image_content_validated=False,limitation='Checks declarations and source identity only, not native perception or observational truth.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');a=p.parse_args()
 if a.controls:print(json.dumps(controls()));return
 result=validate();(E/'artifacts/VALIDATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
