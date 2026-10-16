#!/usr/bin/env python3
"""Post-result replay adapter for a diagnostic using the pre-existing frozen solver."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=B/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
plan=read(A/'POSTSTOP_TRIE_PLAN.json')
for pin in plan['pins']:assert sha(R/pin['path'])==pin['sha256'],pin['path']
p=B/'src/validate.py';sp=importlib.util.spec_from_file_location('frozen_independent_control_trie',p);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
s=read(B/'src/SPEC.json');g=read(A/'GENERATED_CONTROL.json');W=set(mod.sources(s)['deot'])
r=mod.independent_solve(g['encoded_stream'],W,s['signs'],'FWD',s)
if r['status']=='SAT':
 assert len(r['key'])==len(set(r['key'].values()))==22
 assert ''.join(r['key'][u] for u in g['encoded_stream'])==''.join(r['source_words'])
 assert all(w in W for w in r['source_words'])
else:assert r['status']=='UNKNOWN','UNSAT contradicts the planted control witness'
x={'kind':'POST_STOP_SOURCE_ONLY_DIAGNOSTIC','status':r['status'],'result':r,'original_gate':'CLOSED_CAPACITY_STOP_UNCHANGED','native_authorized':False,'native_data_read':False,'original_control_words':g['source_words'],'same_planted_unspaced_message':r['status']=='SAT' and ''.join(r['source_words'])==''.join(g['source_words']),'algorithm_sha256':sha(p),'plan_sha256':sha(A/'POSTSTOP_TRIE_PLAN.json'),'control_sha256':sha(A/'GENERATED_CONTROL.json')}
data=json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n';target=A/'POSTSTOP_TRIE_RESULT.json'
if args.check:assert target.read_text()==data
else:
 assert not target.exists();target.write_text(data)
assert all(not(A/n).exists() for n in ['GATE_VALIDATION.json','NATIVE_INPUT.json','RESULT.json','VALIDATION.json'])
print(json.dumps({'status':'PASS_POSTSTOP_CONTROL_DIAGNOSTIC_REPLAY' if args.check else x['status'],'original_gate':x['original_gate'],'same_planted_message':x['same_planted_unspaced_message'],'native_authorized':False}))
