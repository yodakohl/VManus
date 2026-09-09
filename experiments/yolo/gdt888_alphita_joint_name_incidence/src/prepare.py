"""Project cached admissible blocks, removing even-leaf bodies before fitting."""
import hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
CACHE='experiments/yolo/gdt887_tacuinum_joint_entry_reconstruction/artifacts/SELECTED.json'
EDITIONS=['ZL3b','IT2a','RF1b','CONSENSUS']
def prepare():
 p=ROOT/CACHE;data=json.loads(p.read_text());assert len(data['frames'])==665
 panels={ed:dict(train=[],held_heads=[]) for ed in EDITIONS}
 for f in data['frames']:
  assert not f['page'].startswith('f84')
  assert f['physical_folio']==re.match(r'f[0-9]+',f['page']).group()
  odd=int(f['physical_folio'][1:])%2==1
  for ed in EDITIONS:
   r=f['readings'][ed]
   if not r['eligible']:continue
   assert r['groups'] and all(g['sta'] for g in r['groups'])
   rec=dict(paragraph_id=f['paragraph_id'],page=f['page'],physical_folio=f['physical_folio'],head=r['groups'][0]['sta'])
   if odd:rec['body']=[g['sta'] for g in r['groups'][1:]]
   panels[ed]['train' if odd else 'held_heads'].append(rec)
 return dict(source= CACHE,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),panels=panels)
