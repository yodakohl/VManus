import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def decide(a,b):
 ids=[x['id'] for x in a['landmarks'] if x['distinctive'] and x['nonink']]
 if len(ids)<3:return dict(status='LANDMARK_CAPACITY_STOP',eligible_ids=ids,verified_ids=[],B_required=False)
 if b is None:return dict(status='A_CAPACITY_AWAITING_B',eligible_ids=ids,verified_ids=[],B_required=True)
 verified=[x['id'] for x in b['verifications'] if x['id'] in ids and x['matching_material_pair']]
 return dict(status='MATERIAL_LANDMARK_CAPACITY_SUPPORTED_ONLY' if len(verified)>=3 else 'LANDMARK_VERIFICATION_STOP',eligible_ids=ids,verified_ids=verified,B_required=True)
def controls():
 a=dict(landmarks=[dict(id=str(i),distinctive=True,nonink=True) for i in range(3)]);assert decide(a,None)['status']=='A_CAPACITY_AWAITING_B';assert decide(dict(landmarks=a['landmarks'][:2]),None)['status']=='LANDMARK_CAPACITY_STOP';b=dict(verifications=[dict(id=str(i),matching_material_pair=i<2) for i in range(3)]);assert decide(a,b)['status']=='LANDMARK_VERIFICATION_STOP';b['verifications'][2]['matching_material_pair']=True;assert decide(a,b)['status']=='MATERIAL_LANDMARK_CAPACITY_SUPPORTED_ONLY';a['landmarks'][2]['nonink']=False;assert decide(a,None)['status']=='LANDMARK_CAPACITY_STOP'
 return dict(status='PASS',tests=['below_gate','at_gate','ineligible','verification_rejection','verification_pass'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--check',action='store_true');args=p.parse_args()
 if args.controls:(E/'artifacts/CONTROLS.json').write_text(enc(controls()));print('CONTROLS PASS');return
 read=lambda n:json.loads((E/'artifacts'/n).read_text());a=read('VIEWER_A.json');seal=read('A_SEAL.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc'];assert a['excluded_ink_target_not_inspected'] is True and isinstance(a['proposed_mirror_mapping'],str) and isinstance(a['note'],str);assert len({x['id'] for x in a['landmarks']})==len(a['landmarks'])
 for x in a['landmarks']:assert isinstance(x['id'],str) and x['kind'] in ['HOLE','TEAR','CREASE'] and type(x['distinctive']) is bool and type(x['nonink']) is bool and all(isinstance(x[k],str) for k in ['recto_description','verso_description','note'])
 b=None
 if len([x for x in a['landmarks'] if x['distinctive'] and x['nonink']])>=3 and (E/'artifacts/VIEWER_B.json').exists():
  b=read('VIEWER_B.json');assert b['excluded_ink_target_not_inspected'] is True and isinstance(b['note'],str);assert len(b['verifications'])==len(a['landmarks']) and {x['id'] for x in b['verifications']}=={x['id'] for x in a['landmarks']}
  for x in b['verifications']:assert type(x['matching_material_pair']) is bool and isinstance(x['note'],str)
 result=dict(**decide(a,b),A=a,B=b,A_seal=seal,vision_verified_by_software=False,target_comparison_performed=False);p=E/'artifacts/RESULT.json'
 if args.check:assert p.read_text()==enc(result)
 else:p.write_text(enc(result))
 print(enc(result))
if __name__=='__main__':main()
