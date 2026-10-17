#!/usr/bin/env python3
"""Independent Boolean Parikh encoding and source/certificate reconstruction; shared Z3 backend."""
import argparse,hashlib,json,time,itertools
from collections import Counter,defaultdict
import z3
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=A/n
 if p.exists():assert read(p)==x,'Refuse changed overwrite '+n
 else:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def setup():
 s=read(E/'src/SPEC.json');pins=read(E/'LOCK.json')['files']
 if isinstance(pins,dict):
  for p,h in pins.items():assert sha(ROOT/p)==h,p
 else:
  for p in pins:assert sha(ROOT/p['path'])==p['sha256'],p['path']
 for p,h in s['predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 assert s['mode']=='ARBITRARY_WITHIN_WORD_PERMUTATION' and s['native_groups']==59 and s['control_groups']==32
 assert len(s['signs'])==len(set(s['signs']))==22
 assert s['independent_search']=={'preparation_seconds':20,'solver_seconds':20}
 return s

def inputs(s):
 source=read(ROOT/s['source_projection']);records=source['records'];W=sorted({w for r in records for w in r['words']});alpha=sorted(set(''.join(W)))
 assert W==source['words'] and alpha==source['alphabet'] and len(W)==2133 and len(alpha)==23
 assert sum(len(r['words']) for r in records)==5768 and len(records)==346
 control=read(ROOT/s['control_input']);idx=next(i for i,r in enumerate(records) if len(r['words'])>=32);r=records[idx]
 assert control['source_record_index']==idx and control['source_body_child_index']==r['body_child_index']
 ws=r['words'][:32];key={c:s['signs'][i%s['control_mapping_modulo']] for i,c in enumerate(alpha)};gs=[[key[c] for c in w] for w in ws]
 assert control['planted_words']==ws and control['planted_key']==key and control['groups']==gs
 assert control['source_projection_sha256']==sha(ROOT/s['source_projection'])
 active=set(''.join(ws));classes={}
 for c in alpha:
  if c in active:classes.setdefault(key[c],[]).append(c)
 assert control['active_collision_classes']==[cs for cs in classes.values() if len(cs)>1]
 native=read(ROOT/s['native_input']);assert native['edition']=='IT2a' and native['group_count']==59
 old=read(ROOT/native['source']);assert sha(ROOT/native['source'])==native['source_sha256']
 rows=[r for r in old['groups'] if r['edition']=='IT2a'];assert len(rows)==59
 assert native['ids']==[r['group']['source_group_id'] for r in rows]
 assert native['raw_groups']==[r['group']['ivtff_group_raw'] for r in rows]
 assert native['loci']==[r['locus'] for r in rows]
 units=[]
 for raw in native['raw_groups']:
  dp=[[] for _ in range(len(raw)+1)];dp[0]=[[]]
  for i in range(len(raw)):
   for sign in s['signs']:
    if raw.startswith(sign,i):dp[i+len(sign)]+=[prefix+[sign] for prefix in dp[i]]
  assert len(dp[-1])==1,'Nonunique raw parse'
  units.append(dp[-1][0])
 assert units==native['groups']
 return source,W,control,native

def cert(result,groups,W,signs):
 assert result['status']=='SAT';key=result['key'];ws=result.get('words',result.get('source_words'))
 assert set(key)==set(''.join(W)) and all(v in signs for v in key.values())
 assert len(ws)==len(groups)
 for w,g in zip(ws,groups):assert w in W and Counter(key[c] for c in w)==Counter(g)

def solve(groups,W,signs,limits):
 begin=time.monotonic();alpha=sorted(set(''.join(W)));solver=z3.Solver()
 xs={(c,t):z3.Bool('x_%d_%d'%(i,j)) for i,c in enumerate(alpha) for j,t in enumerate(signs)}
 for c in alpha:solver.add(z3.PbEq([(xs[c,t],1) for t in signs],1))
 profiles=defaultdict(set)
 for w in W:profiles[len(w)].add(tuple(sorted(Counter(w).items())))
 bags=sorted({tuple(sorted(Counter(g).items())) for g in groups})
 for bi,bag in enumerate(bags):
  target=dict(bag);choices=[]
  for wi,profile in enumerate(sorted(profiles[sum(target.values())])):
   if time.monotonic()-begin>limits['preparation_seconds']:return {'status':'UNKNOWN','reason':'preparation_cap'}
   selector=z3.Bool('s_%d_%d'%(bi,wi));choices.append(selector)
   for t in signs:
    equation=z3.PbEq([(xs[c,t],count) for c,count in profile],target.get(t,0))
    solver.add(z3.Implies(selector,equation))
  solver.add(z3.Or(choices))
 if time.monotonic()-begin>limits['preparation_seconds']:return {'status':'UNKNOWN','reason':'preparation_cap'}
 solver.set(timeout=int(1000*limits['solver_seconds']));answer=solver.check()
 if answer==z3.unknown:return {'status':'UNKNOWN','reason':solver.reason_unknown()}
 if answer==z3.unsat:return {'status':'UNSAT'}
 model=solver.model();key={c:next(t for t in signs if z3.is_true(model.eval(xs[c,t],model_completion=True))) for c in alpha}
 index=defaultdict(list)
 for w in sorted(W):index[tuple(sorted(Counter(key[c] for c in w).items()))].append(w)
 words=[index[tuple(sorted(Counter(g).items()))][0] for g in groups]
 result={'status':'SAT','key':key,'words':words};cert(result,groups,set(W),signs);return result

def sourcefree():
 fixtures=[([['p','q'],['q','p']],['ab'],True),([['p','q']],['ab'],True),([['q','p']],['ab'],True),([['p','p']],['ab'],True),([['p','q']],['aa'],False),([['p'],['q']],['a'],False),([['p','p'],['p','q']],['aa','ab'],True)]
 cases=0
 for W in [['a'],['a','b'],['aa'],['ab'],['aa','ab'],['a','ab']]:
  alpha=sorted(set(''.join(W)))
  candidate_groups=[list(x) for n in (1,2) for x in itertools.product('pq',repeat=n)]
  for groups in [[g] for g in candidate_groups]+[[['p'],['q']],[['p','q'],['p','p']]]:
   possible=False
   for vals in itertools.product('pq',repeat=len(alpha)):
    key=dict(zip(alpha,vals));available=[Counter(key[c] for c in w) for w in W]
    if all(Counter(g) in available for g in groups):possible=True;break
   result=solve(groups,W,list('pq'),{'preparation_seconds':5,'solver_seconds':5})
   assert result['status']==('SAT' if possible else 'UNSAT');cases+=1
 for groups,W,expected in fixtures:
  assert solve(groups,W,list('pq'),{'preparation_seconds':5,'solver_seconds':5})['status']==('SAT' if expected else 'UNSAT')
 return {'status':'PASS','exhaustive_function_fixtures':cases,'named_cases':len(fixtures),'independent_encoding':'Boolean ExactlyOne rows, word selectors, weighted PbEq per destination sign','backend':'Z3 shared with primary; not independent solver-engine evidence'}

def check_wrapper(obj,inputpath):
 assert obj['input_sha256']==sha(inputpath)
 status=obj['result']['status'];assert status in ['SAT','UNSAT','UNKNOWN']
 # Root wrappers may expose raw solver status or gate PASS/STOP; decisions below use result.
 assert obj['status'] in [status,'PASS' if status=='SAT' else 'STOP']

def search(s,groups,W):
 start=time.monotonic();r=solve(groups,W,s['signs'],s['independent_search']);elapsed=time.monotonic()-start
 if r['status']=='SAT':cert(r,groups,set(W),s['signs'])
 return r,elapsed

def gate_report(s,W,control):
 a=read(A/'CONTROL_PRIMARY.json');b=read(A/'INDEPENDENT_CONTROL.json')
 for z in [a,b]:
  check_wrapper(z,ROOT/s['control_input'])
  if z['result']['status']=='SAT':cert(z['result'],control['groups'],set(W),s['signs'])
 cert({'status':'SAT','key':control['planted_key'],'words':control['planted_words'],'directions':['FWD']*32},control['groups'],set(W),s['signs'])
 ss=[a['result']['status'],b['result']['status']];invalid='UNSAT' in ss;passed=ss==['SAT','SAT']
 if not passed:assert not (A/'RESULT.json').exists() and not (A/'INDEPENDENT_RESULT.json').exists()
 return {'status':'PASS' if passed else 'STOP','reason':'BOTH_ANY_CERTIFICATES_VERIFIED' if passed else 'INVALID_KNOWN_POSITIVE_UNSAT' if invalid else 'CONTROL_SEARCH_UNKNOWN','known_positive_result_invalid':invalid,'primary_status':ss[0],'independent_status':ss[1],'control_groups':32,'control_input_sha256':sha(ROOT/s['control_input']),'primary_sha256':sha(A/'CONTROL_PRIMARY.json'),'independent_sha256':sha(A/'INDEPENDENT_CONTROL.json'),'lock_sha256':sha(E/'LOCK.json'),'validator_sha256':sha(Path(__file__)),'source_free_controls':sourcefree(),'scope':'ANY-key Parikh capacity only; no exact order, planted recovery or uniqueness. Same Z3 backend with independently constructed constraints.'}

def gate():
 s=setup();_,W,c,_=inputs(s);assert not (A/'INDEPENDENT_CONTROL.json').exists(),'No control rerun'
 assert (A/'CONTROL_PRIMARY.json').exists()
 r,elapsed=search(s,c['groups'],W);save('INDEPENDENT_CONTROL.json',{'status':r['status'],'result':r,'elapsed_seconds':elapsed,'input_sha256':sha(ROOT/s['control_input'])})
 g=gate_report(s,W,c);save('GATE_VALIDATION.json',g);print(json.dumps(g))

def native():
 s=setup();_,W,c,n=inputs(s);g=gate_report(s,W,c);assert g==read(A/'GATE_VALIDATION.json') and g['status']=='PASS'
 assert not (A/'INDEPENDENT_RESULT.json').exists(),'No native rerun'
 r,elapsed=search(s,n['groups'],W);save('INDEPENDENT_RESULT.json',{'status':r['status'],'result':r,'elapsed_seconds':elapsed,'input_sha256':sha(ROOT/s['native_input'])});print(json.dumps({'independent_status':r['status']}))

def inverses(result,n,W):
 key=result['key'];index=defaultdict(list)
 for w in sorted(W):index[tuple(sorted(Counter(key[c] for c in w).items()))].append(w)
 positions=[]
 for ident,locus,raw,g in zip(n['ids'],n['loci'],n['raw_groups'],n['groups']):
  candidates=[]
  for w in index[tuple(sorted(Counter(g).items()))]:
   available=defaultdict(list)
   for j,t in enumerate(g):available[t].append(j)
   permutation=[available[key[c]].pop(0) for c in w]
   assert sorted(permutation)==list(range(len(g))) and all(key[c]==g[j] for c,j in zip(w,permutation))
   candidates.append({'source_word':w,'source_position_to_target_position':permutation})
  assert candidates
  positions.append({'source_group_id':ident,'locus':locus,'raw_group':raw,'units':g,'all_preimages':candidates})
 assert len(positions)==59
 return {'key':key,'positions':positions,'scope':'Complete frozen-W inverse sets and one exact positional permutation per preimage. Arbitrary within-word order only; no meanings or preferred word.'}

def validate():
 s=setup();_,W,c,n=inputs(s);g=gate_report(s,W,c);assert g==read(A/'GATE_VALIDATION.json');inverse={}
 if g['status']!='PASS':
  assert read(A/'NATIVE_STOP.json')['native_cases_executed']==0
  final='INVALID_CONTROL_UNSAT' if g['known_positive_result_invalid'] else 'CONTROL_STOP_NO_NATIVE_SEARCH';statuses={};executed=False
 else:
  a=read(A/'RESULT.json');b=read(A/'INDEPENDENT_RESULT.json');statuses={};executed=True
  for label,z in [('primary',a),('independent',b)]:
   check_wrapper(z,ROOT/s['native_input']);r=z['result'];statuses[label]=r['status']
   if r['status']=='SAT':cert(r,n['groups'],set(W),s['signs']);inverse[label]=inverses(r,n,W)
  ss=set(statuses.values())
  final='INVALID_DISAGREEMENT' if ss=={'SAT','UNSAT'} else 'SAT_CAPACITY_UNASSESSED' if 'SAT' in ss else 'DUAL_ENCODING_UNSAT_ARBITRARY_WORD_ORDER' if ss=={'UNSAT'} else 'UNKNOWN_OPEN'
 decision={'status':final,'confirmed_words':0,'native_executed':executed,'native_cases':int(executed),'engine_statuses':statuses,'gate_status':g['status'],'source_projection_sha256':sha(ROOT/s['source_projection']),'native_input_sha256':sha(ROOT/s['native_input']),'lock_sha256':sha(E/'LOCK.json'),'claim_ceiling':s['claim_ceiling']}
 save('FINAL_DECISION.json',decision)
 if inverse:save('INVERSE_WORD_SETS.json',{'status':'UNASSESSED_FULL_PREIMAGE_SETS','source_projection_sha256':sha(ROOT/s['source_projection']),'by_engine':inverse})
 validation={'status':'INVALID_ENGINE_RESULT' if final.startswith('INVALID') else 'PASS_INDEPENDENT_PARIKH_CERTIFICATE_ACCOUNTING','validator_sha256':sha(Path(__file__)),'decision_sha256':sha(A/'FINAL_DECISION.json'),'control_gate':g,'native_engine_statuses':statuses,'full_inverse_keys':sorted(inverse),'checks':['Pinned unchanged source W and all59 native raw groups uniquely reconstructed','Original first32 source calibration and jmod20 key/groups independently checked','Both control solver outputs checked separately; no planted truth passed to solver','Every returned SAT key checked by encoded multiplicities on all original word occurrences','Native UNSAT effective only with both exhaustive results; UNKNOWN not a rejection','Each nativeSAT gets all frozen-vocabulary bag preimages and positional permutations at all59sourcepositions'],'limits':['No source adjacency, frequency, run inverse or source grammar used; arbitrary word-internal order is a relaxation, not a historical writer.','Raw preimages and positional permutations are unassessed witnesses, not word meanings; distinct keys remain separate.','Independent Boolean weighted-PB encoder; primary Int encoder not imported. Same Z3 backend is not solver-engine diversity.']}
 save('VALIDATION.json',validation);print(json.dumps(decision))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');p.add_argument('--validate',action='store_true');p.add_argument('--check',action='store_true');p.add_argument('--controls',action='store_true');a=p.parse_args()
 if a.controls:print(json.dumps(sourcefree()))
 elif a.gate:gate()
 elif a.native:native()
 elif a.validate or a.check:validate()
 else:p.error('choose --gate, --native or --validate/--check')
