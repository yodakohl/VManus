import argparse,csv,hashlib,json
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parents[1]
def read(n):return json.loads((E/'artifacts'/n).read_text())
def decision(x,y):
 if x['localized'] is not True or y['localized'] is not True or {x['alignment'],y['alignment']}!={'CANDIDATE_ENTITY_REGION'}:return 'UNRESOLVED_OR_DISAGREEMENT'
 labels={x['connection'],y['connection']}
 return {'EXTENDED_UPPER_LINK':'BOTH_VIEWERS_LOCAL_UPPER_LINK','NO_EXTENDED_UPPER_LINK':'BOTH_VIEWERS_NO_LOCAL_UPPER_LINK'}.get(next(iter(labels)),'UNRESOLVED_OR_DISAGREEMENT') if len(labels)==1 else 'UNRESOLVED_OR_DISAGREEMENT'
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');a=p.parse_args();yes=dict(localized=True,alignment='CANDIDATE_ENTITY_REGION',connection='EXTENDED_UPPER_LINK');no=dict(yes,connection='NO_EXTENDED_UPPER_LINK');assert decision(yes,yes)=='BOTH_VIEWERS_LOCAL_UPPER_LINK' and decision(no,no)=='BOTH_VIEWERS_NO_LOCAL_UPPER_LINK';assert all(decision(yes,other)=='UNRESOLVED_OR_DISAGREEMENT' for other in [no,dict(yes,localized=False),dict(yes,alignment='LOCUS_ONLY')])
 if a.controls:print('INDEPENDENT CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text());images=read('SOURCES.json')['source_images'];assert len(images)==2 and {i['page'] for i in images}=={'f100r','f114r'}
 for target in s['targets'].values():
  im=next(i for i in images if i['page']==target['page']);assert all(im[k]==target[k] for k in ['page','canvas_id','url','width','height','cache_filename']);p=E/'runtime'/im['cache_filename'];assert p.is_file();assert p.stat().st_size==im['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==im['sha256']
  with Image.open(p) as image:assert image.size==(im['width'],im['height'])
 with (E/'src/PAGE_ADMISSIONS.tsv').open() as f:rows=list(csv.DictReader(f,delimiter='\t'))
 assert len(rows)==2 and {r['physical_page'] for r in rows}=={'f100r','f114r'} and all(r['source_selector']==r['physical_page'] and r['decision']=='ADMITTED' for r in rows)
 aa=read('VIEWER_A.json');bb=read('VIEWER_B.json');seal=read('A_SEAL.json');r=read('RESULT.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc'];assert r['A_seal']==seal and r['viewer_A_note']==aa['note'] and r['viewer_B_note']==bb['note']
 for ob in [aa,bb]:
  assert isinstance(ob['note'],str) and set(ob['targets'])=={'T100','T114'}
  for item in ob['targets'].values():assert type(item['localized']) is bool and item['connection'] in {'EXTENDED_UPPER_LINK','NO_EXTENDED_UPPER_LINK','UNCERTAIN'} and item['alignment'] in {'LOCUS_ONLY','CANDIDATE_ENTITY_REGION','UNCERTAIN'} and isinstance(item['note'],str)
 assert set(r['targets'])==set(s['targets'])
 for k,source in s['targets'].items():assert r['targets'][k]==dict(source=source,viewer_A=aa['targets'][k],viewer_B=bb['targets'][k],classification=decision(aa['targets'][k],bb['targets'][k]))
 assert r['status']=='COMPLETE_TWO_TARGET_NATIVE_DESCRIPTIVE_COMPARISON' and r['vision_verified_by_software'] is False
 out=dict(status='PASS',image_hash_bytes_dimensions_checked=2,page_admissions_checked=2,A_seal_schema_checked=True,fixed_decisions_independently_recomputed=True,vision_verified_by_software=False,controls='PASS');(E/'artifacts/VALIDATION.json').write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(out))
if __name__=='__main__':main()
