from pathlib import Path
import csv,json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent.relative_to(Path.cwd());s=json.loads((D/'SOURCE.json').read_text());assert s['page']=='f88r' and s['sealed']==['f84','f84r'];assert hashlib.sha256((D/'f88r.jpg').read_bytes()).hexdigest()==s['sha256']=='aa266580695fc4a84cd031015c56f51f1b6ce807b6998c6ef4b8b68bae11983b';assert Image.open(D/'f88r.jpg').size==(s['width'],s['height'])==(2000,2752)
objs=list(csv.DictReader((D/'OBJECTS.tsv').open(),delimiter='\t'));pairs=list(csv.DictReader((D/'PAIRS.tsv').open(),delimiter='\t'));ids={r['id'] for r in objs};assert len(objs)==len(ids)==16 and len(pairs)==9
for r in objs:
 x,y,w,h=[int(r[k]) for k in ['x','y','width','height']];assert 0<=x<x+w<=2000 and 0<=y<y+h<=2752;assert r['id'] in (D/'VIEW.html').read_text()
for r in pairs:assert r['object_a'] in ids and r['object_b'] in ids and r['object_a']!=r['object_b']
v=dict(status='PASS',scope='image byte provenance, dimensions, annotation IDs/bounds and pair references ONLY',manual_regions=16,manual_pairs=9,visual_interpretation_validated=False,meaning_validated=False);(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
