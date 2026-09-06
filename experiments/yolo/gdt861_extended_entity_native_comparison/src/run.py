import argparse,json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def read(n):return json.loads((E/'artifacts'/n).read_text())
def classify(a,b):
 if not all(x['localized'] and x['alignment']=='CANDIDATE_ENTITY_REGION' for x in [a,b]):return 'UNRESOLVED_OR_DISAGREEMENT'
 if a['connection']==b['connection']=='EXTENDED_UPPER_LINK':return 'BOTH_VIEWERS_LOCAL_UPPER_LINK'
 if a['connection']==b['connection']=='NO_EXTENDED_UPPER_LINK':return 'BOTH_VIEWERS_NO_LOCAL_UPPER_LINK'
 return 'UNRESOLVED_OR_DISAGREEMENT'
def controls():
 yes=dict(localized=True,alignment='CANDIDATE_ENTITY_REGION',connection='EXTENDED_UPPER_LINK');no=dict(yes,connection='NO_EXTENDED_UPPER_LINK');unc=dict(yes,alignment='LOCUS_ONLY');miss=dict(yes,localized=False)
 assert classify(yes,yes)=='BOTH_VIEWERS_LOCAL_UPPER_LINK';assert classify(no,no)=='BOTH_VIEWERS_NO_LOCAL_UPPER_LINK';assert classify(yes,no)==classify(unc,yes)==classify(miss,yes)=='UNRESOLVED_OR_DISAGREEMENT'
 return dict(status='PASS',tests=['agreement','no_link','disagreement','locus_only','not_localized'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--check',action='store_true');args=p.parse_args()
 if args.controls:(E/'artifacts/CONTROLS.json').write_text(enc(controls()));print('CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text());a=read('VIEWER_A.json');b=read('VIEWER_B.json');seal=read('A_SEAL.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc']
 for obs in [a,b]:
  assert set(obs['targets'])==set(s['targets']) and isinstance(obs['note'],str)
  for t in obs['targets'].values():assert type(t['localized']) is bool and t['connection'] in s['connection_values'] and t['alignment'] in s['alignment_values'] and isinstance(t['note'],str)
 result=dict(status='COMPLETE_TWO_TARGET_NATIVE_DESCRIPTIVE_COMPARISON',targets={k:dict(source=s['targets'][k],viewer_A=a['targets'][k],viewer_B=b['targets'][k],classification=classify(a['targets'][k],b['targets'][k])) for k in s['targets']},viewer_A_note=a['note'],viewer_B_note=b['note'],A_seal=seal,vision_verified_by_software=False)
 dest=E/'artifacts/RESULT.json'
 if args.check:assert dest.read_text()==enc(result)
 else:dest.write_text(enc(result))
 print(enc(result))
if __name__=='__main__':main()
