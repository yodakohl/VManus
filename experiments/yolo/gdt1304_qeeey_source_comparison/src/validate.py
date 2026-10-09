"""Exact prior-source and provenance replay, not validation of visual truth."""
import argparse,collections,gzip,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
a=argparse.ArgumentParser();a.add_argument('--image-dir');args=a.parse_args()
lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
for path,h in lock.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
spec=json.loads((P/'src/SPEC.json').read_text());lines=json.loads((P/'artifacts/SOURCE_LINES.json').read_text());receipts=json.loads((P/'artifacts/IMAGE_RECEIPTS.json').read_text());result=json.loads((P/'artifacts/RESULT.json').read_text())
assert len(lines)==9 and len(receipts)==3 and len(spec['pages'])==3
assert {r['page'] for r in receipts}=={'f76r','f107r','f108r'}
cache={}
for record in lines:
 path=record['source_path']
 if path not in cache:cache[path]=json.loads((ROOT/path).read_text())
 assert record['group_columns']==cache[path]['group_columns']
 assert record['line'] in cache[path]['lines']
context=json.loads((P/'artifacts/LOCALIZATION_CONTEXT.json').read_text())
assert {r['line']['metadata']['locus'] for r in context}=={'f108r.37','f108r.39'}
for record in context:
 assert record['source_path'] in lock
 assert record['line'] in cache[record['source_path']]['lines']
selected={}
for site in spec['pages']:
 locus=site['locus'];chosen=[r['line'] for r in lines if r['line']['metadata']['locus']==locus]
 assert len(chosen)==3 and {l['metadata']['edition'] for l in chosen}=={'ZL3b','IT2a','RF1b'}
 for line in chosen:
  ed=line['metadata']['edition'];g=line['groups'][site['target']-1]
  assert g==[f"{ed}|{locus}|G{site['target']:03d}",str(site['target']),'qeeey','DEFINITE_SPACE','DEFINITE_SPACE']
  selected.setdefault(ed,set()).add(g[0])
  for idx in site['controls']:assert line['groups'][idx-1][2].startswith('qo')
 # Source annotations are not cleaned away for visual comparison.
 if locus=='f107r.2':assert next(l for l in chosen if l['metadata']['edition']=='RF1b')['groups'][3][2]=='she@152;y'
 if locus=='f108r.38':
  rf=next(l for l in chosen if l['metadata']['edition']=='RF1b')
  assert rf['groups'][2][2]=='qokee@152;y' and rf['groups'][3][2]=='ote@152;y'
  assert rf['metadata']['paragraph_end']=='0'
  assert all(l['metadata']['paragraph_end']=='1' for l in chosen if l['metadata']['edition']!='RF1b')
strict=json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()))
for ed,rows in strict.items():
 hits=[r for r in rows if r['ivtff_group_raw']=='qeeey']
 assert len(hits)==3 and {r['id'] for r in hits}==selected[ed]
 assert all(r['units']==['q','e','e','e','y'] for r in hits)
statuses={};pixel_hashes=0
for site,receipt in zip(spec['pages'],receipts):
 for k in ['page','locus','canvas','dimensions','target','controls']:assert site[k]==receipt[k]
 assert receipt['views']=={'overview':1,'crop':1}
 x,y,w,h=receipt['crop_box'];ow,oh=receipt['dimensions'];assert 0<=x<x+w<=ow and 0<=y<y+h<=oh
 base='https://collections.library.yale.edu/iiif/2/'+site['canvas']
 assert receipt['original_url']==base+'/full/full/0/default.jpg'
 assert receipt['crop_url']==base+'/'+','.join(map(str,receipt['crop_box']))+'/full/0/default.jpg'
 for k in ['original_sha256','crop_sha256']:assert len(receipt[k])==64 and all(c in '0123456789abcdef' for c in receipt[k])
 if args.image_dir:
  for suffix,key in [('', 'original_sha256'),('_crop','crop_sha256')]:
   file=Path(args.image_dir)/('qe3_'+site['page']+suffix+'.jpg')
   assert hashlib.sha256(file.read_bytes()).hexdigest()==receipt[key];pixel_hashes+=1
 ob=json.loads((P/f"artifacts/OBSERVATION_{site['page']}.json").read_text())
 assert ob['page']==site['page'] and ob['locus']==site['locus']
 if ob['localization']=='SECURE' and (ob['initial_shape']=='VISIBLE_DIFFERENCE' or ob['post_initial_round_body']=='PRESENT'):
  status='SOURCE_PREMISE_CHALLENGED'
 elif ob['localization']=='SECURE' and ob['initial_shape']=='COMPATIBLE' and ob['post_initial_round_body']=='ABSENT' and ob['left_outer_seam']==ob['right_outer_seam']=='SPACE_LIKE':status='LOCAL_Q_NON_O_SUPPORT'
 else:status='UNRESOLVED'
 assert ob['status']==status;statuses[site['locus']]=status
assert result['sites']==statuses
assert result['status']==('THREE_LOCAL_Q_NON_O_SUPPORT' if set(statuses.values())=={'LOCAL_Q_NON_O_SUPPORT'} else 'MIXED_OR_UNRESOLVED_SITE_OUTCOMES')
assert result['informed_observers']==result['independent_manuscripts']==1
assert result['meanings_assigned']==result['source_corrections']==0 and not result['images_public']
v={'status':'PASS','reader_lines_replayed':9,'additional_ZL_localization_lines':2,'exact_target_groups':9,'distinct_physical_target_loci':3,'control_group_records':15,'site_outcomes':statuses,'scope':'Source hashes, selected rows, image provenance and declared decision aggregation only; no independent visual or semantic verification.'}
(P/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
if args.image_dir:print('Local image/crop byte hashes checked:',pixel_hashes)
