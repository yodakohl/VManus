#!/usr/bin/env python3
"""Verify saved scoped counts and byte identities; no semantic verification."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent
p=json.loads((B/'BX_SOURCE.json').read_text());rows=p['queries'][2]['rows']+p['queries'][3]['rows']
assert len(rows)==710
assert sum(r['ivtff_group_raw']=='darol' for r in rows)==6
assert sum(r['ivtff_group_raw']=='darolsy' for r in rows)==3
assert all(r['kind']=='L' for r in rows if r['ivtff_group_raw'] in {'darol','darolsy'})
assert all(not r['page'].startswith('f84') for r in rows)
for q in p['queries']:assert hashlib.sha256((ROOT/q['command'][2]).read_bytes()).hexdigest()==q['input_sha256']
for name in ('BX_F82R','BX_F75V'):
 receipt=json.loads((B/(name+'_RECEIPT.json')).read_text())
 assert hashlib.sha256((B/(name+'.jpg')).read_bytes()).hexdigest()==receipt['sha256']
r=json.loads((B/'BX_RESULT.json').read_text());assert r['confirmed_words']==0
print('PASS source counts, images and frozen inputs; not a meaning check.')
