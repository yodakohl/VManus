import argparse,hashlib,json
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def decision(a,b):
 if a['localized'] is not True or b['localized'] is not True or a['seam']!=b['seam']:return 'UNRESOLVED_OR_DISAGREEMENT'
 return {'SPACE_LIKE':'BOTH_VIEWERS_SPACE_LIKE','INTERNAL_LIKE':'BOTH_VIEWERS_INTERNAL_LIKE'}.get(a['seam'],'UNRESOLVED_OR_DISAGREEMENT')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');args=ap.parse_args();a=dict(localized=True,seam='SPACE_LIKE');b=dict(localized=True,seam='INTERNAL_LIKE');assert decision(a,a)=='BOTH_VIEWERS_SPACE_LIKE' and decision(b,b)=='BOTH_VIEWERS_INTERNAL_LIKE';assert decision(a,b)==decision(a,dict(a,localized=False))==decision(a,dict(a,seam='UNCERTAIN'))=='UNRESOLVED_OR_DISAGREEMENT'
 if args.controls:print('INDEPENDENT CONTROLS PASS');return
 read=lambda n:json.loads((E/'artifacts'/n).read_text());s=json.loads((E/'src/SPEC.json').read_text());im=s['image'];p=ROOT/s['image_path'];assert p.is_file() and p.stat().st_size==im['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==im['sha256']
 with Image.open(p) as photo:assert photo.size==(im['width'],im['height'])
 assert im in json.loads((ROOT/s['source_provenance']).read_text())['source_images'];original=json.loads((ROOT/s['occurrence_source']).read_text());chosen=[]
 for o in original:
  for target in s['targets'].values():
   if o['line']['metadata']['locus']==target['locus'] and int(o['group'][1])==target['index']:
    assert o['group'][2]=='qo' and o['follower'][2]==target['follower'];chosen.append(o)
 assert len(chosen)==6 and len({(x['edition'],x['line']['metadata']['locus']) for x in chosen})==6 and chosen==read('SOURCE_LINES.json')
 aa=read('VIEWER_A.json');bb=read('VIEWER_B.json');seal=read('A_SEAL.json');r=read('RESULT.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc']
 for o in [aa,bb]:
  assert set(o['targets'])=={'T21','T30'} and o['excluded_ink_target_not_inspected'] is True and isinstance(o['note'],str)
  for t in o['targets'].values():assert type(t['localized']) is bool and t['seam'] in {'SPACE_LIKE','INTERNAL_LIKE','UNCERTAIN'} and all(isinstance(t[k],str) for k in ['manual_alignment_note','neighbor_whole_group_seams_note','within_group_gaps_note','note'])
 decisions={k:decision(aa['targets'][k],bb['targets'][k]) for k in ['T21','T30']};expected=dict(status='BOTH_FIXED_SEAMS_LOCAL_SPACING_SUPPORTED' if set(decisions.values())=={'BOTH_VIEWERS_SPACE_LIKE'} else 'LOCAL_SPACING_NOT_CONFIRMED_FOR_BOTH',target_results=decisions,A=aa,B=bb,A_seal=seal,vision_verified_by_software=False,manual_alignment_verified_by_software=False);assert r==expected
 v=dict(status='PASS',source_occurrences_checked=6,image_hash_bytes_dimensions_checked=True,A_seal_schema_checked=True,decision_independently_recomputed=True,vision_verified_by_software=False,manual_alignment_verified_by_software=False,controls='PASS');(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(v))
if __name__=='__main__':main()
