import argparse,hashlib,json
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def outcome(n,v,b):return 'LANDMARK_CAPACITY_STOP' if n<3 else 'A_CAPACITY_AWAITING_B' if not b else 'MATERIAL_LANDMARK_CAPACITY_SUPPORTED_ONLY' if v>=3 else 'LANDMARK_VERIFICATION_STOP'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');args=ap.parse_args();assert outcome(2,0,False)=='LANDMARK_CAPACITY_STOP' and outcome(3,0,False)=='A_CAPACITY_AWAITING_B' and outcome(3,2,True)=='LANDMARK_VERIFICATION_STOP' and outcome(3,3,True)=='MATERIAL_LANDMARK_CAPACITY_SUPPORTED_ONLY'
 if args.controls:print('INDEPENDENT CONTROLS PASS');return
 read=lambda n:json.loads((E/'artifacts'/n).read_text());s=json.loads((E/'src/SPEC.json').read_text())
 for i in s['images']:
  p=ROOT/i['path'];assert p.is_file() and p.stat().st_size==i['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==i['sha256']
  with Image.open(p) as im:assert im.size==(i['source_width'],i['source_height'])
 a=read('VIEWER_A.json');seal=read('A_SEAL.json');r=read('RESULT.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc'];assert a['excluded_ink_target_not_inspected'] is True and isinstance(a['note'],str) and isinstance(a['proposed_mirror_mapping'],str)
 ids=[];allids=[]
 for item in a['landmarks']:
  assert isinstance(item['id'],str) and item['kind'] in {'HOLE','TEAR','CREASE'} and type(item['distinctive']) is bool and type(item['nonink']) is bool and all(isinstance(item[k],str) for k in ['recto_description','verso_description','note']);allids.append(item['id'])
  if item['nonink'] is True and item['distinctive'] is True:ids.append(item['id'])
 assert len(set(allids))==len(allids);b=None;verified=[]
 if len(ids)>=3 and (E/'artifacts/VIEWER_B.json').exists():
  b=read('VIEWER_B.json');assert b['excluded_ink_target_not_inspected'] is True and isinstance(b['note'],str);assert len(b['verifications'])==len(allids) and {v['id'] for v in b['verifications']}==set(allids)
  for v in b['verifications']:
   assert type(v['matching_material_pair']) is bool and isinstance(v['note'],str)
   if v['matching_material_pair'] and v['id'] in ids:verified.append(v['id'])
 expected=dict(status=outcome(len(ids),len(verified),b is not None),eligible_ids=ids,verified_ids=verified,B_required=len(ids)>=3,A=a,B=b,A_seal=seal,vision_verified_by_software=False,target_comparison_performed=False);assert r==expected
 out=dict(status='PASS',source_image_hash_bytes_dimensions_checked=2,A_seal_schema_checked=True,B_validation='NOT_REQUIRED_CAPACITY_STOP' if len(ids)<3 else 'PENDING' if b is None else 'PASS_SCHEMA_AND_COUNT_ONLY',fixed_decision_recomputed=True,vision_verified_by_software=False,controls='PASS');(E/'artifacts/VALIDATION.json').write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(out))
if __name__=='__main__':main()
