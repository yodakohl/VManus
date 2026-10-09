#!/usr/bin/env python3
"""Check source provenance and observation consistency, not palaeographic truth."""
import argparse,hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1];root=p.parents[2]
a=argparse.ArgumentParser();a.add_argument('--image');a.add_argument('--crop46');a.add_argument('--crop53');args=a.parse_args()
s=json.loads((p/'artifacts/SOURCE.json').read_text());o=json.loads((p/'artifacts/OBSERVATION.json').read_text());t=json.loads((p/'artifacts/TARGETS.json').read_text())
assert s['canvas']=='1006254' and s['label']=='103r' and s['dimensions']==[2688,3805]
assert [c['box'] for c in s['crops']]==[[350,2640,2010,185],[350,3035,2010,190]]
assert o['views']=={'overview':1,'crops':2} and len(o['sites'])==6
assert all(not o[k] for k in ['meaning_assigned','transcription_changed','linguistic_word_boundaries_confirmed','independent_confirmation'])
source_groups={g[0]:g for l in t['lines'] for g in l['groups']}
for site in o['sites']:
 for sid in site['source_ids'].values(): assert source_groups[sid][2]=='qokeey'
for f in t['inputs']: assert hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256']
assert len(t['lines'])==6
for line in t['lines']:
 ed=line['metadata']['edition']; original=json.loads((root/next(f['path'] for f in t['inputs'] if ed in f['path'])).read_text());assert line in original['lines']
classes=[v['pattern'] for v in o['sites']]+[v[k] for v in o['sites'] for k in ['left_boundary','right_boundary']]+[v['classification'] for v in o['required_other_observations']]
expected='SOURCE_PREMISE_CHALLENGED' if any(v in ['VISIBLE_DIFFERENCE','INTERNAL_LIKE'] for v in classes) else 'UNRESOLVED' if 'UNRESOLVED' in classes else 'SOURCE_COMPATIBLE'
assert o['status']==expected
checked=[]
for value,record in [(args.image,s),(args.crop46,s['crops'][0]),(args.crop53,s['crops'][1])]:
 if value:
  assert hashlib.sha256(Path(value).read_bytes()).hexdigest()==record['sha256'];checked.append(record['sha256'])
v={'status':'PASS','scope':'Provenance, raw-target fidelity and aggregation only; no independent visual truth check','source_lines_replayed':6,'site_source_ids_verified':18,'pixel_hashes_checked':checked,'observation_status':expected}
(p/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
