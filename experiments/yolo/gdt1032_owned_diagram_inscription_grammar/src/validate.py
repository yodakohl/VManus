#!/usr/bin/env python3
"""Verify declared source bindings and complete manual image-status coverage."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parents[1]
lock=json.loads((E/'PREREG_LOCK.json').read_text())
for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
s=json.loads((E/'src/SOURCE.json').read_text());f=json.loads((E/'artifacts/FETCH.json').read_text())
assert [r['id'] for r in s['images']]==[r['id'] for r in f]
for a,b in zip(s['images'],f):
 for k in a:assert a[k]==b[k],k
 if b['status']=='HASH_VERIFIED':assert b['expected_sha256']==b['observed_sha256']
obs=E/'artifacts/OBSERVATIONS.json'
if obs.exists():
 o=json.loads(obs.read_text());assert [r['image_id'] for r in o]==[r['id'] for r in f]
 for r,z in zip(o,f):
  assert r['fetch_status']==z['status']
  assert isinstance(r['regions'],list)
  if z['status']!='HASH_VERIFIED':assert not r['regions']
  for a in r['regions']:
   assert set(['region_id','location','literal_reading','uncertainty','class','rationale']).issubset(a)
 assert len({a['region_id'] for r in o for a in r['regions']})==sum(len(r['regions']) for r in o)
print(json.dumps({'status':'PASS','source_bindings':len(lock['files']),'image_ids':len(f),'manual_coverage_checked':obs.exists(),'historical_transcription_validated':False,'voynich_meaning_checked':False}))
