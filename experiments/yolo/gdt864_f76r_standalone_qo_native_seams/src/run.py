import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def classify(a,b):
 if not a['localized'] or not b['localized']:return 'UNRESOLVED_OR_DISAGREEMENT'
 if a['seam']==b['seam']=='SPACE_LIKE':return 'BOTH_VIEWERS_SPACE_LIKE'
 if a['seam']==b['seam']=='INTERNAL_LIKE':return 'BOTH_VIEWERS_INTERNAL_LIKE'
 return 'UNRESOLVED_OR_DISAGREEMENT'
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--check',action='store_true');args=p.parse_args();yes=dict(localized=True,seam='SPACE_LIKE');no=dict(localized=True,seam='INTERNAL_LIKE');assert classify(yes,yes)=='BOTH_VIEWERS_SPACE_LIKE' and classify(no,no)=='BOTH_VIEWERS_INTERNAL_LIKE';assert all(classify(yes,x)=='UNRESOLVED_OR_DISAGREEMENT' for x in [no,dict(yes,localized=False),dict(yes,seam='UNCERTAIN')])
 if args.controls:(E/'artifacts/CONTROLS.json').write_text(enc(dict(status='PASS')));print('CONTROLS PASS');return
 read=lambda n:json.loads((E/'artifacts'/n).read_text());a=read('VIEWER_A.json');b=read('VIEWER_B.json');seal=read('A_SEAL.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc']
 for ob in [a,b]:
  assert set(ob['targets'])=={'T21','T30'} and ob['excluded_ink_target_not_inspected'] is True and isinstance(ob['note'],str)
  for t in ob['targets'].values():assert type(t['localized']) is bool and t['seam'] in ['SPACE_LIKE','INTERNAL_LIKE','UNCERTAIN'] and all(isinstance(t[k],str) for k in ['manual_alignment_note','neighbor_whole_group_seams_note','within_group_gaps_note','note'])
 results={k:classify(a['targets'][k],b['targets'][k]) for k in ['T21','T30']};r=dict(status='BOTH_FIXED_SEAMS_LOCAL_SPACING_SUPPORTED' if all(v=='BOTH_VIEWERS_SPACE_LIKE' for v in results.values()) else 'LOCAL_SPACING_NOT_CONFIRMED_FOR_BOTH',target_results=results,A=a,B=b,A_seal=seal,vision_verified_by_software=False,manual_alignment_verified_by_software=False);out=E/'artifacts/RESULT.json'
 if args.check:assert out.read_text()==enc(r)
 else:out.write_text(enc(r))
 print(enc(r))
if __name__=='__main__':main()
