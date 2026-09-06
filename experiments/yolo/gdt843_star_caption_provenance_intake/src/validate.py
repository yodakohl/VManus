import json
from pathlib import Path
E=Path(__file__).resolve().parents[1];s=json.loads((E/'src/SPEC.json').read_text());boxes=json.loads((E/'artifacts/CROPS.json').read_text());joins=json.loads((E/'artifacts/JOINS.json').read_text());raw=json.loads((E/'artifacts/RAW_GROUPS.json').read_text());r=json.loads((E/'artifacts/RESULT.json').read_text())
expected={t['id']:[] for t in s['targets']}
for b in boxes:
 for t in s['targets']:
  x=t['x']/s['width'];y=t['y']/s['height']
  if int(b['crop_x'])/s['native_width']<=x<=(int(b['crop_x'])+int(b['crop_width']))/s['native_width'] and int(b['crop_y'])/s['native_height']<=y<=(int(b['crop_y'])+int(b['crop_height']))/s['native_height']:expected[t['id']].append(b['blind_id'])
for j in joins:assert j['crop_ids']==expected[j['id']]
loci={j['locus'] for j in joins if j['locus']};assert {g['locus'] for g in raw}==loci
for locus in loci:
 for ed in ['ZL3b','IT2a','RF1b']:
  gs=[g for g in raw if g['locus']==locus and g['edition']==ed];assert gs;assert [int(g['source_group_index']) for g in gs]==list(range(1,len(gs)+1));assert all(int(g['source_group_count'])==len(gs) for g in gs)
assert r['unique_links']==sum(len(v)==1 for v in expected.values());assert r['clear_linked']==sum(j['clear'] and j['locus'] is not None for j in joins);assert r['raw_groups']==len(raw)
obj=dict(status='PASS',independent_reverse_geometry=True,source_group_inventory=True,authorial_ownership_validated=False);(E/'artifacts/VALIDATION.json').write_text(json.dumps(obj)+'\n');print(obj)
