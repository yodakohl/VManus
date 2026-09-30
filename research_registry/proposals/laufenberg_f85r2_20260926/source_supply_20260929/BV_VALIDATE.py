#!/usr/bin/env python3
"""Check all frozen input hashes, outputs, targeted receipts and replay stability."""
import csv,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parent
r=json.loads((BASE/'BV_RESULT.json').read_text())
for p,h in r['inputs'].items():
 assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
expected={'qotchs':['qot','C','s'],'qotol':['qot','ol'],'qotchy':['qot','Cy'],'qotain':['qot','aI']}
assert {x['surface']:x['bpe_units'] for x in r['formal_replays']}==expected
assert all(x['wrapper']=='q' and x['local_frame']=='NOT_FROZEN_FOR_NEW_INPUT' for x in r['formal_replays'])
assert r['formal_replays'][-1]['right_family']=='ain'
assert all(x['right_family']=='NONE' for x in r['formal_replays'][:-1])
assert len(r['queries'])==2
assert '"selected": 2' in r['queries'][0]['stderr']
assert '"selected": 0' in r['queries'][1]['stderr']
p=json.loads((BASE/'BV_WORD_PRIORS.json').read_text())
assert [x['form'] for x in p['profiles']]==r['forms']
expected_counts={'qotchs':[1,1,1],'qotol':[42,45,42],'qotchy':[58,63,59],'qotain':[60,64,62]}
for prof in p['profiles']:
 assert [d['count'] for d in prof['editions'].values()]==expected_counts[prof['form']]
 for d in prof['editions'].values():
  assert sum(d['positions'].values())==d['count']
  if prof['form']=='qotain':assert next(x['count'] for x in d['strata']['section'] if x['value']=='H')==0
before={name:(BASE/name).read_bytes() for name in ('BV_RESULT.json','BV_FORMAL_TABLE.tsv')}
subprocess.run([sys.executable,str(BASE/'BV_AUDIT.py')],cwd=ROOT,check=True,capture_output=True)
assert all((BASE/name).read_bytes()==blob for name,blob in before.items())
assert r['confirmed_words']==0 and r['independent_meaning_confirmation_capacity']==0
assert not r['reserves_opened'] and not r['images_opened'] and not r['new_decoder']
print('PASS: four unchanged formal replays, frozen input hashes, query receipts, descriptive priors; no meaning validation.')
