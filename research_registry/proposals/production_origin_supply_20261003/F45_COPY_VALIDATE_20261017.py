#!/usr/bin/env python3
"""Replay saved authoring against precomputed independent expectations; no decoding."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
ROOT=D.parents[2]
def load(name):return json.loads((D/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
x=load('F45COPY.json');a=load('F45_COPY_ACCOUNTING_20261017.json');c=load('F45_COPY_COMPARE_20261017.json');old=load('F45R_RECORD_SYNTHESIS_DERIVATION_20261015.json')
for pin in x['pins']:assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
assert sha(D/'F45_COPY_ACCOUNTING_20261017.json')==c['precomputed_review_sha256']
assert sha(D/'F45COPY.json')==c['compared_output_sha256']
assert sha(D/'F45R_RECORD_SYNTHESIS_DERIVATION_20261015.json')==c['parent_sha256']
assert x['original_trace']==old['trace'] and len(old['trace'])==86
for r,base in zip(x['records'],old['records']):
 assert r['A_words']==a['expected_A'][r['record']]
 assert r['B']=={k:v for k,v in base['fields'].items() if k!='dy'}
 assert r['source_explicit_ordinary']==base['ordinary']
 assert [e['event'] for e in r['program'] if e['kind']=='UNCHANGED_B']==[e for e in base['field_events'] if e['roles']!=['dy']]
assert all(v is True for k,v in c['checks'].items() if isinstance(v,bool))
print(json.dumps({'status':'PASS_SAVED_AUTHORING_AND_PRECOMPUTED_EXPECTATIONS','groups':86,'A_lengths':[len(r['A_words']) for r in x['records']],'scope':'Source hashes, exact precomputed lists, unchanged B events and written ordinary anchors only; not semantic validation.'}))
