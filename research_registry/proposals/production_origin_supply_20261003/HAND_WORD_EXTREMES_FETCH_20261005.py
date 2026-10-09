"""Reacquire the four registered photograph files; stop on changed source bytes."""
from pathlib import Path
import hashlib,json,urllib.request
P=Path('research_registry/proposals/production_origin_supply_20261003')
items=[]
for name,dest in [('HAND_WORD_EXTREMES_VISUAL_SCOPE_20261005.json','.cache/word_extremes_20261005/f2r_original.jpg'),('HAND_WORD_EXTREMES_F114R_VISUAL_SCOPE_20261005.json','experiments/yolo/gdt861_extended_entity_native_comparison/runtime/1006272.jpg')]:
 r=json.loads((P/name).read_text());items.append((dest,r['source_url'],r['sha256']))
for page,dest in [('F2R','f2r_line1.jpg'),('F114R','f114r_line39.jpg')]:
 r=json.loads((P/f'HAND_WORD_EXTREMES_{page}_REGION_RECEIPT_20261005.json').read_text());items.append(('.cache/word_extremes_20261005/'+dest,r['source_url'],r['region_sha256']))
for dest,url,expected in items:
 p=Path(dest)
 if not p.exists():
  data=urllib.request.urlopen(url,timeout=30).read()
  assert hashlib.sha256(data).hexdigest()==expected,'Changed source bytes; stop'
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,'Stored source bytes changed; stop'
print('Four registered image files match the pinned hashes')
