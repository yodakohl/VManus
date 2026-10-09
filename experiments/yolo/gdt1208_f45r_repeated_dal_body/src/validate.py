"""Independent same-author receipt/schema/reduction check, not palaeography."""
from pathlib import Path
from datetime import datetime
from PIL import Image
import hashlib,json
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((A/n).read_text())
def dt(s):return datetime.fromisoformat(s)
def main():
 lock=load('REGISTRATION_LOCK.json');o=load('OBSERVATION.json');seal=load('OBSERVATION_SEAL.json');source=load('SOURCE_IMAGE.json');regions=load('REGION_IMAGES.json');r=load('RESULT.json')
 for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
 for name,key in [('OBSERVATION.json','observation_sha256'),('SOURCE_IMAGE.json','source_receipt_sha256'),('REGION_IMAGES.json','region_receipt_sha256')]:assert sha(A/name)==seal[key]
 assert sha(D/'PREREGISTRATION.md')==seal['registration_sha256']
 assert sha(D/'src/run.py')==load('RUN_RECEIPT.json')['runner_sha256'] and sha(A/'OBSERVATION.json')==load('RUN_RECEIPT.json')['observation_sha256']
 registered=dt(lock['registered_utc']);observed=dt(o['recorded_utc']);assert registered<observed<=dt(seal['sealed_utc'])
 assert lock['before_pixel_access'] and source['before_first_view']
 assert source['canvas']=='1006162' and source['label']=='45r' and source['url']=='https://collections.library.yale.edu/iiif/2/1006162/full/full/0/default.jpg'
 assert registered<dt(source['fetched_utc'])<observed
 assert sha(ROOT/source['path'])==source['sha256']==o['image_sha256'] and o['source_image']==source['path']
 with Image.open(ROOT/source['path']) as im:assert im.size==(2823,3706)==tuple(source['dimensions'])
 c=load('CANVAS_METADATA.json')['canvas'];assert c['label']['none']==['45r'] and c['id'].endswith('/1006162') and (c['width'],c['height'])==(2823,3706)
 assert len(regions)==1;reg=regions[0];assert reg['target']=='f45r.10' and reg['before_view']
 x,y,w,h=reg['region'];assert x>=0 and y>=0 and w>0 and h>0 and x+w<=2823 and y+h<=3706
 assert reg['region']==load('REGION_PLAN.json')['region']==[280,1090,1700,210]
 assert reg['url']=='https://collections.library.yale.edu/iiif/2/1006162/'+','.join(map(str,reg['region']))+'/full/0/default.jpg'
 assert sha(ROOT/reg['path'])==reg['sha256']
 assert registered<dt(reg['registered_before_region_fetch_utc'])<dt(reg['fetched_utc'])<observed
 with Image.open(ROOT/reg['path']) as im:assert im.size==(w,h)==tuple(reg['dimensions'])
 lines=load('TARGET_LINES.json');assert len(lines)==3 and {l['edition'] for l in lines}=={'ZL3b','IT2a','RF1b'}
 for l in lines:
  assert l['locus']=='f45r.10' and [g['ivtff_group_raw'] for g in l['groups']]=='okaiin shar yky oky kair daldy dalor cheol dal'.split()
 assert o['location'] in {'LOCATED','UNLOCATED'} and o['shared_body'] in {'COMPATIBLE','DIFFERENT','UNRESOLVED'}
 assert o['endings'] in {'DISTINCT_COMPATIBLE','CONTRADICTED','UNRESOLVED'} and o['clearances'] in {'SPACE_LIKE','CONTRADICTED','UNRESOLVED'}
 assert o['observer_count']==1 and not o['blind'] and o['views_used']=={'whole_original':1,'registered_native_regions':1}
 assert all(o[k] for k in ('line_alignment','variability','limitations','rivals'))
 assert [(t['group'],t['expected_transcription']) for t in o['targets']]==[('G006','daldy'),('G007','dalor'),('G009','dal')]
 for t in o['targets']:assert t['observation'] and 0<=t['approximate_crop_x_span'][0]<t['approximate_crop_x_span'][1]<=w
 positive=(o['shared_body']=='COMPATIBLE' and o['endings']=='DISTINCT_COMPATIBLE' and o['clearances']=='SPACE_LIKE')
 negative=any([o['shared_body']=='DIFFERENT',o['endings']=='CONTRADICTED',o['clearances']=='CONTRADICTED'])
 answer='UNLOCATED' if o['location']=='UNLOCATED' else ('VISUAL_COUNTEREVIDENCE' if negative else ('SOURCE_AWARE_LOCAL_SHAPE_SUPPORT' if positive else 'UNRESOLVED'))
 assert r['status']==answer and r['locus']=='f45r.10' and r['targets']==['daldy','dalor','dal']
 assert all(r[k]==o[k] for k in ('location','shared_body','endings','clearances'))
 assert r['observer_count']==1 and r['independent_confirmation_capacity']==r['native_meanings_assigned']==0 and not r['morpheme_proven'] and not r['native_unit_segmentation_proven']
 out={'status':'PASS','scientific_status':answer,'scope':'Admission/source/observation hash chronology, exact sources/region bounds, target-line provenance and fixed reduction only','same_author':True,'palaeography_validated':False,'new_image_keys':1,'source_region_views':1,'validator_sha256':sha(Path(__file__))}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
