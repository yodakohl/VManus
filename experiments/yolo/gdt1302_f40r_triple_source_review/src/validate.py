"""Validate provenance and retained source contract, not visual truth."""
import argparse, hashlib, json
from pathlib import Path
p=Path(__file__).resolve().parents[1];root=p.parents[2]
a=argparse.ArgumentParser();a.add_argument('--image');a.add_argument('--crop');args=a.parse_args()
for lock in ['REGISTRATION_LOCK.json','SOURCE_LOCK.json']:
 for path,h in json.loads((p/'src'/lock).read_text()).items():
  assert hashlib.sha256((root/path).read_bytes()).hexdigest()==h
sources=json.loads((p/'artifacts/SOURCE_LINES.json').read_text())
assert set(sources)=={'ZL3b','IT2a','RF1b'}
for ed,rec in sources.items():
 original=json.loads((root/rec['source_path']).read_text())
 assert rec['group_columns']==original['group_columns']
 assert rec['line'] in original['lines']
 line=rec['line'];assert line['metadata']['locus']=='f40r.9'
 assert line['metadata']['edition']==ed
 assert len(line['groups'])==9
 for i in [6,7,8]:
  g=line['groups'][i-1]
  assert g==[f'{ed}|f40r.9|G00{i}',str(i),'okaiin','DEFINITE_SPACE','DEFINITE_SPACE']
 assert line['groups'][3][4]==line['groups'][4][3]=='DRAWING_INTERRUPTION'
 assert line['groups'][8][2]==('@152;aram' if ed=='RF1b' else 'daram')
r=json.loads((p/'artifacts/IMAGE_RECEIPT.json').read_text())
assert r['canvas']=='1006152' and r['label']=='40r' and r['dimensions']==[2793,3734]
assert r['crop_box']==[290,1290,1930,200] and r['crop_dimensions']==[1930,200]
assert r['pixel_views']==2 and not r['image_bytes_public'] and r['inspection_complete']
assert r['url']=='https://collections.library.yale.edu/iiif/2/1006152/full/full/0/default.jpg'
assert r['crop_url']=='https://collections.library.yale.edu/iiif/2/1006152/290,1290,1930,200/full/0/default.jpg'
for field in ['sha256','crop_sha256']:assert len(r[field])==64 and all(c in '0123456789abcdef' for c in r[field])
for path,key in [(args.image,'sha256'),(args.crop,'crop_sha256')]:
 if path:assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==r[key]
o=json.loads((p/'artifacts/OBSERVATION.json').read_text())
assert o['status']=='LOCAL_REPEAT_AND_GAP_SUPPORT' and o['locus']=='f40r.9'
assert o['target_indices']==[6,7,8] and o['transcribed_form']=='okaiin'
assert not o['blind'] and o['new_word_meanings']==0
v={'status':'PASS','source_lines_replayed':3,'target_groups_replayed':9,
 'scope':'Input hashes, exact cached lines and observation provenance only; no independent visual judgment',
 'visual_classification':o['status'],'images_redistributed':False}
(p/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v,indent=2))
if args.image or args.crop:print('Optional local image byte hashes also match receipt.')
