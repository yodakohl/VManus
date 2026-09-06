import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def valid(obs):
 assert type(obs['localized']) is bool and obs['endpoint_topology'] in ['ONE_UPRIGHT_FLOURISH','TWO_UPRIGHT_LINK','UNCERTAIN'] and type(obs['uncertainty']) is bool
 count=obs['complete_intervening_groups'];assert count is None or type(count) is int and count>=0
 if not obs['localized'] or obs['uncertainty'] or obs['endpoint_topology']=='UNCERTAIN':assert count is None
 assert all(isinstance(obs[k],str) for k in ['group_boundary_evidence','endpoint_description','note'])
def classify(a,b):
 if not all(x['localized'] and x['uncertainty'] is False and x['endpoint_topology']!='UNCERTAIN' and type(x['complete_intervening_groups']) is int for x in [a,b]):return 'UNRESOLVED_OR_DISAGREEMENT'
 if all(x['endpoint_topology']=='TWO_UPRIGHT_LINK' and x['complete_intervening_groups']>=1 for x in [a,b]):return 'BOTH_VIEWERS_INTERVENING_GROUP_LINK'
 if a['endpoint_topology']==b['endpoint_topology'] and a['complete_intervening_groups']==b['complete_intervening_groups']==0:return 'BOTH_VIEWERS_NO_COMPLETE_INTERVENING_GROUP'
 return 'UNRESOLVED_OR_DISAGREEMENT'
def controls():
 a=dict(localized=True,endpoint_topology='TWO_UPRIGHT_LINK',complete_intervening_groups=1,group_boundary_evidence='',endpoint_description='',uncertainty=False,note='');valid(a);assert classify(a,a)=='BOTH_VIEWERS_INTERVENING_GROUP_LINK';z=dict(a,complete_intervening_groups=0);assert classify(z,z)=='BOTH_VIEWERS_NO_COMPLETE_INTERVENING_GROUP';f=dict(z,endpoint_topology='ONE_UPRIGHT_FLOURISH');assert classify(f,f)=='BOTH_VIEWERS_NO_COMPLETE_INTERVENING_GROUP';assert all(classify(a,x)=='UNRESOLVED_OR_DISAGREEMENT' for x in [z,dict(a,uncertainty=True),dict(a,localized=False,complete_intervening_groups=None),dict(a,endpoint_topology='UNCERTAIN')]);assert classify(z,f)=='UNRESOLVED_OR_DISAGREEMENT'
 for x in [dict(a,complete_intervening_groups=-1),dict(a,complete_intervening_groups=True),dict(a,localized=False)]:
  try:valid(x)
  except AssertionError:pass
  else:raise AssertionError('invalid schema accepted')
 return dict(status='PASS')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args()
 if args.controls:(E/'artifacts/CONTROLS.json').write_text(enc(controls()));print('CONTROLS PASS');return
 read=lambda n:json.loads((E/'artifacts'/n).read_text());a=read('VIEWER_A.json');b=read('VIEWER_B.json');valid(a);valid(b);seal=read('A_SEAL.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc'];r=dict(status=classify(a,b),A=a,B=b,A_seal=seal,vision_verified_by_software=False);p=E/'artifacts/RESULT.json'
 if args.check:assert p.read_text()==enc(r)
 else:p.write_text(enc(r))
 print(enc(r))
if __name__=='__main__':main()
