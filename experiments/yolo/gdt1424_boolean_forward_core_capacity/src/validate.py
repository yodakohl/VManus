#!/usr/bin/env python3
"""Independent certificate checking and pinned old row-DFS; no new primary import."""
import argparse,concurrent.futures,hashlib,importlib.util,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
 p=A/name
 if p.exists():assert read(p)==obj,'Refuse changed output '+name
 else:p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def setup():
 s=read(E/'src/SPEC.json')
 lock=read(E/'LOCK.json')
 pins=lock['files']
 if isinstance(pins,dict):
  for path,h in pins.items():assert sha(ROOT/path)==h,path
 else:
  for pin in pins:assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
 for p,h in s['input_sha256'].items():assert sha(ROOT/p)==h,p
 old=read(ROOT/s['old_spec']);vpath='experiments/yolo/gdt1421_forward_merger_run_tail_core/src/validate.py'
 assert vpath in s['input_sha256']
 v=load(vpath,'old1421_independent_sources');return s,old,v

def cert(r,groups,W,signs,mode):
 assert r['status']=='SAT';key=r['key'];words=r.get('words',r.get('source_words'));dirs=r['directions']
 assert set(key)==set(''.join(W)) and all(u in signs for u in key.values())
 assert len(words)==len(dirs)==len(groups)
 for w,d,g in zip(words,dirs,groups):
  assert w in W and d in (['FWD'] if mode=='FWD' else ['FWD','REV'])
  oriented=w if d=='FWD' else w[::-1]
  assert len(oriented)==len(g) and [key[c] for c in oriented]==g
 return len(groups)

def controls():
 signs=['a','o'];c={'status':'SAT','key':{'x':'a','y':'a'},'words':['xy'],'directions':['FWD']}
 assert cert(c,[['a','a']],{'xy'},signs,'FWD')==1
 try:cert(c,[['a','o']],{'xy'},signs,'FWD')
 except AssertionError:pass
 else:raise AssertionError('inconsistent output accepted')
 d={'status':'SAT','key':{'x':'a','y':'o'},'words':['xy'],'directions':['REV']}
 cert(d,[['o','a']],{'xy'},signs,'BIDIR')
 try:cert(d,[['o','a']],{'xy'},signs,'FWD')
 except AssertionError:pass
 else:raise AssertionError('FWD reversal accepted')
 return 4

def gate(write=True):
 s,old,v=setup();fresh=read(A/'CONTROL.json');parent=read(ROOT/s['control_path']);prior=read(ROOT/s['control_subset_path'])
 assert fresh['control_sha256']==sha(ROOT/s['control_path']) and fresh['lock_sha256']==sha(E/'LOCK.json')
 assert parent['status']=='PASS_EXACT_UNIQUE'
 ids=[i for i,g in enumerate(parent['encoded_groups']) if v.keep(g)]
 assert ids==list(range(32))==prior['selected_indices']==fresh['selected_indices']
 gs=[parent['encoded_groups'][i] for i in ids];ws=[parent['source_words'][i] for i in ids]
 assert gs==prior['groups']==fresh['groups'] and ws==prior['source_words']
 if 'source_words' in fresh:assert fresh['source_words']==ws
 pairs=parent['active_collision_pairs'];assert pairs==prior['active_collision_pairs']
 if 'active_collision_pairs' in fresh:assert fresh['active_collision_pairs']==pairs
 active=set(''.join(ws));assert len(set(map(tuple,gs)))>=2 and len(pairs)==2
 for pair in pairs:assert len(set(pair))==2 and set(pair)<=active and len({parent['planted_key'][c] for c in pair})==1
 W=set(v.vocab(old)['deot'])
 cert({'status':'SAT','key':parent['planted_key'],'words':ws,'directions':['FWD']*32},gs,W,s['signs'],'FWD')
 r=fresh['result'];status=r['status'];assert status in ['SAT','UNKNOWN'] ,'Known positive cannot legitimately be UNSAT'
 if status=='SAT':cert(r,gs,W,s['signs'],'FWD');assert fresh['status']=='PASS'
 else:
  assert fresh['status']=='STOP'
  assert not (A/'RESULT.json').exists() and not (A/'INDEPENDENT_RESULT.json').exists()
 out={'status':'PASS' if status=='SAT' else 'STOP','scope':'Unchanged positive control and ANY-key certificate only; no actual plaintext recovered','control_sha256':sha(A/'CONTROL.json'),'spec_sha256':sha(E/'src/SPEC.json'),'validator_sha256':sha(Path(__file__)),'selected_indices':ids,'groups':32,'active_collision_pairs':pairs,'certificate_checks':controls(),'old1421_stop_unchanged':True}
 if write:save('GATE_VALIDATION.json',out)
 return out

def worker(job):
 source,mode,groups,words,signs,caps,engine,engine_hash=job
 assert sha(ROOT/engine)==engine_hash
 m=load(engine,'old1421_rowdfs')
 result=m.solve(groups,words,signs,mode,caps)
 return {'source':source,'mode':mode,'result':result}

def native():
 s,old,v=setup();g=read(A/'GATE_VALIDATION.json');assert g['status']=='PASS';assert gate(False)==g
 assert (E/'LOCK.json').exists(),'Public lock required before native search'
 assert not (A/'INDEPENDENT_RESULT.json').exists(),'No search reruns'
 rows,units,ids=v.native_packet(old);groups=[units[i] for i in ids];W=v.vocab(old)
 assert len(ids)==46 and s['source_names']==old['source_names'] and s['modes']==old['modes'] and s['signs']==old['signs']
 caps=s['search']['old_dfs'];assert all(caps[k]==old[k] for k in ['seconds_per_case','nodes_cap','checks_cap'])
 jobs=[(n,mode,groups,W[n],s['signs'],caps,s['old_primary_engine'],s['input_sha256'][s['old_primary_engine']]) for n in s['source_names'] for mode in s['modes']]
 with concurrent.futures.ProcessPoolExecutor(max_workers=s['search']['workers']) as ex:cases=list(ex.map(worker,jobs))
 for c in cases:
  if c['result']['status']=='SAT':cert(c['result'],groups,set(W[c['source']]),s['signs'],c['mode'])
 save('INDEPENDENT_RESULT.json',{'engine':'Exact hash-pinned GDT1421 row DFS with unchanged caps','positions_zero_based':ids,'groups':groups,'original_groups':rows,'original_units':units,'cases':cases,'validator_sha256':sha(Path(__file__))})
 print(json.dumps([(c['source'],c['mode'],c['result']['status']) for c in cases]))

def validate():
 s,old,v=setup();g=gate(False);assert g==read(A/'GATE_VALIDATION.json')
 if g['status']!='PASS':
  save('VALIDATION.json',{'status':'PASS_CONTROL_STOP_ACCOUNTING','gate':g,'native_executed':False});return
 rows,units,ids=v.native_packet(old);groups=[units[i] for i in ids];W=v.vocab(old);a=read(A/'RESULT.json');b=read(A/'INDEPENDENT_RESULT.json')
 assert a['core_sha256']==sha(ROOT/s['core_path']) and a['lock_sha256']==sha(E/'LOCK.json')
 for p in [a,b]:
  assert p['positions_zero_based']==ids and p['groups']==groups
  if 'original_groups' in p:assert p['original_groups']==rows
  if 'original_units' in p:assert p['original_units']==units
 expected={(n,m) for n in s['source_names'] for m in s['modes']};aa={(c['source'],c['mode']):c['result'] for c in a['cases']};bb={(c['source'],c['mode']):c['result'] for c in b['cases']}
 assert len(a['cases'])==len(b['cases'])==16 and set(aa)==set(bb)==expected
 decision=[]
 for key in sorted(expected):
  ra,rb=aa[key],bb[key];sa,sb=ra['status'],rb['status'];assert sa in ['SAT','UNSAT','UNKNOWN'] and sb in ['SAT','UNSAT','UNKNOWN']
  for r in [ra,rb]:
   if r['status']=='SAT':cert(r,groups,set(W[key[0]]),s['signs'],key[1])
  assert {sa,sb}!={'SAT','UNSAT'},('independent solver disagreement',key)
  outcome='SAT_CAPACITY_ONLY' if 'SAT' in [sa,sb] else 'UNSAT_BOTH' if sa==sb=='UNSAT' else 'UNKNOWN_OPEN'
  decision.append({'source':key[0],'mode':key[1],'boolean':sa,'row_dfs':sb,'effective':outcome})
 save('VALIDATION.json',{'status':'PASS_INDEPENDENT_CERTIFICATES_AND_OLD_ROW_DFS_COMPARISON','validator_sha256':sha(Path(__file__)),'primary_sha256':sha(A/'RESULT.json'),'independent_sha256':sha(A/'INDEPENDENT_RESULT.json'),'gate_sha256':sha(A/'GATE_VALIDATION.json'),'positions':46,'cases':decision,'limits':['No source alphabet or word meaning identified. SAT is only necessary core capacity.','UNKNOWN remains open; fixed-case UNSAT requires both exhaustive engines.','Exact old1421 source loader/native packet and rowDFS reused under pins; no new Boolean primary import; old STOP unchanged.']})
 print(json.dumps(decision))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');p.add_argument('--validate',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.gate:print(json.dumps(gate()))
 elif a.native:native()
 elif a.validate or a.check:validate()
 else:p.error('choose --gate, --native or --validate/--check')
